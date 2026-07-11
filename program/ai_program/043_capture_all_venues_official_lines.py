from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
import json
import re
import time


# ============================================================
# 043
#
# 全開催 × 全R
# 正式ライン情報取得テスト
#
# 038:
#   全開催 × 全R巡回成功
#
# 041:
#   通常表示 / 競り表示の複数段構造確認
#
# 042:
#   車番cell_index間隔からライン復元成功
#
# 今回:
#
#   ・対象日の全LIVE開催を取得
#   ・全開催切替
#   ・全R巡回
#   ・並び予想DOM取得
#   ・車番cell_index間隔からmain_lines復元
#   ・競り表示をcompetition_rowsへ分離
#   ・prediction_typeはサイト表示をそのまま保存
#   ・TYPEとライン数の一致検証はしない
#   ・race_key付きで正式JSON保存
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

OUT_FILE = (
    OUT_DIR
    / "043_all_venues_official_lines.json"
)

VENUE_WAIT_TIMEOUT = 15

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
# PJ0314署名
# ============================================================


def get_pj0314_signature(page):

    try:

        return page.locator(
            "#PJ0314"
        ).inner_text(
            timeout=3000
        )

    except Exception:

        return ""


# ============================================================
# DOM変化待ち
# ============================================================


def wait_pj0314_change(
    page,
    before,
    timeout_seconds,
):

    start = time.time()


    while (
        time.time() - start
        <
        timeout_seconds
    ):

        after = (
            get_pj0314_signature(
                page
            )
        )


        if (
            after
            and
            after != before
        ):

            time.sleep(1)

            return {

                "changed":
                    True,

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

        "wait_seconds":
            round(
                time.time() - start,
                3,
            ),

    }


# ============================================================
# ページ本文
# ============================================================


def get_body_text(page):

    try:

        return page.locator(
            "body"
        ).inner_text(
            timeout=5000
        )

    except Exception:

        return ""


# ============================================================
# 対象日取得
# ============================================================


