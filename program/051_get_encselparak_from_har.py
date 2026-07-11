import json
import base64


HAR_FILE = "result_page.har"


with open(
    HAR_FILE,
    "r",
    encoding="utf-8"
) as f:

    har = json.load(f)


entry = har["log"]["entries"][0]

content = entry["response"]["content"]

text = content.get("text", "")


if content.get("encoding") == "base64":

    text = base64.b64decode(
        text
    ).decode(
        "utf-8"
    )


data = json.loads(text)


def search(obj, path="root"):

    if isinstance(obj, dict):

        for key, value in obj.items():

            if key == "encSelParaK":

                print()
                print("========================")
                print("encSelParaK 発見！")
                print("場所:", path)
                print("値:", value)
                print("========================")

            search(
                value,
                f"{path}.{key}"
            )

    elif isinstance(obj, list):

        for i, item in enumerate(obj):

            search(
                item,
                f"{path}[{i}]"
            )


print("=== HARレスポンス検索開始 ===")

search(data)

print()
print("=== 検索終了 ===")