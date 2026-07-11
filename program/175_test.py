from playwright.sync_api import sync_playwright
import json
from urllib.parse import urlparse, parse_qs


OUTPUT_FILE = "175_jsj006_live_capture.json"


def main():

    print("=" * 70)
    print("🔥 175 JSJ006 完全常時監視")
    print("=" * 70)

    jsj006_requests = []
    all_json_requests = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            channel="msedge",
            headless=False,
        )

        page = browser.new_page()

        def on_request(request):

            url = request.url

            if "/pc/json" not in url:
                return

            parsed = urlparse(url)

            query = parse_qs(
                parsed.query,
                keep_blank_values=True,
            )

            simple_query = {}

            for key, values in query.items():

                if len(values) == 1:
                    simple_query[key] = values[0]
                else:
                    simple_query[key] = values

            item = {
                "method": request.method,
                "url": url,
                "query": simple_query,
                "post_data": request.post_data,
            }

            all_json_requests.append(item)

            request_type = simple_query.get("type")

            print()
            print(
                "🔥 JSON通信:",
                request_type,
            )

            if request_type == "JSJ006":

                jsj006_requests.append(item)

                print()
                print("=" * 70)
                print("🔥🔥🔥 JSJ006捕獲成功 🔥🔥🔥")
                print("=" * 70)

                print("METHOD:", request.method)

                print()
                print("URL:")
                print(url)

                print()
                print("QUERY:")
                print(
                    json.dumps(
                        simple_query,
                        ensure_ascii=False,
                        indent=2,
                    )
                )

                print()
                print("POST DATA:")
                print(request.post_data)

                print("=" * 70)

                save_data(
                    jsj006_requests,
                    all_json_requests,
                )

        def on_response(response):

            url = response.url

            if "type=JSJ006" not in url:
                return

            print()
            print("=" * 70)
            print("🔥 JSJ006 RESPONSE")
            print("=" * 70)

            print(
                "STATUS:",
                response.status,
            )

            try:

                data = response.json()

                print(
                    "JSON TYPE:",
                    type(data).__name__,
                )

                if isinstance(data, dict):

                    print(
                        "ROOT KEYS:",
                        list(data.keys()),
                    )

                    players = data.get(
                        "sensyuTypeInfo",
                        [],
                    )

                    print(
                        "選手数:",
                        len(players),
                    )

                    for player in players:

                        print(
                            player.get("syaban"),
                            player.get("sensyuName"),
                            player.get("sensyuRegistNo"),
                        )

            except Exception as e:

                print(
                    "RESPONSE解析失敗:",
                    e,
                )

        def save_data(
            jsj006,
            all_json,
        ):

            output = {
                "jsj006_requests": jsj006,
                "all_json_requests": all_json,
            }

            with open(
                OUTPUT_FILE,
                "w",
                encoding="utf-8",
            ) as f:

                json.dump(
                    output,
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

        page.on(
            "request",
            on_request,
        )

        page.on(
            "response",
            on_response,
        )

        print()
        print("🔥 監視開始済み")
        print("🔥 これからEdgeを開く")
        print()
        print(
            "Edgeが開いたら155成功時と同じ"
        )
        print(
            "開催場・レース一覧画面まで移動"
        )
        print()
        print(
            "🔥 今回は移動中から全部監視している"
        )

        page.goto(
            "https://keirin.jp/",
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print()
        print("=" * 70)
        print("🔥 手動操作開始")
        print("=" * 70)
        print(
            "155成功時と同じ画面まで移動"
        )
        print()
        print(
            "🔥 JSJ006捕獲成功が出るまで操作"
        )
        print()
        print(
            "画面まで行ったらEnter"
        )

        input()

        save_data(
            jsj006_requests,
            all_json_requests,
        )

        print()
        print("=" * 70)
        print("🔥 JSJ006 REQUEST最終確認")
        print("=" * 70)

        for i, item in enumerate(
            jsj006_requests
        ):

            print()
            print("-" * 70)
            print(
                f"🔥 JSJ006 #{i + 1}"
            )

            print(
                "METHOD:",
                item["method"],
            )

            print()
            print("QUERY:")

            print(
                json.dumps(
                    item["query"],
                    ensure_ascii=False,
                    indent=2,
                )
            )

            print()
            print(
                "POST DATA:",
                item["post_data"],
            )

        encp_candidates = []

        for item in jsj006_requests:

            query = item["query"]

            for key, value in query.items():

                key_lower = str(key).lower()

                if (
                    "enc" in key_lower
                    or "prm" in key_lower
                    or "para" in key_lower
                ):

                    if value not in encp_candidates:

                        encp_candidates.append(
                            value
                        )

        print()
        print("=" * 70)
        print("🔥 PARAMETER候補")
        print("=" * 70)

        print(
            "候補数:",
            len(encp_candidates),
        )

        for i, value in enumerate(
            encp_candidates
        ):

            print()
            print(
                f"🔥 PARAMETER #{i + 1}"
            )
            print(value)

        print()
        print("=" * 70)
        print("🔥 175テスト終了")
        print("=" * 70)

        print(
            "JSON通信総数:",
            len(all_json_requests),
        )

        print(
            "JSJ006 REQUEST数:",
            len(jsj006_requests),
        )

        print(
            "PARAMETER候補数:",
            len(encp_candidates),
        )

        print(
            "保存先:",
            OUTPUT_FILE,
        )

        print("=" * 70)

        input(
            "確認できたらEnter："
        )

        browser.close()


def save_data(
    jsj006,
    all_json,
):

    output = {
        "jsj006_requests": jsj006,
        "all_json_requests": all_json,
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2,
        )


if __name__ == "__main__":
    main()