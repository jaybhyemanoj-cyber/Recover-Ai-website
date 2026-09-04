import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import shutil
import glob
from ai.video_analyzer import analyze_video_file

files = glob.glob("static/uploads/*.mp4") + glob.glob("dataset/*.mp4")
print(f"Found video files: {files}")

for f in set(files):
    temp = f"scratch/test_{Path(f).name}"
    shutil.copy(f, temp)
    res = analyze_video_file(temp, patient_id="P-101")
    print(f"\n==========================================")
    print(f"FILE: {f}")
    print(f"Duration: {res.get('duration_sec')}s | Frames: {res.get('frames_analyzed')}/{res.get('total_frames')}")
    print(f"Fall Detected: {res.get('fall_detected')} | Fall Conf: {res.get('fall_confidence')} | Max Fall Conf: {res.get('max_fall_confidence')}")
    print(f"NTFY Status: {res.get('ntfy_status')}")
    print(f"Alert: {res.get('alert') is not None}")
    print(f"Screenshots: {res.get('evidence_screenshots')}")
    print(f"Timeline entries: {len(res.get('timeline', []))}")
    for itm in res.get("timeline", []):
        print(f"   [{itm.get('timestamp')}] {itm.get('activity')} (conf={itm.get('confidence'):.2f}, risk={itm.get('risk_level')})")
