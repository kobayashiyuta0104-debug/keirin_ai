from pathlib import Path
from datetime import datetime
import json

from playwright.sync_api import sync_playwright


# ============================================================
# 035
#
# 開催切替 DOM / ナビゲーション構造 詳細解析
#
# 目的:
#   ・034で開催切替に失敗した原因を調査
#   ・開催名を含む要素を全取得
#   ・親要素を最大8階層取得
#   ・href / onclick / data-* / class / id を取得
#   ・兄弟要素を取得
#
# 今回はクリックしない
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "035_venue_navigation_dom"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_JSON = (
    OUT_DIR
    / "035_venue_navigation_dom.json"
)


CDP_URL = "http://127.0.0.1:9222"


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


def safe_title(page):

    try:

        return page.title()

    except Exception:

        return ""


def main():

    print(
        "=== 035 開催切替DOM 詳細解析 ==="
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

            print(
                "ERROR: Edge contextなし"
            )

            return


        target_page = None


        print()

        print(
            "[2] raceliveページ探索"
        )


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

        print(
            safe_title(target_page)
        )


        result = target_page.evaluate(
            """
            (knownVenues) => {

                function getAttributes(el) {

                    const attributes = {};


                    for (
                        const attr
                        of Array.from(
                            el.attributes || []
                        )
                    ) {

                        attributes[
                            attr.name
                        ] = attr.value;

                    }


                    return attributes;

                }


                function getDataset(el) {

                    const dataset = {};


                    try {

                        for (
                            const [
                                key,
                                value
                            ]
                            of Object.entries(
                                el.dataset || {}
                            )
                        ) {

                            dataset[key] = value;

                        }

                    } catch (e) {

                    }


                    return dataset;

                }


                function getRect(el) {

                    try {

                        const rect = (
                            el.getBoundingClientRect()
                        );


                        return {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height,
                            top: rect.top,
                            right: rect.right,
                            bottom: rect.bottom,
                            left: rect.left
                        };

                    } catch (e) {

                        return null;

                    }

                }


                function elementInfo(el) {

                    if (!el) {

                        return null;

                    }


                    return {

                        tag_name:
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
                            ).slice(
                                0,
                                20000
                            ),

                        href:
                            el.href || "",

                        onclick:
                            el.getAttribute(
                                "onclick"
                            )
                            || "",

                        role:
                            el.getAttribute(
                                "role"
                            )
                            || "",

                        attributes:
                            getAttributes(el),

                        dataset:
                            getDataset(el),

                        child_count:
                            el.children
                            ? el.children.length
                            : 0,

                        rect:
                            getRect(el),

                        outer_html:
                            (
                                el.outerHTML || ""
                            ).slice(
                                0,
                                50000
                            )

                    };

                }


                const output = {

                    page_url:
                        location.href,

                    matches:
                        []

                };


                const all = Array.from(
                    document.querySelectorAll(
                        "body *"
                    )
                );


                for (
                    const venue
                    of knownVenues
                ) {

                    const venueMatches = [];


                    for (
                        let index = 0;
                        index < all.length;
                        index++
                    ) {

                        const el = all[index];


                        const text = (
                            el.innerText || ""
                        ).trim();


                        if (
                            text !== venue
                        ) {

                            continue;

                        }


                        const item = {

                            dom_index:
                                index,

                            venue:
                                venue,

                            element:
                                elementInfo(el),

                            parents:
                                [],

                            siblings:
                                []

                        };


                        let current = el;


                        for (
                            let level = 0;
                            level < 8;
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
                                    )

                            });


                            current = (
                                current.parentElement
                            );

                        }


                        if (
                            el.parentElement
                        ) {

                            item.siblings = (
                                Array.from(
                                    el.parentElement
                                    .children
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
                                            )

                                    })
                                )
                            );

                        }


                        venueMatches.push(
                            item
                        );

                    }


                    if (
                        venueMatches.length
                    ) {

                        output.matches.push({

                            venue:
                                venue,

                            match_count:
                                venueMatches.length,

                            items:
                                venueMatches

                        });

                    }

                }


                return output;

            }
            """,
            KNOWN_VENUES,
        )


        output = {

            "program":
                "035_inspect_venue_navigation_dom.py",

            "captured_at":
                datetime.now().isoformat(),

            "page_url":
                target_page.url,

            "page_title":
                safe_title(
                    target_page
                ),

            "result":
                result,

        }


        save_json(
            OUT_JSON,
            output,
        )


        print()

        print(
            "#"
            * 100
        )

        print(
            "035 最終結果"
        )

        print(
            "#"
            * 100
        )


        matches = (
            result.get(
                "matches",
                []
            )
        )


        print()

        print(
            "VENUE MATCH COUNT:",
            len(matches)
        )


        for venue_data in matches:

            print()

            print(
                "="
                * 100
            )

            print(
                "VENUE:",
                venue_data["venue"]
            )

            print(
                "MATCH COUNT:",
                venue_data[
                    "match_count"
                ]
            )


            for item in venue_data[
                "items"
            ]:

                element = (
                    item["element"]
                )


                print()

                print(
                    "-"
                    * 100
                )

                print(
                    "DOM INDEX:",
                    item["dom_index"]
                )

                print(
                    "TAG:",
                    element["tag_name"]
                )

                print(
                    "ID:",
                    element["id"]
                )

                print(
                    "CLASS:",
                    element["class_name"]
                )

                print(
                    "HREF:",
                    element["href"]
                )

                print(
                    "ONCLICK:",
                    element["onclick"]
                )

                print(
                    "ATTRIBUTES:"
                )

                print(
                    json.dumps(
                        element[
                            "attributes"
                        ],
                        ensure_ascii=False,
                        indent=2,
                    )
                )

                print(
                    "DATASET:"
                )

                print(
                    json.dumps(
                        element[
                            "dataset"
                        ],
                        ensure_ascii=False,
                        indent=2,
                    )
                )


                print()

                print(
                    "★ 親要素 ★"
                )


                for parent in item[
                    "parents"
                ]:

                    parent_element = (
                        parent["element"]
                    )


                    print(

                        "LEVEL",

                        parent["level"],

                        "|",

                        parent_element[
                            "tag_name"
                        ],

                        "| ID=",

                        parent_element[
                            "id"
                        ],

                        "| CLASS=",

                        parent_element[
                            "class_name"
                        ],

                        "| HREF=",

                        parent_element[
                            "href"
                        ],

                        "| ONCLICK=",

                        parent_element[
                            "onclick"
                        ],

                        "| DATASET=",

                        json.dumps(
                            parent_element[
                                "dataset"
                            ],
                            ensure_ascii=False,
                        ),

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
            "=== 035 完了 ==="
        )


if __name__ == "__main__":

    main()