import json

FILE = "result_page.har"

with open(FILE, "r", encoding="utf-8") as f:
    har = json.load(f)

entries = har["log"]["entries"]

print("=== encSelParaR検索 ===")

count = 0

for entry in entries:
    response = entry.get("response", {})
    content = response.get("content", {})
    text = content.get("text", "")

    if not text:
        continue

    if "encSelParaR" in text:
        count += 1

        print()
        print("発見:", count)

        request = entry.get("request", {})
        print("URL:", request.get("url"))

        try:
            data = json.loads(text)

            def search(obj):
                if isinstance(obj, dict):
                    for key, value in obj.items():

                        if key == "encSelParaR":
                            print("encSelParaR:", value)

                        search(value)

                elif isinstance(obj, list):
                    for item in obj:
                        search(item)

            search(data)

        except Exception as e:
            print("JSON解析エラー:", e)

print()
print("発見数:", count)