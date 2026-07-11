from pathlib import Path
from datetime import datetime
import json
import re
import time

from playwright.sync_api import sync_playwright


# ============================================================
# 031
#
# 当日 並び予想 自動取得テスト
#
# 目的:
#   ・Edgeデバッグ接続
#   ・現在開いているKEIRIN.JP raceliveページを使用
#   ・開催場名を取得
#   ・1R～12Rボタンを順番に探索
#   ・未終了レースをクリック
#   ・表示済みDOMから「並び予想」を取得
#   ・情報提供元を取得
#   ・更新日時を取得
#   ・ライン構成を解析
#   ・race_key付きJSON保存
#
# race_key:
#   YYYYMMDD_開催場_7R
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
    / "031_daily_line_predictions.json"
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
# 安全取得
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
# ライン数字解析
# ============================================================


def parse_line_numbers(
    raw_text,
):

    if not raw_text:

        return []


    lines = []


    # --------------------------------------------------------
    # DOM側で数字の並びを取得
    #
    # 例:
    #   1 7    4 3 5    2 6
    #
    # 空白量からの解析は壊れやすいため、
    # DOM要素構造側で取得したline_groupsを優先
    # --------------------------------------------------------


    return lines


# ============================================================
# 現在表示中の並び予想DOM解析
# ============================================================


