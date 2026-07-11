import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright

print("=== 204 JSJ004 raceUrlPrm ブラウザ遷移通信捕獲テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "202_jsj004_historical_map_analysis.json"
OUTPUT_FILE = BASE_DIR / "204_raceurlprm_browser_route_capture.json"

with INPUT_FILE.open("r", encoding="utf-8") as f:
    raw = json.load(f)

items = raw.get("items", [])
if not items:
    raise RuntimeError("202解析データがありません")

kaisai_data = items[0].get("kaisaiData") or []
target = next((x for x in kaisai_data if x.get("bkname") == "豊橋"), None)
if not target:
    target = kaisai_data[0]

venue = target.get("bkname")
encp = target.get("raceUrlPrm")
target_url = f"https://www.keirin.jp/pc/racelive?encp={encp}"

print(f"対象開催: {venue}")
print(f"JSJ004 raceUrlPrm: {encp}")
print(f"遷移URL: {target_url}")
print()
print("Edgeが開きます。自動で上のURLへ移動します。")
print("画面が表示されたら30秒ほど待ってください。")
print("操作はしなくてOKです。")
print()

captures = []

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel="msedge",
        headless=False,
    )
    context = browser.new_context()
    page = context.new_page()

    def on_response(response):
        url = response.url
        if "keirin.jp/pc/json" not in url:
            return

        try:
            q = parse_qs(urlparse(url).query)
            typ = (q.get("type") or [None])[0]
            req_encp = (q.get("encp") or [None])[0]
            kday = (q.get("kday") or [None])[0]

            try:
                data = response.json()
            except Exception:
                data = None

            rec = {
                "type": typ,
                "status": response.status,
                "url": url,
                "encp": req_encp,
                "kday": kday,
                "top_keys": list(data.keys()) if isinstance(data, dict) else None,
                "data": data,
            }
            captures.append(rec)

            print()
            print("🔥 JSON通信")
            print(f"TYPE: {typ}")
            print(f"STATUS: {response.status}")
            print(f"ENCP: {req_encp}")
            print(f"KDAY: {kday}")
            print(f"TOP KEYS: {rec['top_keys']}")

        except Exception as e:
            print(f"捕獲解析エラー: {e}")

    page.on("response", on_response)

    page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(30000)

    browser.close()

type_counts = {}
unique_encp = []
for x in captures:
    typ = x.get("type")
    type_counts[typ] = type_counts.get(typ, 0) + 1
    e = x.get("encp")
    if e and e not in unique_encp:
        unique_encp.append(e)

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump({
        "target_venue": venue,
        "jsj004_raceUrlPrm": encp,
        "navigation_url": target_url,
        "capture_count": len(captures),
        "type_counts": type_counts,
        "unique_encp": unique_encp,
        "captures": captures,
    }, f, ensure_ascii=False, indent=2)

print()
print("=== 204 結果 ===")
print(f"通信捕獲数: {len(captures)}")
for typ, count in sorted(type_counts.items(), key=lambda x: str(x[0])):
    print(f"{typ}: {count}件")

print()
print("=== ENCP比較 ===")
print(f"JSJ004 raceUrlPrm: {encp}")
print(f"通信内ユニークencp数: {len(unique_encp)}")
for i, e in enumerate(unique_encp, 1):
    mark = "同一" if e == encp else "別"
    print(f"[{i}] {mark} -> {e}")

print()
print(f"保存完了: {OUTPUT_FILE}")
print("=== 204 完了 ===")
