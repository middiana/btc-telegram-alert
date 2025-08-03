from strategy import check_signal
import time

if __name__ == "__main__":
    print("🚀 영빈 선물전략 v1.2 실행 시작")

    signal = check_signal()
    if signal:
        print("✅ 진입 조건 만족. 텔레그램 알림 전송됨.")
    else:
        print("❌ 진입 조건 미충족.")
