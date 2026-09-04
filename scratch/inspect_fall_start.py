import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import cv2
import numpy as np
import math
from ai.detector import pose_detector

cap = cv2.VideoCapture("dataset/real_fall_video.mp4")
fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"Analyzing {total} frames at {fps} fps ({w}x{h})...", flush=True)

for i in range(0, min(total, 120), 2):
    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ret, frame = cap.read()
    if not ret:
        break
    sec = i / fps
    det = pose_detector.detect(frame, draw_overlay=False)
    kpts = det.get("keypoints", [])
    kconf = det.get("keypoints_conf", [])
    conf = det.get("confidence", 0.0)
    bbox = det.get("bbox", [0, 0, w, h])
    
    if det.get("detected"):
        ls = kpts[5]
        rs = kpts[6]
        lh = kpts[11]
        rh = kpts[12]
        sm = ((ls[0]+rs[0])/2.0, (ls[1]+rs[1])/2.0)
        hm = ((lh[0]+rh[0])/2.0, (lh[1]+rh[1])/2.0)
        dx = abs(sm[0] - hm[0])
        dy = hm[1] - sm[1]
        angle = 90.0 if dy <= 0 else math.degrees(math.atan2(dx, max(0.001, dy)))
        bw = bbox[2] - bbox[0]
        bh = bbox[3] - bbox[1]
        ar = bw / max(1, bh)
        norm_cy = (bbox[1] + bbox[3]) / (2.0 * h)
        
        print(f"F{i:03d} ({sec:4.2f}s) | Conf={conf:.2f} | BBox={bbox} | AR={ar:.2f} | Angle={angle:4.1f} | HipY={hm[1]:.1f} | ShY={sm[1]:.1f} | NormCY={norm_cy:.2f}", flush=True)
    else:
        print(f"F{i:03d} ({sec:4.2f}s) | NO PERSON", flush=True)

cap.release()
