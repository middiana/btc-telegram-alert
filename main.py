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
    try:
        response = requests.post(url, data=payload)
        print("📨 텔레그램 응답:", response.status_code, response.text)
    except Exception as e:
        print(f"❌ 텔레그램 전송 실패: {e}")

last_alert_price = None

print("🔄 [영빈 선물전략 v1.2] 실행 시작됨.")

while True:
    print("✅ 전략 점검 중...")

    try:
        signal = check_long_signal()
        print("📦 check_long_signal 반환값:", signal)

        if signal:
            entry = signal.get("entry_price", None)
            if entry != last_alert_price:
                print("📢 조건 충족! 텔레그램 전송 중...")

                msg = f"""🚨 *롱 진입 신호 발생!*
  
*진입 조건:* {", ".join(signal.get('conditions', []))}
*진입가:* {entry} USDT
*손절가:* {signal.get('stop_loss')}
*익절가:* {signal.get('take_profit')}
*추천 레버리지:* {signal.get('leverage')}x

📊 *지지선 / 저항선:* {signal.get('support')} / {signal.get('resistance')}
📉 *채널 구간:* {signal.get('channel_low')} ~ {signal.get('channel_high')}

📈 *나스닥 추세:* {signal.get('nasdaq', {}).get('trend')} (지지: {signal.get('nasdaq', {}).get('support')}, 저항: {signal.get('nasdaq', {}).get('resistance')}, RSI: {signal.get('nasdaq', {}).get('rsi')})
📰 *뉴스 요약:* {signal.get('news')}

🔖 전략명: 영빈 선물전략 v1.2
"""
                send_telegram_message(msg)
                last_alert_price = entry
            else:
                print("⏳ 동일한 조건으로 이미 알림 전송됨.")
        else:
            print("⏳ 조건 미충족.")
    except Exception as e:
        print(f"❌ 예외 발생 (check_long_signal 또는 전체): {e}")

    print("🕒 5분 후 다시 반복\n")
    time.sleep(300)
