import requests
import pandas as pd
from datetime import datetime
from indicators import calculate_rsi, calculate_ema, calculate_bollinger_bands
from notifier import send_telegram_alert
import time

def fetch_latest_15m():
    url = "https://api.bitget.com/api/mix/v1/market/candles"
    params = {
        "symbol": "BTCUSDT",         # ✅ 선물 심볼
        "granularity": "900",        # ✅ 15분봉
        "productType": "umcbl"       # ✅ usdt 무기한 선물 마켓
    }

    for i in range(3):  # 최대 3번 시도
        try:
            print(f"🌐 Bitget API {i+1}차 요청 중...", flush=True)
            response = requests.get(url, params=params)
            print("📥 응답 코드:", response.status_code, flush=True)

            if response.status_code != 200:
                print("❌ 비정상 응답:", response.text[:300], flush=True)
                time.sleep(2)
                continue

            json_data = response.json()
            data = json_data.get("data", [])

            if not data or len(data) == 0:
                print("⚠️ 데이터가 비어 있음 (응답은 성공)", flush=True)
                time.sleep(2)
                continue

            df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df = df.iloc[::-1]
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)

            df["rsi"] = calculate_rsi(df["close"], 14)
            df["ema20"] = calculate_ema(df["close"], 20)
            df["ema50"] = calculate_ema(df["close"], 50)
            df["bb_lower"], _ = calculate_bollinger_bands(df["close"])

            return df

        except Exception as e:
            print(f"❗ 요청 중 예외 발생 ({i+1}차): {e}", flush=True)
            time.sleep(2)

    print("❌ 최종적으로 Bitget 데이터 수신 실패. 빈 DataFrame 반환", flush=True)
    return pd.DataFrame()

def check_signal():
    print("🔍 check_signal() 함수 실행 시작됨", flush=True)

    df = fetch_latest_15m()
    print(f"📊 데이터 개수: {len(df)}", flush=True)

    if df.empty:
        print("⚠️ 데이터가 비어 있습니다. 다음 시도까지 대기합니다.", flush=True)
        return

    latest = df.iloc[-1]
    print(f"✅ 최신 데이터: {latest.to_dict()}", flush=True)

    checks = {
        "RSI < 40": latest["rsi"] < 40,
        "볼밴 하단 접근": latest["close"] <= latest["bb_lower"] * 1.01,
        "EMA 지지": latest["close"] >= latest["ema20"] or latest["close"] >= latest["ema50"],
        "다중 지지 접근": False,
        "추세 둔화/반전": False
    }

    satisfied = [k for k, v in checks.items() if v]
    print(f"🎯 만족 조건: {satisfied}", flush=True)

    if len(satisfied) >= 2:
        print("🚀 조건 만족 → 텔레그램 알림 전송", flush=True)
        send_telegram_alert(latest, checks, len(satisfied))
    else:
        print("⏳ 조건 미충족 → 대기", flush=True)
