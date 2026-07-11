from pathlib import Path
from collections import Counter, defaultdict
import json
import re


# ============================================================
# 017
# 016保存データからライン・並び情報取得元を特定
#
# 対象:
#   016_official_syusou_analysis.json
#   response_bodies
#   scripts
#
# 目的:
#   ・並び / 並び予想 / narabi 周辺コード抽出
#   ・JSJ TYPEとの対応確認
#   ・XHR実通信のJSJ TYPE抽出
#   ・request post_data確認
#   ・ライン描画変数名候補抽出
# ============================================================


BASE = Path(r"C:\競輪AI")

CAPTURE_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "016_official_syusou_capture"
)

ANALYSIS_JSON = (
    CAPTURE_DIR
    / "016_official_syusou_analysis.json"
)

SCRIPT_DIR = (
    CAPTURE_DIR
    / "scripts"
)

BODY_DIR = (
    CAPTURE_DIR
    / "response_bodies"
)

OUT_JSON = (
    CAPTURE_DIR
    / "017_line_source_analysis.json"
)


IMPORTANT_FILES = [
    "PJ0305_v.js",
    "PJ0305_c.js",
    "commonLive.js",
    "FPJ0315.js",
    "commonRace.js",
    "PC0201_v.js",
    "PC0201_c.js",
]


KEYWORDS = [
    "並び予想",
    "並び",
    "ライン",
    "周回",
    "先頭",
    "番手",
    "三番手",
    "単騎",
    "narabi",
    "nara",
    "syukai",
    "shukai",
    "bante",
    "sentou",
    "tanki",
]


JSJ_PATTERN = re.compile(
    r"\bJSJ\d{3}\b",
    re.IGNORECASE,
)


IDENTIFIER_PATTERN = re.compile(
    r"\b[A-Za-z_$][A-Za-z0-9_$]{2,80}\b"
)


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


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


def read_text(path):

    try:

        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    except Exception:

        return ""


def extract_jsj(text):

    if not text:
        return []

    return sorted(
        {
            value.upper()
            for value
            in JSJ_PATTERN.findall(text)
        }
    )


def find_keyword_positions(
    text,
    keyword,
):

    result = []

    lower_text = text.lower()

    lower_keyword = keyword.lower()

    start = 0

    while True:

        position = lower_text.find(
            lower_keyword,
            start,
        )

        if position < 0:
            break

        result.append(position)

        start = (
            position
            + len(lower_keyword)
        )

    return result


def make_context(
    text,
    position,
    keyword,
    radius=800,
):

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

    return text[left:right]


def extract_identifiers(text):

    identifiers = (
        IDENTIFIER_PATTERN.findall(text)
    )

    ignore = {
        "function",
        "return",
        "var",
        "let",
        "const",
        "true",
        "false",
        "null",
        "undefined",
        "document",
        "window",
        "length",
        "html",
        "text",
        "value",
        "class",
        "style",
        "this",
        "else",
        "case",
        "break",
        "continue",
        "for",
        "while",
        "switch",
        "typeof",
        "new",
    }

    result = []

    for value in identifiers:

        if value.lower() in ignore:
            continue

        result.append(value)

    return result


def analyze_file(path):

    text = read_text(path)

    result = {
        "path": str(path),
        "name": path.name,
        "length": len(text),
        "jsj_types": extract_jsj(text),
        "keyword_hits": [],
        "identifier_counter": {},
    }

    identifier_counter = Counter()

    for keyword in KEYWORDS:

        positions = find_keyword_positions(
            text,
            keyword,
        )

        for position in positions:

            context = make_context(
                text,
                position,
                keyword,
            )

            identifiers = extract_identifiers(
                context
            )

            identifier_counter.update(
                identifiers
            )

            result["keyword_hits"].append({
                "keyword": keyword,
                "position": position,
                "context": context,
                "jsj_types_in_context": (
                    extract_jsj(context)
                ),
                "identifiers": (
                    identifiers[:200]
                ),
            })

    result["identifier_counter"] = dict(
        identifier_counter.most_common(100)
    )

    return result


