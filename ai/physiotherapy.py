"""
AI Physiotherapy / Range-of-Motion (ROM) Coach Module
-----------------------------------------------------
Reuses existing Ultralytics YOLOv8 Pose 17-Keypoints for real-time joint angle
calculation, state-machine repetition counting, and posture feedback.

Non-Diagnostic Medical Disclaimer:
This physiotherapy coach module is an assistive recovery tracking tool designed
for rehabilitation exercise logging. It does not provide medical diagnoses or
replace professional orthopedic physical therapy consultations.
"""

import time
import math
import logging
from typing import Dict, Any, List, Optional, Tuple

import config

logger = logging.getLogger("ai.physiotherapy")

# COCO Keypoint Index Mapping
KP_NOSE = 0
KP_LEFT_SHOULDER = 5
KP_RIGHT_SHOULDER = 6
KP_LEFT_ELBOW = 7
KP_RIGHT_ELBOW = 8
KP_LEFT_WRIST = 9
KP_RIGHT_WRIST = 10
KP_LEFT_HIP = 11
KP_RIGHT_HIP = 12
KP_LEFT_KNEE = 13
KP_RIGHT_KNEE = 14
KP_LEFT_ANKLE = 15
KP_RIGHT_ANKLE = 16

EXERCISE_DEFINITIONS = {
    "knee_flexion": {
        "name": "Knee Flexion (Knee Bend)",
        "target_joint": "Knee (Hip - Knee - Ankle)",
        "start_angle": 160.0,       # Near straight leg
        "target_angle": 95.0,        # Bent knee angle
        "direction": "decrease",     # Angle decreases as knee bends (180 -> 90)
        "tolerance": 12.0,
        "default_target_reps": 10,
        "instructions": "Bend your knee slowly bringing your heel towards your glutes, then extend back."
    },
    "leg_raise": {
        "name": "Straight Leg Raise",
        "target_joint": "Hip (Torso - Hip - Knee)",
        "start_angle": 15.0,        # Leg flat/down
        "target_angle": 55.0,       # Leg raised ~50-60 deg
        "direction": "increase",    # Angle increases as leg lifts
        "tolerance": 10.0,
        "default_target_reps": 8,
        "instructions": "Keep your leg straight and lift upward towards the ceiling, then lower with control."
    },
    "arm_movement": {
        "name": "Shoulder Abduction / Arm Raise",
        "target_joint": "Shoulder (Torso - Shoulder - Elbow)",
        "start_angle": 25.0,        # Arm at side
        "target_angle": 90.0,       # Arm raised perpendicular or overhead
        "direction": "increase",    # Angle increases as arm lifts
        "tolerance": 12.0,
        "default_target_reps": 10,
        "instructions": "Raise your arm outward and upward to shoulder height, then gently lower."
    },
    "elbow_flexion": {
        "name": "Elbow Flexion (Arm Curl)",
        "target_joint": "Elbow (Shoulder - Elbow - Wrist)",
        "start_angle": 150.0,       # Straight arm
        "target_angle": 60.0,       # Curled arm
        "direction": "decrease",    # Angle decreases as elbow flexes
        "tolerance": 10.0,
        "default_target_reps": 10,
        "instructions": "Bend your elbow bringing hand to shoulder, then extend fully."
    }
}


def calculate_3pt_angle(
    a: Tuple[float, float],
    b: Tuple[float, float],
    c: Tuple[float, float]
) -> float:
    """
    Calculate the interior angle at vertex point B formed by points A-B-C in degrees.
    Formula: arccos((BA . BC) / (|BA| * |BC|))
    """
    ba_x = a[0] - b[0]
    ba_y = a[1] - b[1]
    bc_x = c[0] - b[0]
    bc_y = c[1] - b[1]

    mag_ba = math.hypot(ba_x, ba_y)
    mag_bc = math.hypot(bc_x, bc_y)

    if mag_ba < 1e-6 or mag_bc < 1e-6:
        return 0.0

    dot = (ba_x * bc_x) + (ba_y * bc_y)
    cosine_val = dot / (mag_ba * mag_bc)
    cosine_val = max(-1.0, min(1.0, cosine_val))

    angle_rad = math.acos(cosine_val)
    return math.degrees(angle_rad)


