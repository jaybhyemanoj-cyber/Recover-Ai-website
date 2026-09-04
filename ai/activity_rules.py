import time
import math
import logging
from collections import deque
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

import config

logger = logging.getLogger("ai.activity_rules")

class ActivityAnalyzer:
    """
    Temporal Activity, Fall & Gesture Analyzer using REAL YOLO Pose 17-Keypoints.
    
    YOLO keypoint indices:
      0: Nose, 1: Left Eye, 2: Right Eye, 3: Left Ear, 4: Right Ear
      5: Left Shoulder, 6: Right Shoulder
      7: Left Elbow, 8: Right Elbow
      9: Left Wrist, 10: Right Wrist
      11: Left Hip, 12: Right Hip
      13: Left Knee, 14: Right Knee
      15: Left Ankle, 16: Right Ankle
    """
    def __init__(
        self,
        mode: str = "live",
        fall_confirmation_frames: int = config.FALL_CONFIRMATION_FRAMES,
        inactivity_timeout: float = config.INACTIVITY_TIMEOUT,
        fall_alert_cooldown: float = config.FALL_ALERT_COOLDOWN,
        standing_cooldown: float = config.STANDING_SCREENSHOT_COOLDOWN,
        hand_cooldown: float = getattr(config, "HAND_GESTURE_ALERT_COOLDOWN", 10.0),
        bed_zone: List[float] = config.BED_ZONE
    ):
        self.mode = mode.lower()
        if self.mode == "live":
            # Live webcam mode: strict parameters preventing false alerts while sitting
            self.fall_confirmation_frames = max(7, fall_confirmation_frames)
            self.fall_cooldown = max(40.0, fall_alert_cooldown)
            self.floor_threshold = 0.65
            self.aspect_threshold = 0.72
            self.require_rapid_drop = True
        else:
            # Video upload mode: standard room/CCTV recorded video thresholds
            self.fall_confirmation_frames = max(3, fall_confirmation_frames)
            self.fall_cooldown = fall_alert_cooldown
            self.floor_threshold = 0.48
            self.aspect_threshold = 0.58
            self.require_rapid_drop = False

        self.inactivity_timeout = inactivity_timeout
        self.standing_cooldown = standing_cooldown
        self.hand_cooldown = hand_cooldown
        self.bed_zone = bed_zone  # [x1, y1, x2, y2] normalized

        # Temporal histories
        self.history: deque = deque(maxlen=45)
        self.wrist_history: deque = deque(maxlen=25)
        
        # State tracking & counters
        self.fall_counter = 0
        self.standing_counter = 0
        self.standing_captured = False
        self.in_fall_incident = False
        self.consecutive_normal_frames = 0
        self.last_logged_activity: Optional[str] = None
        
        # Cooldown timestamps
        self.last_fall_time: float = -999.0
        self.last_standing_time: float = -999.0
        self.last_hand_time: float = -999.0
        self.last_movement_time: float = time.time()
        
        self.was_in_bed: bool = False
        self.current_activity = "NORMAL"
        self.current_risk = "stable"

    def reset(self):
        """Reset temporal analyzer state."""
        self.history.clear()
        self.wrist_history.clear()
        self.fall_counter = 0
        self.standing_counter = 0
        self.standing_captured = False
        self.in_fall_incident = False
        self.consecutive_normal_frames = 0
        self.last_logged_activity = None
        self.last_fall_time = -999.0
        self.last_standing_time = -999.0
        self.last_hand_time = -999.0
        self.last_movement_time = time.time()
        self.was_in_bed = False
        self.current_activity = "NORMAL"
        self.current_risk = "stable"

    def analyze(
        self,
        detection_result: Dict[str, Any],
        frame_shape: Tuple[int, int],
        sim_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Analyze a single frame's REAL YOLO keypoints in the context of temporal history.
        Detects: STANDING, HAND MOVEMENT, CONFIRMED_FALL, BED_EXIT, WALKING, SITTING, NORMAL.
        """
        current_time = sim_time if sim_time is not None else time.time()
        h, w = frame_shape[:2]

        if not detection_result.get("detected") or not detection_result.get("keypoints"):
            self.fall_counter = 0
            self.consecutive_normal_frames += 1
            if self.consecutive_normal_frames >= 10:
                self.in_fall_incident = False

            return {
                "activity": self.current_activity if self.current_activity not in ("CONFIRMED_FALL", "POSSIBLE_FALL", "FALL_CANDIDATE") else "NORMAL",
                "risk_level": self.current_risk if self.current_risk not in ("critical", "warning") else "stable",
                "is_confirmed_event": False,
                "screenshot_event": None,
                "confidence": 0.0,
                "details": "No person detected in frame",
                "torso_angle": 0.0,
                "aspect_ratio": 0.0,
                "fall_counter": 0
            }

        kpts = detection_result["keypoints"]
        kpts_conf = detection_result.get("keypoints_conf", [])
        bbox = detection_result.get("bbox", [0, 0, w, h])
        confidence = float(detection_result.get("confidence", 0.0))

        person_thresh = getattr(config, "PERSON_CONFIDENCE_THRESHOLD", 0.45)
        kpt_thresh = getattr(config, "KEYPOINT_CONFIDENCE_THRESHOLD", 0.30)

        # Ignore low-confidence person detections
        if confidence < person_thresh:
            self.fall_counter = 0
            self.consecutive_normal_frames += 1
            if self.consecutive_normal_frames >= 10:
                self.in_fall_incident = False

            return {
                "activity": "NORMAL",
                "risk_level": "stable",
                "is_confirmed_event": False,
                "screenshot_event": None,
                "confidence": confidence,
                "details": f"Low confidence person detection ({int(confidence * 100)}%)",
                "torso_angle": 0.0,
                "aspect_ratio": 0.0,
                "fall_counter": 0,
                "visible_keypoints": 0
            }

        # 1. Extract Key Anatomical Joints with Confidence & Coordinate Verification
        # COCO Keypoints: 0: Nose, 5: Left Shoulder, 6: Right Shoulder, 9: Left Wrist, 10: Right Wrist,
        # 11: Left Hip, 12: Right Hip, 15: Left Ankle, 16: Right Ankle
        def is_valid_kpt(pt: Any, conf_val: float) -> bool:
            return (
                conf_val >= kpt_thresh and
                pt is not None and
                len(pt) >= 2 and
                (float(pt[0]) > 1.0 or float(pt[1]) > 1.0)
            )

        ls = kpts[5] if len(kpts) > 5 else [0, 0]
        rs = kpts[6] if len(kpts) > 6 else [0, 0]
        ls_conf = float(kpts_conf[5]) if len(kpts_conf) > 5 else 0.0
        rs_conf = float(kpts_conf[6]) if len(kpts_conf) > 6 else 0.0
        ls_valid = is_valid_kpt(ls, ls_conf)
        rs_valid = is_valid_kpt(rs, rs_conf)

        lh = kpts[11] if len(kpts) > 11 else [0, 0]
        rh = kpts[12] if len(kpts) > 12 else [0, 0]
        lh_conf = float(kpts_conf[11]) if len(kpts_conf) > 11 else 0.0
        rh_conf = float(kpts_conf[12]) if len(kpts_conf) > 12 else 0.0
        lh_valid = is_valid_kpt(lh, lh_conf)
        rh_valid = is_valid_kpt(rh, rh_conf)

        la = kpts[15] if len(kpts) > 15 else [0, 0]
        ra = kpts[16] if len(kpts) > 16 else [0, 0]
        la_conf = float(kpts_conf[15]) if len(kpts_conf) > 15 else 0.0
        ra_conf = float(kpts_conf[16]) if len(kpts_conf) > 16 else 0.0
        la_valid = is_valid_kpt(la, la_conf)
        ra_valid = is_valid_kpt(ra, ra_conf)

        lw = kpts[9] if len(kpts) > 9 else [0, 0]
        rw = kpts[10] if len(kpts) > 10 else [0, 0]
        lw_conf = float(kpts_conf[9]) if len(kpts_conf) > 9 else 0.0
        rw_conf = float(kpts_conf[10]) if len(kpts_conf) > 10 else 0.0
        lw_valid = is_valid_kpt(lw, lw_conf)
        rw_valid = is_valid_kpt(rw, rw_conf)

        nose = kpts[0] if len(kpts) > 0 else [0, 0]
        nose_conf = float(kpts_conf[0]) if len(kpts_conf) > 0 else 0.0
        nose_valid = is_valid_kpt(nose, nose_conf)

        visible_kpts_count = sum(1 for c, pt in zip(kpts_conf, kpts) if is_valid_kpt(pt, float(c)))

        # Torso keypoints visibility check (Shoulders & Hips must be valid for torso angle)
        has_shoulder = (ls_valid or rs_valid)
        has_hip = (lh_valid or rh_valid)
        has_torso = has_shoulder and has_hip

        if ls_valid and rs_valid:
            shoulder_mid = ((float(ls[0]) + float(rs[0])) / 2.0, (float(ls[1]) + float(rs[1])) / 2.0)
        elif ls_valid:
            shoulder_mid = (float(ls[0]), float(ls[1]))
        elif rs_valid:
            shoulder_mid = (float(rs[0]), float(rs[1]))
        else:
            shoulder_mid = (float(nose[0]), float(nose[1]) + 40.0) if nose_valid else (w / 2.0, h / 2.0)

        if lh_valid and rh_valid:
            hip_mid = ((float(lh[0]) + float(rh[0])) / 2.0, (float(lh[1]) + float(rh[1])) / 2.0)
        elif lh_valid:
            hip_mid = (float(lh[0]), float(lh[1]))
        elif rh_valid:
            hip_mid = (float(rh[0]), float(rh[1]))
        else:
            hip_mid = (shoulder_mid[0], min(float(h), shoulder_mid[1] + 120.0))

        if la_valid and ra_valid:
            ankle_mid = ((float(la[0]) + float(ra[0])) / 2.0, (float(la[1]) + float(ra[1])) / 2.0)
        elif la_valid:
            ankle_mid = (float(la[0]), float(la[1]))
        elif ra_valid:
            ankle_mid = (float(ra[0]), float(ra[1]))
        else:
            ankle_mid = hip_mid

        # 2. Kinematic Feature Calculations
        if has_torso:
            dx = abs(shoulder_mid[0] - hip_mid[0])
            dy = hip_mid[1] - shoulder_mid[1]  # positive when shoulders are above hips
            if dy <= 0:
                torso_angle = 90.0
            else:
                torso_angle = math.degrees(math.atan2(dx, max(0.001, dy)))
        else:
            torso_angle = 15.0

        # Bounding box geometry
        bw = max(1, bbox[2] - bbox[0])
        bh = max(1, bbox[3] - bbox[1])
        aspect_ratio = bw / float(bh)

        # Vertical body span in frame
        top_y = min(float(nose[1]) if nose_valid else shoulder_mid[1], shoulder_mid[1])
        bottom_y = max(ankle_mid[1] if (la_valid or ra_valid) else hip_mid[1], hip_mid[1])
        vertical_span_norm = abs(bottom_y - top_y) / float(h)

        # Normalized centroid position
        norm_center_x = (bbox[0] + bbox[2]) / (2.0 * w)
        norm_center_y = (bbox[1] + bbox[3]) / (2.0 * h)

        # Bed Zone Check
        in_bed_zone = (
            self.bed_zone[0] <= norm_center_x <= self.bed_zone[2] and
            self.bed_zone[1] <= norm_center_y <= self.bed_zone[3]
        )

        # 3. Multi-Factor Movement Dynamics & Rapid Descent Calculation
        # Check temporal history for downward velocity (hip drop and center-of-mass drop)
        has_rapid_drop = False
        delta_hip_y = 0.0
        delta_center_y = 0.0

        if len(self.history) >= 2:
            recent_frames = list(self.history)[-12:]  # Look back across recent ~1-1.5 seconds
            past_hips = [f["hip_y"] for f in recent_frames if f.get("has_torso")]
            past_cys = [f["norm_y"] for f in recent_frames]

            if past_hips:
                min_past_hip = min(past_hips)
                delta_hip_y = hip_mid[1] - min_past_hip
                if delta_hip_y > (h * 0.08):
                    has_rapid_drop = True

            if past_cys:
                min_past_cy = min(past_cys)
                delta_center_y = norm_center_y - min_past_cy
                if delta_center_y > 0.08:
                    has_rapid_drop = True

        # Floor position check (uses mode-specific floor threshold)
        is_floor_level = (norm_center_y > self.floor_threshold or hip_mid[1] > (h * self.floor_threshold))
        is_deep_floor = (norm_center_y > 0.65 or hip_mid[1] > (h * 0.65))

        # Record in temporal body history
        frame_data = {
            "time": current_time,
            "hip_y": hip_mid[1],
            "hip_x": hip_mid[0],
            "shoulder_y": shoulder_mid[1],
            "torso_angle": torso_angle,
            "aspect_ratio": aspect_ratio,
            "vertical_span": vertical_span_norm,
            "norm_y": norm_center_y,
            "has_torso": has_torso
        }
        self.history.append(frame_data)

        # Record in wrist/arm trajectory history
        wrist_data = {
            "time": current_time,
            "rw_x": float(rw[0]) if rw_valid else None,
            "rw_y": float(rw[1]) if rw_valid else None,
            "lw_x": float(lw[0]) if lw_valid else None,
            "lw_y": float(lw[1]) if lw_valid else None,
            "shoulder_x": shoulder_mid[0]
        }
        self.wrist_history.append(wrist_data)

        # 4. Comprehensive Fall Posture & Kinematic Condition Evaluation
        if self.mode == "live":
            # Live webcam mode: Sitting at a desk/chair MUST NEVER trigger false alerts.
            # Requires rapid downward drop OR deep horizontal floor lie-down
            is_horizontal_posture = (
                (has_rapid_drop and (aspect_ratio > 0.48 or torso_angle > 20.0 or is_floor_level)) or
                (is_floor_level and torso_angle > 45.0 and aspect_ratio > self.aspect_threshold)
            )
            is_ground_or_dropped = (has_rapid_drop or (is_floor_level and torso_angle > 35.0))
        else:
            # Video upload mode: Standard recorded CCTV room thresholds
            is_horizontal_posture = (
                torso_angle > 45.0 or
                aspect_ratio > self.aspect_threshold or
                (is_floor_level and (aspect_ratio > 0.52 or torso_angle > 24.0)) or
                (has_rapid_drop and (aspect_ratio > 0.42 or torso_angle > 18.0 or is_floor_level))
            )
            is_ground_or_dropped = (has_rapid_drop or is_floor_level)

        # Bed zone check: only normal if resting quietly in bed zone without rapid drop and at normal bed level
        is_lying_in_bed_normal = (
            in_bed_zone and
            not has_rapid_drop and
            norm_center_y < 0.42 and
            hip_mid[1] < (h * 0.42) and
            aspect_ratio < 0.85
        )

        is_fall_candidate = (
            confidence >= person_thresh and
            is_horizontal_posture and
            is_ground_or_dropped and
            not is_lying_in_bed_normal
        )

        # Multi-Frame Verification State Machine:
        # NORMAL -> FALL_CANDIDATE -> VERIFYING -> CONFIRMED_FALL -> INCIDENT_ACTIVE
        if is_fall_candidate:
            self.fall_counter += 1
            self.consecutive_normal_frames = 0
            print("[INFO] FALL_CANDIDATE")
            v_step = min(self.fall_counter, self.fall_confirmation_frames)
            print(f"[INFO] FALL_VERIFICATION: {v_step}/{self.fall_confirmation_frames}")
            logger.info(f"[INFO] FALL_VERIFICATION: Frame {v_step}/{self.fall_confirmation_frames} verifying...")
        else:
            # Resilient counter: if already in incident or verifying, single noisy frame decrements rather than wiping immediately
            if self.fall_counter > 0 and not self.in_fall_incident:
                self.fall_counter = max(0, self.fall_counter - 1)
            elif not self.in_fall_incident:
                self.fall_counter = 0

            self.consecutive_normal_frames += 1
            if self.consecutive_normal_frames >= 10 and self.in_fall_incident:
                self.in_fall_incident = False
                print("[INFO] INCIDENT_RECOVERED")
                logger.info("[INFO] INCIDENT_RECOVERED: Patient posture restored to normal.")

        # 5. Hand Right -> Left Movement Detection (Real YOLO Wrist/Elbow keypoints)
        # Suppress hand movement classification when in floor/fall candidate posture
        hand_right_to_left_detected = False
        if (len(self.wrist_history) >= 4 and
            self.fall_counter == 0 and
            not self.in_fall_incident and
            not is_horizontal_posture and
            not is_ground_or_dropped):
            recent_wrists = list(self.wrist_history)
            for lookback in [3, 4, 6, 8, 10]:
                if len(recent_wrists) > lookback:
                    past_entry = recent_wrists[-lookback]
                    curr_entry = recent_wrists[-1]

                    if past_entry["rw_x"] is not None and curr_entry["rw_x"] is not None:
                        delta_x = past_entry["rw_x"] - curr_entry["rw_x"]
                        delta_y = abs((curr_entry["rw_y"] or 0) - (past_entry["rw_y"] or 0))
                        if delta_x > (w * 0.08) and delta_x > (1.1 * delta_y):
                            hand_right_to_left_detected = True
                            break

                    if past_entry["lw_x"] is not None and curr_entry["lw_x"] is not None:
                        delta_x = past_entry["lw_x"] - curr_entry["lw_x"]
                        delta_y = abs((curr_entry["lw_y"] or 0) - (past_entry["lw_y"] or 0))
                        if delta_x > (w * 0.08) and delta_x > (1.1 * delta_y):
                            hand_right_to_left_detected = True
                            break

        # 6. Standing Detection & Stability Counter
        is_standing_posture = (
            has_torso and
            torso_angle < 25.0 and
            aspect_ratio < 0.45 and
            vertical_span_norm > 0.60 and
            hip_mid[1] < (h * 0.58) and
            confidence > 0.45
        )

        if is_standing_posture:
            self.standing_counter += 1
            if self.standing_counter >= 3:
                if self.in_fall_incident:
                    self.in_fall_incident = False
                    print("[INFO] INCIDENT_RECOVERED")
                    logger.info("[INFO] INCIDENT_RECOVERED: Confirmed standing posture restored.")
                self.fall_counter = 0
        else:
            self.standing_counter = max(0, self.standing_counter - 1)

        # 7. Event Classification & Strict Fall Alert Triggers
        detected_event = "NORMAL"
        risk_level = "stable"
        is_confirmed = False
        screenshot_event: Optional[str] = None
        details = "Normal patient posture"

        # PRIORITY 1: Fall Detection (Critical Emergency)
        if self.fall_counter >= self.fall_confirmation_frames:
            detected_event = "CONFIRMED_FALL"
            risk_level = "critical"
            details = f"Fall detected: Horizontal posture confirmed (Angle: {int(torso_angle)}°, Aspect Ratio: {aspect_ratio:.2f})"

            time_since_last_fall = current_time - self.last_fall_time
            if not self.in_fall_incident and (time_since_last_fall > self.fall_cooldown):
                print("[ALERT] CONFIRMED_FALL")
                logger.warning(f"[ALERT] CONFIRMED_FALL: Confirmed fall detected after {self.fall_confirmation_frames} verified frames.")
                is_confirmed = True
                screenshot_event = "CONFIRMED_FALL"
                self.last_fall_time = current_time
                self.in_fall_incident = True
            else:
                print("[INFO] ALERT_COOLDOWN")
                logger.info("[INFO] ALERT_COOLDOWN: Cooldown active; duplicate notification suppressed.")
                is_confirmed = False

        # PRIORITY 1B: Fall Candidate / Verification (Temporary Non-Emergency State)
        elif self.fall_counter > 0:
            detected_event = "FALL_CANDIDATE"
            risk_level = "warning"
            details = f"Possible Fall — Verifying frame {self.fall_counter}/{self.fall_confirmation_frames}..."
            is_confirmed = False
            screenshot_event = None

        # PRIORITY 2: Hand Movement (Non-Emergency, NTFY Skipped)
        elif hand_right_to_left_detected:
            detected_event = "HAND_MOVEMENT"
            risk_level = "attention"
            details = "Patient hand gesture detected"
            if self.last_logged_activity != "HAND_MOVEMENT":
                print("[INFO] Activity detected: HAND MOVEMENT")
                print("[INFO] No emergency — NTFY skipped")
                self.last_logged_activity = "HAND_MOVEMENT"
            is_confirmed = False

        # PRIORITY 3: Standing Posture (Non-Emergency, NTFY Skipped)
        elif is_standing_posture and self.standing_counter >= 3:
            detected_event = "STANDING"
            risk_level = "stable"
            details = f"Upright standing posture confirmed (Angle: {int(torso_angle)}°)"
            if self.last_logged_activity != "STANDING":
                print("[INFO] Activity detected: STANDING")
                print("[INFO] No emergency — NTFY skipped")
                self.last_logged_activity = "STANDING"
            is_confirmed = False

        # PRIORITY 4: Bed Exit (Non-Emergency, NTFY Skipped)
        elif self.was_in_bed and not in_bed_zone and not is_horizontal_posture and not is_ground_or_dropped:
            detected_event = "BED_EXIT"
            risk_level = "attention"
            details = "Patient exited designated bed zone"
            if self.last_logged_activity != "BED_EXIT":
                print("[INFO] Activity detected: BED EXIT")
                print("[INFO] No emergency — NTFY skipped")
                self.last_logged_activity = "BED_EXIT"
            is_confirmed = False

        else:
            if not has_torso or torso_angle < 45.0:
                detected_event = "SITTING"
                details = "Resting/sitting posture"
            elif vertical_span_norm > 0.45:
                detected_event = "WALKING"
                details = "Patient walking/moving"
            else:
                detected_event = "NORMAL"
                details = "Stable resting posture"

            risk_level = "stable"
            is_confirmed = False
            if self.last_logged_activity != detected_event and self.fall_counter == 0:
                print(f"[INFO] Activity detected: {detected_event}")
                print("[INFO] No emergency — NTFY skipped")
                self.last_logged_activity = detected_event

        # Update persistent state
        self.was_in_bed = in_bed_zone
        self.current_activity = detected_event
        self.current_risk = risk_level

        return {
            "activity": detected_event,
            "risk_level": risk_level,
            "is_confirmed_event": is_confirmed,
            "screenshot_event": screenshot_event,
            "confidence": confidence,
            "details": details,
            "torso_angle": round(torso_angle, 1),
            "aspect_ratio": round(aspect_ratio, 2),
            "vertical_span": round(vertical_span_norm, 2),
            "fall_counter": self.fall_counter,
            "standing_counter": self.standing_counter,
            "in_bed_zone": in_bed_zone,
            "has_rapid_drop": has_rapid_drop,
            "delta_hip_y": round(delta_hip_y, 1),
            "delta_center_y": round(delta_center_y, 2)
        }

# Global Activity Analyzer Singleton
activity_analyzer = ActivityAnalyzer()
