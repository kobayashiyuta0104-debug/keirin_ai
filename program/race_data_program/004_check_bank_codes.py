import importlib.util
import os
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

# ===========================================================
# 調査したい日付
# ===========================================================

TARGET_DATE = "20151001"

# ↑自由に変更
# 京都向日町・高松が開催されていた日付を入れる

# ===========================================================
# 004読込
# ===========================================================

def load_collector():

    if not COLLECTOR_FILE.exists():
        raise FileNotFoundError(COLLECTOR_FILE)

    spec = importlib.util.spec_from_file_location(
        "collector",
        COLLECTOR_FILE,
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module

# ===========================================================
# メイン
# ===========================================================

def main():

    collector = load_collector()

    print("=" * 80)
    print("競輪場コード調査")
    print("TARGET :", TARGET_DATE)
    print("=" * 80)

    daily_map = collector.build_daily_race_map(
        TARGET_DATE
    )

    venues = daily_map.get("venues", [])

    print()
    print("開催場数 :", len(venues))
    print()

    for i, venue in enumerate(venues, start=1):

        print("=" * 80)
        print(f"[{i}/{len(venues)}]")

        print("venue      :", venue.get("venue"))
        print("venue_code :", venue.get("venue_code"))

        jsj001 = venue.get("jsj001")

        if not jsj001:

            print("JSJ001なし")
            continue

        c0201 = jsj001.get("C0201data", {})

        print("selKjyoCd  :", c0201.get("selKjyoCd"))
        print("joName     :", c0201.get("joName"))
        print("raceName   :", c0201.get("raceName"))

    print()
    print("=" * 80)
    print("調査終了")
    print("=" * 80)


# ===========================================================

if __name__ == "__main__":

    main()