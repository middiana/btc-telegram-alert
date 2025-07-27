# strategy.py
import requests
import pandas as pd
import ta
from support_resistance import get_support_resistance

def get_binance_ohlcv(symbol="BTCUSDT", interval="15m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    ohlcv = response.json()
    df = pd.DataFrame(ohlcv, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    df["low"] = df["low"].astype(float)
    df["high"] = df["high"].astype(float)
    df["open"] = df["open"].astype(float)
    return df

def check_entry_signal():
    df = get_binance_ohlcv()
    current_price = df["close"].iloc[-1]

    # RSI 조건
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
    rsi_condition = df["rsi"].iloc[-1] < 40

    # 볼린저 밴드 조건
    bb = ta.volatility.BollingerBands(df["close"], window=20, window_dev=2)
    df["bb_low"] = bb.bollinger_lband()
    bb_condition = current_price <= df["bb_low"].iloc[-1] * 1.01  # 하단에서 1% 이내

    # EMA 지지 조건
    df["ema20"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()
    df["ema50"] = ta.trend.EMAIndicator(df["close"], window=50).ema_indicator()
    ema_condition = current_price >= min(df["ema20"].iloc[-1], df["ema50"].iloc[-1])

    # 지지선 접근 조건
    sr = get_support_resistance()
    near_support_count = 0
    for tf, values in sr.items():
        support = values["support"]
        if current_price <= support * 1.02:
            near_support_count += 1
    support_condition = near_support_count >= 3

    # 조건 만족 수 체크
    satisfied = sum([rsi_condition, bb_condition, ema_condition, support_condition])

    if satisfied >= 2:
        stop_loss = round(current_price * 0.95, 2)
        take_profit = round(current_price * 1.10, 2)
        message = (
            f"📢 *영빈 선물전략 v1.0 롱 진입 조건 충족!*\n\n"
            f"*진입가:* {current_price:.2f} USDT\n"
            f"*손절가:* {stop_loss:.2f} USDT (-5%)\n"
            f"*익절가:* {take_profit:.2f} USDT (+10%)\n\n"
            f"✅ 조건 만족:\n"
            f"{'• RSI < 40\n' if rsi_condition else ''}"
            f"{'• 볼밴 하단 접근\n' if bb_condition else ''}"
            f"{'• EMA 지지\n' if ema_condition else ''}"
            f"{'• 지지선 접근 (3개 이상)\n' if support_condition else ''}"
        )
        return message
    return None
