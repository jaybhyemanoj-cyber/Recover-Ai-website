import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import cv2
import numpy as np
import time
import config
from ai.detector import pose_detector
from ai.activity_rules import ActivityAnalyzer

video_path = "dataset/real_fall_video.mp4"
cap = cv2.VideoCapture(video_path)

fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
duration = total_frames / fps if fps > 0 else 0

print(f"=== VIDEO METADATA ===")
print(f"Path: {video_path}")
print(f"Resolution: {width}x{height}")
print(f"FPS: {fps}")
print(f"Total frames: {total_frames}")
print(f"Duration: {duration:.2f}s")

# Let's test with current sampling_step in video_analyzer.py:
sampling_step = max(1, min(config.VIDEO_FRAME_INTERVAL, int(fps // 10) or 2))
print(f"VIDEO_FRAME_INTERVAL config: {config.VIDEO_FRAME_INTERVAL}")
print(f"Calculated sampling_step: {sampling_step}")

analyzer = ActivityAnalyzer(
    fall_confirmation_frames=min(3, config.FALL_CONFIRMATION_FRAMES),
    inactivity_timeout=config.INACTIVITY_TIMEOUT,
    fall_alert_cooldown=config.FALL_ALERT_COOLDOWN,
    standing_cooldown=config.STANDING_SCREENSHOT_COOLDOWN,
    hand_cooldown=getattr(config, "HAND_GESTURE_ALERT_COOLDOWN", 10.0),
    bed_zone=config.BED_ZONE
)

frame_idx = 0
results = []

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        break

    if frame_idx % sampling_step == 0:
        current_sec = frame_idx / fps
        detection = pose_detector.detect(frame, draw_overlay=False)
        analysis = analyzer.analyze(detection, (height, width), sim_time=current_sec)
        
        kpts = detection.get("keypoints", [])
        kpts_conf = detection.get("keypoints_conf", [])
        conf = detection.get("confidence", 0.0)
        is_person = detection.get("detected", False)
        
        ls = kpts[5] if len(kpts) > 5 else [0, 0]
        rs = kpts[6] if len(kpts) > 6 else [0, 0]
        lh = kpts[11] if len(kpts) > 11 else [0, 0]
        rh = kpts[12] if len(kpts) > 12 else [0, 0]
        
        ls_c = kpts_conf[5] if len(kpts_conf) > 5 else 0.0
        rs_c = kpts_conf[6] if len(kpts_conf) > 6 else 0.0
        lh_c = kpts_conf[11] if len(kpts_conf) > 11 else 0.0
        rh_c = kpts_conf[12] if len(kpts_conf) > 12 else 0.0
        
        results.append({
            "frame_idx": frame_idx,
            "time": current_sec,
            "person": is_person,
            "conf": conf,
            "ls": (ls, ls_c),
            "rs": (rs, rs_c),
            "lh": (lh, lh_c),
            "rh": (rh, rh_c),
            "torso_angle": analysis.get("torso_angle", 0.0),
            "aspect_ratio": analysis.get("aspect_ratio", 0.0),
            "activity": analysis.get("activity"),
            "risk": analysis.get("risk_level"),
            "fall_counter": analysis.get("fall_counter", 0),
            "in_bed_zone": analysis.get("in_bed_zone", False),
            "details": analysis.get("details", "")
        })

    frame_idx += 1

cap.release()

print(f"\nTotal sampled frames: {len(results)}")
activities = [r["activity"] for r in results]
print(f"Activities seen: {set(activities)}")
for r in results:
    print(f"Frame {r['frame_idx']:04d} ({r['time']:.2f}s) | Conf={r['conf']:.2f} | Act={r['activity']:<15} | Angle={r['torso_angle']:5.1f} | AR={r['aspect_ratio']:.2f} | FallCnt={r['fall_counter']} | Bed={r['in_bed_zone']} | Det={r['details']}")

