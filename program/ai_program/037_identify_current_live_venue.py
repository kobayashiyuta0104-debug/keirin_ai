from pathlib import Path
from datetime import datetime
import json
import time

from playwright.sync_api import sync_playwright


# ============================================================
# 037
#
# LIVE切替後 現在開催 特定テスト
#
# 目的:
#   036ではBODY文字検索が毎回「函館」を誤検出した
#
#   今回は各LIVEボタン押下後に
#
#   ・PJ0314周辺
#   ・raceName系
#   ・joName系
#   ・place系
#   ・hidden系
#   ・タイトル系
#
#   を詳細取得
#
#   開催切替そのものが成功しているか特定する
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "037_current_live_venue"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_JSON = (
    OUT_DIR
    / "037_current_live_venue.json"
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
# LIVE開催一覧
# ============================================================


def get_live_venues(page):

    return page.evaluate(
        """
        () => {

            const results = [];

            const container = document.getElementById(
                "hcomRaceDiv"
            );

            if (!container) {

                return results;

            }

            const items = Array.from(
                container.querySelectorAll(
                    "li.kyotuHeader"
                )
            );

            for (
                let index = 0;
                index < items.length;
                index++
            ) {

                const item = items[index];

                const place = item.querySelector(
                    "p.place"
                );

                const liveButton = item.querySelector(
                    "button[id^='hcombtnLive']"
                );

                const hidden = item.querySelector(
                    "input[id^='hcomHdnTouhyouLive']"
                );

                if (
                    !place
                    ||
                    !liveButton
                ) {

                    continue;

                }

                results.push({

                    index:
                        index,

                    venue:
                        (
                            place.innerText || ""
                        ).trim(),

                    button_id:
                        liveButton.id || "",

                    onclick:
                        liveButton.getAttribute(
                            "onclick"
                        ) || "",

                    hidden_id:
                        hidden
                        ? hidden.id
                        : null,

                    hidden_value:
                        hidden
                        ? hidden.value
                        : null,

                });

            }

            return results;

        }
        """
    )


# ============================================================
# 現在DOM詳細取得
# ============================================================


def inspect_current_state(page):

    return page.evaluate(
        """
        () => {

            function elementInfo(el) {

                if (!el) {

                    return null;

                }

                return {

                    tag:
                        el.tagName || "",

                    id:
                        el.id || "",

                    class_name:
                        typeof el.className === "string"
                        ? el.className
                        : "",

                    text:
                        (
                            el.innerText || ""
                        ).trim().slice(
                            0,
                            5000
                        ),

                    value:
                        typeof el.value !== "undefined"
                        ? el.value
                        : null,

                    name:
                        el.getAttribute(
                            "name"
                        ),

                    jname:
                        el.getAttribute(
                            "jname"
                        ),

                    outer_html:
                        (
                            el.outerHTML || ""
                        ).slice(
                            0,
                            10000
                        )

                };

            }


            const output = {

                url:
                    location.href,

                title:
                    document.title,

                pj0314:
                    null,

                exact_ids:
                    {},

                id_candidates:
                    [],

                class_candidates:
                    [],

                text_candidates:
                    [],

                visible_place_elements:
                    []

            };


            // =================================================
            // PJ0314
            // =================================================


            const pj0314 = document.getElementById(
                "PJ0314"
            );


            if (pj0314) {

                output.pj0314 = {

                    text:
                        (
                            pj0314.innerText || ""
                        ).trim().slice(
                            0,
                            20000
                        ),

                    outer_html:
                        (
                            pj0314.outerHTML || ""
                        ).slice(
                            0,
                            50000
                        )

                };

            }


            // =================================================
            // 既知ID候補
            // =================================================


            const exactIds = [

                "raceName",
                "joName",
                "jyoName",
                "placeName",
                "denRaceInfo",
                "PJ0314",
                "PJ0315",
                "FPJ0314",
                "FPJ0315",
                "hhRaceBtn1",
                "hhRaceBtn2",
                "hhRaceBtn3",
                "hhRaceBtn4",
                "hhRaceBtn5",
                "hhRaceBtn6",
                "hhRaceBtn7",
                "hhRaceBtn8",
                "hhRaceBtn9",
                "hhRaceBtn10",
                "hhRaceBtn11",
                "hhRaceBtn12"

            ];


            for (
                const id
                of exactIds
            ) {

                const elements = Array.from(
                    document.querySelectorAll(
                        `[id="${id}"]`
                    )
                );

                if (
                    elements.length
                ) {

                    output.exact_ids[id] = (
                        elements.map(
                            elementInfo
                        )
                    );

                }

            }


            // =================================================
            // ID名候補
            // =================================================


            const allWithId = Array.from(
                document.querySelectorAll(
                    "[id]"
                )
            );


            for (
                const el
                of allWithId
            ) {

                const id = (
                    el.id || ""
                );

                const lower = id.toLowerCase();


                if (
                    lower.includes("race")
                    ||
                    lower.includes("jo")
                    ||
                    lower.includes("jyo")
                    ||
                    lower.includes("place")
                    ||
                    lower.includes("kaisai")
                    ||
                    lower.includes("venue")
                ) {

                    const info = elementInfo(
                        el
                    );

                    if (
                        info.text
                        ||
                        info.value
                    ) {

                        output.id_candidates.push(
                            info
                        );

                    }

                }


                if (
                    output.id_candidates.length
                    >= 300
                ) {

                    break;

                }

            }


            // =================================================
            // class候補
            // =================================================


            const classSelectors = [

                ".place",
                ".raceName",
                ".racename",
                ".joName",
                ".joname",
                ".jyoName",
                ".jyoname",
                ".kaisai",
                ".venue"

            ];


            for (
                const selector
                of classSelectors
            ) {

                const elements = Array.from(
                    document.querySelectorAll(
                        selector
                    )
                );


                for (
                    const el
                    of elements
                ) {

                    const info = elementInfo(
                        el
                    );

                    if (
                        info.text
                    ) {

                        output.class_candidates.push({

                            selector:
                                selector,

                            element:
                                info

                        });

                    }

                }

            }


            // =================================================
            // visible place
            // =================================================


            const placeElements = Array.from(
                document.querySelectorAll(
                    ".place"
                )
            );


            for (
                const el
                of placeElements
            ) {

                const rect = (
                    el.getBoundingClientRect()
                );

                const style = (
                    window.getComputedStyle(
                        el
                    )
                );


                const visible = (

                    rect.width > 0

                    &&

                    rect.height > 0

                    &&

                    style.display !== "none"

                    &&

                    style.visibility !== "hidden"

                );


                if (visible) {

                    output.visible_place_elements.push({

                        text:
                            (
                                el.innerText || ""
                            ).trim(),

                        id:
                            el.id || "",

                        class_name:
                            typeof el.className === "string"
                            ? el.className
                            : "",

                        parent_id:
                            el.parentElement
                            ? el.parentElement.id || ""
                            : "",

                        parent_class:
                            (
                                el.parentElement
                                &&
                                typeof el.parentElement.className
                                === "string"
                            )
                            ? el.parentElement.className
                            : "",

                        x:
                            rect.x,

                        y:
                            rect.y,

                        width:
                            rect.width,

                        height:
                            rect.height

                    });

                }

            }


            // =================================================
            // PJ0314近辺テキスト
            // =================================================


            if (pj0314) {

                let current = pj0314;

                for (
                    let level = 0;
                    level < 6;
                    level++
                ) {

                    if (!current) {

                        break;

                    }

                    const text = (
                        current.innerText || ""
                    ).trim();

                    output.text_candidates.push({

                        level:
                            level,

                        tag:
                            current.tagName || "",

                        id:
                            current.id || "",

                        class_name:
                            typeof current.className === "string"
                            ? current.className
                            : "",

                        text:
                            text.slice(
                                0,
                                20000
                            )

                    });

                    current = (
                        current.parentElement
                    );

                }

            }


            return output;

        }
        """
    )


# ============================================================
# PJ0314簡易比較用
# ============================================================


def make_pj_signature(state):

    pj = state.get(
        "pj0314"
    )

    if not pj:

        return None

    text = pj.get(
        "text",
        ""
    )

    return text[:1000]


# ============================================================
# main
# ============================================================


def main():

    print(
        "=== 037 LIVE切替後 現在開催特定テスト ==="
    )

    print()


    with sync_playwright() as p:

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


        print()

        print(
            "[4] LIVE開催一覧取得"
        )


        venues = get_live_venues(
            target_page
        )


        print()

        print(
            "VENUE COUNT:",
            len(venues)
        )


        for venue in venues:

            print()

            print(
                venue["index"],
                venue["venue"],
                venue["button_id"],
                venue["onclick"]
            )


        print()

        print(
            "[5] LIVE切替後DOM比較開始"
        )


        results = []

        previous_signature = None


        for number, venue in enumerate(
            venues,
            start=1,
        ):

            print()

            print(
                "#"
                * 100
            )

            print(
                f"VENUE {number}/{len(venues)}"
            )

            print(
                "REQUESTED:",
                venue["venue"]
            )

            print(
                "BUTTON:",
                venue["button_id"]
            )

            print(
                "#"
                * 100
            )


            try:

                target_page.locator(
                    "#"
                    +
                    venue["button_id"]
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

                click_error = repr(
                    e
                )


            state = inspect_current_state(
                target_page
            )


            signature = make_pj_signature(
                state
            )


            changed_from_previous = (

                previous_signature is not None

                and

                signature != previous_signature

            )


            pj_text = ""

            if state.get(
                "pj0314"
            ):

                pj_text = state[
                    "pj0314"
                ].get(
                    "text",
                    ""
                )


            requested_in_pj0314 = (

                venue["venue"]
                in
                pj_text

            )


            print()

            print(
                "CLICK STATUS:",
                click_status
            )

            print(
                "PJ0314 EXISTS:",
                state.get("pj0314")
                is not None
            )

            print(
                "PJ0314 CHANGED:",
                changed_from_previous
            )

            print(
                "REQUESTED VENUE IN PJ0314:",
                requested_in_pj0314
            )


            print()

            print(
                "★ PJ0314 TEXT TOP ★"
            )

            print(
                pj_text[:1500]
            )


            print()

            print(
                "★ VISIBLE PLACE TOP 30 ★"
            )


            for item in state[
                "visible_place_elements"
            ][:30]:

                print(

                    item["text"],

                    "| ID=",
                    item["id"],

                    "| PARENT ID=",
                    item["parent_id"],

                    "| PARENT CLASS=",
                    item["parent_class"],

                    "| X=",
                    round(
                        item["x"],
                        1
                    ),

                    "| Y=",
                    round(
                        item["y"],
                        1
                    )

                )


            results.append({

                "requested_venue":
                    venue["venue"],

                "venue":
                    venue,

                "click_status":
                    click_status,

                "click_error":
                    click_error,

                "pj0314_changed_from_previous":
                    changed_from_previous,

                "requested_venue_in_pj0314":
                    requested_in_pj0314,

                "state":
                    state

            })


            previous_signature = (
                signature
            )


            output = {

                "program":
                    "037_identify_current_live_venue.py",

                "captured_at":
                    datetime.now().isoformat(),

                "page_url":
                    target_page.url,

                "venue_count":
                    len(venues),

                "venues":
                    venues,

                "results":
                    results

            }


            save_json(
                OUT_JSON,
                output
            )


        print()

        print(
            "#"
            * 100
        )

        print(
            "037 最終結果"
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


        print()

        print(
            "★ DOM比較結果 ★"
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
                "CLICK:",
                result[
                    "click_status"
                ]
            )

            print(
                "PJ0314 CHANGED:",
                result[
                    "pj0314_changed_from_previous"
                ]
            )

            print(
                "VENUE IN PJ0314:",
                result[
                    "requested_venue_in_pj0314"
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
            "=== 037 完了 ==="
        )


if __name__ == "__main__":

    main()