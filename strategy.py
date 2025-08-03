import pandas as pd
import numpy as np
from utils import (
    get_ohlcv, get_support_resistance_levels,
    get_channel_levels, get_nasdaq_info, get_latest_news
)
from config import SYMBOL, INTERVAL

def check_long_signal():
    try:
        ohlcv = get_ohlcv(SYMBOL, INTERVAL)
        if ohlcv is None:
            return None

        df = pd.DataFrame(ohlcv, columns=[
            "timestamp", "open", "high", "low", "close", "volume"
        ])
        df["close"] = df["close"].astype(float)
        df["low"] = df["low"].astype(float)
        df["high"] = df["high"].astype(float)

        df["rsi"] = compute_rsi(df["close"])
        df["ema20"] = df["close"].ewm(span=20).mean()
        df["ema50"] = df["close"].ewm(span=50).mean()
        df["basis"] = df["close"].rolling(window=20).mean()
        df["stddev"] = df["close"].rolling(window=20).std()
        df["upper"] = df["basis"] + 2 * df["stddev"]
        df["lower"] = df["basis"] - 2 * df["stddev"]

        latest = df.iloc[-1]
        conditions = []

        if latest["rsi"] < 40:
            conditions.append("RSI < 40")
        if latest["close"] <= latest["lower"] * 1.01:
            conditions.append("볼린저 밴드 하단 접근")
        if latest["close"] >= latest["ema20"]:
            conditions.append("EMA20 지지")
        if latest["close"] >= latest["ema50"]:
            conditions.append("EMA50 지지")

        support, resistance = get_support_resistance_levels(ohlcv)
        if latest["close"] <= support * 1.01:
            conditions.append("멀티타임프레임 지지선 접근")

        entry_price = latest["close"]
        stop_loss = round(entry_price * 0.95, 2)
        take_profit = round(entry_price * 1.10, 2)

        leverage = 2
        if len(conditions) >= 4:
            leverage = 5
        elif len(conditions) == 3:
            leverage = 3

        channel_low, channel_high = get_channel_levels(ohlcv)
        nasdaq = get_nasdaq_info()
        news = get_latest_news()

        if len(conditions) >= 2:
            message = f"""
📊 <b>롱 진입 시그널 발생!</b>
🔹 전략: 영빈 선물전략 v1.2
🔸 조건 만족: {len(conditions)}개 - {', '.join(conditions)}

💰 진입가: <b>{entry_price:.2f}</b>
📉 손절가: <b>{stop_loss:.2f}</b>
📈 익절가: <b>{take_profit:.2f}</b>
⚙️ 추천 레버리지: <b>{leverage}x</b>

📌 지지/저항 (15분): {support:.2f} / {resistance:.2f}
📌 채널 구간: {channel_low:.2f} ~ {channel_high:.2f}

📊 나스닥 추세
- 지지: {nasdaq['support']}, 저항: {nasdaq['resistance']}, RSI: {nasdaq['rsi']}

🌐 주요 뉴스 요약:
- {news[0]}
- {news[1]}
- {news[2]}
"""
            return message.strip()
        else:
            return None
    except Exception as e:
        print(f"❌ check_long_signal 실행 실패: {e}")
        return None

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
