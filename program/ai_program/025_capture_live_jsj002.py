from pathlib import Path
import json
import time
from urllib.parse import urlparse, parse_qs

from playwright.sync_api import sync_playwright


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "025_live_jsj002_capture"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_JSON = (
    OUT_DIR
    / "025_live_jsj002_capture.json"
)

TARGET_TYPE = "JSJ002"

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


def main():

    print(
        "=== 025 Edge実通信 JSJ002狙い撃ち捕獲 ==="
    )

    print()

    records = []

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

            print(
                "Edge contextがありません"
            )

            return

        context = contexts[0]

        pages = context.pages

        print(
            "page数:",
            len(pages),
        )

        if not pages:

            print(
                "Edge pageがありません"
            )

            return


        page = None


        for index, wk_page in enumerate(
            pages,
            start=1,
        ):

            try:

                print()

                print(
                    f"[PAGE {index}]"
                )

                print(
                    "URL:",
                    wk_page.url,
                )

                print(
                    "TITLE:",
                    wk_page.title(),
                )


                if (
                    "keirin.jp" in wk_page.url.lower()
                    and "racelive" in wk_page.url.lower()
                ):

                    page = wk_page


            except Exception as e:

                print(
                    "PAGE確認エラー:",
                    repr(e),
                )


        if page is None:

            print()

            print(
                "raceliveページが見つかりません"
            )

            print(
                "EdgeでLIVE&投票ページを"
                "開いてから再実行してください"
            )

            return


        print()

        print(
            "[2] 対象ページ確定"
        )

        print(
            "URL:",
            page.url,
        )

        print(
            "TITLE:",
            page.title(),
        )


        def on_response(response):

            try:

                request = response.request

                url = response.url

                request_url_lower = (
                    url.lower()
                )

                post_data = request.post_data


                target_hit = False


                if TARGET_TYPE.lower() in (
                    request_url_lower
                ):

                    target_hit = True


                if post_data:

                    if TARGET_TYPE.lower() in (
                        post_data.lower()
                    ):

                        target_hit = True


                if not target_hit:

                    return


                print()

                print(
                    "=" * 100
                )

                print(
                    "★ JSJ002 RESPONSE HIT ★"
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
                    "RESOURCE TYPE:",
                    request.resource_type,
                )

                print(
                    "STATUS:",
                    response.status,
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


                headers = {}

                try:

                    headers = request.all_headers()

                except Exception:

                    pass


                response_headers = {}

                try:

                    response_headers = (
                        response.all_headers()
                    )

                except Exception:

                    pass


                body_text = ""

                body_json = None


                try:

                    body_text = response.text()

                except Exception as e:

                    body_text = (
                        "RESPONSE TEXT ERROR: "
                        + repr(e)
                    )


                try:

                    body_json = response.json()

                except Exception:

                    body_json = None


                record_no = len(records) + 1


                body_path = (
                    OUT_DIR
                    / (
                        f"{record_no:03d}_"
                        f"JSJ002_response.txt"
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
                            f"JSJ002_response.json"
                        )
                    )

                    save_json(
                        json_path,
                        body_json,
                    )


                record = {
                    "record_no": record_no,
                    "url": url,
                    "method": request.method,
                    "resource_type": (
                        request.resource_type
                    ),
                    "status": response.status,
                    "post_data": post_data,
                    "parsed_path": parsed.path,
                    "query": parsed.query,
                    "query_params": query_params,
                    "request_headers": headers,
                    "response_headers": (
                        response_headers
                    ),
                    "body_path": str(body_path),
                    "json_path": (
                        str(json_path)
                        if json_path
                        else None
                    ),
                    "body_length": len(body_text),
                    "body_json_type": (
                        type(body_json).__name__
                        if body_json is not None
                        else None
                    ),
                }


                if isinstance(
                    body_json,
                    dict,
                ):

                    record[
                        "body_top_keys"
                    ] = list(
                        body_json.keys()
                    )

                    race_info = body_json.get(
                        "raceInfo"
                    )

                    if isinstance(
                        race_info,
                        list,
                    ):

                        record[
                            "raceInfo_count"
                        ] = len(race_info)

                        narabi_summary = []


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


                            narabi_summary.append({
                                "raceNo": race.get(
                                    "raceNo"
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


                        record[
                            "narabiyoso_summary"
                        ] = narabi_summary


                        print()

                        print(
                            "raceInfo件数:",
                            len(race_info),
                        )

                        print()

                        print(
                            "★ narabiyoso SUMMARY ★"
                        )

                        print(
                            json.dumps(
                                narabi_summary,
                                ensure_ascii=False,
                                indent=2,
                            )
                        )


                records.append(
                    record
                )


                save_json(
                    OUT_JSON,
                    {
                        "program": (
                            "025_capture_live_jsj002.py"
                        ),
                        "target_type": TARGET_TYPE,
                        "records": records,
                    },
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


        page.on(
            "response",
            on_response,
        )


        print()

        print(
            "[3] JSJ002監視開始"
        )

        print()

        print(
            "ページをリロードします"
        )


        try:

            page.reload(
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
            "[4] 通信待機 20秒"
        )


        for second in range(
            1,
            21,
        ):

            print(
                f"{second}/20秒"
            )

            time.sleep(1)


        print()

        print(
            "=" * 100
        )

        print(
            "025 最終結果"
        )

        print(
            "=" * 100
        )

        print()

        print(
            "JSJ002 HIT:",
            len(records),
        )

        print()

        print(
            "保存先:"
        )

        print(
            OUT_JSON
        )

        print()


        if records:

            print(
                "★ JSJ002捕獲成功 ★"
            )

            print()

            for record in records:

                print(
                    "URL:",
                    record["url"],
                )

                print(
                    "QUERY PARAMS:",
                    record["query_params"],
                )

                print(
                    "raceInfo_count:",
                    record.get(
                        "raceInfo_count"
                    ),
                )

                print()

        else:

            print(
                "JSJ002は捕獲されませんでした"
            )


        print()

        print(
            "=== 025 完了 ==="
        )


if __name__ == "__main__":

    main()