import json

INPUT_FILE = "067_race_encp_map.json"

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    encp_list = json.load(f)


print("=== 075 払戻グループ調査開始 ===")
print("encp候補数:", len(encp_list))


for index, item in enumerate(encp_list):

    encp = item.get("encp")

    print()
    print("=" * 80)
    print("順番:", index + 1)
    print("encp:", encp)

    # 070で保存したデータを確認
    with open(
        "070_real_results.json",
        "r",
        encoding="utf-8"
    ) as f:
        real_results = json.load(f)

    if index >= len(real_results):
        print("対応データなし")
        continue

    race = real_results[index]

    print("トップKEY:")
    print(list(race.keys()))

    print()
    print("--- 払戻関連KEYを全部表示 ---")

    for key, value in race.items():

        key_lower = str(key).lower()

        if (
            "harai" in key_lower
            or "gaku" in key_lower
            or "rh" in key_lower
        ):
            print()
            print("KEY:", key)
            print("TYPE:", type(value).__name__)
            print("VALUE:")
            print(
                json.dumps(
                    value,
                    ensure_ascii=False,
                    indent=2
                )[:5000]
            )


print()
print("=== 075 調査終了 ===")