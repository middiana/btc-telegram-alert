import requests
import pandas as pd
import numpy as np
import time
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ 텔레그램 전송 오류: {e}")
    return response

def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    delta = data.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def get_bollinger_bands(close_prices: pd.Series, window: int = 20, num_std_dev: float = 2.0):
    sma = close_prices.rolling(window).mean()
    std = close_prices.rolling(window).std()
    upper_band = sma + (std * num_std_dev)
    lower_band = sma - (std * num_std_dev)
    return upper_band, lower_band

def get_ema(data: pd.Series, period: int = 20) -> pd.Series:
    return data.ewm(span=period, adjust=False).mean()

def get_support_resistance_levels(data: pd.DataFrame, window: int = 20):
    support = data['low'].rolling(window=window).min().iloc[-1]
    resistance = data['high'].rolling(window=window).max().iloc[-1]
    return support, resistance

def get_channel_levels(data: pd.DataFrame):
    highs = data['high']
    lows = data['low']
    channel_high = highs.rolling(window=20).max().iloc[-1]
    channel_low = lows.rolling(window=20).min().iloc[-1]
    return channel_high, channel_low
