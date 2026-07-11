import json
import re
import time

from playwright.sync_api import sync_playwright


OUTPUT_FILE = "170_result_button_route.json"

KEIRIN_URL = "https://www.keirin.jp/pc/top"


def main():

    print("=" * 70)
    print("🔥 170 競走結果ボタン onclick 直接取得")
    print("=" * 70)

    output = {
        "page_url": "",
        "page_title": "",
        "buttons": [],
    }

    with sync_playwright() as p:

        print()
        print("🔥 Edge起動")

        browser = p.chromium.launch(
            channel="msedge",
            headless=False,
        )

        context = browser.new_context()

        page = context.new_page()

        print()
        print("🔥 KEIRIN.JPを開く")

        page.goto(
            KEIRIN_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        time.sleep(5)

        print()
        print("=" * 70)
        print("🔥 準備")
        print("=" * 70)
        print("155成功時と同じ画面へ移動")
        print("開催場・レース一覧が見える画面でEnter")
        print("=" * 70)

        input()

        output["page_url"] = page.url
        output["page_title"] = page.title()

        print()
        print("🔥 現在URL")
        print(page.url)

        print()
        print("🔥 現在TITLE")
        print(page.title())

        print()
        print("=" * 70)
        print("🔥 pibtnResult直接調査")
        print("=" * 70)

        buttons = page.locator("#pibtnResult")

        button_count = buttons.count()

        print("pibtnResult件数:", button_count)

        for index in range(button_count):

            button = buttons.nth(index)

            try:

                info = button.evaluate(
                    """
                    el => ({
                        id: el.id || "",
                        text:
                            (
                                el.innerText ||
                                el.textContent ||
                                ""
                            ).trim(),
                        onclickAttribute:
                            el.getAttribute("onclick") || "",
                        onclickProperty:
                            el.onclick
                            ? el.onclick.toString()
                            : "",
                        outerHTML:
                            el.outerHTML || "",
                        className:
                            el.className || "",
                        disabled:
                            !!el.disabled,
                        visible:
                            !!(
                                el.offsetWidth ||
                                el.offsetHeight ||
                                el.getClientRects().length
                            )
                    })
                    """
                )

            except Exception as e:

                print("取得失敗:", e)
                continue

            onclick = info.get(
                "onclickAttribute",
                "",
            )

            print()
            print("-" * 70)
            print("🔥 RESULT BUTTON", index)
            print("ID:", info["id"])
            print("TEXT:", info["text"])
            print("CLASS:", info["className"])
            print("VISIBLE:", info["visible"])
            print("DISABLED:", info["disabled"])
            print()
            print("ONCLICK ATTRIBUTE:")
            print(info["onclickAttribute"])
            print()
            print("ONCLICK PROPERTY:")
            print(info["onclickProperty"])
            print()
            print("OUTER HTML:")
            print(info["outerHTML"])

            race_basic_url = None
            enc_prm = None

            match = re.search(
                r"""pibtnResultClick\(
                    \s*["']([^"']+)["']
                    \s*,\s*
                    ["']([^"']+)["']
                    \s*\)
                """,
                onclick,
                re.VERBOSE,
            )

            if match:

                race_basic_url = match.group(1)
                enc_prm = match.group(2)

                print()
                print("🔥 RESULT ROUTE解析成功")
                print("raceBasicURL:", race_basic_url)
                print("encPrm:", enc_prm)
                print("disp: PJ0326")

            else:

                print()
                print("⚠ RESULT ROUTE解析失敗")

            item = {
                **info,
                "raceBasicURL": race_basic_url,
                "encPrm": enc_prm,
                "disp": "PJ0326",
            }

            output["buttons"].append(item)

        print()
        print("=" * 70)
        print("🔥 JavaScript変数直接探索")
        print("=" * 70)

        js_result = page.evaluate(
            """
            () => {

                const result = {};

                const names = [
                    "raceBasicURL",
                    "encPrm",
                    "reqPrm",
                    "jsondata"
                ];

                for (const name of names) {

                    try {

                        if (
                            typeof window[name]
                            !== "undefined"
                        ) {

                            result[name] =
                                window[name];

                        }

                    } catch (e) {

                        result[name + "_error"] =
                            e.toString();

                    }

                }

                return result;
            }
            """
        )

        print(
            json.dumps(
                js_result,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        output["javascript_variables"] = js_result

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
                default=str,
            )

        success_count = sum(
            1
            for item in output["buttons"]
            if item.get("raceBasicURL")
            and item.get("encPrm")
        )

        print()
        print("=" * 70)
        print("🔥 170テスト終了")
        print("=" * 70)
        print(
            "pibtnResult件数:",
            button_count,
        )
        print(
            "🔥 RESULT ROUTE取得成功数:",
            success_count,
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