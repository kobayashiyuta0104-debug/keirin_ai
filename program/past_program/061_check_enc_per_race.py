import json

INPUT_FILE = "057_all_results.json"

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    races = json.load(f)

print("=== 061 レース別 enc 確認 ===")
print("データ数:", len(races))

for i, race in enumerate(races):

    name = race.get("競輪場")
    race_no = race.get("レース")

    jsj001 = race.get("JSJ001", {})
    jsj012 = race.get("JSJ012", {})

    c0201 = jsj001.get("C0201data", {})

    enc_r = c0201.get("encSelParaR")
    sel_race = c0201.get("selRaceNo")

    print("=" * 60)
    print("番号:", i + 1)
    print("競輪場:", name)
    print("保存レース:", race_no)
    print("selRaceNo:", sel_race)
    print("encSelParaR:", enc_r)

    harai_sub = jsj012.get(
        "haraiGakuSubData",
        {}
    )

    rh3 = harai_sub.get(
        "RH3HaraiGakuDispItemSubData",
        []
    )

    if rh3:
        print("3連単:", rh3[0].get("kumiBan"))
        print("払戻金:", rh3[0].get("haraiGaku"))
    else:
        print("3連単: なし")

print()
print("=== 061 確認終了 ===")