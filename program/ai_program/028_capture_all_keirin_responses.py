from pathlib import Path
from urllib.parse import urlparse, parse_qs
from collections import Counter
import json
import time

from playwright.sync_api import sync_playwright


# ============================================================
# 028
#
# 全KEIRIN.JPページ
# 全resource type response監視
#
# 目的:
#   ・特定ページ選択をやめる
#   ・全KEIRIN.JPページを同時監視
#   ・xhr / fetch 制限を外す
#   ・全responseを記録
#   ・URL / POST DATA / BODYからJSJ002探索
#   ・JSON本文から
#       raceInfo
#       PJ0314MainData
#       narabiyoso
#     を再帰探索
#   ・iframe一覧も確認
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "028_all_keirin_responses"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_JSON = (
    OUT_DIR
    / "028_all_keirin_responses.json"
)


CDP_URL = "http://127.0.0.1:9222"

WATCH_SECONDS = 30


TARGET_KEYS = [
    "raceInfo",
    "PJ0314MainData",
    "narabiyoso",
]


TARGET_WORDS = [
    "JSJ002",
    "raceInfo",
    "PJ0314MainData",
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


def safe_page_url(page):

    try:

        return page.url

    except Exception:

        return ""


def find_keys_recursive(
    obj,
    target_keys,
    location="root",
):

    results = []


    if isinstance(obj, dict):

        for key, value in obj.items():

            current_location = (
                f"{location}.{key}"
            )


            for target_key in target_keys:

                if (
                    str(key).lower()
                    == target_key.lower()
                ):

                    results.append({
                        "target_key": target_key,
                        "actual_key": str(key),
                        "location": current_location,
                    })


            results.extend(
                find_keys_recursive(
                    value,
                    target_keys,
                    current_location,
                )
            )


    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            current_location = (
                f"{location}[{index}]"
            )


            results.extend(
                find_keys_recursive(
                    value,
                    target_keys,
                    current_location,
                )
            )


    return results


def find_words(
    url,
    post_data,
    body_text,
):

    results = []


    sources = {
        "url": url or "",
        "post_data": post_data or "",
        "body": body_text or "",
    }


    for word in TARGET_WORDS:

        lower_word = word.lower()


        for source_name, text in sources.items():

            if lower_word in text.lower():

                results.append({
                    "word": word,
                    "source": source_name,
                })


    return results


def parse_query(url):

    try:

        parsed = urlparse(url)

        return parse_qs(
            parsed.query
        )

    except Exception:

        return {}


def main():

    print(
        "=== 028 全KEIRIN.JP 全response監視 ==="
    )

    print()


    records = []

    important_records = []

    resource_counter = Counter()

    monitored_pages = []


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
                "ERROR: Edge contextなし"
            )

            return


        print()

        print(
            "[2] 全ページ・iframe確認"
        )


        for context_index, context in enumerate(
            contexts,
            start=1,
        ):

            for page_index, page in enumerate(
                context.pages,
                start=1,
            ):

                page_url = safe_page_url(
                    page
                )

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


                for frame_index, frame in enumerate(
                    page.frames,
                    start=1,
                ):

                    try:

                        print()

                        print(
                            f"  FRAME {frame_index}"
                        )

                        print(
                            "  NAME:",
                            frame.name,
                        )

                        print(
                            "  URL:",
                            frame.url,
                        )

                    except Exception as e:

                        print(
                            "  FRAME ERROR:",
                            repr(e),
                        )


                if (
                    "keirin.jp"
                    in page_url.lower()
                ):

                    monitored_pages.append({
                        "context_index": (
                            context_index
                        ),
                        "page_index": (
                            page_index
                        ),
                        "page": page,
                        "initial_url": (
                            page_url
                        ),
                        "initial_title": (
                            page_title
                        ),
                    })


        print()

        print(
            "監視対象KEIRIN.JPページ:",
            len(monitored_pages),
        )


        if not monitored_pages:

            print()

            print(
                "ERROR:"
                " KEIRIN.JPページなし"
            )

            return


        def make_handler(
            page,
            page_info,
        ):

            def on_response(response):

                try:

                    request = response.request

                    url = response.url

                    resource_type = (
                        request.resource_type
                    )

                    resource_counter[
                        resource_type
                    ] += 1


                    post_data = (
                        request.post_data
                    )


                    body_text = ""


                    try:

                        body_text = (
                            response.text()
                        )

                    except Exception:

                        body_text = ""


                    body_json = None


                    try:

                        body_json = json.loads(
                            body_text
                        )

                    except Exception:

                        body_json = None


                    key_hits = []


                    if body_json is not None:

                        key_hits = (
                            find_keys_recursive(
                                body_json,
                                TARGET_KEYS,
                            )
                        )


                    word_hits = find_words(
                        url,
                        post_data,
                        body_text,
                    )


                    record_no = (
                        len(records) + 1
                    )


                    current_page_url = (
                        safe_page_url(page)
                    )

                    current_page_title = (
                        safe_title(page)
                    )


                    record = {
                        "record_no": record_no,
                        "context_index": (
                            page_info[
                                "context_index"
                            ]
                        ),
                        "page_index": (
                            page_info[
                                "page_index"
                            ]
                        ),
                        "initial_page_url": (
                            page_info[
                                "initial_url"
                            ]
                        ),
                        "initial_page_title": (
                            page_info[
                                "initial_title"
                            ]
                        ),
                        "current_page_url": (
                            current_page_url
                        ),
                        "current_page_title": (
                            current_page_title
                        ),
                        "request_url": url,
                        "method": request.method,
                        "resource_type": (
                            resource_type
                        ),
                        "status": response.status,
                        "post_data": post_data,
                        "query_params": (
                            parse_query(url)
                        ),
                        "body_length": len(
                            body_text
                        ),
                        "body_is_json": (
                            body_json is not None
                        ),
                        "key_hits": key_hits,
                        "word_hits": word_hits,
                    }


                    records.append(
                        record
                    )


                    if key_hits or word_hits:

                        important_records.append(
                            record
                        )


                        print()

                        print(
                            "🔥" * 30
                        )

                        print(
                            "★ IMPORTANT RESPONSE ★"
                        )

                        print(
                            "RECORD:",
                            record_no,
                        )

                        print(
                            "PAGE:"
                        )

                        print(
                            current_page_url
                        )

                        print()

                        print(
                            "REQUEST:"
                        )

                        print(
                            url
                        )

                        print(
                            "METHOD:",
                            request.method,
                        )

                        print(
                            "RESOURCE TYPE:",
                            resource_type,
                        )

                        print(
                            "STATUS:",
                            response.status,
                        )

                        print(
                            "POST DATA:",
                            post_data,
                        )

                        print()

                        print(
                            "QUERY PARAMS:"
                        )

                        print(
                            json.dumps(
                                parse_query(url),
                                ensure_ascii=False,
                                indent=2,
                            )
                        )

                        print()

                        print(
                            "KEY HITS:"
                        )

                        print(
                            json.dumps(
                                key_hits,
                                ensure_ascii=False,
                                indent=2,
                            )
                        )

                        print()

                        print(
                            "WORD HITS:"
                        )

                        print(
                            json.dumps(
                                word_hits,
                                ensure_ascii=False,
                                indent=2,
                            )
                        )


                        important_no = len(
                            important_records
                        )


                        important_body_path = (
                            OUT_DIR
                            / (
                                f"important_"
                                f"{important_no:03d}_"
                                f"body.txt"
                            )
                        )


                        important_body_path.write_text(
                            body_text,
                            encoding="utf-8",
                            errors="replace",
                        )


                        if body_json is not None:

                            important_json_path = (
                                OUT_DIR
                                / (
                                    f"important_"
                                    f"{important_no:03d}_"
                                    f"body.json"
                                )
                            )


                            save_json(
                                important_json_path,
                                body_json,
                            )


                        print()

                        print(
                            "BODY保存:"
                        )

                        print(
                            important_body_path
                        )

                        print(
                            "🔥" * 30
                        )


                except Exception as e:

                    print()

                    print(
                        "response処理エラー:",
                        repr(e),
                    )


            return on_response


        print()

        print(
            "[3] 全KEIRIN.JPページ監視登録"
        )


        for page_info in monitored_pages:

            page = page_info["page"]

            handler = make_handler(
                page,
                page_info,
            )


            page.on(
                "response",
                handler,
            )


            print()

            print(
                "MONITOR:"
            )

            print(
                page_info["initial_url"]
            )


        print()

        print(
            "[4] 全監視ページリロード"
        )


        for page_info in monitored_pages:

            page = page_info["page"]


            try:

                print()

                print(
                    "RELOAD:"
                )

                print(
                    page.url
                )


                page.reload(
                    wait_until=(
                        "domcontentloaded"
                    ),
                    timeout=120000,
                )


            except Exception as e:

                print(
                    "reload例外:",
                    repr(e),
                )


        print()

        print(
            "[5] 30秒監視"
        )


        for second in range(
            1,
            WATCH_SECONDS + 1,
        ):

            print(
                f"{second}/"
                f"{WATCH_SECONDS}秒"
            )

            time.sleep(1)


        print()

        print(
            "=" * 100
        )

        print(
            "028 最終結果"
        )

        print(
            "=" * 100
        )

        print()

        print(
            "全response HIT:",
            len(records),
        )

        print(
            "IMPORTANT RESPONSE:",
            len(important_records),
        )


        print()

        print(
            "★ RESOURCE TYPE一覧 ★"
        )


        if resource_counter:

            for resource_type, count in (
                resource_counter.most_common()
            ):

                print(
                    f"{count:5d}  "
                    f"{resource_type}"
                )

        else:

            print(
                "responseなし"
            )


        print()

        print(
            "★ IMPORTANT一覧 ★"
        )


        if important_records:

            for record in important_records:

                print()

                print(
                    "-" * 100
                )

                print(
                    "RECORD:",
                    record["record_no"],
                )

                print(
                    "PAGE:"
                )

                print(
                    record[
                        "current_page_url"
                    ]
                )

                print()

                print(
                    "REQUEST:"
                )

                print(
                    record["request_url"]
                )

                print(
                    "RESOURCE TYPE:",
                    record[
                        "resource_type"
                    ],
                )

                print()

                print(
                    "KEY HITS:"
                )

                for hit in record[
                    "key_hits"
                ]:

                    print(
                        " ",
                        hit["target_key"],
                        "=>",
                        hit["location"],
                    )


                print()

                print(
                    "WORD HITS:"
                )

                for hit in record[
                    "word_hits"
                ]:

                    print(
                        " ",
                        hit["word"],
                        "=>",
                        hit["source"],
                    )


        else:

            print(
                "JSJ002 / raceInfo / "
                "PJ0314MainData / "
                "narabiyoso HITなし"
            )


        final_data = {
            "program": (
                "028_capture_all_keirin_responses.py"
            ),
            "watch_seconds": (
                WATCH_SECONDS
            ),
            "monitored_pages": [
                {
                    "context_index": item[
                        "context_index"
                    ],
                    "page_index": item[
                        "page_index"
                    ],
                    "initial_url": item[
                        "initial_url"
                    ],
                    "initial_title": item[
                        "initial_title"
                    ],
                }
                for item in monitored_pages
            ],
            "record_count": len(
                records
            ),
            "important_record_count": len(
                important_records
            ),
            "resource_counter": dict(
                resource_counter
            ),
            "important_records": (
                important_records
            ),
            "records": records,
        }


        save_json(
            OUT_JSON,
            final_data,
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
            "=== 028 完了 ==="
        )


if __name__ == "__main__":

    main()