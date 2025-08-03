from config import SYMBOL, INTERVAL
from utils import (
    get_ohlcv,
    calculate_rsi,
    calculate_bollinger_bands,
    calculate_ema
)

def check_long_signal():
    try:
        df = get_ohlcv(SYMBOL, INTERVAL)
        if df is None or df.empty:
            print("❌ 데이터 수신 실패 또는 데이터 없음")
            return None

        # 최신 데이터에 RSI, BB, EMA 추가
        df['rsi'] = calculate_rsi(df)
        df['ema20'] = calculate_ema(df, 20)
        df['ema50'] = calculate_ema(df, 50)
        df['bb_upper'], df['bb_lower'] = calculate_bollinger_bands(df)

        latest = df.iloc[-1]
        conditions = []

        # 조건 1: RSI < 40
        if latest['rsi'] < 40:
            conditions.append("RSI < 40")

        # 조건 2: 볼린저 밴드 하단 접근 (1% 이내)
        bb_range = latest['bb_upper'] - latest['bb_lower']
        if bb_range > 0 and abs(latest['close'] - latest['bb_lower']) < bb_range * 0.01:
            conditions.append("BB 하단 접근")

        # 조건 3: EMA20 지지
        if latest['close'] >= latest['ema20']:
            conditions.append("EMA20 지지")

        # 조건 4: EMA50 지지
        if latest['close'] >= latest['ema50']:
            conditions.append("EMA50 지지")

        # 진입 신호 판단
        if len(conditions) >= 2:
            entry_price = round(float(latest['close']), 2)
            stop_loss = round(entry_price * 0.95, 2)
            take_profit = round(entry_price * 1.10, 2)

            # 추천 레버리지 설정
            if len(conditions) >= 4:
                leverage = "5x (강력 신호)"
            elif len(conditions) == 3:
                leverage = "3x (중간 신호)"
            else:
                leverage = "2x (약한 신호)"

            return {
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "conditions": conditions,
                "leverage": leverage
            }
        else:
            return None

    except Exception as e:
        print(f"❌ check_long_signal 실행 실패: {e}")
        return None
