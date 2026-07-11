from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        found = 0
        request_count = 0

        def check_request(request):
            nonlocal found
            nonlocal request_count

            request_count += 1

            url = request.url
            method = request.method

            try:
                post_data = request.post_data or ""
            except Exception:
                post_data = ""

            target_text = (
                url
                + "\n"
                + post_data
            ).upper()

            if (
                "JSJ012" in target_text
                or "ENCP" in target_text
            ):
                found += 1

                print()
                print("=" * 100)
                print("🔥 怪しい通信発見！")
                print("発見番号:", found)
                print("全通信番号:", request_count)
                print("METHOD:", method)
                print("URL:", url)

                print()
                print("=== POST DATA ===")
                print(post_data[:5000])

                print("=" * 100)
                print()

        page.on(
            "request",
            check_request
        )

        print("=== 全通信監視開始 ===")

        page.goto(
    "https://www.keirin.jp/",
    wait_until="domcontentloaded"
)

        print("ページタイトル:", page.title())
        print()
        print("🔥 ブラウザを操作してください")
        print("前にJSJ012を確認した結果ページまで進んでください")
        print()
        print("URL・POST DATAから")
        print("JSJ012 / encp を監視中...")
        print()
        print("操作が終わったらターミナルでEnter")

        input()

        print()
        print("=== 結果 ===")
        print("全通信数:", request_count)
        print("怪しい通信発見数:", found)

        browser.close()


if __name__ == "__main__":
    main()