from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs


def main():

    print("=== 092 JSJ012 リクエスト調査 ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()

        found = False

        def handle_request(request):

            nonlocal found

            if "JSJ012" not in request.url:
                return

            if found:
                return

            found = True

            print()
            print("🔥 JSJ012発見！")
            print()
            print("【URL】")
            print(request.url)

            print()
            print("【METHOD】")
            print(request.method)

            print()
            print("【POST DATA】")
            print(request.post_data)

            print()
            print("【HEADERS】")

            for key, value in request.headers.items():
                print(
                    f"{key}: {value}"
                )

            print()
            print("【URL QUERY】")

            parsed = urlparse(request.url)

            query = parse_qs(
                parsed.query
            )

            for key, value in query.items():

                print(
                    f"{key} = {value}"
                )

            print()
            print("🔥 調査完了")

        context.on(
            "request",
            handle_request
        )

        page = context.new_page()

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded"
        )

        print()
        print("🔥 ブラウザを操作してください")
        print("091と同じ確定結果ページまで進んでください")
        print()
        print("JSJ012の送信内容を調査します")

        while found is False:

            page.wait_for_timeout(500)

        page.wait_for_timeout(1000)

        browser.close()

        print()
        print("=== 092 調査終了 ===")


if __name__ == "__main__":
    main()