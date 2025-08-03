print("✅ main.py 시작")

try:
    from strategy import check_long_signal
    print("✅ strategy 모듈 import 성공")
except Exception as e:
    print(f"❌ strategy import 실패: {e}")

try:
    print("🚀 check_long_signal 실행 시도 중...")
    result = check_long_signal()
    print("📦 check_long_signal 결과:", result)
except Exception as e:
    print(f"❌ check_long_signal 실행 실패: {e}")
