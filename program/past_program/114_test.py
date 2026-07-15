from playwright.sync_api import sync_playwright


def main():

    print("=== 114 確定結果モード要素調査テスト ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="msedge"
        )

        context = browser.new_context()
        page = context.new_page()

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
        print("確定済みレースがある開催を表示してください")
        print("1レースを表示してください")
        print()

        input(
            "準備できたらターミナルに戻ってEnter："
        )

        # --------------------------------------------------
        # クリック可能要素調査
        # --------------------------------------------------

        print()
        print("=" * 80)
        print("🔥 クリック要素調査開始")
        print("=" * 80)

        elements = page.locator(
            "a, button, input, "
            "[onclick]"
        )

        count = elements.count()

        print()
        print(
            "要素数:",
            count
        )
        print()

        hit_count = 0

        # --------------------------------------------------
        # 結果関係候補だけ表示
        # --------------------------------------------------

        keywords = [
            "結果",
            "確定",
            "一覧",
            "払戻",
            "レース結果",
            "result",
            "Result"
        ]

        for i in range(count):

            el = elements.nth(i)

            try:

                text = (
                    el
                    .inner_text()
                    .strip()
                )

            except:
                text = ""

            try:

                value = (
                    el
                    .get_attribute("value")
                    or ""
                )

            except:
                value = ""

            try:

                onclick = (
                    el
                    .get_attribute("onclick")
                    or ""
                )

            except:
                onclick = ""

            try:

                href = (
                    el
                    .get_attribute("href")
                    or ""
                )

            except:
                href = ""

            search_text = (
                text
                + " "
                + value
                + " "
                + onclick
                + " "
                + href
            )

            if not any(
                keyword in search_text
                for keyword in keywords
            ):
                continue

            hit_count += 1

            try:

                tag_name = el.evaluate(
                    "el => el.tagName"
                )

            except:
                tag_name = ""

            try:

                class_name = (
                    el
                    .get_attribute("class")
                    or ""
                )

            except:
                class_name = ""

            try:

                element_id = (
                    el
                    .get_attribute("id")
                    or ""
                )

            except:
                element_id = ""

            print("=" * 80)

            print(
                f"🔥 HIT #{hit_count}"
            )

            print(
                "ELEMENT INDEX:",
                i
            )

            print(
                "TEXT:",
                repr(text)
            )

            print(
                "VALUE:",
                repr(value)
            )

            print(
                "ONCLICK:",
                repr(onclick)
            )

            print(
                "HREF:",
                repr(href)
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

        # --------------------------------------------------
        # 終了
        # --------------------------------------------------

        print()
        print("=" * 80)
        print(
            "🔥 候補数:",
            hit_count
        )
        print("=" * 80)

        print()
        print("🔥 114テスト終了")

        input(
            "確認できたらEnter："
        )

        browser.close()


if __name__ == "__main__":
    main()