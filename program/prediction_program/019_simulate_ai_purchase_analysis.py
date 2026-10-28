# -*- coding: utf-8 -*-
"""
019_simulate_ai_purchase_analysis.py

AI予想と同じ購入ルールで購入した場合の収支を、
現在のAI分析Excelと同じ切り口で集計する。

購入ルール
------------
AI予想のクラスを「購入対象の払戻レンジ」として使用する。

例：
AI予想 = 10,000～19,999円
→ オッズCSVの3連単504通りから、
   100円購入時の払戻が10,000～19,999円になる組み合わせを全部購入。

実際に的中した場合の払戻は、
予測CSVの「三連単\n払戻」を使用する。
（オッズCSVは「何を買うか」の判定に使用）

分析軸
------
・全体
・AI予想クラス別
・競輪場別
・グレード別
・レース種別別
・AI確信度別
・確信度 × AI予想クラス
・開催区分別
・レース明細
・データ品質
"""

import os
import re
import math
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter


# ============================================================
# 設定
# ============================================================

PREDICTION_FILE = r"C:\競輪AI\csv\training\VER1.5_training_prediction(2026.1.1~2026.8.18).csv"
ODDS_FILE = r"C:\競輪AI\csv\historical_date\historical_odds\historical_odds_2026.1.1~2026.8.18.csv"

OUTPUT_DIR = r"C:\競輪AI\csv\analysis\019_simulate_ai_purchase_analysis"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "019_simulate_ai_purchase_analysis_result.xlsx"
)

BET_UNIT = 100


# ============================================================
# AI予想クラス
# ============================================================

CLASS_ORDER = [
    "0～1,999円",
    "2,000～4,999円",
    "5,000～9,999円",
    "10,000～19,999円",
    "20,000～29,999円",
    "30,000～49,999円",
    "50,000～99,999円",
    "100,000円以上",
]

CLASS_RANGES = {
    "0～1,999円": (0, 1999),
    "2,000～4,999円": (2000, 4999),
    "5,000～9,999円": (5000, 9999),
    "10,000～19,999円": (10000, 19999),
    "20,000～29,999円": (20000, 29999),
    "30,000～49,999円": (30000, 49999),
    "50,000～99,999円": (50000, 99999),
    "100,000円以上": (100000, float("inf")),
}


# ============================================================
# 共通関数
# ============================================================

def read_csv_auto(path):
    """UTF-8系CSVを読み込む。"""
    for enc in ["utf-8-sig", "utf-8", "cp932"]:
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(
        "unknown", b"", 0, 1, f"CSVを読み込めません: {path}"
    )


def clean_text(x):
    if pd.isna(x):
        return ""
    return str(x).strip()


def normalize_class(x):
    """AI予想クラスの表記を正規化。"""
    s = clean_text(x)
    s = s.replace("\n", "")
    s = s.replace(" ", "")
    return s


def normalize_number(x):
    """数字文字列をfloatへ。"""
    if pd.isna(x):
        return None

    s = str(x).strip()
    if not s:
        return None

    s = s.replace(",", "")
    s = s.replace("円", "")

    # オッズCSVの '-' 等
    if s in {"-", "--", "---", "nan", "NaN", "None"}:
        return None

    try:
        return float(s)
    except Exception:
        return None


def parse_actual_payout(x):
    """三連単払戻を円の数値へ。"""
    return normalize_number(x)


def parse_confidence(x):
    """
    AI確信度
    例:
      22% -> 22.0
      22  -> 22.0
    """
    if pd.isna(x):
        return None

    s = str(x).strip().replace("%", "")
    try:
        return float(s)
    except Exception:
        return None


