from playwright.sync_api import sync_playwright


def main():

    print("=== 111 raKeirinjoClick 要素調査テスト ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="msedge"
        )

        context = browser.new_context()
        page = context.new_page()

        # --------------------------------------------------
        # KEIRIN.JPを開く
        # --------------------------------------------------

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

        # --------------------------------------------------
        # raKeirinjoClick要素取得
        # --------------------------------------------------

        print()
        print("=" * 80)
        print("🔥 raKeirinjoClick 要素調査開始")
        print("=" * 80)

        elements = page.locator(
            "[onclick^='raKeirinjoClick']"
        )

        count = elements.count()

        print()
        print(
            "要素数:",
            count
        )
        print()

        # --------------------------------------------------
        # 全要素表示
        # --------------------------------------------------

        for i in range(count):

            el = elements.nth(i)

            print("=" * 80)
            print(
                f"🔥 ELEMENT #{i}"
            )

            try:

                text = el.inner_text().strip()

            except Exception as e:

                text = (
                    f"取得失敗: {e}"
                )

            try:

                onclick = el.get_attribute(
                    "onclick"
                )

            except Exception as e:

                onclick = (
                    f"取得失敗: {e}"
                )

            try:

                tag_name = el.evaluate(
                    "el => el.tagName"
                )

            except Exception as e:

                tag_name = (
                    f"取得失敗: {e}"
                )

            try:

                class_name = el.get_attribute(
                    "class"
                )

            except Exception as e:

                class_name = (
                    f"取得失敗: {e}"
                )

            try:

                element_id = el.get_attribute(
                    "id"
                )

            except Exception as e:

                element_id = (
                    f"取得失敗: {e}"
                )

            try:

                parent_tag = el.evaluate(
                    "el => "
                    "el.parentElement "
                    "? el.parentElement.tagName "
                    ": null"
                )

            except Exception as e:

                parent_tag = (
                    f"取得失敗: {e}"
                )

            try:

                parent_class = el.evaluate(
                    "el => "
                    "el.parentElement "
                    "? el.parentElement.className "
                    ": null"
                )

            except Exception as e:

                parent_class = (
                    f"取得失敗: {e}"
                )

            print(
                "TEXT:",
                repr(text)
            )

            print(
                "ONCLICK:",
                repr(onclick)
            )

            print(
                "TAG:",
                repr(tag_name)
            )

            print(
                "CLASS:",
                repr(class_name)
            )

            print(
                "ID:",
                repr(element_id)
            )

            print(
                "PARENT TAG:",
                repr(parent_tag)
            )

            print(
                "PARENT CLASS:",
                repr(parent_class)
            )

        # --------------------------------------------------
        # 終了
        # --------------------------------------------------

        print()
        print("=" * 80)
        print("🔥 111 調査終了")
        print("=" * 80)

        input(
            "確認できたらEnter："
        )

        browser.close()


if __name__ == "__main__":
    main()