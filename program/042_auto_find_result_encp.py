import json
import requests
import re

KAISAI_FILE = "kaisai_list.json"

with open(
    KAISAI_FILE,
    "r",
    encoding="utf-8"
) as f:
    races = json.load(f)

print("=== 結果encp自動検索開始 ===")
print("レース数:", len(races))
print()

for i, race in enumerate(races, start=1):

    name = race.get("bkname", "")
    race_num = race.get("raceNum", "")
    race_prm = race.get("raceUrlPrm", "")

    print(
        i,
        name,
        race_num
    )

    if not race_prm:
        print("raceUrlPrmなし")
        continue

    url = (
        "https://www.keirin.jp/pc/race/"
        "resultlist?"
        "raceUrlPrm="
        + race_prm
    )

    try:

        response = requests.get(
            url,
            timeout=30
        )

        print(
            "status:",
            response.status_code
        )

        text = response.text

        encps = re.findall(
            r'encp[=:]["\']?'
            r'([A-Za-z0-9_-]+)',
            text
        )

        print(
            "encp候補:",
            len(encps)
        )

        for encp in encps[:5]:
            print(
                " ",
                encp
            )

    except Exception as e:

        print(
            "エラー:",
            e
        )

    print()