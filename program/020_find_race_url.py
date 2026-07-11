import requests

url = "https://keirin.jp/pc/top"

response = requests.get(url)

html = response.text

index = html.find("/pc/racecard")

print(index)
print()
print(html[index-500:index+1000])