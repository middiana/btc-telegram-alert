import requests
import pandas as pd
import numpy as np

def get_ohlcv(symbol="BTCUSDT_UMCBL", interval="15m", limit=100):
    url = f"https://api.bitget.com/api/v2/market/candles"
    params = {
        "symbol": symbol,
        "granularity": interval,
        "limit": str(limit)
    }

    for _ in range(3):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json().get("data")
            if data:
                df = pd.DataFrame(data, columns=[
                    "timestamp", "open", "high", "low", "close", "volume", "quoteVolume"
                ])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                df = df.sort_values("timestamp").reset_index(drop=True)
                for col in ["open", "high", "low", "close", "volume", "quoteVolume"]:
                    df[col] = df[col].astype(float)
                return df
        else:
            print(f"❌ OHLCV 응답 실패: {response.text}")
    return pd.DataFrame()

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
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

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

    # ✅ 진입 조건 평가
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

        print("📈 [롱 진입 신호 포착]")
        print(f"조건 만족: {conditions}")
        print(f"진입가: {entry_price:.2f} / 손절가: {stop_loss:.2f} / 익절가: {take_profit:.2f}")
        return {
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "conditions": conditions
        }

    print("❌ 진입 조건 미충족")
    return None
