services:
  - type: worker
    name: yb-backtest-v14
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: python backtest_v14_bitget.py --symbol BTCUSDT_UMCBL --interval 15 --bars 5000 --save_csv btc_15m.csv
    autoDeploy: false
