from utils import (
    get_ohlcv, calculate_rsi, calculate_bollinger_bands, calculate_ema,
    get_support_resistance, get_channel_range, get_nasdaq_trend, get_crypto_news
)
from config import SYMBOL, INTERVAL

def check_long_signal():
    df = get_ohlcv(SYMBOL, INTERVAL, limit=100)
    if df.empty:
        return None

    rsi = calculate_rsi(df)
    bb_upper, bb_lower = calculate_bollinger_bands(df)
    ema20 = calculate_ema(df, 20)
    ema50 = calculate_ema(df, 50)

    current_price = df["close"].iloc[-1]
    rsi_now = rsi.iloc[-1]
    bb_lower_now = bb_lower.iloc[-1]
    ema20_now = ema20.iloc[-1]
    ema50_now = ema50.iloc[-1]

    conditions = []
    if rsi_now < 40:
        conditions.append("RSI < 40")
    if current_price <= bb_lower_now * 1.01:
        conditions.append("볼밴 하단 접근")
    if current_price >= ema20_now:
        conditions.append("EMA20 지지")
    if current_price >= ema50_now:
        conditions.append("EMA50 지지")
    if current_price <= df["low"].rolling(window=30).min().iloc[-1] * 1.03:
        conditions.append("멀티타임 지지선 접근")

    if len(conditions) >= 2:
        stop_loss = round(current_price * 0.95, 2)
        take_profit = round(current_price * 1.10, 2)

        leverage = 2
        if len(conditions) >= 4:
            leverage = 5
        elif len(conditions) == 3:
            leverage = 3

        support, resistance = get_support_resistance(df)
        channel_low, channel_high = get_channel_range(df)
        nasdaq = get_nasdaq_trend()
        news = get_crypto_news()

        message = (
            f"📢 [영빈 선물전략 v1.2]\n"
            f"진입 조건 만족 ✅ ({', '.join(conditions)})\n\n"
            f"🎯 진입가: {round(current_price, 2)} USDT\n"
            f"🛡 손절가: {stop_loss} / 🎯 익절가: {take_profit}\n"
            f"📈 추천 레버리지: {leverage}x\n\n"
            f"🔹 지지선: {support} / 저항선: {resistance}\n"
            f"🔸 채널 구간: {channel_low} ~ {channel_high}\n"
            f"📊 나스닥 RSI: {nasdaq['rsi']} / 추세: {nasdaq['trend']}\n"
            f"📰 뉴스: {news}"
        )
        return message
    return None
