import json

HAR_FILE = "result_page.har"

with open(HAR_FILE, "r", encoding="utf-8") as f:
    har = json.load(f)

entry = har["log"]["entries"][0]

request = entry.get("request", {})
response = entry.get("response", {})

print("=== HAR番号0 詳細 ===")
print()
print("METHOD:", request.get("method"))
print("URL:", request.get("url"))
print("STATUS:", response.get("status"))
print()
print("=== REQUEST HEADERS ===")

for h in request.get("headers", []):
    print(h.get("name"), ":", h.get("value"))

print()
print("=== RESPONSE CONTENT ===")

content = response.get("content", {})

print("mimeType:", content.get("mimeType"))
print("encoding:", content.get("encoding"))
print("text長さ:", len(content.get("text", "")))

print()
print("=== 終了 ===")