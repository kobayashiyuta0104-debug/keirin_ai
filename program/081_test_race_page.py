import json
import requests

INPUT_FILE = "kaisai_list.json"

BASE_PAGE = "https://www.keirin.jp/pc/racelive"

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


# 奈良を探す
target = None

for race in races:

    if race.get("bkname") == "奈良":

        target = race
        break


if target is None:

    print("奈良が見つかりません")

    raise SystemExit


race_url_prm = target.get("raceUrlPrm")

print("=== 081 レースページ確認開始 ===")
print("競輪場:", target.get("bkname"))
print("レース:", target.get("raceNum"))
print("raceUrlPrm:", race_url_prm)


params = {
    "raceUrlPrm": race_url_prm
}


response = requests.get(
    BASE_PAGE,
    params=params,
    headers=HEADERS,
    timeout=30
)


print()
print("status:", response.status_code)
print("最終URL:", response.url)
print("文字数:", len(response.text))

print()
print("HTML先頭2000文字:")
print(response.text[:2000])

print()
print("JSJ012あり:", "JSJ012" in response.text)
print("encSelParaRあり:", "encSelParaR" in response.text)
print("selRaceNoあり:", "selRaceNo" in response.text)

print()
print("=== 081 確認終了 ===")