def confidence_group(x):
    """
    現在の分析と合わせて10%刻み。
    例:
      22 -> 20～29%
      40以上 -> 40%以上
    """
    v = parse_confidence(x)

    if v is None:
        return "不明"

    if v < 10:
        return "0～9%"
    if v < 20:
        return "10～19%"
    if v < 30:
        return "20～29%"
    if v < 40:
        return "30～39%"
    if v < 50:
        return "40～49%"
    if v < 60:
        return "50～59%"
    if v < 70:
        return "60～69%"
    if v < 80:
        return "70～79%"
    if v < 90:
        return "80～89%"
    return "90～100%"


def make_result_combo(row):
    """予測CSVの実際の1着2着3着から3連単を作る。"""
    a = clean_text(row.get("１着", ""))
    b = clean_text(row.get("２着", ""))
    c = clean_text(row.get("３着", ""))

    if not a or not b or not c:
        return ""

    # 1号車 -> "1" のような表記に揃える
    def car_no(s):
        m = re.search(r"\d+", s)
        return m.group(0) if m else ""

    a = car_no(a)
    b = car_no(b)
    c = car_no(c)

    if not a or not b or not c:
        return ""

    return f"{a}-{b}-{c}"


def class_range(ai_class):
    ai_class = normalize_class(ai_class)

    # 改行なしのCSV表記に合わせる
    aliases = {
        "0～1,999円": "0～1,999円",
        "2,000～4,999円": "2,000～4,999円",
        "5,000～9,999円": "5,000～9,999円",
        "10,000～19,999円": "10,000～19,999円",
        "20,000～29,999円": "20,000～29,999円",
        "30,000～49,999円": "30,000～49,999円",
        "50,000～99,999円": "50,000～99,999円",
        "100,000円以上": "100,000円以上",
    }

    key = aliases.get(ai_class)
    if key is None:
        return None

    return CLASS_RANGES[key]


# ============================================================
# 1. 読み込み
# ============================================================

print("=== 019 AI購入収支分析 開始 ===")

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("\n[1] 予測CSV読み込み")
pred = read_csv_auto(PREDICTION_FILE)
print(f"  予測データ: {len(pred):,} レース")

print("\n[2] オッズCSV読み込み")
odds = read_csv_auto(ODDS_FILE)
print(f"  オッズデータ: {len(odds):,} レース")


# ============================================================
# 2. 列チェック
# ============================================================

required_pred = [
    "レースキー",
    "グレード",
    "競輪場",
    "レース\n番号",
    "レース種別",
    "開催区分",
    "AI予想",
    "AI確信度",
    "三連単\n払戻",
    "１着",
    "２着",
    "３着",
]

required_odds = ["race_key"]

missing_pred = [c for c in required_pred if c not in pred.columns]
missing_odds = [c for c in required_odds if c not in odds.columns]

if missing_pred:
    raise ValueError(f"予測CSVに必要な列がありません: {missing_pred}")

if missing_odds:
    raise ValueError(f"オッズCSVに必要な列がありません: {missing_odds}")


# ============================================================
# 3. race_keyで結合
# ============================================================

pred["レースキー"] = pred["レースキー"].astype(str).str.strip()
odds["race_key"] = odds["race_key"].astype(str).str.strip()

odds = odds.drop_duplicates("race_key")

df = pred.merge(
    odds,
    left_on="レースキー",
    right_on="race_key",
    how="inner",
    suffixes=("", "_odds")
)

print(f"\n[3] 結合")
print(f"  共通レース: {len(df):,}")


# ============================================================
# 4. 3連単オッズ列を特定
# ============================================================

base_odds_cols = {
    "race_key",
    "date",
    "jo_code",
    "jo_name",
    "race_no",
}

trifecta_cols = []

for c in odds.columns:
    if c in base_odds_cols:
        continue

    if re.fullmatch(r"[1-9]-[1-9]-[1-9]", str(c)):
        # 同じ車番を除外
        parts = c.split("-")
        if len(set(parts)) == 3:
            trifecta_cols.append(c)

print(f"  3連単オッズ列: {len(trifecta_cols)} 通り")


# ============================================================
# 5. 購入シミュレーション
# ============================================================

records = []

