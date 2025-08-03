
import requests
import logging

def get_ohlcv(symbol, interval, limit=100):
    url = 'https://api.bitget.com/api/mix/v1/market/candles'
    params = {
        'symbol': symbol,
        'granularity': interval,
        'limit': limit
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()['data']
        else:
            logging.error(f"❌ 데이터 요청 실패: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logging.error(f"❌ OHLCV 데이터 요청 중 오류 발생: {e}")
        return None

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
        logging.error(f"❌ 텔레그램 요청 오류: {e}")
