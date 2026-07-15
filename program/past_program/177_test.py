from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, parse_qs
import json


OUTPUT_JSON = "177_jsj006_encp_capture.json"


def main():

    print("=" * 70)
    print("🔥 177 JSJ006 ENCP直接捕獲")
    print("=" * 70)

    captured = []

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

            venue = current_race["venue"]
            race_no = current_race["race_no"]

            parsed = urlparse(url)

            query = parse_qs(
                parsed.query,
                keep_blank_values=True,
            )

            encp = None

            if "encp" in query:

                values = query["encp"]

                if values:

                    encp = values[0]

            request = response.request

            item = {
                "venue": venue,
                "race_no": race_no,
                "url": url,
                "method": request.method,
                "post_data": request.post_data,
                "encp": encp,
                "status": response.status,
            }

            captured.append(item)

            print()
            print("=" * 70)
            print("🔥🔥🔥 JSJ006 ENCP捕獲成功 🔥🔥🔥")
            print("=" * 70)

            print("開催場:", venue)
            print("R:", race_no)

            print()
            print("METHOD:")
            print(request.method)

            print()
            print("STATUS:")
            print(response.status)

            print()
            print("ENCP:")
            print(encp)

            print()
            print("URL:")
            print(url)

            print()
            print("POST DATA:")
            print(request.post_data)

            print("=" * 70)

            save(captured)

        context.on(
            "response",
            handle_response,
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
        print("155成功時と同じ画面まで進んでください")
        print()
        print("開催場が横に並んでいて")
        print("1R～12Rボタンが見える画面")
        print()
        print("準備できたらEnter")
        print()

        input("🔥 準備できたらEnter：")

        # ==================================================
        # 開催場取得
        # ==================================================

        print()
        print("=" * 70)
        print("🔥 開催場取得")
        print("=" * 70)

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

            if "raKeirinjoClick" not in onclick:
                continue

            venues.append(
                {
                    "name": name,
                    "onclick": onclick,
                }
            )

            print(
                f"{len(venues)}: "
                f"{name}"
            )

        print()
        print(
            "開催場数:",
            len(venues),
        )

        # ==================================================
        # 開催場巡回
        # ==================================================

        for venue_index, venue in enumerate(
            venues
        ):

            venue_name = venue["name"]

            onclick = venue["onclick"]

            print()
            print("=" * 70)
            print(
                f"🔥 開催場 "
                f"{venue_index + 1}/"
                f"{len(venues)}"
            )
            print(
                venue_name
            )
            print("=" * 70)

            try:

                args_text = (
                    onclick
                    .replace(
                        "raKeirinjoClick(",
                        ""
                    )
                    .rsplit(
                        ")",
                        1
                    )[0]
                )

                page.evaluate(
                    f"""
                    () => {{
                        raKeirinjoClick(
                            {args_text}
                        );
                    }}
                    """
                )

                page.wait_for_timeout(
                    1500
                )

            except Exception as e:

                print(
                    "❌ 開催場切替失敗:",
                    e,
                )

                continue

            # ==============================================
            # レースボタン探索
            # ==============================================

            race_buttons = []

            for race_no in range(
                1,
                13,
            ):

                selectors = [
                    f"#raceNum{race_no}",
                    f"#raceNo{race_no}",
                    f"#btnRace{race_no}",
                    (
                        "button:"
                        f"has-text('{race_no}R')"
                    ),
                    (
                        "input[value='"
                        f"{race_no}R"
                        "']"
                    ),
                ]

                found_selector = None

                for selector in selectors:

                    try:

                        locator = page.locator(
                            selector
                        )

                        if locator.count() > 0:

                            found_selector = selector
                            break

                    except Exception:

                        pass

                if found_selector:

                    race_buttons.append(
                        {
                            "race_no": race_no,
                            "selector": found_selector,
                        }
                    )

            print(
                "レースボタン数:",
                len(race_buttons),
            )

            # ==============================================
            # レースクリック
            # ==============================================

            for race in race_buttons:

                race_no = race["race_no"]

                selector = race["selector"]

                current_race[
                    "venue"
                ] = venue_name

                current_race[
                    "race_no"
                ] = race_no

                before_count = len(
                    captured
                )

                print()
                print("-" * 60)

                print(
                    f"🔥 {venue_name} "
                    f"{race_no}R"
                )

                print(
                    "SELECTOR:",
                    selector,
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
                        "❌ CLICK失敗:",
                        e,
                    )

                    continue

                success = False

                for _ in range(40):

                    page.wait_for_timeout(
                        500
                    )

                    if (
                        len(captured)
                        > before_count
                    ):

                        success = True
                        break

                if success:

                    print(
                        f"✅ {venue_name} "
                        f"{race_no}R "
                        "ENCP取得"
                    )

                else:

                    print(
                        f"❌ {venue_name} "
                        f"{race_no}R "
                        "JSJ006なし"
                    )

        # ==================================================
        # 保存
        # ==================================================

        save(captured)

        print()
        print("=" * 70)
        print("🔥 ENCP一覧")
        print("=" * 70)

        for i, item in enumerate(
            captured,
            start=1,
        ):

            print()
            print("-" * 70)

            print(
                f"🔥 ENCP #{i}"
            )

            print(
                "開催場:",
                item["venue"],
            )

            print(
                "R:",
                item["race_no"],
            )

            print(
                "ENCP:",
                item["encp"],
            )

        print()
        print("=" * 70)
        print("🔥 177テスト終了")
        print("=" * 70)

        print(
            "JSJ006捕獲数:",
            len(captured),
        )

        encp_count = sum(
            1
            for item in captured
            if item["encp"]
        )

        print(
            "ENCP取得数:",
            encp_count,
        )

        print(
            "保存先:",
            OUTPUT_JSON,
        )

        print("=" * 70)

        input(
            "確認できたらEnter："
        )

        browser.close()


def save(data):

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


if __name__ == "__main__":
    main()