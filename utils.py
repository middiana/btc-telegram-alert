import requests
import pandas as pd
from datetime import datetime

def get_ohlcv(symbol, interval, limit=500):
    url = f"https://api.bitget.com/api/v2/market/candles?symbol={symbol}&granularity={interval}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume"
        ])
        df = df.sort_values(by="timestamp")
        df["close"] = df["close"].astype(float)
        df["low"] = df["low"].astype(float)
        df["high"] = df["high"].astype(float)
        return df.reset_index(drop=True)
    else:
        print(f"❌ 데이터 요청 실패: {response.status_code}")
        return pd.DataFrame()

def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(df, period=20, stddev=2):
    sma = df["close"].rolling(window=period).mean()
    std = df["close"].rolling(window=period).std()
    upper = sma + stddev * std
    lower = sma - stddev * std
    return upper, lower

def calculate_ema(df, period=20):
    return df["close"].ewm(span=period, adjust=False).mean()

def get_support_resistance(df):
    support = df["low"].min()
    resistance = df["high"].max()
    return round(support, 2), round(resistance, 2)

def get_channel_range(df):
    high = df["high"].max()
    low = df["low"].min()
    return round(low, 2), round(high, 2)

def get_nasdaq_trend():
    return {
        "support": 17500,
        "resistance": 17850,
        "rsi": 53,
        "trend": "약한 상승세"
    }

def get_crypto_news():
    return "ETF 순유입 지속, 단기 조정 이후 반등 기대감 유지 중"
