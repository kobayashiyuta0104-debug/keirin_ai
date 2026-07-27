from pathlib import Path
from datetime import datetime
import json

from playwright.sync_api import sync_playwright


# ============================================================
# 032
#
# 並び予想 DOM構造 詳細解析
#
# 目的:
#   ・現在表示中の並び予想を調査
#   ・「並び予想」を含む表示ブロックを特定
#   ・車番要素を全部取得
#   ・親要素を最大8階層取得
#   ・兄弟要素を取得
#   ・class / id / outerHTML取得
#   ・座標取得
#
# 今回はライン取得しない
# DOM構造を特定するだけ
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "032_line_dom_structure"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_JSON = (
    OUT_DIR
    / "032_line_dom_structure.json"
)


CDP_URL = "http://127.0.0.1:9222"


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
        "=== 032 並び予想 DOM構造 詳細解析 ==="
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


        # ====================================================
        # DOM解析
        # ====================================================


        print()

        print(
            "[4] 並び予想DOM解析"
        )


        result = target_page.evaluate(
            """
            () => {

                function elementInfo(
                    el,
                    maxHtml = 50000
                ) {

                    if (!el) {

                        return null;

                    }


                    let rect = null;


                    try {

                        const r = (
                            el.getBoundingClientRect()
                        );


                        rect = {

                            x: r.x,

                            y: r.y,

                            width: r.width,

                            height: r.height,

                            top: r.top,

                            right: r.right,

                            bottom: r.bottom,

                            left: r.left

                        };

                    } catch (e) {

                        rect = null;

                    }


                    let outerHTML = "";


                    try {

                        outerHTML = (
                            el.outerHTML || ""
                        ).slice(
                            0,
                            maxHtml
                        );

                    } catch (e) {

                        outerHTML = "";

                    }


                    let innerText = "";


                    try {

                        innerText = (
                            el.innerText || ""
                        ).slice(
                            0,
                            20000
                        );

                    } catch (e) {

                        innerText = "";

                    }


                    return {

                        tagName:
                            el.tagName || "",

                        id:
                            el.id || "",

                        className:
                            typeof el.className
                            === "string"
                            ? el.className
                            : "",

                        innerText:
                            innerText,

                        childCount:
                            el.children
                            ? el.children.length
                            : 0,

                        rect:
                            rect,

                        outerHTML:
                            outerHTML

                    };

                }


                const output = {

                    found: false,

                    page_url:
                        location.href,

                    target: null,

                    target_parents: [],

                    number_elements: [],

                    direct_children: []

                };


                // =============================================
                // 「並び予想」を含む要素を全部探す
                // =============================================


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


                let target = null;


                // =============================================
                // 情報提供 + 数字を持つ最小ブロック
                // =============================================


                for (
                    const candidate
                    of candidates
                ) {

                    const text = (
                        candidate.innerText || ""
                    );


                    if (
                        text.includes(
                            "情報提供"
                        )
                        &&
                        /[1-9]/.test(text)
                    ) {

                        target = candidate;

                        break;

                    }

                }


                if (!target) {

                    return output;

                }


                output.found = true;

                output.target = (
                    elementInfo(target)
                );


                // =============================================
                // target親要素 8階層
                // =============================================


                let current = target;


                for (
                    let level = 0;
                    level < 8;
                    level++
                ) {

                    if (!current) {

                        break;

                    }


                    output.target_parents.push({

                        level: level,

                        element:
                            elementInfo(
                                current
                            )

                    });


                    current = (
                        current.parentElement
                    );

                }


                // =============================================
                // target直下の子要素
                // =============================================


                output.direct_children = (
                    Array.from(
                        target.children
                    ).map(
                        (
                            child,
                            index
                        ) => ({

                            index: index,

                            element:
                                elementInfo(
                                    child
                                )

                        })
                    )
                );


                // =============================================
                // 車番候補
                //
                // innerTextが完全に1～9
                // =============================================


                const numberElements = (
                    Array.from(
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


                            // 子要素にも単独車番がある場合は除外
                            // 最小要素だけ残す


                            const childHasNumber = (
                                Array.from(
                                    el.children
                                ).some(
                                    child => {

                                        const childText = (
                                            child.innerText || ""
                                        ).trim();


                                        return (
                                            /^[1-9]$/.test(
                                                childText
                                            )
                                        );

                                    }
                                )
                            );


                            return (
                                !childHasNumber
                            );

                        }
                    )
                );


                // =============================================
                // 各車番の詳細
                // =============================================


                for (
                    let index = 0;
                    index < numberElements.length;
                    index++
                ) {

                    const el = (
                        numberElements[index]
                    );


                    const text = (
                        el.innerText || ""
                    ).trim();


                    const item = {

                        index: index,

                        number:
                            Number(text),

                        element:
                            elementInfo(el),

                        parents: [],

                        siblings: []

                    };


                    // =========================================
                    // 親8階層
                    // =========================================


                    let parent = el;


                    for (
                        let level = 0;
                        level < 8;
                        level++
                    ) {

                        if (!parent) {

                            break;

                        }


                        item.parents.push({

                            level: level,

                            element:
                                elementInfo(
                                    parent
                                )

                        });


                        parent = (
                            parent.parentElement
                        );

                    }


                    // =========================================
                    // 同じ親の兄弟
                    // =========================================


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
                                            sibling,
                                            20000
                                        )

                                })
                            )
                        );

                    }


                    output.number_elements.push(
                        item
                    );

                }


                return output;

            }
            """
        )


        # ====================================================
        # 保存
        # ====================================================


        output = {

            "program":
                "032_inspect_line_dom_structure.py",

            "captured_at":
                datetime.now().isoformat(),

            "page_url":
                target_page.url,

            "page_title":
                safe_title(target_page),

            "result":
                result

        }


        save_json(
            OUT_JSON,
            output,
        )


        # ====================================================
        # ターミナル表示
        # ====================================================


        print()

        print(
            "#" * 100
        )

        print(
            "032 最終結果"
        )

        print(
            "#" * 100
        )

        print()

        print(
            "FOUND:",
            result.get(
                "found"
            )
        )


        target = result.get(
            "target"
        )


        if target:

            print()

            print(
                "TARGET TAG:",
                target.get(
                    "tagName"
                )
            )

            print(
                "TARGET ID:",
                target.get(
                    "id"
                )
            )

            print(
                "TARGET CLASS:",
                target.get(
                    "className"
                )
            )

            print()

            print(
                "TARGET TEXT:"
            )

            print(
                target.get(
                    "innerText"
                )
            )


        number_elements = (
            result.get(
                "number_elements",
                []
            )
        )


        print()

        print(
            "車番候補数:",
            len(number_elements)
        )


        print()

        print(
            "★ 車番候補一覧 ★"
        )


        for item in number_elements:

            element = item[
                "element"
            ]


            rect = (
                element.get(
                    "rect"
                )
                or {}
            )


            print()

            print(
                "-" * 100
            )

            print(
                "INDEX:",
                item["index"]
            )

            print(
                "NUMBER:",
                item["number"]
            )

            print(
                "TAG:",
                element.get(
                    "tagName"
                )
            )

            print(
                "ID:",
                element.get(
                    "id"
                )
            )

            print(
                "CLASS:",
                element.get(
                    "className"
                )
            )

            print(
                "X:",
                rect.get(
                    "x"
                )
            )

            print(
                "Y:",
                rect.get(
                    "y"
                )
            )

            print()

            print(
                "★ 親CLASS一覧 ★"
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

                    parent_element.get(
                        "tagName"
                    ),

                    "| ID=",

                    parent_element.get(
                        "id"
                    ),

                    "| CLASS=",

                    parent_element.get(
                        "className"
                    ),

                    "| CHILDREN=",

                    parent_element.get(
                        "childCount"
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
            "=== 032 完了 ==="
        )


if __name__ == "__main__":

    main()