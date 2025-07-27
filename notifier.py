# notifier.py
import requests

BOT_TOKEN = "8454656493:AAGjqH4zt2Mn-HBleMtCrFgsXLwModMDbC8"
CHAT_ID = "7426355357"

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
