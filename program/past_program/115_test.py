from playwright.sync_api import sync_playwright


def main():

    print("=== 115 競走結果モード復帰 JSJ012テスト ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="msedge"
        )

        context = browser.new_context()

        page = context.new_page()

        jsj012_found = False

        # --------------------------------------------------
        # 通信監視
        # --------------------------------------------------

        def handle_response(response):

            nonlocal jsj012_found

            if "JSJ012" not in response.url:
                return

            print()
            print("🔥🔥🔥 JSJ012発見！")
            print(response.url)
            print()

            jsj012_found = True

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
        print("確定結果ページを開いてください")
        print("確定済み開催を表示してください")
        print("1レースを表示してください")
        print()

        input(
            "準備できたらターミナルに戻ってEnter："
        )

        # --------------------------------------------------
        # 現在の競輪場を確認
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 現在の競輪場を確認")
        print("=" * 70)

        venue_elements = page.locator(
            "td.tdkeirin"
        )

        venue_count = venue_elements.count()

        print(
            "競輪場候補数:",
            venue_count
        )

        venues = []

        for i in range(venue_count):

            el = venue_elements.nth(i)

            try:

                text = el.inner_text().strip()

            except:
                continue

            try:

                onclick = (
                    el.get_attribute("onclick")
                    or ""
                )

            except:
                onclick = ""

            if not text:
                continue

            if "raKeirinjoClick" not in onclick:
                continue

            venues.append(
                {
                    "name": text,
                    "onclick": onclick
                }
            )

            print(
                "🔥 競輪場:",
                text,
                onclick
            )

        # --------------------------------------------------
        # 2番目の競輪場へ切替
        # --------------------------------------------------

        if len(venues) < 2:

            print()
            print("❌ 競輪場が2場見つかりません")

            input(
                "確認できたらEnter："
            )

            browser.close()

            return

        target_venue = venues[1]

        print()
        print("=" * 70)
        print("🔥 競輪場切替")
        print("=" * 70)

        print(
            "切替先:",
            target_venue["name"]
        )

        print(
            "ONCLICK:",
            target_venue["onclick"]
        )

        page.evaluate(
            target_venue["onclick"]
        )

        page.wait_for_timeout(3000)

        print()
        print("✅ 競輪場切替処理終了")

        # --------------------------------------------------
        # 競走結果ボタン確認
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 競走結果ボタン確認")
        print("=" * 70)

        result_button = page.locator(
            "#rctbn8"
        )

        print(
            "rctbn8数:",
            result_button.count()
        )

        if result_button.count() == 0:

            print(
                "❌ #rctbn8 が見つかりません"
            )

            input(
                "確認できたらEnter："
            )

            browser.close()

            return

        button_text = (
            result_button
            .first
            .inner_text()
            .strip()
        )

        button_class = (
            result_button
            .first
            .get_attribute("class")
            or ""
        )

        button_onclick = (
            result_button
            .first
            .get_attribute("onclick")
            or ""
        )

        print(
            "TEXT:",
            repr(button_text)
        )

        print(
            "CLASS:",
            repr(button_class)
        )

        print(
            "ONCLICK:",
            repr(button_onclick)
        )

        # --------------------------------------------------
        # 競走結果モードへ復帰
        # --------------------------------------------------

        print()
        print("🔥 競走結果ボタンをクリック")

        result_button.first.click()

        page.wait_for_timeout(3000)

        print(
            "✅ 競走結果ボタンクリック終了"
        )

        # --------------------------------------------------
        # 1R確認
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 1Rボタン確認")
        print("=" * 70)

        race_button = page.locator(
            "#hhRaceBtn1"
        )

        print(
            "1Rボタン数:",
            race_button.count()
        )

        if race_button.count() == 0:

            print(
                "❌ 1Rボタンが見つかりません"
            )

            input(
                "確認できたらEnter："
            )

            browser.close()

            return

        race_text = (
            race_button
            .first
            .inner_text()
            .strip()
        )

        print(
            "1R TEXT:",
            repr(race_text)
        )

        # --------------------------------------------------
        # JSJ012監視開始状態リセット
        # --------------------------------------------------

        jsj012_found = False

        print()
        print("=" * 70)
        print("🔥 1Rクリック")
        print("=" * 70)

        race_button.first.click()

        # --------------------------------------------------
        # JSJ012待機
        # --------------------------------------------------

        for _ in range(30):

            page.wait_for_timeout(500)

            if jsj012_found:
                break

        # --------------------------------------------------
        # 結果
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 115テスト結果")
        print("=" * 70)

        if jsj012_found:

            print()
            print("🔥🔥🔥 JSJ012取得成功！")
            print()
            print(
                "競輪場切替後に"
                "#rctbn8をクリックすると"
                "JSJ012が復活しました"
            )

        else:

            print()
            print("❌ JSJ012取得失敗")
            print()
            print(
                "#rctbn8クリックだけでは"
                "JSJ012は復活しませんでした"
            )

        print()
        print("=" * 70)

        input(
            "確認できたらEnter："
        )

        browser.close()


if __name__ == "__main__":
    main()