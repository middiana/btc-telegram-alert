
from utils import get_ohlcv
from config import SYMBOL, INTERVAL

def check_long_signal():
    print("🚀 check_long_signal 실행 시도 중...")
    ohlcv = get_ohlcv(SYMBOL, INTERVAL)
    if ohlcv is None:
        print("📦 check_long_signal 결과: None")
        return None
    print(f"📊 받은 데이터 수: {len(ohlcv)}개")
    return "신호 없음"
