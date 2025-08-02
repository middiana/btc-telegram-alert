def fetch_latest_15m():
    url = "https://api.bitget.com/api/mix/v1/market/candles"
    params = {
        "symbol": "BTCUSDT",         # ✅ 정확한 심볼
        "granularity": "900"         # ✅ 15분봉
        # ❌ 'productType' 제거해야 작동함!
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
