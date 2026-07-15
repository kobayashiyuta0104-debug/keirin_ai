from playwright.sync_api import sync_playwright
import json


def main():

    print("=== 120 2開催 × 競走結果復帰 × 全確定JSJ012取得テスト ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="msedge"
        )

        context = browser.new_context()
        page = context.new_page()

        all_results = {}

        current_race = {
            "venue": None,
            "number": None
        }

        # --------------------------------------------------
        # JSJ012監視
        # --------------------------------------------------

        def handle_response(response):

            if "JSJ012" not in response.url:
                return

            venue_name = current_race["venue"]
            race_no = current_race["number"]

            if venue_name is None:
                return

            if race_no is None:
                return

            try:

                data = response.json()

                if venue_name not in all_results:
                    all_results[venue_name] = {}

                all_results[venue_name][str(race_no)] = data

                print(
                    f"🔥 {venue_name} "
                    f"{race_no}R "
                    "JSJ012取得成功！"
                )

            except Exception as e:

                print(
                    f"❌ {venue_name} "
                    f"{race_no}R "
                    "JSON取得失敗:",
                    e
                )

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
        print()
        print("確定結果ページを開いてください")
        print("確定済みレースがある開催を表示してください")
        print("その開催の1レースを表示してください")
        print()

        input(
            "準備できたらターミナルに戻ってEnter："
        )

        # --------------------------------------------------
        # 競輪場抽出
        # --------------------------------------------------

        print()
        print("🔥 競輪場を探します")

        venue_elements = page.locator(
            "td.tdkeirin"
            "[onclick^='raKeirinjoClick']"
        )

        venue_count = venue_elements.count()

        venues = []

        for i in range(venue_count):

            el = venue_elements.nth(i)

            try:

                text = (
                    el
                    .inner_text()
                    .strip()
                )

                onclick = (
                    el
                    .get_attribute("onclick")
                )

            except:
                continue

            if not text:
                continue

            if not onclick:
                continue

            try:

                index = int(
                    onclick
                    .replace(
                        "raKeirinjoClick(",
                        ""
                    )
                    .replace(
                        ")",
                        ""
                    )
                )

            except:
                continue

            venues.append(
                {
                    "name": text,
                    "index": index
                }
            )

        print()
        print("🔥 競輪場一覧")

        for venue in venues:

            print(
                venue["name"],
                "INDEX:",
                venue["index"]
            )

        print()
        print(
            "🔥 最初の2競輪場を取得します"
        )

        test_venues = venues[:2]

        # --------------------------------------------------
        # 2競輪場ループ
        # --------------------------------------------------

        for venue_no, venue in enumerate(
            test_venues,
            start=1
        ):

            venue_name = venue["name"]
            venue_index = venue["index"]

            print()
            print("=" * 70)
            print(
                f"🔥 競輪場 #{venue_no}"
            )
            print(
                f"競輪場: {venue_name}"
            )
            print(
                f"INDEX: {venue_index}"
            )
            print("=" * 70)

            # ----------------------------------------------
            # 競輪場切替
            # ----------------------------------------------

            print()
            print(
                f"🔥 {venue_name}へ切替"
            )

            page.evaluate(
                f"raKeirinjoClick({venue_index})"
            )

            page.wait_for_timeout(3000)

            print(
                "✅ 競輪場切替終了"
            )

            # ----------------------------------------------
            # 119成功方式
            # 競走結果モード直接復帰
            # ----------------------------------------------

            print()
            print(
                "🔥 競走結果モードへ復帰"
            )

            try:

                function_type = page.evaluate(
                    "typeof btnClickOfFrame"
                )

                print(
                    "btnClickOfFrame:",
                    function_type
                )

                if function_type != "function":

                    print(
                        "❌ btnClickOfFrameなし"
                    )

                    continue

                page.evaluate(
                    "btnClickOfFrame('PJ0326')"
                )

                print(
                    "✅ 競走結果モード実行"
                )

            except Exception as e:

                print(
                    "❌ 競走結果モード復帰失敗:",
                    e
                )

                continue

            # ----------------------------------------------
            # 1R出現待機
            # ----------------------------------------------

            print()
            print(
                "🔥 レースボタン出現待機"
            )

            race_area_found = False

            for wait_count in range(40):

                page.wait_for_timeout(500)

                race1 = page.locator(
                    "#hhRaceBtn1"
                )

                count = race1.count()

                print(
                    f"待機 {wait_count + 1}: "
                    f"1R数={count}"
                )

                if count == 0:
                    continue

                try:

                    text = (
                        race1
                        .first
                        .inner_text()
                        .strip()
                    )

                    if text == "1R":

                        race_area_found = True
                        break

                except:
                    pass

            if not race_area_found:

                print()
                print(
                    f"❌ {venue_name} "
                    "レースボタン取得失敗"
                )

                continue

            print()
            print(
                "🔥 レースボタン確認成功"
            )

            # ----------------------------------------------
            # 確定レース調査
            # ----------------------------------------------

            print()
            print(
                "🔥 確定レースを調査します"
            )

            race_buttons = []

            for race in range(1, 13):

                selector = (
                    f"#hhRaceBtn{race}"
                )

                button = page.locator(
                    selector
                )

                if button.count() == 0:
                    continue

                try:

                    text = (
                        button
                        .first
                        .inner_text()
                        .strip()
                    )

                except:
                    continue

                if text != f"{race}R":
                    continue

                class_name = (
                    button
                    .first
                    .get_attribute("class")
                    or ""
                )

                print(
                    f"{race}R CLASS:",
                    repr(class_name)
                )

                if "fin" not in class_name:
                    continue

                race_buttons.append(race)

                print(
                    f"🔥 確定レース発見: "
                    f"{race}R"
                )

            print()
            print(
                "取得対象:",
                race_buttons
            )

            if venue_name not in all_results:

                all_results[venue_name] = {}

            # ----------------------------------------------
            # 全確定レースJSJ012取得
            # ----------------------------------------------

            print()
            print(
                f"🔥 {venue_name} "
                "自動取得開始"
            )

            for race in race_buttons:

                current_race["venue"] = venue_name
                current_race["number"] = race

                print()
                print("=" * 60)

                print(
                    f"🔥 {venue_name} "
                    f"{race}Rを開きます"
                )

                try:

                    race_button = page.locator(
                        f"#hhRaceBtn{race}"
                    )

                    race_button.first.click()

                except Exception as e:

                    print(
                        f"❌ {race}R "
                        "クリック失敗:",
                        e
                    )

                    continue

                for _ in range(30):

                    page.wait_for_timeout(500)

                    if (
                        str(race)
                        in all_results[venue_name]
                    ):
                        break

                if (
                    str(race)
                    in all_results[venue_name]
                ):

                    print(
                        f"✅ {race}R取得完了"
                    )

                else:

                    print(
                        f"❌ {race}R取得失敗"
                    )

            current_race["venue"] = None
            current_race["number"] = None

            print()
            print("=" * 60)

            print(
                f"🔥 {venue_name} "
                "取得終了"
            )

            print(
                "取得数:",
                len(
                    all_results[venue_name]
                )
            )

            print("=" * 60)

        # --------------------------------------------------
        # JSON保存
        # --------------------------------------------------

        save_file = (
            "120_2venues_jsj012.json"
        )

        with open(
            save_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                all_results,
                f,
                ensure_ascii=False,
                indent=2
            )

        print()
        print("=" * 70)
        print("🔥 120テスト終了")
        print("=" * 70)

        for venue_name, results in (
            all_results.items()
        ):

            print(
                venue_name,
                "取得数:",
                len(results)
            )

        print()
        print(
            "保存先:",
            save_file
        )

        input(
            "確認できたらEnter："
        )

        browser.close()


if __name__ == "__main__":
    main()