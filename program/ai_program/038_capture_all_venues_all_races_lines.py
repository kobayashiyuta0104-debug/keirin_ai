from pathlib import Path
from datetime import datetime
import json
import re
import time

from playwright.sync_api import sync_playwright


# ============================================================
# 038
#
# 対象日 全開催 × 全R 並び予想取得
#
# 037で確認:
#
#   LIVEボタンによる開催切替は成功
#   PJ0314は開催切替ごとに変化
#
# 方針:
#
#   ・hcomRaceDivからLIVE開催一覧取得
#   ・LIVEボタンを正規クリック
#   ・押したLIVEボタンの開催名を正とする
#   ・開催切替後PJ0314変化待ち
#   ・各Rボタンを巡回
#   ・Rクリック後DOM安定待ち
#   ・033方式 base_color_0 でライン分割
#   ・全開催を1JSON保存
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
    / "038_all_venues_all_races_lines.json"
)


CDP_URL = "http://127.0.0.1:9222"

VENUE_WAIT_TIMEOUT = 20

RACE_WAIT_TIMEOUT = 15

POLL_SECONDS = 0.5


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

    return (
        f"{race_date}_"
        f"{venue}_"
        f"{race_no}R"
    )


# ============================================================
# PJ0314署名
# ============================================================


def get_pj0314_signature(page):

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
# PJ0314変化待ち
# ============================================================


def wait_pj0314_change(
    page,
    before_signature,
    timeout_seconds,
):

    start = time.time()


    while (
        time.time() - start
        <
        timeout_seconds
    ):

        current_signature = (
            get_pj0314_signature(
                page
            )
        )


        if (
            current_signature
            is not None
            and
            current_signature
            !=
            before_signature
        ):

            return {

                "changed":
                    True,

                "signature":
                    current_signature,

                "wait_seconds":
                    round(
                        time.time() - start,
                        3,
                    ),

            }


        time.sleep(
            POLL_SECONDS
        )


    return {

        "changed":
            False,

        "signature":
            get_pj0314_signature(
                page
            ),

        "wait_seconds":
            round(
                time.time() - start,
                3,
            ),

    }


# ============================================================
# PJ0314存在待ち
# ============================================================


