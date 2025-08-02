import requests
import pandas as pd
import numpy as np
import time

# ✅ RSI 계산
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ✅ EMA 계산
def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

# ✅ 볼린저밴드 하단 계산
def calculate_bollinger_bands(series, window=20, num_std=2):
    rolling_mean = series.rolling(window).mean()
    rolling_std = series.rolling(window).std()
    lower_band = rolling_mean - (rolling_std * num_std)
    upper_band = rolling_mean + (rolling_std * num_std)
    return lower_band, upper_band

# ✅ Bitget API로 15분봉 데이터 가져오기 (선물 기준)
def fetch_latest_15m():
    url = "https://api.bitget.com/api/mix/v1/market/candles"
    params = {
        "symbol": "BTCUSDT",         # 선물 기준 심볼
        "granularity": "900"         # 15분봉
    }

    for i in range(3):
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

# ✅ 전략 조건 체크 (main.py에서 이 함수 불러감)
def check_signal():
    print("🔍 check_signal() 함수 실행 시작됨", flush=True)
    df = fetch_latest_15m()
    print("📊 데이터 개수:", len(df), flush=True)

    if df.empty:
        print("⚠️ 데이터가 비어 있습니다. 다음 시도까지 대기합니다.", flush=True)
        return

    latest = df.iloc[-1]
    conditions = []

    # ✅ 전략 조건 2개 이상 만족 시 진입 신호 출력
    if latest["rsi"] < 40:
        conditions.append("RSI<40")
    if latest["close"] <= latest["bb_lower"] * 1.01:
        conditions.append("볼밴 하단 접근")
    if latest["close"] > latest["ema20"]:
        conditions.append("EMA20 지지")
    if latest["close"] > latest["ema50"]:
        conditions.append("EMA50 지지")

    if len(conditions) >= 2:
        print("🚨 진입 조건 만족:", ", ".join(conditions), flush=True)
    else:
        print("🔕 진입 조건 미충족:", ", ".join(conditions), flush=True)

    print("check_signal 실행 완료", flush=True)
