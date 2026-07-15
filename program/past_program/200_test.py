import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright

print("=== 200 過去レース取得ルート 通信監視テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "200_historical_route_capture.json"

WATCH_TYPES = {
    "JSJ006",
    "JSJ012",
    "JSJ075",
}

captures = []
seen = set()


def safe_json(response):
    try:
        return response.json()
    except Exception:
        return None


def get_type_from_url(url):
    try:
        qs = parse_qs(urlparse(url).query)
        values = qs.get("type", [])
        return values[0] if values else None
    except Exception:
        return None


def summarize_json(data):
    if not isinstance(data, dict):
        return {
            "top_level_type": type(data).__name__,
            "top_level_keys": None,
        }

    summary = {
        "top_level_type": "dict",
        "top_level_keys": list(data.keys()),
    }

    for key in [
        "raceBasicURL",
        "encPrm",
        "encp",
        "kkrParameter",
        "kkParameter",
        "lastUpdateTime",
    ]:
        if key in data:
            summary[key] = data.get(key)

    return summary


with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        channel="msedge",
    )

    page = browser.new_page()

    def on_response(response):
        url = response.url
        request = response.request

        req_type = get_type_from_url(url)
        url_lower = url.lower()

        interesting = (
            req_type in WATCH_TYPES
            or "pj0326" in url_lower
            or "racebasic" in url_lower
        )

        if not interesting:
            return

        key = (
            request.method,
            url,
            request.post_data or "",
        )

        if key in seen:
            return
        seen.add(key)

        data = safe_json(response)

        item = {
            "request_method": request.method,
            "request_url": url,
            "request_type": req_type,
            "request_post_data": request.post_data,
            "status": response.status,
            "response_json": data,
            "response_summary": summarize_json(data),
        }
        captures.append(item)

        print()
        print("🔥 通信捕獲")
        print(f"METHOD: {request.method}")
        print(f"TYPE: {req_type}")
        print(f"STATUS: {response.status}")
        print(f"URL: {url}")
        print(f"POST: {request.post_data}")
        if isinstance(data, dict):
            print(f"JSON TOP KEYS: {list(data.keys())}")
            for special_key in ["raceBasicURL", "encPrm", "encp"]:
                if special_key in data:
                    print(f"{special_key}: {data.get(special_key)}")

    page.on("response", on_response)

    print()
    print("Edgeを開きます。")
    print("KEIRIN.JPで『過去日のレース』を1レースだけ表示してください。")
    print("できれば結果が確定している過去日を選び、")
    print("そのレースの出走表が見える状態まで移動してください。")
    print()
    print("重要:")
    print("今回は自動巡回しません。")
    print("過去レースへ移動する時に発生する通信ルートだけを捕まえます。")
    print()
    print("操作が終わったら、このターミナルへ戻って Enter を押してください。")
    print()

    page.goto("https://www.keirin.jp/pc/top")

    input(">>> 過去レース表示後に Enter: ")

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump({
            "capture_count": len(captures),
            "captures": captures,
        }, f, ensure_ascii=False, indent=2)

    print()
    print("=== 200 結果 ===")
    print(f"通信捕獲数: {len(captures)}")

    type_counts = {}
    for item in captures:
        label = item.get("request_type")
        if label is None and "pj0326" in item.get("request_url", "").lower():
            label = "PJ0326"
        if label is None:
            label = "OTHER"
        type_counts[label] = type_counts.get(label, 0) + 1

    for label, count in sorted(type_counts.items()):
        print(f"{label}: {count}件")

    print()
    print("=== 捕獲通信一覧 ===")
    for i, item in enumerate(captures, start=1):
        print(
            f"[{i}] "
            f"{item.get('request_method')} / "
            f"type={item.get('request_type')} / "
            f"status={item.get('status')}"
        )
        print(f"    URL: {item.get('request_url')}")
        print(f"    POST: {item.get('request_post_data')}")
        print(f"    JSON TOP KEYS: {item.get('response_summary', {}).get('top_level_keys')}")

    print()
    print(f"保存完了: {OUTPUT_FILE}")
    print("=== 200 完了 ===")

    browser.close()
