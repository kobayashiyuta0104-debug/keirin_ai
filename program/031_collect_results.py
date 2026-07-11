import requests
import json
import time

URL = "https://www.keirin.jp/pc/json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

with open(
    "kaisai_list.json",
    "r",
    encoding="utf-8"
) as f:
    kaisai_list = json.load(f)


for race in kaisai_list:

    name = race.get("bkname")
    encp = race.get("raceUrlPrm")

    print()
    print("====================")
    print("開催場:", name)
    print("====================")

    params = {
        "encp": encp,
        "type": "JSJ012"
    }

    try:

        response = requests.get(
            URL,
            params=params,
            headers=headers,
            timeout=30
        )

        print("ステータス:", response.status_code)

        data = response.json()

        print("resultCd:", data.get("resultCd"))
        print("message:", data.get("message"))

        if data.get("resultCd") == 0:

            filename = f"result_{name}.json"

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            print("保存成功:", filename)

    except Exception as e:

        print("エラー:", e)

    time.sleep(1)


print()
print("全開催場の取得終了！")