from pathlib import Path
from datetime import datetime
import json
import re
import time

from playwright.sync_api import sync_playwright


# ============================================================
# 033
#
# 並び予想 DOM区切り方式 全R取得テスト
#
# 目的:
#   ・Edgeデバッグ接続
#   ・現在開いているKEIRIN.JP raceliveページを使用
#   ・1開催の全Rを自動巡回
#   ・PJ0314 並び予想DOMを解析
#   ・snum base_color_1～9 = 車番
#   ・snum base_color_0 = ライン区切り
#   ・line_groupsを正しく作成
#   ・二分戦 / 三分戦 / 四分戦等とライン数を照合
#   ・race_key付きJSON保存
#
# 例:
#
#   1 5 空 4 空 3 6 空 2 7
#
#       ↓
#
#   [[1, 5], [4], [3, 6], [2, 7]]
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
    / "033_daily_line_predictions.json"
)


CDP_URL = "http://127.0.0.1:9222"

CLICK_WAIT_SECONDS = 3


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
# title安全取得
# ============================================================


def safe_title(page):

    try:

        return page.title()

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
# 開催場取得
# ============================================================


def extract_venue(
    page_text,
    title,
):

    known_venues = [

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


    combined = (
        title
        + "\n"
        + page_text
    )


    for venue in known_venues:

        if venue in combined:

            return venue


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
# 予想形態 → 期待ライン数
# ============================================================


def expected_line_count(
    prediction_type,
):

    mapping = {

        "二分戦": 2,
        "三分戦": 3,
        "四分戦": 4,
        "五分戦": 5,

    }


    return mapping.get(
        prediction_type
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
                    + raceNo
                );


                const element = (
                    document.getElementById(id)
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
#
# 032で判明した構造:
#
# <div class="snum base_color_1">1</div>
# <div class="snum base_color_5">5</div>
# <div class="snum base_color_0"></div>
# <div class="snum base_color_4">4</div>
#
# base_color_0をライン境界として使用
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

                    expected_line_count: null,

                    actual_line_count: 0,

                    line_count_match: null,

                    rider_numbers: [],

                    unique_rider_numbers: [],

                    duplicate_rider_numbers: []

                },

                target_text: null,

                target_html: null

            };


            // =================================================
            // PJ0314を最優先
            // =================================================


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


            // =================================================
            // PJ0314で見つからない場合
            // 並び予想文字から探索
            // =================================================


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


            output.target_text = (
                target.innerText || ""
            );


            output.target_html = (
                target.outerHTML || ""
            );


            const fullText = (
                target.innerText || ""
            );


            // =================================================
            // 予想形態
            // =================================================


            const typeMatch = (
                fullText.match(
                    /(?:二分戦|三分戦|四分戦|五分戦|細切れ)/
                )
            );


            if (typeMatch) {

                output.prediction_type = (
                    typeMatch[0]
                );

            }


            // =================================================
            // 情報提供元
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
            // 更新日時
            //
            // target内にない場合はPJ0314周辺から取得
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
            // snum要素取得
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


            // =================================================
            // DOM順に解析
            //
            // base_color_1～9
            //     → 車番
            //
            // base_color_0
            //     → ライン区切り
            // =================================================


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


                // =============================================
                // base_color_0 = 空欄 / 区切り
                // =============================================


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


                // =============================================
                // 車番
                // =============================================


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


            // =================================================
            // 最後のライン追加
            // =================================================


            if (
                currentLine.length
            ) {

                lineGroups.push(
                    currentLine
                );

            }


            // =================================================
            // 空ライン除外
            // =================================================


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
            // 検証
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
                    duplicateRiderNumbers

            };


            // =================================================
            // FOUND判定
            // =================================================


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
# main
# ============================================================


