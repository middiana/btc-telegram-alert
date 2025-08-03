import pandas as pd
from utils import get_ohlcv, calculate_indicators, send_telegram, get_support_resistance, get_nasdaq_trend, get_news_summary
from config import TELEGRAM_CHAT_ID, TELEGRAM_BOT_TOKEN

def check_signal():
    symbol = "BTCUSDT_UMCBL"
    interval = "15m"

    print(f"🔍 {symbol} 선물 데이터 조회 중...")
    df = get_ohlcv(symbol=symbol, interval=interval, limit=100)

    if df.empty:
        print("⚠️ 데이터 없음")
        return None

    df = calculate_indicators(df)
    latest = df.iloc[-1]

    conditions = []

    if latest["RSI"] < 40:
        conditions.append("RSI < 40")

    if abs((latest["close"] - latest["lower"]) / latest["lower"]) < 0.01:
        conditions.append("볼밴 하단 접근")

    if latest["close"] > latest["EMA20"]:
        conditions.append("EMA20 지지 확인")

    if latest["close"] > latest["EMA50"]:
        conditions.append("EMA50 지지 확인")

    if latest["close"] > latest["middle"]:
        conditions.append("추세 반등")

    if len(conditions) >= 2:
        entry = latest["close"]
        stop = entry * 0.95
        target = entry * 1.10

        support, resistance = get_support_resistance(df)
        nasdaq = get_nasdaq_trend()
        news = get_news_summary()

        message = f"""
📈 [롱 진입 신호 포착 - 영빈 선물전략 v1.2]
✅ 조건 만족: {', '.join(conditions)}
📌 진입가: {entry:.2f}
🛑 손절가: {stop:.2f}
🎯 익절가: {target:.2f}

📊 지지선: {support:.2f} / 저항선: {resistance:.2f}
📉 나스닥 추세: {nasdaq}
📰 뉴스 요약: {news}
"""
        send_telegram(message.strip(), TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        return True

    print("❌ 진입 조건 미충족")
    return None
