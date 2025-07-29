import requests
import pandas as pd
from datetime import datetime, timedelta
from indicators import calculate_rsi, calculate_ema, calculate_bollinger_bands

def fetch_binance_ohlcv(start_time, end_time):
    url = "https://fapi.binance.com/fapi/v1/klines"
    all_data = []
    while start_time < end_time:
        params = {
            "symbol": "BTCUSDT",
            "interval": "15m",
            "startTime": int(start_time.timestamp() * 1000),
            "limit": 1000
        }
        res = requests.get(url, params=params)
        data = res.json()
        if not data:
            break
        all_data += data
        last = data[-1][0] / 1000
        start_time = datetime.utcfromtimestamp(last) + timedelta(minutes=15)
    return all_data

def preprocess(data):
    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "_", "_", "_", "_", "_", "_"
    ])
    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
    df["rsi"] = calculate_rsi(df["close"], 14)
    df["ema20"] = calculate_ema(df["close"], 20)
    df["ema50"] = calculate_ema(df["close"], 50)
    df["bb_low"] = calculate_bollinger_bands(df["close"])[0]
    return df

def simulate_strategy(df):
    balance = 100
    position = None
    entry_price = 0
    trades = 0
    current_year = None
    results = {}

    for i in range(50, len(df)):
        row = df.iloc[i]
        year = row["timestamp"].year

        if current_year != year:
            current_year = year
            results[year] = {"trades": 0, "return_pct": 0.0}
            balance = 100

        if not position:
            conditions = 0
            if row["rsi"] < 40:
                conditions += 1
            if row["close"] <= row["bb_low"] * 1.01:
                conditions += 1
            if row["close"] >= row["ema20"] or row["close"] >= row["ema50"]:
                conditions += 1

            if conditions >= 2:
                position = "long"
                entry_price = row["close"]
                trades += 1
                results[year]["trades"] += 1
                # 전략 신뢰도에 따라 레버리지 2~5배 자동 배정
                lev = min(5, max(2, conditions))
        else:
            change = (row["close"] - entry_price) / entry_price * 100
            if change >= 10:
                pnl = 10 * lev
                balance *= (1 + pnl / 100)
                position = None
            elif change <= -5:
                pnl = -5 * lev
                balance *= (1 + pnl / 100)
                position = None
        results[year]["return_pct"] = round(balance - 100, 2)

    return results

def run_backtest():
    start = datetime(2023, 1, 1)
    end = datetime(2025, 1, 1)
    raw_data = fetch_binance_ohlcv(start, end)
    df = preprocess(raw_data)
    return simulate_strategy(df)
