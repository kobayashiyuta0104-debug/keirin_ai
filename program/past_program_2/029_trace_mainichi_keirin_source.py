from pathlib import Path
import json

from playwright.sync_api import sync_playwright


# ============================================================
# 029
#
# 「情報提供：毎日競輪」
# 「毎日競輪」
# 「並び予想」
#
# 画面DOMから表示元を逆追跡
#
# 目的:
#   ・全通信監視はしない
#   ・response.text() は使わない
#   ・現在表示済みDOMを直接調査
#   ・毎日競輪の文字を持つ要素を特定
#   ・親要素を最大10階層保存
#   ・周辺HTMLを保存
#   ・script src一覧保存
#   ・iframe一覧保存
#   ・ページHTML内の対象文字位置を保存
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "029_mainichi_keirin_source"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_JSON = (
    OUT_DIR
    / "029_mainichi_keirin_source.json"
)


CDP_URL = "http://127.0.0.1:9222"


TARGET_WORDS = [
    "情報提供",
    "競輪毎日",
    "並び予想",
    "narabiyoso",
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


def safe_content(page):

    try:

        return page.content()

    except Exception:

        return ""


def find_word_context(
    text,
    word,
    radius=10000,
):

    results = []

    lower_text = text.lower()
    lower_word = word.lower()

    start = 0


    while True:

        pos = lower_text.find(
            lower_word,
            start,
        )


        if pos < 0:

            break


        left = max(
            0,
            pos - radius,
        )

        right = min(
            len(text),
            pos + len(word) + radius,
        )


        results.append({
            "position": pos,
            "context": text[left:right],
        })


        start = pos + len(lower_word)


    return results


def inspect_frame(
    frame,
    frame_index,
):

    print()

    print(
        "=" * 100
    )

    print(
        "FRAME:",
        frame_index,
    )

    print(
        "NAME:",
        frame.name,
    )

    print(
        "URL:",
        frame.url,
    )

    print(
        "=" * 100
    )


    result = {
        "frame_index": frame_index,
        "frame_name": frame.name,
        "frame_url": frame.url,
        "word_hits": [],
        "dom_hits": [],
        "scripts": [],
    }


    # --------------------------------------------------------
    # HTML取得
    # --------------------------------------------------------

    try:

        html = frame.content()

    except Exception as e:

        print(
            "HTML取得エラー:",
            repr(e),
        )

        html = ""


    print()

    print(
        "HTML LENGTH:",
        len(html),
    )


    # --------------------------------------------------------
    # HTML文字検索
    # --------------------------------------------------------

    for word in TARGET_WORDS:

        hits = find_word_context(
            html,
            word,
        )


        print()

        print(
            "WORD:",
            word,
        )

        print(
            "HTML HIT:",
            len(hits),
        )


        for hit_index, hit in enumerate(
            hits,
            start=1,
        ):

            print()

            print(
                "-" * 100
            )

            print(
                f"{word} HTML HIT "
                f"{hit_index}"
            )

            print(
                "POSITION:",
                hit["position"],
            )

            print()

            print(
                hit["context"]
            )

            print(
                "-" * 100
            )


            result["word_hits"].append({
                "word": word,
                "position": hit["position"],
                "context": hit["context"],
            })


    # --------------------------------------------------------
    # DOM直接検索
    #
    # body以下の全要素を確認
    # own textだけではなくinnerTextも見る
    # --------------------------------------------------------

    try:

        dom_hits = frame.evaluate(
            """
            (targetWords) => {

                const results = [];

                const elements = Array.from(
                    document.querySelectorAll("body *")
                );

                for (const el of elements) {

                    let text = "";

                    try {

                        text = el.innerText || "";

                    } catch (e) {

                        text = "";

                    }

                    if (!text) {

                        continue;

                    }

                    const matchedWords = [];

                    for (const word of targetWords) {

                        if (
                            text.toLowerCase().includes(
                                word.toLowerCase()
                            )
                        ) {

                            matchedWords.push(word);

                        }

                    }

                    if (!matchedWords.length) {

                        continue;

                    }


                    const parents = [];

                    let current = el;


                    for (
                        let level = 0;
                        level < 10 && current;
                        level++
                    ) {

                        let html = "";

                        try {

                            html = current.outerHTML || "";

                        } catch (e) {

                            html = "";

                        }


                        parents.push({

                            level: level,

                            tagName:
                                current.tagName || "",

                            id:
                                current.id || "",

                            className:
                                typeof current.className === "string"
                                ? current.className
                                : "",

                            text:
                                (
                                    current.innerText || ""
                                ).slice(
                                    0,
                                    5000
                                ),

                            outerHTML:
                                html.slice(
                                    0,
                                    30000
                                )

                        });


                        current = current.parentElement;

                    }


                    results.push({

                        matchedWords: matchedWords,

                        tagName:
                            el.tagName || "",

                        id:
                            el.id || "",

                        className:
                            typeof el.className === "string"
                            ? el.className
                            : "",

                        text:
                            text.slice(
                                0,
                                10000
                            ),

                        parents: parents

                    });

                }


                return results;

            }
            """,
            TARGET_WORDS,
        )


    except Exception as e:

        print()

        print(
            "DOM検索エラー:",
            repr(e),
        )

        dom_hits = []


    result["dom_hits"] = dom_hits


    print()

    print(
        "#" * 100
    )

    print(
        "DOM HIT:",
        len(dom_hits),
    )

    print(
        "#" * 100
    )


    for hit_index, hit in enumerate(
        dom_hits,
        start=1,
    ):

        print()

        print(
            "=" * 100
        )

        print(
            "DOM HIT",
            hit_index,
        )

        print(
            "MATCHED WORDS:",
            hit["matchedWords"],
        )

        print(
            "TAG:",
            hit["tagName"],
        )

        print(
            "ID:",
            hit["id"],
        )

        print(
            "CLASS:",
            hit["className"],
        )

        print()

        print(
            "TEXT:"
        )

        print(
            hit["text"]
        )


        print()

        print(
            "★ 親要素逆追跡 ★"
        )


        for parent in hit["parents"]:

            print()

            print(
                "-" * 100
            )

            print(
                "LEVEL:",
                parent["level"],
            )

            print(
                "TAG:",
                parent["tagName"],
            )

            print(
                "ID:",
                parent["id"],
            )

            print(
                "CLASS:",
                parent["className"],
            )

            print()

            print(
                "TEXT:"
            )

            print(
                parent["text"]
            )

            print()

            print(
                "OUTER HTML:"
            )

            print(
                parent["outerHTML"]
            )


    # --------------------------------------------------------
    # script一覧
    # --------------------------------------------------------

    try:

        scripts = frame.evaluate(
            """
            () => {

                return Array.from(
                    document.scripts
                ).map(
                    (script, index) => ({

                        index: index,

                        src:
                            script.src || "",

                        type:
                            script.type || "",

                        id:
                            script.id || "",

                        textHead:
                            (
                                script.textContent || ""
                            ).slice(
                                0,
                                5000
                            )

                    })
                );

            }
            """
        )


    except Exception as e:

        print()

        print(
            "SCRIPT取得エラー:",
            repr(e),
        )

        scripts = []


    result["scripts"] = scripts


    print()

    print(
        "#" * 100
    )

    print(
        "SCRIPT数:",
        len(scripts),
    )

    print(
        "#" * 100
    )


    for script in scripts:

        print()

        print(
            "SCRIPT INDEX:",
            script["index"],
        )

        print(
            "SRC:",
            script["src"],
        )

        print(
            "TYPE:",
            script["type"],
        )

        print(
            "ID:",
            script["id"],
        )


        text_head = (
            script["textHead"]
        )


        matched = []


        for word in TARGET_WORDS:

            if (
                word.lower()
                in text_head.lower()
            ):

                matched.append(word)


        if matched:

            print()

            print(
                "🔥 SCRIPT TARGET HIT:"
            )

            print(
                matched
            )

            print()

            print(
                text_head
            )


    return result


def main():

    print(
        "=== 029 毎日競輪・並び予想 表示元追跡 ==="
    )

    print()


    with sync_playwright() as p:

        print(
            "[1] Edgeデバッグ接続"
        )


        browser = p.chromium.connect_over_cdp(
            CDP_URL
        )


        contexts = browser.contexts


        print(
            "context数:",
            len(contexts),
        )


        if not contexts:

            print()

            print(
                "ERROR:"
                " Edge contextがありません"
            )

            return


        page_results = []


        print()

        print(
            "[2] KEIRIN.JPページ探索"
        )


        for context_index, context in enumerate(
            contexts,
            start=1,
        ):

            for page_index, page in enumerate(
                context.pages,
                start=1,
            ):

                try:

                    page_url = page.url

                    page_title = safe_title(
                        page
                    )


                    print()

                    print(
                        "=" * 100
                    )

                    print(
                        f"PAGE "
                        f"{context_index}-"
                        f"{page_index}"
                    )

                    print(
                        "URL:",
                        page_url,
                    )

                    print(
                        "TITLE:",
                        page_title,
                    )

                    print(
                        "FRAME数:",
                        len(page.frames),
                    )


                    if (
                        "keirin.jp"
                        not in page_url.lower()
                    ):

                        print(
                            "KEIRIN.JP以外"
                            " → SKIP"
                        )

                        continue


                    page_result = {
                        "context_index": (
                            context_index
                        ),
                        "page_index": (
                            page_index
                        ),
                        "page_url": page_url,
                        "page_title": page_title,
                        "frames": [],
                    }


                    for frame_index, frame in enumerate(
                        page.frames,
                        start=1,
                    ):

                        frame_result = (
                            inspect_frame(
                                frame,
                                frame_index,
                            )
                        )


                        page_result[
                            "frames"
                        ].append(
                            frame_result
                        )


                    page_results.append(
                        page_result
                    )


                except Exception as e:

                    print()

                    print(
                        "PAGE解析エラー:",
                        repr(e),
                    )


        output = {
            "program": (
                "029_trace_mainichi_keirin_source.py"
            ),
            "target_words": TARGET_WORDS,
            "page_results": page_results,
        }


        save_json(
            OUT_JSON,
            output,
        )


        print()

        print(
            "=" * 100
        )

        print(
            "029 最終結果"
        )

        print(
            "=" * 100
        )

        print()

        print(
            "解析KEIRIN.JPページ:",
            len(page_results),
        )


        total_word_hits = 0

        total_dom_hits = 0


        for page_result in page_results:

            for frame_result in (
                page_result["frames"]
            ):

                total_word_hits += len(
                    frame_result[
                        "word_hits"
                    ]
                )

                total_dom_hits += len(
                    frame_result[
                        "dom_hits"
                    ]
                )


        print(
            "HTML WORD HIT:",
            total_word_hits,
        )

        print(
            "DOM HIT:",
            total_dom_hits,
        )


        print()

        print(
            "★ HIT FRAME一覧 ★"
        )


        for page_result in page_results:

            for frame_result in (
                page_result["frames"]
            ):

                if (
                    not frame_result[
                        "word_hits"
                    ]
                    and not frame_result[
                        "dom_hits"
                    ]
                ):

                    continue


                print()

                print(
                    "-" * 100
                )

                print(
                    "PAGE:"
                )

                print(
                    page_result[
                        "page_url"
                    ]
                )

                print()

                print(
                    "FRAME:"
                )

                print(
                    frame_result[
                        "frame_url"
                    ]
                )

                print()

                print(
                    "WORD HIT:",
                    len(
                        frame_result[
                            "word_hits"
                        ]
                    ),
                )

                print(
                    "DOM HIT:",
                    len(
                        frame_result[
                            "dom_hits"
                        ]
                    ),
                )


                words = sorted({
                    item["word"]
                    for item
                    in frame_result[
                        "word_hits"
                    ]
                })


                print(
                    "WORDS:",
                    words,
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
            "=== 029 完了 ==="
        )


if __name__ == "__main__":

    main()