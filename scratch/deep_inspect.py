import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import cv2
import numpy as np
import config
from ai.detector import pose_detector
from ai.activity_rules import ActivityAnalyzer

video_path = "dataset/real_fall_video.mp4"
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"Video {width}x{height}, {fps} fps, {total_frames} frames ({total_frames/fps:.1f}s)")

# Let's inspect every 10 frames from 0 to total_frames
analyzer = ActivityAnalyzer(
    fall_confirmation_frames=min(3, config.FALL_CONFIRMATION_FRAMES),
    inactivity_timeout=config.INACTIVITY_TIMEOUT,
    fall_alert_cooldown=config.FALL_ALERT_COOLDOWN,
    bed_zone=config.BED_ZONE
)

for f_idx in range(total_frames):
    ret, frame = cap.read()
    if not ret:
        break
    
    # Let's test what happens if we sample at sampling_step=1 vs sampling_step=2 vs sampling_step=3
    # First let's analyze detection on frame
    sec = f_idx / fps
    if f_idx % 5 == 0:
        det = pose_detector.detect(frame, draw_overlay=False)
        ans = analyzer.analyze(det, (height, width), sim_time=sec)
        
        kpts = det.get("keypoints", [])
        kconf = det.get("keypoints_conf", [])
        pconf = det.get("confidence", 0.0)
        detected = det.get("detected", False)
        bbox = det.get("bbox")
        
        # calculate details
        ls = kpts[5] if len(kpts) > 5 else [0, 0]
        rs = kpts[6] if len(kpts) > 6 else [0, 0]
        lh = kpts[11] if len(kpts) > 11 else [0, 0]
        rh = kpts[12] if len(kpts) > 12 else [0, 0]
        
        ls_c = kconf[5] if len(kconf) > 5 else 0.0
        rs_c = kconf[6] if len(kconf) > 6 else 0.0
        lh_c = kconf[11] if len(kconf) > 11 else 0.0
        rh_c = kconf[12] if len(kconf) > 12 else 0.0
        
        if detected:
            print(f"F{f_idx:04d} ({sec:5.2f}s) | Conf={pconf:.2f} | Act={ans['activity']:<14} | FallCnt={ans['fall_counter']} | Angle={ans['torso_angle']:4.1f} | AR={ans['aspect_ratio']:.2f} | ShC=({ls_c:.2f},{rs_c:.2f}) | HipC=({lh_c:.2f},{rh_c:.2f}) | BBox={bbox}")
        else:
            print(f"F{f_idx:04d} ({sec:5.2f}s) | NO PERSON")

cap.release()
