from playwright.sync_api import sync_playwright


def main():

    print("=== 096 レース番号ボタン調査 ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()
        page = context.new_page()

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded"
        )

        print()
        print("🔥 ブラウザを操作してください")
        print("確定結果ページを1レース開いてください")
        print()
        input("開いたらターミナルに戻ってEnter：")

        print()
        print("🔥 ページ内のクリック候補を調査します")
        print()

        elements = page.locator(
            "a, button, input, [onclick], [role='button']"
        )

        count = elements.count()

        print("調査要素数:", count)

        found = 0

        for i in range(count):

            try:

                element = elements.nth(i)

                text = element.inner_text().strip()

                href = element.get_attribute("href")
                onclick = element.get_attribute("onclick")
                value = element.get_attribute("value")
                name = element.get_attribute("name")
                element_id = element.get_attribute("id")
                class_name = element.get_attribute("class")

                check_text = " ".join([
                    text or "",
                    value or ""
                ])

                if any(
                    f"{race}R" in check_text
                    for race in range(1, 13)
                ):

                    found += 1

                    print("=" * 70)
                    print(f"🔥 候補 #{found}")
                    print("TEXT:", text)
                    print("VALUE:", value)
                    print("HREF:", href)
                    print("ONCLICK:", onclick)
                    print("NAME:", name)
                    print("ID:", element_id)
                    print("CLASS:", class_name)

            except Exception:
                pass

        print()
        print("=" * 70)
        print("🔥 調査完了")
        print("レース番号候補:", found)
        print("=" * 70)

        input("確認できたらEnter：")

        browser.close()


if __name__ == "__main__":
    main()