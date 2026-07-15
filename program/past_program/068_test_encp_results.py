import json
import requests

INPUT_FILE = "067_race_encp_map.json"

BASE_URL = "https://www.keirin.jp/pc/json"

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "ja,en;q=0.9",
    "referer": "https://www.keirin.jp/pc/race/",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/149.0.0.0 Safari/537.36"
    )
}

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    encp_list = json.load(f)

print("=== 068 encp別 JSJ012確認開始 ===")

for item in encp_list:

    order = item["順番"]
    encp = item["encp"]

    params = {
        "encp": encp,
        "type": "JSJ012"
    }

    response = requests.get(
        BASE_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    print()
    print("=" * 70)
    print("順番:", order)
    print("status:", response.status_code)

    try:
        data = response.json()

        print("resultCd:", data.get("resultCd"))

        c0201 = data.get("C0201data", {})

        print("selRaceNo:", c0201.get("selRaceNo"))
        print("raceName:", c0201.get("raceName"))
        print("joName:", c0201.get("joName"))

        jsj012 = data.get("JSJ012", {})

        harai_sub = jsj012.get(
            "haraiGakuSubData",
            {}
        )

        rh3_list = harai_sub.get(
            "RH3HaraiGakuDispItemSubData",
            []
        )

        if rh3_list:

            print("3連単:", rh3_list[0].get("kumiBan"))
            print("払戻金:", rh3_list[0].get("haraiGaku"))

        else:

            print("3連単: なし")
            print("払戻金: なし")

    except Exception as e:

        print("JSON解析エラー:", e)

print()
print("=== 068 確認終了 ===")