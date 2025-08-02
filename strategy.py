import requests

def check_symbols():
    url = "https://api.bitget.com/api/mix/v1/market/contracts"
    try:
        print("🔍 사용 가능한 심볼 목록 조회 중...")
        response = requests.get(url, timeout=5)
        data = response.json()
        
        for item in data.get("data", []):
            symbol = item.get("symbol", "Unknown")
            print(f"✅ 심볼: {symbol}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

# 실제 실행
check_symbols()
