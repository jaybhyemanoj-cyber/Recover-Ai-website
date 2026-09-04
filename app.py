import os
import sys
import time
import threading
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, render_template_string, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from typing import Optional, Dict, Any, List
import cv2
import numpy as np

import config
from ai.notifications import notification_service, send_ntfy_alert, send_fall_alert, send_tinkerstream_alert
from ai.tinkerstream_iot import update_alert_state
from ai.camera import camera_manager
from ai.detector import pose_detector
from ai.activity_rules import activity_analyzer
from ai.evidence import handle_confirmed_event, create_evidence_screenshot
from ai.video_analyzer import analyze_video_file
from ai.physiotherapy import physio_coach, EXERCISE_DEFINITIONS
from ai.assistant import recovery_assistant
from ai.report_generator import generate_video_analysis_report, generate_patient_recovery_summary_report
from db import (
    init_db, db_save_alert, db_get_alerts, db_acknowledge_alert,
    db_escalate_alert, db_save_appointment, db_get_appointments, db_cancel_appointment
)
from security import verify_recaptcha_v3, verify_google_oauth_token
from compliance import AuditTrailLogger, GDPRAndDPDPEngine, get_compliance_health_score

try:
    init_db()
except Exception as e:
    logger.warning(f"MySQL initialization notice: {e}")


try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = Flask(__name__, static_folder="static")
CORS(app, resources={r"/*": {"origins": "*"}})

# Allowed video extensions for upload
ALLOWED_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# In-memory storage for alerts and acknowledgments
ALERTS_DB = [
    {
        "id": "ALT-001",
        "patientId": "P-101",
        "patientName": "Rahul Sharma",
        "title": "CRITICAL INCIDENT - Confirmed Fall (Historical Log)",
        "eventType": "CONFIRMED_FALL",
        "message": "AI camera edge sensor detected verified posture drop on bedroom floor. Handled previously.",
        "time": "10:42 AM",
        "timestamp": datetime.now().isoformat(),
        "severity": "critical",
        "riskLevel": "critical",
        "confidence": 0.94,
        "location": "Bedroom Doorway",
        "acknowledged": True,
        "caregiverStatus": "resolved",
        "acknowledgedBy": "Primary Caregiver",
        "acknowledgedAt": "10:45 AM",
        "screenshotUrl": "/static/screenshots/fall_P101_sample.jpg",
        "ntfyStatus": "delivered",
        "ntfyTopic": config.NTFY_TOPIC,
        "source": "simulation",
        "caregiverPhone": config.CAREGIVER_PHONE
    }
]

# Sync initial seed alert to DB if MySQL is active
try:
    db_save_alert(ALERTS_DB[0])
except Exception:
    pass

# Real-time AI Telemetry State
LATEST_TELEMETRY = {
    "camera_connected": False,
    "camera_resolution": f"{config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}",
    "yolo_model": config.YOLO_MODEL_PATH,
    "yolo_img_size": config.YOLO_IMG_SIZE,
    "yolo_inference_fps": config.YOLO_INFERENCE_FPS,
    "device": config.DEVICE.upper(),
    "avg_inference_time_ms": 0.0,
    "activity": "NORMAL",
    "risk_level": "stable",
    "confidence": 0.0,
    "details": "Camera initializing or idle",
    "torso_angle": 0.0,
    "fall_counter": 0,
    "source": "yolo",
    "fps": 0.0,
    "caregiver_phone": config.CAREGIVER_PHONE,
    "last_update": time.time()
}

# Cached detection state for smooth frame overlay between inference steps
LATEST_DETECTION: dict = {
    "detected": False,
    "keypoints": [],
    "keypoints_conf": [],
    "bbox": None,
    "confidence": 0.0
}
LATEST_ANALYSIS: dict = {
    "activity": "NORMAL",
    "risk_level": "stable",
    "details": "Monitoring patient posture",
    "torso_angle": 0.0,
    "fall_counter": 0
}

LATEST_STREAM_JPEG: Optional[bytes] = None
LIVE_CAMERA_PAUSED: bool = True  # Default OFF for privacy until user grants explicit permission
frame_lock = threading.Lock()
state_lock = threading.Lock()

