from playwright.sync_api import sync_playwright


def main():

    print("=== 119 競走結果JS直接実行 JSJ012テスト ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="msedge"
        )

        context = browser.new_context()
        page = context.new_page()

        jsj012_found = False

        # --------------------------------------------------
        # JSJ012監視
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
        print("確定結果ページを開いてください")
        print("確定済み開催を表示してください")
        print("1レースを表示してください")
        print()

        input(
            "準備できたらターミナルに戻ってEnter："
        )

        # --------------------------------------------------
        # 競輪場抽出
        # --------------------------------------------------

        venue_elements = page.locator(
            "td.tdkeirin"
        )

        venues = []

        for i in range(
            venue_elements.count()
        ):

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
            print("❌ 競輪場が2場ありません")

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

        page.evaluate(
            target_venue["onclick"]
        )

        page.wait_for_timeout(3000)

        print(
            "✅ 競輪場切替処理終了"
        )

        # --------------------------------------------------
        # JS関数確認
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 btnClickOfFrame確認")
        print("=" * 70)

        function_type = page.evaluate(
            "typeof btnClickOfFrame"
        )

        print(
            "typeof btnClickOfFrame:",
            function_type
        )

        if function_type != "function":

            print()
            print(
                "❌ btnClickOfFrame が存在しません"
            )

            input(
                "確認できたらEnter："
            )

            browser.close()
            return

        # --------------------------------------------------
        # 競走結果モード直接実行
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 競走結果モード直接実行")
        print("=" * 70)

        try:

            page.evaluate(
                "btnClickOfFrame('PJ0326')"
            )

            print(
                "✅ btnClickOfFrame直接実行成功"
            )

        except Exception as e:

            print()
            print(
                "❌ btnClickOfFrame直接実行失敗"
            )

            print(
                repr(e)
            )

            input(
                "確認できたらEnter："
            )

            browser.close()
            return

        # --------------------------------------------------
        # 1R待機
        # --------------------------------------------------

        print()
        print("🔥 1Rボタン出現待機")

        race_button = page.locator(
            "#hhRaceBtn1"
        )

        race_found = False

        for wait_count in range(40):

            page.wait_for_timeout(500)

            count = race_button.count()

            print(
                f"待機 {wait_count + 1}: "
                f"1R数={count}"
            )

            if count > 0:

                try:

                    text = (
                        race_button
                        .first
                        .inner_text()
                        .strip()
                    )

                    print(
                        "1R候補TEXT:",
                        repr(text)
                    )

                    if text == "1R":

                        race_found = True
                        break

                except:
                    pass

        if not race_found:

            print()
            print(
                "❌ 1Rボタンが出現しません"
            )

            input(
                "確認できたらEnter："
            )

            browser.close()
            return

        print()
        print("🔥 1R確認成功")

        # --------------------------------------------------
        # JSJ012フラグリセット
        # --------------------------------------------------

        jsj012_found = False

        # --------------------------------------------------
        # 1Rクリック
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 1Rクリック")
        print("=" * 70)

        race_button.first.click()

        # --------------------------------------------------
        # JSJ012待機
        # --------------------------------------------------

        for wait_count in range(40):

            page.wait_for_timeout(500)

            print(
                f"JSJ012待機 {wait_count + 1}: "
                f"{jsj012_found}"
            )

            if jsj012_found:
                break

        # --------------------------------------------------
        # 結果
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 119テスト結果")
        print("=" * 70)

        print(
            "切替先:",
            target_venue["name"]
        )

        print(
            "btnClickOfFrame:",
            function_type
        )

        print(
            "1R出現:",
            race_found
        )

        print(
            "JSJ012:",
            jsj012_found
        )

        if jsj012_found:

            print()
            print(
                "🔥🔥🔥 JSJ012取得成功！"
            )

        else:

            print()
            print(
                "❌ JSJ012取得失敗"
            )

        print()
        print("=" * 70)

        input(
            "確認できたらEnter："
        )

        browser.close()


if __name__ == "__main__":
    main()