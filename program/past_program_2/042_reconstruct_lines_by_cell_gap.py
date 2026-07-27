from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
import json
import time


# ============================================================
# 042
#
# セル位置・車番間隔による
# ライン自動復元テスト
#
# 041で判明:
#
# ・通常並びは1段
# ・競りありは複数段
# ・競り表示には「競」文字あり
# ・base_color_0だけでライン分割するのは危険
#
# 今回:
#
# ・各車番のcell_indexを取得
# ・車番セル位置の間隔でライン分割
# ・車番数最多の段をMAIN ROWとする
# ・その他段をCOMPETITION ROWとして保存
#
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "042_cell_gap_lines"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_FILE = (
    OUT_DIR
    / "042_cell_gap_lines.json"
)

CDP_URL = "http://127.0.0.1:9222"


TARGETS = [

    ("伊東", 5),

    ("大垣", 8),

    ("いわき平", 1),

    ("いわき平", 2),

    ("いわき平", 3),

    ("いわき平", 6),

]


KNOWN_SPECIAL = {

    "大垣_8R":
        "ジカ競り",

    "いわき平_1R":
        "ジカ競り",

}


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
# PJ0314変化待ち
# ============================================================


def wait_pj0314_change(
    page,
    before,
    timeout_seconds=15,
):

    start = time.time()


    while (
        time.time() - start
        <
        timeout_seconds
    ):

        try:

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

        except Exception:

            pass


        time.sleep(
            0.5
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
# LIVE開催一覧
# 039 / 041 成功方式
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
# 並び予想 車番セル位置取得
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

                target_html:
                    null,

                line_table_html:
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
            // 並び予想TABLE
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


            output.target_html = (
                target.outerHTML || ""
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

                        outer_html:
                            el.outerHTML || "",

                    });

                }

            }


            output.has_competition_text = (

                output.competition_texts.length
                >
                0

            );


            // =================================================
            // 最初の.snumから最小TABLE
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


            output.line_table_html = (
                lineTable.outerHTML || ""
            );


            // =================================================
            // ROW
            // =================================================


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

                const allTokens = [];


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


                        const className = (
                            typeof snum.className
                            === "string"
                            ? snum.className
                            : ""
                        );


                        const rect = (
                            snum.getBoundingClientRect()
                        );


                        let tokenType = (
                            "other"
                        );


                        let value = null;


                        if (
                            /^[1-9]$/.test(
                                text
                            )
                        ) {

                            tokenType = (
                                "car"
                            );

                            value = (
                                Number(
                                    text
                                )
                            );


                            carCells.push({

                                car_number:
                                    value,

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
                                    className,

                                outer_html:
                                    snum.outerHTML || "",

                            });

                        }

                        else if (
                            className.includes(
                                "base_color_0"
                            )
                        ) {

                            tokenType = (
                                "base_color_0"
                            );

                        }


                        allTokens.push({

                            cell_index:
                                cellIndex,

                            snum_index:
                                snumIndex,

                            token_type:
                                tokenType,

                            value:
                                value,

                            text:
                                text,

                            class_name:
                                className,

                            x:
                                rect.x,

                            y:
                                rect.y,

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
                            item => item.car_number
                        ),

                    car_cells:
                        carCells,

                    all_tokens:
                        allTokens,

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

                    outer_html:
                        tr.outerHTML || "",

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
# 車番セル間隔からライン復元
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
# ROW解析
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


    if not analyzed_rows:

        return {

            "main_row_index":
                None,

            "main_lines":
                [],

            "competition_rows":
                [],

            "all_rows":
                [],

        }


    # ========================================================
    # 車番数最多ROWをメイン段とする
    # ========================================================


    main_row = max(

        analyzed_rows,

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

        row

        for row in analyzed_rows

        if (
            row.get(
                "row_index"
            )
            !=
            main_row_index
            and
            row.get(
                "car_count",
                0
            )
            >
            0
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

        "all_rows":
            analyzed_rows,

    }


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
        "042 セル間隔 ライン自動復元テスト"
    )

    print(
        "="
        * 100
    )

    print()


    results = []


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


        page = None


        for context in browser.contexts:

            for candidate in context.pages:

                try:

                    print(
                        "PAGE:",
                        candidate.url
                    )


                    if (
                        "keirin.jp"
                        in candidate.url.lower()
                        and
                        "racelive"
                        in candidate.url.lower()
                    ):

                        page = candidate

                except Exception:

                    pass


        if page is None:

            print()

            print(
                "ERROR: raceliveページなし"
            )

            return


        print()

        print(
            "TARGET PAGE:"
        )

        print(
            page.url
        )


        # ====================================================
        # 開催一覧
        # ====================================================


        live_venues = (
            get_live_venues(
                page
            )
        )


        venue_map = {

            item["venue"]:
                item

            for item in live_venues

        }


        print()

        print(
            "[3] LIVE開催一覧"
        )

        print()


        for item in live_venues:

            print(

                item["venue"],

                "->",

                item["button_id"]

            )


        # ====================================================
        # 対象巡回
        # ====================================================


        for target_index, (
            venue,
            race_no,
        ) in enumerate(
            TARGETS,
            start=1,
        ):

            race_key = (
                f"{venue}_"
                f"{race_no}R"
            )


            print()

            print(
                "#"
                * 100
            )

            print(

                f"TARGET "
                f"{target_index}/"
                f"{len(TARGETS)}"

            )

            print(
                "RACE:",
                race_key
            )

            print(
                "KNOWN:",
                KNOWN_SPECIAL.get(
                    race_key
                )
            )

            print(
                "#"
                * 100
            )


            record = {

                "venue":
                    venue,

                "race_no":
                    race_no,

                "race_key":
                    race_key,

                "known_special":
                    KNOWN_SPECIAL.get(
                        race_key
                    ),

                "status":
                    None,

                "error":
                    None,

                "venue_wait":
                    None,

                "race_wait":
                    None,

                "dom":
                    None,

                "analysis":
                    None,

            }


            venue_button = (
                venue_map.get(
                    venue
                )
            )


            if not venue_button:

                record["status"] = (
                    "VENUE_BUTTON_NOT_FOUND"
                )

                results.append(
                    record
                )

                print()

                print(
                    "VENUE BUTTON NOT FOUND"
                )

                continue


            try:

                # =============================================
                # 開催クリック
                # =============================================


                before = (
                    get_pj0314_signature(
                        page
                    )
                )


                page.locator(
                    "#"
                    +
                    venue_button[
                        "button_id"
                    ]
                ).click(
                    timeout=30000
                )


                venue_wait = (
                    wait_pj0314_change(
                        page,
                        before,
                    )
                )


                record["venue_wait"] = (
                    venue_wait
                )


                print()

                print(
                    "VENUE WAIT:",
                    venue_wait
                )


                # =============================================
                # Rクリック
                # =============================================


                race_button_id = (
                    "hhRaceBtn"
                    +
                    str(
                        race_no
                    )
                )


                race_button = (
                    page.locator(
                        "#"
                        +
                        race_button_id
                    )
                )


                if (
                    race_button.count()
                    ==
                    0
                ):

                    record["status"] = (
                        "RACE_BUTTON_NOT_FOUND"
                    )

                    results.append(
                        record
                    )

                    print()

                    print(
                        "RACE BUTTON NOT FOUND"
                    )

                    continue


                before = (
                    get_pj0314_signature(
                        page
                    )
                )


                race_button.click(
                    timeout=30000
                )


                race_wait = (
                    wait_pj0314_change(
                        page,
                        before,
                    )
                )


                record["race_wait"] = (
                    race_wait
                )


                print(
                    "RACE WAIT:",
                    race_wait
                )


                # =============================================
                # DOM取得
                # =============================================


                dom = (
                    inspect_line_cells(
                        page
                    )
                )


                record["dom"] = (
                    dom
                )


                if not dom.get(
                    "pj0314_exists"
                ):

                    record["status"] = (
                        "PJ0314_NOT_FOUND"
                    )


                elif not dom.get(
                    "line_target_exists"
                ):

                    record["status"] = (
                        "LINE_TARGET_NOT_FOUND"
                    )


                else:

                    analysis = (
                        analyze_rows(
                            dom
                        )
                    )


                    record["analysis"] = (
                        analysis
                    )


                    record["status"] = (
                        "LINES_RECONSTRUCTED"
                    )


                # =============================================
                # 表示
                # =============================================


                print()

                print(
                    "STATUS:",
                    record["status"]
                )

                print(
                    "TYPE:",
                    dom.get(
                        "prediction_type"
                    )
                )

                print(
                    "PROVIDER:",
                    dom.get(
                        "provider"
                    )
                )

                print(
                    "ROW COUNT:",
                    dom.get(
                        "row_count"
                    )
                )

                print(
                    "競 TEXT:",
                    dom.get(
                        "has_competition_text"
                    )
                )


                analysis = (
                    record.get(
                        "analysis"
                    )
                    or
                    {}
                )


                print()

                print(
                    "★ ROW解析 ★"
                )


                for row in analysis.get(
                    "all_rows",
                    []
                ):

                    print()

                    print(
                        "ROW:",
                        row.get(
                            "row_index"
                        )
                    )

                    print(
                        "CARS:",
                        row.get(
                            "car_numbers"
                        )
                    )

                    print(
                        "CELL INDEX:",
                        row.get(
                            "car_cell_indexes"
                        )
                    )

                    print(
                        "LINES:",
                        row.get(
                            "reconstructed_lines"
                        )
                    )


                print()

                print(
                    "MAIN ROW:",
                    analysis.get(
                        "main_row_index"
                    )
                )

                print(
                    "MAIN LINES:",
                    analysis.get(
                        "main_lines"
                    )
                )

                print(
                    "COMPETITION ROWS:",
                    [

                        row.get(
                            "car_numbers"
                        )

                        for row in analysis.get(
                            "competition_rows",
                            []
                        )

                    ]
                )


            except Exception as e:

                record["status"] = (
                    "ERROR"
                )

                record["error"] = (
                    repr(
                        e
                    )
                )


                print()

                print(
                    "ERROR:"
                )

                print(
                    repr(
                        e
                    )
                )


            results.append(
                record
            )


            # ================================================
            # 途中保存
            # ================================================


            output = {

                "program":
                    "042_reconstruct_lines_by_cell_gap.py",

                "captured_at":
                    datetime.now().isoformat(),

                "target_count":
                    len(
                        TARGETS
                    ),

                "known_special":
                    KNOWN_SPECIAL,

                "results":
                    results,

            }


            with open(
                OUT_FILE,
                "w",
                encoding="utf-8",
            ) as f:

                json.dump(
                    output,
                    f,
                    ensure_ascii=False,
                    indent=2,
                )


        # ====================================================
        # 最終保存
        # ====================================================


        output = {

            "program":
                "042_reconstruct_lines_by_cell_gap.py",

            "captured_at":
                datetime.now().isoformat(),

            "target_count":
                len(
                    TARGETS
                ),

            "known_special":
                KNOWN_SPECIAL,

            "results":
                results,

        }


        with open(
            OUT_FILE,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                output,
                f,
                ensure_ascii=False,
                indent=2,
            )


    # ========================================================
    # 最終結果
    # ========================================================


    print()

    print(
        "="
        * 100
    )

    print(
        "042 最終結果"
    )

    print(
        "="
        * 100
    )


    for item in results:

        dom = (
            item.get(
                "dom"
            )
            or
            {}
        )


        analysis = (
            item.get(
                "analysis"
            )
            or
            {}
        )


        print()

        print(
            "-"
            * 100
        )

        print(
            "RACE:",
            item.get(
                "race_key"
            )
        )

        print(
            "KNOWN:",
            item.get(
                "known_special"
            )
        )

        print(
            "STATUS:",
            item.get(
                "status"
            )
        )

        print(
            "TYPE:",
            dom.get(
                "prediction_type"
            )
        )

        print(
            "競 TEXT:",
            dom.get(
                "has_competition_text"
            )
        )


        for row in analysis.get(
            "all_rows",
            []
        ):

            print(

                "ROW",
                row.get(
                    "row_index"
                ),

                "CARS",
                row.get(
                    "car_numbers"
                ),

                "CELLS",
                row.get(
                    "car_cell_indexes"
                ),

                "LINES",
                row.get(
                    "reconstructed_lines"
                ),

            )


        print(
            "MAIN ROW:",
            analysis.get(
                "main_row_index"
            )
        )

        print(
            "MAIN LINES:",
            analysis.get(
                "main_lines"
            )
        )

        print(
            "COMPETITION ROWS:",
            [

                row.get(
                    "car_numbers"
                )

                for row in analysis.get(
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
        "=== 042 完了 ==="
    )


if __name__ == "__main__":

    main()