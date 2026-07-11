import json
import base64
from urllib.parse import urlparse, parse_qs

HAR_FILE = "www.keirin.jp.har"

with open(HAR_FILE, "r", encoding="utf-8") as f:
    har = json.load(f)

entries = har["log"]["entries"]

count = 0

for entry in entries:

    request = entry.get("request", {})
    response = entry.get("response", {})

    url = request.get("url", "")

    if "/pc/json" not in url:
        continue

    content = response.get("content", {})
    text = content.get("text", "")
    encoding = content.get("encoding")

    if not text:
        continue

    if encoding == "base64":
        try:
            text = base64.b64decode(text).decode(
                "utf-8",
                errors="ignore"
            )
        except Exception:
            continue

    keywords = [
        "haraiGakuSubData",
        "tyakujyunItemSubData"
    ]

    found = [
        word
        for word in keywords
        if word in text
    ]

    if not found:
        continue

    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    count += 1

    print()
    print("=== 結果JSON候補発見 ===")
    print("type:", params.get("type"))
    print("encp:", params.get("encp"))
    print("URL:", url)
    print("含まれるキー:")

    for word in found:
        print(" ", word)

print()
print("結果JSON候補数:", count)