# -*- coding: utf-8 -*-

import argparse
import time
import pandas as pd

from config import SYMBOL_DEFAULT, INTERVAL_MIN_DEFAULT
from utils import log, fetch_bitget_candles, add_indicators
from strategy import select_entries, backtest_long_only

BANNER = "영빈 선물전략 v1.4 - Bitget 자동수집 백테스트 실행 준비 완료"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, default=SYMBOL_DEFAULT)
    parser.add_argument("--interval", type=int, default=INTERVAL_MIN_DEFAULT, help="분 단위 (예: 5, 15, 60)")
    parser.add_argument("--bars", type=int, default=2000)
    parser.add_argument("--save_csv", type=str, default="backtest_v14.csv")
    args = parser.parse_args()

    log(BANNER)
    log(f"[STEP] 1) 캔들 수집 시작: symbol={args.symbol}, interval={args.interval}m, bars={args.bars}")
    df = fetch_bitget_candles(args.symbol, args.interval, args.bars)
    log(f"[STEP] 2) 캔들 수집 완료: {len(df):,}개")

    if df.empty:
        log("[FATAL] 캔들이 비어있어 종료합니다.")
        time.sleep(3)
        return

    log("[STEP] 3) 지표 계산")
    df = add_indicators(df)

    log("[STEP] 4) 엔트리 조건 평가(v1.4 – 2개 이상 만족 시 롱)")
    df = select_entries(df)

    log("[STEP] 5) 백테스트 실행(롱 전용)")
    trades_df, summary = backtest_long_only(df)

    # 저장: 원본 캔들+시그널 / 트레이드 내역
    log(f"[STEP] 6) CSV 저장: {args.save_csv} / trades_{args.save_csv}")
    try:
        df.to_csv(args.save_csv, index=False)
        trades_df.to_csv(f"trades_{args.save_csv}", index=False)
    except Exception as e:
        log(f"[WARN] CSV 저장 중 예외: {repr(e)}")

    # 요약 출력
    log("—"*50)
    log("📊 백테스트 요약 (v1.4)")
    log(f"총 거래수: {summary['trades']:,}회 | 승: {summary['wins']:,} | 패: {summary['losses']:,} | 미도달청산(EOD): {summary['eod']:,}")
    log(f"평균 수익률: {summary['avg_pnl_pct']:.2f}% | 누적 수익률 합계: {summary['cum_pnl_pct']:.2f}%")
    log("—"*50)

    # 엔트리 예시 상위 5개만 미리보기
    if "entry" in df.columns:
        preview = df[df["entry"]].tail(5)[["time","open","high","low","close","rsi","bb_low","ema20","cci","satisfied","risk_pct"]]
        log("[미리보기] 최근 엔트리 5개")
        with pd.option_context("display.max_colwidth", 200):
            print(preview.to_string(index=False), flush=True)

    # Render 로그 플러시용 대기
    time.sleep(3)

if __name__ == "__main__":
    main()
