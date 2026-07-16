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

OUT_DIR = (
    BASE
    / "data_official"
    / "master"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_FILE = (
    OUT_DIR
    / "bank_codes.json"
)

JST = timezone(
    timedelta(hours=9)
)

START_DATE = (
    datetime.now(JST)
    - timedelta(days=1)
).date()

MAX_DAYS = 365

TARGET_COUNT = 43


# ===========================================================
# JSON保存
# ===========================================================

def save_json(path, data):

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


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

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(
        module
    )

    return module


# ===========================================================
# メイン
# ===========================================================

def collect_all_bank_codes():

    collector = load_collector_module()

    bank_codes = {}

    print()
    print("=" * 70)
    print("競輪場コード収集開始")
    print("=" * 70)
    print()

    for offset in range(MAX_DAYS):

        target_date = (
            START_DATE
            - timedelta(days=offset)
        ).strftime("%Y%m%d")

        print()
        print("-" * 70)
        print(
            f"対象日 : {target_date}"
        )
        print("-" * 70)

        try:

            daily_map = collector.build_daily_race_map(
                target_date
            )

        except Exception as e:

            print(
                "取得失敗 :",
                e,
            )

            continue

        venues = daily_map.get(
            "venues",
            [],
        )

        print(
            "開催場数 :",
            len(venues),
        )

        if len(venues) == 0:

            continue

        # -----------------------------------------
        # 競輪場コード取得
        # -----------------------------------------

        for venue in venues:

            venue_code = str(
                venue.get(
                    "venue_code",
                    ""
                )
            )

            jsj001 = venue.get(
                "jsj001"
            )

            if not isinstance(jsj001, dict):

                continue

            c0201 = jsj001.get(
                "C0201data",
                {}
            )

            sel_code = str(
                c0201.get(
                    "selKjyoCd",
                    ""
                )
            )

            jo_name = c0201.get(
                "joName",
                venue.get(
                    "venue",
                    ""
                )
            )

            print()

            print(
                "競輪場 :",
                jo_name
            )

            print(
                "venue_code :",
                venue_code
            )

            print(
                "selKjyoCd :",
                sel_code
            )

            if venue_code != sel_code:

                print(
                    "コード不一致"
                )

                continue

            if venue_code not in bank_codes:

                bank_codes[
                    venue_code
                ] = jo_name

                print(
                    "追加 :",
                    venue_code,
                    jo_name
                )

        # -----------------------------------------
        # 進捗表示
        # -----------------------------------------

        print()

        print(
            f"現在 {len(bank_codes)} / {TARGET_COUNT}"
        )

        if len(bank_codes) >= TARGET_COUNT:

            print()

            print(
                "43場取得完了"
            )

            break

    # =====================================================
    # JSON保存
    # =====================================================

    save_json(

        OUT_FILE,

        bank_codes,

    )

    print()

    print("=" * 70)

    print(
        "bank_codes.json 保存完了"
    )

    print(
        OUT_FILE
    )

    print()

    print(
        f"取得場数 : {len(bank_codes)}"
    )

    print("=" * 70)

    print()

    print(
        "取得一覧"
    )

    print()

    for code in sorted(
        bank_codes.keys(),
        key=int,
    ):

        print(
            f"{code} : {bank_codes[code]}"
        )


# ===========================================================
# main
# ===========================================================

if __name__ == "__main__":

    collect_all_bank_codes()   