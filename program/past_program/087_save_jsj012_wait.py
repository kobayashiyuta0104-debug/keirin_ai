from playwright.sync_api import sync_playwright
import json
import time


SAVE_FILE = "087_jsj012_response.json"


def main():

    saved = False

    with sync_playwright() as p:

        browser = p.chromium.launch(
            channel="msedge",
            headless=False
        )

        page = browser.new_page()

        print("=== JSJ012 保存待機テスト開始 ===")
        print()
        print("🔥 ブラウザを操作してください")
        print("JSJ012が出る結果ページまで進んでください")
        print()
        print("JSJ012を保存できたら自動で監視を終了します")
        print()

        def on_response(response):

            nonlocal saved

            if saved:
                return

            if "type=JSJ012" not in response.url:
                return

            print()
            print("🔥 JSJ012発見！")
            print("URL:", response.url)
            print("STATUS:", response.status)

            try:
                body = response.body()

                print("レスポンス容量:", len(body), "bytes")

                try:
                    text = body.decode("utf-8")
                except UnicodeDecodeError:
                    text = body.decode("utf-8", errors="replace")

                with open(
                    SAVE_FILE,
                    "w",
                    encoding="utf-8"
                ) as f:
                    f.write(text)

                print("🔥 保存成功！")
                print("保存先:", SAVE_FILE)

                try:
                    data = json.loads(text)

                    print("🔥 JSON解析成功！")
                    print("JSON型:", type(data).__name__)

                except Exception as e:
                    print("JSON解析失敗:", e)

                saved = True

            except Exception as e:
                print("レスポンス取得失敗:", e)

        page.on("response", on_response)

        page.goto(
            "https://www.keirin.jp/",
            wait_until="domcontentloaded"
        )

        while not saved:
            page.wait_for_timeout(500)

        print()
        print("=== JSJ012保存完了 ===")

        time.sleep(2)

        browser.close()


if __name__ == "__main__":
    main()
