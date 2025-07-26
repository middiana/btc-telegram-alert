import os
import time
import pandas as pd
import ccxt
import telebot
from datetime import datetime
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

# 🔧 사용자 설정
BOT_TOKEN = '8454656493:AAGGjH4ztzMn-HbIeMtCfrgsXLwModMDbC8'
CHAT_ID = '742635537'
SYMBOL = 'BTC/USDT'
INTERVALS = ['5m', '15m', '30m', '1h', '4h', '1d']
EXCHANGE = ccxt.binance({ 'options': { 'defaultType': 'future' } })
bot = telebot.TeleBot(BOT_TOKEN)

# ✅ 캔들 데이터 가져오기
def fetch_ohlcv(symbol, timeframe, limit=100):
    data = EXCHANGE.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp','open','high','low','close','volume'])
    df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# ✅ 전략 조건 계산
def apply_strategy(df):
    close = df['close']
    ema = EMAIndicator(close, window=20).ema_indicator()
    rsi = RSIIndicator(close, window=14).rsi()
    bb = BollingerBands(close, window=20, window_dev=2)
    upper = bb.bollinger_hband()
    lower = bb.bollinger_lband()
    last = df.iloc[-1]
    is_long = (rsi.iloc[-1] < 30) and (last['close'] <= lower.iloc[-1]) and (last['close'] > ema.iloc[-1])
    is_short = (rsi.iloc[-1] > 70) and (last['close'] >= upper.iloc[-1]) and (last['close'] < ema.iloc[-1])
    return is_long, is_short, rsi.iloc[-1], lower.iloc[-1], ema.iloc[-1]

# ✅ 지지/저항 계산
def calculate_support_resistance(df):
    support = df['low'].rolling(window=20).min().iloc[-1]
    resistance = df['high'].rolling(window=20).max().iloc[-1]
    return round(support, 2), round(resistance, 2)

# ✅ 멀티 타임프레임 지지/저항
def build_sr_table():
    levels = {}
    for tf in INTERVALS:
        df = fetch_ohlcv(SYMBOL, tf)
        s, r = calculate_support_resistance(df)
        levels[tf] = (s, r)
    return levels

# ✅ 텔레그램 메시지 전송
def send_alert(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

# ✅ 메인 루프
def main_loop():
    while True:
        df_15m = fetch_ohlcv(SYMBOL, '15m')
        is_long, is_short, rsi, bb_l, ema = apply_strategy(df_15m)

        if not (is_long or is_short):
            time.sleep(300)
            continue

        direction = "롱 📈" if is_long else "숏 📉"
        price = df_15m.iloc[-1]['close']
        sl = price - (price * 0.03)
        tp = price + (price - sl) * 2 if is_long else price - (sl - price) * 2
        reward_pct = abs((tp - price) / price * 100)
        risk_pct = abs((price - sl) / price * 100)
        rr_ratio = reward_pct / risk_pct

        sr_levels = build_sr_table()
        sr_text = "\n".join([f"• {tf}: 지지 {s} / 저항 {r}" for tf, (s, r) in sr_levels.items()])

        msg = f"""
📢 [BTCUSDT] {direction} 신호 발생 (선물 기준)

✅ RSI: {rsi:.1f} / ✅ 볼밴 하단: {bb_l:.2f} / ✅ EMA20 지지: {ema:.2f}

🎯 목표가: {tp:.2f} USDT
🛑 손절가: {sl:.2f} USDT
⚖️ 손익비: {rr_ratio:.2f}:1 (익절 +{reward_pct:.1f}%, 손절 -{risk_pct:.1f}%)

📍 지지·저항 (멀티 타임프레임)
{sr_text}

🕒 기준봉: 15분봉
        """.strip()

        send_alert(msg)
        time.sleep(300)  # 5분 대기

# ✅ 실행
if __name__ == "__main__":
    main_loop()
