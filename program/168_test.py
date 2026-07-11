import json
import time

from playwright.sync_api import sync_playwright


OUTPUT_FILE = "168_pibtnResult_event_hunt.json"

KEIRIN_URL = "https://www.keirin.jp/pc/top"


def main():

    print("=" * 70)
    print("🔥 168 pibtnResult JavaScript完全追跡")
    print("=" * 70)

    result = {
        "button": {},
        "jquery_events": {},
        "scripts": [],
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
        print("155成功時と同じ画面まで移動")
        print("開催場・レース一覧が見える画面でEnter")
        print("=" * 70)

        input()

        print()
        print("🔥 現在URL")
        print(page.url)

        print()
        print("🔥 pibtnResult探索")

        button = page.locator("#pibtnResult")

        count = button.count()

        print("pibtnResult件数:", count)

        if count > 0:

            btn = button.first

            button_info = btn.evaluate(
                """
                el => {

                    function safeOuter(node) {
                        if (!node) return "";
                        return node.outerHTML || "";
                    }

                    return {
                        tag: el.tagName,
                        id: el.id || "",
                        className: el.className || "",
                        text: (
                            el.innerText ||
                            el.textContent ||
                            ""
                        ).trim(),
                        outerHTML: safeOuter(el),
                        parentHTML: safeOuter(el.parentElement),
                        grandParentHTML:
                            safeOuter(
                                el.parentElement
                                ? el.parentElement.parentElement
                                : null
                            ),
                        onclickAttribute:
                            el.getAttribute("onclick") || "",
                        onclickProperty:
                            el.onclick
                            ? el.onclick.toString()
                            : "",
                        disabled: el.disabled,
                        display:
                            getComputedStyle(el).display,
                        visibility:
                            getComputedStyle(el).visibility,
                        opacity:
                            getComputedStyle(el).opacity
                    };
                }
                """
            )

            result["button"] = button_info

            print()
            print("=" * 70)
            print("🔥 BUTTON情報")
            print("=" * 70)

            for key, value in button_info.items():

                print()
                print(f"🔥 {key}")
                print(value)

            print()
            print("=" * 70)
            print("🔥 jQuery EVENT探索")
            print("=" * 70)

            jquery_events = page.evaluate(
                """
                () => {

                    const el =
                        document.getElementById("pibtnResult");

                    if (!el) {
                        return {
                            error: "pibtnResult not found"
                        };
                    }

                    if (!window.jQuery) {
                        return {
                            error: "jQuery not found"
                        };
                    }

                    try {

                        const events =
                            jQuery._data(el, "events");

                        if (!events) {
                            return {
                                events: null
                            };
                        }

                        const output = {};

                        for (
                            const [eventName, handlers]
                            of Object.entries(events)
                        ) {

                            output[eventName] =
                                handlers.map(
                                    handler => ({
                                        type:
                                            handler.type || "",
                                        origType:
                                            handler.origType || "",
                                        namespace:
                                            handler.namespace || "",
                                        selector:
                                            handler.selector || "",
                                        handler:
                                            handler.handler
                                            ? handler.handler.toString()
                                            : ""
                                    })
                                );
                        }

                        return output;

                    } catch (e) {

                        return {
                            error: e.toString()
                        };
                    }
                }
                """
            )

            result["jquery_events"] = jquery_events

            print(
                json.dumps(
                    jquery_events,
                    ensure_ascii=False,
                    indent=2,
                )
            )

        print()
        print("=" * 70)
        print("🔥 SCRIPT内 pibtnResult 探索")
        print("=" * 70)

        scripts = page.locator("script")

        script_count = scripts.count()

        print("SCRIPT数:", script_count)

        for i in range(script_count):

            script = scripts.nth(i)

            try:

                src = script.get_attribute("src") or ""

                text = script.text_content() or ""

            except Exception:
                continue

            if "pibtnResult" in text:

                item = {
                    "index": i,
                    "src": src,
                    "text": text,
                }

                result["scripts"].append(item)

                print()
                print("-" * 70)
                print("🔥 INLINE SCRIPT HIT")
                print("INDEX:", i)
                print("SRC:", src)

                position = text.find("pibtnResult")

                start = max(
                    0,
                    position - 1500,
                )

                end = min(
                    len(text),
                    position + 3000,
                )

                print()
                print(text[start:end])

        print()
        print("=" * 70)
        print("🔥 外部JavaScript探索")
        print("=" * 70)

        js_urls = page.evaluate(
            """
            () => Array.from(
                document.scripts
            )
            .map(s => s.src)
            .filter(Boolean)
            """
        )

        print("外部JS数:", len(js_urls))

        for index, js_url in enumerate(js_urls):

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

            if "pibtnResult" not in text:
                continue

            position = text.find("pibtnResult")

            start = max(
                0,
                position - 3000,
            )

            end = min(
                len(text),
                position + 6000,
            )

            sample = text[start:end]

            item = {
                "index": index,
                "url": js_url,
                "sample": sample,
            }

            result["scripts"].append(item)

            print()
            print("-" * 70)
            print("🔥 EXTERNAL JS HIT")
            print("INDEX:", index)
            print("URL:", js_url)
            print()
            print(sample)

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                result,
                f,
                ensure_ascii=False,
                indent=2,
            )

        print()
        print("=" * 70)
        print("🔥 168テスト終了")
        print("=" * 70)
        print(
            "pibtnResult件数:",
            count,
        )
        print(
            "関連SCRIPT数:",
            len(result["scripts"]),
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