import requests
import csv
from pathlib import Path

BASE_DIR = Path(r"C:\競輪AI")
CSV_FILE = BASE_DIR / "race_results.csv"

url = "https://www.keirin.jp/pc/json"

params = {
    "encp": "hXAFouF_EW8oCnSpPo40hpDA7JUrLLgRjYqdhgPAgTM",
    "type": "JSJ012"
}


def parse_race_result(data):

    results = data["tyakujyunItemSubData"]

    first = results[0]["syaban"]
    second = results[1]["syaban"]
    third = results[2]["syaban"]

    sanrentan = data["haraiGakuSubData"]["RT3HaraiGakuDispItemSubData"][0]

    kumi = sanrentan["kumiBan"]

    harai = int(
        sanrentan["haraiGaku"].replace(",", "")
    )

    ninki = (
        sanrentan["ninki"]
        .replace("(", "")
        .replace(")", "")
    )

    if harai < 20000:
        label = "20000未満"

    elif harai < 50000:
        label = "20000-49999"

    else:
        label = "50000以上"

    return {
        "1着": first,
        "2着": second,
        "3着": third,
        "3連単": kumi,
        "払戻": harai,
        "人気": ninki,
        "荒れ分類": label
    }


print("KEIRIN.JPから取得中...")

response = requests.get(
    url,
    params=params,
    timeout=30
)

print("ステータス:", response.status_code)

response.raise_for_status()

data = response.json()

result = parse_race_result(data)

file_exists = CSV_FILE.exists()

with open(
    CSV_FILE,
    "a",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=result.keys()
    )

    if not file_exists:
        writer.writeheader()

    writer.writerow(result)


print()
print("=== 取得・解析成功 ===")

for key, value in result.items():

    if key == "払戻":
        print(f"{key}: {value}円")

    else:
        print(f"{key}: {value}")

print()
print("CSV保存成功！")
print("保存先:", CSV_FILE)