from playwright.sync_api import sync_playwright


def main():

    print("=== 103 結果ボタン調査 ===")

    with sync_playwright() as p:

        browser = p.chromium.connect_over_cdp(
            "http://127.0.0.1:9222"
        )

        context = browser.contexts[0]

        # KEIRIN.JPのタブを探す
        page = None

        for p_page in context.pages:

            if "keirin.jp" in p_page.url.lower():
                page = p_page

        if page is None:
            print("❌ KEIRIN.JPのタブが見つかりません")
            return

        print()
        print("🔥 使用ページ")
        print(page.url)

        print()
        print("🔥 ブラウザを操作してください")
        print("確定済みレースを1つ表示してください")
        print()
        print("結果ボタンはまだ押さないでください")
        print()

        input("準備できたらEnter：")

        print()
        print("🔥 『結果』に関係ありそうな要素を調査します")
        print()

        elements = page.locator(
            "a, button, input, div, span, li, td"
        )

        count = elements.count()

        found_count = 0

        for i in range(count):

            el = elements.nth(i)

            try:

                text = el.inner_text().strip()

                value = el.get_attribute("value")
                href = el.get_attribute("href")
                onclick = el.get_attribute("onclick")
                name = el.get_attribute("name")
                element_id = el.get_attribute("id")
                class_name = el.get_attribute("class")

                check_text = " ".join(
                    [
                        text or "",
                        value or "",
                        href or "",
                        onclick or "",
                        name or "",
                        element_id or "",
                        class_name or "",
                    ]
                ).lower()

                if (
                    "結果" not in check_text
                    and "kekka" not in check_text
                    and "result" not in check_text
                ):
                    continue

                found_count += 1

                print("=" * 70)
                print(
                    f"🔥 候補 #{found_count}"
                )
                print("TAG:", el.evaluate("el => el.tagName"))
                print("TEXT:", text)
                print("VALUE:", value)
                print("HREF:", href)
                print("ONCLICK:", onclick)
                print("NAME:", name)
                print("ID:", element_id)
                print("CLASS:", class_name)

            except Exception:
                continue

        print()
        print("=" * 70)
        print("🔥 調査完了")
        print("結果候補:", found_count)
        print("=" * 70)

        input("確認できたらEnter：")


if __name__ == "__main__":
    main()