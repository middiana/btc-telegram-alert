# -*- coding: utf-8 -*-

import time
import math
import json
from typing import List, Tuple, Dict
import requests
import pandas as pd
import numpy as np

from config import (
    BITGET_MIX_CANDLES_URL,
    GRANULARITY_MAP,
    MAX_FETCH_LOOPS,
    RSI_PERIOD, BB_PERIOD, BB_STD, EMA_FAST, EMA_SLOW, CCI_PERIOD
)

# ========== 공용 출력 헬퍼 ==========
def log(msg: str):
    print(msg, flush=True)

# ========== Bitget OHLCV 수집 ==========
def _to_int(x):
    try:
        return int(x)
    except:
        return int(float(x))

def fetch_bitget_candles(symbol: str, interval_min: int, bars: int) -> pd.DataFrame:
    """
    Bitget Mix /market/candles 에서 캔들 수집.
    - 최신 데이터부터 내려오는 형식 방어
    - 부족하면 endTime을 과거로 이동시키며 여러 번 요청
    - 반환: 오름차순 시계열 DataFrame (time, open, high, low, close, volume)
    """
    if interval_min not in GRANULARITY_MAP:
        raise ValueError(f"지원하지 않는 인터벌(분): {interval_min}")
    gran = GRANULARITY_MAP[interval_min]

    all_rows = []
    end_ts_ms = None
    loops = 0

    log(f"[DEBUG] 캔들 수집 시작 symbol={symbol}, interval={interval_min}m({gran}s), bars={bars}")

    while len(all_rows) < bars and loops < MAX_FETCH_LOOPS:
        params = {"symbol": symbol, "granularity": str(gran)}
        if end_ts_ms is not None:
            params["endTime"] = str(end_ts_ms)  # Bitget이 endTime을 지원함(과거 커서)

        log(f"[DEBUG] GET {BITGET_MIX_CANDLES_URL} params={params}")
        resp = requests.get(BITGET_MIX_CANDLES_URL, params=params, timeout=10)
        log(f"[DEBUG] status={resp.status_code}")
        if resp.status_code != 200:
            log(f"[ERROR] body={resp.text[:400]}")
            break

        try:
            data = resp.json()
        except Exception as e:
            log(f"[EXCEPTION] JSON 파싱 실패: {repr(e)}")
            break

        # 응답 포맷 방어
        rows = None
        if isinstance(data, dict) and "data" in data:
            rows = data["data"]
        elif isinstance(data, list):
            rows = data
        else:
            log(f"[ERROR] 예기치 않은 응답 포맷: {str(data)[:300]}")
            break

        if not rows:
            log("[INFO] 더 이상 받을 데이터가 없습니다.")
            break

        # Bitget candles: [ts, open, high, low, close, volume, ...] 최신→과거 순일 수 있음
        # 문자열 → 숫자 변환
        parsed = []
        for r in rows:
            # 일부 필드는 문자열로 올 수 있음
            ts = _to_int(r[0])
            o = float(r[1]); h = float(r[2]); l = float(r[3]); c = float(r[4])
            v = float(r[5]) if len(r) > 5 else np.nan
            parsed.append([ts, o, h, l, c, v])

        # 들어온 덩어리를 append
        all_rows.extend(parsed)

        # 다음 루프용 endTime (가장 오래된 ts보다 한 틱 더 과거)
        oldest_ts = parsed[-1][0]
        end_ts_ms = oldest_ts - gran * 1000
        loops += 1
        log(f"[DEBUG] 누적 캔들: {len(all_rows)}개, 다음 endTime: {end_ts_ms}")

        # 너무 빠른 요청 방지
        time.sleep(0.2)

    if len(all_rows) == 0:
        log("[ERROR] 캔들 수집 실패(0행).")
        return pd.DataFrame(columns=["time","open","high","low","close","volume"])

    # 중복 제거 후 최신→과거 정렬 가정, 오름차순으로 뒤집기
    df = pd.DataFrame(all_rows, columns=["time","open","high","low","close","volume"])
    df = df.drop_duplicates(subset=["time"]).sort_values("time").reset_index(drop=True)
    # bars 만큼만 자르기 (끝쪽이 최신)
    if len(df) > bars:
        df = df.tail(bars).reset_index(drop=True)

    log(f"[DEBUG] 최종 캔들 수: {len(df)}개 (오름차순)")
    return df

