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

print("=== 066 encp切替順確認開始 ===")

current_encp = None
group_no = 0

for i, entry in enumerate(entries):

    request = entry.get("request", {})
    url = request.get("url", "")

    if "keirin.jp/pc/json" not in url:
        continue

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    type_value = query.get("type", [""])[0]
    encp = query.get("encp", [""])[0]

    if not encp:
        continue

    if encp != current_encp:

        group_no += 1
        current_encp = encp

        print()
        print("=" * 70)
        print("切替グループ:", group_no)
        print("HAR位置:", i)
        print("encp:", encp)

    if type_value in [
        "JSJ001",
        "JSJ003",
        "JSJ004",
        "JSJ012"
    ]:
        print(
            "  HAR位置:",
            i,
            "type:",
            type_value
        )

print()
print("=== 066 確認終了 ===")
print("切替グループ数:", group_no)