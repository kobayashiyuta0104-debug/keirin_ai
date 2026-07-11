import json
from urllib.parse import urlparse, parse_qs

HAR_FILE = "race_switch.har"

with open(
    HAR_FILE,
    "r",
    encoding="utf-8"
) as f:
    har = json.load(f)

entries = har.get("log", {}).get("entries", [])

print("=== 064 レース切替HAR解析開始 ===")
print("全リクエスト数:", len(entries))

found = 0

for i, entry in enumerate(entries):

    request = entry.get("request", {})
    response = entry.get("response", {})

    url = request.get("url", "")
    method = request.get("method", "")

    if "keirin.jp" not in url:
        continue

    if "/pc/json" not in url:
        continue

    found += 1

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    post_data = request.get("postData", {})
    post_text = post_data.get("text", "")

    print()
    print("=" * 80)
    print("番号:", found)
    print("HAR位置:", i)
    print("METHOD:", method)
    print("STATUS:", response.get("status"))
    print("URL:", url)

    print("--- QUERY ---")

    for key, value in query.items():
        print(key, "=", value)

    print("--- POST PARAMS ---")

    params = post_data.get("params", [])

    if params:
        for param in params:
            print(
                param.get("name"),
                "=",
                param.get("value")
            )
    else:
        print("なし")

    print("--- POST TEXT ---")

    if post_text:
        print(post_text[:2000])
    else:
        print("なし")

print()
print("=== 064 解析終了 ===")
print("JSON通信数:", found)