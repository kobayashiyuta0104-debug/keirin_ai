import json
import importlib.util
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ===========================================================
# 基本設定
# ===========================================================

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent

COLLECTOR_FILE = (
    BASE
    / "official_program"
    / "origin_program"
    / "004_collect_historical_raw.py"
)

MASTER_FILE = (
    BASE
    / "data_official"
    / "master"
    / "bank_master.json"
)

DAILY_DIR = BASE / "data_official" / "daily"
DAILY_DIR.mkdir(parents=True, exist_ok=True)

JST = timezone(timedelta(hours=9))

YESTERDAY = (
    datetime.now(JST) - timedelta(days=1)
).strftime("%Y%m%d")

RACE_DATA_FILE = (
    DAILY_DIR
    / f"{YESTERDAY}_race_data.json"
)

# ===========================================================
# JSON保存
# ===========================================================

def save_json(path, data):

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

# ===========================================================
# bank_master読込
# ===========================================================

def load_bank_master():

    if not MASTER_FILE.exists():

        print("bank_master.json がありません")

        return {}

    with open(
        MASTER_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    return data.get("banks", {})

# ===========================================================
# 004読込
# ===========================================================

def load_collector_module():

    if not COLLECTOR_FILE.exists():

        raise FileNotFoundError(
            "004_collect_historical_raw.py がありません"
        )

    spec = importlib.util.spec_from_file_location(
        "official_collector_004",
        COLLECTOR_FILE,
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module

# ===========================================================
# 開催情報作成
# ===========================================================

def build_venue_row(

    jsj001,
    bank_master,

):

    c0201 = jsj001["C0201data"]

    bank_code = str(
        c0201["selKjyoCd"]
    )

    bank = bank_master.get(
        bank_code,
        {},
    )

    row = {

        "開催日":

            c0201.get("selKaisai"),

        "競輪場コード":

            bank_code,

        "競輪場名":

            c0201.get("joName"),

        "グレード":

            c0201.get("imgGradeAlt"),

        "開催名":

            c0201.get("raceName"),

        "周長(m)":

            bank.get("周長(m)"),

        "みなし直線(m)":

            bank.get("みなし直線(m)"),

        "カント角(度)":

            bank.get("カント角(度)"),

        "raw_jsj001":

            jsj001,

    }

    return row

# ===========================================================
# 開催情報取得
# ===========================================================

def collect_race_data():

    collector = load_collector_module()

    bank_master = load_bank_master()

    print()
    print("==========================================")
    print("開催情報取得開始")
    print("TARGET DATE :", YESTERDAY)
    print("==========================================")
    print()

    daily_map = collector.build_daily_race_map(
        YESTERDAY
    )

    venue_rows = []

    venue_total = len(
        daily_map.get("venues", [])
    )

    current = 0

    for venue in daily_map.get(
        "venues",
        [],
    ):

        current += 1

        venue_name = venue.get("venue")

        print(
            f"[{current}/{venue_total}] {venue_name}"
        )

        jsj001 = venue.get("jsj001")

        if jsj001 is None:

            print("  JSJ001なし")

            continue

        try:

            row = build_venue_row(

                jsj001=jsj001,

                bank_master=bank_master,

            )

            venue_rows.append(row)

            print("  OK")

        except Exception as e:

            print(
                "  ERROR :",
                e,
            )

    output = {

        "program":
            "002_collect_race_data.py",

        "data_type":
            "RACE_DATA",

        "target_date":
            YESTERDAY,

        "venue_count":
            len(venue_rows),

        "venues":
            venue_rows,

    }

    save_json(

        RACE_DATA_FILE,

        output,

    )

    print()

    print("==========================================")
    print("保存完了")
    print(RACE_DATA_FILE)
    print("開催数 :", len(venue_rows))
    print("==========================================")

    return output


# ===========================================================
# main
# ===========================================================

if __name__ == "__main__":

    collect_race_data()