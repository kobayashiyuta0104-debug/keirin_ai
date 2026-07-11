import json
import requests

INPUT_FILE = "067_race_encp_map.json"
OUTPUT_FILE = "070_real_results.json"

BASE_URL = "https://www.keirin.jp/pc/json"

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "user-agent": "Mozilla/5.0",
    "x-requested-with": "XMLHttpRequest",
}


with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    encp_list = json.load(f)


results = []

print("=== 070 実結果抽出開始 ===")
print("encp候補数:", len(encp_list))


for item in encp_list:

    order = item.get("順番")
    encp = item.get("encp")

    print()
    print("=" * 70)
    print("順番:", order)
    print("encp:", encp)

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

    try:

        data = response.json()

    except Exception as e:

        print("JSONエラー:", e)
        continue


    print("resultCd:", data.get("resultCd"))


    tyakujyun_list = data.get(
        "tyakujyunItemSubData",
        []
    )

    harai_sub = data.get(
        "haraiGakuSubData",
        {}
    )

    rh3_list = harai_sub.get(
        "RH3HaraiGakuDispItemSubData",
        []
    )


    print("着順件数:", len(tyakujyun_list))
    print("3連単件数:", len(rh3_list))


    sanrentan = []

    for rh3 in rh3_list:

        sanrentan.append({
            "組番": rh3.get("kumiBan"),
            "払戻金": rh3.get("haraiGaku"),
            "人気": rh3.get("ninki")
        })


    result = {
        "順番": order,
        "encp": encp,
        "着順": tyakujyun_list,
        "3連単": sanrentan
    }

    results.append(result)


    for rh3 in sanrentan:

        print(
            "3連単:",
            rh3.get("組番"),
            "払戻金:",
            rh3.get("払戻金"),
            "人気:",
            rh3.get("人気")
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
print("=== 070 抽出終了 ===")
print("保存件数:", len(results))
print("保存先:", OUTPUT_FILE)