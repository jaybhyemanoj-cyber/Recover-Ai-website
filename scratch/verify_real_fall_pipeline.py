import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import shutil
import json
from ai.video_analyzer import analyze_video_file

temp_path = "scratch/test_pipeline_real_video.mp4"
shutil.copy("dataset/real_fall_video.mp4", temp_path)

res = analyze_video_file(temp_path, patient_id="P-101")

print("=== REAL VIDEO ANALYSIS RESULT ===", flush=True)
print(f"Success: {res.get('success')}", flush=True)
print(f"Fall Detected: {res.get('fall_detected')}", flush=True)
print(f"Event Type: {res.get('eventType')}", flush=True)
print(f"Max Fall Confidence: {res.get('max_fall_confidence')}", flush=True)
print(f"Fall Confidence: {res.get('fall_confidence')}", flush=True)
print(f"Risk Level: {res.get('riskLevel')}", flush=True)
print(f"Source: {res.get('source')}", flush=True)
print(f"Evidence Saved: {res.get('evidence_saved')}", flush=True)
print(f"Screenshot URL: {res.get('screenshotUrl')}", flush=True)
print(f"NTFY Topic: {res.get('ntfyTopic')}", flush=True)
print(f"NTFY Status: {res.get('ntfyStatus')}", flush=True)
print(f"Incident: {res.get('incident') is not None}", flush=True)
print(f"Timeline Count: {len(res.get('timeline', []))}", flush=True)

print("\n=== COMPLETE TIMELINE ===", flush=True)
for itm in res.get("timeline", []):
    print(f"  [{itm.get('timestamp')}] {itm.get('activity'):<16} | risk={itm.get('risk_level'):<10} | conf={itm.get('confidence'):.2f} | details={itm.get('details')}", flush=True)

if res.get('incident'):
    print("\n=== INCIDENT DETAILS ===", flush=True)
    for k, v in res.get('incident').items():
        print(f"  {k}: {v}", flush=True)

