import json

INPUT_FILE = "071_race_results.json"
OUTPUT_FILE = "073_finish_order.json"

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    races = json.load(f)


results = []

print("=== 073 着順抽出開始 ===")
print("レース数:", len(races))


for race in races:

    finish_list = race.get(
        "着順",
        []
    )

    finish_map = {}

    for finish in finish_list:

        if not isinstance(finish, dict):
            continue

        tyaku = finish.get("tyaku")
        syaban = finish.get("syaban")

        if tyaku is None:
            continue

        if syaban is None:
            continue

        finish_map[str(tyaku)] = str(syaban)


    first = finish_map.get("1")
    second = finish_map.get("2")
    third = finish_map.get("3")

    sanrentan = None

    if first and second and third:

        sanrentan = (
            first
            + "="
            + second
            + "="
            + third
        )


    result = {
        "レース": race.get("レース"),
        "順番": race.get("順番"),
        "1着": first,
        "2着": second,
        "3着": third,
        "3連単着順": sanrentan,
        "3連単払戻金": race.get(
            "3連単"
        )
    }

    results.append(result)


    print()
    print("=" * 70)
    print("レース:", result["レース"])
    print("順番:", result["順番"])
    print("1着:", result["1着"])
    print("2着:", result["2着"])
    print("3着:", result["3着"])
    print(
        "3連単着順:",
        result["3連単着順"]
    )
    print(
        "保存済み3連単:",
        result["3連単払戻金"]
    )


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        ensure_ascii=False,
        indent=2
    )


print()
print("=== 073 抽出終了 ===")
print("保存件数:", len(results))
print("保存先:", OUTPUT_FILE)