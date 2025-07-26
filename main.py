import os
import requests
import time
import pandas as pd
import ccxt
import matplotlib.pyplot as plt
import io
import telebot
from datetime import datetime
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

# ====== [설정] ======
BOT_TOKEN = '8454656493:AAGGjH4ztzMn-HbIeMtCfrgsXLwModMDbC8'  # 사용자 봇 토큰
CHAT_ID = '742635537'  # 사용자 챗 ID
SYMBOL = 'BTC/USDT'
INTERVALS = ['5m', '15m', '30m', '1h', '4h']
THRESHOLD_VOLATILITY = 2.0  # 5분봉 기준 급등락 알림 임계값 (%)

# ✅ 선물 차트 기준 설정
EXCHANGE = ccxt.binance({
    'options': {
        'defaultType': 'future'
    }
})

bot = telebot.TeleBot(BOT_TOKEN)

# ====== [캔들 데이터 가져오기] ======
def fetch_ohlcv(symbol, timeframe, limit=100):
    data = EXCHANGE.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp','open','high','low','close','volume'])
    df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# ====== [전략 조건 계산] ======
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
    return is_long, is_short

# ====== [차트 시각화 생성] ======
def generate_chart(df, timeframe):
    plt.figure(figsize=(10, 5))
    plt.plot(df['time'], df['close'], label='Close Price')
    plt.title(f'{SYMBOL} - {timeframe} (Futures)')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

# ====== [텔레그램 전송 함수] ======
def send_alert(message, chart_buf=None):
    if chart_buf:
        bot.send_photo(chat_id=CHAT_ID, photo=chart_buf, caption=message)
    else:
        bot.send_message(chat_id=CHAT_ID, text=message)

# ====== [메인 루프: 5분 간격 실행] ======
while True:
    print(f"✅ 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for tf in INTERVALS:
        try:
            df = fetch_ohlcv(SYMBOL, tf)
            is_long, is_short = apply_strategy(df)

            # 전략 조건 충족 시 알림
            if is_long or is_short:
                signal = "📈 롱 신호 감지!" if is_long else "📉 숏 신호 감지!"
                price = df.iloc[-1]['close']
                msg = f"{signal}\n⏰ 타임프레임: {tf}\n💰 현재가: {price:.2f} USDT (선물)"
                chart = generate_chart(df, tf)
                send_alert(msg, chart)

            # 5분봉 급등락 감지
            if tf == '5m':
                prev_close = df.iloc[-2]['close']
                curr_close = df.iloc[-1]['close']
                change_pct = (curr_close - prev_close) / prev_close * 100

                if abs(change_pct) >= THRESHOLD_VOLATILITY:
                    sign = "🚀 급등" if change_pct > 0 else "⚠️ 급락"
                    msg = f"{sign} 감지!\n📉 변동률: {change_pct:.2f}%\n💰 가격: {curr_close:.2f} USDT (선물)"
                    chart = generate_chart(df, tf)
                    send_alert(msg, chart)

        except Exception as e:
            print(f"[❌ ERROR] {tf} 오류 발생: {e}")

        time.sleep(1)  # 너무 빠르게 다음 타임프레임으로 넘어가지 않게 조절

    print("⏳ 5분 대기 중...\n")
    time.sleep(300)  # 5분간 대기
