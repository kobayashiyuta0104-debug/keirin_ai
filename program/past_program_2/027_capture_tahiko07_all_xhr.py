from pathlib import Path
from urllib.parse import urlparse, parse_qs
import json
import time

from playwright.sync_api import sync_playwright


# ============================================================
# 027
#
# 弥彦7R 確定前
# 全XHR / fetch レスポンス狙い撃ち捕獲
#
# 目的:
#   ・/pc/json 固定をやめる
#   ・JSJ002文字列固定をやめる
#   ・全XHR / fetchを保存
#   ・JSON本文を再帰探索
#   ・raceInfo を探す
#   ・PJ0314MainData を探す
#   ・narabiyoso を探す
#
# Edge:
#   remote debugging port 9222
#
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "027_yahiko7_all_xhr"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_JSON = (
    OUT_DIR
    / "027_yahiko7_all_xhr.json"
)


CDP_URL = "http://127.0.0.1:9222"

WATCH_SECONDS = 30


TARGET_KEYS = [
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
                        "target_key": (
                            target_key
                        ),
                        "actual_key": key,
                        "location": (
                            current_location
                        ),
                        "value": value,
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


def main():

    print(
        "=== 027 弥彦7R 全XHR/fetch捕獲 ==="
    )

    print()

    records = []

    important_records = []


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


        target_page = None


        print()

        print(
            "[2] KEIRIN.JPページ確認"
        )


        for context_index, context in enumerate(
            contexts,
            start=1,
        ):

            pages = context.pages


            for page_index, page in enumerate(
                pages,
                start=1,
            ):

                try:

                    url = page.url

                    title = safe_title(
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
                        url,
                    )

                    print(
                        "TITLE:",
                        title,
                    )


                    if (
                        "keirin.jp"
                        in url.lower()
                    ):

                        target_page = page


                except Exception as e:

                    print(
                        "PAGE確認エラー:",
                        repr(e),
                    )


        if target_page is None:

            print()

            print(
                "ERROR:"
                " KEIRIN.JPページがありません"
            )

            print()

            print(
                "Edgeで弥彦7Rを"
                "表示してから再実行してください"
            )

            return


        print()

        print(
            "[3] 対象ページ"
        )

        print(
            "URL:",
            target_page.url,
        )

        print(
            "TITLE:",
            safe_title(
                target_page
            ),
        )


        def on_response(response):

            try:

                request = response.request


                if request.resource_type not in {
                    "xhr",
                    "fetch",
                }:

                    return


                url = response.url

                record_no = len(records) + 1


                print()

                print(
                    "-" * 100
                )

                print(
                    f"XHR/FETCH {record_no}"
                )

                print(
                    "URL:",
                    url,
                )

                print(
                    "METHOD:",
                    request.method,
                )

                print(
                    "TYPE:",
                    request.resource_type,
                )

                print(
                    "STATUS:",
                    response.status,
                )


                post_data = request.post_data


                if post_data:

                    print(
                        "POST DATA:",
                        post_data,
                    )


                parsed = urlparse(url)


                query_params = {}


                try:

                    query_params = parse_qs(
                        parsed.query
                    )

                except Exception:

                    pass


                body_text = ""


                try:

                    body_text = response.text()

                except Exception as e:

                    body_text = (
                        "RESPONSE TEXT ERROR: "
                        + repr(e)
                    )


                body_json = None


                try:

                    body_json = json.loads(
                        body_text
                    )

                except Exception:

                    body_json = None


                body_path = (
                    OUT_DIR
                    / (
                        f"{record_no:03d}_"
                        f"response.txt"
                    )
                )


                body_path.write_text(
                    body_text,
                    encoding="utf-8",
                    errors="replace",
                )


                json_path = None

                key_hits = []


                if body_json is not None:

                    json_path = (
                        OUT_DIR
                        / (
                            f"{record_no:03d}_"
                            f"response.json"
                        )
                    )


                    save_json(
                        json_path,
                        body_json,
                    )


                    key_hits = find_keys_recursive(
                        body_json,
                        TARGET_KEYS,
                    )


                record = {
                    "record_no": record_no,
                    "page_url": (
                        target_page.url
                    ),
                    "page_title": (
                        safe_title(
                            target_page
                        )
                    ),
                    "request_url": url,
                    "method": request.method,
                    "resource_type": (
                        request.resource_type
                    ),
                    "status": response.status,
                    "post_data": post_data,
                    "query_params": (
                        query_params
                    ),
                    "body_length": len(
                        body_text
                    ),
                    "body_json": (
                        body_json is not None
                    ),
                    "body_path": str(
                        body_path
                    ),
                    "json_path": (
                        str(json_path)
                        if json_path
                        else None
                    ),
                    "key_hits": key_hits,
                }


                records.append(
                    record
                )


                if key_hits:

                    important_records.append(
                        record
                    )


                    print()

                    print(
                        "🔥🔥🔥"
                        " TARGET KEY HIT "
                        "🔥🔥🔥"
                    )


                    for hit in key_hits:

                        print()

                        print(
                            "TARGET:",
                            hit["target_key"],
                        )

                        print(
                            "ACTUAL KEY:",
                            hit["actual_key"],
                        )

                        print(
                            "LOCATION:",
                            hit["location"],
                        )

                        print(
                            "VALUE:"
                        )

                        print(
                            json.dumps(
                                hit["value"],
                                ensure_ascii=False,
                                indent=2,
                            )
                        )


                save_json(
                    OUT_JSON,
                    {
                        "program": (
                            "027_capture_yahiko7_all_xhr.py"
                        ),
                        "records": records,
                        "important_records": (
                            important_records
                        ),
                    },
                )


                print(
                    "-" * 100
                )


            except Exception as e:

                print()

                print(
                    "response処理エラー:",
                    repr(e),
                )


        target_page.on(
            "response",
            on_response,
        )


        print()

        print(
            "[4] 全XHR/fetch監視開始"
        )

        print()

        print(
            "弥彦7Rページをリロードします"
        )


        try:

            target_page.reload(
                wait_until="domcontentloaded",
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
            "027 最終結果"
        )

        print(
            "=" * 100
        )

        print()

        print(
            "XHR/fetch HIT:",
            len(records),
        )

        print(
            "TARGET KEY HIT通信:",
            len(important_records),
        )


        print()

        print(
            "★ TARGET KEY HIT一覧 ★"
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
                    "REQUEST URL:"
                )

                print(
                    record["request_url"]
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


        else:

            print(
                "raceInfo / "
                "PJ0314MainData / "
                "narabiyoso は"
                "捕獲されませんでした"
            )


        save_json(
            OUT_JSON,
            {
                "program": (
                    "027_capture_yahiko7_all_xhr.py"
                ),
                "watch_seconds": (
                    WATCH_SECONDS
                ),
                "record_count": len(
                    records
                ),
                "important_record_count": (
                    len(important_records)
                ),
                "records": records,
                "important_records": (
                    important_records
                ),
            },
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
            "=== 027 完了 ==="
        )


if __name__ == "__main__":

    main()