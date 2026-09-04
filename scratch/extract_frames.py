import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import cv2

video_path = "dataset/real_fall_video.mp4"
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

out_dir = Path("scratch/frames")
out_dir.mkdir(parents=True, exist_ok=True)

# Save 1 frame per 2 seconds
for sec in range(0, int(total_frames / fps) + 1, 2):
    f_idx = int(sec * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(str(out_dir / f"frame_{sec:02d}s.jpg"), frame)
        print(f"Saved frame at {sec:02d}s (frame {f_idx})")

cap.release()
