import sys
import io
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import app

client = app.test_client()

video_bytes = Path("dataset/real_fall_video.mp4").read_bytes()
data = {
    'video': (io.BytesIO(video_bytes), 'uploaded_test_fall.mp4'),
    'patient_id': 'P-101'
}

response = client.post('/api/video/analyze', data=data, content_type='multipart/form-data')
print(f"HTTP Status: {response.status_code}")
res_json = response.get_json()

print("Response JSON Keys:", list(res_json.keys()))
print("success:", res_json.get("success"))
print("fall_detected:", res_json.get("fall_detected"))
print("eventType:", res_json.get("eventType"))
print("max_fall_confidence:", res_json.get("max_fall_confidence"))
print("riskLevel:", res_json.get("riskLevel"))
print("source:", res_json.get("source"))
print("evidence_saved:", res_json.get("evidence_saved"))
print("screenshotUrl:", res_json.get("screenshotUrl"))
print("ntfyTopic:", res_json.get("ntfyTopic"))
print("ntfyStatus:", res_json.get("ntfyStatus"))
print("timeline count:", len(res_json.get("timeline", [])))
print("incident created:", res_json.get("incident") is not None)
