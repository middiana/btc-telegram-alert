# notifier.py
import requests

# 실제 값으로 교체됨
BOT_TOKEN = "여기에_당신의_텔레그램_봇_토큰"
CHAT_ID = "여기에_당신의_챗_ID"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        res = requests.post(url, data=payload)
        if res.status_code != 200:
            print(f"❌ 텔레그램 전송 실패: {res.text}")
    except Exception as e:
        print(f"❌ 텔레그램 오류: {e}")
