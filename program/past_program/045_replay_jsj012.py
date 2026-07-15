import requests
import json

URL = "https://www.keirin.jp/pc/json"

ENCP = "hXAFouF_EW8oCnSpPo40hpDA7JUrLLgRjYqdhgPAgTM"

session = requests.Session()

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

params = {
    "encp": ENCP,
    "type": "JSJ012",
}

print("=== JSJ012 完全再現テスト ===")

response = session.get(
    URL,
    params=params,
    headers=headers,
    timeout=30,
)

print("ステータス:", response.status_code)
print("最終URL:", response.url)

try:
    result = response.json()

    print("resultCd:", result.get("resultCd"))
    print("message:", result.get("message"))

    with open(
        "045_result.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("保存成功！")
    print("保存先: 045_result.json")

except Exception as e:

    print("JSON変換失敗:", e)
    print(response.text[:1000])