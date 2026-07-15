import json

INPUT_FILE = "kaisai_list.json"

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

print("=== 079 kaisai_list 構造確認 ===")
print("TYPE:", type(data).__name__)
print("件数:", len(data))

print()

for i, item in enumerate(data[:3], 1):

    print("=" * 70)
    print("番号:", i)
    print("TYPE:", type(item).__name__)

    if isinstance(item, dict):

        print("KEY一覧:")
        print(list(item.keys()))

        print()
        print("中身:")
        print(
            json.dumps(
                item,
                ensure_ascii=False,
                indent=2
            )
        )

print()
print("=== 079 確認終了 ===")