import json
import base64
import requests

HAR_FILE = "result_page.har"
URL = "https://www.keirin.jp/pc/json"


def search_value(obj, key_name):
    if isinstance(obj, dict):
        for key, value in obj.items():

            if key == key_name:
                return value

            result = search_value(value, key_name)

            if result is not None:
                return result

    elif isinstance(obj, list):
        for item in obj:

            result = search_value(item, key_name)

            if result is not None:
                return result

    return None


print("=== HARからJSJ001を検索 ===")

with open(HAR_FILE, "r", encoding="utf-8") as f:
    har = json.load(f)

encp = None

for entry in har["log"]["entries"]:

    request = entry.get("request", {})
    url = request.get("url", "")

    if "type=JSJ001" not in url:
        continue

    content = entry.get("response", {}).get("content", {})

    text = content.get("text", "")

    if content.get("encoding") == "base64":
        text = base64.b64decode(text).decode(
            "utf-8",
            errors="ignore"
        )

    if not text:
        continue

    try:
        data = json.loads(text)
    except:
        continue

    found = search_value(data, "encSelParaR")

    if found:
        encp = found

        print("発見！")
        print("encp:", encp)

        break


if not encp:
    print("encSelParaR が見つかりません")
    raise SystemExit


print()
print("=== JSJ012 自動取得 ===")

params = {
    "encp": encp,
    "type": "JSJ012"
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    URL,
    params=params,
    headers=headers,
    timeout=30
)

print("ステータス:", response.status_code)

result = response.json()

print("resultCd:", result.get("resultCd"))
print("message:", result.get("message"))


with open(
    "036_result.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        result,
        f,
        ensure_ascii=False,
        indent=2
    )


print()
print("保存成功！")
print("保存先: 036_result.json")