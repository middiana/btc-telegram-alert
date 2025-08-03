from strategy import check_long_signal
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from utils import send_telegram_message

print("✅ main.py 시작")
print("✅ strategy 모듈 import 성공")

signal = check_long_signal()

if signal:
    print("🚀 신호 발생!")
    send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, signal)
else:
    print("📭 신호 없음 또는 조건 미충족")
