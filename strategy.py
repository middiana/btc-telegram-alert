import requests

def check_symbols():
    url = "https://api.bitget.com/api/mix/v1/market/contracts"
    try:
        print("🔍 사용 가능한 심볼 목록 조회 중...")
        response = requests.get(url, timeout=5)
        data = response.json()

        if "data" not in data:
            print("❌ 'data' 키가 없습니다. 응답 내용:", data)
            return

        for item in data["data"]:
            symbol = item.get("symbol", "Unknown")
            alias = item.get("alias", "")
            product_type = item.get("productType", "")
            if "USDT" in symbol:  # 선물 시장에서 USDT 페어만 필터링
                print(f"✅ 심볼: {symbol} | 유형: {product_type} | 별칭: {alias}")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
