import requests

def check_signal():
    url = "https://api.bitget.com/api/mix/v1/market/contracts"
    print("🔍 사용 가능한 심볼 목록 조회 중...")
    try:
        response = requests.get(url, timeout=5)
        print(f"📥 응답 코드: {response.status_code}")
        print("📦 응답 JSON 내용:")
        print(response.text)
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
