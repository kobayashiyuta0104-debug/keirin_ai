from playwright.sync_api import sync_playwright
import json


def main():

    print("=== 094 レース切替通信調査 ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()

        captured_requests = []

        def handle_request(request):

            url = request.url

            if "/pc/json" not in url:
                return

            try:
                post_data = request.post_data
            except Exception:
                post_data = None

            item = {
                "url": url,
                "method": request.method,
                "post_data": post_data,
                "headers": dict(request.headers),
            }

            captured_requests.append(item)

            print()
            print("🔥 JSON通信発見")
            print("URL:", url)
            print("METHOD:", request.method)

            if post_data:
                print("POST DATA:", post_data)

        page = context.new_page()

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded"
        )

        print()
        print("🔥 ブラウザを操作してください")
        print()
        print("同じ開催場・同じ開催日の")
        print("確定結果ページを1レース開いてください")
        print()
        print("例：7Rを開く")
        print()
        print("開いたらターミナルに戻って")
        print("Enterを押してください")

        input()

        print()
        print("=" * 70)
        print("🔥 15秒間の通信監視開始")
        print("=" * 70)
        print()
        print("今すぐブラウザで")
        print("次のレースへ1回だけ切り替えてください")
        print()
        print("例：7R → 8R")

        context.on("request", handle_request)

        # 15秒間Playwrightを動かしながら監視
        page.wait_for_timeout(15000)

        context.remove_listener(
            "request",
            handle_request
        )

        print()
        print("=" * 70)
        print("🔥 通信記録終了")
        print("=" * 70)

        save_file = "094_race_switch_requests.json"

        with open(
            save_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                captured_requests,
                f,
                ensure_ascii=False,
                indent=2
            )

        print()
        print("取得通信数:", len(captured_requests))
        print("保存先:", save_file)

        print()
        print("=== 通信一覧 ===")

        for i, item in enumerate(
            captured_requests,
            start=1
        ):

            print()
            print("-" * 70)
            print(f"【通信 #{i}】")
            print("URL:", item["url"])
            print("METHOD:", item["method"])

            if item["post_data"]:
                print(
                    "POST DATA:",
                    item["post_data"]
                )

        print()
        print("=" * 70)
        print("🔥 094 調査完了")
        print("=" * 70)

        browser.close()


if __name__ == "__main__":
    main()