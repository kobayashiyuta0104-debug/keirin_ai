import json
import urllib.request
import urllib.parse
import importlib.util
import os
from pathlib import Path
from datetime import datetime, timezone, timedelta

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

OUTPUT_DIR = (
    BASE
    / "data_official"
    / "debug_jsj"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

JST = timezone(timedelta(hours=9))

TARGET_DATE = datetime.now(JST).strftime("%Y%m%d")

# ===========================================================
# Collector読込
# ===========================================================

def load_collector():

    spec = importlib.util.spec_from_file_location(
        "collector",
        COLLECTOR_FILE,
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


# ===========================================================
# JSJ取得
# ===========================================================

def fetch_jsj(encp, jsj_type):

    query = urllib.parse.urlencode({

        "encp": encp,

        "type": jsj_type,

    })

    url = "https://www.keirin.jp/pc/json?" + query

    request = urllib.request.Request(

        url,

        headers={

            "User-Agent": "Mozilla/5.0",

            "Referer": "https://www.keirin.jp/",

            "Accept": "application/json",

            "X-Requested-With": "XMLHttpRequest",

        },

    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=2,
        ) as response:

            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            return json.loads(raw)

    except:

        return None


# ===========================================================
# Main
# ===========================================================

collector = load_collector()

daily_map = collector.build_daily_race_map(
    TARGET_DATE
)

venue = daily_map["venues"][0]

race = venue["races"][0]

encp = race["encParaR"]

print()
print("=" * 80)
print("JSJ総当たり調査")
print("=" * 80)
print()

print("対象日 :", TARGET_DATE)
print("開催 :", venue["venue"])
print("Race :", race["race_key"])
print()

success = []
failed = []

for number in range(1, 101):

    jsj = f"JSJ{number:03d}"

    print(f"{jsj} ... ", end="")

    result = fetch_jsj(encp, jsj)

    if result is None:

        print("NG")

        failed.append(jsj)

        continue

    success.append(jsj)

    print("OK")

    out_file = OUTPUT_DIR / f"{jsj}.json"

    with open(
        out_file,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("   保存 :", out_file.name)

    if isinstance(result, dict):

        print("   Top Keys")

        for key in result.keys():

            print("      ", key)

print()
print("=" * 80)
print("取得成功")
print("=" * 80)

for jsj in success:

    print(jsj)

print()
print("=" * 80)
print("取得失敗")
print("=" * 80)

for jsj in failed:

    print(jsj)

print()
print("成功 :", len(success))
print("失敗 :", len(failed))

input("\nEnterで終了...")