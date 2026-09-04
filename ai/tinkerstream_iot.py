"""
Tinkerstream IoT LED & Buzzer Alert Module
------------------------------------------
State-Change Optimized IoT Integrator:
- Fall detected -> key=1 (LED ON + Buzzer ON)
- Fall cleared / Normal -> key=0 (LED OFF + Buzzer OFF)
- Avoids repeated unnecessary API calls by tracking last_alert_state.
- Handles network/request exceptions safely without crashing the application.
"""

import requests
import logging

logger = logging.getLogger("ai.tinkerstream")

last_alert_state = None

def set_alert(state: int) -> bool:
    """
    Send alert state (1 or 0) to external Tinkerstream IoT server.
    Tries primary endpoint and safe fallback endpoints.
    """
    urls = [
        "https://www.tinkerstream.com/sbj/alert.php",
        "https://www.tinkerstream.com/api/alert.php"
    ]
    for url in urls:
        try:
            response = requests.get(url, params={"key": state}, timeout=5)
            if response.status_code == 200:
                print(f"[IOT_ALERT] Tinkerstream Alert state={state}, Status={response.status_code}, Response={response.text.strip()}")
                logger.info(f"Tinkerstream Alert state={state}, Status={response.status_code}, Response={response.text.strip()}")
                return True
        except requests.RequestException as e:
            logger.warning(f"Tinkerstream Alert API error for {url}: {e}")
            print(f"Alert API error: {e}")
    return False

def update_alert_state(fall_detected: bool):
    """
    State-change optimization:
    Only sends an HTTP request when the alert state changes (0 -> 1 or 1 -> 0).
    Prevents repeated unnecessary API calls on every frame.
    """
    global last_alert_state

    current_state = 1 if fall_detected else 0

    if current_state != last_alert_state:
        set_alert(current_state)
        last_alert_state = current_state
