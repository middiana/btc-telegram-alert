import time
from strategy import check_long_signal
from utils import send_telegram_message

last_signal = None

def main_loop():
    global last_signal
    while True:
        try:
            signal = check_long_signal()
            if signal != last_signal:
                send_telegram_message(signal)
                last_signal = signal
        except Exception as e:
            send_telegram_message(f"❗ 오류 발생: {str(e)}")
        time.sleep(300)  # 5분 간격

if __name__ == "__main__":
    main_loop()
