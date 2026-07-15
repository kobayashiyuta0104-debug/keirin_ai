import json

INPUT_FILE = "071_race_results.json"
OUTPUT_FILE = "074_joined_results.json"

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    races = json.load(f)


results = []

print("=== 074 着順・払戻結合開始 ===")
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

        if tyaku is None or syaban is None:
            continue

        finish_map[str(tyaku)] = str(syaban)


    first = finish_map.get("1")
    second = finish_map.get("2")
    third = finish_map.get("3")

    sanrentan_order = None
    check_key = None

    if first and second and third:

        sanrentan_order = (
            first
            + "="
            + second
            + "="
            + third
        )

        check_key = "=".join(
            sorted(
                [first, second, third],
                key=int
            )
        )


    payout_list = race.get(
        "3連単",
        []
    )

    matched_payout = None
    matched_kumiban = None
    matched_ninki = None


    for payout in payout_list:

        if not isinstance(payout, dict):
            continue

        kumiban = str(
            payout.get("組番", "")
        )

        if kumiban == check_key:

            matched_payout = payout.get(
                "払戻金"
            )

            matched_kumiban = kumiban

            matched_ninki = payout.get(
                "人気"
            )

            break


    result = {
        "レース": race.get("レース"),
        "順番": race.get("順番"),
        "1着": first,
        "2着": second,
        "3着": third,
        "3連単着順": sanrentan_order,
        "照合キー": check_key,
        "払戻側組番": matched_kumiban,
        "3連単払戻金": matched_payout,
        "人気": matched_ninki
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
        "照合キー:",
        result["照合キー"]
    )
    print(
        "払戻側組番:",
        result["払戻側組番"]
    )
    print(
        "3連単払戻金:",
        result["3連単払戻金"]
    )
    print(
        "人気:",
        result["人気"]
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
print("=== 074 結合終了 ===")
print("保存件数:", len(results))
print("保存先:", OUTPUT_FILE)