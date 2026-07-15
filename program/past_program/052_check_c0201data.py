import json
import base64

HAR_FILE = "result_page.har"

with open(
    HAR_FILE,
    "r",
    encoding="utf-8"
) as f:
    har = json.load(f)

entry = har["log"]["entries"][0]

content = entry["response"]["content"]

text = content.get("text", "")

if content.get("encoding") == "base64":
    text = base64.b64decode(
        text
    ).decode(
        "utf-8"
    )

data = json.loads(text)

c0201 = data.get("C0201data", {})

print("=== C0201data 全内容 ===")
print()

print(
    json.dumps(
        c0201,
        ensure_ascii=False,
        indent=2
    )
)

print()
print("=== キー一覧 ===")

for key in c0201.keys():
    print(key)