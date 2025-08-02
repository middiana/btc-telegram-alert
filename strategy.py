import requests

def check_symbols():
    url = "https://api.bitget.com/api/mix/v1/market/contracts"
    try:
        print("🔍 사용 가능한 심볼 목록 조회 중...")
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print(f"❌ 응답 코드: {response.status_code} - 응답 실패")
            return
        
        data = response.json()
        if "data" not in data or not data["data"]:
            print("❌ 'data'가 없거나 비어 있습니다. 전체 응답 내용:", data)
            return

        for item in data["data"]:
            symbol = item.get("symbol", "Unknown")
            alias = item.get("alias", "")
            product_type = item.get("productType", "")
            if "USDT" in symbol:
                print(f"✅ 심볼: {symbol} | 유형: {product_type} | 별칭: {alias}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
