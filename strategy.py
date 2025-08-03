import time
import requests
import pandas as pd

def get_ohlcv(symbol="BTCUSDT_UMCBL", interval="15m", limit=100):
    interval_map = {
        "1m": "60",
        "5m": "300",
        "15m": "900",
        "30m": "1800",
        "1h": "3600",
        "4h": "14400",
        "1d": "86400",
    }

    granularity = interval_map.get(interval)
    if granularity is None:
        raise ValueError(f"Unsupported interval: {interval}")

    end_time = int(time.time() * 1000)
    start_time = end_time - (int(granularity) * limit * 1000)

    url = "https://api.bitget.com/api/mix/v1/market/candles"
    params = {
        "symbol": symbol,
        "granularity": granularity,
        "startTime": str(start_time),
        "endTime": str(end_time)
    }

    for _ in range(3):
        response = requests.get(url, params=params)
        if response.status_code == 200:
            raw = response.json()
            if isinstance(raw, dict):
                data = raw.get("data")
            elif isinstance(raw, list):
                data = raw
            else:
                data = None

            if data:
                df = pd.DataFrame(data, columns=[
                    "timestamp", "open", "high", "low", "close", "volume", "turnover"
                ])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                df = df.sort_values("timestamp").reset_index(drop=True)
                for col in ["open", "high", "low", "close", "volume", "turnover"]:
                    df[col] = df[col].astype(float)
                return df
        else:
            print(f"❌ OHLCV 응답 실패: {response.text}")
    return pd.DataFrame()
