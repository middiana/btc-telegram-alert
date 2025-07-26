import ccxt
import pandas as pd
import numpy as np
import requests
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

# 너의 텔레그램 봇 정보
BOT_TOKEN = "8249903687:AAH0Caguq0cnwTKPuhMyUGIqY4Ca1_qMmFU"
CHAT_ID = "7426355357"  # @middiana

# 메시지 보내기 함수
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

# 바이낸스에서 OHLCV 데이터 가져오기
def get_ohlcv(symbol='BTC/USDT', timeframe='15m', limit=100):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
    return df

# 피보나치 되돌림 계산 함수
def calculate_fibonacci(high, low):
    diff = high - low
    levels = {
        '0.0': high,
        '0.236': high - diff * 0.236,
        '0.382': high - diff * 0.382,
        '0.5': high - diff * 0.5,
        '0.618': high - diff * 0.618,
        '0.786': high - diff * 0.786,
        '1.0': low
    }
    return levels

# 전략 분석 및 조건 판단
def analyze():
    df = get_ohlcv(timeframe='15m')
    close = df['close']

    rsi = RSIIndicator(close, window=14).rsi()
    ema20 = EMAIndicator(close, window=20).ema_indicator()
    ema50 = EMAIndicator(close, window=50).ema_indicator()

    last_price = close.iloc[-1]
    last_rsi = rsi.iloc[-1]
    last_ema20 = ema20.iloc[-1]
    last_ema50 = ema50.iloc[-1]

    high = df['high'].max()
    low = df['low'].min()
    fib = calculate_fibonacci(high, low)

    signals = []

    if last_rsi < 30:
        signals.append("📉 RSI 과매도")
    if last_price < last_ema20 and last_price < last_ema50:
        signals.append("📉 EMA 하단 이탈")
    if fib['0.618'] * 0.99 < last_price < fib['0.618'] * 1.01:
        signals.append("🌀 피보나치 0.618 되돌림")

    if len(signals) >= 3:
        message = f"""
🚨 [매수 신호] BTC/USDT (롱)
✅ 신호 등급: A
📍 현재가: {last_price:.2f} USDT
🔍 조건:
- {'\n- '.join(signals)}
🎯 전략: 영빈작전 (물타기 + 손절 없음)
        """.strip()
        send_telegram(message)

# 실행 (Render에서는 주기적 실행 또는 Worker 사용)
if __name__ == "__main__":
    analyze()
