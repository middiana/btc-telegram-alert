from utils import (
    calculate_rsi,
    calculate_bollinger_bands,
    calculate_ema,
    get_support_resistance_levels,
    get_channel_levels,
    get_nasdaq_info,
    get_latest_news,
    send_telegram_message,
)
import pandas as pd

def check_long_signal(df):
    try:
        df['rsi'] = calculate_rsi(df)
        df['ema20'] = calculate_ema(df, 20)
        df['ema50'] = calculate_ema(df, 50)
        df['bb_lower'], df['bb_middle'], df['bb_upper'] = calculate_bollinger_bands(df)

        latest = df.iloc[-1]
        price = latest['close']

        satisfied_conditions = []

        # 조건 체크
        if latest['rsi'] < 40:
            satisfied_conditions.append("RSI < 40")

        if abs(price - latest['bb_lower']) / price < 0.01:
            satisfied_conditions.append("볼린저밴드 하단 접근")

        if price > latest['ema20']:
            satisfied_conditions.append("EMA20 지지")

        if price > latest['ema50']:
            satisfied_conditions.append("EMA50 지지")

        if len(df) >= 2 and df.iloc[-2]['close'] > df.iloc[-2]['open'] and latest['close'] > latest['open']:
            satisfied_conditions.append("반전형 캔들 출현")

        if len(satisfied_conditions) >= 2:
            entry_price = round(float(latest['close']), 2)
            stop_loss = round(entry_price * 0.95, 2)
            take_profit = round(entry_price * 1.1, 2)

            leverage = {2: "2x", 3: "3x", 4: "5x"}.get(len(satisfied_conditions), "2x")

            support_resistance = get_support_resistance_levels(df)
            channel = get_channel_levels(df)
            nasdaq_info = get_nasdaq_info()
            news = get_latest_news()

            message = f"""
📢 진입 시그널 발생! (조건 {len(satisfied_conditions)}개 이상 만족)

📌 조건 목록:
- {', '.join(satisfied_conditions)}

💰 진입가: {entry_price}  
🛑 손절가: {stop_loss}  
🎯 익절가: {take_profit}  
⚡️ 추천 레버리지: {leverage}

📊 지지/저항:
{support_resistance}

📈 채널 구간:
{channel}

📉 나스닥 추세:
{nasdaq_info}

🌍 최신 뉴스:
{news}

🔖 전략: 영빈 선물전략 v1.2
"""
            print(message)
            send_telegram_message(message)
        else:
            print("📉 조건 미충족 - 시그널 없음.")
    except Exception as e:
        print(f"❌ check_long_signal 실행 실패: {e}")
        return None
