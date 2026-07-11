import json
import requests

URL = "https://www.keirin.jp/pc/json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

with open("kaisai_list.json", "r", encoding="utf-8") as f:
    races = json.load(f)

print("=== 各開催場の結果JSON取得テスト ===")
print()

for race in races:
    name = race.get("bkname", "不明")
    encp = race.get("raceUrlPrm", "")

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

        print(
            name,
            "| ステータス:",
            response.status_code,
            "| 文字数:",
            len(response.text)
        )

    except Exception as e:
        print(name, "| エラー:", e)

print("返り値:", response.text)
print()