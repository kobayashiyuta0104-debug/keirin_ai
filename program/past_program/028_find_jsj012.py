import json
from urllib.parse import urlparse, parse_qs

HAR_FILE = "www.keirin.jp.har"

with open(HAR_FILE, "r", encoding="utf-8") as f:
    har = json.load(f)

entries = har["log"]["entries"]

for i, entry in enumerate(entries, start=1):
    request = entry["request"]
    url = request["url"]

    if "/pc/json" not in url:
        continue

    response = entry.get("response", {})
    content = response.get("content", {})
    text = content.get("text", "")

    if not text:
        continue

    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    keywords = [
        "haraiGakuSubData",
        "tyakujyunItemSubData",
        "7110",
        "3-6-7"
    ]

    found = [word for word in keywords if word in text]

    if found:
        print("=== 結果JSON候補 発見 ===")
        print("HAR番号:", i)
        print("type:", params.get("type"))
        print("encp:", params.get("encp"))
        print("見つかった文字:", found)
        print("URL:", url)
        print()