for idx, row in df.iterrows():

    ai_class = normalize_class(row["AI予想"])
    rng = class_range(ai_class)

    # AI予想クラスが不明なら購入しない
    if rng is None:
        continue

    low, high = rng

    actual_combo = make_result_combo(row)
    actual_payout = parse_actual_payout(row["三連単\n払戻"])

    purchased_points = []
    purchase_count = 0
    hit = False

    # AI予想クラスの払戻レンジに入る3連単を全部購入
    for combo in trifecta_cols:

        odds_value = normalize_number(row.get(combo))

        if odds_value is None:
            continue

        # オッズ × 100円 = 100円購入時の払戻相当額
        estimated_payout = odds_value * BET_UNIT

        if estimated_payout >= low and estimated_payout <= high:
            purchased_points.append(combo)
            purchase_count += 1

            if combo == actual_combo:
                hit = True

    purchase_amount = purchase_count * BET_UNIT
    payout = actual_payout if hit and actual_payout is not None else 0
    profit = payout - purchase_amount

    records.append({
        "レースキー": row["レースキー"],
        "日付": row.get("日付", ""),
        "グレード": row.get("グレード", ""),
        "競輪場": row.get("競輪場", ""),
        "レース番号": row.get("レース\n番号", ""),
        "レース種別": row.get("レース種別", ""),
        "開催区分": row.get("開催区分", ""),
        "AI予想": ai_class,
        "AI確信度": parse_confidence(row.get("AI確信度")),
        "AI確信度区分": confidence_group(row.get("AI確信度")),
        "実際の3連単": actual_combo,
        "実際の払戻": actual_payout,
        "購入点数": purchase_count,
        "購入金額": purchase_amount,
        "的中数": 1 if hit else 0,
        "払戻": payout,
        "収支": profit,
        "購入車券": ",".join(purchased_points),
    })


sim = pd.DataFrame(records)

print(f"\n[4] シミュレーション完了")
print(f"  シミュレーション対象: {len(sim):,} レース")
print(f"  購入レース: {(sim['購入点数'] > 0).sum():,} レース")


# ============================================================
# 6. 集計関数
# ============================================================

def summary_from_group(g):
    races = len(g)
    purchase_races = int((g["購入点数"] > 0).sum())
    points = int(g["購入点数"].sum())
    purchase = int(g["購入金額"].sum())
    hits = int(g["的中数"].sum())
    payout = int(g["払戻"].sum())
    profit = payout - purchase

    recovery = (payout / purchase * 100) if purchase > 0 else 0
    hit_rate = (hits / purchase_races * 100) if purchase_races > 0 else 0
    avg_purchase = purchase / purchase_races if purchase_races > 0 else 0
    avg_points = points / purchase_races if purchase_races > 0 else 0

    return pd.Series({
        "レース数": races,
        "購入レース数": purchase_races,
        "購入点数": points,
        "購入金額": purchase,
        "的中数": hits,
        "払戻": payout,
        "収支": profit,
        "回収率": recovery,
        "的中率": hit_rate,
        "1レース平均購入額": avg_purchase,
        "1レース平均購入点数": avg_points,
    })


def grouped_summary(df, column):
    if df.empty:
        return pd.DataFrame()

    result = df.groupby(column, dropna=False).apply(
        summary_from_group,
        include_groups=False
    ).reset_index()

    return result


# ============================================================
# 7. 各分析
# ============================================================

print("\n[5] 分析作成")

overall = summary_from_group(sim).to_frame().T

class_analysis = grouped_summary(sim, "AI予想")
venue_analysis = grouped_summary(sim, "競輪場")
grade_analysis = grouped_summary(sim, "グレード")
race_type_analysis = grouped_summary(sim, "レース種別")
confidence_analysis = grouped_summary(sim, "AI確信度区分")
holding_analysis = grouped_summary(sim, "開催区分")

