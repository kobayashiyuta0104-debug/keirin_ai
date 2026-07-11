from playwright.sync_api import sync_playwright
import json
import time


OUTPUT_FILE = "173_pibtnresult_event_hunt.json"


def main():

    print("=" * 70)
    print("🔥 173 pibtnResult jQuery EVENT完全調査")
    print("=" * 70)

    result = {
        "jquery": {},
        "button": {},
        "jquery_events": [],
        "native_properties": {},
        "script_hits": [],
    }

    with sync_playwright() as p:

        browser = p.chromium.launch(
            channel="msedge",
            headless=False,
        )

        page = browser.new_page()

        print()
        print("🔥 Edge起動")
        print("🔥 KEIRIN.JPを開く")

        page.goto(
            "https://keirin.jp/",
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print()
        print("=" * 70)
        print("🔥 手動準備")
        print("=" * 70)
        print("155成功時と同じ開催場・レース一覧画面へ移動")
        print("画面が完全表示されたらEnter")
        input()

        try:
            page.wait_for_load_state(
                "domcontentloaded",
                timeout=30000,
            )
        except Exception:
            pass

        time.sleep(5)

        print()
        print("=" * 70)
        print("🔥 jQuery確認")
        print("=" * 70)

        jquery_info = page.evaluate(
            """
            () => {
                return {
                    exists:
                        typeof window.jQuery !== "undefined",

                    dollarExists:
                        typeof window.$ !== "undefined",

                    version:
                        typeof window.jQuery !== "undefined"
                            ? window.jQuery.fn.jquery
                            : null,

                    hasData:
                        typeof window.jQuery !== "undefined"
                            ? typeof window.jQuery._data
                            : null
                };
            }
            """
        )

        result["jquery"] = jquery_info

        print(
            json.dumps(
                jquery_info,
                ensure_ascii=False,
                indent=2,
            )
        )

        print()
        print("=" * 70)
        print("🔥 pibtnResult確認")
        print("=" * 70)

        button_info = page.evaluate(
            """
            () => {

                const el =
                    document.getElementById(
                        "pibtnResult"
                    );

                if (!el) {
                    return {
                        exists: false
                    };
                }

                return {
                    exists: true,
                    tag: el.tagName,
                    id: el.id,
                    text:
                        (el.innerText || "").trim(),
                    className:
                        el.className || "",
                    onclickAttribute:
                        el.getAttribute("onclick"),
                    onclickProperty:
                        el.onclick
                            ? el.onclick.toString()
                            : null,
                    outerHTML:
                        el.outerHTML
                };
            }
            """
        )

        result["button"] = button_info

        print(
            json.dumps(
                button_info,
                ensure_ascii=False,
                indent=2,
            )
        )

        print()
        print("=" * 70)
        print("🔥 jQuery EVENT抽出")
        print("=" * 70)

        jquery_events = page.evaluate(
            """
            () => {

                const output = [];

                const el =
                    document.getElementById(
                        "pibtnResult"
                    );

                if (!el) {
                    return output;
                }

                if (
                    typeof window.jQuery ===
                    "undefined"
                ) {
                    return output;
                }

                if (
                    typeof window.jQuery._data !==
                    "function"
                ) {
                    return output;
                }

                const events =
                    window.jQuery._data(
                        el,
                        "events"
                    ) || {};

                for (
                    const eventType
                    of Object.keys(events)
                ) {

                    const handlers =
                        events[eventType] || [];

                    for (
                        let i = 0;
                        i < handlers.length;
                        i++
                    ) {

                        const item = handlers[i];

                        output.push({
                            eventType:
                                eventType,

                            index:
                                i,

                            guid:
                                item.guid || null,

                            namespace:
                                item.namespace || "",

                            selector:
                                item.selector || null,

                            origType:
                                item.origType || null,

                            handler:
                                item.handler
                                    ? item.handler.toString()
                                    : null
                        });
                    }
                }

                return output;
            }
            """
        )

        result["jquery_events"] = jquery_events

        print(
            "🔥 jQuery EVENT数:",
            len(jquery_events),
        )

        for i, event in enumerate(
            jquery_events
        ):

            print()
            print("-" * 70)
            print(
                f"🔥 EVENT #{i + 1}"
            )
            print(
                json.dumps(
                    event,
                    ensure_ascii=False,
                    indent=2,
                )
            )

        print()
        print("=" * 70)
        print("🔥 native EVENT PROPERTY探索")
        print("=" * 70)

        native_properties = page.evaluate(
            """
            () => {

                const el =
                    document.getElementById(
                        "pibtnResult"
                    );

                if (!el) {
                    return {};
                }

                const result = {};

                const props = [
                    "onclick",
                    "onmousedown",
                    "onmouseup",
                    "onpointerdown",
                    "onpointerup",
                    "ontouchstart",
                    "ontouchend",
                    "onkeydown",
                    "onkeyup"
                ];

                for (const key of props) {

                    try {

                        const value = el[key];

                        if (value) {

                            result[key] =
                                value.toString();
                        }

                    } catch (e) {

                        result[key] =
                            "ERROR: " + e.toString();
                    }
                }

                return result;
            }
            """
        )

        result[
            "native_properties"
        ] = native_properties

        print(
            json.dumps(
                native_properties,
                ensure_ascii=False,
                indent=2,
            )
        )

        print()
        print("=" * 70)
        print("🔥 SCRIPT内 pibtnResult探索")
        print("=" * 70)

        script_hits = page.evaluate(
            """
            async () => {

                const output = [];

                const scripts =
                    Array.from(
                        document.scripts
                    );

                for (
                    let i = 0;
                    i < scripts.length;
                    i++
                ) {

                    const script = scripts[i];

                    let text = "";

                    try {

                        if (script.src) {

                            const response =
                                await fetch(
                                    script.src
                                );

                            text =
                                await response.text();

                        } else {

                            text =
                                script.textContent || "";
                        }

                    } catch (e) {

                        continue;
                    }

                    const keywords = [
                        "pibtnResult",
                        "piInitialize",
                        "rbTyokinResultClick",
                        "JSJ075"
                    ];

                    for (
                        const keyword
                        of keywords
                    ) {

                        const index =
                            text.indexOf(keyword);

                        if (index === -1) {
                            continue;
                        }

                        output.push({
                            scriptIndex:
                                i,

                            src:
                                script.src || "INLINE",

                            keyword:
                                keyword,

                            index:
                                index,

                            sample:
                                text.substring(
                                    Math.max(
                                        0,
                                        index - 1000
                                    ),
                                    Math.min(
                                        text.length,
                                        index + 2000
                                    )
                                )
                        });
                    }
                }

                return output;
            }
            """
        )

        result["script_hits"] = script_hits

        print(
            "🔥 SCRIPT HIT数:",
            len(script_hits),
        )

        for i, hit in enumerate(
            script_hits
        ):

            print()
            print("-" * 70)
            print(
                f"🔥 SCRIPT HIT #{i + 1}"
            )
            print("SRC:", hit["src"])
            print(
                "KEYWORD:",
                hit["keyword"],
            )
            print()
            print(hit["sample"])

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
        print("🔥 173テスト終了")
        print("=" * 70)
        print(
            "jQuery EVENT数:",
            len(jquery_events),
        )
        print(
            "SCRIPT HIT数:",
            len(script_hits),
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