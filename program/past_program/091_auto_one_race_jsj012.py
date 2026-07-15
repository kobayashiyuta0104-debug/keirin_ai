from playwright.sync_api import sync_playwright
import json


def main():

    print("=== 091 指定1レース自動取得テスト ===")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        context = browser.new_context()

        jsj012_data = None

        def handle_response(response):

            nonlocal jsj012_data

            if "JSJ012" not in response.url:
                return

            print("\n🔥 JSJ012発見！")
            print("URL:", response.url)
            print("STATUS:", response.status)

            try:

                data = response.json()

                jsj012_data = data

                print("🔥 JSON取得成功！")

            except Exception as e:

                print("JSON取得失敗:", e)

        # ブラウザ内の全ページを監視
        context.on(
            "response",
            handle_response
        )

        page = context.new_page()

        # 競輪JPを開く
        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded"
        )

        print()
        print("🔥 ブラウザを操作してください")
        print("テストしたい確定結果ページまで進んでください")
        print()
        print("今回はJSJ012を取得したら自動終了します")

        # JSJ012待機
        # time.sleepは使わない
        while jsj012_data is None:

            page.wait_for_timeout(500)

        print("\n🔥 JSJ012取得完了！")

        # 保存
        save_file = "091_jsj012_response.json"

        with open(
            save_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                jsj012_data,
                f,
                ensure_ascii=False,
                indent=2
            )

        print("保存先:", save_file)

        # 着順
        print("\n【着順】")

        racers = jsj012_data.get(
            "tyakujyunItemSubData",
            []
        )

        for racer in racers:

            tyaku = racer.get("tyaku", "")
            syaban = racer.get("syaban", "")
            name = racer.get("sensyuName", "")

            if tyaku in ["1", "2", "3"]:

                print(
                    f"{tyaku}着 "
                    f"{syaban}番 "
                    f"{name}"
                )

        # 3連単
        print("\n【3連単】")

        harai = jsj012_data.get(
            "haraiGakuSubData",
            {}
        )

        sanrentan = harai.get(
            "RT3HaraiGakuDispItemSubData",
            []
        )

        for item in sanrentan:

            kumi = item.get("kumiBan", "")
            money = item.get("haraiGaku", "")
            ninki = item.get("ninki", "")

            print(
                f"{kumi} "
                f"{money}円 "
                f"{ninki}"
            )

        print("\n=== 091 自動取得テスト完了 ===")

        print("🔥 ブラウザを閉じます")

        browser.close()


if __name__ == "__main__":
    main()