import json


JSON_FILE = "045_result.json"


with open(
    JSON_FILE,
    "r",
    encoding="utf-8"
) as f:

    data = json.load(f)


def search(obj, path="root"):

    if isinstance(obj, dict):

        for key, value in obj.items():

            if key == "encSelParaK":

                print()
                print("========================")
                print("encSelParaK 発見！")
                print("場所:", path)
                print("値:", value)
                print("========================")

            search(
                value,
                f"{path}.{key}"
            )

    elif isinstance(obj, list):

        for i, item in enumerate(obj):

            search(
                item,
                f"{path}[{i}]"
            )


print("=== encSelParaK 検索開始 ===")

search(data)

print()
print("=== 検索終了 ===")