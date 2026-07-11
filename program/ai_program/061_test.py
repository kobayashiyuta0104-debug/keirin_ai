import json
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import requests
from playwright.sync_api import sync_playwright


# ============================================================
# 061 修正版
# 20260711 全レース
# JSJ006能力 + 正式LIVE導線ライン予想 race_key接続テスト
#
# 重要:
# ・043は呼ばない
# ・racelive?encp=... へ直接gotoしない
# ・KEIRIN.JPトップ -> LIVEボタン の正式導線で1回だけ入る
# ・開催ボタン -> Rボタンをクリックして全レース巡回
# ・PJ0314変化待ちは最大5秒。永久待機しない
# ・失敗レースがあっても次へ進む
# ・能力JSJ006はrequests直接取得
# ============================================================

print("=== 061 修正版 20260711 能力 + ライン 全レース接続テスト ===")

BASE = Path(r"C:\競輪AI")
TARGET_DATE = "20260711"

DAILY_DIR = BASE / "data_daily" / TARGET_DATE
DAILY_DIR.mkdir(parents=True, exist_ok=True)

PRE_RACE_FILE = DAILY_DIR / "pre_race.json"
OUTPUT_FILE = DAILY_DIR / "061_pre_race_merged.json"
PROGRESS_FILE = DAILY_DIR / "061_progress.json"

KEIRIN_JSON_URL = "https://www.keirin.jp/pc/json"

