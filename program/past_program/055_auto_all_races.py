import json
import requests


KAISAI_FILE = "kaisai_list.json"


with open(
    KAISAI_FILE,
    "r",
    encoding="utf-8"
) as f:

    races = json.load(f)


headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "ja,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
    "referer": "https://www.keirin.jp/pc/racelive",
    "user-agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36",
}


all_results = []


print("=== 全レース自動取得開始 ===")
print("レース数:", len(races))


for i, race in enumerate(
    races,
    start=1
):

    print()
    print("====================")

    race_name = race.get(
        "bkname",
        ""
    )

    race_no = race.get(
        "raceNum",
        ""
    )

    encp = race.get(
        "raceUrlPrm",
        ""
    )


    print(
        i,
        race_name,
        race_no
    )


    if not encp:

        print("raceUrlPrmなし")

        continue


    jsj001_url = (
        "https://www.keirin.jp"
        "/pc/json"
        "?encp="
        + encp
        + "&type=JSJ001"
    )


    try:

        response = requests.get(
            jsj001_url,
            headers=headers,
            timeout=30
        )


        print(
            "JSJ001 status:",
            response.status_code
        )


        jsj001_data = response.json()


        print(
            "JSJ001 resultCd:",
            jsj001_data.get("resultCd")
        )


        c0201 = jsj001_data.get(
            "C0201data"
        )


        if not isinstance(c0201, dict):

            print("C0201dataなし")

            continue


        enc_sel_para_r = c0201.get(
            "encSelParaR"
        )


        if not enc_sel_para_r:

            print("encSelParaRなし")

            continue


        jsj012_url = (
            "https://www.keirin.jp"
            "/pc/json"
            "?encp="
            + enc_sel_para_r
            + "&type=JSJ012"
        )


        response = requests.get(
            jsj012_url,
            headers=headers,
            timeout=30
        )


        print(
            "JSJ012 status:",
            response.status_code
        )


        jsj012_data = response.json()


        print(
            "JSJ012 resultCd:",
            jsj012_data.get("resultCd")
        )


        all_results.append({

            "race_name": race_name,

            "race_no": race_no,

            "jsj001": jsj001_data,

            "jsj012": jsj012_data

        })


    except Exception as e:

        print(
            "エラー:",
            e
        )


with open(
    "055_all_races.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_results,
        f,
        ensure_ascii=False,
        indent=2
    )


print()
print("=== 全レース取得終了 ===")

print(
    "取得成功数:",
    len(all_results)
)

print(
    "保存先: 055_all_races.json"
)