import json

INPUT_FILE = "057_all_results.json"

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    races = json.load(f)


def search_keys(obj, path="root"):

    if isinstance(obj, dict):

        for key, value in obj.items():

            key_text = str(key).lower()
            value_text = str(value).lower()

            targets = [
                "3連単",
                "三連単",
                "払戻",
                "harai",
                "kumi",
                "sanrentan",
                "trifecta",
            ]

            if any(
                target.lower() in key_text
                or target.lower() in value_text
                for target in targets
            ):
                print("=" * 60)
                print("場所:", path)
                print("KEY:", key)
                print("VALUE:", value)

            search_keys(
                value,
                f"{path}.{key}"
            )

    elif isinstance(obj, list):

        for i, value in enumerate(obj):

            search_keys(
                value,
                f"{path}[{i}]"
            )


print("=== 059 JSJ012 キー検索開始 ===")
print("全データ数:", len(races))

for i, race in enumerate(races):

    print()
    print("=" * 60)
    print("レース番号:", i + 1)

    search_keys(
        race,
        f"race[{i}]"
    )

print()
print("=== 059 検索終了 ===")