confidence_class_analysis = (
    sim.groupby(
        ["AI確信度区分", "AI予想"],
        dropna=False
    )
    .apply(summary_from_group, include_groups=False)
    .reset_index()
)


# ============================================================
# 8. データ品質
# ============================================================

quality = pd.DataFrame([
    ["予測CSVレース数", len(pred)],
    ["オッズCSVレース数", len(odds)],
    ["共通レース数", len(df)],
    ["シミュレーション対象", len(sim)],
    ["オッズ3連単列数", len(trifecta_cols)],
    ["購入レース数", int((sim["購入点数"] > 0).sum())],
    ["購入点数", int(sim["購入点数"].sum())],
    ["購入金額", int(sim["購入金額"].sum())],
    ["的中数", int(sim["的中数"].sum())],
    ["払戻", int(sim["払戻"].sum())],
    ["収支", int(sim["収支"].sum())],
], columns=["項目", "値"])


# ============================================================
# 9. Excel出力
# ============================================================

print("\n[6] Excel出力")

with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:

    overall.to_excel(writer, sheet_name="全体収支", index=False)
    class_analysis.to_excel(writer, sheet_name="AI予想クラス別", index=False)
    venue_analysis.to_excel(writer, sheet_name="競輪場別", index=False)
    grade_analysis.to_excel(writer, sheet_name="グレード別", index=False)
    race_type_analysis.to_excel(writer, sheet_name="レース種別別", index=False)
    confidence_analysis.to_excel(writer, sheet_name="AI確信度別", index=False)
    confidence_class_analysis.to_excel(
        writer,
        sheet_name="確信度×AI予想",
        index=False
    )
    holding_analysis.to_excel(writer, sheet_name="開催区分別", index=False)
    sim.to_excel(writer, sheet_name="レース明細", index=False)
    quality.to_excel(writer, sheet_name="データ品質", index=False)


# ============================================================
# 10. Excel整形
# ============================================================

wb = load_workbook(OUTPUT_FILE)

for ws in wb.worksheets:

    # 1行目を太字
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    # 列幅
    for col_idx in range(1, ws.max_column + 1):
        letter = get_column_letter(col_idx)

        max_len = 0

        for row_idx in range(1, min(ws.max_row, 1000) + 1):
            value = ws.cell(row_idx, col_idx).value

            if value is None:
                continue

            length = len(str(value))

            if length > max_len:
                max_len = length

        ws.column_dimensions[letter].width = min(max(max_len + 2, 10), 40)

    # 金額・率の表示
    headers = {
        ws.cell(1, c).value: c
        for c in range(1, ws.max_column + 1)
    }

    for name in [
        "購入金額",
        "払戻",
        "収支",
        "1レース平均購入額",
        "実際の払戻",
    ]:
        if name in headers:
            c = headers[name]
            for r in range(2, ws.max_row + 1):
                ws.cell(r, c).number_format = '#,##0"円"'

    for name in ["回収率", "的中率"]:
        if name in headers:
            c = headers[name]
            for r in range(2, ws.max_row + 1):
                ws.cell(r, c).number_format = '0.00"%"'

wb.save(OUTPUT_FILE)

print("\n========================================")
print("=== 019 AI購入収支分析 完了 ===")
print("========================================")
print(f"出力先: {OUTPUT_FILE}")
print()
print("【全体】")
print(f"レース数       : {len(sim):,}")
print(f"購入レース数   : {(sim['購入点数'] > 0).sum():,}")
print(f"購入点数       : {sim['購入点数'].sum():,}")
print(f"購入金額       : {sim['購入金額'].sum():,} 円")
print(f"的中数         : {sim['的中数'].sum():,}")
print(f"払戻           : {sim['払戻'].sum():,} 円")
print(f"収支           : {sim['収支'].sum():,} 円")

total_purchase = sim["購入金額"].sum()
total_payout = sim["払戻"].sum()

if total_purchase > 0:
    print(f"回収率         : {total_payout / total_purchase * 100:.2f}%")

print("========================================")
