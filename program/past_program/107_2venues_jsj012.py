from playwright.sync_api import sync_playwright
import json


def main():

    print("=== 107 2開催 × 全レース JSJ012取得テスト ===")

    with sync_playwright() as p:

        # --------------------------------------------------
        # ブラウザ起動
        # 097と同じ成功方式
        # --------------------------------------------------

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

                all_results[venue_name][
                    str(race_no)
                ] = data

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
        # KEIRIN.JPを開く
        # --------------------------------------------------

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded"
        )

        print()
        print("🔥 ブラウザを操作してください")
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
        # 開催候補取得
        # --------------------------------------------------

        print()
        print("🔥 開催候補を探します")

        venue_elements = page.locator(
            "[onclick^='raKeirinjoClick']"
        )

        venue_count = venue_elements.count()

        venues = []

        for i in range(venue_count):

            el = venue_elements.nth(i)

            try:

                text = el.inner_text().strip()

                onclick = el.get_attribute(
                    "onclick"
                )

            except:
                continue

            if not text:
                continue

            if text in [
                f"{race}R"
                for race in range(1, 13)
            ]:
                continue

            if not onclick:
                continue

            if "raKeirinjoClick" not in onclick:
                continue

            try:

                index = int(
                    onclick
                    .replace(
                        "raKeirinjoClick(",
                        ""
                    )
                    .replace(")", "")
                )

            except:
                continue

            venues.append(
                {
                    "name": text,
                    "index": index
                }
            )

        # --------------------------------------------------
        # 重複削除
        # --------------------------------------------------

        unique_venues = []

        seen = set()

        for venue in venues:

            key = (
                venue["name"],
                venue["index"]
            )

            if key in seen:
                continue

            seen.add(key)

            unique_venues.append(venue)

        venues = unique_venues

        print()
        print("🔥 開催候補")

        for venue in venues:

            print(
                venue["name"],
                "INDEX:",
                venue["index"]
            )

        print()
        print(
            "🔥 最初の2開催を取得します"
        )

        test_venues = venues[:2]

        # --------------------------------------------------
        # 2開催ループ
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
                f"🔥 開催 #{venue_no}"
            )
            print(
                f"競輪場: {venue_name}"
            )
            print(
                f"INDEX: {venue_index}"
            )
            print("=" * 70)

            # ----------------------------------------------
            # 開催切替
            # ----------------------------------------------

            print()
            print(
                f"🔥 {venue_name}へ切替"
            )

            page.evaluate(
                f"raKeirinjoClick({venue_index})"
            )

            page.wait_for_timeout(3000)

            # ----------------------------------------------
            # レースボタン調査
            # 097方式
            # ----------------------------------------------

            print()
            print("🔥 レースボタンを調査します")

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
            # 097方式
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

                print()
                print("=" * 60)

                print(
                    f"🔥 {venue_name} "
                    f"{race}Rを開きます"
                )

                page.locator(
                    f"#hhRaceBtn{race}"
                ).first.click()

                for _ in range(30):

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
            "107_2venues_jsj012.json"
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
        print("🔥 107 合体テスト終了")
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