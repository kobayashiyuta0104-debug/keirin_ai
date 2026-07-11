from pathlib import Path
from datetime import datetime
import json
import time

from playwright.sync_api import sync_playwright


# ============================================================
# 039
#
# 特殊ライン / ジカ競り DOM詳細調査
#
# 038 VALIDATION ERROR 9レースだけ調査
#
# 確認済み:
#
#   大垣8R     ジカ競り
#   いわき平1R ジカ競り
#
# 目的:
#
#   ・ジカ競りDOM表現の特定
#   ・通常ラインとの違い確認
#   ・snum座標取得
#   ・親 / 兄弟DOM取得
#   ・画像取得
#   ・class / style取得
#   ・PJ0314 HTML保存
#
# 今回は解析ロジックを修正しない
# 調査専用
#
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "039_special_line_dom"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_JSON = (
    OUT_DIR
    / "039_special_line_dom.json"
)

CDP_URL = "http://127.0.0.1:9222"

WAIT_SECONDS = 3


# ============================================================
# 038 VALIDATION ERROR対象
# ============================================================


TARGET_RACES = [

    {
        "venue": "伊東",
        "race_no": 5,
        "known_special": None,
    },

    {
        "venue": "大垣",
        "race_no": 8,
        "known_special": "ジカ競り",
    },

    {
        "venue": "大垣",
        "race_no": 11,
        "known_special": None,
    },

    {
        "venue": "大垣",
        "race_no": 12,
        "known_special": None,
    },

    {
        "venue": "いわき平",
        "race_no": 1,
        "known_special": "ジカ競り",
    },

    {
        "venue": "いわき平",
        "race_no": 2,
        "known_special": None,
    },

    {
        "venue": "いわき平",
        "race_no": 3,
        "known_special": None,
    },

    {
        "venue": "いわき平",
        "race_no": 6,
        "known_special": None,
    },

    {
        "venue": "名古屋",
        "race_no": 6,
        "known_special": None,
    },

]


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

            const container = (
                document.getElementById(
                    "hcomRaceDiv"
                )
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

                const place = (
                    item.querySelector(
                        "p.place"
                    )
                );

                const liveButton = (
                    item.querySelector(
                        "button[id^='hcombtnLive']"
                    )
                );

                const hidden = (
                    item.querySelector(
                        "input[id^='hcomHdnTouhyouLive']"
                    )
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
# PJ0314署名
# ============================================================


def get_pj_signature(page):

    try:

        return page.evaluate(
            """
            () => {

                const pj = (
                    document.getElementById(
                        "PJ0314"
                    )
                );

                if (!pj) {

                    return null;

                }

                return (
                    pj.innerText || ""
                );

            }
            """
        )

    except Exception:

        return None


# ============================================================
# DOM変化待ち
# ============================================================


def wait_dom_change(
    page,
    before_signature,
    timeout_seconds=15,
):

    start = time.time()

    while (
        time.time() - start
        <
        timeout_seconds
    ):

        current = (
            get_pj_signature(
                page
            )
        )

        if (
            current is not None
            and
            current != before_signature
        ):

            time.sleep(1)

            return {

                "changed": True,

                "wait_seconds": round(
                    time.time() - start,
                    3,
                ),

            }

        time.sleep(0.5)

    return {

        "changed": False,

        "wait_seconds": round(
            time.time() - start,
            3,
        ),

    }


# ============================================================
# 特殊ラインDOM詳細取得
# ============================================================


def inspect_special_line_dom(page):

    return page.evaluate(
        """
        () => {

            function attributesToObject(el) {

                const result = {};

                if (!el) {

                    return result;

                }

                for (
                    const attr
                    of Array.from(
                        el.attributes || []
                    )
                ) {

                    result[
                        attr.name
                    ] = attr.value;

                }

                return result;

            }


            function rectInfo(el) {

                if (!el) {

                    return null;

                }

                const rect = (
                    el.getBoundingClientRect()
                );

                return {

                    x:
                        rect.x,

                    y:
                        rect.y,

                    width:
                        rect.width,

                    height:
                        rect.height,

                    top:
                        rect.top,

                    right:
                        rect.right,

                    bottom:
                        rect.bottom,

                    left:
                        rect.left,

                };

            }


            function computedStyleInfo(el) {

                if (!el) {

                    return null;

                }

                const style = (
                    window.getComputedStyle(
                        el
                    )
                );

                return {

                    display:
                        style.display,

                    position:
                        style.position,

                    top:
                        style.top,

                    left:
                        style.left,

                    right:
                        style.right,

                    bottom:
                        style.bottom,

                    margin:
                        style.margin,

                    padding:
                        style.padding,

                    transform:
                        style.transform,

                    float:
                        style.float,

                    clear:
                        style.clear,

                    z_index:
                        style.zIndex,

                    background_image:
                        style.backgroundImage,

                    background_color:
                        style.backgroundColor,

                    border:
                        style.border,

                    visibility:
                        style.visibility,

                    opacity:
                        style.opacity,

                };

            }


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
                        typeof el.className
                        === "string"
                        ? el.className
                        : "",

                    text:
                        (
                            el.innerText || ""
                        ).trim().slice(
                            0,
                            5000
                        ),

                    attributes:
                        attributesToObject(
                            el
                        ),

                    rect:
                        rectInfo(
                            el
                        ),

                    computed_style:
                        computedStyleInfo(
                            el
                        ),

                    outer_html:
                        (
                            el.outerHTML || ""
                        ).slice(
                            0,
                            30000
                        ),

                };

            }


            const output = {

                pj0314_exists:
                    false,

                line_target_exists:
                    false,

                prediction_type:
                    null,

                provider:
                    null,

                pj0314_text:
                    null,

                pj0314_html:
                    null,

                target_text:
                    null,

                target_html:
                    null,

                snum_count:
                    0,

                snum_elements:
                    [],

                all_target_children:
                    [],

                image_elements:
                    [],

                background_image_elements:
                    [],

                special_text_candidates:
                    [],

            };


            const pj0314 = (
                document.getElementById(
                    "PJ0314"
                )
            );


            if (!pj0314) {

                return output;

            }


            output.pj0314_exists = true;

            output.pj0314_text = (
                pj0314.innerText || ""
            ).slice(
                0,
                50000
            );

            output.pj0314_html = (
                pj0314.outerHTML || ""
            ).slice(
                0,
                300000
            );


            // =================================================
            // 並び予想TARGET
            // =================================================


            let target = null;


            const tables = Array.from(
                pj0314.querySelectorAll(
                    "table"
                )
            );


            for (
                const table
                of tables
            ) {

                const text = (
                    table.innerText || ""
                );


                if (
                    text.includes(
                        "並び予想"
                    )
                    &&
                    text.includes(
                        "情報提供"
                    )
                ) {

                    target = table;

                    break;

                }

            }


            if (!target) {

                const candidates = Array.from(
                    pj0314.querySelectorAll(
                        "*"
                    )
                ).filter(
                    el => {

                        const text = (
                            el.innerText || ""
                        ).trim();

                        return (
                            text.includes(
                                "並び予想"
                            )
                            &&
                            text.includes(
                                "情報提供"
                            )
                        );

                    }
                );


                candidates.sort(
                    (
                        a,
                        b
                    ) => (

                        (
                            a.innerText || ""
                        ).length

                        -

                        (
                            b.innerText || ""
                        ).length

                    )
                );


                if (
                    candidates.length
                ) {

                    target = (
                        candidates[0]
                    );

                }

            }


            if (!target) {

                return output;

            }


            output.line_target_exists = true;

            output.target_text = (
                target.innerText || ""
            ).slice(
                0,
                50000
            );

            output.target_html = (
                target.outerHTML || ""
            ).slice(
                0,
                300000
            );


            // =================================================
            // TYPE / PROVIDER
            // =================================================


            const fullText = (
                target.innerText || ""
            );


            const typeMatch = (
                fullText.match(
                    /(?:二分戦|三分戦|四分戦|五分戦|コマ切れ)/
                )
            );


            if (typeMatch) {

                output.prediction_type = (
                    typeMatch[0]
                );

            }


            const providerMatch = (
                fullText.match(
                    /情報提供\\s*[：:]\\s*([^\\n\\r]+)/
                )
            );


            if (providerMatch) {

                output.provider = (
                    providerMatch[1]
                ).trim();

            }


            // =================================================
            // SNUM詳細
            // =================================================


            const snums = Array.from(
                target.querySelectorAll(
                    ".snum"
                )
            );


            output.snum_count = (
                snums.length
            );


            for (
                let index = 0;
                index < snums.length;
                index++
            ) {

                const el = snums[index];


                const item = {

                    index:
                        index,

                    element:
                        elementInfo(
                            el
                        ),

                    parents:
                        [],

                    siblings:
                        [],

                    previous_element:
                        null,

                    next_element:
                        null,

                };


                // ---------------------------------------------
                // 親6階層
                // ---------------------------------------------


                let current = el;


                for (
                    let level = 0;
                    level < 6;
                    level++
                ) {

                    if (!current) {

                        break;

                    }


                    item.parents.push({

                        level:
                            level,

                        element:
                            elementInfo(
                                current
                            ),

                    });


                    current = (
                        current.parentElement
                    );

                }


                // ---------------------------------------------
                // 兄弟
                // ---------------------------------------------


                if (
                    el.parentElement
                ) {

                    item.siblings = Array.from(
                        el.parentElement.children
                    ).map(
                        (
                            sibling,
                            siblingIndex
                        ) => ({

                            index:
                                siblingIndex,

                            is_self:
                                sibling === el,

                            element:
                                elementInfo(
                                    sibling
                                ),

                        })
                    );

                }


                item.previous_element = (
                    elementInfo(
                        el.previousElementSibling
                    )
                );


                item.next_element = (
                    elementInfo(
                        el.nextElementSibling
                    )
                );


                output.snum_elements.push(
                    item
                );

            }


            // =================================================
            // TARGET内 全要素
            // =================================================


            const allChildren = Array.from(
                target.querySelectorAll(
                    "*"
                )
            );


            for (
                let index = 0;
                index < allChildren.length;
                index++
            ) {

                const el = allChildren[index];

                output.all_target_children.push({

                    index:
                        index,

                    element:
                        elementInfo(
                            el
                        ),

                });


                if (
                    output.all_target_children.length
                    >= 1000
                ) {

                    break;

                }

            }


            // =================================================
            // IMG
            // =================================================


            const images = Array.from(
                target.querySelectorAll(
                    "img"
                )
            );


            for (
                let index = 0;
                index < images.length;
                index++
            ) {

                const img = images[index];

                output.image_elements.push({

                    index:
                        index,

                    src:
                        img.src || "",

                    alt:
                        img.alt || "",

                    title:
                        img.title || "",

                    element:
                        elementInfo(
                            img
                        ),

                    parent:
                        elementInfo(
                            img.parentElement
                        ),

                });

            }


            // =================================================
            // background-image
            // =================================================


            for (
                let index = 0;
                index < allChildren.length;
                index++
            ) {

                const el = allChildren[index];

                const style = (
                    window.getComputedStyle(
                        el
                    )
                );

                if (
                    style.backgroundImage
                    &&
                    style.backgroundImage
                    !== "none"
                ) {

                    output.background_image_elements.push({

                        index:
                            index,

                        background_image:
                            style.backgroundImage,

                        element:
                            elementInfo(
                                el
                            ),

                        parent:
                            elementInfo(
                                el.parentElement
                            ),

                    });

                }

            }


            // =================================================
            // 特殊文字候補
            // =================================================


            const specialWords = [

                "競",
                "ジカ",
                "直",
                "単騎",
                "番手",
                "並走",
                "競り",
                "競合",

            ];


            for (
                let index = 0;
                index < allChildren.length;
                index++
            ) {

                const el = allChildren[index];

                const text = (
                    el.innerText || ""
                ).trim();


                if (!text) {

                    continue;

                }


                if (
                    specialWords.some(
                        word => (
                            text.includes(
                                word
                            )
                        )
                    )
                ) {

                    output.special_text_candidates.push({

                        index:
                            index,

                        matched_words:
                            specialWords.filter(
                                word => (
                                    text.includes(
                                        word
                                    )
                                )
                            ),

                        element:
                            elementInfo(
                                el
                            ),

                    });

                }

            }


            return output;

        }
        """
    )


# ============================================================
# SNUM簡易表示
# ============================================================


def print_snum_summary(dom_data):

    snums = (
        dom_data.get(
            "snum_elements",
            []
        )
    )


    print()

    print(
        "★ SNUM座標一覧 ★"
    )


    for item in snums:

        element = (
            item.get(
                "element",
                {}
            )
        )

        rect = (
            element.get(
                "rect"
            )
            or
            {}
        )


        print(

            "INDEX:",
            item.get(
                "index"
            ),

            "| TEXT:",
            element.get(
                "text"
            ),

            "| CLASS:",
            element.get(
                "class_name"
            ),

            "| X:",
            round(
                rect.get(
                    "x",
                    0
                ),
                2,
            ),

            "| Y:",
            round(
                rect.get(
                    "y",
                    0
                ),
                2,
            ),

            "| W:",
            round(
                rect.get(
                    "width",
                    0
                ),
                2,
            ),

            "| H:",
            round(
                rect.get(
                    "height",
                    0
                ),
                2,
            ),

        )


# ============================================================
# main
# ============================================================


def main():

    print(
        "=== 039 特殊ライン / ジカ競り DOM詳細調査 ==="
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
        # racelive探索
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
        # LIVE開催一覧
        # ====================================================


        print()

        print(
            "[4] LIVE開催一覧取得"
        )


        live_venues = (
            get_live_venues(
                target_page
            )
        )


        venue_map = {

            venue["venue"]:
                venue

            for venue in live_venues

        }


        print()

        print(
            "VENUE COUNT:",
            len(live_venues)
        )


        for venue in live_venues:

            print(

                venue["venue"],

                "->",

                venue["button_id"]

            )


        # ====================================================
        # 対象9レース巡回
        # ====================================================


        print()

        print(
            "[5] 対象レース調査開始"
        )


        results = []


        for target_number, target in enumerate(
            TARGET_RACES,
            start=1,
        ):

            venue_name = (
                target["venue"]
            )

            race_no = (
                target["race_no"]
            )

            known_special = (
                target["known_special"]
            )


            print()

            print(
                "#"
                * 100
            )

            print(
                f"TARGET "
                f"{target_number}/"
                f"{len(TARGET_RACES)}"
            )

            print(
                "VENUE:",
                venue_name
            )

            print(
                "RACE:",
                f"{race_no}R"
            )

            print(
                "KNOWN SPECIAL:",
                known_special
            )

            print(
                "#"
                * 100
            )


            # ================================================
            # 開催確認
            # ================================================


            venue = (
                venue_map.get(
                    venue_name
                )
            )


            if not venue:

                print()

                print(
                    "VENUE NOT FOUND"
                )


                results.append({

                    "venue":
                        venue_name,

                    "race_no":
                        race_no,

                    "known_special":
                        known_special,

                    "status":
                        "VENUE_NOT_FOUND",

                })


                continue


            # ================================================
            # 開催クリック
            # ================================================


            before_venue_signature = (
                get_pj_signature(
                    target_page
                )
            )


            try:

                target_page.locator(
                    "#"
                    +
                    venue["button_id"]
                ).click(
                    timeout=30000
                )


                venue_click_status = (
                    "CLICK_OK"
                )

                venue_click_error = None


            except Exception as e:

                venue_click_status = (
                    "CLICK_ERROR"
                )

                venue_click_error = (
                    repr(e)
                )


            if (
                venue_click_status
                ==
                "CLICK_ERROR"
            ):

                print()

                print(
                    "VENUE CLICK ERROR:"
                )

                print(
                    venue_click_error
                )


                results.append({

                    "venue":
                        venue_name,

                    "race_no":
                        race_no,

                    "known_special":
                        known_special,

                    "status":
                        "VENUE_CLICK_ERROR",

                    "error":
                        venue_click_error,

                })


                continue


            venue_wait = (
                wait_dom_change(
                    target_page,
                    before_venue_signature,
                )
            )


            print()

            print(
                "VENUE DOM CHANGED:",
                venue_wait["changed"]
            )

            print(
                "VENUE WAIT:",
                venue_wait["wait_seconds"]
            )


            time.sleep(
                1
            )


            # ================================================
            # Rクリック
            # ================================================


            race_button_id = (
                "hhRaceBtn"
                +
                str(
                    race_no
                )
            )


            race_button_count = (
                target_page.locator(
                    "#"
                    +
                    race_button_id
                ).count()
            )


            if (
                race_button_count
                == 0
            ):

                print()

                print(
                    "RACE BUTTON NOT FOUND:"
                )

                print(
                    race_button_id
                )


                results.append({

                    "venue":
                        venue_name,

                    "race_no":
                        race_no,

                    "known_special":
                        known_special,

                    "status":
                        "RACE_BUTTON_NOT_FOUND",

                })


                continue


            before_race_signature = (
                get_pj_signature(
                    target_page
                )
            )


            try:

                target_page.locator(
                    "#"
                    +
                    race_button_id
                ).click(
                    timeout=30000
                )


                race_click_status = (
                    "CLICK_OK"
                )

                race_click_error = None


            except Exception as e:

                race_click_status = (
                    "CLICK_ERROR"
                )

                race_click_error = (
                    repr(e)
                )


            if (
                race_click_status
                ==
                "CLICK_ERROR"
            ):

                print()

                print(
                    "RACE CLICK ERROR:"
                )

                print(
                    race_click_error
                )


                results.append({

                    "venue":
                        venue_name,

                    "race_no":
                        race_no,

                    "known_special":
                        known_special,

                    "status":
                        "RACE_CLICK_ERROR",

                    "error":
                        race_click_error,

                })


                continue


            race_wait = (
                wait_dom_change(
                    target_page,
                    before_race_signature,
                )
            )


            print()

            print(
                "RACE DOM CHANGED:",
                race_wait["changed"]
            )

            print(
                "RACE WAIT:",
                race_wait["wait_seconds"]
            )


            time.sleep(
                WAIT_SECONDS
            )


            # ================================================
            # DOM詳細取得
            # ================================================


            try:

                dom_data = (
                    inspect_special_line_dom(
                        target_page
                    )
                )


                status = (
                    "DOM_CAPTURED"
                )

                dom_error = None


            except Exception as e:

                dom_data = None

                status = (
                    "DOM_ERROR"
                )

                dom_error = (
                    repr(e)
                )


            print()

            print(
                "STATUS:",
                status
            )


            if dom_data:

                print()

                print(
                    "TYPE:",
                    dom_data.get(
                        "prediction_type"
                    )
                )

                print(
                    "PROVIDER:",
                    dom_data.get(
                        "provider"
                    )
                )

                print(
                    "SNUM COUNT:",
                    dom_data.get(
                        "snum_count"
                    )
                )

                print(
                    "IMG COUNT:",
                    len(
                        dom_data.get(
                            "image_elements",
                            []
                        )
                    )
                )

                print(
                    "BACKGROUND IMAGE COUNT:",
                    len(
                        dom_data.get(
                            "background_image_elements",
                            []
                        )
                    )
                )

                print(
                    "SPECIAL TEXT COUNT:",
                    len(
                        dom_data.get(
                            "special_text_candidates",
                            []
                        )
                    )
                )


                print_snum_summary(
                    dom_data
                )


            result = {

                "venue":
                    venue_name,

                "race_no":
                    race_no,

                "race_key":
                    (
                        f"{venue_name}_"
                        f"{race_no}R"
                    ),

                "known_special":
                    known_special,

                "venue":
                    venue_name,

                "venue_button":
                    venue,

                "venue_wait":
                    venue_wait,

                "race_button_id":
                    race_button_id,

                "race_wait":
                    race_wait,

                "status":
                    status,

                "error":
                    dom_error,

                "dom":
                    dom_data,

            }


            results.append(
                result
            )


            output = {

                "program":
                    "039_inspect_special_line_dom.py",

                "captured_at":
                    datetime.now().isoformat(),

                "target_count":
                    len(
                        TARGET_RACES
                    ),

                "known_jika_races": [

                    "大垣_8R",

                    "いわき平_1R",

                ],

                "results":
                    results,

            }


            save_json(
                OUT_JSON,
                output
            )


        # ====================================================
        # 最終保存
        # ====================================================


        output = {

            "program":
                "039_inspect_special_line_dom.py",

            "captured_at":
                datetime.now().isoformat(),

            "target_count":
                len(
                    TARGET_RACES
                ),

            "known_jika_races": [

                "大垣_8R",

                "いわき平_1R",

            ],

            "results":
                results,

        }


        save_json(
            OUT_JSON,
            output
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
            "039 最終結果"
        )

        print(
            "#"
            * 100
        )


        print()

        print(
            "TARGET COUNT:",
            len(
                TARGET_RACES
            )
        )

        print(
            "DOM CAPTURED:",
            len([
                result
                for result in results
                if result.get(
                    "status"
                )
                ==
                "DOM_CAPTURED"
            ])
        )

        print(
            "ERROR:",
            len([
                result
                for result in results
                if result.get(
                    "status"
                )
                !=
                "DOM_CAPTURED"
            ])
        )


        print()

        print(
            "★ 調査結果 ★"
        )


        for result in results:

            print()

            print(
                "-"
                * 100
            )

            print(
                "RACE:",
                result.get(
                    "race_key"
                )
            )

            print(
                "KNOWN SPECIAL:",
                result.get(
                    "known_special"
                )
            )

            print(
                "STATUS:",
                result.get(
                    "status"
                )
            )


            dom_data = (
                result.get(
                    "dom"
                )
            )


            if dom_data:

                print(
                    "TYPE:",
                    dom_data.get(
                        "prediction_type"
                    )
                )

                print(
                    "SNUM COUNT:",
                    dom_data.get(
                        "snum_count"
                    )
                )

                print(
                    "IMG COUNT:",
                    len(
                        dom_data.get(
                            "image_elements",
                            []
                        )
                    )
                )

                print(
                    "BACKGROUND IMAGE COUNT:",
                    len(
                        dom_data.get(
                            "background_image_elements",
                            []
                        )
                    )
                )

                print(
                    "SPECIAL TEXT COUNT:",
                    len(
                        dom_data.get(
                            "special_text_candidates",
                            []
                        )
                    )
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
            "=== 039 完了 ==="
        )


if __name__ == "__main__":

    main()