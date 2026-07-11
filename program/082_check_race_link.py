import json
import requests

INPUT_FILE = "kaisai_list.json"

URL = "https://www.keirin.jp/pc/racelive"

HEADERS = {
    "user-agent": "Mozilla/5.0",
    "accept-language": "ja,en;q=0.9",
}


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    races = json.load(f)


target = None

for race in races:
    if race.get("bkname") == "奈良":
        target = race
        break


if target is None:
    print("奈良が見つかりません")
    raise SystemExit


race_url_prm = target.get("raceUrlPrm")

print("=== 082 調査開始 ===")
print("競輪場:", target.get("bkname"))
print("レース:", target.get("raceNum"))
print("raceUrlPrm:", race_url_prm)


response = requests.get(
    URL,
    headers=HEADERS,
    timeout=30
)

html = response.text


print()
print("status:", response.status_code)
print("文字数:", len(html))

print()
print("raceUrlPrm値がHTML内にあるか:")
print(race_url_prm in html)


if race_url_prm in html:

    pos = html.find(race_url_prm)

    start = max(
        0,
        pos - 1000
    )

    end = min(
        len(html),
        pos + 1000
    )

    print()
    print("=== 前後2000文字 ===")
    print(html[start:end])

else:

    print()
    print("raceUrlPrm値はHTML内にありません")


print()
print("=== 082 調査終了 ===")