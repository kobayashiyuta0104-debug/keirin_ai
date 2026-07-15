import json
import requests

INPUT_FILE = "kaisai_list.json"

BASE_URL = "https://www.keirin.jp/pc/json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    races = json.load(f)

print("=== 078 全開催場 encp確認開始 ===")
print("データ件数:", len(races))

venue_data = {}

for race in races:

    venue = race.get("競輪場")
    encp = race.get("encSelParaR")

    if not venue or not encp:
        continue

    if venue not in venue_data:
        venue_data[venue] = []

    if encp not in venue_data[venue]:
        venue_data[venue].append(encp)

print()
print("開催場数:", len(venue_data))

for venue, encp_list in venue_data.items():

    print()
    print("=" * 70)
    print("競輪場:", venue)
    print("encp候補数:", len(encp_list))

    for i, encp in enumerate(encp_list, 1):

        print(
            "候補",
            i,
            ":",
            encp
        )

print()
print("=== 078 確認終了 ===")