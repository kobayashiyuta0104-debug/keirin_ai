from playwright.sync_api import sync_playwright
import json
import time
from urllib.parse import urlparse, parse_qs


OUTPUT_FILE = "174_jsj006_request_parameter_hunt.json"


def main():

    print("=" * 70)
    print("🔥 174 JSJ006 REQUEST PARAMETER完全捕獲")
    print("=" * 70)

    captured = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            channel="msedge",
            headless=False,
        )

        page = browser.new_page()

        def on_request(request):

            url = request.url

            if "type=JSJ006" not in url:
                return

            print()
            print("=" * 70)
            print("🔥 JSJ006 REQUEST発見")
            print("=" * 70)

            print("METHOD :", request.method)
            print("URL    :", url)

            parsed = urlparse(url)

            query = parse_qs(
                parsed.query,
                keep_blank_values=True,
            )

            query_simple = {}

            for key, value in query.items():

                if len(value) == 1:
                    query_simple[key] = value[0]
                else:
                    query_simple[key] = value

            post_data = None

            try:
                post_data = request.post_data
            except Exception:
                pass

            headers = {}

            try:
                headers = request.headers
            except Exception:
                pass

            item = {
                "method": request.method,
                "url": url,
                "query": query_simple,
                "post_data": post_data,
                "headers": headers,
            }

            captured.append(item)

            print()
            print("🔥 QUERY")
            print(
                json.dumps(
                    query_simple,
                    ensure_ascii=False,
                    indent=2,
                )
            )

            print()
            print("🔥 POST DATA")
            print(post_data)

        page.on(
            "request",
            on_request,
        )

        print()
        print("🔥 Edge起動")
        print("🔥 KEIRIN.JPを開く")

        page.goto(
            "https://keirin.jp/",
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print()
        print("=" * 70)
        print("🔥 手動準備")
        print("=" * 70)
        print(
            "155成功時と同じ"
            "開催場・レース一覧画面へ移動"
        )
        print(
            "完全表示されたらEnter"
        )

        input()

        print()
        print("=" * 70)
        print("🔥 JSJ006通信監視開始")
        print("=" * 70)
        print(
            "このまま30秒待機"
        )

        time.sleep(30)

        print()
        print("=" * 70)
        print("🔥 JSJ006 REQUEST一覧")
        print("=" * 70)

        for i, item in enumerate(captured):

            print()
            print("-" * 70)
            print(
                f"🔥 REQUEST #{i + 1}"
            )
            print(
                "METHOD:",
                item["method"],
            )
            print(
                "URL:",
                item["url"],
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

        unique_encp = []

        for item in captured:

            query = item["query"]

            for key in [
                "encp",
                "prm",
                "para",
                "parameter",
            ]:

                value = query.get(key)

                if value:

                    if isinstance(
                        value,
                        list,
                    ):

                        values = value

                    else:

                        values = [value]

                    for v in values:

                        if v not in unique_encp:
                            unique_encp.append(v)

        print()
        print("=" * 70)
        print("🔥 ENCP候補")
        print("=" * 70)

        print(
            "ENCP候補数:",
            len(unique_encp),
        )

        for i, value in enumerate(
            unique_encp
        ):

            print()
            print(
                f"🔥 ENCP #{i + 1}"
            )
            print(value)

        output = {
            "captured_requests":
                captured,

            "unique_encp":
                unique_encp,
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

        print()
        print("=" * 70)
        print("🔥 174テスト終了")
        print("=" * 70)
        print(
            "JSJ006 REQUEST数:",
            len(captured),
        )
        print(
            "ENCP候補数:",
            len(unique_encp),
        )
        print(
            "保存先:",
            OUTPUT_FILE,
        )
        print("=" * 70)

        input("確認できたらEnter：")

        browser.close()


if __name__ == "__main__":
    main()