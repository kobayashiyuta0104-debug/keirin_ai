import json
from playwright.sync_api import sync_playwright


def extract_result(data):
    finish_order = []

    for item in data.get("tyakujyunItemSubData", []):
        tyaku = str(item.get("tyaku", "")).strip()
        syaban = str(item.get("syaban", "")).strip()
        sensyu_name = str(item.get("sensyuName", "")).strip()

        if tyaku in ["1", "2", "3"]:
            finish_order.append(
                {
                    "着順": int(tyaku),
                    "車番": syaban,
                    "選手名": sensyu_name,
                }
            )

    finish_order.sort(key=lambda x: x["着順"])

    harai_data = data.get("haraiGakuSubData", {})

    rt3_items = harai_data.get(
        "RT3HaraiGakuDispItemSubData",
        []
    )

    sanrentan = []

    for item in rt3_items:
        kumi_ban = str(item.get("kumiBan", "")).strip()
        harai_gaku = str(item.get("haraiGaku", "")).strip()
        ninki = str(item.get("ninki", "")).strip()

        if kumi_ban:
            sanrentan.append(
                {
                    "組番": kumi_ban,
                    "払戻金": harai_gaku,
                    "人気": ninki,
                }
            )

    return finish_order, sanrentan


def main():
    print("=== JSJ012 捕獲＋確定結果抽出 ===")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="msedge"
        )

        page = browser.new_page()

        captured = {"done": False}

        def on_response(response):
            if captured["done"]:
                return

            if "type=JSJ012" not in response.url:
                return

            print()
            print("🔥 JSJ012発見！")
            print("URL:", response.url)
            print("STATUS:", response.status)

            try:
                data = response.json()
            except Exception as e:
                print("JSON取得失敗:", e)
                return

            captured["done"] = True

            print()
            print("【着順】")

            finish_order, sanrentan = extract_result(data)

            for item in finish_order:
                print(
                    f'{item["着順"]}着 '
                    f'{item["車番"]}番 '
                    f'{item["選手名"]}'
                )

            print()
            print("【3連単】")

            for item in sanrentan:
                print(
                    f'{item["組番"]} '
                    f'{item["払戻金"]}円 '
                    f'{item["人気"]}'
                )

            with open(
                "090_jsj012_response.json",
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            print()
            print("🔥 JSON保存成功！")
            print("保存先: 090_jsj012_response.json")

        page.on("response", on_response)

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded"
        )

        print()
        print("🔥 ブラウザを操作してください")
        print("JSJ012が出る結果ページまで進んでください")
        print()
        print("確定結果を取得できたら自動で終了します")

        while not captured["done"]:
            page.wait_for_timeout(500)

        page.wait_for_timeout(1000)

        browser.close()

    print()
    print("=== 捕獲＋抽出完了 ===")


if __name__ == "__main__":
    main()