import json
import base64

HAR_FILE = "result_page.har"

TARGET = "hXAFouF_EW8oCnSpPo40hpDA7JUrLLgRjYqdhgPAgTM"


with open(
    HAR_FILE,
    "r",
    encoding="utf-8"
) as f:

    har = json.load(f)


entries = har["log"]["entries"]


print("=== encp 発生元検索開始 ===")

found = 0


for i, entry in enumerate(entries):

    request = entry.get("request", {})
    response = entry.get("response", {})

    url = request.get("url", "")

    content = response.get("content", {})

    text = content.get("text", "")

    encoding = content.get("encoding", "")


    if not text:
        continue


    if encoding == "base64":

        try:

            text = base64.b64decode(
                text
            ).decode(
                "utf-8",
                errors="ignore"
            )

        except Exception:
            continue


    if TARGET in text:

        found += 1

        print()
        print("========================")
        print("発見:", found)
        print("HAR番号:", i)
        print("URL:", url)

        position = text.find(TARGET)

        start = max(
            0,
            position - 300
        )

        end = min(
            len(text),
            position + len(TARGET) + 300
        )

        print()
        print("=== 前後の内容 ===")

        print(
            text[start:end]
        )


print()
print("========================")
print("発見数:", found)
print("=== 検索終了 ===")