import json
from urllib.parse import urlparse, parse_qs

HAR_FILE = "result_page.har"

with open(
    HAR_FILE,
    "r",
    encoding="utf-8"
) as f:
    har = json.load(f)

entries = har["log"]["entries"]

target_index = None

for i, entry in enumerate(entries):

    request = entry.get("request", {})
    url = request.get("url", "")

    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    if params.get("type") == ["JSJ012"]:

        target_index = i
        break


if target_index is None:

    print("JSJ012が見つかりません")

else:

    print("=== JSJ012 発見 ===")
    print("位置:", target_index)
    print()

    start = max(
        0,
        target_index - 20
    )

    end = min(
        len(entries),
        target_index + 3
    )

    for i in range(start, end):

        entry = entries[i]

        request = entry.get(
            "request",
            {}
        )

        url = request.get(
            "url",
            ""
        )

        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        print(
            "--------------------"
        )

        print(
            "番号:",
            i
        )

        print(
            "URL:",
            url
        )

        if params:

            print(
                "type:",
                params.get("type")
            )

            print(
                "encp:",
                params.get("encp")
            )

        if i == target_index:

            print(
                "★★★ これがJSJ012 ★★★"
            )


print()
print("=== 終了 ===")