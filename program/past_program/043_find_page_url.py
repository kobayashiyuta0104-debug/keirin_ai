import json

HAR_FILE = "result_page.har"

with open(
    HAR_FILE,
    "r",
    encoding="utf-8"
) as f:
    har = json.load(f)

entries = har["log"]["entries"]

print("=== keirin URL一覧 ===")

count = 0

for entry in entries:

    request = entry.get("request", {})
    url = request.get("url", "")

    if "keirin.jp" not in url:
        continue

    if "/pc/json" in url:
        continue

    count += 1

    print()
    print("番号:", count)
    print("URL:", url)

print()
print("件数:", count)