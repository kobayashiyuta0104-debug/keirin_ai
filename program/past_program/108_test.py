from playwright.sync_api import sync_playwright
import json


def main():

    print("=== 103 Edge 全レースJSJ012取得テスト ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            channel="msedge",
            headless=False
        )

        context = browser.new_context()
        page = context.new_page()

        results = {}
        current_race = None

        def handle_response(response):

            nonlocal current_race

            if "JSJ012" not in response.url:
                return

            try:
                data = response.json()

                if current_race is None:
                    return

                results[str(current_race)] = data

                print(
                    f"🔥 {current_race}R "
                    f"JSJ012取得成功！"
                )

            except Exception as e:
                print(
                    f"❌ {current_race}R "
                    f"JSON取得失敗:",
                    e
                )

        context.on(
            "response",
            handle_response
        )

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded"
        )

        print()
        print("🔥 ブラウザを操作してください")
        print("確定結果ページを1レース開いてください")
        print()
        input(
            "開いたらターミナルに戻ってEnter："
        )

        print()
        print("🔥 レースボタンを調査します")

        race_buttons = []

        for race in range(1, 13):

            selector = f"#hhRaceBtn{race}"

            button = page.locator(selector)

            if button.count() > 0:

                text = button.first.inner_text().strip()

                if text == f"{race}R":

                    race_buttons.append(race)

                    print(
                        f"🔥 レース発見: {race}R"
                    )

        print()
        print(
            "取得対象:",
            race_buttons
        )

        print()
        print("🔥 自動取得開始")
        print()

        for race in race_buttons:

            current_race = race

            print("=" * 60)
            print(
                f"🔥 {race}Rを開きます"
            )

            before_count = len(results)

            page.locator(
                f"#hhRaceBtn{race}"
            ).first.click()

            for _ in range(30):

                page.wait_for_timeout(500)

                if str(race) in results:
                    break

            if str(race) in results:

                print(
                    f"✅ {race}R取得完了"
                )

            else:

                print(
                    f"❌ {race}R取得失敗"
                )

        current_race = None

        print()
        print("=" * 60)
        print("🔥 全レース取得終了")
        print(
            "取得数:",
            len(results)
        )
        print("=" * 60)

        save_file = (
            "103_edge_all_races_jsj012.json"
        )

        with open(
            save_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                results,
                f,
                ensure_ascii=False,
                indent=2
            )

        print(
            "保存先:",
            save_file
        )

        browser.close()


if __name__ == "__main__":
    main()