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

print("=== 069 レスポンス構造確認開始 ===")

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

        print("トップ階層KEY:")
        print(list(data.keys()))

        print()
        print("JSON先頭1500文字:")
        print(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            )[:1500]
        )

    except Exception as e:

        print("エラー:", e)

print()
print("=== 069 確認終了 ===")