from playwright.sync_api import sync_playwright
import json
import os
import re
from urllib.parse import urlparse


OUTPUT_JSON = "152_network_json_inventory.json"

# 今まで成功している奈良7R
TARGET_DATE = "20260703"
TARGET_JO_CODE = "53"
TARGET_RACE_NO = "7"


def safe_filename(text):
    text = re.sub(r"https?://", "", text)
    text = re.sub(r"[^0-9a-zA-Zぁ-んァ-ヶ一-龠._-]+", "_", text)
    return text[:180]


def short_value(value, limit=500):
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


def inspect_json_shape(data):
    result = {
        "root_type": type(data).__name__,
        "root_keys": [],
        "list_length": None,
        "sample": None,
    }

    if isinstance(data, dict):
        result["root_keys"] = list(data.keys())
        result["sample"] = short_value(data, 1000)

    elif isinstance(data, list):
        result["list_length"] = len(data)

        if data:
            result["sample"] = short_value(data[0], 1000)

    else:
        result["sample"] = short_value(data, 1000)

    return result


def main():

    print("=" * 70)
    print("🔥 152 全JSON/API通信探索")
    print("=" * 70)

    inventory = []
    response_no = 0

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
                content_type = response.headers.get(
                    "content-type",
                    ""
                ).lower()

                url = response.url

                # JSONらしい通信だけ対象
                is_json = (
                    "application/json" in content_type
                    or "text/json" in content_type
                    or ".json" in url.lower()
                    or "jsj" in url.lower()
                )

                if not is_json:
                    return

                response_no += 1

                print()
                print("-" * 70)
                print(f"🔥 JSON RESPONSE #{response_no}")
                print(f"STATUS : {response.status}")
                print(f"URL    : {url}")
                print(f"TYPE   : {content_type}")

                item = {
                    "no": response_no,
                    "status": response.status,
                    "url": url,
                    "content_type": content_type,
                    "method": response.request.method,
                    "post_data": response.request.post_data,
                    "json_ok": False,
                    "root_type": None,
                    "root_keys": [],
                    "list_length": None,
                    "sample": None,
                    "body_length": None,
                }

                try:
                    body = response.body()

                    item["body_length"] = len(body)

                    print(f"SIZE   : {len(body)} bytes")

                except Exception as e:

                    print(f"⚠ BODY取得失敗: {e}")

                    inventory.append(item)

                    return

                try:
                    data = response.json()

                    item["json_ok"] = True

                    shape = inspect_json_shape(data)

                    item["root_type"] = shape["root_type"]
                    item["root_keys"] = shape["root_keys"]
                    item["list_length"] = shape["list_length"]
                    item["sample"] = shape["sample"]

                    print(f"ROOT   : {shape['root_type']}")

                    if shape["root_keys"]:

                        print(
                            "KEYS   : "
                            + ", ".join(
                                str(x)
                                for x in shape["root_keys"][:50]
                            )
                        )

                    if shape["list_length"] is not None:

                        print(
                            f"LIST件数: {shape['list_length']}"
                        )

                    print()
                    print("🔥 SAMPLE")
                    print(shape["sample"])

                except Exception as e:

                    print(f"JSON解析失敗: {e}")

                    try:
                        text = response.text()

                        item["sample"] = text[:1000]

                        print()
                        print("🔥 TEXT SAMPLE")
                        print(text[:1000])

                    except Exception:
                        pass

                inventory.append(item)

            except Exception as e:

                print(f"⚠ RESPONSE解析エラー: {e}")

        page.on("response", handle_response)

        print()
        print("🔥 競輪JPを開く")

        # まずトップ
        page.goto(
            "https://keirin.jp/",
            wait_until="domcontentloaded",
            timeout=120000
        )

        page.wait_for_timeout(5000)

        print()
        print("🔥 奈良7R対象ページ探索")

        # 今まで取得に使った開催日・場・RをURL候補として探索
        target_urls = [
            (
                "https://keirin.jp/pc/race/"
                f"?kaisai_date={TARGET_DATE}"
                f"&jo_code={TARGET_JO_CODE}"
                f"&race_no={TARGET_RACE_NO}"
            ),
            (
                "https://keirin.jp/pc/race/raceresult"
                f"?kaisai_date={TARGET_DATE}"
                f"&jo_code={TARGET_JO_CODE}"
                f"&race_no={TARGET_RACE_NO}"
            ),
        ]

        for i, target_url in enumerate(target_urls, 1):

            print()
            print("=" * 70)
            print(f"🔥 URL候補 #{i}")
            print(target_url)
            print("=" * 70)

            try:

                page.goto(
                    target_url,
                    wait_until="domcontentloaded",
                    timeout=120000
                )

                page.wait_for_timeout(10000)

                print(f"TITLE: {page.title()}")
                print(f"FINAL URL: {page.url}")

            except Exception as e:

                print(f"⚠ PAGE ERROR: {e}")

        print()
        print("🔥 追加待機 15秒")
        print("🔥 Edge画面で奈良7Rの出走表・予想ページを開いてOK")

        page.wait_for_timeout(15000)

        browser.close()

    # 重複URL集計
    url_summary = {}

    for item in inventory:

        url = item["url"]

        if url not in url_summary:

            url_summary[url] = {
                "count": 0,
                "status": item["status"],
                "content_type": item["content_type"],
                "body_length": item["body_length"],
                "root_type": item["root_type"],
                "root_keys": item["root_keys"],
            }

        url_summary[url]["count"] += 1

    output = {
        "target": {
            "date": TARGET_DATE,
            "jo_code": TARGET_JO_CODE,
            "race_no": TARGET_RACE_NO,
        },
        "response_count": len(inventory),
        "unique_url_count": len(url_summary),
        "responses": inventory,
        "url_summary": url_summary,
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
    print("🔥 152テスト終了")
    print("=" * 70)
    print(f"JSON/API RESPONSE数: {len(inventory)}")
    print(f"重複除外URL数: {len(url_summary)}")

    print()
    print("🔥 JSON/API URL一覧")

    for no, (url, info) in enumerate(
        url_summary.items(),
        1
    ):

        print()
        print("-" * 70)
        print(f"🔥 API #{no}")
        print(f"COUNT : {info['count']}")
        print(f"SIZE  : {info['body_length']}")
        print(f"ROOT  : {info['root_type']}")

        if info["root_keys"]:

            print(
                "KEYS  : "
                + ", ".join(
                    str(x)
                    for x in info["root_keys"][:30]
                )
            )

        print(f"URL   : {url}")

    print()
    print(f"保存先: {OUTPUT_JSON}")
    print("=" * 70)


if __name__ == "__main__":
    main()