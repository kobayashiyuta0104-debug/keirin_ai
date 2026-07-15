from playwright.sync_api import sync_playwright
import json


OUTPUT_JSON = "154_auto_venue_network_inventory.json"


def short_text(value, limit=2000):
    try:
        text = json.dumps(
            value,
            ensure_ascii=False,
            default=str
        )
    except Exception:
        text = str(value)

    if len(text) > limit:
        return text[:limit] + "..."

    return text


def main():

    print("=" * 70)
    print("🔥 154 今日開催場 自動選択 + 全XHR/FETCH探索")
    print("=" * 70)

    responses = []
    response_no = 0

    selected_venue = None
    selected_race = None

    with sync_playwright() as p:

        print("🔥 Edge起動")

        browser = p.chromium.launch(
            channel="msedge",
            headless=False
        )

        context = browser.new_context()

        page = context.new_page()

        def handle_response(response):

            nonlocal response_no

            try:

                request = response.request
                resource_type = request.resource_type

                if resource_type not in ["xhr", "fetch"]:
                    return

                response_no += 1

                url = response.url

                item = {
                    "no": response_no,
                    "resource_type": resource_type,
                    "method": request.method,
                    "status": response.status,
                    "url": url,
                    "post_data": request.post_data,
                    "content_type": response.headers.get(
                        "content-type",
                        ""
                    ),
                    "body_length": None,
                    "json_ok": False,
                    "root_type": None,
                    "root_keys": [],
                    "sample": None,
                }

                print()
                print("-" * 70)
                print(f"🔥 XHR/FETCH #{response_no}")
                print(f"TYPE   : {resource_type}")
                print(f"METHOD : {request.method}")
                print(f"STATUS : {response.status}")
                print(f"URL    : {url}")

                try:

                    body = response.body()

                    item["body_length"] = len(body)

                    print(
                        f"SIZE   : {len(body)} bytes"
                    )

                except Exception as e:

                    print(
                        f"⚠ BODY取得失敗: {e}"
                    )

                    responses.append(item)

                    return

                try:

                    data = response.json()

                    item["json_ok"] = True
                    item["root_type"] = type(
                        data
                    ).__name__

                    if isinstance(data, dict):

                        item["root_keys"] = list(
                            data.keys()
                        )

                    elif isinstance(data, list):

                        item["root_keys"] = [
                            f"LIST_LENGTH={len(data)}"
                        ]

                    item["sample"] = short_text(
                        data
                    )

                    print(
                        f"JSON   : OK / {item['root_type']}"
                    )

                    if item["root_keys"]:

                        print(
                            "KEYS   : "
                            + ", ".join(
                                str(x)
                                for x in item[
                                    "root_keys"
                                ][:50]
                            )
                        )

                    print()
                    print("🔥 SAMPLE")
                    print(item["sample"])

                except Exception:

                    try:

                        text = response.text()

                        item["sample"] = text[:2000]

                        print("JSON   : NO")

                        print()
                        print("🔥 TEXT SAMPLE")
                        print(text[:2000])

                    except Exception as e:

                        print(
                            f"⚠ TEXT取得失敗: {e}"
                        )

                responses.append(item)

            except Exception as e:

                print(
                    f"⚠ RESPONSE解析エラー: {e}"
                )

        context.on(
            "response",
            handle_response
        )

        print()
        print("🔥 KEIRIN.JP TOPを開く")

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded",
            timeout=120000
        )

        page.wait_for_timeout(7000)

        print()
        print("=" * 70)
        print("🔥 開催場候補探索")
        print("=" * 70)

        venue_candidates = page.locator(
            "[onclick^='raKeirinjoClick']"
        )

        venue_count = venue_candidates.count()

        print(
            f"開催場候補数: {venue_count}"
        )

        venue_list = []

        for i in range(venue_count):

            locator = venue_candidates.nth(i)

            try:

                text = locator.inner_text().strip()

            except Exception:

                text = ""

            onclick = locator.get_attribute(
                "onclick"
            ) or ""

            venue_item = {
                "index": i,
                "text": text,
                "onclick": onclick,
            }

            venue_list.append(
                venue_item
            )

            print()
            print(
                f"🔥 VENUE #{i}"
            )
            print(
                f"TEXT    : {text}"
            )
            print(
                f"ONCLICK : {onclick}"
            )

        print()
        print("=" * 70)
        print("🔥 開催場 自動クリック開始")
        print("=" * 70)

        venue_clicked = False

        for venue_item in venue_list:

            i = venue_item["index"]

            try:

                locator = page.locator(
                    "[onclick^='raKeirinjoClick']"
                ).nth(i)

                if not locator.is_visible():
                    continue

                text = venue_item["text"]

                print()
                print(
                    f"🔥 開催場クリック試行 INDEX={i}"
                )
                print(
                    f"TEXT={text}"
                )

                locator.click(
                    timeout=10000
                )

                page.wait_for_timeout(7000)

                selected_venue = text

                print(
                    f"🔥 開催場クリック成功: {text}"
                )

                venue_clicked = True

                break

            except Exception as e:

                print(
                    f"⚠ クリック失敗 INDEX={i}: {e}"
                )

        if not venue_clicked:

            print()
            print("❌ 開催場クリック全失敗")

            browser.close()

            return

        print()
        print("=" * 70)
        print("🔥 レースボタン探索")
        print("=" * 70)

        race_buttons = []

        for race_no in range(1, 13):

            selector = f"#hhRaceBtn{race_no}"

            locator = page.locator(
                selector
            )

            count = locator.count()

            visible = False

            if count > 0:

                try:

                    visible = locator.first.is_visible()

                except Exception:

                    visible = False

            print(
                f"{race_no}R "
                f"COUNT={count} "
                f"VISIBLE={visible}"
            )

            if count > 0 and visible:

                race_buttons.append(
                    race_no
                )

        print()
        print(
            f"🔥 操作可能レース: {race_buttons}"
        )

        if not race_buttons:

            print()
            print("❌ 操作可能レース無し")

            browser.close()

            return

        # 7Rがあれば7R
        # 無ければ存在する最後のレース
        if 7 in race_buttons:

            selected_race = 7

        else:

            selected_race = race_buttons[-1]

        print()
        print(
            f"🔥 選択レース: {selected_race}R"
        )

        race_button = page.locator(
            f"#hhRaceBtn{selected_race}"
        ).first

        race_button.click(
            timeout=10000
        )

        print()
        print("🔥 レースクリック成功")

        print()
        print("🔥 通信待機 20秒")

        page.wait_for_timeout(20000)

        print()
        print("=" * 70)
        print("🔥 現在ページ")
        print("=" * 70)

        print(
            f"TITLE: {page.title()}"
        )

        print(
            f"URL  : {page.url}"
        )

        browser.close()

    unique_urls = {}

    for item in responses:

        url = item["url"]

        if url not in unique_urls:

            unique_urls[url] = {
                "count": 0,
                "resource_type": item[
                    "resource_type"
                ],
                "method": item["method"],
                "status": item["status"],
                "body_length": item[
                    "body_length"
                ],
                "json_ok": item["json_ok"],
                "root_type": item[
                    "root_type"
                ],
                "root_keys": item[
                    "root_keys"
                ],
                "sample": item["sample"],
            }

        unique_urls[url]["count"] += 1

    output = {
        "selected_venue": selected_venue,
        "selected_race": selected_race,
        "response_count": len(responses),
        "unique_url_count": len(
            unique_urls
        ),
        "responses": responses,
        "unique_urls": unique_urls,
    }

    with open(
        OUTPUT_JSON,
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
    print("🔥 154テスト終了")
    print("=" * 70)

    print(
        f"選択開催場: {selected_venue}"
    )

    print(
        f"選択レース: {selected_race}R"
    )

    print(
        f"XHR/FETCH総数: {len(responses)}"
    )

    print(
        f"重複除外URL数: {len(unique_urls)}"
    )

    print()
    print("🔥 UNIQUE通信一覧")

    for no, (
        url,
        info
    ) in enumerate(
        unique_urls.items(),
        1
    ):

        print()
        print("-" * 70)
        print(
            f"🔥 COMM #{no}"
        )

        print(
            f"TYPE   : {info['resource_type']}"
        )

        print(
            f"METHOD : {info['method']}"
        )

        print(
            f"STATUS : {info['status']}"
        )

        print(
            f"SIZE   : {info['body_length']}"
        )

        print(
            f"JSON   : {info['json_ok']}"
        )

        print(
            f"ROOT   : {info['root_type']}"
        )

        if info["root_keys"]:

            print(
                "KEYS   : "
                + ", ".join(
                    str(x)
                    for x in info[
                        "root_keys"
                    ][:50]
                )
            )

        print(
            f"URL    : {url}"
        )

        print()
        print("SAMPLE:")

        print(
            info["sample"]
        )

    print()
    print(
        f"保存先: {OUTPUT_JSON}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()