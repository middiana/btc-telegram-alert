# main.py
import time
from flask import Flask
from strategy import check_entry_signal
from notifier import send_telegram_alert

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ 영빈 선물전략 v1.0 서버 실행 중"

def main_loop():
    while True:
        try:
            signal = check_entry_signal()
            if signal:
                send_telegram_alert(signal)
        except Exception as e:
            print(f"[오류 발생] {e}")
        time.sleep(300)  # 5분 간격 실행

if __name__ == '__main__':
    main_loop()