def extract_line_prediction(
    page,
):

    result = page.evaluate(
        """
        () => {

            const output = {

                found: false,

                prediction_type: null,

                provider: null,

                updated_at: null,

                line_groups: [],

                target_text: null,

                target_html: null

            };


            const allElements = Array.from(
                document.querySelectorAll("body *")
            );


            // =================================================
            // 「並び予想」を含む最小要素を探す
            // =================================================


            const candidates = allElements.filter(
                el => {

                    const text = (
                        el.innerText || ""
                    ).trim();


                    return (
                        text.includes("並び予想")
                    );

                }
            );


            if (!candidates.length) {

                return output;

            }


            candidates.sort(
                (
                    a,
                    b
                ) => {

                    const aLength = (
                        a.innerText || ""
                    ).length;

                    const bLength = (
                        b.innerText || ""
                    ).length;


                    return (
                        aLength - bLength
                    );

                }
            );


            let target = null;


            for (
                const candidate
                of candidates
            ) {

                const text = (
                    candidate.innerText || ""
                );


                if (
                    /情報提供/.test(text)
                    &&
                    /[1-9]/.test(text)
                ) {

                    target = candidate;

                    break;

                }

            }


            if (!target) {

                target = candidates[0];

            }


            output.target_text = (
                target.innerText || ""
            );


            output.target_html = (
                target.outerHTML || ""
            );


            // =================================================
            // 親要素を広げて並びブロックを探す
            // =================================================


            let container = target;


            for (
                let level = 0;
                level < 8;
                level++
            ) {

                if (!container) {

                    break;

                }


                const text = (
                    container.innerText || ""
                );


                if (
                    text.includes("並び予想")
                    &&
                    text.includes("情報提供")
                    &&
                    /[1-9]/.test(text)
                ) {

                    target = container;

                    break;

                }


                container = (
                    container.parentElement
                );

            }


            const fullText = (
                target.innerText || ""
            );


            output.target_text = fullText;

            output.target_html = (
                target.outerHTML || ""
            );


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
            // =================================================


            const updatedMatch = (
                fullText.match(
                    /(20\\d{2}\\/\\d{1,2}\\/\\d{1,2}\\s+\\d{1,2}:\\d{2}\\s*更新)/
                )
            );


            if (updatedMatch) {

                output.updated_at = (
                    updatedMatch[1]
                ).trim();

            }


            // =================================================
            // ライン形態
            //
            // 二分戦
            // 三分戦
            // 四分戦
            // 細切れ
            // =================================================


            const typeMatch = (
                fullText.match(
                    /(二分戦|三分戦|四分戦|五分戦|細切れ)/
                )
            );


            if (typeMatch) {

                output.prediction_type = (
                    typeMatch[1]
                );

            }


            // =================================================
            // 車番要素候補を探す
            //
            // 1文字の1～9だけを持つ要素
            // =================================================


            const numberElements = Array.from(
                target.querySelectorAll("*")
            ).filter(
                el => {

                    const text = (
                        el.innerText || ""
                    ).trim();


                    if (
                        !/^[1-9]$/.test(text)
                    ) {

                        return false;

                    }


                    const childTexts = Array.from(
                        el.children
                    ).map(
                        child => (
                            child.innerText || ""
                        ).trim()
                    ).filter(
                        text => text
                    );


                    if (
                        childTexts.some(
                            text => (
                                /^[1-9]$/.test(text)
                            )
                        )
                    ) {

                        return false;

                    }


                    return true;

                }
            );


            // =================================================
            // 車番要素のDOM情報
            // =================================================


            const numberInfo = (
                numberElements.map(
                    el => {

                        const rect = (
                            el.getBoundingClientRect()
                        );


                        return {

                            number:
                                Number(
                                    (
                                        el.innerText || ""
                                    ).trim()
                                ),

                            x:
                                rect.x,

                            y:
                                rect.y,

                            width:
                                rect.width,

                            height:
                                rect.height,

                            className:
                                typeof el.className
                                === "string"
                                ? el.className
                                : "",

                            parentClass:
                                el.parentElement
                                &&
                                typeof (
                                    el.parentElement
                                    .className
                                ) === "string"
                                ? (
                                    el.parentElement
                                    .className
                                )
                                : ""

                        };

                    }
                )
            );


            // =================================================
            // 重複除去
            //
            // 同じ車番・ほぼ同じ座標
            // =================================================


            const unique = [];


            for (
                const item
                of numberInfo
            ) {

                const exists = (
                    unique.some(
                        old => (

                            old.number
                            === item.number

                            &&

                            Math.abs(
                                old.x - item.x
                            ) < 2

                            &&

                            Math.abs(
                                old.y - item.y
                            ) < 2

                        )
                    )
                );


                if (!exists) {

                    unique.push(item);

                }

            }


            // =================================================
            // 並び予想領域だけ抽出
            //
            // 同じY付近の車番を候補化
            // =================================================


            if (!unique.length) {

                return output;

            }


            const yGroups = [];


            for (
                const item
                of unique
            ) {

                let group = (
                    yGroups.find(
                        g => (
                            Math.abs(
                                g.y - item.y
                            ) < 10
                        )
                    )
                );


                if (!group) {

                    group = {

                        y: item.y,

                        items: []

                    };


                    yGroups.push(group);

                }


                group.items.push(item);

            }


            yGroups.sort(
                (
                    a,
                    b
                ) => (
                    b.items.length
                    - a.items.length
                )
            );


            let raceRow = null;


            for (
                const group
                of yGroups
            ) {

                const numbers = (
                    group.items.map(
                        item => item.number
                    )
                );


                const uniqueNumbers = (
                    Array.from(
                        new Set(numbers)
                    )
                );


                if (
                    uniqueNumbers.length >= 5
                ) {

                    raceRow = group;

                    break;

                }

            }


            if (!raceRow) {

                return output;

            }


            const raceItems = (
                raceRow.items
            ).sort(
                (
                    a,
                    b
                ) => (
                    a.x - b.x
                )
            );


            // =================================================
            // X座標の間隔からライン分割
            //
            // 通常の車番間隔より大きいgapを
            // ライン境界とする
            // =================================================


            const gaps = [];


            for (
                let i = 1;
                i < raceItems.length;
                i++
            ) {

                gaps.push(

                    raceItems[i].x

                    -

                    (
                        raceItems[i - 1].x
                        +
                        raceItems[i - 1].width
                    )

                );

            }


            const positiveGaps = (
                gaps
                .filter(
                    gap => gap >= 0
                )
                .sort(
                    (
                        a,
                        b
                    ) => a - b
                )
            );


            let baseGap = 0;


            if (positiveGaps.length) {

                baseGap = (
                    positiveGaps[
                        Math.floor(
                            positiveGaps.length / 2
                        )
                    ]
                );

            }


            const splitThreshold = Math.max(

                baseGap * 2.2,

                18

            );


            const lineGroups = [];

            let currentLine = [];


            for (
                let i = 0;
                i < raceItems.length;
                i++
            ) {

                const item = raceItems[i];


                if (
                    i > 0
                ) {

                    const previous = (
                        raceItems[i - 1]
                    );


                    const gap = (

                        item.x

                        -

                        (
                            previous.x
                            +
                            previous.width
                        )

                    );


                    if (
                        gap > splitThreshold
                    ) {

                        if (
                            currentLine.length
                        ) {

                            lineGroups.push(
                                currentLine
                            );

                        }


                        currentLine = [];

                    }

                }


                currentLine.push(
                    item.number
                );

            }


            if (
                currentLine.length
            ) {

                lineGroups.push(
                    currentLine
                );

            }


            output.line_groups = (
                lineGroups
            );


            output.number_debug = (
                raceItems
            );


            output.gaps_debug = gaps;

            output.base_gap_debug = (
                baseGap
            );

            output.split_threshold_debug = (
                splitThreshold
            );


            if (
                lineGroups.length
            ) {

                output.found = true;

            }


            return output;

        }
        """
    )


    return result


