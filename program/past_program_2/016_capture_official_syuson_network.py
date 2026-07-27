from playwright.sync_api import sync_playwright
from pathlib import Path
from urllib.parse import urlparse
from collections import Counter, defaultdict
from datetime import datetime
import json
import re
import time
import traceback


# ============================================================
# 016 修正版
# KEIRIN.JP 正式画面操作
#
# TOP
#   ↓
# 函館開催枠
#   ↓
# 出走表一覧
#   ↓
# 函館4R
#   ↓
# 全通信 / HTML / JavaScript / JSJ TYPE / ライン候補捕獲
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_BASE = (
    BASE
    / "data_official"
    / "line_research"
    / "016_official_syusou_capture"
)

HTML_DIR = OUT_BASE / "html"
BODY_DIR = OUT_BASE / "response_bodies"
SCRIPT_DIR = OUT_BASE / "scripts"

RESULT_JSON = (
    OUT_BASE
    / "016_official_syusou_analysis.json"
)


EDGE_CDP_URL = "http://127.0.0.1:9222"

TOP_URL = "https://keirin.jp/pc/top"

TARGET_PLACE = "函館"
TARGET_RACE_NO = 4


KEYWORDS = [
    "ライン",
    "並び",
    "並び予想",
    "周回",
    "想定",
    "先頭",
    "番手",
    "三番手",
    "単騎",
    "line",
    "narabi",
    "nara",
    "syukai",
    "shukai",
    "bank",
    "bante",
    "sentou",
    "tanki",
    "formation",
    "group",
    "team",
]


JSJ_PATTERN = re.compile(
    r"\bJSJ\d{3}\b",
    re.IGNORECASE,
)


CONTROLLER_PATTERN = re.compile(
    r"""
    (?:
        JSON_REQ_ID_[A-Za-z0-9_]+
        |
        [A-Za-z0-9_]*REQ[A-Za-z0-9_]*
        |
        [A-Za-z0-9_]*JSON[A-Za-z0-9_]*
    )
    \s*[:=]\s*
    ["']
    (JSJ\d{3})
    ["']
    """,
    re.IGNORECASE | re.VERBOSE,
)


def now_iso():

    return datetime.now().isoformat(
        timespec="seconds"
    )


def safe_text(value):

    if value is None:
        return ""

    try:
        return str(value)

    except Exception:
        return repr(value)


def safe_filename(text, max_length=180):

    text = safe_text(text)

    text = re.sub(
        r'[<>:"/\\|?*\x00-\x1f]',
        "_",
        text,
    )

    text = text.strip(" ._")

    if not text:
        text = "unnamed"

    return text[:max_length]


def ensure_dirs():

    OUT_BASE.mkdir(
        parents=True,
        exist_ok=True,
    )

    HTML_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    BODY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    SCRIPT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def save_text(path, text):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
        errors="replace",
    ) as f:

        f.write(text)


