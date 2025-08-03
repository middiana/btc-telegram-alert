import time
from strategy import check_long_signal
from utils import send_telegram_message
from config import CHAT_ID

last_alert = {
    "entry_price": None,
    "conditions": None
}

def should_send_alert(entry_price, conditions):
    global last_alert
    if last_alert["entry_price"] == entry_price and last_alert["conditions"] == conditions:
        return False
    last_alert["entry_price"] = entry_price
    last_alert["conditions"] = conditions
    return True

if __name__ == "__main__":
    while True:
        result = check_long_signal()

        if result:
            if should_send_alert(result["entry_price"], result["conditions"]):
                send_telegram_message(result["message"])
            else:
                print("⚠️ 이미 동일 조건의 알림이 발송됨. 중복 알림 생략.")
        else:
            print("📭 진입 조건 없음.")

        time.sleep(300)  # 5분 간격
