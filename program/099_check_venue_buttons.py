from playwright.sync_api import sync_playwright


def main():

    print("=== 099 競輪場名だけ調査 ===")

    venue_names = [
        "函館", "青森", "いわき平", "弥彦", "前橋",
        "取手", "宇都宮", "大宮", "西武園", "京王閣",
        "立川", "松戸", "千葉", "川崎", "平塚",
        "小田原", "伊東", "静岡", "名古屋", "岐阜",
        "大垣", "豊橋", "富山", "松阪", "四日市",
        "福井", "奈良", "向日町", "和歌山", "岸和田",
        "玉野", "広島", "防府", "高松", "小松島",
        "高知", "松山", "小倉", "久留米", "武雄",
        "佐世保", "別府", "熊本"
    ]

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
        print("🔥 競輪場名を探します")
        print()

        elements = page.locator(
            "a, button, input, td, li, "
            "[onclick], [role='button']"
        )

        count = elements.count()

        found = 0

        for i in range(count):

            try:

                element = elements.nth(i)

                text = element.inner_text().strip()

                if not text:
                    continue

                matched = False

                for venue in venue_names:

                    if venue in text:
                        matched = True
                        break

                if not matched:
                    continue

                found += 1

                print("=" * 70)
                print(f"🔥 競輪場候補 #{found}")
                print("TEXT:", repr(text))
                print("VALUE:", element.get_attribute("value"))
                print("HREF:", element.get_attribute("href"))
                print("ONCLICK:", element.get_attribute("onclick"))
                print("NAME:", element.get_attribute("name"))
                print("ID:", element.get_attribute("id"))
                print("CLASS:", element.get_attribute("class"))

            except Exception:
                pass

        print()
        print("=" * 70)
        print("🔥 調査完了")
        print("競輪場候補数:", found)
        print("=" * 70)

        input(
            "確認できたらEnter："
        )

        browser.close()


if __name__ == "__main__":
    main()