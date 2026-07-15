import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright

print("=== 205 過去レース手動遷移 DOCUMENT + JSON完全捕獲テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "205_manual_historical_navigation_capture.json"

captures = []

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=False)
    context = browser.new_context()
    page = context.new_page()

    def on_request(request):
        url = request.url
        if "keirin.jp" not in url:
            return

        resource_type = request.resource_type
        if resource_type == "document" or "/pc/json" in url:
            q = parse_qs(urlparse(url).query)
            rec = {
                "kind": "REQUEST",
                "resource_type": resource_type,
                "method": request.method,
                "url": url,
                "type": (q.get("type") or [None])[0],
                "encp": (q.get("encp") or [None])[0],
                "kday": (q.get("kday") or [None])[0],
                "post_data": request.post_data,
            }
            captures.append(rec)
            print()
            print("🔥 REQUEST")
            print(f"RESOURCE: {resource_type}")
            print(f"METHOD: {request.method}")
            print(f"URL: {url}")
            print(f"TYPE: {rec['type']}")
            print(f"ENCP: {rec['encp']}")
            print(f"KDAY: {rec['kday']}")
            print(f"POST: {rec['post_data']}")

    def on_response(response):
        url = response.url
        if "/pc/json" not in url:
            return

        q = parse_qs(urlparse(url).query)
        try:
            data = response.json()
        except Exception:
            data = None

        rec = {
            "kind": "RESPONSE",
            "status": response.status,
            "url": url,
            "type": (q.get("type") or [None])[0],
            "encp": (q.get("encp") or [None])[0],
            "kday": (q.get("kday") or [None])[0],
            "top_keys": list(data.keys()) if isinstance(data, dict) else None,
            "data": data,
        }
        captures.append(rec)

    page.on("request", on_request)
    page.on("response", on_response)

    page.goto("https://www.keirin.jp/pc/", wait_until="domcontentloaded", timeout=60000)

    print()
    print("Edgeで手動操作してください。")
    print("1. 2026/07/06 の過去開催を表示")
    print("2. どれか1開催を開く")
    print("3. どれか1レースの出走表または結果画面まで移動")
    print("4. 画面が表示されたらターミナルへ戻って Enter")
    input(">>> 過去レース表示後に Enter: ")

    page.wait_for_timeout(5000)

    final_url = page.url
    title = page.title()

    browser.close()

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump({
        "final_url": final_url,
        "page_title": title,
        "capture_count": len(captures),
        "captures": captures,
    }, f, ensure_ascii=False, indent=2)

docs = [x for x in captures if x.get("kind") == "REQUEST" and x.get("resource_type") == "document"]
json_reqs = [x for x in captures if x.get("kind") == "REQUEST" and "/pc/json" in x.get("url", "")]

print()
print("=== 205 結果 ===")
print(f"最終URL: {final_url}")
print(f"DOCUMENT遷移数: {len(docs)}")
print(f"JSON REQUEST数: {len(json_reqs)}")

print()
print("=== DOCUMENT遷移一覧 ===")
for i, x in enumerate(docs, 1):
    print(f"[{i}] {x['method']} {x['url']}")
    print(f"    POST: {x['post_data']}")

print()
print("=== JSON REQUEST一覧 ===")
for i, x in enumerate(json_reqs, 1):
    print(
        f"[{i}] type={x.get('type')} / encp={x.get('encp')} "
        f"/ kday={x.get('kday')} / method={x.get('method')}"
    )
    print(f"    URL: {x.get('url')}")
    print(f"    POST: {x.get('post_data')}")

print()
print(f"保存完了: {OUTPUT_FILE}")
print("=== 205 完了 ===")
