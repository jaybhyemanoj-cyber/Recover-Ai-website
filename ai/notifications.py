"""
Notification Service Module: NTFY Push & Official WhatsApp Cloud API
---------------------------------------------------------------------
Provides a clean, modular notification architecture:
NotificationService
 ├── NTFYNotifier
 └── WhatsAppNotifier

Zero secrets are hard-coded; all credentials are read from environment variables.
Fails gracefully with informative logging if WhatsApp or NTFY is unconfigured/offline.
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import base64
from email.header import Header
import requests

import config

logger = logging.getLogger("ai.notifications")


def get_priority_for_risk(risk_level: str, event_type: str = "") -> str:
    """Map risk level and event type to ntfy priority level (1 to 5)."""
    evt = str(event_type).upper()
    norm_risk = str(risk_level).lower().strip()

    if "FALL" in evt or norm_risk in ("critical", "emergency", "high"):
        return "5"  # Urgent / Max priority
    elif "HAND" in evt or norm_risk in ("warning", "attention", "medium"):
        return "4"  # High priority
    elif norm_risk in ("info", "low", "stable"):
        return "3"  # Default / Normal
    return "4"


def get_tags_for_event(event_type: str, risk_level: str = "") -> str:
    """Return appropriate emoji tags for ntfy based on event type."""
    evt = str(event_type).upper()
    if "FALL" in evt:
        return "rotating_light,warning"
    elif "HAND" in evt:
        return "raised_hand,wave"
    elif "INACTIVITY" in evt:
        return "bed,warning"
    return "rotating_light,bell"


def format_alert_message(
    event_type: str,
    patient_id: str,
    risk_level: str,
    source: str = "yolo",
    custom_message: Optional[str] = None,
    timestamp_str: Optional[str] = None,
    confidence: float = 0.95,
    has_evidence: bool = True
) -> str:
    """Create structured alert message exactly per project specifications."""
    time_display = timestamp_str or datetime.now().strftime("%I:%M %p")
    source_upper = str(source).upper()
    if source_upper in ("YOLO", "LIVE", "CAMERA", "WEBCAM", "LIVE CAMERA"):
        source_display = "LIVE CAMERA"
    elif source_upper in ("VIDEO_ANALYSIS", "VIDEO_UPLOAD", "VIDEO", "UPLOADED VIDEO"):
        source_display = "UPLOADED VIDEO"
    elif source_upper in ("SIMULATION", "TEST", "SIMULATION TEST"):
        source_display = "SIMULATION TEST"
    else:
        source_display = source_upper

    if isinstance(confidence, (int, float)):
        conf_percent = int(confidence * 100) if confidence <= 1.0 else int(confidence)
    else:
        conf_percent = 95

    if custom_message:
        return custom_message

    evidence_line = "📸 Incident evidence attached." if has_evidence else "📸 Incident evidence saved locally."

    return (
        f"🚨 RECOVERAI — EMERGENCY FALL ALERT\n\n"
        f"🚨 CONFIRMED FALL DETECTED\n\n"
        f"Patient: {patient_id}\n"
        f"Risk: CRITICAL\n"
        f"Source: {source_display}\n"
        f"Time: {time_display}\n"
        f"Confidence: {conf_percent}%\n\n"
        f"{evidence_line}\n\n"
        f"⚠️ Please check the patient immediately."
    )


class BaseNotifier:
    """Abstract Base Class for Alert Notifiers."""
    def send(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError


class NTFYNotifier(BaseNotifier):
    """
    NTFY Push Notification Engine.
    Sends push alert + binary evidence screenshot attachment to caregiver smartphone.
    """
    def __init__(self, topic: str = config.NTFY_TOPIC, server_url: str = config.NTFY_SERVER_URL):
        self.topic = topic
        self.server_url = server_url.rstrip("/")

    def send(
        self,
        event_type: str,
        patient_id: str,
        risk_level: str = "critical",
        screenshot_path: Optional[str] = None,
        message: Optional[str] = None,
        topic: Optional[str] = None,
        source: str = "yolo",
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        target_topic = topic or self.topic
        url = f"{self.server_url}/{target_topic}"
        priority = "5"
        tags = "rotating_light,warning"
        time_str = datetime.now().strftime("%I:%M %p")
        title = "🚨 RECOVERAI — EMERGENCY FALL ALERT"

        conf_val = (extra_data or {}).get("confidence", 0.95) if isinstance(extra_data, dict) else 0.95
        has_file = bool(screenshot_path and os.path.isfile(screenshot_path))
        body_text = message or format_alert_message(event_type, patient_id, risk_level, source, None, time_str, conf_val, has_evidence=has_file)
        # Encode title and multi-line body with RFC 2047 MIME Base64 for HTTP header safety
        b64_title = base64.b64encode(title.encode("utf-8")).decode("utf-8")
        b64_msg = base64.b64encode(body_text.encode("utf-8")).decode("utf-8")

        result = {
            "channel": "ntfy",
            "success": False,
            "status_code": None,
            "topic": target_topic,
            "url": url,
            "title": title,
            "message": body_text,
            "priority": priority,
            "has_screenshot": False,
            "screenshot_path": screenshot_path,
            "timestamp": datetime.now().isoformat(),
            "error": None
        }

        # 1. Attachment POST if screenshot exists (Binary JPEG in request body)
        if has_file:
            try:
                filename = os.path.basename(screenshot_path)
                attachment_headers = {
                    "X-Title": f"=?utf-8?b?{b64_title}?=",
                    "X-Message": f"=?utf-8?b?{b64_msg}?=",
                    "X-Priority": str(priority),
                    "X-Tags": tags,
                    "X-Filename": filename,
                    "Content-Type": "image/jpeg"
                }

                with open(screenshot_path, "rb") as img_file:
                    img_data = img_file.read()

                response = requests.post(
                    url,
                    data=img_data,
                    headers=attachment_headers,
                    timeout=10
                )
                result["status_code"] = response.status_code

                if response.status_code == 200:
                    print("[ALERT] NTFY_SENT")
                    logger.info("[ALERT] NTFY_SENT: Emergency notification delivered with screenshot evidence.")
                    result["success"] = True
                    result["has_screenshot"] = True
                    return result
                elif response.status_code == 429:
                    err_msg = "HTTP 429: NTFY daily quota reached — notification not delivered"
                    result["error"] = err_msg
                    result["has_screenshot"] = False
                    print(f"[WARN] NTFY_429: NTFY quota reached (HTTP 429). Evidence preserved locally: {screenshot_path}")
                    logger.warning(f"[WARN] NTFY_429: NTFY quota reached (HTTP 429). Evidence preserved locally at {screenshot_path}. Retries skipped.")
                    return result
                else:
                    err_msg = f"HTTP {response.status_code}: {response.text}"
                    result["error"] = err_msg
                    print(f"[ERROR] NTFY_FAILED: HTTP {response.status_code}")
                    logger.warning(f"[ERROR] NTFY_FAILED: Attachment POST returned {response.status_code}.")
                    return result

            except Exception as upload_err:
                err_msg = f"Attachment upload failed: {str(upload_err)}"
                result["error"] = err_msg
                print(f"[ERROR] NTFY_FAILED: {upload_err}")
                logger.warning(f"NTFY image attachment error ({upload_err}).")
                return result

        # 2. Text-only request (if no screenshot file present)
        try:
            text_headers = {
                "X-Title": f"=?utf-8?b?{b64_title}?=",
                "X-Priority": str(priority),
                "X-Tags": tags
            }
            response = requests.post(
                url,
                data=body_text.encode("utf-8"),
                headers=text_headers,
                timeout=8
            )
            result["status_code"] = response.status_code
            if response.status_code == 200:
                print("[ALERT] NTFY_SENT")
                logger.info("[ALERT] NTFY_SENT: Emergency text notification delivered.")
                result["success"] = True
                result["error"] = None
                result["has_screenshot"] = False
            elif response.status_code == 429:
                err_msg = "HTTP 429: NTFY daily quota reached — notification not delivered"
                result["error"] = err_msg
                result["has_screenshot"] = False
                print("[WARN] NTFY_429: NTFY quota reached (HTTP 429).")
                logger.warning("[WARN] NTFY_429: NTFY quota reached (HTTP 429) on text request. Automatic retry skipped.")
            else:
                err_msg = f"HTTP {response.status_code}: {response.text}"
                result["error"] = err_msg
                result["has_screenshot"] = False
                print(f"[ERROR] NTFY_FAILED: HTTP {response.status_code}")

        except Exception as req_err:
            result["error"] = f"Network error: {str(req_err)}"
            print(f"[ERROR] NTFY_FAILED: {req_err}")

        return result


class WhatsAppNotifier(BaseNotifier):
    """
    Official Meta WhatsApp Cloud API Notifier.
    Sends emergency incident notifications over WhatsApp Business Platform.
    
    Required Environment Variables:
    - WHATSAPP_ACCESS_TOKEN
    - WHATSAPP_PHONE_NUMBER_ID
    - WHATSAPP_RECIPIENT_NUMBER (or CAREGIVER_PHONE)
    """
    def __init__(
        self,
        access_token: str = config.WHATSAPP_ACCESS_TOKEN,
        phone_number_id: str = config.WHATSAPP_PHONE_NUMBER_ID,
        recipient_number: str = config.WHATSAPP_RECIPIENT_NUMBER,
        api_version: str = config.WHATSAPP_API_VERSION
    ):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.recipient_number = recipient_number
        self.api_version = api_version

    def is_configured(self) -> bool:
        """Check whether valid Meta WhatsApp Cloud API credentials are provided."""
        return bool(self.access_token and self.phone_number_id and self.recipient_number)

    def send(
        self,
        event_type: str,
        patient_id: str,
        risk_level: str = "critical",
        source: str = "yolo",
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send WhatsApp emergency alert via official Graph API.
        """
        result = {
            "channel": "whatsapp",
            "success": False,
            "status_code": None,
            "configured": self.is_configured(),
            "recipient": self.recipient_number,
            "error": None
        }

        if not self.is_configured():
            logger.info(
                "[WhatsApp] Meta WhatsApp Cloud API credentials not configured in environment. "
                "Set WHATSAPP_ACCESS_TOKEN & WHATSAPP_PHONE_NUMBER_ID in .env to enable live WhatsApp alerts. (Safe Fallback active)"
            )
            result["error"] = "WhatsApp credentials not configured (WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID missing)"
            return result

        clean_recipient = "".join(c for c in self.recipient_number if c.isdigit() or c == "+").lstrip("+")
        url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        time_str = datetime.now().strftime("%I:%M %p")
        message_body = (
            f"🚨 *RECOVERAI — EMERGENCY FALL ALERT*\n\n"
            f"• *Patient ID*: {patient_id}\n"
            f"• *Event*: {event_type}\n"
            f"• *Risk Level*: {risk_level.upper()}\n"
            f"• *Time*: {time_str}\n"
            f"• *Source*: {source.upper()}\n\n"
            f"⚠️ *Emergency Instruction*: Please check the patient immediately or access the Caregiver Command Desk."
        )

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_recipient,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message_body
            }
        }

        try:
            logger.info(f"[WhatsApp] Dispatching alert to recipient {clean_recipient} via Meta Cloud API...")
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            result["status_code"] = response.status_code

            if response.status_code in (200, 201):
                logger.info("[WhatsApp] Emergency alert delivered successfully.")
                result["success"] = True
                result["response_data"] = response.json()
            else:
                err_text = response.text
                logger.warning(f"[WhatsApp ERROR] HTTP {response.status_code}: {err_text}")
                result["error"] = f"Meta API HTTP {response.status_code}: {err_text}"

        except Exception as e:
            logger.error(f"[WhatsApp ERROR] Request failed: {e}")
            result["error"] = str(e)

        return result


