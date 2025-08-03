import requests
import pandas as pd
import numpy as np
from utils import get_support_resistance_levels, get_channel_levels, get_nasdaq_info, get_latest_news
from config import SYMBOL

def get_ohlcv(symbol, interval, limit=100):
    url = f"https://api.bitget.com/api/v2/market/candles"
    params = {
        "symbol": symbol,
        "granularity": interval,
        "limit": limit
    }
    response = requests.get(url, params=params)
    raw_data = response.json().get("data", [])
    if not raw_data or not isinstance(raw_data, list):
        print("⚠️ 데이터 없음")
        return None
    df = pd.DataFrame(raw_data, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "quote_volume"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    return df[::-1].reset_index(drop=True)

def calculate_indicators(df):
    df["EMA20"] = df["close"].ewm(span=20).mean()
    df["EMA50"] = df["close"].ewm(span=50).mean()
    df["RSI"] = compute_rsi(df["close"], 14)

    bb_std = df["close"].rolling(window=20).std()
    df["BB_upper"] = df["EMA20"] + 2 * bb_std
    df["BB_lower"] = df["EMA20"] - 2 * bb_std
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def check_long_signal():
    df = get_ohlcv(SYMBOL, interval="900")  # 15분봉
    if df is None or df.empty:
        return None

    df = calculate_indicators(df)
    latest = df.iloc[-1]

    conditions = []
    if latest["RSI"] < 40:
        conditions.append("RSI < 40")
    if latest["close"] <= latest["BB_lower"] * 1.01:
        conditions.append("볼밴 하단 접근")
    if latest["close"] > latest["EMA20"]:
        conditions.append("EMA20 지지 확인")
    if latest["close"] > latest["EMA50"]:
        conditions.append("EMA50 지지 확인")
    if latest["EMA20"] > df["EMA20"].iloc[-2]:
        conditions.append("추세 반등")

    if len(conditions) < 2:
        return None

    entry = round(latest["close"], 2)
    stop = round(entry * 0.95, 2)
    target = round(entry * 1.10, 2)

    # 추천 레버리지
    if len(conditions) >= 4:
        leverage = "5x (강력 신호)"
    elif len(conditions) == 3:
        leverage = "3x (중간 신호)"
    else:
        leverage = "2x (약한 신호)"

    support_resist = get_support_resistance_levels(df)
    channel = get_channel_levels(df)
    nasdaq = get_nasdaq_info()
    news = get_latest_news()

    message = f"""📈 [롱 진입 신호 포착]
조건 만족: {conditions}
진입가: {entry} / 손절가: {stop} / 익절가: {target}
추천 레버리지: {leverage}

📊 지지/저항선
{support_resist}

📉 채널 구간
{channel}

📊 나스닥 지수 정보
{nasdaq}

🗞️ 주요 뉴스 요약
{news}

📌 전략: 영빈 선물전략 v1.2
"""
    return {
        "entry_price": entry,
        "conditions": conditions,
        "message": message
    }
