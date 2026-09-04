import os
from pathlib import Path
from dotenv import load_dotenv
import torch

# Load .env file if present
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Ultralytics Config Directory for cloud/Render compatibility
os.environ.setdefault("YOLO_CONFIG_DIR", "/tmp/Ultralytics" if os.name != "nt" else str(BASE_DIR / ".cache" / "Ultralytics"))

# Patient & Camera Configuration
PATIENT_ID = os.getenv("PATIENT_ID", "P-101")
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
CAMERA_WIDTH = int(os.getenv("CAMERA_WIDTH", "640"))
CAMERA_HEIGHT = int(os.getenv("CAMERA_HEIGHT", "480"))

# YOLO Pose Model Configuration & Optimization
YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolov8n-pose.pt")
YOLO_CONFIDENCE_THRESHOLD = float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", "0.45"))
PERSON_CONFIDENCE_THRESHOLD = float(os.getenv("PERSON_CONFIDENCE_THRESHOLD", str(YOLO_CONFIDENCE_THRESHOLD)))
KEYPOINT_CONFIDENCE_THRESHOLD = float(os.getenv("KEYPOINT_CONFIDENCE_THRESHOLD", "0.30"))
FALL_CONFIDENCE_THRESHOLD = float(os.getenv("FALL_CONFIDENCE_THRESHOLD", "0.50"))
YOLO_IMG_SIZE = int(os.getenv("YOLO_IMG_SIZE", "416"))
YOLO_INFERENCE_FPS = float(os.getenv("YOLO_INFERENCE_FPS", "12"))

# Hardware Acceleration: Auto-select CUDA GPU if available, fallback safely to CPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Bed Zone Coordinates (Normalized [x1, y1, x2, y2] within frame from 0.0 to 1.0)
BED_ZONE = [
    float(x) for x in os.getenv("BED_ZONE", "0.05,0.15,0.55,0.85").split(",")
]

# Activity Detection Rules & Separate Event Cooldowns
FALL_CONFIRMATION_FRAMES = int(os.getenv("FALL_CONFIRMATION_FRAMES", "5"))
INACTIVITY_TIMEOUT = float(os.getenv("INACTIVITY_TIMEOUT", "60.0"))  # seconds
ALERT_COOLDOWN = float(os.getenv("ALERT_COOLDOWN", "10.0"))  # seconds
FALL_ALERT_COOLDOWN = float(os.getenv("FALL_ALERT_COOLDOWN", os.getenv("FALL_ALERT_COOLDOWN_SECONDS", "60.0")))  # seconds (60s cooldown for confirmed fall)
FALL_ALERT_COOLDOWN_SECONDS = FALL_ALERT_COOLDOWN
STANDING_SCREENSHOT_COOLDOWN = float(os.getenv("STANDING_SCREENSHOT_COOLDOWN", "30.0"))  # seconds
HAND_MOVEMENT_SCREENSHOT_COOLDOWN = float(os.getenv("HAND_MOVEMENT_SCREENSHOT_COOLDOWN", "10.0"))  # seconds
HAND_GESTURE_ALERT_COOLDOWN = float(os.getenv("HAND_GESTURE_ALERT_COOLDOWN", "10.0"))  # seconds


# Video Upload & Processing Configuration
MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", "100"))
VIDEO_FRAME_INTERVAL = int(os.getenv("VIDEO_FRAME_INTERVAL", "3"))  # Sample every 3rd frame (~10 FPS analysis)

# Caregiver Emergency Phone Number
CAREGIVER_PHONE = os.getenv("CAREGIVER_PHONE", "+917498964628")

# Notification Configuration
DEFAULT_TOPIC = "Healthnest"
NTFY_TOPIC = os.getenv("NTFY_TOPIC", DEFAULT_TOPIC)
NTFY_SERVER_URL = os.getenv("NTFY_SERVER_URL", "https://ntfy.sh").rstrip("/")

# Official WhatsApp Cloud API Configuration
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_RECIPIENT_NUMBER = os.getenv("WHATSAPP_RECIPIENT_NUMBER", os.getenv("CAREGIVER_PHONE", "+917498964628"))
WHATSAPP_TEMPLATE_NAME = os.getenv("WHATSAPP_TEMPLATE_NAME", "")
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v20.0")

# Telegram Bot API Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1267104193").strip()

# Caregiver Escalation Timeout (seconds before unacknowledged alert escalates)
UNACKNOWLEDGED_ALERT_TIMEOUT = float(os.getenv("UNACKNOWLEDGED_ALERT_TIMEOUT", "90.0"))

# AI Physiotherapy & ROM Configuration
PHYSIO_KEYPOINT_CONF_THRESHOLD = float(os.getenv("PHYSIO_KEYPOINT_CONF_THRESHOLD", "0.35"))
PHYSIO_REP_COOLDOWN = float(os.getenv("PHYSIO_REP_COOLDOWN", "0.6"))

# AI Recovery Assistant (Groq LLM) Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Server Configuration
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("PORT", os.getenv("FLASK_PORT", "5000")))
DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")

# Storage Configuration
STATIC_DIR = BASE_DIR / "static"
SCREENSHOT_DIR = STATIC_DIR / "screenshots"
UPLOAD_FOLDER = STATIC_DIR / "uploads"
REPORTS_DIR = STATIC_DIR / "reports"

# Ensure directories exist
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

