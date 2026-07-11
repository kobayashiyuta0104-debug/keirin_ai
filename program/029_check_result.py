import json

with open("result.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== result.json トップキー ===")

for key in data.keys():
    print(key)

print()
print("resultCd:", data.get("resultCd"))
print("message:", data.get("message"))
print()

print("=== 結果系キー確認 ===")

words = [
    "harai",
    "tyaku",
    "race",
    "syaban",
    "sensyu"
]

for key in data.keys():
    lower_key = key.lower()

    if any(word in lower_key for word in words):
        print(key)