class PhysiotherapyCoach:
    """
    State-based repetition counter and Range-of-Motion (ROM) coach.
    Reuses YOLO Pose keypoints without additional heavy neural networks.
    """
    def __init__(self):
        self.active_exercise: str = "knee_flexion"
        self.rep_count: int = 0
        self.target_reps: int = 10
        self.state: str = "START"  # States: START -> IN_MOTION -> TARGET_ZONE -> RETURNING -> COUNTED
        
        self.current_angle: float = 0.0
        self.peak_angle_in_rep: float = 0.0
        self.target_angle: float = 95.0
        self.start_angle: float = 160.0
        
        self.target_hold_frames: int = 0
        self.last_rep_time: float = -999.0
        self.rep_cooldown: float = config.PHYSIO_REP_COOLDOWN
        self.conf_threshold: float = config.PHYSIO_KEYPOINT_CONF_THRESHOLD

        self.feedback_message: str = "Position yourself in front of camera to begin"
        self.is_tracking: bool = False
        self.side: str = "auto"  # 'left', 'right', or 'auto'
        self.session_history: List[Dict[str, Any]] = []

    @property
    def exercise_name(self) -> str:
        defn = EXERCISE_DEFINITIONS.get(self.active_exercise, EXERCISE_DEFINITIONS["knee_flexion"])
        return defn["name"]

    def set_exercise(self, exercise_name: str, side: str = "auto", target_reps: Optional[int] = None):
        """Configure exercise mode and reset session counter."""
        if exercise_name not in EXERCISE_DEFINITIONS:
            exercise_name = "knee_flexion"

        defn = EXERCISE_DEFINITIONS[exercise_name]
        self.active_exercise = exercise_name
        self.side = side
        self.rep_count = 0
        self.target_reps = target_reps or defn["default_target_reps"]
        self.state = "START"
        self.current_angle = 0.0
        self.peak_angle_in_rep = 0.0
        self.start_angle = defn["start_angle"]
        self.target_angle = defn["target_angle"]
        self.target_hold_frames = 0
        self.feedback_message = f"Ready: {defn['name']}. {defn['instructions']}"
        self.session_history = []
        logger.info(f"Physio coach set to: {exercise_name} (Target Reps: {self.target_reps}, Side: {self.side})")

    def reset_counter(self):
        """Reset rep count and state."""
        self.rep_count = 0
        self.state = "START"
        self.target_hold_frames = 0
        self.session_history = []
        self.feedback_message = "Counter reset. Begin your first repetition."

    def process_keypoints(
        self,
        keypoints: List[List[float]],
        keypoints_conf: List[float],
        sim_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process a single frame of YOLO 17 keypoints.
        Calculates joint angle, updates state machine, and provides real-time coaching feedback.
        """
        current_time = sim_time if sim_time is not None else time.time()
        defn = EXERCISE_DEFINITIONS.get(self.active_exercise, EXERCISE_DEFINITIONS["knee_flexion"])

        if not keypoints or len(keypoints) < 17:
            self.is_tracking = False
            return self._build_response(False, 0.0, "Patient keypoints not detected. Please face camera.")

        side_to_use = self._select_tracking_side(keypoints_conf)
        angle, tracking_valid = self._calculate_exercise_angle(keypoints, keypoints_conf, side_to_use)

        if not tracking_valid:
            self.is_tracking = False
            return self._build_response(False, 0.0, "Adjust position — joint keypoints partially obscured.")

        self.is_tracking = True
        self.current_angle = round(angle, 1)

        # Execute State-Machine Repetition Counter with Hysteresis & Debounce
        self._update_state_machine(angle, defn, current_time)

        return self._build_response(True, self.current_angle, self.feedback_message, side_to_use)

    def _select_tracking_side(self, confs: List[float]) -> str:
        """Select left or right side based on user setting or joint confidence."""
        if self.side in ("left", "right"):
            return self.side

        if self.active_exercise in ("knee_flexion", "leg_raise"):
            left_conf = (confs[KP_LEFT_HIP] + confs[KP_LEFT_KNEE] + confs[KP_LEFT_ANKLE]) / 3.0
            right_conf = (confs[KP_RIGHT_HIP] + confs[KP_RIGHT_KNEE] + confs[KP_RIGHT_ANKLE]) / 3.0
            return "left" if left_conf >= right_conf else "right"
        else:
            left_conf = (confs[KP_LEFT_SHOULDER] + confs[KP_LEFT_ELBOW] + confs[KP_LEFT_WRIST]) / 3.0
            right_conf = (confs[KP_RIGHT_SHOULDER] + confs[KP_RIGHT_ELBOW] + confs[KP_RIGHT_WRIST]) / 3.0
            return "left" if left_conf >= right_conf else "right"

    def _calculate_exercise_angle(
        self,
        kpts: List[List[float]],
        confs: List[float],
        side: str
    ) -> Tuple[float, bool]:
        """Calculate the precise joint angle for the configured exercise and side."""
        thresh = self.conf_threshold

        try:
            if self.active_exercise == "knee_flexion":
                # Knee angle: Hip -> Knee -> Ankle
                hip_idx = KP_LEFT_HIP if side == "left" else KP_RIGHT_HIP
                knee_idx = KP_LEFT_KNEE if side == "left" else KP_RIGHT_KNEE
                ankle_idx = KP_LEFT_ANKLE if side == "left" else KP_RIGHT_ANKLE

                if confs[hip_idx] < thresh or confs[knee_idx] < thresh or confs[ankle_idx] < thresh:
                    return 0.0, False

                angle = calculate_3pt_angle(
                    (kpts[hip_idx][0], kpts[hip_idx][1]),
                    (kpts[knee_idx][0], kpts[knee_idx][1]),
                    (kpts[ankle_idx][0], kpts[ankle_idx][1])
                )
                return angle, True

            elif self.active_exercise == "leg_raise":
                # Leg raise angle: Shoulder -> Hip -> Knee
                sh_idx = KP_LEFT_SHOULDER if side == "left" else KP_RIGHT_SHOULDER
                hip_idx = KP_LEFT_HIP if side == "left" else KP_RIGHT_HIP
                knee_idx = KP_LEFT_KNEE if side == "left" else KP_RIGHT_KNEE

                if confs[hip_idx] < thresh or confs[knee_idx] < thresh:
                    return 0.0, False

                angle = calculate_3pt_angle(
                    (kpts[sh_idx][0], kpts[sh_idx][1]),
                    (kpts[hip_idx][0], kpts[hip_idx][1]),
                    (kpts[knee_idx][0], kpts[knee_idx][1])
                )
                elevation_angle = abs(180.0 - angle)
                return elevation_angle, True

            elif self.active_exercise == "arm_movement":
                # Arm abduction: Hip -> Shoulder -> Elbow
                hip_idx = KP_LEFT_HIP if side == "left" else KP_RIGHT_HIP
                sh_idx = KP_LEFT_SHOULDER if side == "left" else KP_RIGHT_SHOULDER
                elbow_idx = KP_LEFT_ELBOW if side == "left" else KP_RIGHT_ELBOW

                if confs[sh_idx] < thresh or confs[elbow_idx] < thresh:
                    return 0.0, False

                angle = calculate_3pt_angle(
                    (kpts[hip_idx][0], kpts[hip_idx][1]),
                    (kpts[sh_idx][0], kpts[sh_idx][1]),
                    (kpts[elbow_idx][0], kpts[elbow_idx][1])
                )
                return angle, True

            elif self.active_exercise == "elbow_flexion":
                # Elbow flexion: Shoulder -> Elbow -> Wrist
                sh_idx = KP_LEFT_SHOULDER if side == "left" else KP_RIGHT_SHOULDER
                elbow_idx = KP_LEFT_ELBOW if side == "left" else KP_RIGHT_ELBOW
                wrist_idx = KP_LEFT_WRIST if side == "left" else KP_RIGHT_WRIST

                if confs[sh_idx] < thresh or confs[elbow_idx] < thresh or confs[wrist_idx] < thresh:
                    return 0.0, False

                angle = calculate_3pt_angle(
                    (kpts[sh_idx][0], kpts[sh_idx][1]),
                    (kpts[elbow_idx][0], kpts[elbow_idx][1]),
                    (kpts[wrist_idx][0], kpts[wrist_idx][1])
                )
                return angle, True

            return 0.0, False

        except Exception as e:
            logger.error(f"Error calculating joint angle: {e}")
            return 0.0, False

    def _update_state_machine(self, angle: float, defn: Dict[str, Any], current_time: float):
        """
        State Machine with Hysteresis:
        - direction == 'decrease' (e.g. Knee flexion: 180° start, bends down to <= 95°)
        - direction == 'increase' (e.g. Leg raise: 15° start, lifts up to >= 55°)
        """
        direction = defn["direction"]
        start_angle = defn["start_angle"]
        target_angle = defn["target_angle"]
        tol = defn["tolerance"]

        is_in_start_zone = (
            (angle >= start_angle - tol) if direction == "decrease" else (angle <= start_angle + tol)
        )
        is_in_target_zone = (
            (angle <= target_angle + tol) if direction == "decrease" else (angle >= target_angle - tol)
        )

        # STATE: START / READY
        if self.state == "START":
            if is_in_target_zone:
                self.state = "TARGET_ZONE"
                self.peak_angle_in_rep = angle
                self.feedback_message = f"Target reached ({int(angle)}°)! Now return smoothly to start position."
            elif not is_in_start_zone:
                self.state = "IN_MOTION"
                self.feedback_message = "Movement detected. Moving towards target angle..."
            else:
                self.feedback_message = "Good starting position. Begin your movement."

        # STATE: IN_MOTION
        elif self.state == "IN_MOTION":
            if is_in_target_zone:
                self.state = "TARGET_ZONE"
                self.peak_angle_in_rep = angle
                self.feedback_message = f"Target reached ({int(angle)}°)! Now return smoothly to start position."
            elif is_in_start_zone:
                self.state = "START"
                self.feedback_message = "Returned to start. Move further to reach target."
            else:
                remaining = abs(angle - target_angle)
                if remaining > 15:
                    self.feedback_message = f"Keep going! Move {int(remaining)}° further to hit target."
                else:
                    self.feedback_message = "Almost there! Complete the full movement."

        # STATE: TARGET_ZONE
        elif self.state == "TARGET_ZONE":
            if not is_in_target_zone:
                self.state = "RETURNING"
                self.feedback_message = "Returning to start position..."
            else:
                if direction == "decrease":
                    self.peak_angle_in_rep = min(self.peak_angle_in_rep, angle)
                else:
                    self.peak_angle_in_rep = max(self.peak_angle_in_rep, angle)
                self.feedback_message = "Holding peak position. Return gently to finish rep."

        # STATE: RETURNING -> COUNT REP
        elif self.state == "RETURNING":
            if is_in_start_zone:
                if (current_time - self.last_rep_time) >= self.rep_cooldown:
                    self.rep_count += 1
                    self.last_rep_time = current_time
                    self.session_history.append({
                        "rep": self.rep_count,
                        "peak_angle": round(self.peak_angle_in_rep, 1),
                        "timestamp": current_time
                    })

                    if self.rep_count >= self.target_reps:
                        self.feedback_message = f"Target completed! {self.rep_count}/{self.target_reps} reps achieved. Great recovery work!"
                    else:
                        self.feedback_message = f"Repetition {self.rep_count} counted! Ready for next rep ({self.rep_count}/{self.target_reps})."

                self.state = "START"
                self.target_hold_frames = 0
            elif is_in_target_zone:
                self.state = "TARGET_ZONE"
                self.feedback_message = "Target position held."
            else:
                self.feedback_message = "Extend all the way back to starting position to complete rep."


    def _build_response(
        self,
        valid: bool,
        angle: float,
        feedback: str,
        side_used: str = "auto"
    ) -> Dict[str, Any]:
        """Compile structured telemetry dictionary."""
        defn = EXERCISE_DEFINITIONS.get(self.active_exercise, EXERCISE_DEFINITIONS["knee_flexion"])
        return {
            "exercise": self.active_exercise,
            "exercise_name": defn["name"],
            "target_joint": defn["target_joint"],
            "side": side_used,
            "is_tracking": valid,
            "current_angle": angle,
            "start_angle": defn["start_angle"],
            "target_angle": defn["target_angle"],
            "rep_count": self.rep_count,
            "target_reps": self.target_reps,
            "state": self.state,
            "feedback": feedback,
            "progress_pct": min(100, int((self.rep_count / max(1, self.target_reps)) * 100)),
            "disclaimer": "Assistive rehabilitation logging only. Follow surgeon's specified weight-bearing limits."
        }


# Global Physiotherapy Coach Singleton
physio_coach = PhysiotherapyCoach()
