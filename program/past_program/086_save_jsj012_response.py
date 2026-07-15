from playwright.sync_api import sync_playwright
import json


OUTPUT_FILE = "086_jsj012_response.json"


def main():

    found = 0

    with sync_playwright() as p:

        browser = p.chromium.launch(
            channel="msedge",
            headless=False
        )

        page = browser.new_page()

        def handle_response(response):

            nonlocal found

            url = response.url

            if "type=JSJ012" not in url:
                return

            found += 1

            print()
            print("🔥 JSJ012発見！")
            print("URL:", url)
            print("STATUS:", response.status)

            try:

                text = response.text()

                print("レスポンス文字数:", len(text))

                with open(
                    OUTPUT_FILE,
                    "w",
                    encoding="utf-8"
                ) as f:
                    f.write(text)

                print()
                print("🔥 保存成功！")
                print("保存先:", OUTPUT_FILE)

                try:

                    data = json.loads(text)

                    print("JSON解析成功！")
                    print("JSON型:", type(data).__name__)

                except Exception as e:

                    print("JSON解析失敗:", e)

            except Exception as e:

                print("レスポンス取得失敗:", e)

        page.on("response", handle_response)

        print("=== JSJ012保存監視開始 ===")

        page.goto(
            "https://www.keirin.jp/",
            wait_until="domcontentloaded"
        )

        print()
        print("🔥 ブラウザを操作してください")
        print("確定結果が見られるページまで進んでください")
        print()
        print("終わったらターミナルでEnter")

        input()

        print()
        print("JSJ012発見数:", found)

        browser.close()


if __name__ == "__main__":
    main()