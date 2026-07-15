import json
import requests

KAISAI_FILE = "kaisai_list.json"
BASE_URL = "https://www.keirin.jp/pc/json"

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "ja,en;q=0.9",
    "referer": "https://www.keirin.jp/pc/racelive",
    "user-agent": "Mozilla/5.0",
}

print("=== 083 奈良7R JSJ012テスト開始 ===")

with open(KAISAI_FILE, "r", encoding="utf-8") as f:
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

print("競輪場:", target.get("bkname"))
print("場コード:", target.get("bkCode"))
print("kaisai_listのraceNum:", target.get("raceNum"))
print("raceUrlPrm:", race_url_prm)

params = {
    "encp": race_url_prm,
    "type": "JSJ012",
    "selRaceNo": 7,
}

response = requests.get(
    BASE_URL,
    params=params,
    headers=HEADERS,
    timeout=30
)

print()
print("status:", response.status_code)
print("最終URL:", response.url)
print("文字数:", len(response.text))

try:
    data = response.json()
except Exception:
    print("JSON変換失敗")
    print(response.text[:1000])
    raise SystemExit

print()
print("resultCd:", data.get("resultCd"))
print("トップキー:")
print(list(data.keys()))

print()
print("C0201data:")
print(data.get("C0201data"))

print()
print("RT3HaraiGakuDispItemSubData:")
print(data.get("RT3HaraiGakuDispItemSubData"))

with open(
    "083_nara7_jsj012.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print()
print("保存完了: 083_nara7_jsj012.json")
print("=== 083 テスト終了 ===")