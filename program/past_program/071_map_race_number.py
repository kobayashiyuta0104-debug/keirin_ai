import json

MAP_FILE = "067_race_encp_map.json"
RESULT_FILE = "070_real_results.json"
OUTPUT_FILE = "071_race_results.json"


with open(
    MAP_FILE,
    "r",
    encoding="utf-8"
) as f:
    encp_map = json.load(f)


with open(
    RESULT_FILE,
    "r",
    encoding="utf-8"
) as f:
    real_results = json.load(f)


result_by_encp = {}

for result in real_results:

    encp = result.get("encp")

    result_by_encp[encp] = result


final_results = []


print("=== 071 レース番号対応開始 ===")
print("encp数:", len(encp_map))


for item in encp_map:

    order = item.get("順番")
    encp = item.get("encp")

    race_no = order

    result = result_by_encp.get(
        encp,
        {}
    )

    sanrentan_list = result.get(
        "3連単",
        []
    )


    final_item = {
        "レース": race_no,
        "順番": order,
        "encp": encp,
        "着順": result.get("着順", []),
        "3連単": sanrentan_list
    }

    final_results.append(final_item)


    print()
    print("=" * 70)

    print("順番:", order)
    print("対応レース:", race_no)

    print("encp:", encp)

    print(
        "着順件数:",
        len(result.get("着順", []))
    )

    print(
        "3連単件数:",
        len(sanrentan_list)
    )


    for sanrentan in sanrentan_list:

        print(
            "3連単:",
            sanrentan.get("組番"),
            "払戻金:",
            sanrentan.get("払戻金"),
            "人気:",
            sanrentan.get("人気")
        )


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        final_results,
        f,
        ensure_ascii=False,
        indent=2
    )


print()
print("=== 071 対応終了 ===")
print("保存件数:", len(final_results))
print("保存先:", OUTPUT_FILE)