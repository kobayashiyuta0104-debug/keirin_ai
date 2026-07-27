from pathlib import Path
from datetime import datetime
import json
import time

from playwright.sync_api import sync_playwright


# ============================================================
# 036
#
# LIVEボタン方式 開催切替テスト
#
# 035で判明:
#
#   開催名そのものはクリック対象ではない
#
#   各開催には
#
#       hcombtnLive0
#       hcombtnLive1
#       hcombtnLive2
#       ...
#
#   が存在
#
#   onclick:
#
#       pc0101_checkKaimeLive('0')
#       pc0101_checkKaimeLive('1')
#       ...
#
#   今回は実際のLIVEボタンをクリックして
#   開催が正しく切り替わるか確認する
#
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "036_live_venue_navigation"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_JSON = (
    OUT_DIR
    / "036_live_venue_navigation.json"
)

CDP_URL = "http://127.0.0.1:9222"

WAIT_SECONDS = 5


# ============================================================
# JSON保存
# ============================================================


def save_json(path, data):

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ============================================================
# 開催一覧取得
# ============================================================


def get_live_venues(page):

    return page.evaluate(
        """
        () => {

            const results = [];

            const container = (
                document.getElementById(
                    "hcomRaceDiv"
                )
            );

            if (!container) {

                return results;

            }

            const venueItems = Array.from(
                container.querySelectorAll(
                    "li.kyotuHeader"
                )
            );

            for (
                let index = 0;
                index < venueItems.length;
                index++
            ) {

                const item = venueItems[index];

                const placeElement = (
                    item.querySelector(
                        "p.place"
                    )
                );

                if (!placeElement) {

                    continue;

                }

                const venue = (
                    placeElement.innerText || ""
                ).trim();

                const liveButton = (
                    item.querySelector(
                        "button[id^='hcombtnLive']"
                    )
                );

                const hiddenInput = (
                    item.querySelector(
                        "input[id^='hcomHdnTouhyouLive']"
                    )
                );

                if (!liveButton) {

                    continue;

                }

                results.push({

                    index:
                        index,

                    venue:
                        venue,

                    live_button_id:
                        liveButton.id || "",

                    live_button_text:
                        (
                            liveButton.innerText || ""
                        ).trim(),

                    onclick:
                        liveButton.getAttribute(
                            "onclick"
                        ) || "",

                    hidden_id:
                        hiddenInput
                        ? hiddenInput.id
                        : null,

                    hidden_value:
                        hiddenInput
                        ? hiddenInput.value
                        : null,

                    item_class:
                        typeof item.className
                        === "string"
                        ? item.className
                        : "",

                });

            }

            return results;

        }
        """
    )


# ============================================================
# 現在開催取得
# ============================================================


def detect_current_venue(page):

    return page.evaluate(
        """
        () => {

            // ------------------------------------------------
            // racelive本体の開催名候補
            // ------------------------------------------------

            const selectors = [

                "#PJ0314 .place",

                "#PJ0315 .place",

                "#FPJ0314 .place",

                "#FPJ0315 .place"

            ];

            for (
                const selector
                of selectors
            ) {

                const elements = Array.from(
                    document.querySelectorAll(
                        selector
                    )
                );

                for (
                    const element
                    of elements
                ) {

                    const text = (
                        element.innerText || ""
                    ).trim();

                    if (
                        text
                        &&
                        !/^\\d+R$/.test(text)
                    ) {

                        return {

                            method:
                                selector,

                            venue:
                                text

                        };

                    }

                }

            }


            // ------------------------------------------------
            // ページ本文から競輪場情報候補
            // ------------------------------------------------

            const bodyText = (
                document.body.innerText || ""
            );

            const knownVenues = [

                "函館",
                "青森",
                "いわき平",
                "弥彦",
                "前橋",
                "取手",
                "宇都宮",
                "大宮",
                "西武園",
                "京王閣",
                "立川",
                "松戸",
                "千葉",
                "川崎",
                "平塚",
                "小田原",
                "伊東",
                "静岡",
                "名古屋",
                "岐阜",
                "大垣",
                "豊橋",
                "富山",
                "松阪",
                "四日市",
                "福井",
                "奈良",
                "向日町",
                "和歌山",
                "岸和田",
                "玉野",
                "広島",
                "防府",
                "高松",
                "小松島",
                "高知",
                "松山",
                "小倉",
                "久留米",
                "武雄",
                "佐世保",
                "別府",
                "熊本"

            ];

            // hcomRaceDivを除いたコピーで検索
            const clone = (
                document.body.cloneNode(true)
            );

            const header = (
                clone.querySelector(
                    "#hcomRaceDiv"
                )
            );

            if (header) {

                header.remove();

            }

            const mainText = (
                clone.innerText || ""
            );

            for (
                const venue
                of knownVenues
            ) {

                if (
                    mainText.includes(
                        venue
                    )
                ) {

                    return {

                        method:
                            "BODY_WITHOUT_HCOM_RACE_DIV",

                        venue:
                            venue

                    };

                }

            }

            return {

                method:
                    null,

                venue:
                    null

            };

        }
        """
    )


