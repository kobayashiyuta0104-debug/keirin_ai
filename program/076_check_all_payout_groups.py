import json
import requests

INPUT_FILE = "067_race_encp_map.json"

BASE_URL = "https://www.keirin.jp/pc/json"

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    ),
    "x-requested-with": "XMLHttpRequest",
}

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    encp_list = json.load(f)


print("=== 076 生払戻グループ調査開始 ===")
print("encp候補数:", len(encp_list))


for index, item in enumerate(encp_list):

    encp = item.get("encp")

    print()
    print("=" * 80)
    print("順番:", index + 1)
    print("encp:", encp)

    response = requests.get(
        BASE_URL,
        params={
            "encp": encp,
            "type": "JSJ012"
        },
        headers=HEADERS,
        timeout=30
    )

    print("status:", response.status_code)

    try:
        data = response.json()

    except Exception as e:
        print("JSONエラー:", e)
        continue


    harai_sub = data.get(
        "haraiGakuSubData",
        {}
    )

    print()
    print("haraiGakuSubData KEY一覧:")

    for key in harai_sub.keys():
        print("KEY:", key)


    print()
    print("--- 各払戻グループの中身 ---")

    for key, value in harai_sub.items():

        print()
        print("-" * 60)
        print("KEY:", key)
        print("TYPE:", type(value).__name__)
        print("VALUE:")

        print(
            json.dumps(
                value,
                ensure_ascii=False,
                indent=2
            )[:3000]
        )


print()
print("=== 076 調査終了 ===")