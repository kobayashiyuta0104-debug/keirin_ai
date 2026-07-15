import requests
import json
import csv
import os
import time


KAISAI_FILE = "kaisai_list.json"
CSV_FILE = "race_results.csv"
URL = "https://www.keirin.jp/pc/json"


headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "ja,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
    "referer": "https://www.keirin.jp/pc/racelive",
    "user-agent": (
        "Mozilla/5.0 (Linux; Android 15; Pixel 9) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/149.0.0.0 Mobile Safari/537.36"
    ),
}


def find_sanrentan(obj):

    results = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            if key == "RT3HaraiGakuDispItemSubData":

                if isinstance(value, list):

                    for item in value:

                        if not isinstance(item, dict):
                            continue

                        kumi = item.get("kumiBan")
                        harai = item.get("haraiGaku")
                        ninki = item.get("ninki")

                        if kumi and harai:

                            results.append(
                                (
                                    kumi,
                                    harai,
                                    ninki
                                )
                            )

            results.extend(
                find_sanrentan(value)
            )

    elif isinstance(obj, list):

        for item in obj:

            results.extend(
                find_sanrentan(item)
            )

    return results


print("=== 046 全レース自動取得開始 ===")


with open(
    KAISAI_FILE,
    "r",
    encoding="utf-8"
) as f:

    races = json.load(f)


print("レース数:", len(races))


existing = set()


if os.path.exists(CSV_FILE):

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.reader(f)

        next(reader, None)

        for row in reader:

            if len(row) >= 3:

                existing.add(
                    (
                        row[0],
                        row[1]
                    )
                )


session = requests.Session()


file_exists = os.path.exists(CSV_FILE)


with open(
    CSV_FILE,
    "a",
    encoding="utf-8-sig",
    newline=""
) as csvfile:

    writer = csv.writer(csvfile)


    if not file_exists:

        writer.writerow(
            [
                "開催場",
                "レース",
                "式別",
                "組み合わせ",
                "払戻金",
                "人気"
            ]
        )


    for index, race in enumerate(races, 1):

        name = race.get("bkname", "")
        race_num = race.get("raceNum", "")
        encp = race.get("raceUrlPrm", "")


        print()
        print("========================")
        print(
            index,
            name,
            race_num
        )


        race_key = (
            name,
            race_num
        )


        if race_key in existing:

            print("保存済み → スキップ")
            continue


        if not encp:

            print("encpなし → スキップ")
            continue


        params = {
            "encp": encp,
            "type": "JSJ012"
        }


        try:

            response = session.get(
                URL,
                params=params,
                headers=headers,
                timeout=30
            )


            print(
                "ステータス:",
                response.status_code
            )


            result = response.json()


            print(
                "resultCd:",
                result.get("resultCd")
            )


            if result.get("resultCd") != 0:

                print(
                    "結果未取得:",
                    result.get("message")
                )

                continue


            sanrentan = find_sanrentan(result)


            if not sanrentan:

                print("3連単結果なし")
                continue


            print(
                "3連単発見:",
                len(sanrentan),
                "件"
            )


            for kumi, harai, ninki in sanrentan:

                print(
                    kumi,
                    harai,
                    ninki
                )


                writer.writerow(
                    [
                        name,
                        race_num,
                        "3連単",
                        kumi,
                        harai,
                        ninki
                    ]
                )


            csvfile.flush()


            existing.add(race_key)


            print("保存成功！")


        except Exception as e:

            print(
                "エラー:",
                e
            )


        time.sleep(1)


print()
print("=== 全レース取得終了 ===")
print(
    "保存先:",
    CSV_FILE
)