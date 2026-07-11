from playwright.sync_api import sync_playwright
import json


def main():

    print("=== 102 2開催 × 全レース JSJ012取得テスト ===")

    all_results = {}

    with sync_playwright() as p:

        browser = p.chromium.connect_over_cdp(
            "http://127.0.0.1:9222"
        )

        context = browser.contexts[0]

        # 今開いているKEIRIN.JPのタブを探す
        page = None

        for p_page in context.pages:

            if "keirin.jp" in p_page.url.lower():
                page = p_page

        if page is None:
            print("❌ KEIRIN.JPのタブが見つかりません")
            return

        print()
        print("🔥 使用ページ")
        print(page.url)

        print()
        print("🔥 ブラウザを操作してください")
        print("確定結果ページを1開催開いてください")
        print("その開催の1レースを表示してください")
        print()

        input("準備できたらEnter：")

        # --------------------------------------------------
        # 開催候補取得
        # --------------------------------------------------

        venue_elements = page.locator(
            "[onclick^='raKeirinjoClick']"
        )

        venue_count = venue_elements.count()

        venues = []

        for i in range(venue_count):

            el = venue_elements.nth(i)

            text = el.inner_text().strip()

            if text in [f"{i}R" for i in range(1, 13)]:
                continue

            onclick = el.get_attribute("onclick")

            if not text:
                continue

            if not onclick:
                continue

            if "raKeirinjoClick" not in onclick:
                continue

            try:

                index = int(
                    onclick
                    .replace("raKeirinjoClick(", "")
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
        print("🔥 今回は最初の2開催だけ取得します")

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
            print(f"🔥 開催 #{venue_no}")
            print(f"競輪場: {venue_name}")
            print(f"INDEX: {venue_index}")
            print("=" * 70)

            venue_results = {}

            current_race = {
                "number": None
            }

            # --------------------------------------------------
            # JSJ012監視
            # 097方式
            # --------------------------------------------------

            def handle_response(response):

                if "/pc/json?" not in response.url:
                    return

                target_types = [
                    "JSJ001",
                    "JSJ003",
                    "JSJ004",
                    "JSJ005",
                    "JSJ006",
                    "JSJ012",
                ]

                found_type = None

                for json_type in target_types:

                    if f"type={json_type}" in response.url:
                        found_type = json_type
                        break

                if found_type is None:
                    return

                race_no = current_race["number"]

                if race_no is None:
                    return

                try:

                    data = response.json()

                    print()
                    print("=" * 70)
                    print(
                        f"🔥 {venue_name} "
                        f"{race_no}R "
                        f"{found_type}取得"
                    )
                    print("=" * 70)

                    print(
                        json.dumps(
                            data,
                            ensure_ascii=False,
                            indent=2
                        )[:3000]
                    )

                except Exception as e:

                    print(
                        f"❌ {found_type} "
                        "JSON取得失敗:",
                        e
                    )
            context.on(
                "response",
                handle_response
            )

            # --------------------------------------------------
            # 競輪場切替
            # --------------------------------------------------

            print()
            print(f"🔥 {venue_name}へ切替")

            page.evaluate(
                f"raKeirinjoClick({venue_index})"
            )

            page.wait_for_timeout(3000)

            # --------------------------------------------------
            # 確定レース番号取得
            # --------------------------------------------------

            race_buttons = page.locator(
                "[name='hhRaceBtn']"
            )

            race_count = race_buttons.count()

            races = []

            for i in range(race_count):

                btn = race_buttons.nth(i)

                text = btn.inner_text().strip()

                class_name = (
                    btn.get_attribute("class") or ""
                )

                if "fin" not in class_name:
                    continue

                if not text.endswith("R"):
                    continue

                try:

                    race_no = int(
                        text.replace("R", "")
                    )

                except:
                    continue

                races.append(race_no)

            races = sorted(set(races))

            print()
            print(
                "🔥 確定レース:",
                races
            )

            # --------------------------------------------------
            # 全確定レース巡回
            # --------------------------------------------------

            for race_no in races:

                print()
                print(
                    f"🔥 {venue_name} "
                    f"{race_no}Rを開きます"
                )

                current_race["number"] = race_no

                button = page.locator(
                    f"#hhRaceBtn{race_no}"
                ).first

                try:

                    button.click()

                    # Playwrightに通信処理をさせる
                    page.wait_for_timeout(3000)

                except Exception as e:

                    print(
                        f"❌ {race_no}R "
                        "クリック失敗"
                    )

                    print(e)

                    continue

                if str(race_no) in venue_results:

                    print(
                        f"✅ {race_no}R取得処理完了"
                    )

                else:

                    print(
                        f"⚠️ {race_no}R "
                        "JSJ012未取得"
                    )

            # --------------------------------------------------
            # listener解除
            # --------------------------------------------------

            context.remove_listener(
                "response",
                handle_response
            )

            # --------------------------------------------------
            # 開催保存
            # --------------------------------------------------

            all_results[
                venue_name
            ] = venue_results

            print()
            print(
                f"🔥 {venue_name}取得終了"
            )

            print(
                "取得数:",
                len(venue_results)
            )

        # --------------------------------------------------
        # JSON保存
        # --------------------------------------------------

        output_file = (
            "102_test_2venues_all_races.json"
        )

        with open(
            output_file,
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
        print("🔥 102 合体テスト終了")
        print("=" * 70)

        for venue_name, results in all_results.items():

            print(
                venue_name,
                "取得数:",
                len(results)
            )

        print()
        print(
            "保存先:",
            output_file
        )

        input(
            "確認できたらEnter："
        )


if __name__ == "__main__":
    main()