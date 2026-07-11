import json

FILE = "036_result.json"

with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


harai_data = data.get("haraiGakuSubData", {})

print("=== haraiGakuSubData のキー ===")

for key in harai_data.keys():
    print(key)


print()
print("=== 払戻データ詳細 ===")

for key, value in harai_data.items():

    print()
    print("==============================")
    print("キー:", key)
    print("型:", type(value).__name__)

    if isinstance(value, list):

        print("件数:", len(value))

        for i, item in enumerate(value):

            print()
            print("---", i, "---")

            print(
                json.dumps(
                    item,
                    ensure_ascii=False,
                    indent=2
                )
            )

    else:

        print(
            json.dumps(
                value,
                ensure_ascii=False,
                indent=2
            )
        )