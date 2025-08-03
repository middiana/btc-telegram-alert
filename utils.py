import requests
import time

def get_ohlcv(symbol, interval):
    url = f"https://api.bitget.com/api/v2/mix/market/candles"
    params = {
        "symbol": symbol,
        "productType": "umcbl",  # USDT-M futures
        "granularity": interval_to_granularity(interval),
        "limit": "100"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"❌ 데이터 요청 실패: {response.status_code} - {response.text}")
        return None

def interval_to_granularity(interval):
    mapping = {
        "1m": "60", "5m": "300", "15m": "900", "30m": "1800",
        "1h": "3600", "4h": "14400", "1d": "86400"
    }
    return mapping.get(interval, "900")

def get_support_resistance_levels(data):
    closes = [float(candle[4]) for candle in data]
    return min(closes), max(closes)

def get_channel_levels(data):
    lows = [float(candle[3]) for candle in data]
    highs = [float(candle[2]) for candle in data]
    return min(lows), max(highs)

def get_nasdaq_info():
    return {"support": 17800, "resistance": 18300, "rsi": 52}

def get_latest_news():
    return [
        "미국 고용지표 발표 대기 중",
        "ETF 유입 지속",
        "중동 리스크 완화"
    ]
