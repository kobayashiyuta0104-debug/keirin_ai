from playwright.sync_api import sync_playwright


def main():

    print("=== 093 JSJ012 複数レース調査 ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()

        found_urls = []

        def handle_response(response):

            if "JSJ012" not in response.url:
                return

            if response.url in found_urls:
                return

            found_urls.append(response.url)

            print()
            print("=" * 70)
            print(f"🔥 JSJ012 #{len(found_urls)} 発見")
            print("=" * 70)

            print("URL:")
            print(response.url)

            print()
            print("ページURL:")
            print(response.request.frame.url)

            print()
            print("REFERER:")
            print(
                response.request.headers.get(
                    "referer",
                    ""
                )
            )

            try:

                data = response.json()

                racers = data.get(
                    "tyakujyunItemSubData",
                    []
                )

                print()
                print("【着順】")

                for racer in racers:

                    tyaku = racer.get("tyaku", "")
                    syaban = racer.get("syaban", "")
                    name = racer.get("sensyuName", "")

                    if tyaku in ["1", "2", "3"]:

                        print(
                            f"{tyaku}着 "
                            f"{syaban}番 "
                            f"{name}"
                        )

            except Exception as e:

                print(
                    "JSON取得失敗:",
                    e
                )

            print()
            print(
                f"現在 {len(found_urls)} 件取得"
            )

        context.on(
            "response",
            handle_response
        )

        page = context.new_page()

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded"
        )

        print()
        print("🔥 ブラウザを操作してください")
        print()
        print("同じ開催場の確定結果を")
        print("違うレースで3レース開いてください")
        print()
        print("例：7R → 8R → 9R")
        print()
        print("JSJ012を3種類取得したら自動終了します")

        while len(found_urls) < 3:

            page.wait_for_timeout(500)

        print()
        print("=" * 70)
        print("🔥 3レース取得完了")
        print("=" * 70)

        for i, url in enumerate(
            found_urls,
            start=1
        ):

            print()
            print(f"【JSJ012 #{i}】")
            print(url)

        browser.close()

        print()
        print("=== 093 調査終了 ===")


if __name__ == "__main__":
    main()