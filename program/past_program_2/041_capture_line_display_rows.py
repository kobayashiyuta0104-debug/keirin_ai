from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
import json
import time


# ============================================================
# 041
#
# 並び予想DOM
# 表示段単位取得テスト
#
# 040修正版
#
# 修正:
# 開催名取得を039成功方式
# p.place 直接取得へ戻す
#
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "041_line_display_rows"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_FILE = (
    OUT_DIR
    / "041_line_display_rows.json"
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

        time.sleep(0.5)


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
#
# 039成功方式
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
# 並び表示段取得
# ============================================================


def inspect_line_rows(page):

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

                display_rows:
                    [],

                row_count:
                    0,

                has_multi_row:
                    false,

                has_competition_text:
                    false,

                competition_texts:
                    [],

                target_text:
                    null,

                target_html:
                    null,

                line_table_html:
                    null,

            };


            const pj = (
                document.querySelector(
                    "#PJ0314"
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
            // 競り文字探索
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
            // .snumを持つ最小TABLE探索
            // =================================================


            const snums = Array.from(
                target.querySelectorAll(
                    ".snum"
                )
            );


            if (
                snums.length === 0
            ) {

                return output;

            }


            let lineTable = null;


            let current = (
                snums[0].closest(
                    "table"
                )
            );


            if (current) {

                lineTable = current;

            }


            if (!lineTable) {

                return output;

            }


            output.line_table_html = (
                lineTable.outerHTML || ""
            );


            // =================================================
            // 直属TR取得
            // =================================================


            let rows = [];


            if (
                lineTable.tBodies
                &&
                lineTable.tBodies.length
                >
                0
            ) {

                rows = Array.from(
                    lineTable.tBodies[0].rows
                );

            }


            // =================================================
            // 各表示段解析
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


                const tokens = [];

                const carNumbers = [];

                const separatorCellIndexes = [];


                for (
                    let cellIndex = 0;
                    cellIndex < cells.length;
                    cellIndex++
                ) {

                    const td = (
                        cells[cellIndex]
                    );


                    const snum = (
                        td.querySelector(
                            ".snum"
                        )
                    );


                    if (snum) {

                        const text = (
                            snum.textContent || ""
                        ).trim();


                        const className = (

                            typeof snum.className
                            === "string"

                            ?

                            snum.className

                            :

                            ""

                        );


                        const rect = (
                            snum.getBoundingClientRect()
                        );


                        let tokenType = (
                            "unknown"
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

                            carNumbers.push(
                                value
                            );

                        }

                        else if (
                            className.includes(
                                "base_color_0"
                            )
                        ) {

                            tokenType = (
                                "separator"
                            );

                            value = 0;

                            separatorCellIndexes.push(
                                cellIndex
                            );

                        }

                        else if (
                            text === ""
                        ) {

                            tokenType = (
                                "blank"
                            );

                        }


                        tokens.push({

                            cell_index:
                                cellIndex,

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

                            width:
                                rect.width,

                            height:
                                rect.height,

                            outer_html:
                                snum.outerHTML || "",

                        });

                    }

                    else {

                        const img = (
                            td.querySelector(
                                "img"
                            )
                        );


                        if (img) {

                            tokens.push({

                                cell_index:
                                    cellIndex,

                                token_type:
                                    "image",

                                value:
                                    null,

                                text:
                                    "",

                                class_name:
                                    typeof img.className
                                    === "string"
                                    ? img.className
                                    : "",

                                src:
                                    img.getAttribute(
                                        "src"
                                    ) || "",

                                outer_html:
                                    img.outerHTML || "",

                            });

                        }

                        else {

                            const text = (
                                td.innerText || ""
                            ).trim();


                            if (text) {

                                tokens.push({

                                    cell_index:
                                        cellIndex,

                                    token_type:
                                        "text",

                                    value:
                                        null,

                                    text:
                                        text,

                                    class_name:
                                        typeof td.className
                                        === "string"
                                        ? td.className
                                        : "",

                                    outer_html:
                                        td.outerHTML || "",

                                });

                            }

                        }

                    }

                }


                const rowRect = (
                    tr.getBoundingClientRect()
                );


                output.display_rows.push({

                    row_index:
                        rowIndex,

                    row_text:
                        tr.innerText || "",

                    car_numbers:
                        carNumbers,

                    separator_cell_indexes:
                        separatorCellIndexes,

                    token_count:
                        tokens.length,

                    tokens:
                        tokens,

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
                output.display_rows.length
            );


            output.has_multi_row = (

                output.row_count
                >
                1

            );


            return output;

        }
        """
    )


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
        "041 並び予想 表示段DOM取得テスト"
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


        print()

        print(
            "[3] LIVE開催一覧"
        )


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

                "venue_button":
                    None,

                "venue_wait":
                    None,

                "race_button_id":
                    None,

                "race_wait":
                    None,

                "status":
                    None,

                "error":
                    None,

                "dom":
                    None,

            }


            venue_button = (
                venue_map.get(
                    venue
                )
            )


            record["venue_button"] = (
                venue_button
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
                # レースクリック
                # =============================================


                race_button_id = (
                    "hhRaceBtn"
                    +
                    str(
                        race_no
                    )
                )


                record["race_button_id"] = (
                    race_button_id
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
                    inspect_line_rows(
                        page
                    )
                )


                record["dom"] = (
                    dom
                )


                if not dom[
                    "pj0314_exists"
                ]:

                    record["status"] = (
                        "PJ0314_NOT_FOUND"
                    )

                elif not dom[
                    "line_target_exists"
                ]:

                    record["status"] = (
                        "LINE_TARGET_NOT_FOUND"
                    )

                else:

                    record["status"] = (
                        "ROWS_CAPTURED"
                    )


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
                    "MULTI ROW:",
                    dom.get(
                        "has_multi_row"
                    )
                )

                print(
                    "競 TEXT:",
                    dom.get(
                        "has_competition_text"
                    )
                )


                print()

                print(
                    "DISPLAY ROWS:"
                )


                for row in dom.get(
                    "display_rows",
                    []
                ):

                    print(

                        "ROW",
                        row[
                            "row_index"
                        ],

                        "CARS:",
                        row[
                            "car_numbers"
                        ],

                        "SEP:",
                        row[
                            "separator_cell_indexes"
                        ],

                        "TEXT:",
                        repr(
                            row[
                                "row_text"
                            ]
                        ),

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
                    "041_capture_line_display_rows.py",

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
                "041_capture_line_display_rows.py",

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
        "041 最終結果"
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


        print()

        print(
            "-"
            * 100
        )

        print(
            "RACE:",
            item[
                "race_key"
            ]
        )

        print(
            "KNOWN:",
            item[
                "known_special"
            ]
        )

        print(
            "STATUS:",
            item[
                "status"
            ]
        )

        print(
            "TYPE:",
            dom.get(
                "prediction_type"
            )
        )

        print(
            "ROW COUNT:",
            dom.get(
                "row_count"
            )
        )

        print(
            "MULTI ROW:",
            dom.get(
                "has_multi_row"
            )
        )

        print(
            "競 TEXT:",
            dom.get(
                "has_competition_text"
            )
        )


        for row in dom.get(
            "display_rows",
            []
        ):

            print(

                "ROW",
                row[
                    "row_index"
                ],

                ":",

                row[
                    "car_numbers"
                ],

                "SEP",

                row[
                    "separator_cell_indexes"
                ],

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
        "=== 041 完了 ==="
    )


if __name__ == "__main__":

    main()