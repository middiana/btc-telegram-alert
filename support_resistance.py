# support_resistance.py
import requests
import pandas as pd

def get_ohlcv(symbol="BTCUSDT", interval="15m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    r = requests.get(url)
    raw = r.json()
    df = pd.DataFrame(raw, columns=[
        "time", "open", "high", "low", "close", "volume",
        "close_time", "qav", "trades", "tbav", "tqav", "ignore"
    ])
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    return df

def get_support_resistance(symbol="BTCUSDT"):
    timeframes = ["5m", "15m", "30m", "1h", "4h", "1d"]
    result = {}

    for tf in timeframes:
        df = get_ohlcv(symbol=symbol, interval=tf, limit=100)
        support = round(df["low"].quantile(0.15), 2)
        resistance = round(df["high"].quantile(0.85), 2)
        channel_low = round(df["low"].min(), 2)
        channel_high = round(df["high"].max(), 2)

        result[tf] = {
            "support": support,
            "resistance": resistance,
            "channel_low": channel_low,
            "channel_high": channel_high
        }

    return result
