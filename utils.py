import requests
import pandas as pd
import numpy as np

# Bitget API에서 OHLCV 데이터 가져오기
def get_ohlcv(symbol, interval, limit=100):
    url = "https://api.bitget.com/api/mix/v1/market/candles"
    params = {
        "symbol": symbol,
        "granularity": interval,
        "limit": limit
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()["data"]
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df = df.astype({
            "open": float, "high": float, "low": float,
            "close": float, "volume": float
        })
        df.sort_values("timestamp", inplace=True)
        return df
    else:
        print(f"❌ 데이터 요청 실패: {response.status_code} - {response.text}")
        return None

# RSI 계산 함수
def calculate_rsi(data, period=14):
    delta = data['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# 볼린저 밴드 계산 함수
def calculate_bollinger_bands(data, period=20, num_std_dev=2):
    ma = data['close'].rolling(window=period).mean()
    std = data['close'].rolling(window=period).std()
    upper_band = ma + num_std_dev * std
    lower_band = ma - num_std_dev * std
    return upper_band, lower_band

# EMA 계산
def calculate_ema(data, period=20):
    return data['close'].ewm(span=period, adjust=False).mean()
