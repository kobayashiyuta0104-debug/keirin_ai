import json
import requests

INPUT_FILE = "067_race_encp_map.json"
OUTPUT_FILE = "077_real_sanrentan_results.json"

BASE_URL = "https://www.keirin.jp/pc/json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    races = json.load(f)

results = []

print("=== 077 本物の3連単 抽出開始 ===")
print("encp候補数:", len(races))

for race in races:

    order = race.get("順番")
    encp = race.get("encp")

    print()
    print("=" * 70)
    print("順番:", order)
    print("encp:", encp)

    try:

        response = requests.get(
            BASE_URL,
            params={
                "encp": encp,
                "type": "JSJ012"
            },
            headers=HEADERS,
            timeout=30
        )

        print("status:", response.status_code)

        data = response.json()

        payout_root = data.get(
            "haraiGakuSubData",
            {}
        )

        sanrentan_list = payout_root.get(
            "RT3HaraiGakuDispItemSubData",
            []
        )

        finish_list = data.get(
            "tyakujyunItemSubData",
            []
        )

        print("着順件数:", len(finish_list))
        print("3連単件数:", len(sanrentan_list))

        finish_sorted = sorted(
            finish_list,
            key=lambda x: int(x.get("tyaku", 999))
        )

        first = None
        second = None
        third = None

        for item in finish_sorted:

            tyaku = str(item.get("tyaku", ""))

            if tyaku == "1":
                first = item.get("syaban")

            elif tyaku == "2":
                second = item.get("syaban")

            elif tyaku == "3":
                third = item.get("syaban")

        finish_order = None

        if first and second and third:
            finish_order = (
                f"{first}-{second}-{third}"
            )

        print("着順:", finish_order)

        for sanrentan in sanrentan_list:

            kumi = sanrentan.get("kumiBan")
            harai = sanrentan.get("haraiGaku")
            ninki = sanrentan.get("ninki")

            print(
                "3連単:",
                kumi,
                "払戻金:",
                harai,
                "人気:",
                ninki
            )

            results.append({
                "順番": order,
                "encp": encp,
                "着順": finish_order,
                "3連単": kumi,
                "払戻金": harai,
                "人気": ninki
            })

    except Exception as e:

        print("エラー:", e)

print()
print("=== 077 抽出終了 ===")
print("保存件数:", len(results))

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

print("保存先:", OUTPUT_FILE)