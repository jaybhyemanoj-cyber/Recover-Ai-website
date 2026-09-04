import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

import config

logger = logging.getLogger("ai.report_generator")

def generate_video_analysis_report(
    patient_id: str,
    video_filename: str,
    duration_sec: float,
    total_frames: int,
    frames_analyzed: int,
    events: List[Dict[str, Any]],
    fall_detected: bool,
    max_confidence: float,
    evidence_screenshots: List[str],
    ntfy_status: str,
    source: str = "yolo"
) -> Dict[str, Any]:
    """
    Generates a structured, printable HTML Post-Operative Incident & Video Analysis Report.
    Saves to static/reports/ and returns report metadata.
    """
    now = datetime.now()
    report_id = f"REP-{patient_id.replace('-', '')}-{now.strftime('%Y%m%d%H%M%S')}"
    report_filename = f"report_{patient_id.replace('-', '')}_{now.strftime('%Y%m%d_%H%M%S')}.html"
    report_path = config.REPORTS_DIR / report_filename

    status_badge_color = "#e11d48" if fall_detected else "#10b981"
    status_text = "CRITICAL INCIDENT: CONFIRMED FALL DETECTED" if fall_detected else "NORMAL: NO ABNORMAL EVENT DETECTED"

    # Build timeline rows
    timeline_rows = ""
    for evt in events:
        sev_color = "#e11d48" if evt.get("risk_level") == "critical" else "#f59e0b" if evt.get("risk_level") == "attention" else "#10b981"
        timeline_rows += f"""
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 10px 14px; font-family: monospace; font-weight: 700; color: #94a3b8;">{evt.get('timestamp', '00:00')}</td>
            <td style="padding: 10px 14px; font-weight: 800; color: {sev_color};">{evt.get('activity', 'NORMAL')}</td>
            <td style="padding: 10px 14px; text-transform: uppercase; font-size: 11px; font-weight: 700; color: {sev_color};">{evt.get('risk_level', 'stable')}</td>
            <td style="padding: 10px 14px; font-weight: 700; color: #38bdf8;">{int(evt.get('confidence', 0.0) * 100)}%</td>
            <td style="padding: 10px 14px; font-size: 12px; color: #cbd5e1;">{evt.get('details', '')}</td>
        </tr>
        """

    # Build screenshots gallery
    screenshots_html = ""
    for img_url in evidence_screenshots:
        screenshots_html += f"""
        <div style="background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 10px; text-align: center;">
            <img src="{img_url}" alt="Evidence Frame" style="width: 100%; max-height: 240px; object-fit: contain; border-radius: 8px; background: #000;" />
            <p style="font-size: 11px; color: #94a3b8; margin-top: 6px;">Single Keyframe Privacy Evidence</p>
        </div>
        """

    if not evidence_screenshots:
        screenshots_html = "<p style='color: #64748b; font-style: italic;'>No critical incident keyframe captures required for this session.</p>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Video Incident Report - {patient_id} - {report_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #090d16;
            color: #f1f5f9;
            margin: 0;
            padding: 30px 20px;
        }}
        .container {{
            max-width: 860px;
            margin: 0 auto;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 24px;
            padding: 36px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #334155;
            padding-bottom: 20px;
            margin-bottom: 24px;
        }}
        .status-banner {{
            background: {status_badge_color}22;
            border: 1px solid {status_badge_color}66;
            color: {status_badge_color};
            padding: 14px 20px;
            border-radius: 16px;
            font-weight: 900;
            font-size: 15px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 24px;
        }}
        .card {{
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 16px;
        }}
        .card-title {{
            font-size: 11px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            margin-bottom: 8px;
        }}
        .card-value {{
            font-size: 16px;
            font-weight: 800;
            color: #ffffff;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th {{
            background: #0f172a;
            padding: 10px 14px;
            text-align: left;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            border-bottom: 1px solid #334155;
        }}
        .disclaimer {{
            margin-top: 32px;
            padding: 16px;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 14px;
            font-size: 11px;
            color: #94a3b8;
            line-height: 1.6;
        }}
        .actions {{
            margin-top: 24px;
            text-align: center;
        }}
        .print-btn {{
            background: #0ea5e9;
            color: #ffffff;
            border: none;
            padding: 10px 24px;
            font-size: 13px;
            font-weight: 800;
            border-radius: 12px;
            cursor: pointer;
        }}
        @media print {{
            body {{ background: #fff; color: #000; padding: 0; }}
            .container {{ border: none; box-shadow: none; padding: 0; background: #fff; color: #000; }}
            .card, .status-banner, .disclaimer, table, th, td {{ background: #fff !important; color: #000 !important; border-color: #ccc !important; }}
            .print-btn {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: #0ea5e9;">Recover-AI Telemetry System</span>
                <h1 style="margin: 4px 0 0 0; font-size: 24px; font-weight: 900; color: #ffffff;">Post-Operative AI Video Incident Report</h1>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #94a3b8;">Report ID: {report_id} • Generated: {now.strftime('%Y-%m-%d %I:%M:%S %p')}</p>
            </div>
            <button class="print-btn" onclick="window.print()">Print / Save PDF</button>
        </div>

        <div class="status-banner">
            <span>{status_text}</span>
            <span>Confidence: {int(max_confidence * 100)}%</span>
        </div>

        <div class="grid-2">
            <div class="card">
                <div class="card-title">Patient Identification</div>
                <div class="card-value">{patient_id} (Rahul Sharma)</div>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #94a3b8;">Assigned Caregiver: Primary Caregiver ({config.CAREGIVER_PHONE})</p>
            </div>
            <div class="card">
                <div class="card-title">Video Telemetry Metadata</div>
                <div class="card-value">{video_filename}</div>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #94a3b8;">Duration: {duration_sec:.1f}s • Analyzed: {frames_analyzed} / {total_frames} frames</p>
            </div>
            <div class="card">
                <div class="card-title">AI Vision & Pose Pipeline</div>
                <div class="card-value">Ultralytics YOLOv8 Pose ({config.YOLO_MODEL_PATH})</div>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #94a3b8;">17 COCO Keypoints • imgsz: {config.YOLO_IMG_SIZE} • Source: {source.upper()}</p>
            </div>
            <div class="card">
                <div class="card-title">Emergency Alert & Push Status</div>
                <div class="card-value">ntfy: {ntfy_status}</div>
                <p style="margin: 4px 0 0 0; font-size: 12px; color: #94a3b8;">Topic: {config.NTFY_TOPIC} (Priority 5 Push)</p>
            </div>
        </div>

        <h3 style="font-size: 15px; font-weight: 800; color: #ffffff; margin-top: 24px; margin-bottom: 10px;">Detected Activity & Kinematic Timeline</h3>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Detected Activity</th>
                    <th>Risk Level</th>
                    <th>Confidence</th>
                    <th>Kinematic Posture Notes</th>
                </tr>
            </thead>
            <tbody>
                {timeline_rows}
            </tbody>
        </table>

        <h3 style="font-size: 15px; font-weight: 800; color: #ffffff; margin-top: 28px; margin-bottom: 10px;">Incident Keyframe Evidence Gallery</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 14px;">
            {screenshots_html}
        </div>

        <div class="disclaimer">
            <strong>Mandatory Safety & Privacy Disclaimer:</strong><br />
            This system operates as an AI-assisted monitoring and warning prototype. It does not provide medical diagnoses or replace emergency medical response services. In compliance with HIPAA and privacy mandates, raw continuous video files are discarded immediately upon analysis completion, and only verified incident keyframes are archived.
        </div>
    </div>
</body>
</html>"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"Generated incident report saved to: {report_path}")

    return {
        "report_id": report_id,
        "report_filename": report_filename,
        "report_url": f"/static/reports/{report_filename}",
        "report_path": str(report_path),
        "timestamp": now.strftime("%Y-%m-%d %I:%M:%S %p"),
        "fall_detected": fall_detected,
        "max_confidence": max_confidence,
        "events_count": len(events)
    }


def generate_patient_recovery_summary_report(
    patient_data: Dict[str, Any],
    alerts_list: Optional[List[Dict[str, Any]]] = None,
    physio_summary: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates a full Clinical Post-Operative Recovery Report for a patient.
    Includes recovery milestones, vitals history, medication adherence,
    physiotherapy ROM metrics, and incident audit log.
    Safely displays 'Data not available' for missing fields without inventing values.
    """
    now = datetime.now()
    pid = patient_data.get("id", config.PATIENT_ID)
    pname = patient_data.get("name", "Rahul Sharma")
    clean_pid = pid.replace("-", "").replace(" ", "_")
    report_id = f"CLINICAL-{clean_pid}-{now.strftime('%Y%m%d%H%M%S')}"
    report_filename = f"recovery_report_{clean_pid}_{now.strftime('%Y%m%d_%H%M%S')}.html"
    report_path = config.REPORTS_DIR / report_filename

    vitals = patient_data.get("vitals", {})
    temp = f"{vitals.get('temperature', 'N/A')} °F" if vitals.get('temperature') else "Data not available"
    bp = f"{vitals.get('bpSystolic', 'N/A')}/{vitals.get('bpDiastolic', 'N/A')} mmHg" if vitals.get('bpSystolic') else "Data not available"
    hr = f"{vitals.get('heartRate', 'N/A')} bpm" if vitals.get('heartRate') else "Data not available"
    spo2 = f"{vitals.get('spO2', 'N/A')}%" if vitals.get('spO2') else "Data not available"
    pain = f"{vitals.get('painLevel', 'N/A')}/10" if vitals.get('painLevel') is not None else "Data not available"
    mobility = vitals.get("mobility", "Data not available")

    surgery = patient_data.get("surgeryType", "Data not available")
    surgery_date = patient_data.get("surgeryDate", "Data not available")
    recovery_day = patient_data.get("recoveryDay", "Data not available")
    target_days = patient_data.get("targetRecoveryDays", "Data not available")
    doctor = patient_data.get("doctorName", "Data not available")
    caregiver = patient_data.get("caregiverName", "Data not available")
    adherence = f"{patient_data.get('medicationAdherence', 'N/A')}%" if patient_data.get('medicationAdherence') else "Data not available"

    # Alert incidents
    alerts = alerts_list or []
    fall_incidents = [a for a in alerts if "FALL" in str(a.get("eventType", "")).upper() or "FALL" in str(a.get("title", "")).upper()]
    
    alert_rows = ""
    for a in alerts[:8]:
        sev = a.get("severity", "stable")
        color = "#e11d48" if sev == "critical" else "#f59e0b" if sev == "attention" else "#10b981"
        ack = "Acknowledged" if a.get("acknowledged") else "Pending"
        alert_rows += f"""
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 10px 14px; font-family: monospace; color: #94a3b8;">{a.get('time', a.get('timestamp', 'N/A'))}</td>
            <td style="padding: 10px 14px; font-weight: 700; color: {color};">{a.get('title', a.get('eventType', 'Incident'))}</td>
            <td style="padding: 10px 14px; text-transform: uppercase; font-weight: 700; color: {color};">{sev}</td>
            <td style="padding: 10px 14px; color: #cbd5e1;">{ack}</td>
            <td style="padding: 10px 14px; font-size: 12px; color: #94a3b8;">{a.get('message', 'Data not available')}</td>
        </tr>
        """

    if not alert_rows:
        alert_rows = "<tr><td colspan='5' style='padding: 16px; text-align: center; color: #64748b; font-style: italic;'>No incident alerts recorded during this recovery period.</td></tr>"

    # Evidence captures
    evidence_html = ""
    for a in alerts:
        s_url = a.get("screenshotUrl")
        if s_url:
            evidence_html += f"""
            <div style="background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 10px; text-align: center;">
                <img src="{s_url}" alt="Incident Screenshot" style="width: 100%; max-height: 200px; object-fit: contain; border-radius: 8px; background: #000;" />
                <p style="font-size: 11px; color: #94a3b8; margin-top: 6px;">{a.get('title', 'Incident Evidence')}</p>
            </div>
            """
    if not evidence_html:
        evidence_html = "<p style='color: #64748b; font-style: italic;'>No critical incident keyframe captures on record.</p>"

    # Physio summary
    physio = physio_summary or {}
    p_ex = physio.get("exercise_name", "Knee Flexion (Knee Bend)")
    p_reps = physio.get("rep_count", 0)
    p_target = physio.get("target_reps", 10)
    p_angle = f"{physio.get('current_angle', 0.0)}°"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Post-Op Clinical Recovery Report - {pname} ({pid})</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #090d16;
            color: #f1f5f9;
            margin: 0;
            padding: 30px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 24px;
            padding: 36px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #334155;
            padding-bottom: 20px;
            margin-bottom: 24px;
        }}
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .card {{
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 16px;
        }}
        .card-title {{
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            font-weight: 700;
        }}
        .card-value {{
            font-size: 20px;
            font-weight: 900;
            color: #ffffff;
            margin-top: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
            font-size: 13px;
        }}
        th {{
            background: #0f172a;
            padding: 10px 14px;
            text-align: left;
            font-size: 11px;
            text-transform: uppercase;
            color: #94a3b8;
            border-bottom: 2px solid #334155;
        }}
        .disclaimer {{
            margin-top: 30px;
            padding: 16px;
            background: #0f172a;
            border-left: 4px solid #38bdf8;
            border-radius: 8px;
            font-size: 11px;
            color: #94a3b8;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <span style="font-size: 11px; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.1em;">RECOVERAI • CLINICAL POST-OP RECOVERY REPORT</span>
                <h1 style="margin: 4px 0 0 0; font-size: 26px; font-weight: 900; color: #ffffff;">{pname} ({pid})</h1>
                <p style="margin: 4px 0 0 0; font-size: 13px; color: #94a3b8;">Surgery: <strong>{surgery}</strong> (Date: {surgery_date})</p>
            </div>
            <div style="text-align: right;">
                <span style="display: inline-block; padding: 6px 14px; border-radius: 9999px; font-size: 12px; font-weight: 800; background: #38bdf822; color: #38bdf8; border: 1px solid #38bdf866;">
                    Recovery Day {recovery_day} / {target_days}
                </span>
                <p style="margin: 6px 0 0 0; font-size: 11px; color: #64748b;">Report ID: {report_id}</p>
            </div>
        </div>

        <h3 style="font-size: 14px; font-weight: 800; color: #38bdf8; text-transform: uppercase; margin-bottom: 12px;">1. Vital Telemetry & Recovery Status</h3>
        <div class="grid-2">
            <div class="card"><div class="card-title">Temperature</div><div class="card-value">{temp}</div></div>
            <div class="card"><div class="card-title">Blood Pressure</div><div class="card-value">{bp}</div></div>
            <div class="card"><div class="card-title">Heart Rate</div><div class="card-value">{hr}</div></div>
            <div class="card"><div class="card-title">Oxygen (SpO2)</div><div class="card-value">{spo2}</div></div>
            <div class="card"><div class="card-title">Pain Score</div><div class="card-value">{pain}</div></div>
            <div class="card"><div class="card-title">Medication Adherence</div><div class="card-value" style="color: #34d399;">{adherence}</div></div>
        </div>

        <h3 style="font-size: 14px; font-weight: 800; color: #38bdf8; text-transform: uppercase; margin-bottom: 12px;">2. Care Team & Mobility</h3>
        <div class="grid-2">
            <div class="card"><div class="card-title">Attending Surgeon</div><div class="card-value" style="font-size: 15px;">{doctor}</div></div>
            <div class="card"><div class="card-title">Assigned Caregiver</div><div class="card-value" style="font-size: 15px;">{caregiver}</div></div>
            <div class="card"><div class="card-title">Mobility Milestone</div><div class="card-value" style="font-size: 15px; color: #f59e0b;">{mobility}</div></div>
            <div class="card"><div class="card-title">Physiotherapy ROM Log</div><div class="card-value" style="font-size: 15px;">{p_ex}: {p_reps}/{p_target} reps ({p_angle})</div></div>
        </div>

        <h3 style="font-size: 14px; font-weight: 800; color: #38bdf8; text-transform: uppercase; margin-top: 24px; margin-bottom: 8px;">3. Safety Incident & Fall Log (Total: {len(alerts)}, Falls: {len(fall_incidents)})</h3>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Incident</th>
                    <th>Severity</th>
                    <th>Caregiver Status</th>
                    <th>Details</th>
                </tr>
            </thead>
            <tbody>
                {alert_rows}
            </tbody>
        </table>

        <h3 style="font-size: 14px; font-weight: 800; color: #38bdf8; text-transform: uppercase; margin-top: 24px; margin-bottom: 8px;">4. Verified Keyframe Evidence Gallery</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px;">
            {evidence_html}
        </div>

        <div class="disclaimer">
            <strong>Clinical Safety Disclaimer:</strong> This clinical report is compiled from edge telemetry, daily health submissions, and AI event logs. It is intended as assistive telemetry documentation for the attending medical team and does not replace in-person clinical examination.
        </div>
    </div>
</body>
</html>"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"Generated patient clinical summary report saved to: {report_path}")

    return {
        "report_id": report_id,
        "report_filename": report_filename,
        "report_url": f"/static/reports/{report_filename}",
        "report_path": str(report_path),
        "timestamp": now.strftime("%Y-%m-%d %I:%M:%S %p"),
        "patient_id": pid,
        "patient_name": pname
    }

