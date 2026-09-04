import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests
import config

def test_telegram_connectivity():
    token = getattr(config, "TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = getattr(config, "TELEGRAM_CHAT_ID", "").strip() or "1267104193"

    print("=== TELEGRAM CONNECTIVITY TEST ===", flush=True)
    print(f"Chat ID Loaded:               {chat_id}", flush=True)
    print(f"Token Configured in .env:     {'YES (Length: ' + str(len(token)) + ')' if token else 'NO (Awaiting user token in .env)'}", flush=True)

    if not token:
        print("\n[STATUS] TELEGRAM_BOT_TOKEN is not set yet in .env file.", flush=True)
        print("Please open .env and add your BotFather token: TELEGRAM_BOT_TOKEN=your_token_here", flush=True)
        return {
            "token_loaded": False,
            "chat_id": chat_id,
            "message_sent": False,
            "status_code": None,
            "reason": "Token missing in .env"
        }

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "RecoverAI Telegram connection test ✅"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        status_code = response.status_code
        print(f"Telegram HTTP Status:         {status_code}", flush=True)
        
        if status_code == 200:
            print("[SUCCESS] Test message 'RecoverAI Telegram connection test ✅' delivered to Chat ID!", flush=True)
            return {
                "token_loaded": True,
                "chat_id": chat_id,
                "message_sent": True,
                "status_code": status_code,
                "response": "Success"
            }
        else:
            print(f"[ERROR] Telegram API returned HTTP {status_code}: {response.text}", flush=True)
            return {
                "token_loaded": True,
                "chat_id": chat_id,
                "message_sent": False,
                "status_code": status_code,
                "response": response.text
            }
    except Exception as e:
        print(f"[EXCEPTION] Network error contacting Telegram API: {e}", flush=True)
        return {
            "token_loaded": True,
            "chat_id": chat_id,
            "message_sent": False,
            "status_code": None,
            "error": str(e)
        }

if __name__ == "__main__":
    test_telegram_connectivity()
