import sys
import shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ai.video_analyzer import analyze_video_file

temp_path = "scratch/test_ntfy_real_fall.mp4"
shutil.copy("dataset/real_fall_video.mp4", temp_path)

print("=== STARTING REAL FALL VIDEO ANALYSIS ===", flush=True)
result = analyze_video_file(temp_path, patient_id="P-101")

print("\n=== REAL VIDEO FALL ANALYSIS REPORT ===", flush=True)
print(f"Fall Detected:          {result.get('fall_detected')}", flush=True)
print(f"Confirmed Fall:         {result.get('eventType') == 'CONFIRMED_FALL'}", flush=True)
print(f"Event Type:             {result.get('eventType')}", flush=True)
print(f"Risk Level:             {result.get('riskLevel')}", flush=True)
print(f"Max Fall Confidence:    {result.get('max_fall_confidence')}", flush=True)
print(f"Evidence Saved:         {result.get('evidence_saved')}", flush=True)
print(f"Screenshot Path:        {result.get('screenshotUrl')}", flush=True)
print(f"NTFY Topic:             {result.get('ntfyTopic')}", flush=True)
print(f"NTFY Status:            {result.get('ntfyStatus')}", flush=True)
incident = result.get('incident', {}) or {}
tg_res = (incident.get('dispatch') or {}).get('telegram', {}) or {}
print(f"Telegram Configured:    {tg_res.get('configured', True)}", flush=True)
print(f"Telegram Sent:          {tg_res.get('success', False)}", flush=True)
print(f"Telegram HTTP Status:   {tg_res.get('status_code')}", flush=True)
print(f"Telegram Photo Attached:{tg_res.get('has_screenshot', False)}", flush=True)
print(f"Incident Created:       {result.get('incident') is not None}", flush=True)
print(f"Evidence Screenshots:   {len(result.get('evidence_screenshots', []))}", flush=True)
print(f"Timeline Entries:       {len(result.get('timeline', []))}", flush=True)
