from playwright.sync_api import sync_playwright
import time


def main():

    print("=== 105 全通信URL確認テスト ===")

    with sync_playwright() as p:

        browser = p.chromium.connect_over_cdp(
            "http://127.0.0.1:9222"
        )

        context = browser.contexts[0]

        page = None

        for pg in context.pages:

            if "keirin.jp" in pg.url:
                page = pg
                break

        if page is None:
            print("❌ keirin.jpのタブが見つかりません")
            return

        print()
        print("🔥 ブラウザを操作してください")
        print("確定済みレースがある開催を表示してください")
        print("「結果一覧」は押さないでください")
        print()

        input("準備できたらEnter：")

        requests = []

        def handle_response(response):

            url = response.url

            requests.append(url)

            print()
            print("🔥 RESPONSE")
            print(url)

        context.on(
            "response",
            handle_response
        )

        result_button = page.locator(
            "#hhbtnResultList"
        )

        if result_button.count() == 0:

            print("❌ 結果一覧ボタンが見つかりません")
            return

        print()
        print("🔥 結果一覧をクリックします")

        result_button.click()

        page.wait_for_timeout(10000)

        context.remove_listener(
            "response",
            handle_response
        )

        print()
        print("=" * 70)
        print("🔥 105 調査完了")
        print("=" * 70)

        print()
        print(
            "取得通信数:",
            len(requests)
        )

        print()
        print("=== 全通信URL ===")

        for i, url in enumerate(
            requests,
            start=1
        ):

            print(
                i,
                url
            )

        input(
            "確認できたらEnter："
        )


if __name__ == "__main__":
    main()