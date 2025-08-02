import time
from strategy import check_signal

print("main.py 시작됨", flush=True)

if __name__ == "__main__":
    print("영빈 선물전략 v1.1 실시간 실행 시작 (5분 간격)", flush=True)
    while True:
        try:
            print("check_signal 호출 직전", flush=True)
            check_signal()
            print("check_signal 실행 완료", flush=True)
        except Exception as e:
            print(f"오류 발생: {e}", flush=True)
        time.sleep(300)
