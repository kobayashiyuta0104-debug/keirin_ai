import json


JSON_FILE = "087_jsj012_response.json"


def walk(obj, path="root"):

    if isinstance(obj, dict):

        for key, value in obj.items():

            print(
                f"{path}.{key}"
                f" | type={type(value).__name__}"
            )

            if isinstance(value, (dict, list)):
                walk(
                    value,
                    f"{path}.{key}"
                )

            else:
                print(
                    "    値:",
                    repr(value)
                )

    elif isinstance(obj, list):

        for i, item in enumerate(obj):

            print(
                f"{path}[{i}]"
                f" | type={type(item).__name__}"
            )

            if isinstance(item, (dict, list)):
                walk(
                    item,
                    f"{path}[{i}]"
                )

            else:
                print(
                    "    値:",
                    repr(item)
                )


def main():

    with open(
        JSON_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    print("=" * 80)
    print("JSJ012 JSON 全構造調査")
    print("=" * 80)

    print()
    print("トップ型:", type(data).__name__)

    if isinstance(data, dict):

        print(
            "トップキー:",
            list(data.keys())
        )

    print()
    print("=" * 80)
    print("全階層表示")
    print("=" * 80)
    print()

    walk(data)

    print()
    print("=" * 80)
    print("調査終了")
    print("=" * 80)


if __name__ == "__main__":
    main()