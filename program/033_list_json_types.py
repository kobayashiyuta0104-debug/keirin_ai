import json
from urllib.parse import urlparse, parse_qs

HAR_FILE = "www.keirin.jp.har"

with open(HAR_FILE, "r", encoding="utf-8") as f:
    har = json.load(f)

entries = har["log"]["entries"]

count = 0

for entry in entries:
    request = entry.get("request", {})
    url = request.get("url", "")

    if "/pc/json" not in url:
        continue

    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    count += 1

    print(
        count,
        "| type:",
        params.get("type"),
        "| encp:",
        params.get("encp")
    )

print()
print("JSON通信数:", count)

print()
print("=== JSJ012だけ検索 ===")

for entry in entries:
    request = entry.get("request", {})
    url = request.get("url", "")

    if "/pc/json" not in url:
        continue

    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    if params.get("type") == ["JSJ012"]:
        print("type:", params.get("type"))
        print("encp:", params.get("encp"))
        print("URL:", url)