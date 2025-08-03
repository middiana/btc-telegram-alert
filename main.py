import time
import requests
from strategy import check_long_signal
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

last_alert_price = None

while True:
    signal = check_long_signal()
    if signal:
        entry = signal["entry_price"]
        if entry != last_alert_price:
            msg = f"""🚨 *롱 진입 신호 발생!*
  
*진입 조건:* {", ".join(signal['conditions'])}
*진입가:* {entry} USDT
*손절가:* {signal['stop_loss']} USDT
*익절가:* {signal['take_profit']} USDT
*추천 레버리지:* {signal['leverage']}x

📊 *지지선 / 저항선:* {signal['support']} / {signal['resistance']}
📉 *채널 구간:* {signal['channel_low']} ~ {signal['channel_high']}

📈 *나스닥 추세:* {signal['nasdaq']['trend']} (지지: {signal['nasdaq']['support']}, 저항: {signal['nasdaq']['resistance']}, RSI: {signal['nasdaq']['rsi']})
📰 *뉴스 요약:* {signal['news']}

🔖 전략명: 영빈 선물전략 v1.2
"""
            send_telegram_message(msg)
            last_alert_price = entry
    time.sleep(300)  # 5분 간격 실행
