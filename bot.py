import os
import time
import requests
import ta
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime
from telegram import Bot
from flask import Flask

app = Flask(__name__)

# === ✅ 사용자 정보 반영 완료 ===
TELEGRAM_TOKEN = '6365054760:AAHdMOWOmXxTgGN4zC0ufGOdc0d4dyAVkqI'
TELEGRAM_CHAT_ID = '@middiana'  # 숫자 ID로 바꿔도 됨
SYMBOL = 'BTCUSDT'
INTERVALS = ['5m', '15m', '1h', '4h']
LIMIT = 100
RSI_LOW = 30
RSI_HIGH = 70
EMA_PERIOD = 100
PRICE_ALERT_CHANGE = 0.02  # 2% 이상
ALERT_COOLDOWN = 900  # 15분 중복 방지

bot = Bot(token=TELEGRAM_TOKEN)
last_alert_time = 0
last_price = None

def fetch_klines(symbol, interval):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={LIMIT}'
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
    ])
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('time', inplace=True)
    return df

def calculate_indicators(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    df['ema'] = ta.trend.EMAIndicator(df['close'], window=EMA_PERIOD).ema_indicator()
    return df

def get_support_resistance(df):
    supports = df['low'].rolling(window=5).min().dropna().tail(3).tolist()
    resistances = df['high'].rolling(window=5).max().dropna().tail(3).tolist()
    return supports, resistances

def aggregate_support_resistance():
    support_levels = []
    resistance_levels = []
    for interval in INTERVALS:
        df = fetch_klines(SYMBOL, interval)
        s, r = get_support_resistance(df)
        support_levels.extend(s)
        resistance_levels.extend(r)
    support_levels = sorted(set(round(s, 1) for s in support_levels))
    resistance_levels = sorted(set(round(r, 1) for r in resistance_levels))
    return support_levels, resistance_levels

def generate_chart(df, support_levels, resistance_levels, filename='chart.png'):
    apds = []
    for s in support_levels:
        apds.append(mpf.make_addplot([s]*len(df), color='green', linestyle='dotted'))
    for r in resistance_levels:
        apds.append(mpf.make_addplot([r]*len(df), color='red', linestyle='dotted'))

    mpf.plot(df[-50:], type='candle', style='charles', addplot=apds,
             title='BTCUSDT with Support & Resistance',
             ylabel='Price (USDT)', volume=True,
             savefig=filename)

def check_conditions():
    global last_alert_time, last_price
    now = time.time()
    df = fetch_klines(SYMBOL, '5m')
    df = calculate_indicators(df)
    price = df['close'].iloc[-1]
    ema = df['ema'].iloc[-1]
    rsi = df['rsi'].iloc[-1]

    supports, resistances = aggregate_support_resistance()
    near_support = [s for s in supports if abs(price - s) / price < 0.005]
    near_resistance = [r for r in resistances if abs(price - r) / price < 0.005]

    msg = None
    if now - last_alert_time > ALERT_COOLDOWN:
        if rsi < RSI_LOW and price > ema:
            msg = f"📈 *RSI 진입 신호 (롱)*\n가격: {price:.2f} USDT\nRSI: {rsi:.2f}"
        elif rsi > RSI_HIGH and price < ema:
            msg = f"📉 *RSI 과열 신호 (숏)*\n가격: {price:.2f} USDT\nRSI: {rsi:.2f}"

        if last_price:
            change = abs(price - last_price) / last_price
            if change > PRICE_ALERT_CHANGE:
                msg = f"⚠️ *급변동 감지*\n가격: {price:.2f}\n변동률: {change*100:.2f:.2f}%"

        if msg:
            last_alert_time = now
            last_price = price
            msg += f"\n📊 근접 지지선: {near_support}\n📊 근접 저항선: {near_resistance}"
            # 차트 저장 및 전송
            generate_chart(df, near_support, near_resistance)
            bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=open("chart.png", 'rb'), caption=msg, parse_mode='Markdown')

@app.route('/')
def home():
    return "✅ BTC 전략 시스템 v2.0 + 차트 시각화 실행 중"

def main_loop():
    while True:
        try:
            check_conditions()
        except Exception as e:
            print(f"[에러] {e}")
        time.sleep(60)

if __name__ == '__main__':
    import threading
    threading.Thread(target=main_loop).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
