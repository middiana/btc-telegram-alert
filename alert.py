import requests
import time
import os

print("✅ 프로그램 시작!")

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

print(f"✅ BOT_TOKEN: {BOT_TOKEN}")
print(f"✅ CHAT_ID: {CHAT_ID}")

# 환경변수 비어있으면 종료
if not BOT_TOKEN or not CHAT_ID:
    print("❌ 환경변수 설정 오류! TELEGRAM_TOKEN 또는 TELEGRAM_CHAT_ID가 비어있습니다.")
    exit()

def send_telegram_alert():
    print("🚀 텔레그램 메시지 전송 시도 중...")
    message = """
🚨 BTCUSDT 롱 진입 신호 발생!
진입가: 62,300 / 손절: 61,700 / 목표: 63,700
"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    print(f"📬 응답 코드: {response.status_code}")
    print(f"📨 응답 내용: {response.text}")

# 테스트용으로 1번만 실행
send_telegram_alert()
print("🎉 완료됨! 프로그램 종료")
