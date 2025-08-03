from strategy import check_long_signal
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from utils import send_telegram_message
import time

print("✅ main.py 시작")

if __name__ == "__main__":
    print("✅ strategy 모듈 import 성공")
    signal = check_long_signal()
    print(f"📦 check_long_signal 결과: {signal}")
    if signal:
        send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, signal)
