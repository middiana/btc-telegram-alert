# utils.py

import requests
import pandas as pd

def get_ohlcv(symbol: str, interval: str):
    url = "https://api.bitget.com/api/v2/market/candles"
    params = {
        "symbol": symbol,
        "granularity": interval,
        "limit": "200"
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"❌ 데이터 요청 실패: {response.status_code} - {response.text}")
            return None
        data = response.json().get("data", [])
        if not data:
            print("❗ 빈 데이터 수신됨")
            return None
        df = pd.DataFrame(data)
        df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.astype({
            'open': 'float',
            'high': 'float',
            'low': 'float',
            'close': 'float',
            'volume': 'float'
        })
        df = df.sort_values('timestamp').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"❌ get_ohlcv 예외 발생: {e}")
        return None
