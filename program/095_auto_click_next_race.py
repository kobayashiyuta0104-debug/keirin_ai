from playwright.sync_api import sync_playwright


def main():

    print("=== 095 次レース自動クリックテスト ===")

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
        print("例：7Rの確定結果ページ")
        print()
        input("開いたらターミナルに戻ってEnterを押してください：")

        print()
        print("🔥 レース番号らしきボタンを調査します")

        # ページ内のリンクを全部調査
        links = page.locator("a")

        count = links.count()

        print("リンク数:", count)

        race_links = []

        for i in range(count):

            link = links.nth(i)

            try:

                text = link.inner_text().strip()

                if text in [
                    "1R", "2R", "3R", "4R",
                    "5R", "6R", "7R", "8R",
                    "9R", "10R", "11R", "12R"
                ]:

                    print(
                        "🔥 レースリンク発見:",
                        text
                    )

                    race_links.append(
                        {
                            "text": text,
                            "index": i
                        }
                    )

            except:
                pass

        print()
        print("=== 発見したレースリンク ===")

        for item in race_links:

            print(
                item["text"],
                "index:",
                item["index"]
            )

        print()

        if len(race_links) == 0:

            print("❌ レースリンクが見つかりませんでした")

        else:

            print("🔥 最初に見つかったレースリンクをクリックします")

            target = race_links[0]

            print(
                "クリック対象:",
                target["text"]
            )

            links.nth(
                target["index"]
            ).click()

            page.wait_for_timeout(5000)

            print("🔥 自動クリック完了")

        input(
            "\n確認できたらEnterを押してください："
        )

        browser.close()

        print()
        print("=== 095 テスト完了 ===")


if __name__ == "__main__":
    main()