VENUE_WAIT_SECONDS = 5
RACE_WAIT_SECONDS = 5
RETRY_COUNT = 2

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0 Safari/537.36 Edg/142.0"
    ),
    "Referer": "https://www.keirin.jp/pc/top",
    "Accept": "application/json,text/plain,*/*",
})


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def walk_objects(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk_objects(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk_objects(value)


def find_races(obj):
    found = {}
    for item in walk_objects(obj):
        race_key = item.get("race_key")
        if not isinstance(race_key, str):
            continue
        if not race_key.startswith(TARGET_DATE + "_"):
            continue
        if race_key not in found:
            found[race_key] = item
    return found


def find_enc_para_r(obj):
    if isinstance(obj, dict):
        for key in ("encParaR", "enc_para_r", "encp"):
            value = obj.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for value in obj.values():
            found = find_enc_para_r(value)
            if found:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = find_enc_para_r(value)
            if found:
                return found
    return None


def parse_race_key(race_key):
    # 日付_開催_1R
    parts = race_key.split("_")
    if len(parts) < 3:
        return None, None
    venue = "_".join(parts[1:-1])
    race_text = parts[-1]
    try:
        race_no = int(race_text[:-1])
    except Exception:
        return venue, None
    return venue, race_no


def fetch_jsj006(enc_para_r):
    response = SESSION.get(
        KEIRIN_JSON_URL,
        params={"encp": enc_para_r, "type": "JSJ006"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_player_count(jsj006):
    if not isinstance(jsj006, dict):
        return 0
    players = jsj006.get("sensyuTypeInfo", [])
    if not isinstance(players, list):
        return 0
    return len(players)


def get_pj0314_signature(page):
    try:
        return page.locator("#PJ0314").inner_text(timeout=1500)
    except Exception:
        return ""


def bounded_wait_change(page, before, seconds):
    start = time.time()
    while time.time() - start < seconds:
        after = get_pj0314_signature(page)
        if after and after != before:
            page.wait_for_timeout(500)
            return True
        page.wait_for_timeout(250)
    return False


def get_live_venues(page):
    return page.evaluate(
        """
        () => {
            const results = [];
            const container = document.getElementById("hcomRaceDiv");
            if (!container) return results;

            const items = Array.from(
                container.querySelectorAll("li.kyotuHeader")
            );

            for (const item of items) {
                const place = item.querySelector("p.place");
                const button = item.querySelector(
                    "button[id^='hcombtnLive']"
                );

                if (!place || !button) continue;

                const venue = (place.innerText || "").trim();
                if (!venue) continue;

                results.push({
                    venue: venue,
                    button_id: button.id || ""
                });
            }

            return results;
        }
        """
    )


def capture_line_dom(page):
    return page.evaluate(
        """
        () => {
            const output = {
                line_target_exists: false,
                prediction_type: null,
                provider: null,
                has_competition_text: false,
                rows: []
            };

            const pj = document.getElementById("PJ0314");
            if (!pj) return output;

            const tables = Array.from(pj.querySelectorAll("table"));
            let target = null;

            for (const table of tables) {
                const text = table.innerText || "";
                if (
                    text.includes("並び予想") &&
                    text.includes("情報提供")
                ) {
                    target = table;
                    break;
                }
            }

            if (!target) return output;
            output.line_target_exists = true;

            const targetText = target.innerText || "";

            const types = [
                "二分戦", "三分戦", "四分戦",
                "五分戦", "コマ切れ", "先行一車"
            ];

            for (const type of types) {
                if (targetText.includes(type)) {
                    output.prediction_type = type;
                    break;
                }
            }

            const providerMatch = targetText.match(
                /情報提供\\s*[：:]\\s*([^\\n\\r]+)/
            );
            if (providerMatch) {
                output.provider = providerMatch[1].trim();
            }

            const allElements = Array.from(target.querySelectorAll("*"));
            for (const el of allElements) {
                const text = (el.innerText || "").trim();
                if (
                    text === "競" ||
                    text === "競り" ||
                    text.includes("ジカ")
                ) {
                    output.has_competition_text = true;
                    break;
                }
            }

            const firstSnum = target.querySelector(".snum");
            if (!firstSnum) return output;

            const lineTable = firstSnum.closest("table");
            if (!lineTable) return output;

            let rows = [];
            if (lineTable.tBodies && lineTable.tBodies.length > 0) {
                rows = Array.from(lineTable.tBodies[0].rows);
            }

            for (
                let rowIndex = 0;
                rowIndex < rows.length;
                rowIndex++
            ) {
                const tr = rows[rowIndex];
                const cells = Array.from(tr.cells || []);
                const carCells = [];

                for (
                    let cellIndex = 0;
                    cellIndex < cells.length;
                    cellIndex++
                ) {
                    const snums = Array.from(
                        cells[cellIndex].querySelectorAll(".snum")
                    );

                    for (const snum of snums) {
                        const text = (snum.textContent || "").trim();
                        if (!/^[1-9]$/.test(text)) continue;

                        const rect = snum.getBoundingClientRect();

                        carCells.push({
                            car_number: Number(text),
                            cell_index: cellIndex,
                            x: rect.x
                        });
                    }
                }

                if (carCells.length > 0) {
                    output.rows.push({
                        row_index: rowIndex,
                        car_count: carCells.length,
                        car_cells: carCells
                    });
                }
            }

            return output;
        }
        """
    )


def reconstruct_lines(car_cells):
    if not car_cells:
        return []

    cells = sorted(
        car_cells,
        key=lambda x: (
            x.get("cell_index", 0),
            x.get("x", 0),
        ),
    )

    lines = []
    current = []
    previous_index = None

    for item in cells:
        car_number = item.get("car_number")
        cell_index = item.get("cell_index")

        if previous_index is None:
            current = [car_number]
        else:
            gap = cell_index - previous_index
            if gap > 1:
                if current:
                    lines.append(current)
                current = [car_number]
            else:
                current.append(car_number)

        previous_index = cell_index

    if current:
        lines.append(current)

    return lines


def analyze_line_dom(dom):
    analyzed = []

    for row in dom.get("rows", []):
        analyzed.append({
            "row_index": row.get("row_index"),
            "car_count": row.get("car_count", 0),
            "lines": reconstruct_lines(
                row.get("car_cells", [])
            ),
        })

    valid = [
        row for row in analyzed
        if row.get("car_count", 0) > 0
    ]

    if not valid:
        return [], []

    main_row = max(
        valid,
        key=lambda x: x.get("car_count", 0),
    )

    competition_rows = [
        row for row in valid
        if row.get("row_index") != main_row.get("row_index")
    ]

    return (
        main_row.get("lines", []),
        competition_rows,
    )


def open_official_racelive(page):
    print("[2] KEIRIN.JPトップページ表示")

    page.goto(
        "https://www.keirin.jp/pc/top",
        wait_until="domcontentloaded",
        timeout=120000,
    )

    page.wait_for_timeout(5000)

    buttons = page.locator("button[id^='hcombtnLive']")
    count = buttons.count()

    print("LIVE BUTTON COUNT:", count)

    for index in range(count):
        button = buttons.nth(index)

        try:
            if not button.is_visible():
                continue

            print("LIVE CLICK:", button.get_attribute("id"))
            button.click(timeout=30000)

            try:
                page.wait_for_url(
                    "**/pc/racelive**",
                    timeout=30000,
                )
            except Exception:
                pass

            page.wait_for_timeout(5000)

            body = page.locator("body").inner_text(timeout=5000)

            if (
                "EC0500E" not in body
                and "予期せぬエラー" not in body
                and "racelive" in page.url.lower()
            ):
                print("RACELIVE OK:", page.url)
                return True

        except Exception as e:
            print("LIVE CLICK SKIP:", repr(e))

    return False


def click_venue(page, venue_name):
    venues = get_live_venues(page)

    for item in venues:
        if item.get("venue") != venue_name:
            continue

        button_id = item.get("button_id")
        before = get_pj0314_signature(page)

        try:
            page.locator("#" + button_id).click(timeout=15000)
            changed = bounded_wait_change(
                page,
                before,
                VENUE_WAIT_SECONDS,
            )
            return True, changed, button_id
        except Exception as e:
            return False, False, repr(e)

    return False, False, "VENUE_BUTTON_NOT_FOUND"


def capture_one_race(page, race_no):
    button_id = f"hhRaceBtn{race_no}"

    for attempt in range(1, RETRY_COUNT + 1):
        try:
            button = page.locator("#" + button_id)

            if button.count() == 0:
                return {
                    "status": "RACE_BUTTON_NOT_FOUND",
                    "main_lines": [],
                    "prediction_type": None,
                    "provider": None,
                    "has_competition": False,
                    "competition_rows": [],
                    "attempt": attempt,
                }

            before = get_pj0314_signature(page)
            button.click(timeout=15000)

            changed = bounded_wait_change(
                page,
                before,
                RACE_WAIT_SECONDS,
            )

            # 変化しなくても現在DOMを必ず確認する。
            # 既に対象Rが表示中ならPJ0314は変化しないため。
            dom = capture_line_dom(page)

            if dom.get("line_target_exists"):
                main_lines, competition_rows = analyze_line_dom(dom)

                if main_lines:
                    return {
                        "status": "LINE_FOUND",
                        "main_lines": main_lines,
                        "prediction_type": dom.get("prediction_type"),
                        "provider": dom.get("provider"),
                        "has_competition": (
                            dom.get("has_competition_text") is True
                            or len(competition_rows) > 0
                        ),
                        "competition_rows": competition_rows,
                        "pj0314_changed": changed,
                        "attempt": attempt,
                    }

            print(
                f"  RETRY {attempt}/{RETRY_COUNT}: "
                f"{button_id} LINE未取得"
            )
            page.wait_for_timeout(700)

        except Exception as e:
            print(
                f"  RETRY {attempt}/{RETRY_COUNT} ERROR:",
                repr(e),
            )
            page.wait_for_timeout(700)

    return {
        "status": "LINE_NOT_FOUND",
        "main_lines": [],
        "prediction_type": None,
        "provider": None,
        "has_competition": False,
        "competition_rows": [],
        "attempt": RETRY_COUNT,
    }


def main():
    print()
    print("=" * 100)
    print("061 修正版 20260711 能力 + ライン 全レース接続")
    print("=" * 100)
    print()

    print("[1] 20260711 pre_race.json確認")
    print("FILE:", PRE_RACE_FILE)

    if not PRE_RACE_FILE.exists():
        print("ERROR: 20260711 pre_race.json がありません")
        return

    pre_raw = load_json(PRE_RACE_FILE)
    races = find_races(pre_raw)

    print("RACE COUNT:", len(races))

    if not races:
        print("ERROR: 20260711のrace_keyが見つかりません")
        return

    race_items = sorted(races.items())

    grouped = defaultdict(list)

    for race_key, race_source in race_items:
        venue, race_no = parse_race_key(race_key)

        grouped[venue].append({
            "race_key": race_key,
            "race_no": race_no,
            "race_source": race_source,
        })

    merged = {}
    ability_found = 0
    ability_failed = 0
    line_found = 0
    line_failed = 0
    processed = 0

    with sync_playwright() as p:
        print()
        print("[2] Edge自動起動")

        browser = p.chromium.launch(
            headless=False,
            channel="msedge",
        )

        context = browser.new_context()
        page = context.new_page()

        if not open_official_racelive(page):
            print("ERROR: 正式LIVE導線でraceliveへ入れません")
            browser.close()
            return

        print()
        print("[3] 開催別に能力 + ライン取得開始")

        for venue_index, venue_name in enumerate(
            sorted(grouped.keys()),
            start=1,
        ):
            venue_races = sorted(
                grouped[venue_name],
                key=lambda x: x["race_no"],
            )

            print()
            print("#" * 100)
            print(
                f"VENUE {venue_index}/{len(grouped)}: "
                f"{venue_name}"
            )
            print("#" * 100)

            venue_ok, venue_changed, venue_info = click_venue(
                page,
                venue_name,
            )

            print("VENUE CLICK:", venue_ok)
            print("VENUE PJ0314 CHANGED:", venue_changed)
            print("VENUE INFO:", venue_info)

            if not venue_ok:
                for item in venue_races:
                    race_key = item["race_key"]
                    race_source = item["race_source"]
                    enc_para_r = find_enc_para_r(race_source)

                    jsj006 = None
                    player_count = 0

                    if enc_para_r:
                        try:
                            jsj006 = fetch_jsj006(enc_para_r)
                            player_count = get_player_count(jsj006)
                        except Exception:
                            pass

                    if player_count > 0:
                        ability_found += 1
                    else:
                        ability_failed += 1

                    line_failed += 1
                    processed += 1

                    merged[race_key] = {
                        "race_key": race_key,
                        "target_date": TARGET_DATE,
                        "encParaR": enc_para_r,
                        "status": "NOT_READY",
                        "ability": {
                            "player_count": player_count,
                            "jsj006": jsj006,
                        },
                        "line_prediction": {
                            "status": "VENUE_CLICK_ERROR",
                            "prediction_type": None,
                            "main_lines": [],
                            "provider": None,
                        },
                    }

                continue

            for item in venue_races:
                race_key = item["race_key"]
                race_no = item["race_no"]
                race_source = item["race_source"]
                processed += 1

                print()
                print("-" * 100)
                print(
                    f"[{processed}/{len(race_items)}] "
                    f"{race_key}"
                )

                enc_para_r = find_enc_para_r(race_source)

                jsj006 = None
                player_count = 0

                if enc_para_r:
                    try:
                        jsj006 = fetch_jsj006(enc_para_r)
                        player_count = get_player_count(jsj006)

                        if player_count > 0:
                            ability_found += 1
                            print("ABILITY:", player_count, "riders")
                        else:
                            ability_failed += 1
                            print("ABILITY: NG")

                    except Exception as e:
                        ability_failed += 1
                        print("ABILITY ERROR:", repr(e))
                else:
                    ability_failed += 1
                    print("ABILITY: encParaRなし")

                line_data = capture_one_race(
                    page,
                    race_no,
                )

                if line_data.get("status") == "LINE_FOUND":
                    line_found += 1
                    print("LINE STATUS: LINE_FOUND")
                    print("TYPE:", line_data.get("prediction_type"))
                    print("LINES:", line_data.get("main_lines"))
                    print("PROVIDER:", line_data.get("provider"))
                    print(
                        "PJ0314 CHANGED:",
                        line_data.get("pj0314_changed"),
                    )
                else:
                    line_failed += 1
                    print(
                        "LINE STATUS:",
                        line_data.get("status"),
                    )

                ready = (
                    player_count > 0
                    and line_data.get("status") == "LINE_FOUND"
                )

                merged[race_key] = {
                    "race_key": race_key,
                    "target_date": TARGET_DATE,
                    "encParaR": enc_para_r,
                    "status": (
                        "READY_PRE_RACE_AI"
                        if ready
                        else "NOT_READY"
                    ),
                    "ability": {
                        "player_count": player_count,
                        "jsj006": jsj006,
                    },
                    "line_prediction": {
                        "status": line_data.get("status"),
                        "prediction_type": line_data.get(
                            "prediction_type"
                        ),
                        "main_lines": line_data.get(
                            "main_lines",
                            [],
                        ),
                        "provider": line_data.get("provider"),
                        "has_competition": line_data.get(
                            "has_competition",
                            False,
                        ),
                        "competition_rows": line_data.get(
                            "competition_rows",
                            [],
                        ),
                        "pj0314_changed": line_data.get(
                            "pj0314_changed"
                        ),
                        "attempt": line_data.get("attempt"),
                    },
                }

                save_json(
                    PROGRESS_FILE,
                    {
                        "target_date": TARGET_DATE,
                        "processed": processed,
                        "race_count": len(race_items),
                        "races": merged,
                    },
                )

        browser.close()

    ready_count = len([
        race
        for race in merged.values()
        if race.get("status") == "READY_PRE_RACE_AI"
    ])

    status_summary = defaultdict(int)

    for race in merged.values():
        line_status = (
            race.get("line_prediction", {})
            .get("status", "UNKNOWN")
        )
        status_summary[line_status] += 1

    output = {
        "program": "061_test.py",
        "created_at": datetime.now().isoformat(),
        "target_date": TARGET_DATE,
        "summary": {
            "race_count": len(races),
            "ability_found": ability_found,
            "ability_failed": ability_failed,
            "line_found": line_found,
            "line_failed": line_failed,
            "ready_pre_race_ai": ready_count,
            "line_status_summary": dict(status_summary),
        },
        "races": merged,
    }

    save_json(OUTPUT_FILE, output)

    print()
    print("#" * 100)
    print("061 最終結果")
    print("#" * 100)
    print()
    print("TARGET DATE:", TARGET_DATE)
    print("RACE COUNT:", len(races))
    print("ABILITY FOUND:", ability_found)
    print("ABILITY FAILED:", ability_failed)
    print("LINE FOUND:", line_found)
    print("LINE FAILED:", line_failed)
    print("ABILITY + LINE MERGED:", ready_count)
    print()
    print("★ LINE STATUS SUMMARY ★")

    for status, count in sorted(status_summary.items()):
        print(status, ":", count)

    print()
    print("保存先:")
    print(OUTPUT_FILE)
    print()
    print("=== 061 完了 ===")


if __name__ == "__main__":
    main()
