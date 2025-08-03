import requests
import pandas as pd
import numpy as np
from datetime import datetime
import time

# OHLCV 데이터 가져오기
def get_ohlcv(symbol="BTCUSDT_UMCBL", interval="15m", limit=200):
    interval_map = {
        "1m": "60", "5m": "300", "15m": "900", "30m": "1800",
        "1h": "3600", "4h": "14400", "1d": "86400"
    }
    granularity = interval_map.get(interval)
    end_time = int(time.time() * 1000)
    start_time = end_time - (int(granularity) * limit * 1000)

    url = "https://api.bitget.com/api/mix/v1/market/candles"
    params = {
        "symbol": symbol,
        "granularity": granularity,
        "startTime": str(start_time),
        "endTime": str(end_time)
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        raw = response.json()
        data = raw["data"] if isinstance(raw, dict) else raw
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "turnover"])
        df["timestamp"] = pd.to_datetime(df["timestamp"].astype(np.int64), unit="ms")
        for col in ["open", "high", "low", "close", "volume", "turnover"]:
            df[col] = df[col].astype(float)
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df
    else:
        print(f"❌ OHLCV 응답 실패: {response.text}")
        return pd.DataFrame()

# 기술적 지표 계산
def calculate_indicators(df):
    df["EMA20"] = df["close"].ewm(span=20).mean()
    df["EMA50"] = df["close"].ewm(span=50).mean()
    df["upper"], df["middle"], df["lower"] = bollinger_bands(df["close"])
    df["RSI"] = rsi(df["close"])
    return df

def bollinger_bands(series, window=20, num_std=2):
    rolling_mean = series.rolling(window).mean()
    rolling_std = series.rolling(window).std()
    upper_band = rolling_mean + (rolling_std * num_std)
    lower_band = rolling_mean - (rolling_std * num_std)
    return upper_band, rolling_mean, lower_band

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# 다중 타임프레임 지지선/저항선 계산
def calculate_support_resistance(df):
    recent = df.tail(20)
    return recent["low"].min(), recent["high"].max()

# 채널 구간 계산
def calculate_channel(df):
    return df["low"].min(), df["high"].max()

# 메인 체크 함수
def check_signal():
    symbol = "BTCUSDT_UMCBL"
    df = get_ohlcv(symbol=symbol, interval="15m", limit=200)
    if df.empty:
        print("⚠️ 데이터 없음")
        return None

    df = calculate_indicators(df)
    latest = df.iloc[-1]
    support, resistance = calculate_support_resistance(df)
    channel_low, channel_high = calculate_channel(df)

    # 진입 조건 평가
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
        entry_price = latest["close"]
        stop_loss = entry_price * 0.95
        take_profit = entry_price * 1.10

        # 추천 레버리지
        if len(conditions) >= 4:
            leverage = "5x"
        elif len(conditions) == 3:
            leverage = "3x"
        else:
            leverage = "2x"

        print("📈 [롱 진입 신호 포착]")
        print(f"조건 만족: {conditions}")
        print(f"진입가: {entry_price:.2f} / 손절가: {stop_loss:.2f} / 익절가: {take_profit:.2f}")
        print(f"추천 레버리지: {leverage}")
        print(f"지지선: {support:.2f} / 저항선: {resistance:.2f}")
        print(f"채널 하단: {channel_low:.2f} / 채널 상단: {channel_high:.2f}")

        return {
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "conditions": conditions,
            "leverage": leverage,
            "support": support,
            "resistance": resistance,
            "channel_low": channel_low,
            "channel_high": channel_high
        }
    else:
        print("❌ 진입 조건 미충족")
        return None
