import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
import numpy as np

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        if not response.ok:
            print("❌ 텔레그램 전송 실패")
    except Exception as e:
        print(f"❌ 텔레그램 예외 발생: {e}")

def get_support_resistance_levels(df):
    recent = df.tail(20)
    support = np.percentile(recent["low"], 10)
    resistance = np.percentile(recent["high"], 90)
    return f"지지선: {support:.2f} / 저항선: {resistance:.2f}"

def get_channel_levels(df):
    recent = df.tail(20)
    high = recent["high"].max()
    low = recent["low"].min()
    return f"상단: {high:.2f} / 하단: {low:.2f}"

def get_nasdaq_info():
    try:
        # 모의 데이터 사용
        price = 17982.32
        rsi = 52.3
        support = 17800
        resistance = 18100
        trend = "약한 상승 추세"

        return f"가격: {price} / RSI: {rsi} / 추세: {trend} / 지지: {support} / 저항: {resistance}"
    except:
        return "나스닥 정보 불러오기 실패"

def get_latest_news():
    try:
        # 모의 뉴스 데이터
        news_items = [
            "SEC, 비트코인 ETF 관련 언급 없음",
            "미국 7월 고용지표 발표 예정 (이번 주 금요일)",
            "코인베이스, 알트코인 상장 관련 루머 해명"
        ]
        return "\n".join([f"- {item}" for item in news_items])
    except:
        return "뉴스 데이터 불러오기 실패"
