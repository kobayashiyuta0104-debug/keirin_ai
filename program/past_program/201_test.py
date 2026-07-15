import json
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright

print("=== 201 過去レース通信 待機付き全JSON監視テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "201_historical_json_route_capture.json"

captures = []
seen = set()


def get_type(url):
    try:
        return parse_qs(urlparse(url).query).get("type", [None])[0]
    except Exception:
        return None


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        channel="msedge",
    )
    page = browser.new_page()

    def on_response(response):
        url = response.url
        if "/pc/json" not in url:
            return

        req = response.request
        key = (req.method, url, req.post_data or "")
        if key in seen:
            return
        seen.add(key)

        try:
            data = response.json()
        except Exception:
            data = None

        item = {
            "method": req.method,
            "url": url,
            "type": get_type(url),
            "post_data": req.post_data,
            "status": response.status,
            "json_top_keys": list(data.keys()) if isinstance(data, dict) else None,
            "data": data,
        }
        captures.append(item)

        print()
        print("🔥 JSON通信捕獲")
        print(f"TYPE: {item['type']}")
        print(f"STATUS: {item['status']}")
        print(f"URL: {url}")
        print(f"TOP KEYS: {item['json_top_keys']}")

    page.on("response", on_response)

    print()
    print("Edgeを開きます。")
    print("結果確定済みの過去レースを1レース表示してください。")
    print("出走表または競走結果が表示されたらターミナルへ戻って Enter。")
    print()
    print("Enter後も15秒間通信を監視します。")
    print("15秒待って自動で保存するので、途中で閉じないでください。")
    print()

    page.goto("https://www.keirin.jp/pc/top")
    input(">>> 過去レース表示後に Enter: ")

    print()
    print("⏳ 15秒間、残りの通信を監視中...")
    for sec in range(15, 0, -1):
        print(f"  残り {sec} 秒", end="\r", flush=True)
        page.wait_for_timeout(1000)
    print(" " * 40, end="\r")

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "capture_count": len(captures),
                "captures": captures,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    type_counts = {}
    for item in captures:
        label = item["type"] or "TYPE_NONE"
        type_counts[label] = type_counts.get(label, 0) + 1

    print()
    print("=== 201 結果 ===")
    print(f"JSON通信捕獲数: {len(captures)}")
    for label, count in sorted(type_counts.items()):
        print(f"{label}: {count}件")

    print()
    print("=== 捕獲通信一覧 ===")
    for i, item in enumerate(captures, 1):
        print(f"[{i}] type={item['type']} / status={item['status']}")
        print(f"    URL: {item['url']}")
        print(f"    TOP KEYS: {item['json_top_keys']}")

    print()
    print(f"保存完了: {OUTPUT_FILE}")
    print("=== 201 完了 ===")

    browser.close()