def wait_pj0314_exists(
    page,
    timeout_seconds,
):

    start = time.time()


    while (
        time.time() - start
        <
        timeout_seconds
    ):

        signature = (
            get_pj0314_signature(
                page
            )
        )


        if signature is not None:

            return {

                "found":
                    True,

                "signature":
                    signature,

                "wait_seconds":
                    round(
                        time.time() - start,
                        3,
                    ),

            }


        time.sleep(
            POLL_SECONDS
        )


    return {

        "found":
            False,

        "signature":
            None,

        "wait_seconds":
            round(
                time.time() - start,
                3,
            ),

    }


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


                const venue = (
                    place.innerText || ""
                ).trim();


                if (!venue) {

                    continue;

                }


                results.push({

                    index:
                        index,

                    venue:
                        venue,

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

                    text:
                        (
                            element.innerText || ""
                        ).trim(),

                    class_name:
                        typeof element.className
                        === "string"
                        ? element.className
                        : "",

                    encp:
                        element.getAttribute(
                            "data-encp"
                        ),

                    disabled:
                        element.disabled
                        === true,

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

                found:
                    false,

                prediction_type:
                    null,

                provider:
                    null,

                updated_at:
                    null,

                line_groups:
                    [],

                raw_sequence:
                    [],

                snum_count:
                    0,

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


            if (!pj0314) {

                return output;

            }


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


            const fullText = (
                target.innerText || ""
            );


            // =============================================
            // TYPE
            // =============================================


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


            // =============================================
            // PROVIDER
            // =============================================


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


            // =============================================
            // UPDATED
            // =============================================


            let updateSearchText = (
                fullText
            );


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


            // =============================================
            // SNUM解析
            // =============================================


            const snumElements = Array.from(
                target.querySelectorAll(
                    ".snum"
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

                        "type":
                            "separator",

                        "value":
                            null,

                        "class_name":
                            className,

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

                        "type":
                            "rider",

                        "value":
                            number,

                        "class_name":
                            className,

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


            // =============================================
            // VALIDATION
            // =============================================


            const expectedMapping = {

                "二分戦":
                    2,

                "三分戦":
                    3,

                "四分戦":
                    4,

                "五分戦":
                    5,

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


            const uniqueRiderNumbers = Array.from(
                new Set(
                    riderNumbers
                )
            );


            const duplicateRiderNumbers = (
                uniqueRiderNumbers.filter(
                    number => (

                        riderNumbers.filter(
                            value => (
                                value === number
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
                    duplicateRiderNumbers,

            };


            if (
                output.line_groups.length > 0
                &&
                riderNumbers.length > 0
                &&
                duplicateRiderNumbers.length === 0
            ) {

                output.found = true;

            }


            return output;

        }
        """
    )


# ============================================================
# R切替後ライン変化待ち
# ============================================================


def wait_race_line_stable(
    page,
    before_signature,
    timeout_seconds,
):

    start = time.time()

    last_signature = None

    stable_count = 0


    while (
        time.time() - start
        <
        timeout_seconds
    ):

        current_signature = (
            get_pj0314_signature(
                page
            )
        )


        if (
            current_signature
            is not None
            and
            current_signature
            !=
            before_signature
        ):

            if (
                current_signature
                ==
                last_signature
            ):

                stable_count += 1

            else:

                stable_count = 0


            last_signature = (
                current_signature
            )


            if (
                stable_count >= 2
            ):

                return {

                    "changed":
                        True,

                    "stable":
                        True,

                    "signature":
                        current_signature,

                    "wait_seconds":
                        round(
                            time.time() - start,
                            3,
                        ),

                }


        time.sleep(
            POLL_SECONDS
        )


    return {

        "changed":
            (
                last_signature
                is not None
                and
                last_signature
                !=
                before_signature
            ),

        "stable":
            False,

        "signature":
            get_pj0314_signature(
                page
            ),

        "wait_seconds":
            round(
                time.time() - start,
                3,
            ),

    }


# ============================================================
# 途中保存
# ============================================================


def save_progress(
    race_date,
    live_venues,
    venue_results,
):

    all_races = []


    for venue_data in venue_results:

        all_races.extend(
            venue_data.get(
                "races",
                []
            )
        )


    output = {

        "program":
            "038_capture_all_venues_all_races_lines.py",

        "captured_at":
            datetime.now().isoformat(),

        "race_date":
            race_date,

        "venue_count":
            len(venue_results),

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
                    "RACE_CLICK_ERROR",
                    "DOM_ERROR",
                }
            ]),

        "live_venues":
            live_venues,

        "venues":
            venue_results,

    }


    save_json(
        OUT_JSON,
        output
    )


    return output


# ============================================================
# main
# ============================================================


def main():

    print(
        "=== 038 全開催 × 全R 並び予想取得 ==="
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


        # ====================================================
        # 日付
        # ====================================================


        body_text = (
            safe_body_text(
                target_page
            )
        )


        race_date = (
            extract_race_date(
                body_text
            )
        )


        print()

        print(
            "TARGET DATE:",
            race_date
        )


        if not race_date:

            print()

            print(
                "ERROR: 日付取得失敗"
            )

            return


        # ====================================================
        # LIVE開催一覧
        # ====================================================


        print()

        print(
            "[3] LIVE開催一覧取得"
        )


        live_venues = (
            get_live_venues(
                target_page
            )
        )


        print()

        print(
            "VENUE COUNT:",
            len(live_venues)
        )


        print()

        print(
            "★ 対象開催 ★"
        )


        for venue in live_venues:

            print(

                venue["index"],

                venue["venue"],

                venue["button_id"]

            )


        # ====================================================
        # 全開催巡回
        # ====================================================


        venue_results = []


        for venue_number, venue in enumerate(
            live_venues,
            start=1,
        ):

            venue_name = (
                venue["venue"]
            )


            print()

            print(
                "#"
                * 100
            )

            print(
                f"VENUE "
                f"{venue_number}/"
                f"{len(live_venues)}"
            )

            print(
                "VENUE:",
                venue_name
            )

            print(
                "#"
                * 100
            )


            before_signature = (
                get_pj0314_signature(
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

                venue_click_error = (
                    None
                )


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


                venue_results.append({

                    "venue":
                        venue_name,

                    "status":
                        "VENUE_CLICK_ERROR",

                    "error":
                        venue_click_error,

                    "races":
                        [],

                })


                save_progress(
                    race_date,
                    live_venues,
                    venue_results,
                )


                continue


            # =================================================
            # 開催DOM変化待ち
            # =================================================


            venue_wait = (
                wait_pj0314_change(
                    target_page,
                    before_signature,
                    VENUE_WAIT_TIMEOUT,
                )
            )


            if not venue_wait[
                "changed"
            ]:

                # 最初から同開催の場合を考慮

                exists_wait = (
                    wait_pj0314_exists(
                        target_page,
                        5,
                    )
                )


                print()

                print(
                    "PJ0314 CHANGE: False"
                )

                print(
                    "PJ0314 EXISTS:",
                    exists_wait["found"]
                )


            else:

                print()

                print(
                    "PJ0314 CHANGE: True"
                )

                print(
                    "WAIT:",
                    venue_wait[
                        "wait_seconds"
                    ],
                    "sec"
                )


            time.sleep(
                1
            )


            # =================================================
            # Rボタン取得
            # =================================================


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


            venue_data = {

                "venue":
                    venue_name,

                "live_button":
                    venue,

                "venue_wait":
                    venue_wait,

                "status":
                    "VENUE_RUNNING",

                "races":
                    [],

            }


            # =================================================
            # 全R
            # =================================================


            for race_button in race_buttons:

                race_no = (
                    race_button[
                        "race_no"
                    ]
                )


                race_key = (
                    build_race_key(
                        race_date,
                        venue_name,
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


                before_race_signature = (
                    get_pj0314_signature(
                        target_page
                    )
                )


                try:

                    target_page.locator(
                        "#"
                        +
                        race_button["id"]
                    ).click(
                        timeout=30000
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


                if (
                    click_status
                    ==
                    "CLICK_ERROR"
                ):

                    print()

                    print(
                        "RACE CLICK ERROR:"
                    )

                    print(
                        click_error
                    )


                    venue_data[
                        "races"
                    ].append({

                        "race_date":
                            race_date,

                        "venue":
                            venue_name,

                        "race_no":
                            race_no,

                        "race_key":
                            race_key,

                        "status":
                            "RACE_CLICK_ERROR",

                        "error":
                            click_error,

                    })


                    continue


                # =============================================
                # R切替DOM安定待ち
                # =============================================


                race_wait = (
                    wait_race_line_stable(
                        target_page,
                        before_race_signature,
                        RACE_WAIT_TIMEOUT,
                    )
                )


                # 既に選択中Rの場合
                if not race_wait[
                    "changed"
                ]:

                    time.sleep(
                        1
                    )


                # =============================================
                # ライン解析
                # =============================================


                try:

                    line_data = (
                        extract_line_prediction(
                            target_page
                        )
                    )


                except Exception as e:

                    print()

                    print(
                        "DOM ERROR:"
                    )

                    print(
                        repr(e)
                    )


                    venue_data[
                        "races"
                    ].append({

                        "race_date":
                            race_date,

                        "venue":
                            venue_name,

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

                print(
                    "RACE WAIT:",
                    race_wait[
                        "wait_seconds"
                    ],
                    "sec"
                )


                venue_data[
                    "races"
                ].append({

                    "race_date":
                        race_date,

                    "venue":
                        venue_name,

                    "race_no":
                        race_no,

                    "race_key":
                        race_key,

                    "status":
                        status,

                    "race_button":
                        race_button,

                    "race_wait":
                        race_wait,

                    "line_prediction":
                        line_data,

                })


                save_progress(
                    race_date,
                    live_venues,
                    venue_results
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


            venue_results.append(
                venue_data
            )


            save_progress(
                race_date,
                live_venues,
                venue_results,
            )


        # ====================================================
        # 最終保存
        # ====================================================


        output = (
            save_progress(
                race_date,
                live_venues,
                venue_results,
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
            "038 最終結果"
        )

        print(
            "#"
            * 100
        )

        print()

        print(
            "DATE:",
            output["race_date"]
        )

        print(
            "VENUE COUNT:",
            output["venue_count"]
        )

        print(
            "RACE COUNT:",
            output["race_count"]
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


        for venue_data in venue_results:

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
                "VENUE:",
                venue_data.get(
                    "venue"
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
                    ==
                    "LINE_FOUND"
                ])
            )

            print(
                "LINE NOT FOUND:",
                len([
                    race
                    for race in races
                    if race.get(
                        "status"
                    )
                    ==
                    "LINE_NOT_FOUND"
                ])
            )

            print(
                "VALIDATION ERROR:",
                len([
                    race
                    for race in races
                    if race.get(
                        "status"
                    )
                    ==
                    "LINE_VALIDATION_ERROR"
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
            "=== 038 完了 ==="
        )


if __name__ == "__main__":

    main()