def extract_race_date(text):

    patterns = [

        r"(20\d{2})[/-](\d{1,2})[/-](\d{1,2})",

        r"(20\d{2})年\s*(\d{1,2})月\s*(\d{1,2})日",

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
# LIVE開催一覧
#
# 039 / 041 / 042 成功方式
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
# Rボタン一覧
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

                    disabled:
                        element.disabled
                        === true,

                    encp:
                        element.getAttribute(
                            "data-encp"
                        ),

                });

            }

            return results;

        }
        """
    )


# ============================================================
# 並び予想DOM取得
# ============================================================


def inspect_line_cells(page):

    return page.evaluate(
        """
        () => {

            const output = {

                pj0314_exists:
                    false,

                line_target_exists:
                    false,

                prediction_type:
                    null,

                provider:
                    null,

                has_competition_text:
                    false,

                competition_texts:
                    [],

                rows:
                    [],

                row_count:
                    0,

                target_text:
                    null,

            };


            const pj = (
                document.getElementById(
                    "PJ0314"
                )
            );


            if (!pj) {

                return output;

            }


            output.pj0314_exists = true;


            // =================================================
            // 並び予想TABLE探索
            // =================================================


            const tables = Array.from(
                pj.querySelectorAll(
                    "table"
                )
            );


            let target = null;


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

                return output;

            }


            output.line_target_exists = true;


            const targetText = (
                target.innerText || ""
            );


            output.target_text = (
                targetText
            );


            // =================================================
            // TYPE
            // =================================================


            const typeCandidates = [

                "二分戦",

                "三分戦",

                "四分戦",

                "五分戦",

                "コマ切れ",

                "先行一車",

            ];


            for (
                const type
                of typeCandidates
            ) {

                if (
                    targetText.includes(
                        type
                    )
                ) {

                    output.prediction_type = (
                        type
                    );

                    break;

                }

            }


            // =================================================
            // PROVIDER
            // =================================================


            const providerMatch = (
                targetText.match(
                    /情報提供\\s*[：:]\\s*([^\\n\\r]+)/
                )
            );


            if (providerMatch) {

                output.provider = (
                    providerMatch[1]
                ).trim();

            }


            // =================================================
            // 競り文字
            // =================================================


            const allElements = Array.from(
                target.querySelectorAll(
                    "*"
                )
            );


            for (
                const el
                of allElements
            ) {

                const text = (
                    el.innerText || ""
                ).trim();


                if (
                    text === "競"
                    ||
                    text === "競り"
                    ||
                    text.includes(
                        "ジカ"
                    )
                ) {

                    output.competition_texts.push({

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
                            text,

                    });

                }

            }


            output.has_competition_text = (

                output.competition_texts.length
                >
                0

            );


            // =================================================
            // 最初の.snumからラインTABLE取得
            // =================================================


            const firstSnum = (
                target.querySelector(
                    ".snum"
                )
            );


            if (!firstSnum) {

                return output;

            }


            const lineTable = (
                firstSnum.closest(
                    "table"
                )
            );


            if (!lineTable) {

                return output;

            }


            let rows = [];


            if (
                lineTable.tBodies
                &&
                lineTable.tBodies.length > 0
            ) {

                rows = Array.from(
                    lineTable.tBodies[0].rows
                );

            }


            // =================================================
            // ROW解析
            // =================================================


            for (
                let rowIndex = 0;
                rowIndex < rows.length;
                rowIndex++
            ) {

                const tr = (
                    rows[rowIndex]
                );


                const cells = Array.from(
                    tr.cells || []
                );


                const carCells = [];


                for (
                    let cellIndex = 0;
                    cellIndex < cells.length;
                    cellIndex++
                ) {

                    const td = (
                        cells[cellIndex]
                    );


                    const snums = Array.from(
                        td.querySelectorAll(
                            ".snum"
                        )
                    );


                    for (
                        let snumIndex = 0;
                        snumIndex < snums.length;
                        snumIndex++
                    ) {

                        const snum = (
                            snums[snumIndex]
                        );


                        const text = (
                            snum.textContent || ""
                        ).trim();


                        if (
                            !/^[1-9]$/.test(
                                text
                            )
                        ) {

                            continue;

                        }


                        const rect = (
                            snum.getBoundingClientRect()
                        );


                        carCells.push({

                            car_number:
                                Number(
                                    text
                                ),

                            cell_index:
                                cellIndex,

                            snum_index:
                                snumIndex,

                            x:
                                rect.x,

                            y:
                                rect.y,

                            width:
                                rect.width,

                            height:
                                rect.height,

                            class_name:
                                typeof snum.className
                                === "string"
                                ? snum.className
                                : "",

                        });

                    }

                }


                const rowRect = (
                    tr.getBoundingClientRect()
                );


                output.rows.push({

                    row_index:
                        rowIndex,

                    row_text:
                        tr.innerText || "",

                    car_count:
                        carCells.length,

                    car_numbers:
                        carCells.map(
                            item => (
                                item.car_number
                            )
                        ),

                    car_cells:
                        carCells,

                    rect: {

                        x:
                            rowRect.x,

                        y:
                            rowRect.y,

                        width:
                            rowRect.width,

                        height:
                            rowRect.height,

                    },

                });

            }


            output.row_count = (
                output.rows.length
            );


            return output;

        }
        """
    )


# ============================================================
# セル間隔からライン復元
# ============================================================


def reconstruct_lines(car_cells):

    if not car_cells:

        return []


    sorted_cells = sorted(

        car_cells,

        key=lambda item: (

            item.get(
                "cell_index",
                0
            ),

            item.get(
                "x",
                0
            ),

        ),

    )


    lines = []

    current_line = []

    previous_cell_index = None


    for item in sorted_cells:

        car_number = (
            item.get(
                "car_number"
            )
        )


        cell_index = (
            item.get(
                "cell_index"
            )
        )


        if (
            previous_cell_index
            is None
        ):

            current_line = [
                car_number
            ]


        else:

            cell_gap = (

                cell_index
                -
                previous_cell_index

            )


            if (
                cell_gap > 1
            ):

                if current_line:

                    lines.append(
                        current_line
                    )


                current_line = [
                    car_number
                ]


            else:

                current_line.append(
                    car_number
                )


        previous_cell_index = (
            cell_index
        )


    if current_line:

        lines.append(
            current_line
        )


    return lines


# ============================================================
# ROW構造解析
# ============================================================


def analyze_rows(dom):

    rows = (
        dom.get(
            "rows",
            []
        )
    )


    analyzed_rows = []


    for row in rows:

        reconstructed_lines = (
            reconstruct_lines(
                row.get(
                    "car_cells",
                    []
                )
            )
        )


        analyzed_rows.append({

            "row_index":
                row.get(
                    "row_index"
                ),

            "car_count":
                row.get(
                    "car_count",
                    0
                ),

            "car_numbers":
                row.get(
                    "car_numbers",
                    []
                ),

            "car_cell_indexes": [

                item.get(
                    "cell_index"
                )

                for item in row.get(
                    "car_cells",
                    []
                )

            ],

            "reconstructed_lines":
                reconstructed_lines,

        })


    valid_rows = [

        row

        for row in analyzed_rows

        if (
            row.get(
                "car_count",
                0
            )
            >
            0
        )

    ]


    if not valid_rows:

        return {

            "main_row_index":
                None,

            "main_lines":
                [],

            "competition_rows":
                [],

            "display_rows":
                analyzed_rows,

        }


    # ========================================================
    # 車番数最多段をMAIN
    # ========================================================


    main_row = max(

        valid_rows,

        key=lambda item: (
            item.get(
                "car_count",
                0
            )
        ),

    )


    main_row_index = (
        main_row.get(
            "row_index"
        )
    )


    competition_rows = [

        {

            "row_index":
                row.get(
                    "row_index"
                ),

            "car_numbers":
                row.get(
                    "car_numbers",
                    []
                ),

            "car_cell_indexes":
                row.get(
                    "car_cell_indexes",
                    []
                ),

            "reconstructed_lines":
                row.get(
                    "reconstructed_lines",
                    []
                ),

        }

        for row in valid_rows

        if (
            row.get(
                "row_index"
            )
            !=
            main_row_index
        )

    ]


    return {

        "main_row_index":
            main_row_index,

        "main_lines":
            main_row.get(
                "reconstructed_lines",
                []
            ),

        "competition_rows":
            competition_rows,

        "display_rows":
            analyzed_rows,

    }


# ============================================================
# 車番検証
# ============================================================


def validate_riders(
    main_lines,
    competition_rows,
):

    rider_numbers = []


    for line in main_lines:

        rider_numbers.extend(
            line
        )


    for row in competition_rows:

        rider_numbers.extend(
            row.get(
                "car_numbers",
                []
            )
        )


    unique_riders = sorted(
        set(
            rider_numbers
        )
    )


    duplicate_riders = sorted({

        number

        for number in rider_numbers

        if (
            rider_numbers.count(
                number
            )
            >
            1
        )

    })


    return {

        "rider_numbers":
            rider_numbers,

        "unique_rider_numbers":
            unique_riders,

        "rider_count":
            len(
                rider_numbers
            ),

        "unique_rider_count":
            len(
                unique_riders
            ),

        "duplicate_rider_numbers":
            duplicate_riders,

        "has_duplicate":
            len(
                duplicate_riders
            )
            >
            0,

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
            "043_capture_all_venues_official_lines.py",

        "captured_at":
            datetime.now().isoformat(),

        "race_date":
            race_date,

        "venue_count":
            len(
                venue_results
            ),

        "race_count":
            len(
                all_races
            ),

        "line_found_count":
            len([

                race

                for race in all_races

                if (
                    race.get(
                        "status"
                    )
                    ==
                    "LINE_FOUND"
                )

            ]),

        "competition_count":
            len([

                race

                for race in all_races

                if race.get(
                    "has_competition"
                )
                is True

            ]),

        "line_not_found_count":
            len([

                race

                for race in all_races

                if (
                    race.get(
                        "status"
                    )
                    ==
                    "LINE_NOT_FOUND"
                )

            ]),

        "validation_error_count":
            len([

                race

                for race in all_races

                if (
                    race.get(
                        "status"
                    )
                    ==
                    "RIDER_VALIDATION_ERROR"
                )

            ]),

        "error_count":
            len([

                race

                for race in all_races

                if (
                    race.get(
                        "status"
                    )
                    in {

                        "VENUE_CLICK_ERROR",

                        "RACE_CLICK_ERROR",

                        "DOM_ERROR",

                    }
                )

            ]),

        "live_venues":
            live_venues,

        "venues":
            venue_results,

    }


    save_json(
        OUT_FILE,
        output,
    )


    return output




# ============================================================
# 060連携: 今日のpre_race.jsonから最初のencParaRを取得
# ============================================================

def find_first_enc_para_r(obj):
    if isinstance(obj, dict):
        value = obj.get("encParaR")
        if isinstance(value, str) and value.strip():
            return value.strip()

        value = obj.get("enc_para_r")
        if isinstance(value, str) and value.strip():
            return value.strip()

        for child in obj.values():
            found = find_first_enc_para_r(child)
            if found:
                return found

    elif isinstance(obj, list):
        for child in obj:
            found = find_first_enc_para_r(child)
            if found:
                return found

    return None


def build_start_racelive_url():
    today = datetime.now().strftime("%Y%m%d")

    pre_race_file = (
        BASE
        / "data_daily"
        / today
        / "pre_race.json"
    )

    print("[1] 今日の最初のレースURL作成")
    print("PRE RACE FILE:", pre_race_file)

    if not pre_race_file.exists():
        raise FileNotFoundError(
            f"今日のpre_race.jsonがありません: {pre_race_file}"
        )

    with open(
        pre_race_file,
        "r",
        encoding="utf-8",
    ) as f:
        pre_race_data = json.load(f)

    enc_para_r = find_first_enc_para_r(
        pre_race_data
    )

    if not enc_para_r:
        raise RuntimeError(
            "pre_race.json内にencParaRが見つかりません"
        )

    target_url = (
        "https://www.keirin.jp/pc/racelive"
        "?encp="
        + enc_para_r
    )

    print("ENCP:", enc_para_r)
    print("TARGET URL:", target_url)

    return today, target_url


# ============================================================
# MAIN
# ============================================================


def main():

    print()

    print(
        "="
        * 100
    )

    print(
        "043 全開催 × 全R 正式ライン取得"
    )

    print(
        "="
        * 100
    )

    print()


    expected_date = datetime.now().strftime("%Y%m%d")

    with sync_playwright() as p:

        # ====================================================
        # Edge自動起動
        # ====================================================

        print()
        print("[1] Edge自動起動")

        browser = p.chromium.launch(
            headless=False,
            channel="msedge",
        )

        context = browser.new_context()

        page = context.new_page()

        # ====================================================
        # トップページから正式LIVE導線でraceliveへ入る
        # ====================================================

        print()
        print("[2] KEIRIN.JPトップページ表示")

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded",
            timeout=120000,
        )

        page.wait_for_timeout(5000)

        print("TOP PAGE:", page.url)
        print("TOP TITLE:", page.title())

        live_buttons = page.locator(
            "button[id^='hcombtnLive']"
        )

        live_count = live_buttons.count()

        print("LIVE BUTTON COUNT:", live_count)

        if live_count == 0:
            print("ERROR: LIVEボタンが見つかりません")
            browser.close()
            return

        clicked = False

        for live_index in range(live_count):

            button = live_buttons.nth(live_index)

            try:
                if not button.is_visible():
                    continue

                button_id = button.get_attribute("id")

                print("LIVE CLICK:", button_id)

                button.click(timeout=30000)

                clicked = True
                break

            except Exception as e:
                print("LIVE CLICK SKIP:", repr(e))

        if not clicked:
            print("ERROR: LIVEボタンをクリックできません")
            browser.close()
            return

        print()
        print("[3] racelive正式遷移待機")

        try:
            page.wait_for_url(
                "**/pc/racelive**",
                timeout=120000,
            )
        except Exception:
            pass

        page.wait_for_timeout(8000)


        print()

        print(
            "TARGET PAGE:"
        )

        print(
            page.url
        )


        current_body = get_body_text(page)

        if (
            "EC0500E" in current_body
            or
            "予期せぬエラー" in current_body
            or
            "keirin.jp" not in page.url.lower()
            or
            "racelive" not in page.url.lower()
        ):

            print()

            print(
                "ERROR: raceliveページ表示失敗"
            )

            browser.close()

            return


        # ====================================================
        # 日付
        # ====================================================


        body_text = (
            get_body_text(
                page
            )
        )


        race_date = (
            extract_race_date(
                body_text
            )
            or
            expected_date
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
        # 開催一覧
        # ====================================================


        live_venues = (
            get_live_venues(
                page
            )
        )


        print()

        print(
            "[3] LIVE開催一覧"
        )

        print()

        print(
            "VENUE COUNT:",
            len(
                live_venues
            )
        )


        for item in live_venues:

            print(

                item["venue"],

                "->",

                item["button_id"]

            )


        # ====================================================
        # 全開催巡回
        # ====================================================


        venue_results = []


        for venue_index, venue_data in enumerate(
            live_venues,
            start=1,
        ):

            venue_name = (
                venue_data[
                    "venue"
                ]
            )


            print()

            print(
                "#"
                * 100
            )

            print(

                f"VENUE "
                f"{venue_index}/"
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


            venue_record = {

                "venue":
                    venue_name,

                "live_button":
                    venue_data,

                "venue_wait":
                    None,

                "status":
                    "VENUE_RUNNING",

                "error":
                    None,

                "races":
                    [],

            }


            # =================================================
            # 開催クリック
            # =================================================


            before = (
                get_pj0314_signature(
                    page
                )
            )


            try:

                page.locator(
                    "#"
                    +
                    venue_data[
                        "button_id"
                    ]
                ).click(
                    timeout=30000
                )


            except Exception as e:

                venue_record[
                    "status"
                ] = (
                    "VENUE_CLICK_ERROR"
                )

                venue_record[
                    "error"
                ] = (
                    repr(
                        e
                    )
                )


                venue_results.append(
                    venue_record
                )


                save_progress(
                    race_date,
                    live_venues,
                    venue_results,
                )


                print()

                print(
                    "VENUE CLICK ERROR:"
                )

                print(
                    repr(
                        e
                    )
                )


                continue


            venue_wait = (
                wait_pj0314_change(
                    page,
                    before,
                    VENUE_WAIT_TIMEOUT,
                )
            )


            venue_record[
                "venue_wait"
            ] = (
                venue_wait
            )


            print()

            print(
                "VENUE WAIT:",
                venue_wait
            )


            # =================================================
            # R一覧
            # =================================================


            race_buttons = (
                get_race_buttons(
                    page
                )
            )


            print()

            print(
                "RACE COUNT:",
                len(
                    race_buttons
                )
            )


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


                race_record = {

                    "race_date":
                        race_date,

                    "venue":
                        venue_name,

                    "race_no":
                        race_no,

                    "race_key":
                        race_key,

                    "status":
                        None,

                    "error":
                        None,

                    "race_button":
                        race_button,

                    "race_wait":
                        None,

                    "prediction_type":
                        None,

                    "provider":
                        None,

                    "main_lines":
                        [],

                    "has_competition":
                        False,

                    "competition_rows":
                        [],

                    "display_rows":
                        [],

                    "validation":
                        None,

                }


                # =============================================
                # Rクリック
                # =============================================


                before = (
                    get_pj0314_signature(
                        page
                    )
                )


                try:

                    page.locator(
                        "#"
                        +
                        race_button[
                            "id"
                        ]
                    ).click(
                        timeout=30000
                    )


                except Exception as e:

                    race_record[
                        "status"
                    ] = (
                        "RACE_CLICK_ERROR"
                    )

                    race_record[
                        "error"
                    ] = (
                        repr(
                            e
                        )
                    )


                    venue_record[
                        "races"
                    ].append(
                        race_record
                    )


                    print()

                    print(
                        "RACE CLICK ERROR:"
                    )

                    print(
                        repr(
                            e
                        )
                    )


                    continue


                race_wait = (
                    wait_pj0314_change(
                        page,
                        before,
                        RACE_WAIT_TIMEOUT,
                    )
                )


                race_record[
                    "race_wait"
                ] = (
                    race_wait
                )


                # =============================================
                # DOM取得
                # =============================================


                try:

                    dom = (
                        inspect_line_cells(
                            page
                        )
                    )


                except Exception as e:

                    race_record[
                        "status"
                    ] = (
                        "DOM_ERROR"
                    )

                    race_record[
                        "error"
                    ] = (
                        repr(
                            e
                        )
                    )


                    venue_record[
                        "races"
                    ].append(
                        race_record
                    )


                    print()

                    print(
                        "DOM ERROR:"
                    )

                    print(
                        repr(
                            e
                        )
                    )


                    continue


                # =============================================
                # 並び予想なし
                # =============================================


                if (
                    not dom.get(
                        "line_target_exists"
                    )
                ):

                    race_record[
                        "status"
                    ] = (
                        "LINE_NOT_FOUND"
                    )


                    venue_record[
                        "races"
                    ].append(
                        race_record
                    )


                    print()

                    print(
                        "STATUS: LINE_NOT_FOUND"
                    )


                    save_progress(
                        race_date,
                        live_venues,
                        venue_results
                        +
                        [
                            venue_record
                        ],
                    )


                    continue


                # =============================================
                # ROW解析
                # =============================================


                analysis = (
                    analyze_rows(
                        dom
                    )
                )


                main_lines = (
                    analysis.get(
                        "main_lines",
                        []
                    )
                )


                competition_rows = (
                    analysis.get(
                        "competition_rows",
                        []
                    )
                )


                has_competition = (

                    dom.get(
                        "has_competition_text"
                    )
                    is True

                    or

                    len(
                        competition_rows
                    )
                    >
                    0

                )


                validation = (
                    validate_riders(
                        main_lines,
                        competition_rows,
                    )
                )


                race_record[
                    "prediction_type"
                ] = (
                    dom.get(
                        "prediction_type"
                    )
                )


                race_record[
                    "provider"
                ] = (
                    dom.get(
                        "provider"
                    )
                )


                race_record[
                    "main_lines"
                ] = (
                    main_lines
                )


                race_record[
                    "has_competition"
                ] = (
                    has_competition
                )


                race_record[
                    "competition_rows"
                ] = (
                    competition_rows
                )


                race_record[
                    "display_rows"
                ] = (
                    analysis.get(
                        "display_rows",
                        []
                    )
                )


                race_record[
                    "validation"
                ] = (
                    validation
                )


                # =============================================
                # STATUS
                # =============================================


                if (
                    not main_lines
                ):

                    race_record[
                        "status"
                    ] = (
                        "LINE_NOT_FOUND"
                    )


                elif validation.get(
                    "has_duplicate"
                ):

                    race_record[
                        "status"
                    ] = (
                        "RIDER_VALIDATION_ERROR"
                    )


                else:

                    race_record[
                        "status"
                    ] = (
                        "LINE_FOUND"
                    )


                venue_record[
                    "races"
                ].append(
                    race_record
                )


                # =============================================
                # 表示
                # =============================================


                print()

                print(
                    "STATUS:",
                    race_record[
                        "status"
                    ]
                )

                print(
                    "TYPE:",
                    race_record[
                        "prediction_type"
                    ]
                )

                print(
                    "PROVIDER:",
                    race_record[
                        "provider"
                    ]
                )

                print(
                    "MAIN LINES:",
                    race_record[
                        "main_lines"
                    ]
                )

                print(
                    "COMPETITION:",
                    race_record[
                        "has_competition"
                    ]
                )

                print(
                    "COMPETITION ROWS:",
                    [

                        row.get(
                            "car_numbers"
                        )

                        for row in race_record[
                            "competition_rows"
                        ]

                    ]
                )

                print(
                    "RIDERS:",
                    validation.get(
                        "unique_rider_numbers"
                    )
                )


                # =============================================
                # 途中保存
                # =============================================


                save_progress(
                    race_date,
                    live_venues,
                    venue_results
                    +
                    [
                        venue_record
                    ],
                )


            # =================================================
            # 開催完了
            # =================================================


            venue_record[
                "status"
            ] = (
                "VENUE_COMPLETE"
            )


            venue_results.append(
                venue_record
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


    # ========================================================
    # 最終結果
    # ========================================================


    print()

    print(
        "#"
        * 100
    )

    print(
        "043 最終結果"
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
        "COMPETITION:",
        output[
            "competition_count"
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


    for venue_data in output[
        "venues"
    ]:

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
            len(
                races
            )
        )

        print(
            "LINE FOUND:",
            len([

                race

                for race in races

                if (
                    race.get(
                        "status"
                    )
                    ==
                    "LINE_FOUND"
                )

            ])
        )

        print(
            "COMPETITION:",
            len([

                race

                for race in races

                if race.get(
                    "has_competition"
                )
                is True

            ])
        )

        print(
            "LINE NOT FOUND:",
            len([

                race

                for race in races

                if (
                    race.get(
                        "status"
                    )
                    ==
                    "LINE_NOT_FOUND"
                )

            ])
        )

        print(
            "VALIDATION ERROR:",
            len([

                race

                for race in races

                if (
                    race.get(
                        "status"
                    )
                    ==
                    "RIDER_VALIDATION_ERROR"
                )

            ])
        )


    print()

    print(
        "★ 競りありレース ★"
    )


    for venue_data in output[
        "venues"
    ]:

        for race in venue_data.get(
            "races",
            []
        ):

            if race.get(
                "has_competition"
            ) is True:

                print()

                print(
                    race.get(
                        "race_key"
                    )
                )

                print(
                    "TYPE:",
                    race.get(
                        "prediction_type"
                    )
                )

                print(
                    "MAIN:",
                    race.get(
                        "main_lines"
                    )
                )

                print(
                    "COMPETITION ROWS:",
                    [

                        row.get(
                            "car_numbers"
                        )

                        for row in race.get(
                            "competition_rows",
                            []
                        )

                    ]
                )


    print()

    print(
        "保存先:"
    )

    print(
        OUT_FILE
    )

    print()

    print(
        "=== 043 完了 ==="
    )


if __name__ == "__main__":

    main()