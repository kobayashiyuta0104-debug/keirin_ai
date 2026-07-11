from playwright.sync_api import sync_playwright


def main():

    print("=== 112 競輪場正確抽出テスト ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="msedge"
        )

        context = browser.new_context()
        page = context.new_page()

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded"
        )

        print()
        print("🔥 Edgeを操作してください")
        print()
        print("確定結果ページを開いてください")
        print("確定済みレースがある開催を表示してください")
        print("1レースを表示してください")
        print()

        input(
            "準備できたらターミナルに戻ってEnter："
        )

        print()
        print("=" * 70)
        print("🔥 競輪場抽出開始")
        print("=" * 70)

        # --------------------------------------------------
        # tdkeirinだけ取得
        # --------------------------------------------------

        venue_elements = page.locator(
            "td.tdkeirin"
            "[onclick^='raKeirinjoClick']"
        )

        venue_count = venue_elements.count()

        print()
        print(
            "🔥 候補要素数:",
            venue_count
        )
        print()

        venues = []

        for i in range(venue_count):

            el = venue_elements.nth(i)

            try:

                text = (
                    el
                    .inner_text()
                    .strip()
                )

                onclick = (
                    el
                    .get_attribute(
                        "onclick"
                    )
                )

            except Exception as e:

                print(
                    "❌ 要素取得失敗:",
                    e
                )

                continue

            if not text:
                continue

            if not onclick:
                continue

            try:

                index = int(
                    onclick
                    .replace(
                        "raKeirinjoClick(",
                        ""
                    )
                    .replace(
                        ")",
                        ""
                    )
                )

            except Exception as e:

                print(
                    "❌ INDEX取得失敗:",
                    text,
                    onclick,
                    e
                )

                continue

            venues.append(
                {
                    "name": text,
                    "index": index
                }
            )

            print(
                f"🔥 競輪場発見: "
                f"{text} "
                f"INDEX: {index}"
            )

        print()
        print("=" * 70)
        print("🔥 抽出結果")
        print("=" * 70)

        print(
            "競輪場数:",
            len(venues)
        )

        print()

        for venue in venues:

            print(
                venue["name"],
                "INDEX:",
                venue["index"]
            )

        print()
        print("=" * 70)
        print("🔥 112テスト終了")
        print("=" * 70)

        input(
            "確認できたらEnter："
        )

        browser.close()


if __name__ == "__main__":
    main()