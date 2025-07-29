import requests
import pandas as pd
from datetime import datetime, timedelta
from indicators import calculate_rsi, calculate_ema, calculate_bollinger_bands
from notifier import send_telegram_alert

def fetch_latest_15m():
    url = "https://fapi.binance.com/fapi/v1/klines"
    end = int(datetime.utcnow().timestamp() * 1000)
    start = end - 1000 * 15 * 60  # 15분
    params = {
        "symbol": "BTCUSDT",
        "interval": "15m",
        "limit": 100
    }
    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "_1", "_2", "_3", "_4", "_5", "_6"
    ])
    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    df["rsi"] = calculate_rsi(df["close"], 14)
    df["ema20"] = calculate_ema(df["close"], 20)
    df["ema50"] = calculate_ema(df["close"], 50)
    df["bb_lower"], _ = calculate_bollinger_bands(df["close"])
    return df

def check_signal():
    df = fetch_latest_15m()
    latest = df.iloc[-1]
    checks = {
        "RSI < 40": latest["rsi"] < 40,
        "볼밴 하단 접근": latest["close"] <= latest["bb_lower"] * 1.01,
        "EMA 지지": latest["close"] >= latest["ema20"] or latest["close"] >= latest["ema50"],
        "다중 지지 접근": False,  # 추후 구현
        "추세 둔화/반전": False   # 추후 구현
    }
    satisfied = [k for k, v in checks.items() if v]
    if len(satisfied) >= 2:
        send_telegram_alert(latest, checks, len(satisfied))
