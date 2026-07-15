import json
from urllib.parse import urlparse, parse_qs

HAR_FILE = "result_page.har"

with open(
    HAR_FILE,
    "r",
    encoding="utf-8"
) as f:
    har = json.load(f)

entries = har.get("log", {}).get("entries", [])

print("=== 063 HAR レース切替候補検索 ===")
print("全リクエスト数:", len(entries))

found = 0

for i, entry in enumerate(entries):

    request = entry.get("request", {})
    url = request.get("url", "")
    method = request.get("method", "")

    if "keirin.jp" not in url:
        continue

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    post_text = (
        request
        .get("postData", {})
        .get("text", "")
    )

    target_words = [
        "selRaceNo",
        "raceNo",
        "race_no",
        "encSelParaR",
        "encp",
        "JSJ001",
        "JSJ012",
    ]

    combined = url + "\n" + post_text

    if not any(
        word.lower() in combined.lower()
        for word in target_words
    ):
        continue

    found += 1

    print()
    print("=" * 70)
    print("候補番号:", found)
    print("HAR位置:", i)
    print("METHOD:", method)
    print("URL:", url)

    print("--- QUERY ---")

    if query:
        for key, value in query.items():
            print(key, "=", value)
    else:
        print("なし")

    print("--- POST DATA ---")

    if post_text:
        print(post_text[:3000])
    else:
        print("なし")

print()
print("=== 063 検索終了 ===")
print("候補数:", found)