import json

INPUT_FILE = "057_all_results.json"
OUTPUT_FILE = "058_sanrentan_results.json"

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    races = json.load(f)


results = []


def search_sanrentan(obj, path="root"):

    found = []

    if isinstance(obj, dict):

        if "haraigaku" in obj and "kumiBan" in obj:

            found.append({
                "path": path,
                "kumiBan": obj.get("kumiBan"),
                "haraigaku": obj.get("haraigaku"),
                "ninki": obj.get("ninki")
            })

        for key, value in obj.items():

            found.extend(
                search_sanrentan(
                    value,
                    f"{path}.{key}"
                )
            )

    elif isinstance(obj, list):

        for i, value in enumerate(obj):

            found.extend(
                search_sanrentan(
                    value,
                    f"{path}[{i}]"
                )
            )

    return found


print("=== 058 3連単検索開始 ===")
print("全データ数:", len(races))


for race in races:

    name = race.get("競輪場", "")
    race_no = race.get("レース", "")

    data012 = race.get("JSJ012", {})

    found = search_sanrentan(data012)

    if found:

        print()
        print("========================")
        print(name, str(race_no) + "R")
        print("候補数:", len(found))

        for item in found:

            print(
                item["kumiBan"],
                item["haraigaku"],
                item["ninki"]
            )

        results.append({
            "競輪場": name,
            "レース": race_no,
            "3連単候補": found
        })


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
print("=== 058 検索終了 ===")
print("3連単候補ありレース:", len(results))
print("保存先:", OUTPUT_FILE)