import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import json
import shutil
from ai.video_analyzer import analyze_video_file

# Make a temporary copy so analyze_video_file's unlink doesn't delete our dataset copy
test_path = "dataset/temp_test_video.mp4"
shutil.copy("dataset/real_fall_video.mp4", test_path)

res = analyze_video_file(test_path, patient_id="P-101")
print("=== ANALYZE_VIDEO_FILE RESULT ===")
print("fall_detected:", res.get("fall_detected"))
print("fall_confidence:", res.get("fall_confidence"))
print("max_fall_confidence:", res.get("max_fall_confidence"))
print("ntfy_status:", res.get("ntfy_status"))
print("evidence_screenshots:", res.get("evidence_screenshots"))
print("timeline count:", len(res.get("timeline", [])))
print("TIMELINE:")
for item in res.get("timeline", []):
    print(f"  [{item.get('timestamp')}] {item.get('activity')} (risk={item.get('risk_level')}, conf={item.get('confidence')}) - {item.get('details')}")