def find_matching_files(
    directory,
    target_name,
):

    result = []

    for path in directory.glob("*"):

        if target_name.lower() in path.name.lower():

            result.append(path)

    return sorted(result)


def analyze_network(data):

    network_records = data.get(
        "network_records",
        [],
    )

    xhr_requests = []

    xhr_responses = []

    jsj_request_counter = Counter()

    jsj_response_counter = Counter()

    post_data_records = []

    for record in network_records:

        resource_type = record.get(
            "resource_type",
            "",
        )

        event = record.get(
            "event",
            "",
        )

        if resource_type not in {
            "xhr",
            "fetch",
        }:
            continue

        url = record.get(
            "url",
            "",
        )

        post_data = record.get(
            "post_data",
            "",
        )

        combined = (
            str(url)
            + " "
            + str(post_data)
        )

        jsj_types = extract_jsj(
            combined
        )

        if event == "request":

            item = {
                "url": url,
                "method": record.get(
                    "method",
                    "",
                ),
                "post_data": post_data,
                "jsj_types": jsj_types,
            }

            xhr_requests.append(item)

            for jsj in jsj_types:

                jsj_request_counter[jsj] += 1

            if post_data:

                post_data_records.append(item)

        elif event == "response":

            item = {
                "url": url,
                "status": record.get(
                    "status",
                    None,
                ),
                "content_type": record.get(
                    "content_type",
                    "",
                ),
                "jsj_types": jsj_types,
            }

            xhr_responses.append(item)

            for jsj in jsj_types:

                jsj_response_counter[jsj] += 1

    return {
        "xhr_request_count": len(
            xhr_requests
        ),
        "xhr_response_count": len(
            xhr_responses
        ),
        "jsj_request_counter": dict(
            sorted(
                jsj_request_counter.items()
            )
        ),
        "jsj_response_counter": dict(
            sorted(
                jsj_response_counter.items()
            )
        ),
        "post_data_records": (
            post_data_records
        ),
        "xhr_requests": xhr_requests,
        "xhr_responses": xhr_responses,
    }


def analyze_response_bodies():

    result = []

    for path in sorted(
        BODY_DIR.glob("*")
    ):

        text = read_text(path)

        if not text:
            continue

        found_keywords = []

        lower_text = text.lower()

        for keyword in KEYWORDS:

            if (
                keyword.lower()
                in lower_text
            ):

                found_keywords.append(
                    keyword
                )

        if not found_keywords:
            continue

        result.append({
            "path": str(path),
            "name": path.name,
            "length": len(text),
            "jsj_types": extract_jsj(
                text
            ),
            "keywords": found_keywords,
        })

    return result


