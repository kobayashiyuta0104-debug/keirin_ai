from playwright.sync_api import sync_playwright


def main():

    print("=== 109 JSJ通信比較テスト ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="msedge"
        )

        context = browser.new_context()
        page = context.new_page()

        capture_mode = False

        # --------------------------------------------------
        # 通信監視
        # --------------------------------------------------

        def handle_response(response):

            if not capture_mode:
                return

            url = response.url

            if "keirin.jp" not in url:
                return

            if "JSJ" not in url:
                return

            print()
            print("🌐 JSJ通信発見")
            print(url)

        context.on(
            "response",
            handle_response
        )

        # --------------------------------------------------
        # KEIRIN.JP
        # --------------------------------------------------

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded"
        )

        print()
        print("🔥 Edgeを操作してください")
        print()
        print("107と同じように")
        print("確定結果ページを開いてください")
        print("確定済みレースがある開催を表示")
        print("1レースを表示してください")
        print()

        input(
            "準備できたらターミナルに戻ってEnter："
        )

        # --------------------------------------------------
        # 手動状態でレースクリック
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 TEST 1")
        print("現在の状態でレースボタンをクリック")
        print("=" * 70)

        capture_mode = True

        page.locator(
            "#hhRaceBtn1"
        ).first.click()

        page.wait_for_timeout(5000)

        capture_mode = False

        input(
            "TEST 1確認後 Enter："
        )

        # --------------------------------------------------
        # 開催候補取得
        # --------------------------------------------------

        print()
        print("🔥 開催候補を探します")

        venue_elements = page.locator(
            "[onclick^='raKeirinjoClick']"
        )

        venue_count = venue_elements.count()

        venues = []

        for i in range(venue_count):

            el = venue_elements.nth(i)

            try:

                text = el.inner_text().strip()

                onclick = el.get_attribute(
                    "onclick"
                )

            except:
                continue

            if not text:
                continue

            if not onclick:
                continue

            if "raKeirinjoClick" not in onclick:
                continue

            try:

                index = int(
                    onclick
                    .replace(
                        "raKeirinjoClick(",
                        ""
                    )
                    .replace(")", "")
                )

            except:
                continue

            key = (
                text,
                index
            )

            if key not in [
                (
                    venue["name"],
                    venue["index"]
                )
                for venue in venues
            ]:

                venues.append(
                    {
                        "name": text,
                        "index": index
                    }
                )

        print()
        print("🔥 開催候補")

        for venue in venues:

            print(
                venue["name"],
                "INDEX:",
                venue["index"]
            )

        if len(venues) < 2:

            print()
            print("❌ 開催候補が2つありません")

            browser.close()
            return

        # --------------------------------------------------
        # 別開催へ切替
        # --------------------------------------------------

        target_venue = venues[1]

        print()
        print("=" * 70)
        print("🔥 TEST 2")
        print(
            "開催切替:",
            target_venue["name"]
        )
        print("=" * 70)

        capture_mode = True

        page.evaluate(
            f"raKeirinjoClick("
            f"{target_venue['index']}"
            f")"
        )

        page.wait_for_timeout(5000)

        capture_mode = False

        input(
            "TEST 2確認後 Enter："
        )

        # --------------------------------------------------
        # 開催切替後レースクリック
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 TEST 3")
        print("開催切替後に1Rクリック")
        print("=" * 70)

        capture_mode = True

        page.locator(
            "#hhRaceBtn1"
        ).first.click()

        page.wait_for_timeout(5000)

        capture_mode = False

        print()
        print("=" * 70)
        print("🔥 109テスト終了")
        print("=" * 70)

        input(
            "確認できたらEnter："
        )

        browser.close()


if __name__ == "__main__":
    main()