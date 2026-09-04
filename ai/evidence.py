"""
Incident Evidence Generator & Dispatcher
-----------------------------------------
Captures and annotates the exact single keyframe corresponding to confirmed abnormal
events (e.g. falls, hand gestures), enforces deduplication, saves to disk, and
dispatches urgent alerts via NotificationService (NTFY + WhatsApp).

Zero continuous video recording is performed (Privacy Mandate).
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import cv2
import numpy as np

import config
from ai.notifications import notification_service, send_fall_alert

logger = logging.getLogger("ai.evidence")

# In-memory deduplication cache: (patient_id, event_type) -> (timestamp, filepath, filename)
_EVIDENCE_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_DEDUPLICATION_WINDOW_SEC = 15.0


def create_evidence_screenshot(
    frame: np.ndarray,
    patient_id: str,
    event_type: str,
    risk_level: str,
    confidence: float,
    source: str = "yolo",
    force_new: bool = False
) -> str:
    """
    Annotate and save the single keyframe corresponding to confirmed fall event.
    Screenshots are strictly captured only for CONFIRMED_FALL.
    Reuses existing screenshot if identical incident was recorded within deduplication window.
    """
    clean_type = str(event_type).upper().strip()
    if clean_type != "CONFIRMED_FALL" and "FALL" not in clean_type:
        logger.info(f"Skipping screenshot creation for non-emergency event: {event_type}")
        return ""

    now = time.time()
    cache_key = f"{patient_id}_{event_type}"

    # Deduplication check
    if not force_new and cache_key in _EVIDENCE_CACHE:
        cached_entry = _EVIDENCE_CACHE[cache_key]
        if (now - cached_entry["time"]) < CACHE_DEDUPLICATION_WINDOW_SEC:
            if os.path.isfile(cached_entry["filepath"]):
                logger.info(f"Reusing existing incident screenshot for {cache_key}: {cached_entry['filepath']}")
                return cached_entry["filepath"]

    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    display_time = timestamp.strftime("%Y-%m-%d %I:%M:%S %p")

    clean_event = "confirmed_fall"
    clean_pid = patient_id.replace("-", "").replace(" ", "_")
    filename = f"{clean_event}_{clean_pid}_{timestamp_str}.jpg"
    filepath = str(config.SCREENSHOT_DIR / filename)

    h, w = frame.shape[:2]
    evidence_frame = frame.copy()

    # Draw Evidence Top Header Banner
    cv2.rectangle(evidence_frame, (0, 0), (w, 50), (15, 23, 42), -1)

    header_color = (225, 29, 72) if str(risk_level).lower() in ("critical", "emergency") else (245, 158, 11)  # BGR
    cv2.circle(evidence_frame, (20, 25), 8, header_color, -1)

    title_text = f"EVENT: {event_type.upper()} ({risk_level.upper()}) | SOURCE: {source.upper()}"
    cv2.putText(
        evidence_frame,
        title_text,
        (38, 31),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )

    # Draw Bottom Telemetry Banner
    cv2.rectangle(evidence_frame, (0, h - 45), (w, h), (15, 23, 42), -1)

    telemetry_text = f"PATIENT: {patient_id} | CONFIDENCE: {int(confidence * 100)}% | TIME: {display_time}"
    cv2.putText(
        evidence_frame,
        telemetry_text,
        (16, h - 16),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (220, 230, 242),
        1
    )

    # Privacy label
    cv2.putText(
        evidence_frame,
        "PRIVACY: SINGLE KEYFRAME ONLY",
        (w - 260, 31),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.42,
        (52, 211, 153),
        1
    )

    # Save to disk
    cv2.imwrite(filepath, evidence_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    print("[ALERT] SCREENSHOT_CREATED")
    logger.info(f"[ALERT] SCREENSHOT_CREATED: Saved event evidence screenshot: {filepath}")

    # Update cache
    _EVIDENCE_CACHE[cache_key] = {
        "time": now,
        "filepath": filepath,
        "filename": filename
    }

    return filepath


def handle_confirmed_event(
    frame: np.ndarray,
    patient_id: str,
    event_type: str,
    risk_level: str,
    confidence: float,
    source: str = "yolo"
) -> Dict[str, Any]:
    """
    Full pipeline triggered on confirmed event:
    1. Capture & annotate single frame with deduplication ONLY for CONFIRMED_FALL.
    2. Save to static/screenshots/.
    3. Dispatch urgent alert via send_fall_alert (NTFY + WhatsApp) ONLY for confirmed critical falls.
    4. Return structured event summary.
    """
    evt_upper = str(event_type).upper().strip()
    norm_risk = str(risk_level).upper().strip()
    is_emergency_fall = (evt_upper == "CONFIRMED_FALL") and (norm_risk in ("CRITICAL", "EMERGENCY"))

    screenshot_path = ""
    filename = None
    screenshot_url = None

    if is_emergency_fall:
        screenshot_path = create_evidence_screenshot(
            frame=frame,
            patient_id=patient_id,
            event_type=event_type,
            risk_level=risk_level,
            confidence=confidence,
            source=source
        )
        if screenshot_path:
            filename = os.path.basename(screenshot_path)
            screenshot_url = f"/static/screenshots/{filename}"

    if is_emergency_fall:
        event_dict = {
            "type": "CONFIRMED_FALL",
            "event_type": "CONFIRMED_FALL",
            "patient_id": patient_id,
            "risk_level": "CRITICAL",
            "confidence": confidence,
            "source": source,
            "screenshot_path": screenshot_path if screenshot_path else None,
            "time": datetime.now().strftime("%I:%M %p")
        }
        ntfy_res = send_fall_alert(event_dict)
        tg_res = notification_service.telegram.send(
            event_type=event_type,
            patient_id=patient_id,
            risk_level=risk_level,
            screenshot_path=screenshot_path if screenshot_path else None,
            source=source,
            confidence=confidence
        )
        wa_res = notification_service.whatsapp.send(
            event_type=event_type,
            patient_id=patient_id,
            risk_level=risk_level,
            source=source
        )
        dispatch_result = {
            "success": ntfy_res.get("success", False) or tg_res.get("success", False) or wa_res.get("success", False),
            "ntfy": ntfy_res,
            "telegram": tg_res,
            "whatsapp": wa_res
        }
    else:
        print("[INFO] No emergency — NTFY skipped")
        dispatch_result = {
            "success": False,
            "ntfy": {"channel": "ntfy", "success": False, "skipped": True, "reason": "No emergency — NTFY skipped"},
            "telegram": {"channel": "telegram", "success": False, "skipped": True},
            "whatsapp": {"channel": "whatsapp", "success": False, "skipped": True}
        }

    alert_id = f"ALT-{int(time.time() * 1000) % 1000000:06d}"
    print("[ALERT] INCIDENT_CREATED")
    logger.info(f"[ALERT] INCIDENT_CREATED: {alert_id} ({event_type}) for Patient {patient_id}")

    return {
        "alert_id": alert_id,
        "patient_id": patient_id,
        "event_type": event_type,
        "risk_level": risk_level,
        "confidence": confidence,
        "source": source,
        "timestamp": datetime.now().strftime("%I:%M %p"),
        "timestamp_iso": datetime.now().isoformat(),
        "screenshot_filename": filename,
        "screenshot_url": screenshot_url,
        "screenshot_path": screenshot_path,
        "ntfy": dispatch_result.get("ntfy", {}),
        "telegram": dispatch_result.get("telegram", {}),
        "whatsapp": dispatch_result.get("whatsapp", {}),
        "dispatch": dispatch_result
    }

