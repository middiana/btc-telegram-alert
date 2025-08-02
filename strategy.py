import requests
import pandas as pd

def fetch_latest_15m():
    url = "https://api.bitget.com/api/mix/v1/market/candles"
    params = {
        "symbol": "BTCUSDT_UMCBL",     # ✅ 정확한 선물 심볼명
        "granularity": "900",          # 15분
        "productType": "umcbl"         # USDT 선물
    }

    for i in range(3):
        try:
            print(f"🌐 Bitget API {i+1}차 요청 중...")
            response = requests.get(url, params=params, timeout=10)
            print(f"📥 응답 코드: {response.status_code}")
            if response.status_code == 200:
                data = response.json()["data"]
                df = pd.DataFrame(data, columns=[
                    "timestamp", "open", "high", "low", "close", "volume", "quoteVolume"])
                df["close"] = df["close"].astype(float)
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                df = df.sort_values("timestamp").reset_index(drop=True)
                return df
            else:
                print(f"❌ 비정상 응답: {response.text}")
        except Exception as e:
            print(f"❗ 예외 발생: {e}")
    print("❌ 최종적으로 Bitget 데이터 수신 실패. 빈 DataFrame 반환")
    return pd.DataFrame()

def check_signal():
    print("🔍 check_signal() 함수 실행 시작됨")
    df = fetch_latest_15m()
    print(f"📊 데이터 개수: {len(df)}")

    if df.empty:
        print("⚠️ 데이터가 비어 있습니다. 다음 시도까지 대기합니다.")
        return

    df["rsi"] = df["close"].rolling(window=14).apply(
        lambda x: 100 - 100 / (1 + ((x.diff().clip(lower=0).sum()) / (x.diff().clip(upper=0).abs().sum() + 1e-6)))
    )

    rsi_now = df["rsi"].iloc[-1]
    close_now = df["close"].iloc[-1]

    ema20 = df["close"].ewm(span=20).mean()
    ema_now = ema20.iloc[-1]

    print(f"📉 현재 RSI: {rsi_now:.2f}, 종가: {close_now:.2f}, EMA20: {ema_now:.2f}")

    signal_conditions = []

    if rsi_now < 40:
        signal_conditions.append("RSI < 40")
    if close_now >= ema_now:
        signal_conditions.append("EMA20 지지")

    if len(signal_conditions) >= 2:
        print(f"🚨 진입 조건 만족: {', '.join(signal_conditions)}")
    else:
        print("✅ 진입 조건 아직 미충족")
