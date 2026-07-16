import json
import urllib.request
import urllib.parse
import importlib.util
import os
from datetime import datetime, timezone, timedelta
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
# JSJ003取得
# ===========================================================

def fetch_jsj003(encp):

    query = urllib.parse.urlencode({
        "encp": encp,
        "type": "JSJ003",
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

    with urllib.request.urlopen(request) as response:

        return json.loads(
            response.read().decode("utf-8")
        )

# ===========================================================
# main
# ===========================================================

collector = load_collector()

daily_map = collector.build_daily_race_map(
    TARGET_DATE
)

venue = daily_map["venues"][0]

race = venue["races"][0]

encp = race["encParaR"]

print("=" * 80)
print("JSJ003 デバッグ")
print("=" * 80)
print()

print("対象日 :", TARGET_DATE)
print("開催 :", venue["venue"])
print("race_key :", race["race_key"])
print("encParaR :", encp)
print()

js = fetch_jsj003(encp)

print("=" * 80)
print("JSJ003 JSON")
print("=" * 80)

print(
    json.dumps(
        js,
        ensure_ascii=False,
        indent=2,
    )
)

print()

print("=" * 80)
print("トップキー")
print("=" * 80)

for k in js.keys():
    print(k)

if isinstance(js, dict):

    for key, value in js.items():

        if isinstance(value, dict):

            print()

            print("=" * 80)
            print(key, "キー")
            print("=" * 80)

            for k in value.keys():

                print(k)

print()

input("Enterで終了...")