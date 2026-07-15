import json

INPUT_FILE = "kaisai_list.json"

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

print("=== 080 raceUrlPrm確認開始 ===")

for i, item in enumerate(data[:8], 1):

    print()
    print("=" * 70)

    print("番号:", i)
    print("競輪場:", item.get("bkname"))
    print("bkCode:", item.get("bkCode"))
    print("kCode:", item.get("kCode"))
    print("レース:", item.get("raceNum"))
    print("raceUrlPrm:", item.get("raceUrlPrm"))

print()
print("=== 080 確認終了 ===")