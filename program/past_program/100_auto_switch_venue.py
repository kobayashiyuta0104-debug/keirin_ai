from playwright.sync_api import sync_playwright
import time
import re


def main():

    print("=== 100 開催自動切替テスト ===")

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
        print("🔥 開催切替ボタンを探します")
        print()

        venue_buttons = []

        elements = page.locator(
            "[onclick^='raKeirinjoClick']"
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
            "開催候補数:",
            len(venue_buttons)
        )

        print()

        for venue in venue_buttons:

            print(
                f"🔥 {venue['text']} "
                f"→ raKeirinjoClick"
                f"({venue['index']})"
            )

        if len(venue_buttons) < 2:

            print()
            print(
                "❌ 切替候補が2件未満です"
            )

            input("Enterで終了：")

            browser.close()

            return

        print()
        print("=" * 70)
        print("🔥 自動切替テスト開始")
        print("=" * 70)

        current_venue = venue_buttons[0]
        next_venue = venue_buttons[1]

        print()
        print(
            "現在候補:",
            current_venue["text"]
        )

        print(
            "切替先:",
            next_venue["text"]
        )

        print()
        print(
            "🔥 Pythonから切替関数を実行します"
        )

        page.evaluate(
            f"raKeirinjoClick("
            f"{next_venue['index']}"
            f")"
        )

        page.wait_for_timeout(
            5000
        )

        print()
        print(
            "🔥 自動切替処理を実行しました"
        )

        print(
            "現在ページ:",
            page.url
        )

        print()
        print(
            "ブラウザを確認してください"
        )

        input(
            "切り替わっていたらEnter："
        )

        browser.close()

        print()
        print(
            "🔥 100 テスト完了"
        )


if __name__ == "__main__":
    main()