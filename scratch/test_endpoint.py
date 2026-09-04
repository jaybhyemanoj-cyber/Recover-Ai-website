import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import io
import json
from app import app

client = app.test_client()

video_path = "dataset/real_fall_video.mp4"
with open(video_path, "rb") as f:
    video_bytes = f.read()

data = {
    "video": (io.BytesIO(video_bytes), "test_patient_fall.mp4"),
    "patient_id": "P-101"
}

print("Posting to /api/video/analyze...", flush=True)
res = client.post("/api/video/analyze", data=data, content_type="multipart/form-data")

print(f"Status code: {res.status_code}", flush=True)
json_data = res.get_json()
print("Keys in response:", list(json_data.keys()), flush=True)
print("fall_detected:", json_data.get("fall_detected"), flush=True)
print("fall_confidence:", json_data.get("fall_confidence"), flush=True)
print("max_fall_confidence:", json_data.get("max_fall_confidence"), flush=True)
print("ntfy_status:", json_data.get("ntfy_status"), flush=True)
print("evidence_screenshots:", json_data.get("evidence_screenshots"), flush=True)
print("alert:", json_data.get("alert"), flush=True)
print("timeline:", flush=True)
for item in json_data.get("timeline", []):
    print(f"  {item.get('timestamp')} | {item.get('activity'):<15} | risk={item.get('risk_level'):<10} | conf={item.get('confidence'):.2f} | details={item.get('details')}", flush=True)
