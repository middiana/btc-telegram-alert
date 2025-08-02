import requests
import pandas as pd
import time

def get_ohlcv(symbol="BTCUSDT_UMCBL", interval="1m", limit=100):
    url = "https://api.bitget.com/api/mix/v1/market/candles"
    params = {
        "symbol": symbol,
        "granularity": interval,
        "limit": str(limit)
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if response.status_code == 200 and "data" in data:
            df = pd.DataFrame(data["data"])
            df.columns = ["timestamp", "open", "high", "low", "close", "volume"]
            df = df.iloc[::-1]  # 시간 순서 정렬
            df["close"] = df["close"].astype(float)
            return df
        else:
            print("❌ OHLCV 응답 실패:", data)
            return None
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return None

def check_signal():
    print("🔍 BTCUSDT 선물 데이터 조회 중...")
    df = get_ohlcv()

    if df is None or df.empty:
        print("⚠️ 데이터 없음")
        return

    # 전략 조건 예시: 5개 종가 평균이 마지막 종가보다 작을 경우 진입 신호
    avg = df["close"].tail(5).mean()
    last = df["close"].iloc[-1]

    print(f"📊 5개 종가 평균: {avg:.2f}, 현재가: {last:.2f}")
    if last > avg:
        print("✅ 롱 진입 신호 발생")
    else:
        print("🕓 진입 조건 불충족 (대기)")
