from playwright.sync_api import sync_playwright


def main():

    print("=== 116 競輪場切替後 全FRAME競走結果ボタン調査 ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="msedge"
        )

        context = browser.new_context()

        page = context.new_page()

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
        print("確定済み開催を表示してください")
        print("1レースを表示してください")
        print()

        input(
            "準備できたらターミナルに戻ってEnter："
        )

        # --------------------------------------------------
        # 切替前FRAME確認
        # --------------------------------------------------

        print()
        print("=" * 80)
        print("🔥 切替前 FRAME一覧")
        print("=" * 80)

        print(
            "FRAME数:",
            len(page.frames)
        )

        for i, frame in enumerate(page.frames):

            print()
            print(
                f"FRAME #{i}"
            )

            print(
                "NAME:",
                repr(frame.name)
            )

            print(
                "URL:",
                frame.url
            )

            try:

                count = frame.locator(
                    "#rctbn8"
                ).count()

            except:
                count = -1

            print(
                "rctbn8数:",
                count
            )

            try:

                result_count = frame.get_by_text(
                    "競走結果",
                    exact=True
                ).count()

            except:
                result_count = -1

            print(
                "競走結果TEXT数:",
                result_count
            )

        # --------------------------------------------------
        # 競輪場抽出
        # --------------------------------------------------

        print()
        print("=" * 80)
        print("🔥 競輪場抽出")
        print("=" * 80)

        venue_elements = page.locator(
            "td.tdkeirin"
        )

        venue_count = venue_elements.count()

        venues = []

        for i in range(venue_count):

            el = venue_elements.nth(i)

            try:

                text = el.inner_text().strip()

            except:
                continue

            try:

                onclick = (
                    el.get_attribute("onclick")
                    or ""
                )

            except:
                onclick = ""

            if not text:
                continue

            if "raKeirinjoClick" not in onclick:
                continue

            venues.append(
                {
                    "name": text,
                    "onclick": onclick
                }
            )

            print(
                "🔥 競輪場:",
                text,
                onclick
            )

        # --------------------------------------------------
        # 2番目の競輪場へ切替
        # --------------------------------------------------

        if len(venues) < 2:

            print()
            print(
                "❌ 競輪場が2場見つかりません"
            )

            input(
                "確認できたらEnter："
            )

            browser.close()

            return

        target_venue = venues[1]

        print()
        print("=" * 80)
        print("🔥 競輪場切替")
        print("=" * 80)

        print(
            "切替先:",
            target_venue["name"]
        )

        print(
            "ONCLICK:",
            target_venue["onclick"]
        )

        page.evaluate(
            target_venue["onclick"]
        )

        page.wait_for_timeout(5000)

        print()
        print(
            "✅ 競輪場切替処理終了"
        )

        # --------------------------------------------------
        # 切替後FRAME確認
        # --------------------------------------------------

        print()
        print("=" * 80)
        print("🔥 切替後 FRAME一覧")
        print("=" * 80)

        print(
            "FRAME数:",
            len(page.frames)
        )

        total_rctbn8 = 0
        total_result_text = 0

        for i, frame in enumerate(page.frames):

            print()
            print("-" * 80)

            print(
                f"🔥 FRAME #{i}"
            )

            print(
                "NAME:",
                repr(frame.name)
            )

            print(
                "URL:",
                frame.url
            )

            try:

                count = frame.locator(
                    "#rctbn8"
                ).count()

            except Exception as e:

                count = -1

                print(
                    "rctbn8調査エラー:",
                    e
                )

            print(
                "rctbn8数:",
                count
            )

            if count > 0:

                total_rctbn8 += count

                for j in range(count):

                    el = frame.locator(
                        "#rctbn8"
                    ).nth(j)

                    try:

                        print(
                            "🔥 rctbn8 TEXT:",
                            repr(
                                el.inner_text().strip()
                            )
                        )

                    except:
                        pass

                    try:

                        print(
                            "🔥 rctbn8 CLASS:",
                            repr(
                                el.get_attribute("class")
                            )
                        )

                    except:
                        pass

                    try:

                        print(
                            "🔥 rctbn8 ONCLICK:",
                            repr(
                                el.get_attribute("onclick")
                            )
                        )

                    except:
                        pass

            try:

                result_elements = frame.get_by_text(
                    "競走結果",
                    exact=True
                )

                result_count = (
                    result_elements.count()
                )

            except Exception as e:

                result_count = -1

                print(
                    "競走結果TEXT調査エラー:",
                    e
                )

            print(
                "競走結果TEXT数:",
                result_count
            )

            if result_count > 0:

                total_result_text += result_count

                for j in range(result_count):

                    el = result_elements.nth(j)

                    try:

                        tag = el.evaluate(
                            "el => el.tagName"
                        )

                    except:
                        tag = ""

                    try:

                        element_id = (
                            el.get_attribute("id")
                            or ""
                        )

                    except:
                        element_id = ""

                    try:

                        class_name = (
                            el.get_attribute("class")
                            or ""
                        )

                    except:
                        class_name = ""

                    try:

                        onclick = (
                            el.get_attribute("onclick")
                            or ""
                        )

                    except:
                        onclick = ""

                    print()
                    print(
                        "🔥 競走結果ELEMENT発見"
                    )

                    print(
                        "TAG:",
                        repr(tag)
                    )

                    print(
                        "ID:",
                        repr(element_id)
                    )

                    print(
                        "CLASS:",
                        repr(class_name)
                    )

                    print(
                        "ONCLICK:",
                        repr(onclick)
                    )

        # --------------------------------------------------
        # 結果
        # --------------------------------------------------

        print()
        print("=" * 80)
        print("🔥 116テスト結果")
        print("=" * 80)

        print(
            "切替後FRAME数:",
            len(page.frames)
        )

        print(
            "全FRAME rctbn8数:",
            total_rctbn8
        )

        print(
            "全FRAME 競走結果TEXT数:",
            total_result_text
        )

        print()
        print("=" * 80)

        input(
            "確認できたらEnter："
        )

        browser.close()


if __name__ == "__main__":
    main()