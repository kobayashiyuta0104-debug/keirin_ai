import json
import requests

KAISAI_FILE = "kaisai_list.json"
OUTPUT_FILE = "057_all_results.json"

BASE_URL = "https://www.keirin.jp/pc/json"

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "ja,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
    "referer": "https://www.keirin.jp/pc/racelive",
    "user-agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36",
}

with open(
    KAISAI_FILE,
    "r",
    encoding="utf-8"
) as f:
    races = json.load(f)


all_results = []

print("=== 057 全レース取得テスト開始 ===")
print("開催数:", len(races))


for race in races:

    name = race.get("bkname", "")
    race_url_prm = race.get("raceUrlPrm", "")

    print()
    print("========================")
    print("競輪場:", name)

    for race_no in range(1, 13):

        print()
        print(name, str(race_no) + "R")

        params001 = {
            "encp": race_url_prm,
            "type": "JSJ001"
        }

        try:
            response001 = requests.get(
                BASE_URL,
                params=params001,
                headers=HEADERS,
                timeout=20
            )

            data001 = response001.json()

            print(
                "JSJ001:",
                response001.status_code,
                data001.get("resultCd")
            )

            c0201data = data001.get("C0201data", {})

            if not isinstance(c0201data, dict):
                print("C0201dataなし")
                continue

            enc_sel_para_r = c0201data.get(
                "encSelParaR",
                ""
            )

            if not enc_sel_para_r:
                print("encSelParaRなし")
                continue


            params012 = {
                "encp": enc_sel_para_r,
                "type": "JSJ012"
            }

            response012 = requests.get(
                BASE_URL,
                params=params012,
                headers=HEADERS,
                timeout=20
            )

            data012 = response012.json()

            print(
                "JSJ012:",
                response012.status_code,
                data012.get("resultCd")
            )

            all_results.append({
                "競輪場": name,
                "レース": race_no,
                "JSJ001": data001,
                "JSJ012": data012
            })

        except Exception as e:

            print("エラー:", e)


with open(
    OUTPUT_FILE,
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
print("=== 057 取得終了 ===")
print("保存件数:", len(all_results))
print("保存先:", OUTPUT_FILE)