def main():

    print(
        "=== 017 ライン・並び取得元解析 ==="
    )

    print()

    print(
        "016解析JSON:"
    )

    print(
        ANALYSIS_JSON
    )

    if not ANALYSIS_JSON.exists():

        print()

        print(
            "ERROR:"
            " 016解析JSONがありません"
        )

        return

    data = load_json(
        ANALYSIS_JSON
    )

    print()

    print(
        "[1] 重要JavaScript解析"
    )

    file_analyses = []

    for target_name in IMPORTANT_FILES:

        print()

        print(
            "=" * 70
        )

        print(
            "TARGET:",
            target_name,
        )

        print(
            "=" * 70
        )

        matched_files = (
            find_matching_files(
                SCRIPT_DIR,
                target_name,
            )
        )

        print(
            "一致ファイル数:",
            len(matched_files),
        )

        for path in matched_files:

            analysis = analyze_file(
                path
            )

            file_analyses.append(
                analysis
            )

            print()

            print(
                "FILE:",
                path
            )

            print(
                "JSJ:",
                analysis["jsj_types"],
            )

            print(
                "キーワードHIT数:",
                len(
                    analysis[
                        "keyword_hits"
                    ]
                ),
            )

            for hit in (
                analysis["keyword_hits"][:30]
            ):

                print()

                print(
                    "--------------------------------"
                )

                print(
                    "KEYWORD:",
                    hit["keyword"],
                )

                print(
                    "POSITION:",
                    hit["position"],
                )

                print(
                    "JSJ IN CONTEXT:",
                    hit[
                        "jsj_types_in_context"
                    ],
                )

                print()

                print(
                    hit["context"]
                )

                print(
                    "--------------------------------"
                )


    print()

    print(
        "[2] XHR / fetch実通信解析"
    )

    network_analysis = (
        analyze_network(data)
    )

    print()

    print(
        "XHR request数:",
        network_analysis[
            "xhr_request_count"
        ],
    )

    print(
        "XHR response数:",
        network_analysis[
            "xhr_response_count"
        ],
    )

    print()

    print(
        "request JSJ分布:"
    )

    print(
        network_analysis[
            "jsj_request_counter"
        ]
    )

    print()

    print(
        "response JSJ分布:"
    )

    print(
        network_analysis[
            "jsj_response_counter"
        ]
    )


    print()

    print(
        "★ POST DATAありXHR ★"
    )

    post_records = (
        network_analysis[
            "post_data_records"
        ]
    )

    print(
        "件数:",
        len(post_records),
    )

    for index, record in enumerate(
        post_records,
        start=1,
    ):

        print()

        print(
            f"[POST {index}]"
        )

        print(
            "URL:",
            record["url"],
        )

        print(
            "METHOD:",
            record["method"],
        )

        print(
            "JSJ:",
            record["jsj_types"],
        )

        print(
            "POST DATA:"
        )

        print(
            record["post_data"]
        )


    print()

    print(
        "[3] ラインキーワードBODY一覧"
    )

    body_analysis = (
        analyze_response_bodies()
    )

    print()

    print(
        "候補BODY数:",
        len(body_analysis),
    )

    for index, record in enumerate(
        body_analysis,
        start=1,
    ):

        print()

        print(
            f"[BODY {index}]"
        )

        print(
            "FILE:",
            record["name"],
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
            record["path"],
        )


    print()

    print(
        "[4] キーワード周辺変数名ランキング"
    )

    global_identifier_counter = Counter()

    keyword_jsj_map = defaultdict(
        Counter
    )

    for analysis in file_analyses:

        global_identifier_counter.update(
            analysis[
                "identifier_counter"
            ]
        )

        for hit in analysis[
            "keyword_hits"
        ]:

            keyword = hit[
                "keyword"
            ]

            for jsj in hit[
                "jsj_types_in_context"
            ]:

                keyword_jsj_map[
                    keyword
                ][jsj] += 1


    print()

    print(
        "★ 周辺変数名 TOP100 ★"
    )

    for name, count in (
        global_identifier_counter
        .most_common(100)
    ):

        print(
            f"{count:5d}  {name}"
        )


    print()

    print(
        "★ キーワード → JSJ対応候補 ★"
    )

    keyword_jsj_output = {}

    for keyword in KEYWORDS:

        counter = keyword_jsj_map.get(
            keyword,
            Counter(),
        )

        values = dict(
            counter.most_common()
        )

        keyword_jsj_output[
            keyword
        ] = values

        print()

        print(
            keyword,
            "=>",
            values,
        )


    result = {
        "program": (
            "017_analyze_line_sources.py"
        ),
        "important_files": (
            IMPORTANT_FILES
        ),
        "keywords": KEYWORDS,
        "file_analyses": (
            file_analyses
        ),
        "network_analysis": (
            network_analysis
        ),
        "body_analysis": (
            body_analysis
        ),
        "global_identifier_counter": dict(
            global_identifier_counter
            .most_common(200)
        ),
        "keyword_jsj_map": (
            keyword_jsj_output
        ),
    }


    save_json(
        OUT_JSON,
        result,
    )


    print()

    print(
        "=" * 70
    )

    print(
        "017 最終結果"
    )

    print(
        "=" * 70
    )

    print()

    print(
        "重要JS解析数:",
        len(file_analyses),
    )

    print(
        "XHR request数:",
        network_analysis[
            "xhr_request_count"
        ],
    )

    print(
        "POST DATAありXHR:",
        len(post_records),
    )

    print(
        "ライン候補BODY数:",
        len(body_analysis),
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
        "=== 017 完了 ==="
    )


if __name__ == "__main__":

    main()