class TelegramNotifier(BaseNotifier):
    """
    Official Telegram Bot API Notifier.
    Sends emergency incident notifications + evidence photo attachments to caregiver Telegram chat.
    
    Required Environment Variables:
    - TELEGRAM_BOT_TOKEN
    - TELEGRAM_CHAT_ID
    """
    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None
    ):
        self._bot_token = bot_token
        self._chat_id = chat_id

    @property
    def bot_token(self) -> str:
        return (self._bot_token or getattr(config, "TELEGRAM_BOT_TOKEN", "")).strip()

    @property
    def chat_id(self) -> str:
        return (self._chat_id or getattr(config, "TELEGRAM_CHAT_ID", "1267104193")).strip()

    def is_configured(self) -> bool:
        """Check whether valid Telegram Bot token and chat_id are configured."""
        return bool(self.bot_token and self.chat_id)

    def send(
        self,
        event_type: str,
        patient_id: str,
        risk_level: str = "critical",
        screenshot_path: Optional[str] = None,
        source: str = "yolo",
        custom_message: Optional[str] = None,
        confidence: float = 0.95
    ) -> Dict[str, Any]:
        """
        Send Telegram emergency alert with photo evidence via Bot API sendPhoto.
        """
        token = self.bot_token
        chat_id = self.chat_id

        result = {
            "channel": "telegram",
            "success": False,
            "status_code": None,
            "configured": bool(token and chat_id),
            "chat_id": chat_id,
            "has_screenshot": False,
            "error": None
        }

        if not token or not chat_id:
            logger.info("[Telegram] Bot credentials not configured in environment.")
            result["error"] = "Telegram credentials not configured (TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing in .env)"
            return result

        time_str = datetime.now().strftime("%I:%M %p")
        source_upper = str(source).upper()
        if source_upper in ("YOLO", "LIVE", "CAMERA", "WEBCAM", "LIVE CAMERA"):
            source_display = "LIVE CAMERA"
        elif source_upper in ("VIDEO_ANALYSIS", "VIDEO_UPLOAD", "VIDEO", "UPLOADED VIDEO"):
            source_display = "VIDEO ANALYSIS"
        elif source_upper in ("SIMULATION", "TEST", "SIMULATION TEST"):
            source_display = "SIMULATION TEST"
        else:
            source_display = source_upper

        if isinstance(confidence, (int, float)):
            conf_percent = int(confidence * 100) if confidence <= 1.0 else int(confidence)
        else:
            conf_percent = 95

        caption = custom_message or (
            f"🚨 RECOVERAI — EMERGENCY FALL ALERT\n\n"
            f"🚨 CONFIRMED FALL DETECTED\n\n"
            f"Patient: {patient_id}\n"
            f"Risk: CRITICAL\n"
            f"Source: {source_display}\n"
            f"Time: {time_str}\n"
            f"Confidence: {conf_percent}%\n\n"
            f"📸 Fall evidence screenshot attached.\n"
            f"⚠️ Please check the patient immediately."
        )

        has_file = bool(screenshot_path and os.path.isfile(screenshot_path))

        if has_file:
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            try:
                with open(screenshot_path, "rb") as photo_file:
                    files = {"photo": (os.path.basename(screenshot_path), photo_file, "image/jpeg")}
                    data = {"chat_id": chat_id, "caption": caption}
                    response = requests.post(url, data=data, files=files, timeout=12)

                result["status_code"] = response.status_code
                if response.status_code == 200 and response.json().get("ok"):
                    print("[ALERT] TELEGRAM_SENT")
                    logger.info("[ALERT] TELEGRAM_SENT: Emergency photo alert delivered successfully.")
                    result["success"] = True
                    result["has_screenshot"] = True
                    result["response_data"] = response.json()
                    return result
                else:
                    err_msg = f"Telegram sendPhoto HTTP {response.status_code}: {response.text}"
                    logger.warning(f"[Telegram ERROR] {err_msg}")
                    result["error"] = err_msg
            except Exception as e:
                logger.error(f"[Telegram ERROR] sendPhoto failed: {e}")
                result["error"] = str(e)

        # Fallback to text message if photo send failed or no photo file present
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            payload = {"chat_id": chat_id, "text": caption}
            response = requests.post(url, json=payload, timeout=10)
            result["status_code"] = response.status_code
            if response.status_code == 200 and response.json().get("ok"):
                print("[ALERT] TELEGRAM_SENT")
                logger.info("[ALERT] TELEGRAM_SENT: Emergency text alert delivered successfully.")
                result["success"] = True
                result["has_screenshot"] = False
                result["response_data"] = response.json()
            else:
                err_msg = f"Telegram sendMessage HTTP {response.status_code}: {response.text}"
                logger.warning(f"[Telegram ERROR] {err_msg}")
                result["error"] = err_msg
        except Exception as e:
            logger.error(f"[Telegram ERROR] sendMessage failed: {e}")
            result["error"] = str(e)

        return result


