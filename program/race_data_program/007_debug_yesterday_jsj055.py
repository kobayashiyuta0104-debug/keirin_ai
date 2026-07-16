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

TARGET_DATE = (
    datetime.now(JST) - timedelta(days=1)
).strftime("%Y%m%d")


# ===========================================================
# collector
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
# JSJ055取得
# ===========================================================

def fetch_jsj055(encp):

    query = urllib.parse.urlencode({

        "encp": encp,

        "type": "JSJ055",

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

    with urllib.request.urlopen(
        request,
        timeout=10,
    ) as response:

        return json.loads(
            response.read().decode(
                "utf-8",
                errors="replace",
            )
        )


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

print("=" * 80)
print("昨日のJSJ055 デバッグ")
print("=" * 80)
print()

print("対象日 :", TARGET_DATE)
print("開催 :", venue["venue"])
print("race_key :", race["race_key"])
print("encParaR :", encp)
print()

js = fetch_jsj055(encp)

save_path = OUTPUT_DIR / "JSJ055_yesterday.json"

with open(
    save_path,
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        js,
        f,
        ensure_ascii=False,
        indent=2,
    )

print("保存 :", save_path)
print()

print("=" * 80)
print("トップキー")
print("=" * 80)

for k in js.keys():

    print(k)

print()

print("=" * 80)
print("JSON全文")
print("=" * 80)

print(
    json.dumps(
        js,
        ensure_ascii=False,
        indent=2,
    )
)

input("\nEnterで終了...")