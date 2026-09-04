"""
AI Detection, Pose Estimation, Video Analysis, and Notification Package for Post-Operative Monitoring.
"""
from .camera import camera_manager, CameraManager
from .detector import pose_detector, YOLOPoseDetector
from .activity_rules import activity_analyzer, ActivityAnalyzer
from .evidence import handle_confirmed_event, create_evidence_screenshot
from .notifications import send_ntfy_alert, send_fall_alert, send_emergency_alert
from .report_generator import generate_video_analysis_report
from .video_analyzer import analyze_video_file

__all__ = [
    "camera_manager",
    "CameraManager",
    "pose_detector",
    "YOLOPoseDetector",
    "activity_analyzer",
    "ActivityAnalyzer",
    "handle_confirmed_event",
    "create_evidence_screenshot",
    "send_ntfy_alert",
    "send_fall_alert",
    "send_emergency_alert",
    "generate_video_analysis_report",
    "analyze_video_file"
]
