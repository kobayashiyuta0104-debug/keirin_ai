import requests

url = "https://keirin.jp/pc/top"

response = requests.get(url)

html = response.text
words = [
    "keirinjoName",
    "raceNum",
    "kaisaiDate",
    "denTime",
    "naibu",
    "keirinCd",
    "code"
]

for word in words:
    print(word,html.find(word))