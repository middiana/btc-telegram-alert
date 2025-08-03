import requests
import pandas as pd
import numpy as np
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def get_ohlcv(symbol="BTCUSDT_UMCBL", interval="15m", limit=100):
    interval_map = {
        "1m": "60", "5m": "300", "15m": "900", "30m": "1800",
        "1h": "3600", "4h": "14400", "1d": "86400",
    }

    granularity = interval_map.get(interval)
    if granularity is None:
        raise ValueError(f"Unsupported interval: {interval}")

    url = f"https://api.bitget.com/api/mix/v1/market/candles"
    params = {
        "symbol": symbol,
        "granularity": granularity
    }

    for _ in range(3):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            result = response.json()
            data = result.get("data")
            if not data:
                continue
            df = pd.DataFrame(data, columns=[
                "timestamp", "open", "high", "low", "close", "volume", "turnover"
            ])
            df["timestamp"] = pd.to_datetime(df["timestamp"].astype(float), unit="ms")
            df = df.sort_values("timestamp").reset_index(drop=True)
            for col in ["open", "high", "low", "close", "volume", "turnover"]:
                df[col] = df[col].astype(float)
            return df
    return pd.DataFrame()

def calculate_indicators(df):
    df["EMA20"] = df["close"].ewm(span=20).mean()
    df["EMA50"] = df["close"].ewm(span=50).mean()
    df["upper"], df["middle"], df["lower"] = bollinger_bands(df["close"])
    df["RSI"] = rsi(df["close"])
    return df

def bollinger_bands(series, window=20, num_std=2):
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()
    return mean + num_std * std, mean, mean - num_std * std

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_support_resistance(df, lookback=20):
    support = df["low"].tail(lookback).min()
    resistance = df["high"].tail(lookback).max()
    return support, resistance

def get_nasdaq_trend():
    # 추후 실제 API 연동 가능, 현재는 예시
    return "RSI 과매도권 + 지지선 근접 (상승 가능성)"

def get_news_summary():
    # 추후 웹스크래핑 또는 뉴스 API 가능, 현재는 예시
    return "ETF 유입 지속 / CPI 대기 / 미장 상승 출발"
    
def send_telegram(message, bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("텔레그램 전송 실패:", e)
