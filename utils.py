import requests
import pandas as pd
from datetime import datetime

import requests
import pandas as pd
from datetime import datetime

def get_ohlcv(symbol, interval, limit=100):
    granularity_map = {
        "1m": 60,
        "5m": 300,
        "15m": 900,
        "30m": 1800,
        "1h": 3600,
        "4h": 14400,
        "1d": 86400
    }
    granularity = granularity_map.get(interval, 900)

    url = "https://api.bitget.com/api/mix/v1/market/candles"
    params = {
        "symbol": symbol,
        "granularity": granularity,
        "limit": limit
    }

    headers = {
        "User-Agent": "Mozilla/5.0",  # ✅ 일부 서버에서 필수
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            print(f"❌ 데이터 요청 실패: {response.status_code} - {response.text}")
            return pd.DataFrame()

        raw = response.json().get("data", [])
        if not raw:
            print("⚠️ 받은 데이터가 비어있음")
            return pd.DataFrame()

        df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume", "_"])
        df = df.astype(float)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df.sort_values(by="timestamp").reset_index(drop=True)

    except Exception as e:
        print(f"❌ get_ohlcv 예외 발생: {e}")
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
