import requests
import json

URL = "https://www.keirin.jp/pc/json"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.keirin.jp/pc/racelive",
}

# HARで確認した開催一覧JSON
params = {
    "encp": "hXAFouF_EW8oCnSpPo40hpDA7JUrLLgRjYqdhgPAgTM",
    "type": "JSJ004",
}

response = requests.get(
    URL,
    params=params,
    headers=headers,
    timeout=30
)

print("ステータス:", response.status_code)
print()

if response.status_code == 200:

    data = response.json()

    print("=== 今日の開催場 ===")
    print(data.get("today"))
    print()

    kaisai_data = data.get("kaisaiData", [])

    for race in kaisai_data:

        print(
            race.get("bkname"),
            "| 場コード:", race.get("bkCode"),
            "| 現在:", race.get("raceNum"),
            "| encp:", race.get("raceUrlPrm")
        )

else:
    print("取得失敗")

    import json

with open("kaisai_list.json", "w", encoding="utf-8") as f:
    json.dump(kaisai_data, f, ensure_ascii=False, indent=2)

print()
print("開催場一覧を保存しました！")
print("保存先: kaisai_list.json")