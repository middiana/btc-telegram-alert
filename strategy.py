import pandas as pd
import requests
import time
from datetime import datetime
from config import SYMBOL, INTERVAL

def get_ohlcv(symbol: str, interval: str):
    url = f"https://api.bitget.com/api/v2/market/candles"
    params = {
        "symbol": symbol,
        "granularity": interval,
        "limit": "200"  # Bitget는 limit 값 문자열 필요
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"❌ 데이터 요청 실패: {response.status_code} - {response.text}")
            return None
        data = response.json().get("data", [])
        if not data:
            print("❗ 빈 데이터 수신됨")
            return None

        df = pd.DataFrame(data)
        df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.astype({
            'open': 'float',
            'high': 'float',
            'low': 'float',
            'close': 'float',
            'volume': 'float'
        })
        df = df.sort_values('timestamp').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"❌ get_ohlcv 예외 발생: {e}")
        return None

def calculate_indicators(df):
    df['EMA20'] = df['close'].ewm(span=20).mean()
    df['EMA50'] = df['close'].ewm(span=50).mean()
    df['MA100'] = df['close'].rolling(window=100).mean()
    df['stddev'] = df['close'].rolling(window=20).std()
    df['upper_bb'] = df['MA100'] + 2 * df['stddev']
    df['lower_bb'] = df['MA100'] - 2 * df['stddev']
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def check_long_signal():
    print("🚀 check_long_signal 실행 시도 중...")
    df = get_ohlcv(SYMBOL, INTERVAL)
    if df is None:
        print("📦 check_long_signal 결과: None")
        return None

    df = calculate_indicators(df)
    last = df.iloc[-1]
    conditions = []

    # 조건 검사
    if last['RSI'] < 40:
        conditions.append("RSI < 40")
    if last['close'] <= last['lower_bb'] * 1.01:
        conditions.append("볼린저밴드 하단 접근")
    if last['close'] >= last['EMA20']:
        conditions.append("EMA20 지지 확인")
    if last['close'] >= last['EMA50']:
        conditions.append("EMA50 지지 확인")

    if len(conditions) >= 2:
        entry_price = round(last['close'], 2)
        stop_loss = round(entry_price * 0.95, 2)
        take_profit = round(entry_price * 1.10, 2)

        if len(conditions) >= 4:
            leverage = "5x"
        elif len(conditions) == 3:
            leverage = "3x"
        else:
            leverage = "2x"

        print(f"""
✅ 롱 신호 포착!
- 조건 만족 수: {len(conditions)}개
- 만족 조건: {', '.join(conditions)}
- 진입가: {entry_price}
- 손절가: {stop_loss}
- 익절가: {take_profit}
- 추천 레버리지: {leverage}
        """)
    else:
        print(f"⚠ 진입 조건 부족 (현재 조건 수: {len(conditions)}개)")
