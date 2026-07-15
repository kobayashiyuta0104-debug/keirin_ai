import json
import requests

INPUT_FILE = "kaisai_list.json"

BASE_URL = "https://www.keirin.jp/pc/json"

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "ja,en;q=0.9",
    "referer": "https://www.keirin.jp/pc/racelive",
    "user-agent": "Mozilla/5.0",
}


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    races = json.load(f)


# まず小松島だけ使う
target = None

for race in races:

    if race.get("bkname") == "小松島":
        target = race
        break


if target is None:
    print("小松島が見つかりません")
    raise SystemExit


encp = target.get("raceUrlPrm")

print("=== 062 レース切替テスト ===")
print("競輪場: 小松島")
print("encp:", encp)


for race_no in range(1, 13):

    params = {
        "encp": encp,
        "type": "JSJ001",
        "selRaceNo": race_no,
    }

    response = requests.get(
        BASE_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    print()
    print("=" * 50)
    print("指定レース:", race_no)
    print("status:", response.status_code)

    try:
        data = response.json()
    except Exception:
        print("JSON変換失敗")
        continue

    print("resultCd:", data.get("resultCd"))

    c0201 = data.get("C0201data", {})

    print(
        "返ってきた selRaceNo:",
        c0201.get("selRaceNo")
    )

    print(
        "返ってきた encSelParaR:",
        c0201.get("encSelParaR")
    )


print()
print("=== 062 テスト終了 ===")