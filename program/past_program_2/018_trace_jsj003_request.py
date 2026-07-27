from pathlib import Path
import json
import re
from collections import Counter


BASE = Path(r"C:\競輪AI")

CAPTURE_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "016_official_syusou_capture"
)

SCRIPT_DIR = CAPTURE_DIR / "scripts"
BODY_DIR = CAPTURE_DIR / "response_bodies"

ANALYSIS_016 = (
    CAPTURE_DIR
    / "016_official_syusou_analysis.json"
)

OUT_JSON = (
    CAPTURE_DIR
    / "018_jsj003_request_trace.json"
)


SEARCH_WORDS = [
    "getRequestGet",
    "Com.getRequestGet",
    "JSJ003",
    "PJ0314MainData",
    "narabiyoso",
    "stCreateList",
    "JSON_REQ_ID",
]


def read_text(path):

    try:

        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    except Exception:

        return ""


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


def find_all_positions(
    text,
    word,
):

    result = []

    start = 0

    lower_text = text.lower()
    lower_word = word.lower()

    while True:

        pos = lower_text.find(
            lower_word,
            start,
        )

        if pos < 0:
            break

        result.append(pos)

        start = pos + len(lower_word)

    return result


def context(
    text,
    pos,
    word,
    radius=2500,
):

    left = max(
        0,
        pos - radius,
    )

    right = min(
        len(text),
        pos + len(word) + radius,
    )

    return text[left:right]


def search_files():

    results = []

    all_files = []

    all_files.extend(
        SCRIPT_DIR.glob("*")
    )

    all_files.extend(
        BODY_DIR.glob("*")
    )

    seen = set()

    for path in all_files:

        path_key = str(path).lower()

        if path_key in seen:
            continue

        seen.add(path_key)

        text = read_text(path)

        if not text:
            continue

        hits = []

        for word in SEARCH_WORDS:

            positions = find_all_positions(
                text,
                word,
            )

            for pos in positions:

                hits.append({
                    "word": word,
                    "position": pos,
                    "context": context(
                        text,
                        pos,
                        word,
                    ),
                })

        if hits:

            results.append({
                "path": str(path),
                "name": path.name,
                "length": len(text),
                "hits": hits,
            })

    return results


def extract_network():

    data = load_json(
        ANALYSIS_016
    )

    records = data.get(
        "network_records",
        [],
    )

    requests = []
    responses = []

    for record in records:

        resource_type = record.get(
            "resource_type",
            "",
        )

        if resource_type not in {
            "xhr",
            "fetch",
        }:
            continue

        event = record.get(
            "event",
            "",
        )

        if event == "request":

            requests.append({
                "url": record.get(
                    "url",
                    "",
                ),
                "method": record.get(
                    "method",
                    "",
                ),
                "post_data": record.get(
                    "post_data",
                    "",
                ),
                "headers": record.get(
                    "headers",
                    {},
                ),
            })

        elif event == "response":

            responses.append({
                "url": record.get(
                    "url",
                    "",
                ),
                "status": record.get(
                    "status",
                    None,
                ),
                "content_type": record.get(
                    "content_type",
                    "",
                ),
                "headers": record.get(
                    "headers",
                    {},
                ),
            })

    return requests, responses


def analyze_urls(requests):

    url_counter = Counter()

    path_counter = Counter()

    query_key_counter = Counter()

    analyzed = []

    for record in requests:

        url = record["url"]

        url_counter[url] += 1

        match = re.match(
            r"https?://[^/]+([^?]*)",
            url,
        )

        if match:

            path_counter[
                match.group(1)
            ] += 1

        query_keys = re.findall(
            r"[?&]([^=&]+)=",
            url,
        )

        for key in query_keys:

            query_key_counter[
                key
            ] += 1

        analyzed.append({
            "url": url,
            "method": record["method"],
            "query_keys": query_keys,
        })

    return {
        "url_counter": dict(
            url_counter.most_common()
        ),
        "path_counter": dict(
            path_counter.most_common()
        ),
        "query_key_counter": dict(
            query_key_counter.most_common()
        ),
        "analyzed": analyzed,
    }


def main():

    print(
        "=== 018 JSJ003通信ルート追跡 ==="
    )

    print()

    print(
        "[1] getRequestGet / JSJ003 定義探索"
    )

    search_results = search_files()

    print()

    print(
        "HITファイル数:",
        len(search_results),
    )

    for file_index, result in enumerate(
        search_results,
        start=1,
    ):

        print()

        print(
            "=" * 70
        )

        print(
            f"[FILE {file_index}]"
        )

        print(
            result["path"]
        )

        print(
            "HIT数:",
            len(result["hits"]),
        )

        for hit_index, hit in enumerate(
            result["hits"],
            start=1,
        ):

            print()

            print(
                "-" * 70
            )

            print(
                f"HIT {hit_index}"
            )

            print(
                "WORD:",
                hit["word"],
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
                "-" * 70
            )


    print()

    print(
        "[2] XHR / fetch URL完全一覧"
    )

    requests, responses = (
        extract_network()
    )

    print()

    print(
        "request数:",
        len(requests),
    )

    for index, record in enumerate(
        requests,
        start=1,
    ):

        print()

        print(
            f"[REQUEST {index}]"
        )

        print(
            "METHOD:",
            record["method"],
        )

        print(
            "URL:",
            record["url"],
        )

        if record["post_data"]:

            print(
                "POST DATA:"
            )

            print(
                record["post_data"]
            )


    print()

    print(
        "[3] URL構造集計"
    )

    url_analysis = analyze_urls(
        requests
    )

    print()

    print(
        "★ PATH分布 ★"
    )

    for path, count in (
        url_analysis[
            "path_counter"
        ].items()
    ):

        print(
            f"{count:4d}  {path}"
        )


    print()

    print(
        "★ QUERY KEY分布 ★"
    )

    for key, count in (
        url_analysis[
            "query_key_counter"
        ].items()
    ):

        print(
            f"{count:4d}  {key}"
        )


    result = {
        "program": (
            "018_trace_jsj003_request.py"
        ),
        "search_words": SEARCH_WORDS,
        "search_results": search_results,
        "requests": requests,
        "responses": responses,
        "url_analysis": url_analysis,
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
        "018 最終結果"
    )

    print(
        "=" * 70
    )

    print()

    print(
        "探索HITファイル:",
        len(search_results),
    )

    print(
        "XHR request:",
        len(requests),
    )

    print(
        "XHR response:",
        len(responses),
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
        "=== 018 完了 ==="
    )


if __name__ == "__main__":

    main()