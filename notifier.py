import os
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_alert(row, checks, matched_count):
    check_lines = []
    for condition, status in checks.items():
        check_lines.append(f"{'☑️' if status else '⬜'} {condition}")

    price = row["close"]
    sl = round(price * 0.95, 2)
    tp = round(price * 1.10, 2)
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    msg = f"""📢 [영빈 선물전략 v1.1] 롱 진입 신호 발생 (15분봉 기준)

✅ 조건 만족: {matched_count}개 / {len(checks)}
{chr(10).join(check_lines)}

📍진입가: {price:.2f} USDT
📉 손절가: {sl:.2f} USDT (-5%)
📈 익절가: {tp:.2f} USDT (+10%)
📊 레버리지: {min(5, max(2, matched_count))}x

⏰ 알림시간: {time_str} (UTC+9)
"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    requests.post(url, json=payload)
