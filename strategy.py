import requests
import pandas as pd
from datetime import datetime
from indicators import calculate_rsi, calculate_ema, calculate_bollinger_bands
from notifier import send_telegram_alert

def fetch_latest_15m():
    url = "https://api.bitget.com/api/mix/v1/market/candles"
    params = {
        "symbol": "BTCUSDT_UMCBL",  # Bitget BTCUSDT 선물
        "granularity": "900",       # 15분 = 900초
        "limit": "100"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json().get("data", [])

        if not data or len(data) == 0:
            print("❗ Bitget에서 받은 데이터가 없습니다.")
            return pd.DataFrame()

        # Bitget 데이터는 내림차순이라 정렬 필요
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df = df.iloc[::-1]  # 시간 순 정렬 (가장 오래된 것이 위로)

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)

        df["rsi"] = calculate_rsi(df["close"], 14)
        df["ema20"] = calculate_ema(df["close"], 20)
        df["ema50"] = calculate_ema(df["close"], 50)
        df["bb_lower"], _ = calculate_bollinger_bands(df["close"])

        return df

    except Exception as e:
        print(f"❗ Bitget 데이터 요청 중 오류: {e}")
        return pd.DataFrame()

def check_signal():
    df = fetch_latest_15m()

    if df.empty:
        print("⚠️ 데이터가 비어 있습니다. 다음 시도까지 대기합니다.")
        return

    latest = df.iloc[-1]

    checks = {
        "RSI < 40": latest["rsi"] < 40,
        "볼밴 하단 접근": latest["close"] <= latest["bb_lower"] * 1.01,
        "EMA 지지": latest["close"] >= latest["ema20"] or latest["close"] >= latest["ema50"],
        "다중 지지 접근": False,  # 추후 구현
        "추세 둔화/반전": False   # 추후 구현
    }

    satisfied = [k for k, v in checks.items() if v]
    if len(satisfied) >= 2:
        send_telegram_alert(latest, checks, len(satisfied))
