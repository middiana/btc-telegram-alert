# -*- coding: utf-8 -*-

from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np

from config import (
    RSI_LONG_TH, BB_TOUCH_TOL, EMA_TOUCH_TOL, CCI_OVERSOLD, FIB_TOL,
    RISK_MIN, RISK_MAX, BB_PERIOD, RR_MIN
)
from utils import recent_swing_levels, nearest_fib_proximity, is_bullish_reversal

def compute_dynamic_risk(bb_width_pct: float) -> float:
    """
    v1.4: 가변 손절(변동성 기반)
    - 볼밴 폭 비율을 사용하여 3% ~ 6% 사이에서 가변
    """
    if np.isnan(bb_width_pct) or bb_width_pct <= 0:
        return 0.05
    return float(np.clip(bb_width_pct, RISK_MIN, RISK_MAX))

def build_entry_flags(row: pd.Series, fib_levels: Dict[str, float]) -> Dict[str, bool]:
    close = row["close"]; low = row["low"]; open_ = row["open"]
    # 1) RSI
    cond_rsi = (row["rsi"] < RSI_LONG_TH) if not np.isnan(row["rsi"]) else False
    # 2) 볼밴 하단 접근(1%이내)
    if np.isnan(row["bb_low"]):
        cond_bb = False
    else:
        cond_bb = (close <= row["bb_low"] * (1 + BB_TOUCH_TOL))
    # 3) EMA20 지지 확인(저가가 ema20 근접 & 종가가 ema20 위)
    if np.isnan(row["ema20"]):
        cond_ema = False
    else:
        cond_ema = (low <= row["ema20"] * (1 + EMA_TOUCH_TOL)) and (close >= row["ema20"])
    # 4) CCI 과매도
    cond_cci = (row["cci"] < CCI_OVERSOLD) if not np.isnan(row["cci"]) else False
    # 5) 피보 되돌림 근접 (0.5% 이내)
    fib_key, fib_err = nearest_fib_proximity(close, fib_levels)
    cond_fib = (fib_err <= FIB_TOL)
    # 6) 추세둔화(간단 패턴)
    cond_candle = is_bullish_reversal(open_, row["high"], low, close)

    return {
        "RSI<40": cond_rsi,
        "BB하단접근": cond_bb,
        "EMA20지지": cond_ema,
        "CCI<-100": cond_cci,
        f"FIB근접({fib_key})": cond_fib,
        "패턴반전": cond_candle,
    }

def select_entries(df: pd.DataFrame) -> pd.DataFrame:
    """
    바마다 조건을 평가하여 '엔트리 시도'를 표기
    - 규칙: 위 조건 중 '2개 이상' 만족 시 롱 엔트리 시그널
    - 시그널 메타 정보(만족 조건 리스트, 동적 손절%)도 같이 보관
    """
    df = df.copy()
    entries = []

    # 피보 레벨은 구간마다 갱신 (과도한 미래 참조 방지: 바마다 최근 200봉 기준)
    for i in range(len(df)):
        sub = df.iloc[: i + 1]
        if len(sub) < max(BB_PERIOD, 60):  # 지표 안정화 후부터
            entries.append((False, [], np.nan))
            continue

        low, high, fib_levels = recent_swing_levels(sub, lookback=200)
        flags = build_entry_flags(df.iloc[i], fib_levels)
        satisfied = [k for k, v in flags.items() if v]

        # 조건 2개 이상이면 엔트리
        if len(satisfied) >= 2:
            risk_pct = compute_dynamic_risk(df.iloc[i]["bb_width_pct"])
            entries.append((True, satisfied, risk_pct))
        else:
            entries.append((False, satisfied, np.nan))

    df["entry"] = [e[0] for e in entries]
    df["satisfied"] = [e[1] for e in entries]
    df["risk_pct"] = [e[2] for e in entries]
    return df

def backtest_long_only(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    롱 전용 시그널 백테스트
    - 엔트리 바 다음 캔들 시가로 진입
    - 동적 손절%(risk_pct), TP = risk_pct * RR_MIN
    - 스탑/익절 먼저 도달하는 쪽으로 종료
    - 포지션 중복 방지(종료 전까지 신규 진입 무시)
    """
    df = df.copy()
    trades = []
    in_pos = False
    i = 0
    n = len(df)

    while i < n - 2:
        if not in_pos and df.iloc[i]["entry"]:
            # 진입은 다음 바 오픈으로
            entry_idx = i + 1
            entry_time = int(df.iloc[entry_idx]["time"])
            entry_price = float(df.iloc[entry_idx]["open"])

            risk_pct = df.iloc[i]["risk_pct"]
            if np.isnan(risk_pct) or risk_pct <= 0:
                risk_pct = 0.05
            tp_pct = max(RR_MIN * risk_pct, RR_MIN * 0.03)  # 최소 1.7*3%=5.1% 확보

            stop_price = entry_price * (1 - risk_pct)
            tp_price = entry_price * (1 + tp_pct)

            satisfied = df.iloc[i]["satisfied"]
            in_pos = True

            # 포지션 추적: i+1 이후부터 탐색
            j = entry_idx + 1
            exit_price = None
            exit_time = None
            outcome = None  # "TP" or "SL" or "EOD"
            while j < n:
                hi = float(df.iloc[j]["high"])
                lo = float(df.iloc[j]["low"])
                t  = int(df.iloc[j]["time"])

                if lo <= stop_price and hi >= tp_price:
                    # 동시 충족 시 보수적으로 SL 우선
                    exit_price = stop_price
                    exit_time = t
                    outcome = "SL"
                    break
                elif lo <= stop_price:
                    exit_price = stop_price
                    exit_time = t
                    outcome = "SL"
                    break
                elif hi >= tp_price:
                    exit_price = tp_price
                    exit_time = t
                    outcome = "TP"
                    break
                j += 1

            if exit_price is None:
                # 데이터 끝까지 미도달 → 마지막 종가 청산
                exit_price = float(df.iloc[-1]["close"])
                exit_time  = int(df.iloc[-1]["time"])
                outcome = "EOD"

            pnl_pct = (exit_price / entry_price - 1) * 100.0

            trades.append({
                "entry_time": entry_time,
                "entry_price": entry_price,
                "exit_time": exit_time,
                "exit_price": exit_price,
                "risk_pct": risk_pct * 100,
                "tp_pct": tp_pct * 100,
                "outcome": outcome,
                "pnl_pct": pnl_pct,
                "conditions": "; ".join(satisfied)
            })
            in_pos = False
            i = j  # 포지션 종료 시점으로 점프
        else:
            i += 1

    # 요약
    if trades:
        pnl_list = [t["pnl_pct"] for t in trades]
        wins = sum(1 for t in trades if t["outcome"] == "TP")
        losses = sum(1 for t in trades if t["outcome"] == "SL")
        eods = sum(1 for t in trades if t["outcome"] == "EOD")
        total = len(trades)
        avg = float(np.mean(pnl_list))
        cum = float(np.sum(pnl_list))
    else:
        wins = losses = eods = total = 0
        avg = cum = 0.0

    summary = {
        "trades": len(trades),
        "wins": wins,
        "losses": losses,
        "eod": eods,
        "avg_pnl_pct": avg,
        "cum_pnl_pct": cum,
    }

    trades_df = pd.DataFrame(trades)
    return trades_df, summary
