import time
import telegram
from strategy import check_long_signal
from config import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN

bot = telegram.Bot(token=TELEGRAM_TOKEN)
last_signal = None

print("✅ main.py 시작")

while True:
    print("🚀 check_long_signal 실행 시도 중...")
    signal = check_long_signal()
    print(f"📦 check_long_signal 결과: {signal}")

    if signal and signal != last_signal:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=signal, parse_mode='HTML')
        last_signal = signal
    time.sleep(300)
