import requests
import json

URL = "https://www.keirin.jp/pc/json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# result_page.har で取得成功した JSJ012
params = {
    "type": "JSJ012",
    "encp": "hXAFouF_EW8oCnSpPo40hpDA7JUrLLgRjYqdhgPAgTM"
}

print("=== 結果JSON自動取得テスト ===")

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
print()

if data.get("resultCd") == 0:

    print("=== 着順データ ===")

    tyaku_data = data.get("tyakujyunItemSubData", [])

    for item in tyaku_data:
        print(item)

    print()
    print("=== 払戻データ ===")

    harai_data = data.get("haraiGakuSubData", [])

    for item in harai_data:
        print(item)

    with open(
        "034_result.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("保存成功！")
    print("保存先: 034_result.json")

else:

    print("結果取得失敗")