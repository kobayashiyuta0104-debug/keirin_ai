from playwright.sync_api import sync_playwright


def main():

    print("=== 117 切替後 競走結果ELEMENT詳細調査 ===")

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
        # 競輪場抽出
        # --------------------------------------------------

        print()
        print("=" * 80)
        print("🔥 競輪場抽出")
        print("=" * 80)

        venue_elements = page.locator(
            "td.tdkeirin"
        )

        venues = []

        for i in range(
            venue_elements.count()
        ):

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
            print("❌ 競輪場が2場ありません")

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
        print("✅ 切替終了")

        # --------------------------------------------------
        # 全FRAMEから競走結果を探す
        # --------------------------------------------------

        print()
        print("=" * 80)
        print("🔥 競走結果ELEMENT詳細調査")
        print("=" * 80)

        hit_count = 0

        for frame_index, frame in enumerate(
            page.frames
        ):

            try:

                elements = frame.get_by_text(
                    "競走結果",
                    exact=True
                )

                count = elements.count()

            except:
                continue

            if count == 0:
                continue

            print()
            print("#" * 80)

            print(
                "🔥 発見FRAME:",
                frame_index
            )

            print(
                "FRAME NAME:",
                repr(frame.name)
            )

            print(
                "FRAME URL:",
                frame.url
            )

            print(
                "FRAME内 競走結果数:",
                count
            )

            print("#" * 80)

            for i in range(count):

                hit_count += 1

                el = elements.nth(i)

                print()
                print("=" * 80)

                print(
                    f"🔥 競走結果 HIT #{hit_count}"
                )

                print(
                    "FRAME INDEX:",
                    frame_index
                )

                try:

                    print(
                        "TEXT:",
                        repr(
                            el.inner_text().strip()
                        )
                    )

                except Exception as e:

                    print(
                        "TEXT ERROR:",
                        e
                    )

                try:

                    print(
                        "TAG:",
                        repr(
                            el.evaluate(
                                "el => el.tagName"
                            )
                        )
                    )

                except Exception as e:

                    print(
                        "TAG ERROR:",
                        e
                    )

                try:

                    print(
                        "ID:",
                        repr(
                            el.get_attribute("id")
                        )
                    )

                except Exception as e:

                    print(
                        "ID ERROR:",
                        e
                    )

                try:

                    print(
                        "CLASS:",
                        repr(
                            el.get_attribute("class")
                        )
                    )

                except Exception as e:

                    print(
                        "CLASS ERROR:",
                        e
                    )

                try:

                    print(
                        "ONCLICK:",
                        repr(
                            el.get_attribute("onclick")
                        )
                    )

                except Exception as e:

                    print(
                        "ONCLICK ERROR:",
                        e
                    )

                try:

                    print(
                        "VISIBLE:",
                        el.is_visible()
                    )

                except Exception as e:

                    print(
                        "VISIBLE ERROR:",
                        e
                    )

                try:

                    print(
                        "ENABLED:",
                        el.is_enabled()
                    )

                except Exception as e:

                    print(
                        "ENABLED ERROR:",
                        e
                    )

                # ------------------------------------------
                # 親要素
                # ------------------------------------------

                try:

                    parent = el.locator("..")

                    print()
                    print("🔥 親要素")

                    print(
                        "PARENT TAG:",
                        repr(
                            parent.evaluate(
                                "el => el.tagName"
                            )
                        )
                    )

                    print(
                        "PARENT ID:",
                        repr(
                            parent.get_attribute("id")
                        )
                    )

                    print(
                        "PARENT CLASS:",
                        repr(
                            parent.get_attribute("class")
                        )
                    )

                    print(
                        "PARENT ONCLICK:",
                        repr(
                            parent.get_attribute("onclick")
                        )
                    )

                except Exception as e:

                    print(
                        "PARENT ERROR:",
                        e
                    )

                # ------------------------------------------
                # HTML
                # ------------------------------------------

                try:

                    html = el.evaluate(
                        "el => el.outerHTML"
                    )

                    print()
                    print("🔥 OUTER HTML")
                    print(html)

                except Exception as e:

                    print(
                        "HTML ERROR:",
                        e
                    )

        # --------------------------------------------------
        # 結果
        # --------------------------------------------------

        print()
        print("=" * 80)
        print("🔥 117テスト結果")
        print("=" * 80)

        print(
            "競走結果ELEMENT総数:",
            hit_count
        )

        print()
        print("=" * 80)

        input(
            "確認できたらEnter："
        )

        browser.close()


if __name__ == "__main__":
    main()