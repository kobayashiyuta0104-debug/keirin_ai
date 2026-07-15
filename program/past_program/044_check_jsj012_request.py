import json

HAR_FILE = "result_page.har"

with open(
    HAR_FILE,
    "r",
    encoding="utf-8"
) as f:
    har = json.load(f)

entries = har["log"]["entries"]

print("=== JSJ012通信 詳細確認 ===")

count = 0

for entry in entries:

    request = entry.get("request", {})
    url = request.get("url", "")

    if "JSJ012" not in url:
        continue

    count += 1

    print()
    print("==============================")
    print("発見:", count)
    print("==============================")

    print()
    print("METHOD:")
    print(request.get("method"))

    print()
    print("URL:")
    print(url)

    print()
    print("QUERY STRING:")

    for item in request.get("queryString", []):
        print(
            item.get("name"),
            "=",
            item.get("value")
        )

    print()
    print("HEADERS:")

    for item in request.get("headers", []):
        print(
            item.get("name"),
            ":",
            item.get("value")
        )

    print()
    print("POST DATA:")
    print(
        request.get("postData")
    )

print()
print("JSJ012発見数:", count)