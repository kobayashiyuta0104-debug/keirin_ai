import requests
import json

URL = "https://www.keirin.jp/pc/json"

encp = "hXAFouF_EW8oCnSpPo40hpDA7JUrLLgRjYqdhgPAgTM"

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

data = response.json()

print("resultCd:", data.get("resultCd"))
print("message:", data.get("message"))

with open(
    "auto_result.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        data,
        f,
        ensure_ascii=False,
        indent=2
    )

print("保存成功！")
print("保存先: auto_result.json")