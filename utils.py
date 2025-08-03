import requests
import time

def get_ohlcv(symbol, interval, limit=100):
    url = f'https://api.bitget.com/api/v2/market/candles'
    params = {
        'symbol': symbol,
        'granularity': interval,
        'limit': str(limit)
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()['data']
            return list(reversed(data))  # 가장 오래된 -> 최신순 정렬
        else:
            print(f'❌ 데이터 요청 실패: {response.status_code} - {response.text}')
            return None
    except Exception as e:
        print(f'❌ 예외 발생: {e}')
        return None

def send_telegram_message(token, chat_id, message):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message}
    try:
        res = requests.post(url, data=payload)
        if res.status_code != 200:
            print(f'❌ 텔레그램 전송 실패: {res.text}')
    except Exception as e:
        print(f'❌ 텔레그램 전송 예외: {e}')