# ============================================================
# Rボタン取得
# ============================================================


def get_race_buttons(
    page,
):

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

                    race_no: raceNo,

                    id: id,

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
                        (
                            element.disabled
                            === true
                        )

                });

            }


            return results;

        }
        """
    )


# ============================================================
# main
# ============================================================


def main():

    print(
        "=== 031 当日並び予想 自動取得テスト ==="
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


        contexts = browser.contexts


        if not contexts:

            print()

            print(
                "ERROR:"
                " Edge contextなし"
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
                "ERROR:"
                " raceliveページなし"
            )

            print()

            print(
                "Edgeで並び予想が見える"
                "KEIRIN.JPページを"
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
        # ページ基本情報
        # ====================================================


        page_text = (
            target_page.locator(
                "body"
            ).inner_text()
        )


        page_title = safe_title(
            target_page
        )


        race_date = extract_race_date(
            page_text
        )


        venue = extract_venue(
            page_text,
            page_title,
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


        if not race_date:

            print()

            print(
                "WARNING:"
                " 日付取得失敗"
            )


        if not venue:

            print()

            print(
                "WARNING:"
                " 開催場取得失敗"
            )


        # ====================================================
        # Rボタン確認
        # ====================================================


        print()

        print(
            "[4] Rボタン確認"
        )


        race_buttons = get_race_buttons(
            target_page
        )


        print(
            "Rボタン数:",
            len(race_buttons),
        )


        for button in race_buttons:

            print()

            print(
                button
            )


        # ====================================================
        # 各R巡回
        # ====================================================


        print()

        print(
            "[5] 各R 並び予想取得"
        )


        races = []


        for button in race_buttons:

            race_no = button[
                "race_no"
            ]


            class_name = (
                button[
                    "class_name"
                ]
                or ""
            )


            race_key = build_race_key(
                race_date,
                venue,
                race_no,
            )


            print()

            print(
                "=" * 100
            )

            print(
                f"{race_no}R"
            )

            print(
                "race_key:",
                race_key,
            )

            print(
                "class:",
                class_name,
            )


            # ================================================
            # 終了済みはスキップ
            # ================================================


            if (
                "fin"
                in class_name.lower()
            ):

                print(
                    "終了済み → SKIP"
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
                        "FINISHED_SKIP",

                    "button":
                        button,

                })


                continue


            # ================================================
            # Rボタンクリック
            # ================================================


            try:

                target_page.locator(
                    "#"
                    + button["id"]
                ).click(
                    timeout=30000
                )


                time.sleep(
                    CLICK_WAIT_SECONDS
                )


            except Exception as e:

                print(
                    "CLICK ERROR:",
                    repr(e),
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

                    "button":
                        button,

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

                print(
                    "DOM解析 ERROR:",
                    repr(e),
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

                    "button":
                        button,

                })


                continue


            print()

            print(
                "FOUND:",
                line_data.get(
                    "found"
                ),
            )

            print(
                "TYPE:",
                line_data.get(
                    "prediction_type"
                ),
            )

            print(
                "PROVIDER:",
                line_data.get(
                    "provider"
                ),
            )

            print(
                "UPDATED:",
                line_data.get(
                    "updated_at"
                ),
            )

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


            if line_data.get(
                "found"
            ):

                status = (
                    "LINE_FOUND"
                )

            else:

                status = (
                    "LINE_NOT_FOUND"
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
                        "031_capture_daily_line_predictions.py",

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
        # 最終集計
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


        finished_skip = [

            race

            for race in races

            if race["status"]
            == "FINISHED_SKIP"

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
                "031_capture_daily_line_predictions.py",

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

            "finished_skip_count":
                len(finished_skip),

            "error_count":
                len(errors),

            "races":
                races,

        }


        save_json(
            OUT_JSON,
            output,
        )


        print()

        print(
            "#" * 100
        )

        print(
            "031 最終結果"
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
            "FINISHED SKIP:",
            len(finished_skip),
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

            print()

            print(
                race["race_key"]
            )

            print(
                "TYPE:",
                race[
                    "line_prediction"
                ].get(
                    "prediction_type"
                ),
            )

            print(
                "PROVIDER:",
                race[
                    "line_prediction"
                ].get(
                    "provider"
                ),
            )

            print(
                "LINE:"
            )

            print(
                race[
                    "line_prediction"
                ].get(
                    "line_groups"
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
            "=== 031 完了 ==="
        )


if __name__ == "__main__":

    main()