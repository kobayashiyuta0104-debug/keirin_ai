import json
import requests
from urllib.parse import urlparse, parse_qs


HAR_FILE = "result_page.har"


with open(
    HAR_FILE,
    "r",
    encoding="utf-8"
) as f:
    har = json.load(f)


entries = har["log"]["entries"]

jsj001_list = []


for entry in entries:

    request = entry.get("request", {})

    url = request.get("url", "")

    if "keirin.jp/pc/json" not in url:
        continue

    query = parse_qs(
        urlparse(url).query
    )

    type_value = query.get("type", [""])[0]


    if type_value != "JSJ001":
        continue


    response = entry.get("response", {})

    content = response.get(
        "content",
        {}
    )

    text = content.get("text", "")


    if not text:
        continue


    try:

        data = json.loads(text)

    except:

        continue


    c0201 = data.get("C0201data")

    if not isinstance(c0201, dict):
        continue


    jsj001_list.append(c0201)


print("=== JSJ001取得完了 ===")

print(
    "レース数:",
    len(jsj001_list)
)


headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "ja,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
    "referer": "https://www.keirin.jp/pc/racelive",
    "user-agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Mobile Safari/537.36",
}


results = []


for i, race in enumerate(
    jsj001_list,
    start=1
):

    encp = race.get("encSelParaR")

    if not encp:
        continue


    race_name = race.get(
        "joName",
        ""
    )

    race_no = race.get(
        "selRaceNo",
        ""
    )


    print()
    print(
        "===================="
    )

    print(
        i,
        race_name,
        race_no
    )


    url = (
        "https://www.keirin.jp"
        "/pc/json"
        "?encp="
        + encp
        + "&type=JSJ012"
    )


    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        print(
            "status:",
            response.status_code
        )


        data = response.json()


        print(
            "resultCd:",
            data.get("resultCd")
        )


        results.append({
            "race": race,
            "result": data
        })


    except Exception as e:

        print(
            "エラー:",
            e
        )


with open(
    "054_all_results.json",
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
print(
    "=== 全取得終了 ==="
)

print(
    "保存先: 054_all_results.json"
)