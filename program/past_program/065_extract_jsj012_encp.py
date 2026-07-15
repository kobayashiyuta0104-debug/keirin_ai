import json
from urllib.parse import urlparse, parse_qs

HAR_FILE = "race_switch.har"

with open(
    HAR_FILE,
    "r",
    encoding="utf-8"
) as f:
    har = json.load(f)

entries = har.get("log", {}).get("entries", [])

print("=== 065 JSJ012 encp抽出開始 ===")

results = []

for i, entry in enumerate(entries):

    request = entry.get("request", {})
    url = request.get("url", "")

    if "keirin.jp/pc/json" not in url:
        continue

    parsed = urlparse(url)
    query = parse_qs(parsed.query)

    type_value = query.get("type", [""])[0]

    if type_value != "JSJ012":
        continue

    encp = query.get("encp", [""])[0]

    response = entry.get("response", {})
    content = response.get("content", {})
    text = content.get("text", "")

    sel_race_no = None
    jo_name = None
    sanrentan = None
    haraigaku = None

    if text:
        try:
            data = json.loads(text)

            c0201 = data.get("C0201data", {})

            sel_race_no = c0201.get("selRaceNo")
            jo_name = c0201.get("joName")

            jsj012 = data.get("JSJ012", {})

            harai_sub = jsj012.get(
                "haraiGakuSubData",
                {}
            )

            rh3 = harai_sub.get(
                "RH3HaraiGakuDispItemSubData",
                []
            )

            if rh3:
                sanrentan = rh3[0].get("kumiBan")
                haraigaku = rh3[0].get("haraiGaku")

        except Exception:
            pass

    results.append({
        "har_position": i,
        "encp": encp,
        "selRaceNo": sel_race_no,
        "joName": jo_name,
        "sanrentan": sanrentan,
        "haraigaku": haraigaku,
    })

for no, result in enumerate(results, start=1):

    print()
    print("=" * 70)
    print("順番:", no)
    print("HAR位置:", result["har_position"])
    print("selRaceNo:", result["selRaceNo"])
    print("競輪場:", result["joName"])
    print("encp:", result["encp"])
    print("3連単:", result["sanrentan"])
    print("払戻金:", result["haraigaku"])

print()
print("=== 065 抽出終了 ===")
print("JSJ012件数:", len(results))
print(
    "encp種類数:",
    len(set(
        result["encp"]
        for result in results
    ))
)