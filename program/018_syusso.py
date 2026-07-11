import requests

# 例：函館1R
url = "https://keirin.jp/pc/racecard?keirinCd=11&kaisaiBi=20260703&raceNo=1"

response = requests.get(url)

print(response.status_code)
print(response.url)
print(response.text[:1000])