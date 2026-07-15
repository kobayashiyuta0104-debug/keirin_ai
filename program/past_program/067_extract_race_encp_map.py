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

print("=== 067 レースencp候補抽出開始 ===")

current_encp = None
group_no = 0
results = []

for i, entry in enumerate(entries):

    request = entry.get("request", {})
    url = request.get("url", "")

    if "keirin.jp/pc/json" not in url:
        continue

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    type_value = query.get("type", [""])[0]
    encp = query.get("encp", [""])[0]

    if type_value != "JSJ012":
        continue

    if not encp:
        continue

    if encp != current_encp:

        group_no += 1
        current_encp = encp

        results.append({
            "順番": group_no,
            "HAR位置": i,
            "encp": encp
        })

        print()
        print("=" * 70)
        print("順番:", group_no)
        print("HAR位置:", i)
        print("encp:", encp)

print()
print("=== 067 抽出終了 ===")
print("encp候補数:", len(results))

with open(
    "067_race_encp_map.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        ensure_ascii=False,
        indent=2
    )

print("保存先: 067_race_encp_map.json")