class NotificationService:
    """
    Unified Notification Orchestrator managing NTFY, Telegram & WhatsApp Cloud API.
    """
    def __init__(self):
        self.ntfy = NTFYNotifier()
        self.telegram = TelegramNotifier()
        self.whatsapp = WhatsAppNotifier()

    def dispatch(
        self,
        event_type: str,
        patient_id: str,
        risk_level: str = "critical",
        screenshot_path: Optional[str] = None,
        message: Optional[str] = None,
        topic: Optional[str] = None,
        source: str = "yolo",
        confidence: float = 0.95
    ) -> Dict[str, Any]:
        """
        Dispatch confirmed event to NTFY, Telegram and WhatsApp only if confirmed emergency.
        """
        evt_upper = str(event_type).upper().strip()
        norm_risk = str(risk_level).upper().strip()

        is_emergency = (evt_upper == "CONFIRMED_FALL" or "ESCALAT" in evt_upper) and (norm_risk in ("CRITICAL", "EMERGENCY"))

        if not is_emergency:
            print("[INFO] No emergency — NTFY skipped")
            return {
                "success": False,
                "ntfy": {"channel": "ntfy", "success": False, "skipped": True, "reason": "No emergency — NTFY skipped"},
                "telegram": {"channel": "telegram", "success": False, "skipped": True},
                "whatsapp": {"channel": "whatsapp", "success": False, "skipped": True}
            }

        # 1. Strict Fall Alert via send_fall_alert (NTFY Healthnest)
        event_dict = {
            "type": evt_upper,
            "event_type": event_type,
            "patient_id": patient_id,
            "risk_level": norm_risk,
            "confidence": confidence,
            "screenshot_path": screenshot_path,
            "message": message,
            "topic": topic,
            "source": source
        }
        ntfy_res = send_fall_alert(event_dict)

        # 2. Telegram Alert (Photo Attachment + Fall Caption)
        tg_res = {"success": False, "configured": False, "skipped": True}
        if is_emergency:
            tg_res = self.telegram.send(
                event_type=event_type,
                patient_id=patient_id,
                risk_level=risk_level,
                screenshot_path=screenshot_path,
                source=source,
                custom_message=message,
                confidence=confidence
            )

        # 3. WhatsApp Dispatch (Secondary Official Channel for Confirmed Fall Events)
        wa_res = {"success": False, "configured": False, "skipped": True}
        if is_emergency:
            wa_res = self.whatsapp.send(
                event_type=event_type,
                patient_id=patient_id,
                risk_level=risk_level,
                source=source,
                custom_message=message
            )

        return {
            "success": ntfy_res.get("success", False) or tg_res.get("success", False) or wa_res.get("success", False),
            "ntfy": ntfy_res,
            "telegram": tg_res,
            "whatsapp": wa_res
        }


