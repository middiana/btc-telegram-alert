# Interval 문자열을 초(seconds) 단위 숫자로 바꿔주는 표
INTERVAL_SECONDS = {
    '5m': 300,
    '15m': 900,
    '30m': 1800,
    '1h': 3600,
    '4h': 14400,
    '1d': 86400
}
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import time
import os

# --------- 설정 ---------
SYMBOL = 'btcusdt'
INTERVALS = ['5m', '15m', '30m', '1h', '4h', '1d']
LIMIT = 1000  # 최대 1000개 캔들
RSI_PERIOD = 14
BOLLINGER_PERIOD = 20
STOP_LOSS_PCT = -0.05
TAKE_PROFIT_PCT = 0.10
RSI_THRESHOLD = 35
# ------------------------

def def fetch_klines(symbol, interval):
    seconds = INTERVAL_SECONDS[interval]
    url = f"https://api.bitget.com/api/v2/market/candles?symbol={symbol}&granularity={seconds}&limit={LIMIT}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"[에러] 응답 실패 ({response.status_code}): {url}")
        return []

    try:
        data = response.json()
    except ValueError as e:
        print(f"[에러] JSON 파싱 실패: {e}")
        print(f"응답 내용: {response.text}")
        return []

    if not data or 'data' not in data:
        print(f"[에러] 비어 있는 데이터 또는 'data' 없음: {data}")
        return []

    return data['data']

def compute_rsi(prices, period=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def compute_bollinger_bands(prices, period=20):
    ma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = ma + (2 * std)
    lower = ma - (2 * std)
    return upper, lower

def backtest(df):
    df['RSI'] = compute_rsi(df['close'], RSI_PERIOD)
    upper, lower = compute_bollinger_bands(df['close'], BOLLINGER_PERIOD)
    df['bb_lower'] = lower

    trades = []
    position = None

    for i in range(len(df)):
        row = df.iloc[i]
        price = row['close']
        rsi = row['RSI']
        bb_lower = row['bb_lower']
        time = df.index[i]

        if position is None:
            if rsi < RSI_THRESHOLD and price <= bb_lower:
                entry_price = price
                stop_loss = entry_price * (1 + STOP_LOSS_PCT)
                take_profit = entry_price * (1 + TAKE_PROFIT_PCT)
                position = {
                    'entry_time': time,
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit
                }
        else:
            if price <= position['stop_loss']:
                trades.append({
                    'entry_time': position['entry_time'],
                    'exit_time': time,
                    'entry_price': position['entry_price'],
                    'exit_price': price,
                    'pnl_pct': STOP_LOSS_PCT
                })
                position = None
            elif price >= position['take_profit']:
                pnl = (price - position['entry_price']) / position['entry_price']
                trades.append({
                    'entry_time': position['entry_time'],
                    'exit_time': time,
                    'entry_price': position['entry_price'],
                    'exit_price': price,
                    'pnl_pct': pnl
                })
                position = None

    return pd.DataFrame(trades)

# --------- 실행 ---------
all_trades = []
for interval in INTERVALS:
    print(f"📊 {interval} 봉 백테스트 중...")
    try:
        df = fetch_klines(SYMBOL, interval)
        trades = backtest(df)
        trades['interval'] = interval
        all_trades.append(trades)
        time.sleep(1.2)
    except Exception as e:
        print(f"[오류] {interval} 백테스트 실패: {e}")

results = pd.concat(all_trades, ignore_index=True)
results['return_multiple'] = results['pnl_pct'] + 1
results['cumulative_return'] = results['return_multiple'].cumprod()

# --------- 저장 및 출력 ---------
results.to_csv('bitget_backtest_results.csv', index=False)
print("✅ 결과 저장됨: bitget_backtest_results.csv")

# --------- 그래프 ---------
plt.figure(figsize=(12,6))
plt.plot(results['exit_time'], results['cumulative_return'], label='누적 수익률')
plt.title("Bitget 전략 백테스트 누적 수익률")
plt.xlabel("날짜")
plt.ylabel("수익률 (배)")
plt.grid()
plt.legend()
plt.tight_layout()
plt.show()
