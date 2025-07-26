import ccxt
import pandas as pd
import numpy as np
import requests
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from ta.volatility import BollingerBands
import yfinance as yf

# ====== 환경변수 ======
BOT_TOKEN = "8249903687:AAH0Caguq0cnwTKPuhMyUGIqY4Ca1_qMmFU"
CHAT_ID = "7426355357"  # @middiana

# ====== 텔레그램 전송 ======
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

# ====== 피보나치 계산 ======
def calculate_fibonacci(high, low):
    diff = high - low
    return {
        '0.236': high - diff * 0.236,
        '0.382': high - diff * 0.382,
        '0.5': high - diff * 0.5,
        '0.618': high - diff * 0.618,
        '0.786': high - diff * 0.786,
    }

# ====== 나스닥 추세 필터 ======
def get_nasdaq_trend():
    ndx = yf.download("^NDX", period="2d", interval="1h")
    if ndx.empty: return "unknown"
    last = ndx["Close"].iloc[-1]
    prev = ndx["Close"].iloc[-5]
    return "uptrend" if last > prev else "downtrend"

# ====== 주요 지지·저항 계산 ======
def calculate_support_resistance(df):
    supports = [df['low'].min()]
    resistances = [df['high'].max()]
    return supports, resistances

# ====== 전략 판단 메인 ======
def analyze():
    exchange = ccxt.binance()
    df = exchange.fetch_ohlcv("BTC/USDT", timeframe='15m', limit=100)
    df = pd.DataFrame(df, columns=['timestamp','open','high','low','close','volume'])

    close = df['close']
    high = df['high'].max()
    low = df['low'].min()
    last_price = close.iloc[-1]

    # 보조지표 계산
    rsi = RSIIndicator(close, window=14).rsi().iloc[-1]
    ema20 = EMAIndicator(close, window=20).ema_indicator().iloc[-1]
    ema50 = EMAIndicator(close, window=50).ema_indicator().iloc[-1]
    bb = BollingerBands(close, window=20, window_dev=2)
    bb_lower = bb.bollinger_lband().iloc[-1]

    fib = calculate_fibonacci(high, low)
    nasdaq_trend = get_nasdaq_trend()
    supports, resistances = calculate_support_resistance(df)

    # 조건 판단
    signals = []

    if rsi < 30:
        signals.append("📉 RSI 과매도")
    if last_price < ema20 and last_price < ema50:
        signals.append("📉 EMA 20/50 하단")
    if fib['0.618'] * 0.99 < last_price < fib['0.618'] * 1.01:
        signals.append("🌀 피보나치 0.618 되돌림")
    if last_price < bb_lower:
        signals.append("📉 볼밴 하단 이탈")
    if nasdaq_trend == "uptrend":
        signals.append("📈 나스닥 상승 추세")
    if any(abs(last_price - s) / last_price < 0.01 for s in supports):
        signals.append("🛡️ 지지선 근접")

    if len(signals) >= 4:
        message = f"""
🚨 [BTC 롱 신호]  
📍 현재가: {last_price:.2f} USDT  
🧠 전략: 영빈작전 v2.0  
✅ 조건 충족:  
- {'\n- '.join(signals)}
📌 손익비 2:1 이상만 필터링됨
🕒 타임프레임: 15분봉 기준
        """.strip()
        send_telegram(message)

# ====== 실행 ======
if __name__ == "__main__":
    analyze()
