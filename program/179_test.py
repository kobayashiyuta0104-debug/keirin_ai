from playwright.sync_api import sync_playwright
import json
import time


OUTPUT_JSON = "178_all_venues_jsj006_with_request.json"


def main():

    print("=" * 70)
    print("🔥 155修正版 全開催 × 全レース JSJ006自動取得")
    print("=" * 70)

    all_results = {}

    current_race = {
        "venue": None,
        "race_no": None,
    }

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="msedge",
        )

        context = browser.new_context()

        page = context.new_page()

        # ==================================================
        # JSJ006監視
        # ==================================================

        def handle_response(response):

            url = response.url

            if "type=JSJ006" not in url:
                return

            print()
            print("🔥 JSJ006通信発見！")
            print(url)

            venue = current_race["venue"]
            race_no = current_race["race_no"]

            if venue is None:
                print("⚠ venue未設定")
                return

            if race_no is None:
                print("⚠ race未設定")
                return

            try:

                data = response.json()
                request = response.request

                print()
                print("=" * 70)
                print("🔥 JSJ006 REQUEST DETAIL")
                print("=" * 70)
                print("URL:")
                print(url)
                print()
                print("METHOD:")
                print(request.method)
                print()
                print("POST DATA:")
                print(request.post_data)
                print("=" * 70)

                if isinstance(data, dict):

                    data["_capture_meta"] = {
                        "request_url": url,
                        "request_method": request.method,
                        "request_post_data": request.post_data,
                    }
                

            except Exception as e:

                print(
                    f"❌ JSON解析失敗: {e}"
                )

                return

            if venue not in all_results:

                all_results[venue] = {}

            all_results[
                venue
            ][
                str(race_no)
            ] = data

            player_count = 0

            if isinstance(data, dict):

                players = data.get(
                    "sensyuTypeInfo",
                    []
                )

                if isinstance(players, list):

                    player_count = len(players)

            print(
                f"🔥 取得成功 "
                f"{venue} "
                f"{race_no}R "
                f"選手数={player_count}"
            )

        context.on(
            "response",
            handle_response
        )

        # ==================================================
        # KEIRIN.JP
        # ==================================================

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded",
            timeout=120000,
        )

        print()
        print("🔥 Edgeを操作してください")
        print()
        print("122テストで巡回成功した時と同じ画面まで進んでください")
        print()
        print("開催場が横に並んでいて")
        print("1R～12Rのレースボタンが見える画面")
        print()
        print("さらにJSJ006通信が出るページを開いてください")
        print()
        print("準備できたらEdgeは触らなくてOK")
        print()

        input(
            "🔥 準備できたらEnter："
        )

        # ==================================================
        # 開催場取得
        # ==================================================

        print()
        print("🔥 開催場取得開始")

        venue_elements = page.locator(
            "td.tdkeirin[onclick^='raKeirinjoClick']"
        )

        venue_count = venue_elements.count()

        venues = []

        for i in range(venue_count):

            el = venue_elements.nth(i)

            try:

                name = (
                    el.inner_text()
                    .strip()
                )

                onclick = (
                    el.get_attribute(
                        "onclick"
                    )
                    or ""
                )

            except Exception:

                continue

            if not name:
                continue

            if "raKeirinjoClick" not in onclick:
                continue

            try:

                index_text = (
                    onclick
                    .replace(
                        "raKeirinjoClick(",
                        ""
                    )
                    .replace(
                        ");",
                        ""
                    )
                    .replace(
                        ")",
                        ""
                    )
                    .strip()
                )

                venue_index = int(
                    index_text
                )

            except Exception:

                continue

            venues.append({
                "name": name,
                "index": venue_index,
            })

        print()
        print("🔥 開催場一覧")

        for venue in venues:

            print(
                venue["name"],
                "INDEX:",
                venue["index"],
            )

        print()
        print(
            f"開催場数: {len(venues)}"
        )

        # ==================================================
        # 全開催巡回
        # ==================================================

        for venue_number, venue in enumerate(
            venues,
            start=1,
        ):

            venue_name = venue["name"]
            venue_index = venue["index"]

            print()
            print("=" * 70)
            print(
                f"🔥 開催場 "
                f"{venue_number}/{len(venues)}"
            )
            print(
                f"競輪場: {venue_name}"
            )
            print(
                f"INDEX: {venue_index}"
            )
            print("=" * 70)

            all_results.setdefault(
                venue_name,
                {}
            )

            current_race[
                "venue"
            ] = venue_name

            current_race[
                "race_no"
            ] = None

            # ==============================================
            # 開催場切替
            # ==============================================

            print()
            print(
                f"🔥 {venue_name}へ切替"
            )

            try:

                venue_locator = page.locator(
                    f"td.tdkeirin[onclick*='raKeirinjoClick({venue_index}']"
                )

                venue_locator_count = venue_locator.count()

                print(
                    "🔥 開催場DOM候補数:",
                    venue_locator_count,
                )

                if venue_locator_count == 0:

                    print(
                        f"❌ 開催場DOM無し "
                        f"{venue_name} "
                        f"INDEX={venue_index}"
                    )

                    continue

                venue_element = venue_locator.first

                print(
                    "🔥 開催場DOM直接CLICK:",
                    venue_name,
                )

                venue_element.click(
                    timeout=10000,
                    force=True,
                )

            except Exception as e:

                print(
                    f"❌ 開催場DOM CLICK失敗: {e}"
                )

                continue

            page.wait_for_timeout(
                2500
            )

            # ==============================================
            # レースボタン探索
            # ==============================================

            print()
            print("🔥 レースボタン探索")

            race_buttons = []

            for race_no in range(
                1,
                13,
            ):

                selectors = [
                    f"#hhRaceBtn{race_no}",
                    f"#raceBtn{race_no}",
                    f"[id*='RaceBtn{race_no}']",
                ]

                found = False

                for selector in selectors:

                    locator = page.locator(
                        selector
                    )

                    if locator.count() == 0:
                        continue

                    try:

                        if not locator.first.is_visible():
                            continue

                        text = (
                            locator
                            .first
                            .inner_text()
                            .strip()
                        )

                    except Exception:

                        continue

                    print(
                        f"🔥 {race_no}R候補 "
                        f"{selector} "
                        f"TEXT={text}"
                    )

                    race_buttons.append({
                        "race_no": race_no,
                        "selector": selector,
                    })

                    found = True
                    break

                if found:
                    continue

            print()
            print(
                "🔥 レース候補数:",
                len(race_buttons),
            )

            # ==============================================
            # 全レース巡回
            # ==============================================

            for race_info in race_buttons:

                race_no = race_info[
                    "race_no"
                ]

                selector = race_info[
                    "selector"
                ]

                current_race[
                    "race_no"
                ] = race_no

                all_results[
                    venue_name
                ].pop(
                    str(race_no),
                    None,
                )

                print()
                print("-" * 60)
                print(
                    f"🔥 {venue_name} "
                    f"{race_no}R"
                )
                print(
                    f"SELECTOR: {selector}"
                )

                try:

                    button = page.locator(
                        selector
                    ).first

                    button.click(
                        timeout=10000,
                        force=True,
                    )

                except Exception as e:

                    print(
                        f"❌ レースクリック失敗: {e}"
                    )

                    continue

                # ==========================================
                # JSJ006待機
                # ==========================================

                success = False

                for wait_count in range(
                    40
                ):

                    page.wait_for_timeout(
                        500
                    )

                    if (
                        str(race_no)
                        in all_results[
                            venue_name
                        ]
                    ):

                        success = True
                        break

                if success:

                    data = all_results[
                        venue_name
                    ][
                        str(race_no)
                    ]

                    player_count = 0

                    if isinstance(
                        data,
                        dict,
                    ):

                        players = data.get(
                            "sensyuTypeInfo",
                            []
                        )

                        if isinstance(
                            players,
                            list,
                        ):

                            player_count = len(
                                players
                            )

                    print(
                        f"✅ {venue_name} "
                        f"{race_no}R "
                        f"取得完了 "
                        f"選手数={player_count}"
                    )

                else:

                    print(
                        f"❌ {venue_name} "
                        f"{race_no}R "
                        "JSJ006通信なし"
                    )

            print()
            print("=" * 60)
            print(
                f"🔥 {venue_name}終了"
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

        # ==================================================
        # 保存
        # ==================================================

        with open(
            OUTPUT_JSON,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                all_results,
                f,
                ensure_ascii=False,
                indent=2,
            )

        # ==================================================
        # 集計
        # ==================================================

        print()
        print("=" * 70)
        print("🔥 155修正版テスト終了")
        print("=" * 70)

        total_races = 0
        total_players = 0

        for venue_name, races in (
            all_results.items()
        ):

            race_count = len(
                races
            )

            player_count = 0

            for data in races.values():

                if not isinstance(
                    data,
                    dict,
                ):

                    continue

                players = data.get(
                    "sensyuTypeInfo",
                    []
                )

                if isinstance(
                    players,
                    list,
                ):

                    player_count += len(
                        players
                    )

            total_races += race_count
            total_players += player_count

            print(
                f"{venue_name} "
                f"取得数: {race_count} "
                f"選手数: {player_count}"
            )

        print()
        print(
            f"総レース取得数: {total_races}"
        )

        print(
            f"総選手データ数: {total_players}"
        )

        print()
        print(
            f"保存先: {OUTPUT_JSON}"
        )

        print("=" * 70)

        input(
            "確認できたらEnter："
        )

        browser.close()


if __name__ == "__main__":
    main()
