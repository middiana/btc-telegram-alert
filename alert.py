import requests
import time

BOT_TOKEN = "여기에_당신의_텔레그램_봇_토큰"
CHAT_ID = "여기에_당신의_챗_ID"

def send_telegram_alert():
    message = """
🚨 BTCUSDT 롱 진입 신호 발생!
진입가: 62,300 / 손절: 61,700 / 목표: 63,700
"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

# 예시: 30분마다 알림 보내기
while True:
    send_telegram_alert()
    print("알림 보냈습니다!")
    time.sleep(1800)
