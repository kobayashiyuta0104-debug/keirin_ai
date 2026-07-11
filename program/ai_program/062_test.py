from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from collections import Counter
import json
import re
import time

print("=== 062 ライン並び予想 直接取得キー・通信先探索 ===")

BASE = Path(r"C:\競輪AI")
OUT_DIR = BASE / "data_official" / "line_research" / "062_line_direct_key_research"
BODY_DIR = OUT_DIR / "response_bodies"
OUT_FILE = OUT_DIR / "062_line_direct_key_research.json"

OUT_DIR.mkdir(parents=True, exist_ok=True)
BODY_DIR.mkdir(parents=True, exist_ok=True)

CAPTURE_WAIT = 8


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def safe_text(response):
    try:
        return response.text()
    except Exception:
        return None


def safe_filename(text):
    text = re.sub(r"[^0-9A-Za-z_.-]+", "_", text or "")
    return text[:100] or "unknown"


def get_pj0314_text(page):
    try:
        return page.locator("#PJ0314").inner_text(timeout=3000)
    except Exception:
        return ""


def wait_change(page, before, timeout=8):
    start = time.time()
    while time.time() - start < timeout:
        after = get_pj0314_text(page)
        if after and after != before:
            page.wait_for_timeout(1000)
            return True
        page.wait_for_timeout(250)
    return False


def extract_date(text):
    patterns = [
        r"(20\d{2})年\s*(\d{1,2})月\s*(\d{1,2})日",
        r"(20\d{2})[/-](\d{1,2})[/-](\d{1,2})",
    ]
    for pattern in patterns:
        m = re.search(pattern, text or "")
        if m:
            return f"{int(m.group(1)):04d}{int(m.group(2)):02d}{int(m.group(3)):02d}"
    return datetime.now().strftime("%Y%m%d")


def get_live_venues(page):
    return page.evaluate("""
    () => {
        const out = [];
        const root = document.getElementById("hcomRaceDiv");
        if (!root) return out;
        for (const li of root.querySelectorAll("li.kyotuHeader")) {
            const place = li.querySelector("p.place");
            const btn = li.querySelector("button[id^='hcombtnLive']");
            if (!place || !btn) continue;
            const venue = (place.innerText || "").trim();
            if (venue) out.push({venue, button_id: btn.id});
        }
        return out;
    }
    """)


def get_race_buttons(page):
    return page.evaluate("""
    () => {
        const out = [];
        for (const el of document.querySelectorAll("[id^='hhRaceBtn']")) {
            const m = (el.id || "").match(/^hhRaceBtn(\\d+)$/);
            if (!m) continue;
            out.push({
                id: el.id,
                race_no: Number(m[1]),
                text: (el.innerText || el.textContent || "").trim()
            });
        }
        out.sort((a,b) => a.race_no - b.race_no);
        return out;
    }
    """)


def inspect_line(page):
    return page.evaluate("""
    () => {
        const out = {
            found: false,
            target_text: "",
            target_html: "",
            prediction_type: null,
            provider: null,
            rider_numbers: []
        };

        const pj = document.getElementById("PJ0314");
        if (!pj) return out;

        for (const table of pj.querySelectorAll("table")) {
            const text = table.innerText || "";
            if (!text.includes("並び予想") || !text.includes("情報提供")) continue;

            out.found = true;
            out.target_text = text;
            out.target_html = table.outerHTML;

            for (const type of [
                "二分戦", "三分戦", "四分戦",
                "五分戦", "コマ切れ", "先行一車"
            ]) {
                if (text.includes(type)) {
                    out.prediction_type = type;
                    break;
                }
            }

            const pm = text.match(/情報提供\\s*[：:]\\s*([^\\n\\r]+)/);
            if (pm) out.provider = pm[1].trim();

            out.rider_numbers = Array.from(table.querySelectorAll(".snum"))
                .map(x => (x.textContent || "").trim())
                .filter(x => /^[1-9]$/.test(x))
                .map(Number);

            break;
        }

        return out;
    }
    """)


