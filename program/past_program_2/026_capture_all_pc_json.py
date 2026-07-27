from pathlib import Path
from urllib.parse import urlparse, parse_qs
from collections import Counter, defaultdict
import json
import time

from playwright.sync_api import sync_playwright


# ============================================================
# 026
#
# Edgeで開いている全KEIRIN.JPページを監視
#
# 目的:
#   ・racelive固定をやめる
#   ・全KEIRIN.JPページの /pc/json 通信を捕獲
#   ・type=JSJxxx を実通信から一覧化
#   ・JSJ002が発生したページを特定
#   ・JSJ002 response JSONを保存
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "026_all_pc_json_capture"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_JSON = (
    OUT_DIR
    / "026_all_pc_json_capture.json"
)


CDP_URL = "http://127.0.0.1:9222"

TARGET_HOST = "keirin.jp"

TARGET_PATH = "/pc/json"

WATCH_SECONDS = 30


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


def parse_request_type(
    url,
    post_data,
):

    request_types = []


    try:

        parsed = urlparse(url)

        query_params = parse_qs(
            parsed.query
        )


        for value in query_params.get(
            "type",
            [],
        ):

            if value:

                request_types.append(
                    str(value).upper()
                )


    except Exception:

        pass


    if post_data:

        try:

            post_params = parse_qs(
                post_data
            )


            for value in post_params.get(
                "type",
                [],
            ):

                if value:

                    request_types.append(
                        str(value).upper()
                    )


        except Exception:

            pass


    return sorted(
        set(request_types)
    )


def is_target_json_url(url):

    try:

        parsed = urlparse(url)

        host = parsed.netloc.lower()

        path = parsed.path.lower()


        if TARGET_HOST not in host:

            return False


        if path != TARGET_PATH:

            return False


        return True


    except Exception:

        return False


