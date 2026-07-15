import json
import csv
import os

JSON_FILE = "036_result.json"
CSV_FILE = "race_results.csv"

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

sanrentan_list = (
    data
    .get("haraiGakuSubData", {})
    .get("RT3HaraiGakuDispItemSubData", [])
)

print("=== 3連単結果 ===")

if not sanrentan_list:
    print("3連単データがありません")

else:
    file_exists = os.path.exists(CSV_FILE)

    with open(
        CSV_FILE,
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "bet_type",
                "kumiBan",
                "haraiGaku",
                "ninki"
            ])

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
                "3連単",
                kumi,
                harai,
                ninki
            ])

print()
print("保存完了！")
print("保存先:", CSV_FILE)