def ai_camera_worker():
    """
    Optimized AI Camera Pipeline:
    - Runs REAL YOLO Pose inference at target YOLO_INFERENCE_FPS (12 FPS).
    - Renders skeleton overlay onto live frames at full camera rate (30 FPS) with 0 lag.
    - Runs activity temporal rules and confirms fall/inactivity events.
    - Dispatches single keyframe screenshot & ntfy alert.
    """
    global LATEST_STREAM_JPEG, LATEST_TELEMETRY, LATEST_DETECTION, LATEST_ANALYSIS, LIVE_CAMERA_PAUSED
    logger.info(f"AI Camera Worker active on: {config.DEVICE.upper()} (Inference FPS: {config.YOLO_INFERENCE_FPS}, imgsz: {config.YOLO_IMG_SIZE})")

    last_inference_time = 0.0
    inference_interval = 1.0 / max(1.0, config.YOLO_INFERENCE_FPS)

    while True:
        try:
            if LIVE_CAMERA_PAUSED:
                # Release webcam device while camera is OFF/paused for total privacy
                if camera_manager.running:
                    camera_manager.stop()

                placeholder = np.zeros((360, 640, 3), dtype=np.uint8)
                placeholder[:] = (15, 23, 42)
                cv2.putText(placeholder, "Live Camera: OFF (User Permission Required)", (50, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (239, 68, 68), 2)
                cv2.putText(placeholder, "Click 'Turn ON Live Camera' to start monitoring", (60, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (148, 163, 184), 1)
                _, enc = cv2.imencode(".jpg", placeholder)
                with frame_lock:
                    LATEST_STREAM_JPEG = enc.tobytes()
                    LATEST_TELEMETRY["details"] = "Live camera OFF (Waiting for user permission)."
                    LATEST_TELEMETRY["camera_connected"] = False
                    LATEST_TELEMETRY["camera_enabled"] = False
                time.sleep(0.3)
                continue

            if not camera_manager.is_connected():
                if not camera_manager.running:
                    started = camera_manager.start()
                    if not started:
                        # Cloud/headless environment - update placeholder frame and sleep
                        placeholder = np.zeros((360, 640, 3), dtype=np.uint8)
                        placeholder[:] = (15, 23, 42)
                        cv2.putText(placeholder, "Live Camera: Ready / Video Upload Mode Active", (50, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (56, 189, 248), 1)
                        _, enc = cv2.imencode(".jpg", placeholder)
                        with frame_lock:
                            LATEST_STREAM_JPEG = enc.tobytes()
                        time.sleep(5.0)
                        continue
                time.sleep(0.5)
                continue

            frame = camera_manager.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            now = time.time()
            h, w = frame.shape[:2]

            # 1. Periodic Real YOLO Inference Step
            if (now - last_inference_time) >= inference_interval:
                last_inference_time = now
                detection = pose_detector.detect(frame, draw_overlay=False)
                analysis = activity_analyzer.analyze(detection, (h, w))

                # State-change optimized IoT Alert update (key=1 on fall, key=0 when posture normal)
                fall_detected = (analysis.get("activity") == "CONFIRMED_FALL" or analysis.get("risk_level") == "critical")
                update_alert_state(fall_detected)

                with state_lock:
                    LATEST_DETECTION = detection
                    LATEST_ANALYSIS = analysis

                # Handle Confirmed Events (Standing, Hand Right->Left, Possible Fall, Bed Exit)
                if analysis.get("is_confirmed_event"):
                    event_type = analysis.get("screenshot_event") or analysis.get("activity", "NORMAL")
                    risk_level = analysis.get("risk_level", "stable")
                    logger.info(f"CONFIRMED CAPTURE EVENT: {event_type} ({risk_level}) for Patient {config.PATIENT_ID}")

                    evidence_frame = frame.copy()
                    if detection.get("detected"):
                        evidence_frame = pose_detector.draw_pose_overlay(
                            evidence_frame,
                            detection.get("keypoints", []),
                            detection.get("keypoints_conf", []),
                            detection.get("bbox"),
                            detection.get("confidence", 0.0)
                        )

                    event_result = handle_confirmed_event(
                        frame=evidence_frame,
                        patient_id=config.PATIENT_ID,
                        event_type=event_type,
                        risk_level=risk_level,
                        confidence=float(detection.get("confidence", 0.0)),
                        source="yolo"
                    )

                    new_alert = {
                        "id": event_result["alert_id"],
                        "patientId": config.PATIENT_ID,
                        "patientName": "Rahul Sharma" if config.PATIENT_ID == "P-101" else f"Patient {config.PATIENT_ID}",
                        "title": f"CRITICAL INCIDENT - {event_type}" if risk_level == "critical" else f"PATIENT EVENT - {event_type}",
                        "eventType": event_type,
                        "message": f"Real YOLO Pose detector captured {event_type} in patient room.",
                        "time": event_result["timestamp"],
                        "timestamp": event_result["timestamp_iso"],
                        "severity": risk_level,
                        "riskLevel": risk_level,
                        "confidence": float(detection.get("confidence", 0.0)),
                        "location": "Patient Room / Bedside",
                        "acknowledged": risk_level != "critical",
                        "caregiverStatus": "pending" if risk_level == "critical" else "info",
                        "screenshotUrl": event_result["screenshot_url"],
                        "ntfyStatus": "delivered" if event_result.get("ntfy", {}).get("success") else ("failed" if event_result.get("ntfy", {}).get("status_code") else "not_sent"),
                        "ntfyTopic": config.NTFY_TOPIC,
                        "source": "yolo",
                        "caregiverPhone": config.CAREGIVER_PHONE
                    }
                    ALERTS_DB.insert(0, new_alert)

                # Process Physiotherapy & ROM Keypoint Telemetry
                physio_telemetry = physio_coach.process_keypoints(
                    detection.get("keypoints", []),
                    detection.get("keypoints_conf", []),
                    sim_time=now
                )

                # Atomically update live telemetry synchronized with this exact detection
                with frame_lock:
                    LATEST_TELEMETRY.update({
                        "camera_connected": True,
                        "camera_resolution": f"{w}x{h}",
                        "yolo_model": config.YOLO_MODEL_PATH,
                        "yolo_img_size": config.YOLO_IMG_SIZE,
                        "yolo_inference_fps": config.YOLO_INFERENCE_FPS,
                        "device": config.DEVICE.upper(),
                        "avg_inference_time_ms": pose_detector.avg_inference_time_ms,
                        "activity": analysis["activity"],
                        "risk_level": analysis["risk_level"],
                        "confidence": float(detection.get("confidence", 0.0)),
                        "details": analysis["details"],
                        "torso_angle": analysis.get("torso_angle", 0.0),
                        "fall_counter": analysis.get("fall_counter", 0),
                        "standing_counter": analysis.get("standing_counter", 0),
                        "latest_event": analysis.get("screenshot_event") or analysis.get("activity"),
                        "patient_id": config.PATIENT_ID,
                        "source": "yolo",
                        "fps": round(camera_manager.fps if camera_manager.fps > 0 else 30.0, 1),
                        "caregiver_phone": config.CAREGIVER_PHONE,
                        "physio": physio_telemetry,
                        "timestamp": datetime.now().strftime("%I:%M:%S %p"),
                        "last_update": now
                    })


            # 2. Fast Skeleton & HUD Overlay on Live Frame (~30 FPS)
            with state_lock:
                cached_det = LATEST_DETECTION
                cached_ana = LATEST_ANALYSIS

            annotated_frame = frame.copy()
            if cached_det.get("detected"):
                annotated_frame = pose_detector.draw_pose_overlay(
                    annotated_frame,
                    cached_det.get("keypoints", []),
                    cached_det.get("keypoints_conf", []),
                    cached_det.get("bbox"),
                    cached_det.get("confidence", 0.0)
                )

            # Top Visual Debug HUD Banner
            cv2.rectangle(annotated_frame, (0, 0), (w, 36), (15, 23, 42), -1)
            status_color = (52, 211, 153) if cached_ana["risk_level"] == "stable" else (225, 29, 72) if cached_ana["risk_level"] == "critical" else (245, 158, 11)
            cv2.circle(annotated_frame, (12, 18), 5, status_color, -1)
            
            is_person = cached_det.get("detected", False)
            conf_val = float(cached_det.get("confidence", 0.0))
            kpts_conf_list = cached_det.get("keypoints_conf", [])
            kpts_count = sum(1 for c in kpts_conf_list if c >= getattr(config, "KEYPOINT_CONFIDENCE_THRESHOLD", 0.30))
            fps_val = int(camera_manager.fps if camera_manager.fps > 0 else 30)
            fall_cnt = cached_ana.get("fall_counter", 0)
            fall_score_pct = int((fall_cnt / max(1, config.FALL_CONFIRMATION_FRAMES)) * 100)
            
            hud_text = f"Person: {'YES' if is_person else 'NO'} ({int(conf_val * 100)}%) | Kpts: {kpts_count}/17 | FPS: {fps_val} | Act: {cached_ana['activity']} | Fall: {fall_score_pct}%"
            cv2.putText(annotated_frame, hud_text, (24, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (241, 245, 249), 1)

            # Bed Zone Guide box
            bx1 = int(config.BED_ZONE[0] * w)
            by1 = int(config.BED_ZONE[1] * h)
            bx2 = int(config.BED_ZONE[2] * w)
            by2 = int(config.BED_ZONE[3] * h)
            cv2.rectangle(annotated_frame, (bx1, by1), (bx2, by2), (234, 179, 8), 1)
            cv2.putText(annotated_frame, "BED ZONE", (bx1 + 4, by1 + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (234, 179, 8), 1)

            # Encode frame for MJPEG stream
            ret_enc, jpeg = cv2.imencode(".jpg", annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if ret_enc:
                with frame_lock:
                    LATEST_STREAM_JPEG = jpeg.tobytes()

            time.sleep(0.005)

        except Exception as e:
            logger.error(f"Error in AI worker loop: {e}")
            time.sleep(0.05)

# Start background AI worker thread
ai_thread = threading.Thread(target=ai_camera_worker, daemon=True)
ai_thread.start()

# Ensure baseline sample screenshot exists for dashboard preview without creating duplicate files
try:
    sample_path = config.SCREENSHOT_DIR / "fall_P101_sample.jpg"
    if not sample_path.exists():
        dummy_frame = np.zeros((360, 640, 3), dtype=np.uint8)
        dummy_frame[:] = (15, 23, 42)
        cv2.putText(dummy_frame, "CONFIRMED FALL - Keyframe Evidence", (80, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (56, 189, 248), 2)
        cv2.imwrite(str(sample_path), dummy_frame)
except Exception:
    pass

@app.route("/", methods=["GET"])
def home():
    """Service status and quick links."""
    return jsonify({
        "service": "Post-Operative Patient Monitoring AI & ntfy Notification Server",
        "status": "online",
        "modes": ["LIVE CAMERA MONITORING", "VIDEO UPLOAD + AI ANALYSIS"],
        "camera_connected": camera_manager.is_connected(),
        "camera_resolution": f"{config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}",
        "device": config.DEVICE.upper(),
        "yolo_model": config.YOLO_MODEL_PATH,
        "yolo_img_size": config.YOLO_IMG_SIZE,
        "yolo_inference_fps": config.YOLO_INFERENCE_FPS,
        "caregiver_phone": config.CAREGIVER_PHONE,
        "ntfy_topic": config.NTFY_TOPIC,
        "ntfy_url": f"{config.NTFY_SERVER_URL}/{config.NTFY_TOPIC}",
        "endpoints": {
            "video_feed": "/video_feed",
            "video_analyze": "/api/video/analyze",
            "camera_status": "/api/camera/status",
            "test_fall": "/test-fall",
            "get_alerts": "/api/alerts",
            "config": "/api/config"
        }
    })

@app.route("/video_feed")
def video_feed():
    """MJPEG stream of the live webcam with real YOLO Pose skeleton annotations."""
    def generate_frames():
        while True:
            with frame_lock:
                frame_bytes = LATEST_STREAM_JPEG

            if frame_bytes is None:
                placeholder = np.zeros((360, 640, 3), dtype=np.uint8)
                placeholder[:] = (15, 23, 42)
                status_text = "Webcam Initializing / Disconnected"
                if not camera_manager.is_connected():
                    status_text = "Webcam Offline (Check Index 0 or permissions)"
                cv2.putText(placeholder, status_text, (80, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (148, 163, 184), 2)
                _, enc = cv2.imencode(".jpg", placeholder)
                frame_bytes = enc.tobytes()

            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
            time.sleep(0.033)  # ~30 FPS

    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/api/camera/status", methods=["GET"])
def get_camera_status():
    """Returns live JSON telemetry for the React dashboard."""
    return jsonify(LATEST_TELEMETRY)

@app.route("/api/video/analyze", methods=["POST"])
def analyze_video_endpoint():
    """
    Video Upload & AI Analysis Endpoint:
    Accepts patient room video, executes YOLO Pose & Activity rules, generates incident report,
    and returns full timeline and fall detection evidence.
    """
    if "video" not in request.files and "file" not in request.files:
        return jsonify({"status": "error", "message": "No video file provided in request."}), 400

    file = request.files.get("video") or request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"status": "error", "message": "Selected video file is empty."}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "status": "error",
            "message": f"Invalid video file format. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400

    patient_id = request.form.get("patient_id") or config.PATIENT_ID
    filename = secure_filename(file.filename)
    unique_filename = f"upload_{int(time.time())}_{filename}"
    temp_path = config.UPLOAD_FOLDER / unique_filename

    global LIVE_CAMERA_PAUSED
    LIVE_CAMERA_PAUSED = True

    try:
        # Save temporary video for processing
        file.save(str(temp_path))
        
        # Execute Real AI Video Pipeline
        analysis_result = analyze_video_file(
            video_path=str(temp_path),
            patient_id=patient_id,
            frame_interval=config.VIDEO_FRAME_INTERVAL
        )

        # If a critical fall alert was confirmed, insert it into ALERTS_DB for caregiver dashboard
        if analysis_result.get("alert"):
            ALERTS_DB.insert(0, analysis_result["alert"])

        return jsonify(analysis_result)

    except Exception as e:
        logger.error(f"Video analysis failed: {e}")
        # Clean up temporary file on failure
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        LIVE_CAMERA_PAUSED = False

@app.route("/api/camera/pause", methods=["POST"])
def pause_camera():
    """Pause live webcam AI analysis and release camera hardware."""
    global LIVE_CAMERA_PAUSED
    LIVE_CAMERA_PAUSED = True
    camera_manager.stop()
    return jsonify({"status": "success", "paused": True, "camera_enabled": False, "message": "Live camera analysis paused & webcam released."})

@app.route("/api/camera/resume", methods=["POST"])
@app.route("/api/camera/start", methods=["POST"])
def resume_camera():
    """Resume live webcam AI analysis and start camera hardware upon explicit user permission."""
    global LIVE_CAMERA_PAUSED
    LIVE_CAMERA_PAUSED = False
    success = camera_manager.start()
    return jsonify({"status": "success" if success else "error", "paused": False, "camera_enabled": True, "camera_connected": success})

@app.route("/api/camera/stop", methods=["POST"])
def stop_camera():
    """Stop webcam capture, release device, and mark paused."""
    global LIVE_CAMERA_PAUSED
    LIVE_CAMERA_PAUSED = True
    camera_manager.stop()
    return jsonify({"status": "success", "paused": True, "camera_enabled": False, "camera_connected": False})

@app.route("/test-fall", methods=["GET", "POST"])
@app.route("/test-alert", methods=["GET", "POST"])
@app.route("/api/camera/simulate-fall", methods=["GET", "POST"])
def test_fall():
    """
    Development/testing endpoint.
    Simulates CONFIRMED_FALL, creates a clearly labelled test screenshot (source='simulation'),
    creates the alert, triggers NTFY via send_fall_alert, and shows the event in the caregiver dashboard.
    Does NOT require webcam or YOLO model.
    """
    req_data = request.get_json(silent=True) or {}
    recaptcha_token = req_data.get("recaptcha_token") or request.args.get("recaptcha_token") or ""

    # Verify Google reCAPTCHA v3
    recaptcha_res = verify_recaptcha_v3(recaptcha_token, action="test_fall")
    if not recaptcha_res.get("valid"):
        return jsonify({
            "status": "error",
            "message": recaptcha_res.get("message", "Bot activity detected! Request blocked by Google reCAPTCHA v3."),
            "score": recaptcha_res.get("score", 0.0)
        }), 403

    patient_id = req_data.get("patient_id") or request.args.get("patient_id") or "P-101"
    event_type = "CONFIRMED_FALL"
    risk_level = "critical"
    topic = req_data.get("topic") or request.args.get("topic") or config.NTFY_TOPIC

    sim_frame = np.zeros((360, 640, 3), dtype=np.uint8)
    sim_frame[:] = (15, 23, 42)
    cv2.line(sim_frame, (0, 280), (640, 280), (30, 41, 59), 2)
    cv2.rectangle(sim_frame, (180, 240), (460, 310), (225, 29, 72), 2)
    cv2.putText(sim_frame, "[TEST SIMULATION] Simulated Fall Keyframe", (120, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(sim_frame, "Source: SIMULATION (No live camera required)", (140, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (56, 189, 248), 1)

    screenshot_path = create_evidence_screenshot(
        frame=sim_frame,
        patient_id=patient_id,
        event_type=event_type,
        risk_level=risk_level,
        confidence=0.95,
        source="simulation"
    )
    filename = os.path.basename(screenshot_path)
    screenshot_url = f"/static/screenshots/{filename}"

    event_dict = {
        "type": "CONFIRMED_FALL",
        "event_type": "CONFIRMED_FALL",
        "patient_id": patient_id,
        "risk_level": "CRITICAL",
        "confidence": 0.95,
        "source": "SIMULATION TEST",
        "screenshot_path": screenshot_path,
        "topic": topic,
        "time": datetime.now().strftime("%I:%M %p")
    }
    ntfy_result = send_fall_alert(event_dict)
    wa_result = notification_service.whatsapp.send(
        event_type=event_type,
        patient_id=patient_id,
        risk_level=risk_level,
        source="simulation"
    )

    alert_id = f"ALT-{datetime.now().strftime('%H%M%S')}"
    new_alert = {
        "id": alert_id,
        "patientId": patient_id,
        "patientName": "Rahul Sharma" if patient_id == "P-101" else f"Patient {patient_id}",
        "title": f"CRITICAL INCIDENT - {event_type} (Test Simulation)",
        "eventType": event_type,
        "message": f"Simulated test fall for Patient {patient_id}. Dispatched via test-fall endpoint.",
        "time": datetime.now().strftime("%I:%M %p"),
        "timestamp": datetime.now().isoformat(),
        "severity": "critical",
        "riskLevel": "critical",
        "confidence": 0.95,
        "location": "Patient Bedside (Simulated)",
        "acknowledged": False,
        "caregiverStatus": "pending",
        "acknowledgedBy": None,
        "acknowledgedAt": None,
        "screenshotUrl": screenshot_url,
        "ntfyStatus": "delivered" if ntfy_result.get("success") else "failed",
        "whatsappStatus": "delivered" if wa_result.get("success") else ("not_configured" if not wa_result.get("configured") else "failed"),
        "ntfyTopic": topic,
        "source": "simulation",
        "caregiverPhone": config.CAREGIVER_PHONE
    }
    ALERTS_DB.insert(0, new_alert)
    db_save_alert(new_alert)

    return jsonify({
        "status": "success",
        "message": "Simulated CONFIRMED_FALL event dispatched successfully",
        "source": "simulation",
        "alert": new_alert,
        "ntfy_dispatch": ntfy_result,
        "whatsapp_dispatch": wa_result,
        "ntfy_feed": f"{config.NTFY_SERVER_URL}/{topic}",
        "caregiver_phone": config.CAREGIVER_PHONE
    })


@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    """Retrieve all recent alerts. Only genuine critical emergencies contribute to unread_count."""
    db_alerts = db_get_alerts()
    active_alerts = db_alerts if db_alerts is not None else ALERTS_DB

    unread_emergencies = [
        a for a in active_alerts
        if not a.get("acknowledged") and (
            str(a.get("severity", "")).lower() in ("critical", "emergency") or
            str(a.get("riskLevel", "")).lower() in ("critical", "emergency")
        ) and str(a.get("eventType", "")).upper() in ("CONFIRMED_FALL", "CONFIRMED FALL", "FALL", "EMERGENCY ESCALATION", "AUTO-ESCALATION (UNACKNOWLEDGED)")
    ]
    return jsonify({
        "alerts": active_alerts,
        "unread_count": len(unread_emergencies)
    })

@app.route("/api/alerts/<alert_id>/acknowledge", methods=["POST"])
def acknowledge_alert(alert_id):
    """Caregiver 'I'm Checking' action."""
    action_type = (request.json or {}).get("action", "checking")
    caregiver_name = (request.json or {}).get("caregiver_name", "Primary Caregiver")
    ack_at = datetime.now().strftime("%I:%M %p")
    
    db_acknowledge_alert(alert_id, action_type, caregiver_name, ack_at)
    
    for alert in ALERTS_DB:
        if alert["id"] == alert_id:
            alert["acknowledged"] = True
            alert["caregiverStatus"] = "checking" if action_type == "checking" else "resolved"
            alert["acknowledgedBy"] = caregiver_name
            alert["acknowledgedAt"] = ack_at
            
            # Reset IoT Alert / Buzzer signal to key=0 upon acknowledgment
            update_alert_state(False)

            return jsonify({
                "status": "success",
                "message": f"Alert {alert_id} marked as '{alert['caregiverStatus']}' by {caregiver_name}",
                "alert": alert
            })
            
    return jsonify({"status": "error", "message": f"Alert {alert_id} not found"}), 404

@app.route("/api/alerts/<alert_id>/escalate", methods=["POST"])
def escalate_alert(alert_id):
    """Caregiver 'Escalate' action."""
    reason = (request.json or {}).get("reason", "Caregiver requested emergency medical escalation")
    escalated_at = datetime.now().strftime("%I:%M %p")
    
    db_escalate_alert(alert_id, reason, escalated_at)
    
    for alert in ALERTS_DB:
        if alert["id"] == alert_id:
            alert["caregiverStatus"] = "escalated"
            alert["escalatedAt"] = escalated_at
            alert["escalationReason"] = reason
            
            notification_service.dispatch(
                event_type="EMERGENCY ESCALATION",
                patient_id=alert.get("patientId", "P-101"),
                risk_level="critical",
                message=f"EMERGENCY: Caregiver escalated alert {alert_id} for Patient {alert.get('patientId')}. Reason: {reason}",
                topic=config.NTFY_TOPIC
            )
            
            return jsonify({
                "status": "success",
                "message": f"Alert {alert_id} escalated to Emergency Response & On-Call Doctor",
                "alert": alert
            })
            
    return jsonify({"status": "error", "message": f"Alert {alert_id} not found"}), 404

@app.route("/api/alerts/unacknowledged/escalate", methods=["GET", "POST"])
def check_unacknowledged_escalation():
    """
    Checks for critical unacknowledged alerts older than timeout and auto-escalates.
    """
    now_ts = time.time()
    timeout = config.UNACKNOWLEDGED_ALERT_TIMEOUT
    escalated_count = 0

    for alert in ALERTS_DB:
        if alert.get("severity") == "critical" and not alert.get("acknowledged") and alert.get("caregiverStatus") == "pending":
            # Check age from timestamp if available
            try:
                alert_time = datetime.fromisoformat(alert.get("timestamp", ""))
                age_sec = (datetime.now() - alert_time).total_seconds()
            except Exception:
                age_sec = 0.0

            if age_sec > timeout:
                alert["caregiverStatus"] = "auto_escalated"
                alert["escalatedAt"] = datetime.now().strftime("%I:%M %p")
                escalated_count += 1
                logger.warning(f"Auto-escalating unacknowledged critical alert {alert['id']} (Age: {age_sec:.1f}s)")
                notification_service.dispatch(
                    event_type="AUTO-ESCALATION (UNACKNOWLEDGED)",
                    patient_id=alert.get("patientId", "P-101"),
                    risk_level="critical",
                    message=f"URGENT: Alert {alert['id']} for Patient {alert.get('patientId')} unacknowledged for >{int(timeout)}s. Auto-escalated to Chief Doctor.",
                    topic=config.NTFY_TOPIC
                )

    return jsonify({
        "status": "success",
        "escalated_count": escalated_count,
        "timeout_seconds": timeout,
        "active_critical_alerts": len([a for a in ALERTS_DB if a.get("severity") == "critical"])
    })

# -------------------------------------------------------------
# AI Physiotherapy / ROM Coach REST Endpoints
# -------------------------------------------------------------
@app.route("/api/physio/state", methods=["GET"])
def get_physio_state():
    """Returns current physiotherapy coach state and available exercise definitions."""
    return jsonify({
        "state": physio_coach._build_response(physio_coach.is_tracking, physio_coach.current_angle, physio_coach.feedback_message, physio_coach.side),
        "available_exercises": EXERCISE_DEFINITIONS,
        "session_history": physio_coach.session_history
    })

@app.route("/api/physio/config", methods=["POST"])
def configure_physio():
    """Configure active physiotherapy exercise, side, or target reps."""
    data = request.json or {}
    exercise = data.get("exercise", "knee_flexion")
    side = data.get("side", "auto")
    target_reps = int(data.get("target_reps", 10))

    physio_coach.set_exercise(exercise, side, target_reps)
    return jsonify({
        "status": "success",
        "message": f"Configured exercise: {exercise}",
        "state": physio_coach._build_response(False, 0.0, physio_coach.feedback_message, side)
    })

@app.route("/api/physio/reset", methods=["POST"])
def reset_physio_counter():
    """Reset repetition counter for active physiotherapy session."""
    physio_coach.reset_counter()
    return jsonify({
        "status": "success",
        "message": "Physiotherapy counter reset",
        "rep_count": 0
    })

# -------------------------------------------------------------
# Multilingual AI Recovery & Appointment Assistant Endpoints
# -------------------------------------------------------------
import ai.appointment_tools as apt_tools

@app.route("/api/doctors", methods=["GET"])
def get_doctors():
    """Retrieve directory of specialists and doctors with schedules."""
    specialty = request.args.get("specialty")
    name = request.args.get("name")
    doctors = apt_tools.find_doctors(specialty=specialty, name=name)
    return jsonify({"status": "success", "count": len(doctors), "doctors": doctors})

@app.route("/api/appointments", methods=["GET", "POST"])
def manage_appointments():
    """GET upcoming appointments or POST new appointment booking."""
    if request.method == "POST":
        data = request.json or {}
        patient_id = data.get("patient_id") or data.get("patientId") or config.PATIENT_ID
        doctor_id = data.get("doctor_id") or data.get("doctorId") or "DOC-01"
        appointment_date = data.get("date") or (date.today() + timedelta(days=1)).isoformat()
        appointment_time = data.get("time") or data.get("slot") or "05:30 PM"
        reason = data.get("reason", "Follow-up Consultation")
        patient_name = data.get("patient_name") or data.get("patientName") or "Rahul Sharma"
        consultation_type = data.get("type", "in_person")

        result = apt_tools.create_appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=reason,
            patient_name=patient_name,
            consultation_type=consultation_type
        )
        return jsonify(result), 201

    patient_id = request.args.get("patient_id") or config.PATIENT_ID
    appointments = apt_tools.get_upcoming_appointments(patient_id)
    return jsonify({"status": "success", "count": len(appointments), "appointments": appointments})

@app.route("/api/appointments/<appointment_id>/reschedule", methods=["POST", "PUT"])
def reschedule_patient_appointment(appointment_id):
    """Reschedule an appointment to a new date and time."""
    data = request.json or {}
    new_date = data.get("date") or (date.today() + timedelta(days=3)).isoformat()
    new_time = data.get("time") or data.get("slot") or "06:00 PM"
    reason = data.get("reason")

    result = apt_tools.reschedule_appointment(
        appointment_id=appointment_id,
        new_date=new_date,
        new_time=new_time,
        reason=reason
    )
    status_code = 200 if result.get("status") == "success" else 404
    return jsonify(result), status_code

@app.route("/api/appointments/<appointment_id>/cancel", methods=["POST", "DELETE"])
def cancel_patient_appointment(appointment_id):
    """Cancel an appointment."""
    data = request.json or {}
    reason = data.get("reason")
    result = apt_tools.cancel_appointment(appointment_id=appointment_id, reason=reason)
    status_code = 200 if result.get("status") == "success" else 404
    return jsonify(result), status_code

@app.route("/api/assistant/chat", methods=["POST"])
def assistant_chat():
    """
    Patient-friendly Multilingual AI Recovery & Appointment Assistant endpoint.
    Accepts: { message: str, language: 'en'|'hi', patient_id: str, patient_data?: dict }
    Returns safe clinical recovery guidance and appointment scheduling actions.
    """
    data = request.json or {}
    message = data.get("message", "").strip()
    language = data.get("language", "en")
    patient_data = data.get("patient_data")

    if not message:
        return jsonify({"status": "error", "message": "Empty message query"}), 400

    response_dict = recovery_assistant.respond(
        query=message,
        language=language,
        custom_patient_data=patient_data
    )
    return jsonify(response_dict)

# -------------------------------------------------------------
# WhatsApp Cloud API Test Endpoint
# -------------------------------------------------------------
@app.route("/api/notifications/whatsapp/test", methods=["GET", "POST"])
def test_whatsapp_notification():
    """Test dispatching an emergency alert via Meta WhatsApp Cloud API."""
    patient_id = (request.json or {}).get("patient_id") or request.args.get("patient_id") or config.PATIENT_ID
    event_type = (request.json or {}).get("event_type") or "TEST WHATSAPP ALERT"

    result = notification_service.whatsapp.send(
        event_type=event_type,
        patient_id=patient_id,
        risk_level="critical",
        source="simulation"
    )
    return jsonify({
        "status": "success" if result.get("success") else "info",
        "configured": result.get("configured", False),
        "result": result,
        "setup_guide": (
            "Set WHATSAPP_ACCESS_TOKEN & WHATSAPP_PHONE_NUMBER_ID in .env to send live WhatsApp alerts."
            if not result.get("configured") else "WhatsApp message sent to configured recipient."
        )
    })

# -------------------------------------------------------------
# Comprehensive Patient Recovery Summary Report Endpoint
# -------------------------------------------------------------
@app.route("/api/reports/patient/<patient_id>", methods=["GET"])
def get_patient_recovery_report(patient_id):
    """
    Generates a full Clinical Post-Operative Recovery Report with vitals,
    milestones, fall incidents, and physio ROM metrics.
    """
    # Build patient data dict
    patient_info = {
        "id": patient_id,
        "name": "Rahul Sharma" if patient_id == "P-101" else f"Patient {patient_id}",
        "surgeryType": "Total Knee Replacement (Right)",
        "surgeryDate": "2026-08-21",
        "recoveryDay": 8,
        "targetRecoveryDays": 30,
        "doctorName": "Dr. Vikramaditya Rao, M.S. Ortho",
        "caregiverName": f"Priya Sharma ({config.CAREGIVER_PHONE})",
        "medicationAdherence": 87,
        "vitals": {
            "temperature": 98.6,
            "bpSystolic": 120,
            "bpDiastolic": 80,
            "heartRate": 72,
            "spO2": 98,
            "painLevel": 2,
            "mobility": "Independent Walking with Cane"
        }
    }

    patient_alerts = [a for a in ALERTS_DB if a.get("patientId") == patient_id]
    physio_state = physio_coach._build_response(physio_coach.is_tracking, physio_coach.current_angle, physio_coach.feedback_message)

    report_result = generate_patient_recovery_summary_report(
        patient_data=patient_info,
        alerts_list=patient_alerts,
        physio_summary=physio_state
    )

    return jsonify(report_result)

@app.route("/api/camera/simulate-fall", methods=["POST"])
def simulate_fall():
    """Trigger simulated fall event."""
    return test_fall()

@app.route("/api/config", methods=["GET", "POST"])
def get_or_update_config():
    """View or update settings dynamically."""
    if request.method == "POST":
        data = request.json or {}
        if "ntfy_topic" in data:
            config.NTFY_TOPIC = data["ntfy_topic"].strip()
        if "yolo_confidence_threshold" in data:
            config.YOLO_CONFIDENCE_THRESHOLD = float(data["yolo_confidence_threshold"])
            pose_detector.conf_threshold = config.YOLO_CONFIDENCE_THRESHOLD
        if "yolo_inference_fps" in data:
            config.YOLO_INFERENCE_FPS = float(data["yolo_inference_fps"])
        if "yolo_img_size" in data:
            config.YOLO_IMG_SIZE = int(data["yolo_img_size"])
            pose_detector.img_size = config.YOLO_IMG_SIZE
        if "caregiver_phone" in data:
            config.CAREGIVER_PHONE = data["caregiver_phone"].strip()

        return jsonify({
            "status": "success",
            "ntfy_topic": config.NTFY_TOPIC,
            "yolo_confidence_threshold": config.YOLO_CONFIDENCE_THRESHOLD,
            "yolo_inference_fps": config.YOLO_INFERENCE_FPS,
            "yolo_img_size": config.YOLO_IMG_SIZE,
            "caregiver_phone": config.CAREGIVER_PHONE,
            "camera_index": config.CAMERA_INDEX
        })
    
    return jsonify({
        "patient_id": config.PATIENT_ID,
        "ntfy_topic": config.NTFY_TOPIC,
        "ntfy_server_url": config.NTFY_SERVER_URL,
        "ntfy_url": f"{config.NTFY_SERVER_URL}/{config.NTFY_TOPIC}",
        "whatsapp_configured": notification_service.whatsapp.is_configured(),
        "whatsapp_recipient": config.WHATSAPP_RECIPIENT_NUMBER,
        "camera_index": config.CAMERA_INDEX,
        "camera_connected": camera_manager.is_connected(),
        "camera_resolution": f"{config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}",
        "device": config.DEVICE.upper(),
        "yolo_model": config.YOLO_MODEL_PATH,
        "yolo_img_size": config.YOLO_IMG_SIZE,
        "yolo_inference_fps": config.YOLO_INFERENCE_FPS,
        "avg_inference_time_ms": pose_detector.avg_inference_time_ms,
        "caregiver_phone": config.CAREGIVER_PHONE,
        "bed_zone": config.BED_ZONE,
        "fall_confirmation_frames": config.FALL_CONFIRMATION_FRAMES,
        "inactivity_timeout": config.INACTIVITY_TIMEOUT,
        "alert_cooldown": config.ALERT_COOLDOWN
    })


@app.route("/static/screenshots/<path:filename>")
def serve_screenshot(filename):
    """Serve captured screenshot images."""
    return send_from_directory(config.SCREENSHOT_DIR, filename)

@app.route("/static/reports/<path:filename>")
def serve_report(filename):
    """Serve generated HTML incident reports."""
    return send_from_directory(config.REPORTS_DIR, filename)

@app.route("/api/auth/google", methods=["POST"])
def google_auth_login():
    """Google OAuth 2.0 Identity verification endpoint."""
    token = (request.json or {}).get("credential") or (request.json or {}).get("id_token")
    if not token:
        return jsonify({"status": "error", "message": "Missing Google ID Token credential"}), 400

    auth_res = verify_google_oauth_token(token)
    if auth_res.get("valid"):
        return jsonify({
            "status": "success",
            "message": "Google Authentication Successful",
            "user": auth_res
        })
    else:
        return jsonify({
            "status": "error",
            "message": auth_res.get("message", "Google Authentication Failed")
        }), 401


# ==============================================================================
# COMPLIANCE & REGULATORY FRAMEWORK ENDPOINTS
# ==============================================================================

@app.route("/api/compliance/status", methods=["GET"])
def get_compliance_status():
    """Retrieve compliance health score and regulatory framework audit status."""
    return jsonify(get_compliance_health_score())

@app.route("/api/compliance/audit", methods=["GET"])
def get_audit_trail():
    """Retrieve Indian IT Act 2000/2008 & CERT-In Section 43A immutable audit trail logs."""
    logs = AuditTrailLogger.get_recent_audit_logs(limit=50)
    return jsonify({
        "status": "success",
        "standard": "Indian IT Act 2000 & 2008 Sec 43A SPDI Rules",
        "audit_logs": logs
    })

@app.route("/api/compliance/gdpr-export/<patient_id>", methods=["GET"])
def gdpr_export_patient_data(patient_id):
    """GDPR Article 20 & DPDP Act 2023 Section 12 Data Portability export endpoint."""
    data_bundle = GDPRAndDPDPEngine.export_patient_data_bundle(patient_id)
    return jsonify({
        "status": "success",
        "export_bundle": data_bundle
    })

if __name__ == "__main__":
    print("================================================================")
    print("PatientCare AI Multi-Mode YOLO Pose & Video Analysis Server")
    print(f"Modes:          1) Live Camera  2) Video Upload Analysis")
    print(f"Resolution:     {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}")
    print(f"Device:         {config.DEVICE.upper()}")
    print(f"Inference FPS:  {config.YOLO_INFERENCE_FPS}")
    print(f"Caregiver Tel:  {config.CAREGIVER_PHONE}")
    print(f"Video Feed:     http://localhost:{config.FLASK_PORT}/video_feed")
    print(f"Video Analyze:  http://localhost:{config.FLASK_PORT}/api/video/analyze")
    print(f"Test Fall:      http://localhost:{config.FLASK_PORT}/test-fall")
    print("================================================================")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.DEBUG)
