from playwright.sync_api import sync_playwright
import json


def main():

    print("=== 104 結果一覧クリック通信調査 ===")

    with sync_playwright() as p:

        browser = p.chromium.connect_over_cdp(
            "http://127.0.0.1:9222"
        )

        context = browser.contexts[0]

        # KEIRIN.JPのタブを探す
        page = None

        for p_page in context.pages:

            if "keirin.jp" in p_page.url.lower():
                page = p_page

        if page is None:
            print("❌ KEIRIN.JPのタブが見つかりません")
            return

        print()
        print("🔥 使用ページ")
        print(page.url)

        print()
        print("🔥 ブラウザを操作してください")
        print("確定済みレースがある開催を表示してください")
        print()
        print("『結果一覧』は押さないでください")
        print()

        input("準備できたらEnter：")

        requests = []

        # --------------------------------------------------
        # JSON通信監視
        # --------------------------------------------------

        def handle_response(response):

            if "/pc/json?" not in response.url:
                return

            try:

                data = response.json()

            except Exception:
                data = None

            requests.append(
                {
                    "url": response.url,
                    "status": response.status,
                    "data": data,
                }
            )

            print()
            print("🔥 JSON通信発見")
            print("URL:", response.url)
            print("STATUS:", response.status)

        context.on(
            "response",
            handle_response
        )

        # --------------------------------------------------
        # 結果一覧ボタン確認
        # --------------------------------------------------

        result_button = page.locator(
            "#hhbtnResultList"
        )

        if result_button.count() == 0:

            print()
            print("❌ 結果一覧ボタンが見つかりません")

            context.remove_listener(
                "response",
                handle_response
            )

            return

        print()
        print("🔥 結果一覧ボタン発見！")

        # --------------------------------------------------
        # 結果一覧クリック
        # --------------------------------------------------

        print()
        print("🔥 結果一覧をクリックします")

        result_button.click()

        # Playwrightに通信処理をさせる
        page.wait_for_timeout(5000)

        # --------------------------------------------------
        # listener解除
        # --------------------------------------------------

        context.remove_listener(
            "response",
            handle_response
        )

        # --------------------------------------------------
        # 保存
        # --------------------------------------------------

        output_file = (
            "104_result_list_requests.json"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                requests,
                f,
                ensure_ascii=False,
                indent=2
            )

        print()
        print("=" * 70)
        print("🔥 104 調査完了")
        print("=" * 70)

        print()
        print(
            "取得通信数:",
            len(requests)
        )

        print(
            "保存先:",
            output_file
        )

        print()
        print("=== JSON通信一覧 ===")

        for i, item in enumerate(
            requests,
            start=1
        ):

            print()
            print("-" * 70)
            print(
                f"【通信 #{i}】"
            )
            print(
                item["url"]
            )

        input(
            "\n確認できたらEnter："
        )


if __name__ == "__main__":
    main()