def main():
    captures = []
    phase = {"name": "START"}
    sequence = {"n": 0}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="msedge",
        )
        context = browser.new_context()
        page = context.new_page()

        def on_response(response):
            url = response.url

            if "keirin.jp" not in url.lower():
                return

            resource_type = response.request.resource_type

            # 画像・フォント・CSSは今回の直接キー探索では不要
            if resource_type in {"image", "font", "stylesheet"}:
                return

            body = safe_text(response)
            if body is None:
                return

            sequence["n"] += 1
            n = sequence["n"]

            parsed = urlparse(url)
            query = parse_qs(parsed.query, keep_blank_values=True)

            jsj_type = (query.get("type") or [None])[0]
            encp = (query.get("encp") or [None])[0]
            kday = (query.get("kday") or [None])[0]

            lower = body.lower()

            keywords = []
            for word in [
                "並び予想", "情報提供", "二分戦", "三分戦",
                "四分戦", "五分戦", "コマ切れ", "先行一車",
                "line", "formation", "narabi", "yoso"
            ]:
                if word.lower() in lower:
                    keywords.append(word)

            interesting = (
                resource_type in {"xhr", "fetch", "document", "script"}
                or jsj_type is not None
                or len(keywords) > 0
            )

            if not interesting:
                return

            suffix = ".json" if body.lstrip().startswith(("{", "[")) else ".txt"
            body_name = (
                f"{n:04d}_"
                f"{safe_filename(phase['name'])}_"
                f"{safe_filename(resource_type)}_"
                f"{safe_filename(jsj_type or parsed.path.split('/')[-1])}"
                f"{suffix}"
            )
            body_path = BODY_DIR / body_name
            body_path.write_text(body, encoding="utf-8", errors="replace")

            rec = {
                "sequence": n,
                "phase": phase["name"],
                "url": url,
                "method": response.request.method,
                "post_data": response.request.post_data,
                "status": response.status,
                "resource_type": resource_type,
                "content_type": response.headers.get("content-type"),
                "jsj_type": jsj_type,
                "encp": encp,
                "kday": kday,
                "query": query,
                "body_length": len(body),
                "keywords": keywords,
                "saved_body": str(body_path),
            }
            captures.append(rec)

            if resource_type in {"xhr", "fetch"} or jsj_type or keywords:
                print()
                print("🔥 RESPONSE")
                print("PHASE:", phase["name"])
                print("TYPE:", resource_type)
                print("JSJ:", jsj_type)
                print("STATUS:", response.status)
                print("URL:", url)
                print("METHOD:", response.request.method)
                print("POST DATA:", response.request.post_data)
                print("KEYWORDS:", keywords)
                print("BODY:", body_path)

        context.on("response", on_response)

        print()
        print("[1] KEIRIN.JPトップ")
        phase["name"] = "TOP_OPEN"

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded",
            timeout=120000,
        )
        page.wait_for_timeout(5000)

        live_buttons = page.locator("button[id^='hcombtnLive']")
        live_count = live_buttons.count()

        print("LIVE BUTTON COUNT:", live_count)

        if live_count == 0:
            print("ERROR: LIVEボタンなし")
            browser.close()
            return

        print()
        print("[2] 正式LIVE導線")
        phase["name"] = "LIVE_CLICK"

        clicked = False
        for i in range(live_count):
            btn = live_buttons.nth(i)
            try:
                if not btn.is_visible():
                    continue
                print("LIVE CLICK:", btn.get_attribute("id"))
                btn.click(timeout=30000)
                clicked = True
                break
            except Exception as e:
                print("LIVE SKIP:", repr(e))

        if not clicked:
            print("ERROR: LIVEクリック失敗")
            browser.close()
            return

        try:
            page.wait_for_url("**/pc/racelive**", timeout=120000)
        except Exception:
            pass

        page.wait_for_timeout(8000)

        print("RACELIVE URL:", page.url)

        body_text = page.locator("body").inner_text(timeout=10000)
        race_date = extract_date(body_text)

        venues = get_live_venues(page)

        print("TARGET DATE:", race_date)
        print("VENUE COUNT:", len(venues))

        if not venues:
            print("ERROR: 開催なし")
            browser.close()
            return

        # キー探索なので1開催・1レースだけ。
        # 043でラインDOM取得成功済みの構造を使い、
        # クリック前後の全XHR/fetch/JSON通信を捕獲する。
        target_venue = venues[0]

        print()
        print("[3] 対象開催クリック")
        print("VENUE:", target_venue["venue"])

        phase["name"] = f"VENUE_CLICK_{target_venue['venue']}"

        before = get_pj0314_text(page)
        page.locator("#" + target_venue["button_id"]).click(timeout=30000)
        wait_change(page, before, 8)
        page.wait_for_timeout(3000)

        race_buttons = get_race_buttons(page)

        print("RACE COUNT:", len(race_buttons))

        if not race_buttons:
            print("ERROR: Rボタンなし")
            browser.close()
            return

        target_race = race_buttons[0]
        race_key = (
            f"{race_date}_"
            f"{target_venue['venue']}_"
            f"{target_race['race_no']}R"
        )

        print()
        print("[4] 1レースクリック前 通信基準点")
        print("RACE KEY:", race_key)

        # 開催クリック通信とレースクリック通信を明確に分離
        phase["name"] = f"BEFORE_RACE_{race_key}"
        page.wait_for_timeout(2000)

        capture_start_index = len(captures)

        print()
        print("[5] Rクリック → 全通信捕獲")
        phase["name"] = f"RACE_CLICK_{race_key}"

        before = get_pj0314_text(page)
        page.locator("#" + target_race["id"]).click(timeout=30000)
        changed = wait_change(page, before, 8)

        page.wait_for_timeout(CAPTURE_WAIT * 1000)

        line_dom = inspect_line(page)

        race_click_captures = captures[capture_start_index:]

        print()
        print("[6] DOMの正解ライン確認")
        print("PJ0314 CHANGED:", changed)
        print("LINE FOUND:", line_dom["found"])
        print("TYPE:", line_dom["prediction_type"])
        print("PROVIDER:", line_dom["provider"])
        print("RIDER NUMBERS:", line_dom["rider_numbers"])

        # DOM正解情報とレスポンスBODYの一致を機械探索
        provider = line_dom.get("provider") or ""
        prediction_type = line_dom.get("prediction_type") or ""
        rider_numbers = line_dom.get("rider_numbers") or []

        candidates = []

        for rec in race_click_captures:
            try:
                body = Path(rec["saved_body"]).read_text(
                    encoding="utf-8",
                    errors="replace",
                )
            except Exception:
                continue

            score = 0
            reasons = []

            if "並び予想" in body:
                score += 100
                reasons.append("HAS_NARABI_TEXT")

            if "情報提供" in body:
                score += 50
                reasons.append("HAS_PROVIDER_LABEL")

            if provider and provider in body:
                score += 80
                reasons.append("PROVIDER_MATCH")

            if prediction_type and prediction_type in body:
                score += 80
                reasons.append("TYPE_MATCH")

            # 車番列がJSON/HTML内に存在する可能性を見る
            rider_hit = 0
            for num in sorted(set(rider_numbers)):
                if str(num) in body:
                    rider_hit += 1

            if rider_numbers and rider_hit == len(set(rider_numbers)):
                score += 20
                reasons.append("ALL_RIDER_NUMBERS_PRESENT")

            if rec.get("resource_type") in {"xhr", "fetch"}:
                score += 10
                reasons.append("XHR_OR_FETCH")

            if rec.get("jsj_type"):
                score += 5
                reasons.append("JSJ_TYPE")

            if score > 0:
                candidates.append({
                    "score": score,
                    "reasons": reasons,
                    **rec,
                })

        candidates.sort(
            key=lambda x: (
                x["score"],
                x["body_length"],
            ),
            reverse=True,
        )

        jsj_counter = Counter(
            str(x.get("jsj_type"))
            for x in race_click_captures
            if x.get("jsj_type")
        )

        resource_counter = Counter(
            str(x.get("resource_type"))
            for x in race_click_captures
        )

        output = {
            "program": "062_test.py",
            "created_at": datetime.now().isoformat(),
            "purpose": (
                "ライン並び予想の直接取得キー・JSON・通信先探索"
            ),
            "race_date": race_date,
            "race_key": race_key,
            "venue": target_venue["venue"],
            "race_no": target_race["race_no"],
            "pj0314_changed": changed,
            "line_dom_truth": line_dom,
            "race_click_response_count": len(race_click_captures),
            "resource_type_summary": dict(resource_counter),
            "jsj_type_summary": dict(jsj_counter),
            "direct_source_candidates": candidates,
            "race_click_captures": race_click_captures,
            "all_captures": captures,
        }

        save_json(OUT_FILE, output)

        print()
        print("=" * 100)
        print("062 最終結果")
        print("=" * 100)
        print()
        print("RACE KEY:", race_key)
        print("LINE DOM FOUND:", line_dom["found"])
        print("TYPE:", line_dom["prediction_type"])
        print("PROVIDER:", line_dom["provider"])
        print("RACE CLICK RESPONSE COUNT:", len(race_click_captures))
        print()
        print("★ RESOURCE TYPE ★")
        for key, value in resource_counter.most_common():
            print(key, ":", value)

        print()
        print("★ JSJ TYPE ★")
        if jsj_counter:
            for key, value in jsj_counter.most_common():
                print(key, ":", value)
        else:
            print("なし")

        print()
        print("★ DIRECT SOURCE CANDIDATE TOP20 ★")

        if not candidates:
            print("なし")
        else:
            for item in candidates[:20]:
                print()
                print("-" * 100)
                print("SCORE:", item["score"])
                print("REASONS:", item["reasons"])
                print("PHASE:", item["phase"])
                print("RESOURCE:", item["resource_type"])
                print("JSJ:", item["jsj_type"])
                print("METHOD:", item["method"])
                print("POST DATA:", item["post_data"])
                print("URL:", item["url"])
                print("BODY:", item["saved_body"])

        print()
        print("保存先:")
        print(OUT_FILE)
        print()
        print("=== 062 完了 ===")

        browser.close()


if __name__ == "__main__":
    main()
