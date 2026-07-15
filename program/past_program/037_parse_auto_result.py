import json

FILE = "036_result.json"

with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


keywords = [
    "tyaku",
    "syaban",
    "harai",
    "sensyu",
    "race",
    "jun",
    "gaku"
]


def search(obj, path="root"):

    if isinstance(obj, dict):

        for key, value in obj.items():

            new_path = f"{path}.{key}"

            key_lower = key.lower()

            if any(word in key_lower for word in keywords):

                print()
                print("==============================")
                print("発見キー:", key)
                print("場所:", new_path)
                print("型:", type(value).__name__)
                print("中身:")

                if isinstance(value, (dict, list)):
                    print(
                        json.dumps(
                            value,
                            ensure_ascii=False,
                            indent=2
                        )[:3000]
                    )

                else:
                    print(value)

            search(value, new_path)

    elif isinstance(obj, list):

        for i, item in enumerate(obj):
            search(item, f"{path}[{i}]")


print("=== 036_result.json 自動解析開始 ===")

search(data)

print()
print("=== 解析終了 ===")