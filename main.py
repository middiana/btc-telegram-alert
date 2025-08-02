import time
from strategy import check_signal

print("🔥 main.py 시작됨")

if __name__ == "__main__":
    print("▶️ 영빈 선물전략 v1.1 실시간 실행 시작 (5분 간격)")
    while True:
        try:
            print("⏱ check_signal 호출 직전")
            check_signal()
            print("✅ check_signal 실행 완료")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        time.sleep(300)  # 5분 대기
