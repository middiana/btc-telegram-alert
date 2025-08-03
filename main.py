print("✅ main.py 시작")

try:
    from strategy import check_long_signal
    print("✅ strategy 모듈 import 성공")
except Exception as e:
    print(f"❌ strategy import 실패: {e}")
