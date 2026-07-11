from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        found = 0

        def check_response(response):
            nonlocal found

            url = response.url

            if "JSJ012" in url.upper():
                found += 1

                print()
                print("=" * 80)
                print("🔥 JSJ012発見！")
                print("番号:", found)
                print("STATUS:", response.status)
                print("URL:", url)

                try:
                    print("CONTENT-TYPE:", response.headers.get("content-type"))
                except Exception as e:
                    print("HEADER取得失敗:", e)

                try:
                    body = response.text()

                    print()
                    print("=== RESPONSE先頭2000文字 ===")
                    print(body[:2000])

                except Exception as e:
                    print("RESPONSE取得失敗:", e)

                print("=" * 80)
                print()

        page.on(
            "response",
            check_response
        )

        print("=== ブラウザ起動 ===")

        page.goto(
            "https://www.keirin.jp/pc/racelive",
            wait_until="domcontentloaded"
        )

        print("ページタイトル:", page.title())
        print()
        print("🔥 ブラウザを操作してください")
        print("結果ページなどを自由に押してOK")
        print("JSJ012通信を自動監視中...")
        print()
        print("終了するときはターミナルでEnter")

        input()

        print()
        print("JSJ012発見数:", found)

        browser.close()


if __name__ == "__main__":
    main()