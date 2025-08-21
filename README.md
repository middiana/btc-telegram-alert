# 영빈 선물전략 v1.4 백테스트 (Bitget 자동수집)

### 사용법
1. 깃허브에서 새 리포지토리 생성 → 위 3개 파일을 올린다.
2. Render 접속 → New → **Blueprint** 선택 → 해당 깃허브 리포 연결.
3. Render가 자동으로 `render.yaml`을 읽어 설정한다.
4. 배포 완료 후 Logs에서 결과 확인:
   - 총 거래수, 승률, 손익률이 출력됨.
   - `trades.csv`, `equity_curve.csv`도 생성.

### 옵션 바꾸기
- `--interval 15` : 1 / 5 / 15 / 30 / 60 / 240 / 1440 분
- `--bars 5000` : 수집 봉 개수 (3000~10000 권장)

### 주의사항
- 심볼은 반드시 `BTCUSDT_UMCBL`
- Bitget API 정식 엔드포인트(`https://api.bitget.com/api/mix/v1/market/candles`) 사용
- 레이트리밋 대비 0.15초 딜레이 포함