def save_json(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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


def extract_jsj_types(text):

    if not text:
        return []

    return sorted(
        {
            value.upper()
            for value
            in JSJ_PATTERN.findall(text)
        }
    )


def find_keywords(text):

    if not text:
        return []

    lower_text = text.lower()

    result = []

    for keyword in KEYWORDS:

        if keyword.lower() in lower_text:

            result.append(keyword)

    return result


def make_keyword_snippets(
    text,
    keyword,
    radius=200,
    limit=10,
):

    if not text:
        return []

    lower_text = text.lower()

    lower_keyword = keyword.lower()

    result = []

    start = 0

    while len(result) < limit:

        position = lower_text.find(
            lower_keyword,
            start,
        )

        if position < 0:
            break

        left = max(
            0,
            position - radius,
        )

        right = min(
            len(text),
            position
            + len(keyword)
            + radius,
        )

        snippet = text[left:right]

        snippet = re.sub(
            r"\s+",
            " ",
            snippet,
        ).strip()

        result.append(snippet)

        start = (
            position
            + len(keyword)
        )

    return result


def collect_keyword_detail(text):

    result = {}

    for keyword in find_keywords(text):

        result[keyword] = (
            make_keyword_snippets(
                text,
                keyword,
            )
        )

    return result


def wait_page(page, seconds=5):

    try:

        page.wait_for_load_state(
            "domcontentloaded",
            timeout=30000,
        )

    except Exception:
        pass

    try:

        page.wait_for_load_state(
            "networkidle",
            timeout=15000,
        )

    except Exception:
        pass

    time.sleep(seconds)


def get_page_summary(page, label):

    result = {
        "label": label,
        "timestamp": now_iso(),
        "url": "",
        "title": "",
        "headings": [],
        "body_text_head": "",
        "jsj_types_in_html": [],
        "keywords_in_html": [],
    }

    try:

        result["url"] = page.url

    except Exception:
        pass

    try:

        result["title"] = page.title()

    except Exception:
        pass

    try:

        headings = page.locator(
            "h1, h2, h3, h4, h5, h6"
        ).all_inner_texts()

        result["headings"] = [
            text.strip()
            for text in headings
            if text.strip()
        ][:100]

    except Exception:
        pass

    try:

        body_text = (
            page.locator("body").inner_text()
        )

        result["body_text_head"] = (
            body_text[:10000]
        )

    except Exception:
        pass

    try:

        html = page.content()

        result["jsj_types_in_html"] = (
            extract_jsj_types(html)
        )

        result["keywords_in_html"] = (
            find_keywords(html)
        )

    except Exception:
        pass

    return result


def save_page_html(page, filename):

    try:

        html = page.content()

        path = HTML_DIR / filename

        save_text(
            path,
            html,
        )

        return str(path)

    except Exception as e:

        return (
            "HTML_SAVE_ERROR: "
            + str(e)
        )


def inspect_place_dom(page, place_name):

    script = """
    (placeName) => {

        const result = [];

        const all = Array.from(
            document.querySelectorAll("*")
        );

        for (const el of all) {

            const ownText = (
                el.innerText ||
                el.textContent ||
                ""
            ).trim();

            if (
                ownText !== placeName
                &&
                !ownText.startsWith(
                    placeName + "\\n"
                )
            ) {
                continue;
            }

            let current = el;

            for (
                let depth = 0;
                depth < 12 && current;
                depth++
            ) {

                const text = (
                    current.innerText ||
                    current.textContent ||
                    ""
                ).trim();

                const html = (
                    current.outerHTML || ""
                );

                const hasPlace =
                    text.includes(placeName);

                const hasSyusou =
                    text.includes("出走表")
                    ||
                    html.includes("出走表")
                    ||
                    html
                        .toLowerCase()
                        .includes(
                            "btnsyusoulistclick"
                        );

                if (
                    hasPlace
                    &&
                    hasSyusou
                ) {

                    result.push({

                        depth: depth,

                        tag:
                            current.tagName,

                        id:
                            current.id || "",

                        className:
                            current.className
                            ? String(
                                current.className
                            )
                            : "",

                        text:
                            text.slice(
                                0,
                                5000
                            ),

                        html:
                            html.slice(
                                0,
                                20000
                            )
                    });

                    break;
                }

                current = (
                    current.parentElement
                );
            }
        }

        return result;
    }
    """

    return page.evaluate(
        script,
        place_name,
    )


def mark_place_syusou_button(
    page,
    place_name,
):

    script = """
    (placeName) => {

        const all = Array.from(
            document.querySelectorAll("*")
        );

        const placeElements = all.filter(
            (el) => {

                const text = (
                    el.innerText ||
                    el.textContent ||
                    ""
                ).trim();

                return (
                    text === placeName
                    ||
                    text.startsWith(
                        placeName + "\\n"
                    )
                );
            }
        );

        const candidates = [];

        for (
            const placeElement
            of placeElements
        ) {

            let current = placeElement;

            for (
                let depth = 0;
                depth < 12 && current;
                depth++
            ) {

                const containerText = (
                    current.innerText ||
                    current.textContent ||
                    ""
                ).trim();

                if (
                    !containerText.includes(
                        placeName
                    )
                ) {

                    current =
                        current.parentElement;

                    continue;
                }

                const clickables = Array.from(
                    current.querySelectorAll(
                        "a, button, input, [onclick]"
                    )
                );

                for (
                    const target
                    of clickables
                ) {

                    const text = (
                        target.innerText ||
                        target.textContent ||
                        target.value ||
                        ""
                    ).trim();

                    const onclick = (
                        target.getAttribute(
                            "onclick"
                        ) || ""
                    );

                    const href = (
                        target.getAttribute(
                            "href"
                        ) || ""
                    );

                    const combined = (
                        text
                        + " "
                        + onclick
                        + " "
                        + href
                    ).toLowerCase();

                    let score = 0;

                    if (
                        text.includes(
                            "出走表"
                        )
                    ) {
                        score += 100;
                    }

                    if (
                        combined.includes(
                            "btnsyusoulistclick"
                        )
                    ) {
                        score += 200;
                    }

                    if (
                        combined.includes(
                            "syusou"
                        )
                    ) {
                        score += 50;
                    }

                    if (score > 0) {

                        candidates.push({

                            element: target,

                            score: score,

                            depth: depth,

                            text: text,

                            onclick: onclick,

                            href: href,

                            containerText:
                                containerText.slice(
                                    0,
                                    5000
                                ),

                            outerHTML:
                                (
                                    target.outerHTML
                                    || ""
                                ).slice(
                                    0,
                                    10000
                                )
                        });
                    }
                }

                current = (
                    current.parentElement
                );
            }
        }

        if (
            candidates.length === 0
        ) {

            return {
                found: false,
                candidates: []
            };
        }

        candidates.sort(
            (a, b) =>
                b.score - a.score
                ||
                a.depth - b.depth
        );

        const selected =
            candidates[0];

        selected.element.setAttribute(
            "data-capture-016-syusou",
            "1"
        );

        return {

            found: true,

            score:
                selected.score,

            depth:
                selected.depth,

            text:
                selected.text,

            onclick:
                selected.onclick,

            href:
                selected.href,

            containerText:
                selected.containerText,

            outerHTML:
                selected.outerHTML,

            candidateCount:
                candidates.length,

            candidates:
                candidates
                    .slice(0, 20)
                    .map(
                        (x) => ({
                            score:
                                x.score,

                            depth:
                                x.depth,

                            text:
                                x.text,

                            onclick:
                                x.onclick,

                            href:
                                x.href,

                            outerHTML:
                                x.outerHTML
                        })
                    )
        };
    }
    """

    return page.evaluate(
        script,
        place_name,
    )


def click_marked_syusou(page):

    locator = page.locator(
        '[data-capture-016-syusou="1"]'
    )

    if locator.count() == 0:

        return (
            False,
            "marked syusou locator not found",
        )

    try:

        locator.first.scroll_into_view_if_needed()

        time.sleep(1)

        locator.first.click(
            timeout=15000,
        )

        return (
            True,
            "clicked",
        )

    except Exception as e:

        return (
            False,
            str(e),
        )


def inspect_race_clickables(
    page,
    race_no,
):

    script = """
    (raceNo) => {

        const result = [];

        const clickables = Array.from(
            document.querySelectorAll(
                "a, button, input, [onclick]"
            )
        );

        for (const el of clickables) {

            const text = (
                el.innerText ||
                el.textContent ||
                el.value ||
                ""
            ).trim();

            const href = (
                el.getAttribute("href")
                || ""
            );

            const onclick = (
                el.getAttribute("onclick")
                || ""
            );

            const title = (
                el.getAttribute("title")
                || ""
            );

            const html = (
                el.outerHTML || ""
            );

            const combined = (
                text
                + " "
                + href
                + " "
                + onclick
                + " "
                + title
                + " "
                + html
            );

            const patterns = [
                `${raceNo}R`,
                `${raceNo}Ｒ`,
                `${raceNo}レース`,
                `第${raceNo}レース`
            ];

            if (
                patterns.some(
                    (pattern) =>
                        combined.includes(
                            pattern
                        )
                )
            ) {

                result.push({

                    text: text,

                    href: href,

                    onclick: onclick,

                    title: title,

                    outerHTML:
                        html.slice(
                            0,
                            10000
                        )
                });
            }
        }

        return result;
    }
    """

    return page.evaluate(
        script,
        race_no,
    )


def mark_race_button(
    page,
    race_no,
):

    script = """
    (raceNo) => {

        const clickables = Array.from(
            document.querySelectorAll(
                "a, button, input, [onclick]"
            )
        );

        const candidates = [];

        for (const el of clickables) {

            const text = (
                el.innerText ||
                el.textContent ||
                el.value ||
                ""
            ).trim();

            const href = (
                el.getAttribute("href")
                || ""
            );

            const onclick = (
                el.getAttribute("onclick")
                || ""
            );

            const title = (
                el.getAttribute("title")
                || ""
            );

            const html = (
                el.outerHTML || ""
            );

            const combined = (
                text
                + " "
                + href
                + " "
                + onclick
                + " "
                + title
                + " "
                + html
            );

            let score = 0;

            if (
                text === `${raceNo}R`
                ||
                text === `${raceNo}Ｒ`
            ) {
                score += 300;
            }

            if (
                text.includes(
                    `${raceNo}R`
                )
                ||
                text.includes(
                    `${raceNo}Ｒ`
                )
            ) {
                score += 150;
            }

            if (
                text.includes(
                    `${raceNo}レース`
                )
                ||
                text.includes(
                    `第${raceNo}レース`
                )
            ) {
                score += 100;
            }

            if (onclick) {
                score += 20;
            }

            if (href) {
                score += 10;
            }

            if (
                combined.includes(
                    `${raceNo}R`
                )
                ||
                combined.includes(
                    `${raceNo}Ｒ`
                )
                ||
                combined.includes(
                    `${raceNo}レース`
                )
                ||
                combined.includes(
                    `第${raceNo}レース`
                )
            ) {

                if (score > 0) {

                    candidates.push({

                        element: el,

                        score: score,

                        text: text,

                        href: href,

                        onclick: onclick,

                        title: title,

                        outerHTML:
                            html.slice(
                                0,
                                10000
                            )
                    });
                }
            }
        }

        if (
            candidates.length === 0
        ) {

            return {
                found: false,
                candidates: []
            };
        }

        candidates.sort(
            (a, b) =>
                b.score - a.score
        );

        const selected =
            candidates[0];

        selected.element.setAttribute(
            "data-capture-016-race",
            "1"
        );

        return {

            found: true,

            score:
                selected.score,

            text:
                selected.text,

            href:
                selected.href,

            onclick:
                selected.onclick,

            title:
                selected.title,

            outerHTML:
                selected.outerHTML,

            candidateCount:
                candidates.length,

            candidates:
                candidates
                    .slice(0, 20)
                    .map(
                        (x) => ({
                            score:
                                x.score,

                            text:
                                x.text,

                            href:
                                x.href,

                            onclick:
                                x.onclick,

                            title:
                                x.title,

                            outerHTML:
                                x.outerHTML
                        })
                    )
        };
    }
    """

    return page.evaluate(
        script,
        race_no,
    )


def click_marked_race(page):

    locator = page.locator(
        '[data-capture-016-race="1"]'
    )

    if locator.count() == 0:

        return (
            False,
            "marked race locator not found",
        )

    try:

        locator.first.scroll_into_view_if_needed()

        time.sleep(1)

        locator.first.click(
            timeout=15000,
        )

        return (
            True,
            "clicked",
        )

    except Exception as e:

        return (
            False,
            str(e),
        )


def main():

    print(
        "=== 016 修正版 "
        "KEIRIN.JP 正式出走表遷移・"
        "ライン通信捕獲 ==="
    )

    print()

    print(
        "対象開催:",
        TARGET_PLACE,
    )

    print(
        "対象レース:",
        f"{TARGET_RACE_NO}R",
    )

    print(
        "CDP:",
        EDGE_CDP_URL,
    )

    print()

    ensure_dirs()

    network_records = []

    response_body_records = []

    script_records = []

    errors = []

    response_counter = {
        "value": 0
    }


    with sync_playwright() as p:

        try:

            print(
                "Edgeデバッグへ接続中..."
            )

            browser = (
                p.chromium.connect_over_cdp(
                    EDGE_CDP_URL
                )
            )

            print(
                "Edgeデバッグ接続成功"
            )

        except Exception as e:

            print()

            print(
                "ERROR: "
                "Edgeデバッグへ接続できません"
            )

            print(e)

            return


        contexts = browser.contexts

        if not contexts:

            print(
                "ERROR: "
                "Edge contextがありません"
            )

            return


        context = contexts[0]

        pages = context.pages

        if pages:

            page = pages[0]

        else:

            page = context.new_page()


        # ====================================================
        # ネットワークイベント
        # ====================================================

        def on_request(request):

            try:

                record = {

                    "event":
                        "request",

                    "timestamp":
                        now_iso(),

                    "method":
                        request.method,

                    "resource_type":
                        request.resource_type,

                    "url":
                        request.url,

                    "post_data":
                        request.post_data,

                    "jsj_types":
                        extract_jsj_types(
                            request.url
                            + " "
                            + safe_text(
                                request.post_data
                            )
                        ),
                }

                network_records.append(
                    record
                )

            except Exception as e:

                errors.append({

                    "stage":
                        "on_request",

                    "error":
                        str(e),
                })


        def on_response(response):

            try:

                request = response.request

                content_type = (
                    response.headers.get(
                        "content-type",
                        "",
                    )
                )

                record = {

                    "event":
                        "response",

                    "timestamp":
                        now_iso(),

                    "status":
                        response.status,

                    "resource_type":
                        request.resource_type,

                    "url":
                        response.url,

                    "content_type":
                        content_type,

                    "jsj_types_url":
                        extract_jsj_types(
                            response.url
                        ),
                }

                network_records.append(
                    record
                )


                lower_content_type = (
                    content_type.lower()
                )

                resource_type = (
                    request.resource_type
                )


                should_read = (

                    resource_type in {
                        "xhr",
                        "fetch",
                        "document",
                        "script",
                    }

                    or
                    "json"
                    in lower_content_type

                    or
                    "javascript"
                    in lower_content_type

                    or
                    "text/"
                    in lower_content_type
                )


                if not should_read:

                    return


                try:

                    body = response.text()

                except Exception as e:

                    errors.append({

                        "stage":
                            "response.text",

                        "url":
                            response.url,

                        "error":
                            str(e),
                    })

                    return


                response_counter["value"] += 1

                body_no = (
                    response_counter["value"]
                )


                parsed = urlparse(
                    response.url
                )

                base_name = (
                    Path(
                        parsed.path
                    ).name
                    or
                    "response"
                )


                extension = ".txt"

                if (
                    "json"
                    in lower_content_type
                ):

                    extension = ".json"

                elif (
                    resource_type == "script"
                    or
                    "javascript"
                    in lower_content_type
                ):

                    extension = ".js"

                elif (
                    resource_type == "document"
                    or
                    "html"
                    in lower_content_type
                ):

                    extension = ".html"


                filename = (

                    f"{body_no:05d}_"

                    f"{resource_type}_"

                    f"{safe_filename(base_name)}"

                    f"{extension}"
                )


                body_path = (
                    BODY_DIR
                    / filename
                )


                save_text(
                    body_path,
                    body,
                )


                jsj_types = (
                    extract_jsj_types(body)
                )

                keywords = (
                    find_keywords(body)
                )

                keyword_detail = (
                    collect_keyword_detail(body)
                )


                body_record = {

                    "body_no":
                        body_no,

                    "timestamp":
                        now_iso(),

                    "url":
                        response.url,

                    "status":
                        response.status,

                    "resource_type":
                        resource_type,

                    "content_type":
                        content_type,

                    "body_length":
                        len(body),

                    "saved_path":
                        str(body_path),

                    "jsj_types":
                        jsj_types,

                    "keywords":
                        keywords,

                    "keyword_detail":
                        keyword_detail,
                }


                response_body_records.append(
                    body_record
                )


                if (
                    resource_type == "script"
                    or
                    "javascript"
                    in lower_content_type
                    or
                    response.url
                        .lower()
                        .endswith(".js")
                ):

                    controller_matches = sorted(
                        {
                            value.upper()
                            for value
                            in CONTROLLER_PATTERN.findall(
                                body
                            )
                        }
                    )


                    script_path = (

                        SCRIPT_DIR

                        / (
                            f"{body_no:05d}_"
                            f"{safe_filename(base_name)}"
                            ".js"
                        )
                    )


                    save_text(
                        script_path,
                        body,
                    )


                    script_records.append({

                        "body_no":
                            body_no,

                        "url":
                            response.url,

                        "saved_path":
                            str(script_path),

                        "body_length":
                            len(body),

                        "jsj_types":
                            jsj_types,

                        "controller_matches":
                            controller_matches,

                        "keywords":
                            keywords,

                        "keyword_detail":
                            keyword_detail,
                    })


            except Exception as e:

                errors.append({

                    "stage":
                        "on_response",

                    "error":
                        str(e),

                    "traceback":
                        traceback.format_exc(),
                })


        page.on(
            "request",
            on_request,
        )

        page.on(
            "response",
            on_response,
        )


        # ====================================================
        # TOP
        # ====================================================

        print()

        print(
            "[1] KEIRIN.JP TOPへ移動"
        )


        try:

            page.goto(
                TOP_URL,
                wait_until="domcontentloaded",
                timeout=60000,
            )

        except Exception as e:

            print(
                "goto警告:",
                e,
            )


        wait_page(
            page,
            seconds=5,
        )


        top_summary = get_page_summary(
            page,
            "top",
        )


        top_html = save_page_html(
            page,
            "001_top.html",
        )


        print()

        print(
            "TOP URL:",
            top_summary["url"],
        )

        print(
            "TOP title:",
            top_summary["title"],
        )

        print(
            "TOP HTML:",
            top_html,
        )


        # ====================================================
        # 函館DOM
        # ====================================================

        print()

        print(
            "[2] 函館開催枠DOMを調査"
        )


        place_dom = inspect_place_dom(
            page,
            TARGET_PLACE,
        )


        print(
            "函館DOM候補数:",
            len(place_dom),
        )


        for index, item in enumerate(
            place_dom[:10],
            start=1,
        ):

            print()

            print(
                f"[函館DOM {index}]"
            )

            print(
                "depth:",
                item.get("depth"),
            )

            print(
                "tag:",
                item.get("tag"),
            )

            print(
                "class:",
                item.get("className"),
            )

            print(
                "text:"
            )

            print(
                safe_text(
                    item.get("text")
                )[:3000]
            )


        # ====================================================
        # 函館出走表一覧
        # ====================================================

        print()

        print(
            "[3] 函館開催枠内の"
            "出走表一覧ボタンを特定"
        )


        syusou_target = (
            mark_place_syusou_button(
                page,
                TARGET_PLACE,
            )
        )


        print(
            json.dumps(
                syusou_target,
                ensure_ascii=False,
                indent=2,
            )[:20000]
        )


        before_syusou_url = page.url


        syusou_click_success = False

        syusou_click_message = ""


        if syusou_target.get("found"):

            print()

            print(
                "★ 函館の出走表一覧候補を発見 ★"
            )

            syusou_click_success, (
                syusou_click_message
            ) = click_marked_syusou(
                page
            )

        else:

            print()

            print(
                "函館の出走表一覧候補を"
                "発見できませんでした"
            )


        print()

        print(
            "クリック結果:",
            syusou_click_success,
        )

        print(
            "クリックメッセージ:",
            syusou_click_message,
        )


        if syusou_click_success:

            wait_page(
                page,
                seconds=7,
            )


        after_syusou_url = page.url


        syusou_summary = get_page_summary(
            page,
            "syusou_list",
        )


        syusou_html = save_page_html(
            page,
            "002_syusou_list.html",
        )


        print()

        print("=" * 70)

        print(
            "出走表一覧 正式遷移確認"
        )

        print("=" * 70)


        print(
            "移動前URL:",
            before_syusou_url,
        )

        print(
            "移動後URL:",
            after_syusou_url,
        )

        print(
            "URL変化:",
            (
                before_syusou_url
                !=
                after_syusou_url
            ),
        )

        print(
            "title:",
            syusou_summary["title"],
        )

        print(
            "見出し:",
            syusou_summary["headings"][:30],
        )

        print()

        print(
            "本文先頭:"
        )

        print(
            syusou_summary[
                "body_text_head"
            ][:5000]
        )

        print()

        print(
            "HTML:",
            syusou_html,
        )


        # ====================================================
        # 4R
        # ====================================================

        print()

        print(
            "[4] 函館4R候補を調査"
        )


        race_clickables = (
            inspect_race_clickables(
                page,
                TARGET_RACE_NO,
            )
        )


        print(
            "4R候補数:",
            len(race_clickables),
        )


        for index, item in enumerate(
            race_clickables[:30],
            start=1,
        ):

            print()

            print(
                f"[4R候補 {index}]"
            )

            print(
                "text:",
                item.get("text"),
            )

            print(
                "href:",
                item.get("href"),
            )

            print(
                "onclick:",
                item.get("onclick"),
            )

            print(
                "title:",
                item.get("title"),
            )

            print(
                "HTML:",
                safe_text(
                    item.get("outerHTML")
                )[:2000],
            )


        race_target = mark_race_button(
            page,
            TARGET_RACE_NO,
        )


        print()

        print(
            "4R選択結果:"
        )


        print(
            json.dumps(
                race_target,
                ensure_ascii=False,
                indent=2,
            )[:20000]
        )


        before_race_url = page.url


        race_click_success = False

        race_click_message = ""


        if race_target.get("found"):

            print()

            print(
                "★ 函館4R候補を発見 ★"
            )


            race_click_success, (
                race_click_message
            ) = click_marked_race(
                page
            )

        else:

            print()

            print(
                "函館4R候補を"
                "発見できませんでした"
            )


        print()

        print(
            "4Rクリック結果:",
            race_click_success,
        )

        print(
            "4Rクリックメッセージ:",
            race_click_message,
        )


        if race_click_success:

            wait_page(
                page,
                seconds=10,
            )


        after_race_url = page.url


        race_summary = get_page_summary(
            page,
            "race_4",
        )


        race_html = save_page_html(
            page,
            "003_hakodate_4r.html",
        )


        print()

        print("=" * 70)

        print(
            "函館4R 正式遷移確認"
        )

        print("=" * 70)


        print(
            "移動前URL:",
            before_race_url,
        )

        print(
            "移動後URL:",
            after_race_url,
        )

        print(
            "URL変化:",
            (
                before_race_url
                !=
                after_race_url
            ),
        )

        print(
            "title:",
            race_summary["title"],
        )

        print(
            "見出し:",
            race_summary["headings"][:30],
        )

        print()

        print(
            "本文先頭:"
        )

        print(
            race_summary[
                "body_text_head"
            ][:10000]
        )

        print()

        print(
            "HTML:",
            race_html,
        )


        # ====================================================
        # 遅延通信
        # ====================================================

        print()

        print(
            "[5] 遅延通信捕獲 10秒"
        )

        time.sleep(10)


        final_summary = get_page_summary(
            page,
            "final",
        )


        final_html = save_page_html(
            page,
            "004_final.html",
        )


        # ====================================================
        # 集計
        # ====================================================

        jsj_counter = Counter()

        jsj_sources = defaultdict(list)


        for record in network_records:

            values = []

            values.extend(
                record.get(
                    "jsj_types",
                    [],
                )
            )

            values.extend(
                record.get(
                    "jsj_types_url",
                    [],
                )
            )

            for jsj in values:

                jsj_counter[jsj] += 1

                jsj_sources[jsj].append({

                    "source_type":
                        "network",

                    "url":
                        record.get(
                            "url",
                            "",
                        ),

                    "resource_type":
                        record.get(
                            "resource_type",
                            "",
                        ),
                })


        for record in response_body_records:

            for jsj in record.get(
                "jsj_types",
                [],
            ):

                jsj_counter[jsj] += 1

                jsj_sources[jsj].append({

                    "source_type":
                        "response_body",

                    "url":
                        record.get(
                            "url",
                            "",
                        ),

                    "saved_path":
                        record.get(
                            "saved_path",
                            "",
                        ),
                })


        for record in script_records:

            for jsj in record.get(
                "controller_matches",
                [],
            ):

                jsj_counter[jsj] += 1

                jsj_sources[jsj].append({

                    "source_type":
                        "controller_definition",

                    "url":
                        record.get(
                            "url",
                            "",
                        ),

                    "saved_path":
                        record.get(
                            "saved_path",
                            "",
                        ),
                })


        known_top_jsj = {

            "JSJ048",

            "JSJ057",

            "JSJ078",

            "JSJ079",

            "JSJ080",

            "JSJ081",

            "JSJ082",
        }


        detected_jsj = sorted(
            jsj_counter.keys()
        )


        new_jsj_types = sorted(

            set(detected_jsj)

            -

            known_top_jsj
        )


        keyword_bodies = [

            record

            for record
            in response_body_records

            if record.get("keywords")
        ]


        keyword_scripts = [

            record

            for record
            in script_records

            if record.get("keywords")
        ]


        resource_distribution = Counter(

            record.get(
                "resource_type",
                "unknown",
            )

            for record
            in network_records
        )


        result = {

            "program":
                "016_capture_official_syusou_network.py",

            "created_at":
                now_iso(),

            "target": {

                "place":
                    TARGET_PLACE,

                "race_no":
                    TARGET_RACE_NO,
            },

            "navigation": {

                "before_syusou_url":
                    before_syusou_url,

                "after_syusou_url":
                    after_syusou_url,

                "syusou_click_success":
                    syusou_click_success,

                "syusou_click_message":
                    syusou_click_message,

                "before_race_url":
                    before_race_url,

                "after_race_url":
                    after_race_url,

                "race_click_success":
                    race_click_success,

                "race_click_message":
                    race_click_message,
            },

            "page_summaries": {

                "top":
                    top_summary,

                "syusou":
                    syusou_summary,

                "race":
                    race_summary,

                "final":
                    final_summary,
            },

            "place_dom":
                place_dom,

            "syusou_target":
                syusou_target,

            "race_clickables":
                race_clickables,

            "race_target":
                race_target,

            "counts": {

                "network_records":
                    len(network_records),

                "response_body_records":
                    len(
                        response_body_records
                    ),

                "script_records":
                    len(script_records),

                "keyword_bodies":
                    len(keyword_bodies),

                "keyword_scripts":
                    len(keyword_scripts),

                "errors":
                    len(errors),
            },

            "resource_type_distribution":
                dict(
                    resource_distribution
                ),

            "jsj_type_distribution":
                dict(
                    sorted(
                        jsj_counter.items()
                    )
                ),

            "detected_jsj_types":
                detected_jsj,

            "new_jsj_types":
                new_jsj_types,

            "jsj_sources":
                dict(jsj_sources),

            "keyword_bodies":
                keyword_bodies,

            "keyword_scripts":
                keyword_scripts,

            "network_records":
                network_records,

            "response_body_records":
                response_body_records,

            "script_records":
                script_records,

            "errors":
                errors,
        }


        save_json(
            RESULT_JSON,
            result,
        )


        # ====================================================
        # 最終表示
        # ====================================================

        print()

        print("=" * 70)

        print(
            "016 修正版 最終結果"
        )

        print("=" * 70)


        print()

        print(
            "函館出走表一覧クリック成功:",
            syusou_click_success,
        )

        print(
            "出走表URL変化:",
            (
                before_syusou_url
                !=
                after_syusou_url
            ),
        )


        print()

        print(
            "函館4Rクリック成功:",
            race_click_success,
        )

        print(
            "4R URL変化:",
            (
                before_race_url
                !=
                after_race_url
            ),
        )


        print()

        print(
            "最終URL:",
            final_summary["url"],
        )

        print(
            "最終title:",
            final_summary["title"],
        )


        print()

        print(
            "通信レコード数:",
            len(network_records),
        )

        print(
            "BODY保存数:",
            len(response_body_records),
        )

        print(
            "SCRIPT保存数:",
            len(script_records),
        )

        print(
            "通信エラー数:",
            len(errors),
        )


        print()

        print(
            "resource type分布:"
        )

        print(
            dict(
                resource_distribution
            )
        )


        print()

        print(
            "全JSJ TYPE:"
        )

        print(
            detected_jsj
        )


        print()

        print(
            "JSJ TYPE分布:"
        )

        print(
            dict(
                sorted(
                    jsj_counter.items()
                )
            )
        )


        print()

        print(
            "★ TOP既知TYPE以外の"
            "新JSJ TYPE ★"
        )


        if new_jsj_types:

            for jsj in new_jsj_types:

                print()

                print(
                    "NEW:",
                    jsj,
                )

                for source in (
                    jsj_sources.get(
                        jsj,
                        [],
                    )[:20]
                ):

                    print(
                        "  ",
                        source,
                    )

        else:

            print(
                "新JSJ TYPEなし"
            )


        print()

        print(
            "★ ライン・並び候補BODY ★"
        )


        if keyword_bodies:

            for record in keyword_bodies:

                important_keywords = [

                    keyword

                    for keyword
                    in record["keywords"]

                    if keyword in {
                        "ライン",
                        "並び",
                        "並び予想",
                        "周回",
                        "想定",
                        "先頭",
                        "番手",
                        "三番手",
                        "単騎",
                        "narabi",
                        "syukai",
                        "shukai",
                        "bante",
                        "sentou",
                        "tanki",
                    }
                ]


                if not important_keywords:

                    continue


                print()

                print(
                    "BODY:",
                    record["body_no"],
                )

                print(
                    "TYPE:",
                    record["resource_type"],
                )

                print(
                    "URL:",
                    record["url"],
                )

                print(
                    "JSJ:",
                    record["jsj_types"],
                )

                print(
                    "KEYWORDS:",
                    record["keywords"],
                )

                print(
                    "PATH:",
                    record["saved_path"],
                )


        print()

        print(
            "★ ライン・並び候補SCRIPT ★"
        )


        if keyword_scripts:

            for record in keyword_scripts:

                important_keywords = [

                    keyword

                    for keyword
                    in record["keywords"]

                    if keyword in {
                        "ライン",
                        "並び",
                        "並び予想",
                        "周回",
                        "想定",
                        "先頭",
                        "番手",
                        "三番手",
                        "単騎",
                        "narabi",
                        "syukai",
                        "shukai",
                        "bante",
                        "sentou",
                        "tanki",
                    }
                ]


                if not important_keywords:

                    continue


                print()

                print(
                    "URL:",
                    record["url"],
                )

                print(
                    "JSJ:",
                    record["jsj_types"],
                )

                print(
                    "Controller:",
                    record[
                        "controller_matches"
                    ],
                )

                print(
                    "KEYWORDS:",
                    record["keywords"],
                )

                print(
                    "PATH:",
                    record["saved_path"],
                )


        print()

        print(
            "保存先:"
        )

        print(
            RESULT_JSON
        )


        print()

        print(
            "=== 016 修正版 完了 ==="
        )


if __name__ == "__main__":

    main()