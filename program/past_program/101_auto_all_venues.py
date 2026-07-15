from playwright.sync_api import sync_playwright
import re


def main():

    print("=== 101 全開催自動切替テスト ===")

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
        print("確定結果ページを1開催開いてください")
        print()

        input(
            "開いたらターミナルに戻ってEnter："
        )

        print()
        print("🔥 開催中の競輪場だけ探します")
        print()

        venue_buttons = []

        elements = page.locator(
            "td.tdkeirin[onclick^='raKeirinjoClick']"
        )

        count = elements.count()

        for i in range(count):

            try:

                element = elements.nth(i)

                text = element.inner_text().strip()

                onclick = element.get_attribute(
                    "onclick"
                )

                if not text:
                    continue

                match = re.search(
                    r"raKeirinjoClick\((\d+)\)",
                    onclick or ""
                )

                if not match:
                    continue

                index = int(
                    match.group(1)
                )

                venue_buttons.append(
                    {
                        "text": text,
                        "index": index
                    }
                )

            except Exception:
                pass

        print(
            "🔥 開催候補数:",
            len(venue_buttons)
        )

        print()

        for venue in venue_buttons:

            print(
                f"🔥 {venue['text']} "
                f"→ raKeirinjoClick"
                f"({venue['index']})"
            )

        if not venue_buttons:

            print()
            print(
                "❌ 開催候補が見つかりません"
            )

            input("Enterで終了：")

            browser.close()

            return

        print()
        print("=" * 70)
        print("🔥 全開催 自動切替開始")
        print("=" * 70)

        for number, venue in enumerate(
            venue_buttons,
            start=1
        ):

            print()
            print("-" * 70)

            print(
                f"🔥 開催 #{number}"
            )

            print(
                "競輪場:",
                venue["text"]
            )

            print(
                "INDEX:",
                venue["index"]
            )

            print(
                "🔥 自動切替します"
            )

            page.evaluate(
                f"raKeirinjoClick("
                f"{venue['index']}"
                f")"
            )

            page.wait_for_timeout(
                3000
            )

            print(
                "✅ 切替処理完了"
            )

        print()
        print("=" * 70)
        print("🔥 全開催切替終了")
        print(
            "切替数:",
            len(venue_buttons)
        )
        print("=" * 70)

        print()
        print(
            "ブラウザを確認してください"
        )

        input(
            "確認できたらEnter："
        )

        browser.close()

        print()
        print(
            "🔥 101 テスト完了"
        )


if __name__ == "__main__":
    main()