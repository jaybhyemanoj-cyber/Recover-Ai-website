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
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"FPS: {fps}, Total frames: {total_frames}, Resolution: {width}x{height}")

# Let's inspect every 25th frame (1 second intervals) or every 5th frame
for f_idx in range(0, total_frames, 10):
    cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
    ret, frame = cap.read()
    if not ret:
        break
    sec = f_idx / fps
    det = pose_detector.detect(frame, draw_overlay=False)
    kpts = det.get("keypoints", [])
    k_conf = det.get("keypoints_conf", [])
    p_conf = det.get("confidence", 0.0)
    bbox = det.get("bbox", [])
    
    if det.get("detected"):
        ls = kpts[5]
        rs = kpts[6]
        lh = kpts[11]
        rh = kpts[12]
        la = kpts[15]
        ra = kpts[16]
        bw = bbox[2] - bbox[0]
        bh = bbox[3] - bbox[1]
        ar = bw / max(1, bh)
        norm_center_x = (bbox[0] + bbox[2]) / (2.0 * width)
        norm_center_y = (bbox[1] + bbox[3]) / (2.0 * height)
        
        # calculate torso angle
        sm = ((ls[0]+rs[0])/2.0, (ls[1]+rs[1])/2.0)
        hm = ((lh[0]+rh[0])/2.0, (lh[1]+rh[1])/2.0)
        dx = abs(sm[0] - hm[0])
        dy = hm[1] - sm[1]
        import math
        angle = 90.0 if dy <= 0 else math.degrees(math.atan2(dx, max(0.001, dy)))
        
        print(f"F{f_idx:04d} ({sec:5.2f}s) | Conf={p_conf:.2f} | BBox={bbox} | Ctr=({norm_center_x:.2f},{norm_center_y:.2f}) | AR={ar:.2f} | Angle={angle:5.1f} | HipY={hm[1]:.1f} | ShY={sm[1]:.1f}")
    else:
        print(f"F{f_idx:04d} ({sec:5.2f}s) | NO PERSON DETECTED")

cap.release()
