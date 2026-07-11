import requests
url="http://www.python.org"
response=requests.get(url)
print(response.text)
