import json
import csv
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

# ===========================================================
# 基本設定
# ===========================================================

import os

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent

DAILY_DIR = BASE / "data_official" / "daily"
CSV_DIR = BASE / "csv" / "lines"
CSV_DIR.mkdir(parents=True, exist_ok=True)

# 前日の日付
JST = timezone(timedelta(hours=9))
YESTERDAY = (datetime.now(JST) - timedelta(days=1)).strftime("%Y%m%d")

PRE_RACE_FILE = DAILY_DIR / f"{YESTERDAY}_pre_race.json"
OUTPUT_CSV = CSV_DIR / f"{YESTERDAY}_lines.csv"


# ===========================================================
# JSON 読込
# ===========================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ===========================================================
# ライン情報CSV出力（prediction_type / provider 追加版）
# ===========================================================

def export_lines_csv():

    if not PRE_RACE_FILE.exists():
        raise FileNotFoundError(f"{PRE_RACE_FILE} がありません")

    root = load_json(PRE_RACE_FILE)
    rows = root.get("races", [])

    output_rows = []

    # ===========================================================
    # ライン列は固定9列
    # ===========================================================

    max_lines = 9

    # CSVヘッダー作成
    fieldnames = [
        "レースキー",
        "開催場",
        "レース番号",
        "戦型",   # ←追加
        "提供者"           # ←追加
    ]

    for i in range(1, max_lines + 1):
        fieldnames.append(f"line_{i}")

    # データ作成
    for row in rows:
        race_key = row.get("race_key")
        venue = row.get("venue")
        race_no = row.get("race_no")

        line_info = row.get("line_prediction", {})
        line_found = line_info.get("line_found", False)
        prediction_type = line_info.get("prediction_type") or ""
        provider = line_info.get("provider") or ""

        main_lines = line_info.get("main_lines", [])

        # ラインを文字列化
        line_cells = []
        for line in main_lines:
            line_cells.append("-".join(str(x) for x in line))

        # 足りない分は空欄で埋める
        while len(line_cells) < max_lines:
            line_cells.append("")

        output_rows.append({
            "レースキー": race_key,
            "開催場": venue,
            "レース番号": race_no,
            "戦型": prediction_type,
            "提供者": provider,
            **{f"line_{i+1}": line_cells[i] for i in range(max_lines)}
        })

    # CSV 出力
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print()
    print("=== ライン情報CSV（prediction_type / provider 追加）出力 完了 ===")
    print("保存:", OUTPUT_CSV)


# ===========================================================
# main
# ===========================================================

if __name__ == "__main__":
    export_lines_csv()