# ========== 지표 계산 ==========
def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    RSI, Bollinger Bands, EMA20/50, CCI 추가
    """
    if df.empty:
        return df.copy()

    out = df.copy()

    # RSI (Wilder 방식)
    delta = out["close"].diff()
    up = np.where(delta > 0, delta, 0.0)
    down = np.where(delta < 0, -delta, 0.0)
    roll_up = pd.Series(up).ewm(alpha=1/RSI_PERIOD, adjust=False).mean()
    roll_down = pd.Series(down).ewm(alpha=1/RSI_PERIOD, adjust=False).mean()
    rs = roll_up / (roll_down + 1e-12)
    rsi = 100 - (100 / (1 + rs))
    out["rsi"] = rsi.to_numpy()

    # Bollinger
    ma = out["close"].rolling(BB_PERIOD).mean()
    std = out["close"].rolling(BB_PERIOD).std(ddof=0)
    out["bb_mid"] = ma
    out["bb_up"] = ma + BB_STD * std
    out["bb_low"] = ma - BB_STD * std
    out["bb_width_pct"] = (out["bb_up"] - out["bb_low"]) / (out["bb_mid"] + 1e-12)

    # EMA
    out["ema20"] = out["close"].ewm(span=EMA_FAST, adjust=False).mean()
    out["ema50"] = out["close"].ewm(span=EMA_SLOW, adjust=False).mean()

    # CCI
    tp = (out["high"] + out["low"] + out["close"]) / 3.0
    sma_tp = tp.rolling(CCI_PERIOD).mean()
    mad = (tp - sma_tp).abs().rolling(CCI_PERIOD).mean()
    out["cci"] = (tp - sma_tp) / (0.015 * (mad + 1e-12))

    return out

# ========== 최근 스윙 & 피보나치 ==========
def recent_swing_levels(df: pd.DataFrame, lookback: int = 200) -> Tuple[float, float, Dict[str, float]]:
    """
    최근 lookback 내 high/low로 피보 되돌림 레벨 계산.
    - 상방/하방 구분 없이 일단 최근 극값 기준.
    """
    if len(df) < lookback:
        lb = len(df)
    else:
        lb = lookback
    sub = df.tail(lb)
    recent_high = sub["high"].max()
    recent_low = sub["low"].min()

    # 상승 스윙 가정: low->high 기준 되돌림 레벨
    diff = recent_high - recent_low
    levels = {
        "0.236": recent_high - 0.236 * diff,
        "0.382": recent_high - 0.382 * diff,
        "0.5":   recent_high - 0.5   * diff,
        "0.618": recent_high - 0.618 * diff,
        "0.786": recent_high - 0.786 * diff,
    }
    return recent_low, recent_high, levels

def nearest_fib_proximity(price: float, fib_levels: Dict[str, float]) -> Tuple[str, float]:
    """
    가격과 가장 가까운 피보 레벨과 상대 오차 반환
    """
    best_key, best_err = None, 1e9
    for k, lvl in fib_levels.items():
        err = abs(price - lvl) / max(price, 1e-12)
        if err < best_err:
            best_err = err
            best_key = k
    return best_key, best_err

# ========== 캔들 패턴(간단 – 추세둔화형) ==========
def is_bullish_reversal(open_, high, low, close) -> bool:
    """
    간단한 해머/도지 계열 체크:
    - 아래꼬리 >= 몸통*2
    - 종가 >= 시가
    """
    body = abs(close - open_)
    lower_wick = close - low if close < open_ else open_ - low
    return (lower_wick >= 2 * (body + 1e-9)) and (close >= open_)
