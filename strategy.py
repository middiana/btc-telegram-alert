import requests

def check_signal():
    print("🔍 사용 가능한 심볼 목록 조회 중...")

    url = "https://api.bitget.com/api/mix/v1/market/contracts"
    params = {
        "productType": "umcbl"  # ✅ USDT 선물 (기타: cmcbl은 코인 마진)
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        print(f"📥 응답 코드: {response.status_code}")
        print("📦 응답 JSON 내용:")
        print(response.text)
    except Exception as e:
        print(f"❌ 예외 발생: {e}")
