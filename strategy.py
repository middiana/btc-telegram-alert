import pandas as pd
from utils import get_ohlcv
from config import SYMBOL, INTERVAL

def calculate_indicators(df):
    df['close'] = df['close'].astype(float)
    df['RSI'] = df['close'].diff().apply(lambda x: max(x, 0)).rolling(14).mean() / \
                df['close'].diff().abs().rolling(14).mean() * 100
    df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['close'].ewm(span=50, adjust=False).mean()
    df['upper_band'] = df['close'].rolling(window=20).mean() + 2 * df['close'].rolling(window=20).std()
    df['lower_band'] = df['close'].rolling(window=20).mean() - 2 * df['close'].rolling(window=20).std()
    return df

def check_long_signal():
    print("🚀 check_long_signal 실행 시도 중...")
    raw_data = get_ohlcv(SYMBOL, INTERVAL, limit=100)
    if raw_data is None:
        return None

    df = pd.DataFrame(raw_data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume'
    ])
    df = calculate_indicators(df)

    latest = df.iloc[-1]
    conditions = []

    if latest['RSI'] < 40:
        conditions.append("🔹 RSI < 40")
    if latest['close'] <= latest['lower_band'] * 1.01:
        conditions.append("🔹 볼린저밴드 하단 접근")
    if latest['close'] >= latest['EMA20']:
        conditions.append("🔹 EMA20 지지")
    if latest['close'] >= latest['EMA50']:
        conditions.append("🔹 EMA50 지지")

    if len(conditions) >= 2:
        entry = float(latest['close'])
        sl = round(entry * 0.95, 2)
        tp = round(entry * 1.10, 2)

        if len(conditions) >= 4:
            leverage = "5x (강력 신호)"
        elif len(conditions) == 3:
            leverage = "3x (중간 신호)"
        else:
            leverage = "2x (약한 신호)"

        message = f"""
📢 [영빈 선물전략 v1.2] 롱 진입 신호 발생
✅ 조건 만족: {len(conditions)}개
{chr(10).join(conditions)}

💰 진입가: {entry}
🔻 손절가: {sl}
🔺 익절가: {tp}
⚙ 추천 레버리지: {leverage}
"""
        return message.strip()
    else:
        return None
