from playwright.sync_api import sync_playwright
import json


def main():

    print("=== 098 競輪場・開催切替調査 ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()
        page = context.new_page()

        records = []
        recording = False

        def handle_request(request):

            if not recording:
                return

            if "/pc/json" not in request.url:
                return

            record = {
                "url": request.url,
                "method": request.method,
                "post_data": request.post_data,
                "page_url": request.frame.url,
                "resource_type": request.resource_type
            }

            records.append(record)

            print()
            print("🔥 JSON通信発見")
            print("URL:", request.url)
            print("METHOD:", request.method)
            print("PAGE URL:", request.frame.url)
            print("TYPE:", request.resource_type)

        context.on(
            "request",
            handle_request
        )

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded"
        )

        print()
        print("🔥 ブラウザを操作してください")
        print()
        print("1. 確定結果ページを1開催開く")
        print("2. その開催の1レースを表示する")
        print()
        input(
            "準備できたらターミナルに戻ってEnter："
        )

        records.clear()
        recording = True

        print()
        print("=" * 70)
        print("🔥 15秒間の通信監視開始")
        print("=" * 70)
        print()
        print("今すぐブラウザに戻って")
        print("別の競輪場・別開催へ1回だけ切り替えてください")
        print()
        print("例：奈良 → 小松島")
        print()

        page.wait_for_timeout(15000)

        recording = False

        print()
        print("=" * 70)
        print("🔥 通信記録終了")
        print("=" * 70)

        save_file = (
            "098_venue_switch_requests.json"
        )

        with open(
            save_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                records,
                f,
                ensure_ascii=False,
                indent=2
            )

        print()
        print("取得通信数:", len(records))
        print("保存先:", save_file)

        print()
        print("=== 通信一覧 ===")

        for index, record in enumerate(
            records,
            start=1
        ):

            print()
            print("-" * 70)
            print(
                f"【通信 #{index}】"
            )
            print(
                "URL:",
                record["url"]
            )
            print(
                "METHOD:",
                record["method"]
            )
            print(
                "PAGE URL:",
                record["page_url"]
            )
            print(
                "TYPE:",
                record["resource_type"]
            )

        print()
        print("=" * 70)
        print("🔥 098 調査完了")
        print("=" * 70)

        input(
            "確認できたらEnter："
        )

        browser.close()


if __name__ == "__main__":
    main()