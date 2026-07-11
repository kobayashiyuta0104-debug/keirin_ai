import json
import base64
import requests
from urllib.parse import urlparse, parse_qs

HAR_FILE = "result_page.har"

with open(HAR_FILE, "r", encoding="utf-8") as f:
    har = json.load(f)

entries = har["log"]["entries"]

jsj001_url = None

for entry in entries:
    url = entry.get("request", {}).get("url", "")

    if "/pc/json" not in url:
        continue

    params = parse_qs(urlparse(url).query)

    if params.get("type") == ["JSJ001"]:
        jsj001_url = url
        break

if jsj001_url is None:
    print("JSJ001が見つかりません")
    raise SystemExit

print("=== JSJ001取得 ===")

response = requests.get(jsj001_url)

print("status:", response.status_code)

data001 = response.json()

print("resultCd:", data001.get("resultCd"))

c0201 = data001.get("C0201data", {})

encp = c0201.get("encSelParaR")

print("selKaisai:", c0201.get("selKaisai"))
print("selKjyoCd:", c0201.get("selKjyoCd"))
print("selRaceNo:", c0201.get("selRaceNo"))
print("encSelParaR:", encp)

if not encp:
    print("encSelParaRがありません")
    raise SystemExit

print()
print("=== JSJ012取得 ===")

url012 = "https://www.keirin.jp/pc/json"

response012 = requests.get(
    url012,
    params={
        "encp": encp,
        "type": "JSJ012"
    }
)

print("status:", response012.status_code)

data012 = response012.json()

print("resultCd:", data012.get("resultCd"))
print("message:", data012.get("message"))

with open(
    "053_result.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        data012,
        f,
        ensure_ascii=False,
        indent=2
    )

print()
print("保存先: 053_result.json")