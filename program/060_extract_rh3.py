import json

INPUT_FILE = "057_all_results.json"
OUTPUT_FILE = "060_rh3_results.json"

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    races = json.load(f)

results = []

print("=== 060 3連単 RH3 抽出開始 ===")
print("全データ数:", len(races))


for race in races:

    jsj012 = race.get("JSJ012", {})

    harai_sub = jsj012.get(
        "haraiGakuSubData",
        {}
    )

    rh3_list = harai_sub.get(
        "RH3HaraiGakuDispItemSubData",
        []
    )

    if not rh3_list:
        continue

    for rh3 in rh3_list:

        kumi = rh3.get("kumiBan")
        harai = rh3.get("haraiGaku")
        ninki = rh3.get("ninki")

        result = {
            "競輪場": race.get("競輪場"),
            "レース": race.get("レース"),
            "3連単": kumi,
            "払戻金": harai,
            "人気": ninki
        }

        results.append(result)

        print("=" * 50)
        print("競輪場:", race.get("競輪場"))
        print("レース:", race.get("レース"))
        print("3連単:", kumi)
        print("払戻金:", harai)
        print("人気:", ninki)


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
print("=== 060 抽出終了 ===")
print("3連単結果数:", len(results))
print("保存先:", OUTPUT_FILE)