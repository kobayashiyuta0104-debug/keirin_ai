import json
import time

from playwright.sync_api import sync_playwright


OUTPUT_FILE = "171_piinitialize_trigger_hunt.json"

KEIRIN_URL = "https://www.keirin.jp/pc/top"


SEARCH_WORDS = [
    "piInitialize",
    "reqTanpyoTenkai",
    "PJ9110Controller",
    "PJ9110View",
    "pibtnResult",
]


def make_sample(text, word, before=3000, after=6000):

    position = text.find(word)

    if position < 0:
        return ""

    start = max(
        0,
        position - before,
    )

    end = min(
        len(text),
        position + after,
    )

    return text[start:end]


def main():

    print("=" * 70)
    print("🔥 171 piInitialize 発火元完全追跡")
    print("=" * 70)

    output = {
        "page_url": "",
        "page_title": "",
        "dom_hits": [],
        "script_hits": [],
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
        print("🔥 DOM 発火候補探索")
        print("=" * 70)

        elements = page.locator(
            "a, button, input, [onclick]"
        )

        count = elements.count()

        print("ELEMENT数:", count)

        for index in range(count):

            element = elements.nth(index)

            try:

                info = element.evaluate(
                    """
                    el => ({
                        tag: el.tagName || "",
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
                        onclick:
                            el.getAttribute("onclick") || "",
                        href:
                            el.href || "",
                        outerHTML:
                            el.outerHTML || ""
                    })
                    """
                )

            except Exception:
                continue

            combined = " ".join([
                info["id"],
                info["className"],
                info["text"],
                info["onclick"],
                info["href"],
                info["outerHTML"],
            ])

            words = [
                "短評",
                "展開",
                "tanpyo",
                "tenkai",
                "PJ9110",
                "piInitialize",
                "reqTanpyoTenkai",
            ]

            if not any(
                word.lower() in combined.lower()
                for word in words
            ):
                continue

            item = {
                "index": index,
                **info,
            }

            output["dom_hits"].append(item)

            print()
            print("-" * 70)
            print("🔥 DOM HIT")
            print("INDEX:", index)
            print("TAG:", info["tag"])
            print("ID:", info["id"])
            print("CLASS:", info["className"])
            print("TEXT:", info["text"])
            print("ONCLICK:", info["onclick"])
            print("HREF:", info["href"])
            print()
            print("OUTER HTML:")
            print(info["outerHTML"])

        print()
        print("=" * 70)
        print("🔥 外部JavaScript 全文探索")
        print("=" * 70)

        js_urls = page.evaluate(
            """
            () => Array.from(document.scripts)
                .map(script => script.src)
                .filter(Boolean)
            """
        )

        print("外部JS数:", len(js_urls))

        for js_index, js_url in enumerate(js_urls):

            try:

                response = context.request.get(
                    js_url,
                    timeout=30000,
                )

                if not response.ok:
                    continue

                text = response.text()

            except Exception:
                continue

            for word in SEARCH_WORDS:

                if word not in text:
                    continue

                sample = make_sample(
                    text,
                    word,
                )

                item = {
                    "js_index": js_index,
                    "url": js_url,
                    "word": word,
                    "sample": sample,
                }

                output["script_hits"].append(item)

                print()
                print("-" * 70)
                print("🔥 SCRIPT HIT")
                print("WORD:", word)
                print("JS INDEX:", js_index)
                print("URL:", js_url)
                print()
                print(sample)

        print()
        print("=" * 70)
        print("🔥 window関数存在確認")
        print("=" * 70)

        functions = page.evaluate(
            """
            () => {

                const names = [
                    "piInitialize",
                    "pibtnResultClick"
                ];

                const result = {};

                for (const name of names) {

                    result[name] = {
                        exists:
                            typeof window[name]
                            !== "undefined",

                        type:
                            typeof window[name],

                        source:
                            typeof window[name]
                            === "function"
                            ? window[name].toString()
                            : ""
                    };

                }

                return result;
            }
            """
        )

        output["window_functions"] = functions

        print(
            json.dumps(
                functions,
                ensure_ascii=False,
                indent=2,
            )
        )

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
        print("🔥 171テスト終了")
        print("=" * 70)
        print(
            "DOM HIT数:",
            len(output["dom_hits"]),
        )
        print(
            "SCRIPT HIT数:",
            len(output["script_hits"]),
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