def main():

    print(
        "=== 026 全KEIRIN.JP /pc/json 実通信監視 ==="
    )

    print()


    records = []

    type_counter = Counter()

    type_pages = defaultdict(set)

    attached_pages = []


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


        print()

        print(
            "[2] 全ページ確認"
        )


        for context_index, context in enumerate(
            contexts,
            start=1,
        ):

            pages = context.pages


            print()

            print(
                f"CONTEXT {context_index}"
            )

            print(
                "page数:",
                len(pages),
            )


            for page_index, page in enumerate(
                pages,
                start=1,
            ):

                try:

                    page_url = page.url

                    page_title = safe_title(
                        page
                    )


                    print()

                    print(
                        f"[PAGE "
                        f"{context_index}-"
                        f"{page_index}]"
                    )

                    print(
                        "URL:",
                        page_url,
                    )

                    print(
                        "TITLE:",
                        page_title,
                    )


                    if (
                        TARGET_HOST
                        in page_url.lower()
                    ):

                        attached_pages.append({
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


                except Exception as e:

                    print(
                        "PAGE確認エラー:",
                        repr(e),
                    )


        print()

        print(
            "監視対象KEIRIN.JPページ数:",
            len(attached_pages),
        )


        if not attached_pages:

            print()

            print(
                "ERROR:"
                " KEIRIN.JPページがありません"
            )

            print()

            print(
                "EdgeでKEIRIN.JPを"
                "開いてから再実行してください"
            )

            return


        def create_response_handler(
            page,
            page_info,
        ):

            def on_response(response):

                try:

                    url = response.url


                    if not is_target_json_url(
                        url
                    ):

                        return


                    request = response.request

                    post_data = request.post_data


                    request_types = (
                        parse_request_type(
                            url,
                            post_data,
                        )
                    )


                    current_page_url = page.url

                    current_page_title = (
                        safe_title(page)
                    )


                    record_no = (
                        len(records) + 1
                    )


                    print()

                    print(
                        "=" * 100
                    )

                    print(
                        "★ /pc/json RESPONSE ★"
                    )

                    print(
                        "RECORD:",
                        record_no,
                    )

                    print(
                        "PAGE URL:",
                        current_page_url,
                    )

                    print(
                        "PAGE TITLE:",
                        current_page_title,
                    )

                    print(
                        "REQUEST URL:",
                        url,
                    )

                    print(
                        "METHOD:",
                        request.method,
                    )

                    print(
                        "STATUS:",
                        response.status,
                    )

                    print(
                        "TYPE:",
                        request_types,
                    )

                    print(
                        "POST DATA:",
                        post_data,
                    )


                    parsed = urlparse(url)

                    query_params = parse_qs(
                        parsed.query
                    )


                    print()

                    print(
                        "QUERY PARAMS:"
                    )

                    print(
                        json.dumps(
                            query_params,
                            ensure_ascii=False,
                            indent=2,
                        )
                    )


                    body_text = ""

                    body_json = None


                    try:

                        body_text = (
                            response.text()
                        )

                    except Exception as e:

                        body_text = (
                            "RESPONSE TEXT ERROR: "
                            + repr(e)
                        )


                    try:

                        body_json = (
                            response.json()
                        )

                    except Exception:

                        body_json = None


                    body_path = (
                        OUT_DIR
                        / (
                            f"{record_no:03d}_"
                            f"pc_json_response.txt"
                        )
                    )


                    body_path.write_text(
                        body_text,
                        encoding="utf-8",
                        errors="replace",
                    )


                    json_path = None


                    if body_json is not None:

                        json_path = (
                            OUT_DIR
                            / (
                                f"{record_no:03d}_"
                                f"pc_json_response.json"
                            )
                        )


                        save_json(
                            json_path,
                            body_json,
                        )


                    body_top_keys = []

                    race_info_count = None

                    narabiyoso_summary = []


                    if isinstance(
                        body_json,
                        dict,
                    ):

                        body_top_keys = list(
                            body_json.keys()
                        )


                        race_info = body_json.get(
                            "raceInfo"
                        )


                        if isinstance(
                            race_info,
                            list,
                        ):

                            race_info_count = len(
                                race_info
                            )


                            for race in race_info:

                                if not isinstance(
                                    race,
                                    dict,
                                ):

                                    continue


                                main_data = race.get(
                                    "PJ0314MainData"
                                )


                                narabiyoso = None


                                if isinstance(
                                    main_data,
                                    dict,
                                ):

                                    narabiyoso = (
                                        main_data.get(
                                            "narabiyoso"
                                        )
                                    )


                                narabiyoso_summary.append({
                                    "raceNo": (
                                        race.get(
                                            "raceNo"
                                        )
                                    ),
                                    "has_PJ0314MainData": (
                                        isinstance(
                                            main_data,
                                            dict,
                                        )
                                    ),
                                    "narabiyoso": (
                                        narabiyoso
                                    ),
                                })


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
                            request.resource_type
                        ),
                        "status": response.status,
                        "post_data": post_data,
                        "request_types": (
                            request_types
                        ),
                        "query_params": (
                            query_params
                        ),
                        "body_path": str(
                            body_path
                        ),
                        "json_path": (
                            str(json_path)
                            if json_path
                            else None
                        ),
                        "body_length": len(
                            body_text
                        ),
                        "body_top_keys": (
                            body_top_keys
                        ),
                        "raceInfo_count": (
                            race_info_count
                        ),
                        "narabiyoso_summary": (
                            narabiyoso_summary
                        ),
                    }


                    records.append(
                        record
                    )


                    for request_type in (
                        request_types
                    ):

                        type_counter[
                            request_type
                        ] += 1


                        type_pages[
                            request_type
                        ].add(
                            current_page_url
                        )


                    save_json(
                        OUT_JSON,
                        {
                            "program": (
                                "026_capture_all_pc_json.py"
                            ),
                            "records": records,
                        },
                    )


                    if "JSJ002" in request_types:

                        print()

                        print(
                            "🔥🔥🔥"
                            " JSJ002 CAPTURED "
                            "🔥🔥🔥"
                        )

                        print()

                        print(
                            "raceInfo_count:",
                            race_info_count,
                        )

                        print()

                        print(
                            "narabiyoso SUMMARY:"
                        )

                        print(
                            json.dumps(
                                narabiyoso_summary,
                                ensure_ascii=False,
                                indent=2,
                            )
                        )


                    print()

                    print(
                        "BODY保存:",
                        body_path,
                    )


                    if json_path:

                        print(
                            "JSON保存:",
                            json_path,
                        )


                    print(
                        "=" * 100
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
            "[3] 全KEIRIN.JPページへ"
            " response監視登録"
        )


        for page_info in attached_pages:

            page = page_info["page"]


            handler = create_response_handler(
                page,
                page_info,
            )


            page.on(
                "response",
                handler,
            )


            print(
                "監視登録:",
                page_info[
                    "initial_url"
                ],
            )


        print()

        print(
            "[4] 全対象ページをリロード"
        )


        for page_info in attached_pages:

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
            "[5] 通信監視 30秒"
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
            "026 最終結果"
        )

        print(
            "=" * 100
        )


        print()

        print(
            "/pc/json HIT:",
            len(records),
        )


        print()

        print(
            "★ TYPE一覧 ★"
        )


        if type_counter:

            for request_type, count in (
                type_counter.most_common()
            ):

                print(
                    f"{count:4d}  "
                    f"{request_type}"
                )


        else:

            print(
                "TYPEなし"
            )


        print()

        print(
            "★ TYPE → PAGE一覧 ★"
        )


        for request_type in sorted(
            type_pages.keys()
        ):

            print()

            print(
                request_type
            )


            for page_url in sorted(
                type_pages[
                    request_type
                ]
            ):

                print(
                    "  ",
                    page_url,
                )


        jsj002_records = [
            record
            for record in records
            if "JSJ002"
            in record["request_types"]
        ]


        print()

        print(
            "★ JSJ002 HIT:",
            len(jsj002_records),
        )


        if jsj002_records:

            for record in jsj002_records:

                print()

                print(
                    "-" * 100
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
                    record[
                        "request_url"
                    ]
                )

                print()

                print(
                    "QUERY PARAMS:"
                )

                print(
                    json.dumps(
                        record[
                            "query_params"
                        ],
                        ensure_ascii=False,
                        indent=2,
                    )
                )

                print()

                print(
                    "raceInfo_count:",
                    record[
                        "raceInfo_count"
                    ],
                )

                print()

                print(
                    "narabiyoso SUMMARY:"
                )

                print(
                    json.dumps(
                        record[
                            "narabiyoso_summary"
                        ],
                        ensure_ascii=False,
                        indent=2,
                    )
                )


        print()

        print(
            "保存先:"
        )

        print(
            OUT_JSON
        )


        save_json(
            OUT_JSON,
            {
                "program": (
                    "026_capture_all_pc_json.py"
                ),
                "watch_seconds": (
                    WATCH_SECONDS
                ),
                "record_count": len(
                    records
                ),
                "type_counter": dict(
                    type_counter
                ),
                "type_pages": {
                    key: sorted(value)
                    for key, value
                    in type_pages.items()
                },
                "jsj002_count": len(
                    jsj002_records
                ),
                "records": records,
            },
        )


        print()

        print(
            "=== 026 完了 ==="
        )


if __name__ == "__main__":

    main()