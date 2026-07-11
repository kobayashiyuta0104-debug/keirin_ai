import json
import requests
from urllib.parse import urlencode

KAISAI_FILE = "kaisai_list.json"
OUTPUT_FILE = "056_all_race_results.json"

with open(
    KAISAI_FILE,
    "r",
    encoding="utf-8"
) as f:

    races = json.load(f)


print("=== 056 1R〜12R 全自動取得開始 ===")
print("開催データ数:", len(races))


for race in races:

    name = race.get("bkname", "")
    code = race.get("bkCode", "")

    print()
    print("========================")
    print("競輪場:", name)
    print("場コード:", code)

    for race_no in range(1, 13):

        print(
            name,
            str(race_no) + "R"
        )


print()
print("=== テスト終了 ===")