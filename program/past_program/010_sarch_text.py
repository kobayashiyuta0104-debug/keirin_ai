import requests
url = "https://www.keirin.jp/pc/top"
response = requests.get(url)
html = response.text
print("開催" in html)
print("函館" in html)
print("青森" in html)
print("立川" in html)
print("平塚" in html)