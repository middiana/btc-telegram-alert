# -*- coding: utf-8 -*-

"""
영빈 선물전략 v1.4 – 설정값 모음
"""

# 기본 심볼/인터벌 (Render Start Command에서 덮어씀 가능)
SYMBOL_DEFAULT = "BTCUSDT_UMCBL"   # Bitget Perp 정식 심볼
INTERVAL_MIN_DEFAULT = 15          # 분 단위 (5, 15, 30, 60, 240, 1440 등)

# Bitget Mix 캔들 엔드포인트 (공식 문서 기준)
BITGET_MIX_CANDLES_URL = "https://api.bitget.com/api/mix/v1/market/candles"

# 분 → 초 granularity 매핑 (Bitget은 초 단위)
GRANULARITY_MAP = {
    1: 60,
    3: 180,
    5: 300,
    15: 900,
    30: 1800,
    60: 3600,
    240: 14400,
    1440: 86400,
}

# v1.4 전략 기본 파라미터
RSI_PERIOD = 14
BB_PERIOD = 20
BB_STD = 2.0
EMA_FAST = 20
EMA_SLOW = 50
CCI_PERIOD = 20

# 조건 임계
RSI_LONG_TH = 40                 # RSI < 40
BB_TOUCH_TOL = 0.01              # 볼밴 하단 1% 이내 접근
EMA_TOUCH_TOL = 0.005            # EMA20 근접(저가가 EMA20의 0.5% 이내)
CCI_OVERSOLD = -100              # CCI < -100
FIB_TOL = 0.005                  # 피보 되돌림 구간 0.5% 이내

# 손절/익절 (가변 손절 + 손익비 ≥ 1.7:1)
RISK_MIN = 0.03                  # 최소 3%
RISK_MAX = 0.06                  # 최대 6%
RR_MIN = 1.7                     # 최소 손익비 1.7:1

# 백테스트 안전장치
MAX_FETCH_LOOPS = 30             # 오래된 캔들까지 최대 루프 횟수