def main():

    print(
        "=== 033 DOM区切り方式 全R並び予想取得テスト ==="
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
                "EdgeでKEIRIN.JPの"
                "並び予想が見えるページを"
                "開いてください"
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
        # 基本情報
        # ====================================================


        page_text = (
            target_page.locator(
                "body"
            ).inner_text()
        )


        page_title = (
            safe_title(
                target_page
            )
        )


        race_date = (
            extract_race_date(
                page_text
            )
        )


        venue = (
            extract_venue(
                page_text,
                page_title,
            )
        )


        print()

        print(
            "DATE:",
            race_date,
        )

        print(
            "VENUE:",
            venue,
        )


        # ====================================================
        # Rボタン取得
        # ====================================================


        print()

        print(
            "[4] Rボタン取得"
        )


        race_buttons = (
            get_race_buttons(
                target_page
            )
        )


        print()

        print(
            "RACE BUTTON COUNT:",
            len(race_buttons),
        )


        # ====================================================
        # 全R巡回
        # ====================================================


        print()

        print(
            "[5] 全R巡回開始"
        )


        races = []


        for button in race_buttons:

            race_no = (
                button["race_no"]
            )


            race_key = (
                build_race_key(
                    race_date,
                    venue,
                    race_no,
                )
            )


            print()

            print(
                "=" * 100
            )

            print(
                race_key
            )

            print(
                "=" * 100
            )


            # ================================================
            # Rクリック
            # ================================================


            try:

                target_page.locator(
                    "#"
                    +
                    button["id"]
                ).click(
                    timeout=30000
                )


                time.sleep(
                    CLICK_WAIT_SECONDS
                )


            except Exception as e:

                print()

                print(
                    "CLICK ERROR:"
                )

                print(
                    repr(e)
                )


                races.append({

                    "race_date":
                        race_date,

                    "venue":
                        venue,

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


            # ================================================
            # DOM解析
            # ================================================


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


                races.append({

                    "race_date":
                        race_date,

                    "venue":
                        venue,

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


            print()

            print(
                "FOUND:",
                line_data.get(
                    "found"
                )
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
                "UPDATED:",
                line_data.get(
                    "updated_at"
                )
            )

            print(
                "SNUM COUNT:",
                line_data.get(
                    "snum_count"
                )
            )

            print()

            print(
                "LINE GROUPS:"
            )

            print(
                json.dumps(
                    line_data.get(
                        "line_groups"
                    ),
                    ensure_ascii=False,
                    indent=2,
                )
            )

            print()

            print(
                "EXPECTED LINE COUNT:",
                validation.get(
                    "expected_line_count"
                )
            )

            print(
                "ACTUAL LINE COUNT:",
                validation.get(
                    "actual_line_count"
                )
            )

            print(
                "LINE COUNT MATCH:",
                validation.get(
                    "line_count_match"
                )
            )

            print(
                "RIDER NUMBERS:",
                validation.get(
                    "rider_numbers"
                )
            )

            print(
                "DUPLICATE RIDERS:",
                validation.get(
                    "duplicate_rider_numbers"
                )
            )


            # ================================================
            # status判定
            # ================================================


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


            races.append({

                "race_date":
                    race_date,

                "venue":
                    venue,

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


            # ================================================
            # 途中保存
            # ================================================


            save_json(

                OUT_JSON,

                {

                    "program":
                        "033_capture_line_predictions_by_dom_separator.py",

                    "captured_at":
                        datetime.now().isoformat(),

                    "race_date":
                        race_date,

                    "venue":
                        venue,

                    "race_count":
                        len(races),

                    "races":
                        races,

                },

            )


        # ====================================================
        # 集計
        # ====================================================


        line_found = [

            race

            for race in races

            if race["status"]
            == "LINE_FOUND"

        ]


        line_not_found = [

            race

            for race in races

            if race["status"]
            == "LINE_NOT_FOUND"

        ]


        validation_errors = [

            race

            for race in races

            if race["status"]
            == "LINE_VALIDATION_ERROR"

        ]


        errors = [

            race

            for race in races

            if race["status"]
            in {
                "CLICK_ERROR",
                "DOM_ERROR",
            }

        ]


        output = {

            "program":
                "033_capture_line_predictions_by_dom_separator.py",

            "captured_at":
                datetime.now().isoformat(),

            "race_date":
                race_date,

            "venue":
                venue,

            "race_count":
                len(races),

            "line_found_count":
                len(line_found),

            "line_not_found_count":
                len(line_not_found),

            "validation_error_count":
                len(validation_errors),

            "error_count":
                len(errors),

            "races":
                races,

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
            "#" * 100
        )

        print(
            "033 最終結果"
        )

        print(
            "#" * 100
        )

        print()

        print(
            "DATE:",
            race_date,
        )

        print(
            "VENUE:",
            venue,
        )

        print()

        print(
            "RACE COUNT:",
            len(races),
        )

        print(
            "LINE FOUND:",
            len(line_found),
        )

        print(
            "LINE NOT FOUND:",
            len(line_not_found),
        )

        print(
            "VALIDATION ERROR:",
            len(validation_errors),
        )

        print(
            "ERROR:",
            len(errors),
        )


        print()

        print(
            "★ LINE FOUND一覧 ★"
        )


        for race in line_found:

            line_prediction = (
                race[
                    "line_prediction"
                ]
            )


            print()

            print(
                race["race_key"]
            )

            print(
                "TYPE:",
                line_prediction.get(
                    "prediction_type"
                )
            )

            print(
                "PROVIDER:",
                line_prediction.get(
                    "provider"
                )
            )

            print(
                "LINE:",
                line_prediction.get(
                    "line_groups"
                )
            )


        if validation_errors:

            print()

            print(
                "★ VALIDATION ERROR一覧 ★"
            )


            for race in validation_errors:

                line_prediction = (
                    race[
                        "line_prediction"
                    ]
                )


                print()

                print(
                    race["race_key"]
                )

                print(
                    "TYPE:",
                    line_prediction.get(
                        "prediction_type"
                    )
                )

                print(
                    "LINE:",
                    line_prediction.get(
                        "line_groups"
                    )
                )

                print(
                    "VALIDATION:",
                    line_prediction.get(
                        "validation"
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
            "=== 033 完了 ==="
        )


if __name__ == "__main__":

    main()