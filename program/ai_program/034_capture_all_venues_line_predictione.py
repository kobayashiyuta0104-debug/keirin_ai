from pathlib import Path
from datetime import datetime
import json
import re
import time

from playwright.sync_api import sync_playwright


# ============================================================
# 034
#
# 対象日 全開催・全R 並び予想 自動取得テスト
#
# 目的:
#   ・Edgeデバッグ接続
#   ・現在開いているKEIRIN.JP raceliveページを使用
#   ・現在表示日の開催ボタンを取得
#   ・開催を順番にクリック
#   ・各開催1R～12Rを巡回
#   ・033方式で並び予想取得
#   ・base_color_0をライン境界として解析
#   ・提供元取得
#   ・二分戦 / 三分戦 / 四分戦 / 五分戦 / コマ切れ取得
#   ・全開催を1個のJSONへ保存
#
# 注意:
#   今回は「現在画面に表示されている日」が対象
#
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_predictions"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_JSON = (
    OUT_DIR
    / "034_all_venues_line_predictions.json"
)


CDP_URL = "http://127.0.0.1:9222"

VENUE_CLICK_WAIT_SECONDS = 4

RACE_CLICK_WAIT_SECONDS = 2


KNOWN_VENUES = [

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
    "熊本",

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
# 安全取得
# ============================================================


def safe_title(page):

    try:

        return page.title()

    except Exception:

        return ""


def safe_body_text(page):

    try:

        return page.locator(
            "body"
        ).inner_text()

    except Exception:

        return ""


# ============================================================
# 日付取得
# ============================================================


def extract_race_date(text):

    patterns = [

        r"(20\d{2})[/-](\d{1,2})[/-](\d{1,2})",

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            text,
        )


        if match:

            year = int(
                match.group(1)
            )

            month = int(
                match.group(2)
            )

            day = int(
                match.group(3)
            )


            return (
                f"{year:04d}"
                f"{month:02d}"
                f"{day:02d}"
            )


    return None


# ============================================================
# race_key
# ============================================================


def build_race_key(
    race_date,
    venue,
    race_no,
):

    if (
        not race_date
        or not venue
        or race_no is None
    ):

        return None


    return (
        f"{race_date}_"
        f"{venue}_"
        f"{race_no}R"
    )


# ============================================================
# 開催ボタン探索
# ============================================================


def get_venue_buttons(page):

    return page.evaluate(
        """
        (knownVenues) => {

            const results = [];

            const all = Array.from(
                document.querySelectorAll(
                    "body *"
                )
            );


            for (
                const venue
                of knownVenues
            ) {

                const candidates = (
                    all.filter(
                        el => {

                            const text = (
                                el.innerText || ""
                            ).trim();


                            if (
                                text !== venue
                            ) {

                                return false;

                            }


                            const tag = (
                                el.tagName || ""
                            ).toUpperCase();


                            const role = (
                                el.getAttribute(
                                    "role"
                                )
                                || ""
                            );


                            const onclick = (
                                el.getAttribute(
                                    "onclick"
                                )
                                || ""
                            );


                            const className = (
                                typeof el.className
                                === "string"
                                ? el.className
                                : ""
                            );


                            return (

                                tag === "A"

                                ||

                                tag === "BUTTON"

                                ||

                                role === "button"

                                ||

                                onclick.length > 0

                                ||

                                className.toLowerCase()
                                .includes("btn")

                                ||

                                className.toLowerCase()
                                .includes("tab")

                                ||

                                className.toLowerCase()
                                .includes("jo")

                            );

                        }
                    )
                );


                if (!candidates.length) {

                    continue;

                }


                const element = (
                    candidates[0]
                );


                results.push({

                    venue:
                        venue,

                    tag_name:
                        element.tagName || "",

                    id:
                        element.id || "",

                    class_name:
                        typeof element.className
                        === "string"
                        ? element.className
                        : "",

                    text:
                        (
                            element.innerText || ""
                        ).trim(),

                    href:
                        element.href || "",

                    onclick:
                        element.getAttribute(
                            "onclick"
                        )
                        || "",

                    data_encp:
                        element.getAttribute(
                            "data-encp"
                        ),

                    outer_html:
                        (
                            element.outerHTML || ""
                        ).slice(
                            0,
                            10000
                        )

                });

            }


            return results;

        }
        """,
        KNOWN_VENUES,
    )


# ============================================================
# 開催ボタンクリック
# ============================================================


def click_venue(
    page,
    venue,
):

    return page.evaluate(
        """
        (venue) => {

            const all = Array.from(
                document.querySelectorAll(
                    "body *"
                )
            );


            const candidates = (
                all.filter(
                    el => {

                        const text = (
                            el.innerText || ""
                        ).trim();


                        if (
                            text !== venue
                        ) {

                            return false;

                        }


                        const tag = (
                            el.tagName || ""
                        ).toUpperCase();


                        const role = (
                            el.getAttribute(
                                "role"
                            )
                            || ""
                        );


                        const onclick = (
                            el.getAttribute(
                                "onclick"
                            )
                            || ""
                        );


                        const className = (
                            typeof el.className
                            === "string"
                            ? el.className
                            : ""
                        );


                        return (

                            tag === "A"

                            ||

                            tag === "BUTTON"

                            ||

                            role === "button"

                            ||

                            onclick.length > 0

                            ||

                            className.toLowerCase()
                            .includes("btn")

                            ||

                            className.toLowerCase()
                            .includes("tab")

                            ||

                            className.toLowerCase()
                            .includes("jo")

                        );

                    }
                )
            );


            if (!candidates.length) {

                return {

                    clicked: false,

                    reason:
                        "VENUE_ELEMENT_NOT_FOUND"

                };

            }


            const element = (
                candidates[0]
            );


            element.click();


            return {

                clicked: true,

                tag_name:
                    element.tagName || "",

                id:
                    element.id || "",

                class_name:
                    typeof element.className
                    === "string"
                    ? element.className
                    : "",

                href:
                    element.href || "",

                onclick:
                    element.getAttribute(
                        "onclick"
                    )
                    || ""

            };

        }
        """,
        venue,
    )


# ============================================================
# 現在の開催場判定
# ============================================================


def detect_current_venue(page):

    body_text = (
        safe_body_text(page)
    )


    title = (
        safe_title(page)
    )


    combined = (
        title
        + "\n"
        + body_text
    )


    # --------------------------------------------------------
    # active開催ボタンを優先
    # --------------------------------------------------------


    active_venue = page.evaluate(
        """
        (knownVenues) => {

            const all = Array.from(
                document.querySelectorAll(
                    "body *"
                )
            );


            for (
                const el
                of all
            ) {

                const text = (
                    el.innerText || ""
                ).trim();


                if (
                    !knownVenues.includes(
                        text
                    )
                ) {

                    continue;

                }


                const className = (
                    typeof el.className
                    === "string"
                    ? el.className
                    : ""
                ).toLowerCase();


                if (
                    className.includes(
                        "active"
                    )
                    ||
                    className.includes(
                        "selected"
                    )
                    ||
                    className.includes(
                        "current"
                    )
                ) {

                    return text;

                }

            }


            return null;

        }
        """,
        KNOWN_VENUES,
    )


    if active_venue:

        return active_venue


    for venue in KNOWN_VENUES:

        if venue in combined:

            return venue


    return None


# ============================================================
# Rボタン取得
# ============================================================


def get_race_buttons(page):

    return page.evaluate(
        """
        () => {

            const results = [];


            for (
                let raceNo = 1;
                raceNo <= 12;
                raceNo++
            ) {

                const id = (
                    "hhRaceBtn"
                    +
                    raceNo
                );


                const element = (
                    document.getElementById(
                        id
                    )
                );


                if (!element) {

                    continue;

                }


                results.push({

                    race_no:
                        raceNo,

                    id:
                        id,

                    class_name:
                        typeof element.className
                        === "string"
                        ? element.className
                        : "",

                    text:
                        (
                            element.innerText || ""
                        ).trim(),

                    encp:
                        element.getAttribute(
                            "data-encp"
                        ),

                    disabled:
                        element.disabled
                        === true

                });

            }


            return results;

        }
        """
    )


# ============================================================
# 並び予想DOM解析
# ============================================================


def extract_line_prediction(page):

    return page.evaluate(
        """
        () => {

            const output = {

                found: false,

                prediction_type: null,

                provider: null,

                updated_at: null,

                line_groups: [],

                raw_sequence: [],

                snum_count: 0,

                validation: {

                    expected_line_count:
                        null,

                    actual_line_count:
                        0,

                    line_count_match:
                        null,

                    rider_numbers:
                        [],

                    unique_rider_numbers:
                        [],

                    duplicate_rider_numbers:
                        []

                }

            };


            const pj0314 = (
                document.getElementById(
                    "PJ0314"
                )
            );


            let target = null;


            if (pj0314) {

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

            }


            if (!target) {

                const all = Array.from(
                    document.querySelectorAll(
                        "body *"
                    )
                );


                const candidates = (
                    all.filter(
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
                    )
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


            const fullText = (
                target.innerText || ""
            );


            // =================================================
            // TYPE
            // =================================================


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


            // =================================================
            // PROVIDER
            // =================================================


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
            // UPDATED
            // =================================================


            let updateSearchText = (
                fullText
            );


            if (pj0314) {

                let parent = (
                    pj0314.parentElement
                );


                for (
                    let i = 0;
                    i < 3;
                    i++
                ) {

                    if (!parent) {

                        break;

                    }


                    updateSearchText += (
                        "\\n"
                        +
                        (
                            parent.innerText || ""
                        )
                    );


                    parent = (
                        parent.parentElement
                    );

                }

            }


            const updatedMatch = (
                updateSearchText.match(
                    /(20\\d{2}\\/\\d{1,2}\\/\\d{1,2}\\s+\\d{1,2}:\\d{2})\\s*更新/
                )
            );


            if (updatedMatch) {

                output.updated_at = (
                    updatedMatch[1]
                    +
                    " 更新"
                );

            }


            // =================================================
            // SNUM
            // =================================================


            const snumElements = (
                Array.from(
                    target.querySelectorAll(
                        ".snum"
                    )
                )
            );


            output.snum_count = (
                snumElements.length
            );


            const lineGroups = [];

            const rawSequence = [];

            let currentLine = [];


            for (
                const element
                of snumElements
            ) {

                const className = (
                    typeof element.className
                    === "string"
                    ? element.className
                    : ""
                );


                const text = (
                    element.innerText || ""
                ).trim();


                if (
                    className.includes(
                        "base_color_0"
                    )
                ) {

                    rawSequence.push({

                        type:
                            "separator",

                        value:
                            null,

                        class_name:
                            className

                    });


                    if (
                        currentLine.length
                    ) {

                        lineGroups.push(
                            currentLine
                        );


                        currentLine = [];

                    }


                    continue;

                }


                if (
                    /^[1-9]$/.test(text)
                ) {

                    const number = (
                        Number(text)
                    );


                    rawSequence.push({

                        type:
                            "rider",

                        value:
                            number,

                        class_name:
                            className

                    });


                    currentLine.push(
                        number
                    );

                }

            }


            if (
                currentLine.length
            ) {

                lineGroups.push(
                    currentLine
                );

            }


            output.line_groups = (
                lineGroups.filter(
                    line => (
                        Array.isArray(line)
                        &&
                        line.length > 0
                    )
                )
            );


            output.raw_sequence = (
                rawSequence
            );


            // =================================================
            // VALIDATION
            // =================================================


            const expectedMapping = {

                "二分戦": 2,

                "三分戦": 3,

                "四分戦": 4,

                "五分戦": 5

            };


            const expectedCount = (
                expectedMapping[
                    output.prediction_type
                ]
                ?? null
            );


            const riderNumbers = (
                output.line_groups.flat()
            );


            const uniqueRiderNumbers = (
                Array.from(
                    new Set(
                        riderNumbers
                    )
                )
            );


            const duplicateRiderNumbers = (
                uniqueRiderNumbers.filter(
                    number => (

                        riderNumbers.filter(
                            value => (
                                value
                                ===
                                number
                            )
                        ).length > 1

                    )
                )
            );


            output.validation = {

                expected_line_count:
                    expectedCount,

                actual_line_count:
                    output.line_groups.length,

                line_count_match:
                    expectedCount === null
                    ? null
                    : (
                        expectedCount
                        ===
                        output.line_groups.length
                    ),

                rider_numbers:
                    riderNumbers,

                unique_rider_numbers:
                    uniqueRiderNumbers,

                duplicate_rider_numbers:
                    duplicateRiderNumbers

            };


            if (
                output.line_groups.length > 0
                &&
                riderNumbers.length > 0
                &&
                duplicateRiderNumbers.length
                === 0
            ) {

                output.found = true;

            }


            return output;

        }
        """
    )


# ============================================================
# 現在状態保存
# ============================================================


def save_progress(
    race_date,
    venue_buttons,
    venues,
):

    all_races = []


    for venue_data in venues:

        all_races.extend(
            venue_data.get(
                "races",
                []
            )
        )


    output = {

        "program":
            "034_capture_all_venues_line_predictions.py",

        "captured_at":
            datetime.now().isoformat(),

        "race_date":
            race_date,

        "venue_button_count":
            len(venue_buttons),

        "venue_count":
            len(venues),

        "race_count":
            len(all_races),

        "line_found_count":
            len([
                race
                for race in all_races
                if race.get("status")
                == "LINE_FOUND"
            ]),

        "line_not_found_count":
            len([
                race
                for race in all_races
                if race.get("status")
                == "LINE_NOT_FOUND"
            ]),

        "validation_error_count":
            len([
                race
                for race in all_races
                if race.get("status")
                == "LINE_VALIDATION_ERROR"
            ]),

        "error_count":
            len([
                race
                for race in all_races
                if race.get("status")
                in {
                    "VENUE_CLICK_ERROR",
                    "CLICK_ERROR",
                    "DOM_ERROR",
                }
            ]),

        "venue_buttons":
            venue_buttons,

        "venues":
            venues,

    }


    save_json(
        OUT_JSON,
        output,
    )


    return output


# ============================================================
# main
# ============================================================


def main():

    print(
        "=== 034 全開催・全R 並び予想自動取得テスト ==="
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


        contexts = (
            browser.contexts
        )


        if not contexts:

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


        for context in contexts:

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

            print()

            print(
                "Edgeで対象日の"
                "KEIRIN.JP raceliveページを"
                "1つ開いてください"
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
        # 日付
        # ====================================================


        page_text = (
            safe_body_text(
                target_page
            )
        )


        race_date = (
            extract_race_date(
                page_text
            )
        )


        print()

        print(
            "TARGET DATE:",
            race_date,
        )


        if not race_date:

            print()

            print(
                "ERROR: 日付取得失敗"
            )

            return


        # ====================================================
        # 開催ボタン
        # ====================================================


        print()

        print(
            "[4] 開催ボタン探索"
        )


        venue_buttons = (
            get_venue_buttons(
                target_page
            )
        )


        print()

        print(
            "VENUE BUTTON COUNT:",
            len(venue_buttons),
        )


        print()

        print(
            "★ 開催候補 ★"
        )


        for button in venue_buttons:

            print()

            print(
                button["venue"]
            )

            print(
                "TAG:",
                button["tag_name"]
            )

            print(
                "ID:",
                button["id"]
            )

            print(
                "CLASS:",
                button["class_name"]
            )

            print(
                "HREF:",
                button["href"]
            )

            print(
                "ONCLICK:",
                button["onclick"]
            )


        if not venue_buttons:

            print()

            print(
                "ERROR:"
                " 開催ボタンを"
                "見つけられませんでした"
            )

            return


        # ====================================================
        # 全開催巡回
        # ====================================================


        print()

        print(
            "[5] 全開催巡回開始"
        )


        venues = []


        for venue_index, venue_button in enumerate(
            venue_buttons,
            start=1,
        ):

            requested_venue = (
                venue_button["venue"]
            )


            print()

            print(
                "#" * 100
            )

            print(
                f"VENUE "
                f"{venue_index}/"
                f"{len(venue_buttons)}"
            )

            print(
                "REQUESTED VENUE:",
                requested_venue
            )

            print(
                "#" * 100
            )


            # ================================================
            # 開催クリック
            # ================================================


            try:

                click_result = (
                    click_venue(
                        target_page,
                        requested_venue,
                    )
                )


                print()

                print(
                    "VENUE CLICK:"
                )

                print(
                    json.dumps(
                        click_result,
                        ensure_ascii=False,
                        indent=2,
                    )
                )


                if not click_result.get(
                    "clicked"
                ):

                    venues.append({

                        "requested_venue":
                            requested_venue,

                        "detected_venue":
                            None,

                        "status":
                            "VENUE_CLICK_ERROR",

                        "click_result":
                            click_result,

                        "races":
                            [],

                    })


                    save_progress(
                        race_date,
                        venue_buttons,
                        venues,
                    )


                    continue


                time.sleep(
                    VENUE_CLICK_WAIT_SECONDS
                )


            except Exception as e:

                print()

                print(
                    "VENUE CLICK ERROR:"
                )

                print(
                    repr(e)
                )


                venues.append({

                    "requested_venue":
                        requested_venue,

                    "detected_venue":
                        None,

                    "status":
                        "VENUE_CLICK_ERROR",

                    "error":
                        repr(e),

                    "races":
                        [],

                })


                save_progress(
                    race_date,
                    venue_buttons,
                    venues,
                )


                continue


            # ================================================
            # 開催判定
            # ================================================


            detected_venue = (
                detect_current_venue(
                    target_page
                )
            )


            print()

            print(
                "DETECTED VENUE:",
                detected_venue
            )


            venue_data = {

                "requested_venue":
                    requested_venue,

                "detected_venue":
                    detected_venue,

                "status":
                    "VENUE_OPENED",

                "races":
                    [],

            }


            # ================================================
            # Rボタン
            # ================================================


            race_buttons = (
                get_race_buttons(
                    target_page
                )
            )


            print()

            print(
                "RACE BUTTON COUNT:",
                len(race_buttons)
            )


            # ================================================
            # 全R巡回
            # ================================================


            for button in race_buttons:

                race_no = (
                    button["race_no"]
                )


                race_key = (
                    build_race_key(
                        race_date,
                        requested_venue,
                        race_no,
                    )
                )


                print()

                print(
                    "-"
                    * 100
                )

                print(
                    race_key
                )


                try:

                    target_page.locator(
                        "#"
                        +
                        button["id"]
                    ).click(
                        timeout=30000
                    )


                    time.sleep(
                        RACE_CLICK_WAIT_SECONDS
                    )


                except Exception as e:

                    print()

                    print(
                        "CLICK ERROR:",
                        repr(e)
                    )


                    venue_data[
                        "races"
                    ].append({

                        "race_date":
                            race_date,

                        "venue":
                            requested_venue,

                        "race_no":
                            race_no,

                        "race_key":
                            race_key,

                        "status":
                            "CLICK_ERROR",

                        "error":
                            repr(e),

                    })


                    continue


                try:

                    line_data = (
                        extract_line_prediction(
                            target_page
                        )
                    )


                except Exception as e:

                    print()

                    print(
                        "DOM ERROR:",
                        repr(e)
                    )


                    venue_data[
                        "races"
                    ].append({

                        "race_date":
                            race_date,

                        "venue":
                            requested_venue,

                        "race_no":
                            race_no,

                        "race_key":
                            race_key,

                        "status":
                            "DOM_ERROR",

                        "error":
                            repr(e),

                    })


                    continue


                validation = (
                    line_data.get(
                        "validation",
                        {}
                    )
                )


                if not line_data.get(
                    "found"
                ):

                    status = (
                        "LINE_NOT_FOUND"
                    )


                elif (
                    validation.get(
                        "line_count_match"
                    )
                    is False
                ):

                    status = (
                        "LINE_VALIDATION_ERROR"
                    )


                elif (
                    validation.get(
                        "duplicate_rider_numbers"
                    )
                ):

                    status = (
                        "LINE_VALIDATION_ERROR"
                    )


                else:

                    status = (
                        "LINE_FOUND"
                    )


                print()

                print(
                    "STATUS:",
                    status
                )

                print(
                    "TYPE:",
                    line_data.get(
                        "prediction_type"
                    )
                )

                print(
                    "PROVIDER:",
                    line_data.get(
                        "provider"
                    )
                )

                print(
                    "LINE:",
                    line_data.get(
                        "line_groups"
                    )
                )


                venue_data[
                    "races"
                ].append({

                    "race_date":
                        race_date,

                    "venue":
                        requested_venue,

                    "race_no":
                        race_no,

                    "race_key":
                        race_key,

                    "status":
                        status,

                    "button":
                        button,

                    "line_prediction":
                        line_data,

                })


                save_progress(
                    race_date,
                    venue_buttons,
                    venues
                    +
                    [
                        venue_data
                    ],
                )


            venue_data[
                "status"
            ] = (
                "VENUE_COMPLETE"
            )


            venues.append(
                venue_data
            )


            save_progress(
                race_date,
                venue_buttons,
                venues,
            )


        # ====================================================
        # 最終保存
        # ====================================================


        output = (
            save_progress(
                race_date,
                venue_buttons,
                venues,
            )
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
            "034 最終結果"
        )

        print(
            "#"
            * 100
        )

        print()

        print(
            "DATE:",
            output[
                "race_date"
            ]
        )

        print(
            "VENUE COUNT:",
            output[
                "venue_count"
            ]
        )

        print(
            "RACE COUNT:",
            output[
                "race_count"
            ]
        )

        print(
            "LINE FOUND:",
            output[
                "line_found_count"
            ]
        )

        print(
            "LINE NOT FOUND:",
            output[
                "line_not_found_count"
            ]
        )

        print(
            "VALIDATION ERROR:",
            output[
                "validation_error_count"
            ]
        )

        print(
            "ERROR:",
            output[
                "error_count"
            ]
        )


        print()

        print(
            "★ 開催別結果 ★"
        )


        for venue_data in venues:

            races = (
                venue_data.get(
                    "races",
                    []
                )
            )


            print()

            print(
                "-"
                * 100
            )

            print(
                "REQUESTED:",
                venue_data.get(
                    "requested_venue"
                )
            )

            print(
                "DETECTED:",
                venue_data.get(
                    "detected_venue"
                )
            )

            print(
                "STATUS:",
                venue_data.get(
                    "status"
                )
            )

            print(
                "RACES:",
                len(races)
            )

            print(
                "LINE FOUND:",
                len([
                    race
                    for race in races
                    if race.get(
                        "status"
                    )
                    == "LINE_FOUND"
                ])
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
            "=== 034 完了 ==="
        )


if __name__ == "__main__":

    main()