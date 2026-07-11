from playwright.sync_api import sync_playwright
import json
import os
import re
import time


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "172_jsj075_result_route.json"
)


def safe_json(response):
    try:
        return response.json()
    except Exception:
        return None


def walk(obj, path="ROOT"):
    if isinstance(obj, dict):
        yield path, obj

        for key, value in obj.items():
            new_path = f"{path}.{key}"
            yield from walk(value, new_path)

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            new_path = f"{path}[{index}]"
            yield from walk(value, new_path)


def main():

    print("=" * 70)
    print("🔥 172 JSJ075 → 競走結果ルート直接取得")
    print("=" * 70)

    captured = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            channel="msedge",
            headless=False
        )

        context = browser.new_context()

        page = context.new_page()

        # --------------------------------------------------
        # RESPONSE監視
        # --------------------------------------------------

        def on_response(response):

            url = response.url

            if "type=JSJ075" not in url:
                return

            print()
            print("🔥 JSJ075 RESPONSE発見！")
            print("URL:", url)
            print("STATUS:", response.status)

            data = safe_json(response)

            if data is None:
                print("⚠ JSON解析失敗")
                return

            captured.append({
                "url": url,
                "data": data
            })

            print()
            print("🔥 JSJ075 生JSON")
            print("=" * 70)

            print(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2
                )
            )

            print("=" * 70)

            if isinstance(data, dict):

                print()
                print("🔥 RESULT ROUTE")
                print("=" * 70)

                print(
                    "raceBasicURL:",
                    data.get("raceBasicURL")
                )

                print(
                    "encPrm:",
                    data.get("encPrm")
                )

                print(
                    "btnResultFlag:",
                    data.get("btnResultFlag")
                )

                print(
                    "jyoName:",
                    data.get("jyoName")
                )

                print(
                    "kaisaihi:",
                    data.get("kaisaihi")
                )

                print(
                    "raceNo:",
                    data.get("raceNo")
                )

                print("=" * 70)

        page.on("response", on_response)

        # --------------------------------------------------
        # KEIRIN.JP
        # --------------------------------------------------

        print()
        print("🔥 Edge起動")

        page.goto(
            "https://www.keirin.jp/",
            wait_until="domcontentloaded",
            timeout=120000
        )

        print()
        print("=" * 70)
        print("🔥 手動準備")
        print("=" * 70)

        print("155成功時と同じ開催場・レース一覧画面へ移動")
        print("画面が見えたらEnter")
        print()

        input("準備できたらEnter：")

        # --------------------------------------------------
        # ページ遷移完全停止待ち
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 ページ安定待機")
        print("=" * 70)

        try:
            page.wait_for_load_state(
                "domcontentloaded",
                timeout=30000
            )

            print("DOM CONTENT LOADED")

        except Exception as e:

            print(
                "⚠ DOM待機TIMEOUT:",
                repr(e)
            )

        try:
            page.wait_for_load_state(
                "networkidle",
                timeout=30000
            )

            print("NETWORK IDLE")

        except Exception as e:

            print(
                "⚠ NETWORK IDLE待機TIMEOUT:",
                repr(e)
            )

        print("🔥 追加安定待機 5秒")

        time.sleep(5)

        # --------------------------------------------------
        # piInitialize発火候補探索
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 piInitialize発火候補探索")
        print("=" * 70)

        candidates = None

        for retry in range(10):

            try:

                print(
                    f"🔥 DOM探索 TRY "
                    f"{retry + 1} / 10"
                )

                candidates = page.evaluate(
                    """
                    () => {

                        const result = [];

                        const all =
                            document.querySelectorAll("*");

                        for (
                            let i = 0;
                            i < all.length;
                            i++
                        ) {

                            const el = all[i];

                            const onclick =
                                el.getAttribute(
                                    "onclick"
                                ) || "";

                            if (
                                onclick.includes(
                                    "piInitialize"
                                ) ||
                                onclick.includes(
                                    "rbTyokinResultClick"
                                )
                            ) {

                                result.push({
                                    index: i,

                                    tag:
                                        el.tagName,

                                    id:
                                        el.id || "",

                                    className:
                                        typeof el.className
                                        === "string"
                                            ? el.className
                                            : "",

                                    text:
                                        (
                                            el.innerText || ""
                                        )
                                        .trim()
                                        .substring(
                                            0,
                                            300
                                        ),

                                    onclick:
                                        onclick
                                });
                            }
                        }

                        return result;
                    }
                    """
                )

                print("🔥 DOM探索成功")

                break

            except Exception as e:

                print(
                    "⚠ DOM探索ERROR:",
                    repr(e)
                )

                print(
                    "🔥 ページ遷移終了待ち 3秒"
                )

                time.sleep(3)

        if candidates is None:

            print()
            print(
                "❌ DOM探索10回失敗"
            )

            candidates = []
            """
            () => {

                const result = [];

                const all = document.querySelectorAll("*");

                for (let i = 0; i < all.length; i++) {

                    const el = all[i];

                    const onclick =
                        el.getAttribute("onclick") || "";

                    if (
                        onclick.includes("piInitialize") ||
                        onclick.includes("rbTyokinResultClick")
                    ) {

                        result.push({
                            index: i,
                            tag: el.tagName,
                            id: el.id || "",
                            className:
                                typeof el.className === "string"
                                    ? el.className
                                    : "",
                            text:
                                (el.innerText || "")
                                .trim()
                                .substring(0, 300),
                            onclick: onclick
                        });
                    }
                }

                return result;
            }
            """

        print("候補数:", len(candidates))

        for i, item in enumerate(candidates):

            print()
            print("-" * 70)

            print("🔥 CANDIDATE", i)

            print("TAG:", item["tag"])
            print("ID:", item["id"])
            print("CLASS:", item["className"])
            print("TEXT:", item["text"])
            print("ONCLICK:", item["onclick"])

        # --------------------------------------------------
        # encp候補抽出
        # --------------------------------------------------

        encp_candidates = []

        for item in candidates:

            onclick = item.get("onclick", "")

            patterns = [
                r"rbTyokinResultClick\\(['\"]([^'\"]+)['\"]\\)",
                r"piInitialize\\(['\"]([^'\"]+)['\"]"
            ]

            for pattern in patterns:

                match = re.search(
                    pattern,
                    onclick
                )

                if match:

                    encp = match.group(1)

                    if encp not in encp_candidates:
                        encp_candidates.append(encp)

        print()
        print("=" * 70)
        print("🔥 ENCP候補")
        print("=" * 70)

        print("ENCP候補数:", len(encp_candidates))

        for i, encp in enumerate(encp_candidates):

            print(
                f"{i + 1}:",
                encp
            )

        # --------------------------------------------------
        # piInitialize直接発火
        # --------------------------------------------------

        print()
        print("=" * 70)
        print("🔥 piInitialize直接発火")
        print("=" * 70)

        for index, encp in enumerate(encp_candidates):

            print()
            print(
                f"🔥 発火 {index + 1} / "
                f"{len(encp_candidates)}"
            )

            print("ENCP:", encp)

            try:

                result = page.evaluate(
                    """
                    (encp) => {

                        if (
                            typeof window.piInitialize
                            !== "function"
                        ) {
                            return {
                                success: false,
                                error:
                                    "piInitializeなし"
                            };
                        }

                        window.piInitialize(encp);

                        return {
                            success: true
                        };
                    }
                    """,
                    encp
                )

                print(
                    "発火結果:",
                    result
                )

                time.sleep(1)

            except Exception as e:

                print(
                    "⚠ 発火ERROR:",
                    repr(e)
                )

        # --------------------------------------------------
        # 追加待機
        # --------------------------------------------------

        print()
        print("🔥 RESPONSE待機 10秒")

        time.sleep(10)

        # --------------------------------------------------
        # JSJ075から結果POST情報抽出
        # --------------------------------------------------

        result_routes = []

        print()
        print("=" * 70)
        print("🔥 競走結果POSTルート抽出")
        print("=" * 70)

        for item in captured:

            data = item["data"]

            if not isinstance(data, dict):
                continue

            race_basic_url = data.get(
                "raceBasicURL"
            )

            enc_prm = data.get(
                "encPrm"
            )

            btn_result_flag = data.get(
                "btnResultFlag"
            )

            if (
                race_basic_url
                and enc_prm
            ):

                route = {
                    "jyoName":
                        data.get("jyoName"),

                    "kaisaihi":
                        data.get("kaisaihi"),

                    "raceNo":
                        data.get("raceNo"),

                    "btnResultFlag":
                        btn_result_flag,

                    "raceBasicURL":
                        race_basic_url,

                    "encPrm":
                        enc_prm,

                    "post_data": {
                        "disp": "PJ0326",
                        "encp": enc_prm
                    }
                }

                result_routes.append(route)

                print()
                print("🔥 RESULT ROUTE発見")

                print(
                    json.dumps(
                        route,
                        ensure_ascii=False,
                        indent=2
                    )
                )

        # --------------------------------------------------
        # 保存
        # --------------------------------------------------

        output = {
            "jsj075_count":
                len(captured),

            "encp_candidate_count":
                len(encp_candidates),

            "result_route_count":
                len(result_routes),

            "encp_candidates":
                encp_candidates,

            "result_routes":
                result_routes,

            "jsj075":
                captured
        }

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                output,
                f,
                ensure_ascii=False,
                indent=2
            )

        print()
        print("=" * 70)
        print("🔥 172テスト終了")
        print("=" * 70)

        print(
            "JSJ075取得数:",
            len(captured)
        )

        print(
            "ENCP候補数:",
            len(encp_candidates)
        )

        print(
            "🔥 RESULT ROUTE取得数:",
            len(result_routes)
        )

        print()
        print(
            "保存先:",
            os.path.basename(
                OUTPUT_FILE
            )
        )

        print("=" * 70)

        input("確認できたらEnter：")

        browser.close()


if __name__ == "__main__":
    main()