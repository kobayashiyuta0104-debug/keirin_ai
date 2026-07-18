# ===========================================================
# 999_collect_all_historical.py
#
# 過去データ一括取得
#
# 001 Schedule
# 002 Pre Race
# 003 Player
# 004 Result
# 005 Race Data
#
# 2023/01/01 ～ 2026/07/15
# ===========================================================

from pathlib import Path
from datetime import datetime, timedelta
import importlib.util
import traceback
import time


# ===========================================================
# 基本設定
# ===========================================================

BASE_DIR = Path(__file__).resolve().parent

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2026, 7, 15)

ERROR_LOG = BASE_DIR / "999error_log.txt"

RACE_DATA_DIR = (
    BASE_DIR.parent.parent
    / "data_official"
    / "historical"
    / "race_data"
)


# ===========================================================
# モジュール読込
# ===========================================================

def load_module(filename, module_name):

    path = BASE_DIR / filename

    spec = importlib.util.spec_from_file_location(
    module_name,
    path
)

    if spec is None or spec.loader is None:
        raise ImportError(f"モジュールを読み込めません: {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


print("Loading modules...")

m001 = load_module(
    "001_collect_historical_schedule.py",
    "m001"
)

m002 = load_module(
    "002_collect_historical_pre_race.py",
    "m002"
)

m003 = load_module(
    "003_collect_historical_player.py",
    "m003"
)

m004 = load_module(
    "004_collect_historical_result.py",
    "m004"
)

m005 = load_module(
    "005_collect_historical_race_data.py",
    "m005"
)

print("Modules loaded.\n")


# ===========================================================
# 日付生成
# ===========================================================

def generate_dates():

    current = START_DATE

    while current <= END_DATE:

        yield current.strftime("%Y%m%d")

        current += timedelta(days=1)


# ===========================================================
# race_data存在確認
# ===========================================================

def race_data_exists(target_date):

    file = (
        RACE_DATA_DIR
        / f"{target_date}_race_data.json"
    )

    return file.exists()


# ===========================================================
# エラーログ
# ===========================================================

def write_error(target_date, error):

    with open(
        ERROR_LOG,
        "a",
        encoding="utf-8"
    ) as f:

        f.write("=" * 80 + "\n")
        f.write(target_date + "\n")
        f.write(str(error) + "\n")
        f.write(traceback.format_exc())
        f.write("\n\n")


# ===========================================================
# 表示
# ===========================================================

def print_header(total):

    print("=" * 60)
    print("Historical Data Collector")
    print("=" * 60)
    print()

    print("START :", START_DATE.strftime("%Y%m%d"))
    print("END   :", END_DATE.strftime("%Y%m%d"))
    print("TOTAL :", total)

    print()

# ===========================================================
# メイン処理
# ===========================================================

def run():

    start_time = time.time()

    total_days = (
        (END_DATE - START_DATE).days + 1
    )

    print_header(total_days)

    success = 0
    skip = 0
    error = 0

    dates = list(generate_dates())

    try:

        for index, target_date in enumerate(dates, start=1):

            print("=" * 60)
            print(f"[ {index} / {total_days} ]")
            print(f"DATE : {target_date}")
            print("=" * 60)

            # -----------------------------------
            # 取得済み判定
            # -----------------------------------

            if race_data_exists(target_date):

                print("SKIP")
                print()

                skip += 1

                continue

            # -----------------------------------
            # 実行開始
            # -----------------------------------

            try:

                print("001 Schedule")
                m001.main(target_date)

                print("002 Pre Race")
                m002.main(target_date)

                print("003 Player")
                m003.main(target_date)

                print("004 Result")
                m004.main(target_date)

                print("005 Race Data")
                m005.main(target_date)

                success += 1

                print()
                print("SUCCESS")
                print()

            except Exception as e:

                error += 1

                print()
                print("ERROR")
                print(e)
                print()

                write_error(target_date, e)

                continue

    except KeyboardInterrupt:

        print()
        print("=" * 60)
        print("STOPPED BY USER")
        print("=" * 60)
        print()

    elapsed = time.time() - start_time

    return (
        success,
        skip,
        error,
        elapsed
    )

# ===========================================================
# 結果表示
# ===========================================================

def print_result(success, skip, error, elapsed):

    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)

    print()
    print("=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print()

    print(f"SUCCESS : {success}")
    print(f"SKIP    : {skip}")
    print(f"ERROR   : {error}")

    print()
    print("-" * 60)

    print(
        f"TIME : "
        f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    )

    print()
    print("=" * 60)


# ===========================================================
# main
# ===========================================================

def main():

    success, skip, error, elapsed = run()

    print_result(
        success,
        skip,
        error,
        elapsed
    )


# ===========================================================
# 実行
# ===========================================================

if __name__ == "__main__":

    main()