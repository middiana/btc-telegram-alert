import requests
import pandas as pd
import datetime

def get_bitget_data():
    url = "https://api.bitget.com/api/mix/v1/market/candles"
    params = {
        "symbol": "BTCUSDT_UMCBL",         # 선물 심볼
        "granularity": "900",              # 15분봉 (900초)
        "productType": "umcbl"             # ✅ 꼭 있어야 함!
    }

    df = pd.DataFrame()

    for attempt in range(1, 4):
        print(f"🌐 Bitget API {attempt}차 요청 중...")
        response = requests.get(url, params=params)
        print(f"📥 응답 코드: {response.status_code}")

        if response.status_code == 200:
            data = response.json().get("data", [])
            if not data:
                print("❌ 받은 데이터가 비어 있음.")
                continue

            df = pd.DataFrame(data, columns=[
                "timestamp", "open", "high", "low", "close", "volume", "quoteVolume"
            ])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df = df.sort_values("timestamp").reset_index(drop=True)
            return df
        else:
            print(f"❌ 비정상 응답: {response.text}")

    print("❌ 최종적으로 Bitget 데이터 수신 실패. 빈 DataFrame 반환")
    return df

def check_signal():
    print("🔍 check_signal() 함수 실행 시작됨")
    df = get_bitget_data()
    print(f"📊 데이터 개수: {len(df)}")

    if df.empty:
        print("⚠️ 데이터가 비어 있습니다. 다음 시도까지 대기합니다.")
        return

    # 전략 조건 예시
    df["close"] = df["close"].astype(float)
    df["EMA20"] = df["close"].ewm(span=20).mean()
    df["EMA50"] = df["close"].ewm(span=50).mean()
    last = df.iloc[-1]

    entry_conditions = []

    if last["close"] < last["EMA20"]:
        entry_conditions.append("EMA20 아래")
    if last["close"] < last["EMA50"]:
        entry_conditions.append("EMA50 아래")

    if len(entry_conditions) >= 2:
        print(f"✅ 진입 신호 발생: {entry_conditions}")
    else:
        print(f"⏸️ 조건 미충족: {entry_conditions}")
