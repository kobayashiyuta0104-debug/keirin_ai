import json
import time

from playwright.sync_api import sync_playwright


OUTPUT_FILE = "167_clickable_dom_inventory.json"

KEIRIN_URL = "https://www.keirin.jp/pc/top"


def main():

    print("=" * 70)
    print("🔥 167 KEIRIN.JP クリック要素完全調査")
    print("=" * 70)

    output = []

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
        print("🔥 ここで準備")
        print("=" * 70)
        print("Edgeで155成功時と同じ画面まで移動")
        print("開催場とレース番号が見える画面で止める")
        print("準備できたらEnter")
        print("=" * 70)

        input()

        print()
        print("🔥 現在URL")
        print(page.url)

        print()
        print("🔥 現在TITLE")
        print(page.title())

        elements = page.locator(
            "a, button, input, [onclick], [role='button']"
        )

        count = elements.count()

        print()
        print("🔥 対象ELEMENT数:", count)

        for i in range(count):

            element = elements.nth(i)

            try:

                info = element.evaluate(
                    """
                    el => ({
                        tag: el.tagName,
                        id: el.id || "",
                        className:
                            typeof el.className === "string"
                            ? el.className
                            : "",
                        text:
                            (
                                el.innerText ||
                                el.value ||
                                el.textContent ||
                                ""
                            ).trim(),
                        href:
                            el.href || "",
                        onclick:
                            el.getAttribute("onclick") || "",
                        name:
                            el.getAttribute("name") || "",
                        type:
                            el.getAttribute("type") || "",
                        role:
                            el.getAttribute("role") || "",
                        visible:
                            !!(
                                el.offsetWidth ||
                                el.offsetHeight ||
                                el.getClientRects().length
                            )
                    })
                    """
                )

            except Exception:
                continue

            info["index"] = i

            output.append(info)

            text = info["text"]
            element_id = info["id"]
            class_name = info["className"]
            href = info["href"]
            onclick = info["onclick"]

            combined = (
                text
                + " "
                + element_id
                + " "
                + class_name
                + " "
                + href
                + " "
                + onclick
            ).lower()

            important_words = [
                "1r",
                "2r",
                "3r",
                "4r",
                "5r",
                "6r",
                "7r",
                "8r",
                "9r",
                "10r",
                "11r",
                "12r",
                "結果",
                "競走結果",
                "race",
                "result",
                "jsj012",
                "jsj006",
            ]

            if any(
                word.lower() in combined
                for word in important_words
            ):

                print()
                print("-" * 70)
                print("🔥 ELEMENT INDEX:", i)
                print("TAG     :", info["tag"])
                print("ID      :", info["id"])
                print("CLASS   :", info["className"])
                print("TEXT    :", info["text"])
                print("HREF    :", info["href"])
                print("ONCLICK :", info["onclick"])
                print("NAME    :", info["name"])
                print("TYPE    :", info["type"])
                print("ROLE    :", info["role"])
                print("VISIBLE :", info["visible"])

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
        print("🔥 167テスト終了")
        print("=" * 70)
        print("ELEMENT総数:", len(output))
        print("保存先:", OUTPUT_FILE)
        print("=" * 70)

        input("確認できたらEnter：")

        browser.close()


if __name__ == "__main__":
    main()