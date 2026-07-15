from playwright.sync_api import sync_playwright
import json


def main():

    print("=== 121 全開催 × 全確定JSJ012取得テスト ===")

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

        jsj012_found = False

        # --------------------------------------------------
        # JSJ012監視
        # --------------------------------------------------

        def handle_response(response):

            nonlocal jsj012_found

            if "JSJ012" not in response.url:
                return

            venue_name = current_race["venue"]
            race_no = current_race["number"]

            if venue_name is None:
                return

            if race_no is None:
                return

            print()
            print(
                f"🔥 {venue_name} "
                f"{race_no}R "
                "JSJ012発見！"
            )

            try:

                data = response.json()

                if venue_name not in all_results:
                    all_results[venue_name] = {}

                all_results[venue_name][
                    str(race_no)
                ] = data

                jsj012_found = True

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
        print("結果一覧は押さなくてOKです")
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
                    .get_attribute(
                        "onclick"
                    )
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
            "🔥 全競輪場を取得します"
        )

        test_venues = venues

        # --------------------------------------------------
        # 全競輪場ループ
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

            # ----------------------------------------------
            # 競走結果ボタン待機
            # ----------------------------------------------

            print()
            print("🔥 競走結果ボタン待機")

            result_button = page.locator(
                "#rctbn8"
            )

            result_found = False

            for wait_count in range(30):

                page.wait_for_timeout(500)

                count = result_button.count()

                print(
                    f"待機 {wait_count + 1}: "
                    f"rctbn8数={count}"
                )

                if count > 0:

                    try:

                        if (
                            result_button
                            .first
                            .is_visible()
                        ):

                            result_found = True
                            break

                    except:
                        pass

            if not result_found:

                print()
                print(
                    f"❌ {venue_name} "
                    "#rctbn8が出現しません"
                )

                if venue_name not in all_results:

                    all_results[
                        venue_name
                    ] = {}

                continue

            print()
            print(
                "🔥 #rctbn8 出現確認！"
            )

            # ----------------------------------------------
            # 競走結果クリック
            # ----------------------------------------------

            result_button.first.click()

            page.wait_for_timeout(3000)

            print(
                "✅ 競走結果クリック終了"
            )

            # ----------------------------------------------
            # 1R待機
            # ----------------------------------------------

            print()
            print("🔥 1Rボタン待機")

            race1_button = page.locator(
                "#hhRaceBtn1"
            )

            race1_found = False

            for wait_count in range(30):

                page.wait_for_timeout(500)

                if race1_button.count() == 0:
                    continue

                try:

                    text = (
                        race1_button
                        .first
                        .inner_text()
                        .strip()
                    )

                    if text == "1R":

                        race1_found = True
                        break

                except:
                    pass

            if not race1_found:

                print()
                print(
                    f"❌ {venue_name} "
                    "1Rが出現しません"
                )

                if venue_name not in all_results:

                    all_results[
                        venue_name
                    ] = {}

                continue

            print()
            print("🔥 1R出現確認")

            # ----------------------------------------------
            # 確定レース調査
            # ----------------------------------------------

            print()
            print("🔥 確定レースを調査します")

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

                all_results[
                    venue_name
                ] = {}

            # ----------------------------------------------
            # 全確定レース取得
            # ----------------------------------------------

            print()
            print(
                f"🔥 {venue_name} "
                "自動取得開始"
            )

            for race in race_buttons:

                current_race[
                    "venue"
                ] = venue_name

                current_race[
                    "number"
                ] = race

                jsj012_found = False

                print()
                print("-" * 60)

                print(
                    f"🔥 {venue_name} "
                    f"{race}Rを開きます"
                )

                race_button = page.locator(
                    f"#hhRaceBtn{race}"
                )

                if race_button.count() == 0:

                    print(
                        f"❌ {race}Rボタンなし"
                    )

                    continue

                race_button.first.click()

                # ------------------------------------------
                # JSJ012待機
                # ------------------------------------------

                for wait_count in range(30):

                    page.wait_for_timeout(
                        500
                    )

                    if (
                        str(race)
                        in all_results[
                            venue_name
                        ]
                    ):
                        break

                if (
                    str(race)
                    in all_results[
                        venue_name
                    ]
                ):

                    print(
                        f"✅ {race}R取得完了"
                    )

                else:

                    print(
                        f"❌ {race}R取得失敗"
                    )

            current_race[
                "venue"
            ] = None

            current_race[
                "number"
            ] = None

            print()
            print("=" * 60)

            print(
                f"🔥 {venue_name} "
                "取得終了"
            )

            print(
                "取得数:",
                len(
                    all_results[
                        venue_name
                    ]
                )
            )

            print("=" * 60)

        # --------------------------------------------------
        # JSON保存
        # --------------------------------------------------

        save_file = (
            "121_all_venues_jsj012.json"
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

        # --------------------------------------------------
        # 最終結果
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 121テスト終了")
        print("=" * 70)

        total_count = 0

        for venue_name, results in (
            all_results.items()
        ):

            result_count = len(results)

            total_count += result_count

            print(
                venue_name,
                "取得数:",
                result_count
            )

        print()
        print(
            "🔥 総取得数:",
            total_count
        )

        print()
        print(
            "保存先:",
            save_file
        )

        print("=" * 70)

        input(
            "確認できたらEnter："
        )

        browser.close()


if __name__ == "__main__":
    main()