# config.py

# 텔레그램 설정
TELEGRAM_TOKEN = "8454656493:AAGjqH4zt2Mn-HBleMtCrFgsXLwModMDbC8"
TELEGRAM_CHAT_ID = "7426355357"

# 전략명
STRATEGY_NAME = "영빈 선물전략 v1.2"

# 종목 심볼 (비트겟 선물 기준)
SYMBOL = "BTCUSDT_UMCBL"

# 전략 조건
RSI_THRESHOLD = 40
BOLLINGER_BAND_APPROACH = 0.01  # 1% 이내 접근
STOP_LOSS_PCT = 0.05  # -5%
TAKE_PROFIT_PCT = 0.10  # +10% (손익비 2:1)