# ============================================================
# 並び予想存在確認
# ============================================================


def inspect_line_area(page):

    return page.evaluate(
        """
        () => {

            const bodyText = (
                document.body.innerText || ""
            );

            const pj0314 = (
                document.getElementById(
                    "PJ0314"
                )
            );

            let pjText = "";

            if (pj0314) {

                pjText = (
                    pj0314.innerText || ""
                );

            }

            return {

                pj0314_exists:
                    pj0314 !== null,

                pj0314_text_length:
                    pjText.length,

                body_has_line_prediction:
                    bodyText.includes(
                        "並び予想"
                    ),

                pj0314_has_line_prediction:
                    pjText.includes(
                        "並び予想"
                    ),

                pj0314_has_provider:
                    pjText.includes(
                        "情報提供"
                    ),

            };

        }
        """
    )


# ============================================================
# main
# ============================================================


def main():

    print(
        "=== 036 LIVEボタン方式 開催切替テスト ==="
    )

    print()


    with sync_playwright() as p:

        # ====================================================
        # Edge接続
        # ====================================================

        print(
            "[1] Edgeデバッグ接続"
        )

        browser = (
            p.chromium.connect_over_cdp(
                CDP_URL
            )
        )

        if not browser.contexts:

            print()

            print(
                "ERROR: Edge contextなし"
            )

            return


        # ====================================================
        # raceliveページ探索
        # ====================================================

        print()

        print(
            "[2] raceliveページ探索"
        )

        target_page = None

        for context in browser.contexts:

            for page in context.pages:

                try:

                    print()

                    print(
                        "PAGE:"
                    )

                    print(
                        page.url
                    )

                    if (
                        "keirin.jp"
                        in page.url.lower()
                        and
                        "racelive"
                        in page.url.lower()
                    ):

                        target_page = page

                except Exception:

                    pass


        if target_page is None:

            print()

            print(
                "ERROR: raceliveページなし"
            )

            return


        print()

        print(
            "[3] 対象ページ"
        )

        print(
            target_page.url
        )


        # ====================================================
        # 開催一覧
        # ====================================================

        print()

        print(
            "[4] LIVE開催一覧取得"
        )

        venues = (
            get_live_venues(
                target_page
            )
        )

        print()

        print(
            "VENUE COUNT:",
            len(venues)
        )

        print()

        print(
            "★ LIVE開催一覧 ★"
        )

        for venue in venues:

            print()

            print(
                "INDEX:",
                venue["index"]
            )

            print(
                "VENUE:",
                venue["venue"]
            )

            print(
                "BUTTON:",
                venue["live_button_id"]
            )

            print(
                "ONCLICK:",
                venue["onclick"]
            )

            print(
                "HIDDEN ID:",
                venue["hidden_id"]
            )

            print(
                "HIDDEN VALUE:",
                venue["hidden_value"]
            )


        # ====================================================
        # 開催切替テスト
        # ====================================================

        print()

        print(
            "[5] 開催切替テスト開始"
        )

        results = []


        for venue_index, venue in enumerate(
            venues,
            start=1,
        ):

            requested_venue = (
                venue["venue"]
            )

            button_id = (
                venue["live_button_id"]
            )

            print()

            print(
                "#"
                * 100
            )

            print(
                f"VENUE "
                f"{venue_index}/"
                f"{len(venues)}"
            )

            print(
                "REQUESTED:",
                requested_venue
            )

            print(
                "BUTTON:",
                button_id
            )

            print(
                "#"
                * 100
            )


            before_url = (
                target_page.url
            )

            before_venue = (
                detect_current_venue(
                    target_page
                )
            )

            print()

            print(
                "BEFORE URL:",
                before_url
            )

            print(
                "BEFORE VENUE:",
                before_venue
            )


            try:

                target_page.locator(
                    "#"
                    +
                    button_id
                ).click(
                    timeout=30000
                )

                time.sleep(
                    WAIT_SECONDS
                )

                click_status = (
                    "CLICK_OK"
                )

                click_error = None

            except Exception as e:

                click_status = (
                    "CLICK_ERROR"
                )

                click_error = (
                    repr(e)
                )


            after_url = (
                target_page.url
            )

            after_venue = (
                detect_current_venue(
                    target_page
                )
            )

            line_area = (
                inspect_line_area(
                    target_page
                )
            )


            print()

            print(
                "CLICK STATUS:",
                click_status
            )

            print(
                "AFTER URL:",
                after_url
            )

            print(
                "AFTER VENUE:",
                after_venue
            )

            print(
                "LINE AREA:"
            )

            print(
                json.dumps(
                    line_area,
                    ensure_ascii=False,
                    indent=2,
                )
            )


            detected_venue = (
                after_venue.get(
                    "venue"
                )
            )


            if (
                click_status
                !=
                "CLICK_OK"
            ):

                status = (
                    "CLICK_ERROR"
                )

            elif (
                detected_venue
                ==
                requested_venue
            ):

                status = (
                    "VENUE_SWITCH_OK"
                )

            else:

                status = (
                    "VENUE_SWITCH_UNKNOWN"
                )


            print()

            print(
                "STATUS:",
                status
            )


            results.append({

                "requested_venue":
                    requested_venue,

                "button":
                    venue,

                "before_url":
                    before_url,

                "before_venue":
                    before_venue,

                "click_status":
                    click_status,

                "click_error":
                    click_error,

                "after_url":
                    after_url,

                "after_venue":
                    after_venue,

                "line_area":
                    line_area,

                "status":
                    status,

            })


        # ====================================================
        # 保存
        # ====================================================

        output = {

            "program":
                "036_test_live_venue_navigation.py",

            "captured_at":
                datetime.now().isoformat(),

            "page_url":
                target_page.url,

            "venue_count":
                len(venues),

            "venues":
                venues,

            "results":
                results,

        }

        save_json(
            OUT_JSON,
            output,
        )


        # ====================================================
        # 最終結果
        # ====================================================

        print()

        print(
            "#"
            * 100
        )

        print(
            "036 最終結果"
        )

        print(
            "#"
            * 100
        )

        print()

        print(
            "VENUE COUNT:",
            len(venues)
        )

        print(
            "SWITCH OK:",
            len([
                result
                for result in results
                if result["status"]
                ==
                "VENUE_SWITCH_OK"
            ])
        )

        print(
            "SWITCH UNKNOWN:",
            len([
                result
                for result in results
                if result["status"]
                ==
                "VENUE_SWITCH_UNKNOWN"
            ])
        )

        print(
            "CLICK ERROR:",
            len([
                result
                for result in results
                if result["status"]
                ==
                "CLICK_ERROR"
            ])
        )


        print()

        print(
            "★ 開催切替結果 ★"
        )

        for result in results:

            print()

            print(
                "-"
                * 100
            )

            print(
                "REQUESTED:",
                result[
                    "requested_venue"
                ]
            )

            print(
                "DETECTED:",
                result[
                    "after_venue"
                ].get(
                    "venue"
                )
            )

            print(
                "METHOD:",
                result[
                    "after_venue"
                ].get(
                    "method"
                )
            )

            print(
                "STATUS:",
                result[
                    "status"
                ]
            )

            print(
                "LINE PREDICTION:",
                result[
                    "line_area"
                ][
                    "pj0314_has_line_prediction"
                ]
            )


        print()

        print(
            "保存先:"
        )

        print(
            OUT_JSON
        )

        print()

        print(
            "=== 036 完了 ==="
        )


if __name__ == "__main__":

    main()