# Global Singletons
notification_service = NotificationService()


def send_tinkerstream_alert(key: int = 1) -> Dict[str, Any]:
    """
    Dispatches IoT Alert signal to Tinkerstream server:
    https://www.tinkerstream.com/sbj/alert.php?key=1 (Fall Detected -> Buzzer/Alert ON)
    https://www.tinkerstream.com/sbj/alert.php?key=0 (Normal / Cleared -> Buzzer/Alert OFF)
    """
    url = "https://www.tinkerstream.com/sbj/alert.php"
    try:
        res = requests.get(url, params={"key": key}, timeout=5)
        print(f"[ALERT] TINKERSTREAM_SENT (key={key})")
        logger.info(f"[Tinkerstream IoT] Alert API called with key={key} -> HTTP {res.status_code}: {res.text.strip()}")
        return {
            "success": res.status_code == 200,
            "key": key,
            "status_code": res.status_code,
            "response": res.text.strip()
        }
    except Exception as e:
        logger.warning(f"[Tinkerstream IoT ERROR] Failed to call alert API with key={key}: {e}")
        return {
            "success": False,
            "key": key,
            "error": str(e)
        }


def send_fall_alert(event: Any) -> Dict[str, Any]:
    """
    Strict Fall-Only NTFY Alert Dispatcher.
    Immediately returns without sending anything if:
      event.type != "CONFIRMED_FALL"
      or event.risk_level != "CRITICAL"
    """
    if isinstance(event, dict):
        event_type = str(event.get("type") or event.get("event_type") or "").upper().strip()
        risk_level = str(event.get("risk_level") or event.get("riskLevel") or "").upper().strip()
        patient_id = event.get("patient_id") or event.get("patientId") or config.PATIENT_ID
        source = event.get("source", "LIVE CAMERA")
        time_str = event.get("time") or event.get("timestamp") or datetime.now().strftime("%I:%M %p")
        conf_val = event.get("confidence", 0.95)
        screenshot_path = event.get("screenshot_path")
        topic = event.get("topic") or config.NTFY_TOPIC
        custom_message = event.get("message")
    else:
        event_type = str(getattr(event, "type", getattr(event, "event_type", ""))).upper().strip()
        risk_level = str(getattr(event, "risk_level", getattr(event, "riskLevel", ""))).upper().strip()
        patient_id = getattr(event, "patient_id", getattr(event, "patientId", config.PATIENT_ID))
        source = getattr(event, "source", "LIVE CAMERA")
        time_str = getattr(event, "time", getattr(event, "timestamp", datetime.now().strftime("%I:%M %p")))
        conf_val = getattr(event, "confidence", 0.95)
        screenshot_path = getattr(event, "screenshot_path", None)
        topic = getattr(event, "topic", config.NTFY_TOPIC)
        custom_message = getattr(event, "message", None)

    # Immediately return without sending if not confirmed fall or not critical
    is_valid_type = event_type in ("CONFIRMED_FALL", "EMERGENCY ESCALATION", "AUTO-ESCALATION (UNACKNOWLEDGED)")
    is_valid_risk = risk_level in ("CRITICAL", "EMERGENCY")

    if not is_valid_type or not is_valid_risk:
        print("[INFO] No emergency — NTFY skipped")
        return {
            "channel": "ntfy",
            "success": False,
            "skipped": True,
            "reason": "No emergency — NTFY skipped"
        }

    # Dispatch IoT Alert key=1 to Tinkerstream hardware buzzer/server
    send_tinkerstream_alert(1)

    # Normalize source display

    # Normalize source display
    source_upper = str(source).upper()
    if source_upper in ("YOLO", "LIVE", "CAMERA", "WEBCAM", "LIVE CAMERA"):
        source_display = "LIVE CAMERA"
    elif source_upper in ("VIDEO_ANALYSIS", "VIDEO_UPLOAD", "VIDEO", "UPLOADED VIDEO"):
        source_display = "UPLOADED VIDEO"
    elif source_upper in ("SIMULATION", "TEST", "SIMULATION TEST"):
        source_display = "SIMULATION TEST"
    else:
        source_display = source_upper

    if "T" in str(time_str):
        try:
            time_str = datetime.fromisoformat(str(time_str)).strftime("%I:%M %p")
        except Exception:
            pass

    if isinstance(conf_val, (int, float)):
        conf_percent = int(conf_val * 100) if conf_val <= 1.0 else int(conf_val)
    else:
        conf_percent = 95

    # Exact format required
    body_text = custom_message or (
        f"🚨 RECOVERAI — EMERGENCY FALL ALERT\n\n"
        f"🚨 CONFIRMED FALL DETECTED\n\n"
        f"Patient: {patient_id}\n"
        f"Risk: CRITICAL\n"
        f"Source: {source_display}\n"
        f"Time: {time_str}\n"
        f"Confidence: {conf_percent}%\n\n"
        f"📸 Incident evidence attached.\n\n"
        f"⚠️ Please check the patient immediately."
    )

    return notification_service.ntfy.send(
        event_type=event_type,
        patient_id=patient_id,
        risk_level=risk_level,
        screenshot_path=screenshot_path,
        message=body_text,
        topic=topic,
        source=source_display,
        extra_data={"confidence": conf_val}
    )


def send_ntfy_alert(
    event_type: str,
    patient_id: str,
    risk_level: str = "critical",
    screenshot_path: Optional[str] = None,
    message: Optional[str] = None,
    topic: Optional[str] = None,
    source: str = "yolo",
    extra_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Backwards-compatible wrapper calling send_fall_alert.
    """
    clean_type = str(event_type).strip()
    event_dict = {
        "type": clean_type.upper(),
        "event_type": clean_type,
        "patient_id": patient_id,
        "risk_level": str(risk_level).upper(),
        "screenshot_path": screenshot_path,
        "message": message,
        "topic": topic,
        "source": source,
        "confidence": (extra_data or {}).get("confidence", 0.95) if isinstance(extra_data, dict) else 0.95
    }
    return send_fall_alert(event_dict)


# Central emergency alert function alias
send_emergency_alert = send_fall_alert


