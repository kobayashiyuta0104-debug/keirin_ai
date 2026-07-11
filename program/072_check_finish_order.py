import json

INPUT_FILE = "071_race_results.json"

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    races = json.load(f)


print("=== 072 着順構造確認開始 ===")
print("レース数:", len(races))


for race in races:

    print()
    print("=" * 70)

    print("レース:", race.get("レース"))
    print("順番:", race.get("順番"))

    finish_list = race.get(
        "着順",
        []
    )

    print("着順件数:", len(finish_list))


    for i, finish in enumerate(
        finish_list,
        start=1
    ):

        print()
        print("--- 着順データ", i, "---")

        if isinstance(finish, dict):

            print("KEY:", list(finish.keys()))

            for key, value in finish.items():

                print(
                    key,
                    ":",
                    value
                )

        else:

            print("VALUE:", finish)


print()
print("=== 072 確認終了 ===")