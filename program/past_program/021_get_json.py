import requests

url = "https://www.keirin.jp/pc/json"

params = {
    "encp": "hXAFouF_EW8oCnSpPo40hpDA7JUrLLgRjYqdhgPAgTM",
    "type": "JSJ012"
}

response = requests.get(url, params=params)

print("ステータス:", response.status_code)
print("URL:", response.url)
print()
print(response.text[:1000])

with open("result.json", "w", encoding="utf-8") as f:
    f.write(response.text)

print("result.json に保存しました！")