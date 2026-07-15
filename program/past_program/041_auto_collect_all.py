import json
import csv
import os
import time
import requests

KAISAI_FILE = "kaisai_list.json"
CSV_FILE = "race_results.csv"
URL = "https://www.keirin.jp/pc/json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

with open(KAISAI_FILE, "r", encoding="utf-8") as f:
    kaisai_data = json.load(f)

file_exists = os.path.exists(CSV_FILE)

with open(
    CSV_FILE,
    "a",
    newline="",
    encoding="utf-8-sig"
) as csvfile:

    writer = csv.writer(csvfile)

    if not file_exists:
        writer.writerow([
            "date",
            "keirinjo",
            "race",
            "bet_type",
            "kumiBan",
            "haraiGaku",
            "ninki"
        ])

    print("=== 全開催場 3連単取得開始 ===")

    for race in kaisai_data:

        name = race.get("bkname", "")
        bk_code = race.get("bkCode", "")
        race_num = race.get("raceNum", "")
        encp = race.get("raceUrlPrm", "")

        print()
        print("======================")
        print("開催場:", name)
        print("場コード:", bk_code)
        print("現在R:", race_num)
        print("======================")

        params = {
            "encp": encp,
            "type": "JSJ012"
        }

        try:
            response = requests.get(
                URL,
                params=params,
                headers=headers,
                timeout=30
            )

            print("ステータス:", response.status_code)

            data = response.json()

            print("resultCd:", data.get("resultCd"))
            print("message:", data.get("message"))

            sanrentan_list = (
                data
                .get("haraiGakuSubData", {})
                .get("RT3HaraiGakuDispItemSubData", [])
            )

            if not sanrentan_list:
                print("3連単結果なし")
                continue

            for item in sanrentan_list:

                kumi = item.get("kumiBan", "")
                harai = item.get("haraiGaku", "")
                ninki = item.get("ninki", "")

                print(
                    "3連単:",
                    kumi,
                    "| 払戻:",
                    harai,
                    "| 人気:",
                    ninki
                )

                writer.writerow([
                    kaisai_data.get("today", "")
                    if isinstance(kaisai_data, dict)
                    else "",
                    name,
                    race_num,
                    "3連単",
                    kumi,
                    harai,
                    ninki
                ])

                csvfile.flush()

        except Exception as e:
            print("エラー:", e)

        time.sleep(1)

print()
print("=== 取得終了 ===")
print("保存先:", CSV_FILE)