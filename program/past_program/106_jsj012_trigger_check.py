from playwright.sync_api import sync_playwright
import time


def main():

    print("=== 106 JSJ012発生タイミング確認 ===")

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
        print("確定済みレースがある開催のレース画面を開いてください")
        print("例：豊橋の確定済み1Rなど")
        print()

        input("準備できたらEnter：")

        jsj012_count = 0

        def handle_response(response):

            nonlocal jsj012_count

            url = response.url

            if "JSJ012" not in url.upper():
                return

            jsj012_count += 1

            print()
            print("=" * 70)
            print("🔥🔥🔥 JSJ012発見！")
            print("URL:", url)
            print("現在ページ:", page.url)
            print("発見数:", jsj012_count)
            print("=" * 70)

        context.on(
            "response",
            handle_response
        )

        print()
        print("🔥 監視開始")
        print()
        print("これからブラウザを手動操作してください")
        print()
        print("順番に👇")
        print("① 別のレース番号を押す")
        print("② 競走結果タブを押す")
        print("③ 基本情報タブを押す")
        print("④ また別のレース番号を押す")
        print()
        print("操作するたびに2〜3秒待ってください")
        print()
        print("全部終わったら、このターミナルでEnterを押してください")
        print()

        input("手動操作が終わったらEnter：")

        context.remove_listener(
            "response",
            handle_response
        )

        print()
        print("=" * 70)
        print("🔥 106 調査完了")
        print("=" * 70)

        print(
            "JSJ012発見数:",
            jsj012_count
        )

        input(
            "確認できたらEnter："
        )


if __name__ == "__main__":
    main()