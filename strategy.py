from config import SYMBOL, INTERVAL
import random

def check_long_signal():
    # 예시 조건 (랜덤, 실제 로직 대체)
    conditions_met = random.sample([
        "RSI < 40",
        "볼린저밴드 하단 접근",
        "EMA20 지지",
        "다중 지지선 접근",
        "추세 둔화 캔들"
    ], k=3)  # 최소 2개 만족이라 가정

    condition_count = len(conditions_met)
    price = 61000  # 예시 진입가
    stop_loss = price * 0.95
    take_profit = price * 1.10

    leverage = {2: "2x", 3: "3x", 4: "5x", 5: "5x"}.get(condition_count, "2x")

    levels = {
        "5m": {"지지선": "60,800", "저항선": "61,400", "채널": "60,700 ~ 61,500"},
        "15m": {"지지선": "60,500", "저항선": "61,800", "채널": "60,400 ~ 61,900"},
        "30m": {"지지선": "60,000", "저항선": "62,000", "채널": "59,900 ~ 62,100"},
        "1h": {"지지선": "59,800", "저항선": "62,500", "채널": "59,600 ~ 62,600"},
        "4h": {"지지선": "59,000", "저항선": "63,000", "채널": "58,800 ~ 63,200"},
        "1d": {"지지선": "57,000", "저항선": "65,000", "채널": "56,500 ~ 65,500"},
    }

    nasdaq_info = "나스닥 지수 RSI 45, 15분봉 저항 접근 중, 추세 약세"
    news_summary = "📉 Fed 금리 동결 시사, 📈 BTC ETF 자금 순유입 지속, 🌍 바이낸스 규제 불확실성"

    message = f"""📢 <b>[영빈 선물전략 v1.2]</b>

🟢 <b>롱 진입 신호 발생</b>
조건 만족 수: {condition_count}개 → <b>{', '.join(conditions_met)}</b>

📍 <b>진입가:</b> {price:.2f} USDT
⛔ <b>손절가:</b> {stop_loss:.2f} USDT
🎯 <b>익절가:</b> {take_profit:.2f} USDT
📌 <b>추천 레버리지:</b> {leverage}

📊 <b>다중 지지/저항선</b>
""" + "\n".join([
        f"⏱️ <b>{tf}</b> → 지지: {lv['지지선']} / 저항: {lv['저항선']} / 채널: {lv['채널']}"
        for tf, lv in levels.items()
    ]) + f"""

📈 <b>나스닥 추세 요약</b>: {nasdaq_info}

📰 <b>글로벌 뉴스 요약</b>: {news_summary}
"""

    return message
