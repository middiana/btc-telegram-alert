import requests

def check_symbols():
    url = "https://api.bitget.com/api/mix/v1/market/contracts"
    params = {"productType": "umcbl"}

    try:
        print("🔍 사용 가능한 심볼 목록 조회 중...")
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        for item in data["data"]:
            print(f"✅ 심볼: {item['symbol']} / 거래종류: {item['productType']}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

check_symbols()
