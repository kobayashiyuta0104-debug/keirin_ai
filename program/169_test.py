import json
import time

from playwright.sync_api import sync_playwright


OUTPUT_FILE = "169_pj9110_result_route.json"

KEIRIN_URL = "https://www.keirin.jp/pc/top"


def main():

    print("=" * 70)
    print("🔥 169 PJ9110 → 競走結果POSTルート捕獲")
    print("=" * 70)

    hits = []

    with sync_playwright() as p:

        print()
        print("🔥 Edge起動")

        browser = p.chromium.launch(
            channel="msedge",
            headless=False,
        )

        context = browser.new_context()

        page = context.new_page()

        def on_response(response):

            try:

                content_type = (
                    response.headers.get(
                        "content-type",
                        ""
                    )
                    .lower()
                )

                if (
                    "json" not in content_type
                    and "javascript" not in content_type
                    and "text" not in content_type
                ):
                    return

                text = response.text()

            except Exception:
                return

            if (
                "raceBasicURL" not in text
                and "encPrm" not in text
                and "btnResultFlag" not in text
            ):
                return

            print()
            print("=" * 70)
            print("🔥 PJ9110候補通信発見")
            print("=" * 70)
            print("STATUS:", response.status)
            print("URL:", response.url)
            print("TYPE:", content_type)
            print("SIZE:", len(text))

            try:

                data = json.loads(text)

            except Exception:

                print()
                print("⚠ JSON解析失敗")

                return

            def walk(obj, path="ROOT"):

                if isinstance(obj, dict):

                    if (
                        "raceBasicURL" in obj
                        or "encPrm" in obj
                        or "btnResultFlag" in obj
                    ):

                        item = {
                            "path": path,
                            "response_url": response.url,
                            "raceBasicURL":
                                obj.get("raceBasicURL"),
                            "encPrm":
                                obj.get("encPrm"),
                            "btnResultFlag":
                                obj.get("btnResultFlag"),
                            "raceNo":
                                obj.get("raceNo"),
                            "jyoName":
                                obj.get("jyoName"),
                            "kaisaihi":
                                obj.get("kaisaihi"),
                            "prmJyoCd":
                                obj.get("prmJyoCd"),
                            "prmKaisaihi":
                                obj.get("prmKaisaihi"),
                            "raw": obj,
                        }

                        hits.append(item)

                        print()
                        print("-" * 70)
                        print("🔥 RESULT ROUTE")
                        print("PATH:", path)
                        print(
                            "jyoName:",
                            item["jyoName"],
                        )
                        print(
                            "raceNo:",
                            item["raceNo"],
                        )
                        print(
                            "kaisaihi:",
                            item["kaisaihi"],
                        )
                        print(
                            "btnResultFlag:",
                            item["btnResultFlag"],
                        )
                        print(
                            "raceBasicURL:",
                            item["raceBasicURL"],
                        )
                        print(
                            "encPrm:",
                            item["encPrm"],
                        )

                    for key, value in obj.items():

                        walk(
                            value,
                            f"{path}.{key}",
                        )

                elif isinstance(obj, list):

                    for index, value in enumerate(obj):

                        walk(
                            value,
                            f"{path}[{index}]",
                        )

            walk(data)

        page.on(
            "response",
            on_response,
        )

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

        print()
        print("🔥 30秒通信監視")
        print("画面は触らなくてOK")

        time.sleep(30)

        unique = []

        seen = set()

        for item in hits:

            key = (
                str(item.get("raceBasicURL")),
                str(item.get("encPrm")),
            )

            if key in seen:
                continue

            seen.add(key)

            unique.append(item)

        print()
        print("=" * 70)
        print("🔥 捕獲結果")
        print("=" * 70)

        for index, item in enumerate(
            unique,
            start=1,
        ):

            print()
            print("-" * 70)
            print(
                f"🔥 ROUTE #{index}"
            )
            print(
                "開催場:",
                item.get("jyoName"),
            )
            print(
                "RACE:",
                item.get("raceNo"),
            )
            print(
                "開催日:",
                item.get("kaisaihi"),
            )
            print(
                "結果FLAG:",
                item.get("btnResultFlag"),
            )
            print(
                "POST URL:",
                item.get("raceBasicURL"),
            )
            print(
                "disp: PJ0326"
            )
            print(
                "encp:",
                item.get("encPrm"),
            )

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                unique,
                f,
                ensure_ascii=False,
                indent=2,
            )

        print()
        print("=" * 70)
        print("🔥 169テスト終了")
        print("=" * 70)
        print(
            "PJ9110候補数:",
            len(hits),
        )
        print(
            "ユニーク結果ルート数:",
            len(unique),
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