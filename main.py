import time
from strategy import check_signal

if __name__ == "__main__":
    print("▶️ 영빈 선물전략 v1.1 실시간 실행 시작 (5분 간격)")
    while True:
        try:
            check_signal()
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        time.sleep(300)  # 5분 대기
