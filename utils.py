import requests
import pandas as pd
import time
import logging

def get_ohlcv(symbol, interval, limit=100):
    end_time = int(time.time() * 1000)
    start_time = end_time - interval * 1000 * limit
    url = "https://api.bitget.com/api/mix/v1/market/candles"
    params = {
        "symbol": symbol,
        "granularity": interval,
        "startTime": start_time,
        "endTime": end_time
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            raw_data = response.json()["data"]
            df = pd.DataFrame(raw_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df = df.sort_values(by="timestamp")
            df["close"] = df["close"].astype(float)
            df["low"] = df["low"].astype(float)
            df["high"] = df["high"].astype(float)
            return df.reset_index(drop=True)
        else:
            logging.error(f"❌ 데이터 요청 실패: {response.status_code} - {response.text}")
            return pd.DataFrame()
    except Exception as e:
        logging.error(f"❌ OHLCV 요청 중 예외 발생: {e}")
        return pd.DataFrame()

def send_telegram_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            logging.error(f"❌ 텔레그램 전송 실패: {response.text}")
    except Exception as e:
        logging.error(f"❌ 텔레그램 예외 발생: {e}")
