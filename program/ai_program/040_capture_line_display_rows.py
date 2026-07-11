from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
import json
import time


# ============================================================
# 040
# 並び予想DOMを「表示段単位」でそのまま取得する
# ============================================================

BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "040_line_display_rows"
)

OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUT_DIR / "040_line_display_rows.json"

CDP_URL = "http://127.0.0.1:9222"


TARGETS = [
    ("伊東", 5),
    ("大垣", 8),
    ("いわき平", 1),
    ("いわき平", 2),
    ("いわき平", 3),
    ("いわき平", 6),
]


KNOWN_SPECIAL = {
    "大垣_8R": "ジカ競り",
    "いわき平_1R": "ジカ競り",
}


print()
print("=" * 100)
print("040 並び予想 表示段DOM取得テスト")
print("=" * 100)
print()


def safe_text(locator):
    try:
        return locator.inner_text(timeout=3000).strip()
    except Exception:
        return ""


def get_pj0314_signature(page):
    try:
        return page.locator("#PJ0314").inner_text(timeout=3000)
    except Exception:
        return ""


def wait_pj0314_change(page, before, timeout_seconds=15):
    start = time.time()

    while time.time() - start < timeout_seconds:
        try:
            after = get_pj0314_signature(page)

            if after and after != before:
                return {
                    "changed": True,
                    "wait_seconds": round(time.time() - start, 3),
                }

        except Exception:
            pass

        time.sleep(0.5)

    return {
        "changed": False,
        "wait_seconds": round(time.time() - start, 3),
    }


def get_venue_buttons(page):
    return page.evaluate(
        """
        () => {
            const result = [];

            const buttons = Array.from(
                document.querySelectorAll(
                    'button[id^="hcombtnLive"]'
                )
            );

            for (const button of buttons) {
                const id = button.id || "";
                const m = id.match(/hcombtnLive(\\d+)/);

                if (!m) continue;

                const index = Number(m[1]);

                const li = button.closest("li");

                let venue = "";

                if (li) {
                    const text = (li.innerText || "")
                        .replace(/LIVE/g, "")
                        .replace(/投票/g, "")
                        .replace(/\\d+R/g, "")
                        .trim();

                    const lines = text
                        .split(/\\n+/)
                        .map(v => v.trim())
                        .filter(Boolean);

                    if (lines.length > 0) {
                        venue = lines[0];
                    }
                }

                const hidden =
                    document.querySelector(
                        "#hcomHdnTouhyouLive" + index
                    );

                result.push({
                    index: index,
                    venue: venue,
                    button_id: id,
                    onclick: button.getAttribute("onclick") || "",
                    hidden_id: hidden ? hidden.id : null,
                    hidden_value: hidden ? hidden.value : null,
                });
            }

            return result;
        }
        """
    )


def find_venue_button(page, target_venue):
    buttons = get_venue_buttons(page)

    for item in buttons:
        venue = item.get("venue", "")

        if venue == target_venue:
            return item

        if target_venue == "いわき平":
            if venue in ["平", "いわき平", "　平　"]:
                return item

    return None


def inspect_line_rows(page):
    return page.evaluate(
        """
        () => {
            const pj = document.querySelector("#PJ0314");

            if (!pj) {
                return {
                    pj0314_exists: false,
                    line_target_exists: false,
                    prediction_type: null,
                    provider: null,
                    display_rows: [],
                    row_count: 0,
                    has_multi_row: false,
                    has_competition_text: false,
                    competition_texts: [],
                    target_html: null
                };
            }

            const tables = Array.from(
                pj.querySelectorAll("table")
            );

            let target = null;

            for (const table of tables) {
                const text = table.innerText || "";

                if (text.includes("並び予想")) {
                    target = table;
                    break;
                }
            }

            if (!target) {
                return {
                    pj0314_exists: true,
                    line_target_exists: false,
                    prediction_type: null,
                    provider: null,
                    display_rows: [],
                    row_count: 0,
                    has_multi_row: false,
                    has_competition_text: false,
                    competition_texts: [],
                    target_html: null
                };
            }

            let predictionType = null;

            const typeCandidates = [
                "二分戦",
                "三分戦",
                "四分戦",
                "コマ切れ",
                "先行一車"
            ];

            const targetText = target.innerText || "";

            for (const t of typeCandidates) {
                if (targetText.includes(t)) {
                    predictionType = t;
                    break;
                }
            }

            let provider = null;

            const providerMatch =
                targetText.match(/情報提供：([^\\n]+)/);

            if (providerMatch) {
                provider = providerMatch[1].trim();
            }

            const competitionTexts = [];

            const allElements = Array.from(
                target.querySelectorAll("*")
            );

            for (const el of allElements) {
                const text = (el.innerText || "").trim();

                if (
                    text === "競" ||
                    text.includes("競り") ||
                    text.includes("ジカ")
                ) {
                    competitionTexts.push({
                        tag: el.tagName,
                        id: el.id || "",
                        class_name: el.className || "",
                        text: text,
                        outer_html: el.outerHTML
                    });
                }
            }

            /*
            並び本体を探す。

            「並び予想」を持つ外側tableの中から、
            .snum を持つtableを探す。

            そのtableの直属に近い tr 単位で
            表示段を保存する。
            */

            const candidateTables = Array.from(
                target.querySelectorAll("table")
            ).filter(
                table => table.querySelector(".snum")
            );

            let lineTable = null;

            if (candidateTables.length > 0) {
                lineTable = candidateTables[0];
            }

            const displayRows = [];

            if (lineTable) {
                const rows = Array.from(
                    lineTable.querySelectorAll(":scope > tbody > tr")
                );

                rows.forEach((tr, rowIndex) => {
                    const cells = Array.from(
                        tr.querySelectorAll(":scope > td")
                    );

                    const tokens = [];
                    const carNumbers = [];
                    const separators = [];

                    cells.forEach((td, cellIndex) => {
                        const snum = td.querySelector(".snum");

                        if (snum) {
                            const text =
                                (snum.textContent || "").trim();

                            const className =
                                snum.className || "";

                            const rect =
                                snum.getBoundingClientRect();

                            let tokenType = "unknown";
                            let value = null;

                            if (/^[1-9]$/.test(text)) {
                                tokenType = "car";
                                value = Number(text);
                                carNumbers.push(Number(text));
                            }
                            else if (
                                className.includes("base_color_0")
                            ) {
                                tokenType = "separator";
                                value = 0;
                                separators.push(cellIndex);
                            }
                            else if (text === "") {
                                tokenType = "blank";
                                value = null;
                            }

                            tokens.push({
                                cell_index: cellIndex,
                                token_type: tokenType,
                                value: value,
                                text: text,
                                class_name: className,
                                x: rect.x,
                                y: rect.y,
                                width: rect.width,
                                height: rect.height,
                                outer_html: snum.outerHTML
                            });
                        }
                        else {
                            const img = td.querySelector("img");

                            if (img) {
                                tokens.push({
                                    cell_index: cellIndex,
                                    token_type: "image",
                                    value: null,
                                    text: "",
                                    class_name: img.className || "",
                                    src: img.getAttribute("src") || "",
                                    outer_html: img.outerHTML
                                });
                            }
                            else {
                                const text =
                                    (td.innerText || "").trim();

                                if (text) {
                                    tokens.push({
                                        cell_index: cellIndex,
                                        token_type: "text",
                                        value: null,
                                        text: text,
                                        class_name: td.className || "",
                                        outer_html: td.outerHTML
                                    });
                                }
                            }
                        }
                    });

                    const rowRect =
                        tr.getBoundingClientRect();

                    displayRows.push({
                        row_index: rowIndex,
                        row_text: tr.innerText || "",
                        car_numbers: carNumbers,
                        separator_cell_indexes: separators,
                        token_count: tokens.length,
                        tokens: tokens,
                        rect: {
                            x: rowRect.x,
                            y: rowRect.y,
                            width: rowRect.width,
                            height: rowRect.height
                        },
                        outer_html: tr.outerHTML
                    });
                });
            }

            return {
                pj0314_exists: true,
                line_target_exists: true,
                prediction_type: predictionType,
                provider: provider,
                display_rows: displayRows,
                row_count: displayRows.length,
                has_multi_row: displayRows.length >= 2,
                has_competition_text:
                    competitionTexts.length > 0,
                competition_texts: competitionTexts,
                target_text: targetText,
                target_html: target.outerHTML,
                line_table_html:
                    lineTable ? lineTable.outerHTML : null
            };
        }
        """
    )


results = []


with sync_playwright() as p:

    print("Edge接続:")
    print(CDP_URL)
    print()

    browser = p.chromium.connect_over_cdp(CDP_URL)

    contexts = browser.contexts

    if not contexts:
        raise RuntimeError("Edge context がありません")

    context = contexts[0]

    pages = context.pages

    if not pages:
        raise RuntimeError("Edge page がありません")

    page = pages[0]

    print("接続成功")
    print("URL:", page.url)
    print("TITLE:", page.title())
    print()

    for target_index, (venue, race_no) in enumerate(
        TARGETS,
        start=1
    ):

        race_key = f"{venue}_{race_no}R"

        print("#" * 100)
        print(
            f"TARGET {target_index}/{len(TARGETS)}"
        )
        print("RACE:", race_key)
        print("#" * 100)
        print()

        record = {
            "venue": venue,
            "race_no": race_no,
            "race_key": race_key,
            "known_special":
                KNOWN_SPECIAL.get(race_key),
            "venue_button": None,
            "venue_wait": None,
            "race_button_id": None,
            "race_wait": None,
            "status": None,
            "error": None,
            "dom": None,
        }

        try:
            venue_button = find_venue_button(
                page,
                venue
            )

            record["venue_button"] = venue_button

            if venue_button is None:
                record["status"] = "VENUE_BUTTON_NOT_FOUND"

                print("開催ボタンなし")
                results.append(record)
                continue

            print(
                "VENUE BUTTON:",
                venue_button["button_id"]
            )

            before = get_pj0314_signature(page)

            page.locator(
                "#" + venue_button["button_id"]
            ).click()

            venue_wait = wait_pj0314_change(
                page,
                before
            )

            record["venue_wait"] = venue_wait

            print(
                "VENUE WAIT:",
                venue_wait
            )

            race_button_id = f"hhRaceBtn{race_no}"

            record["race_button_id"] = race_button_id

            race_button = page.locator(
                "#" + race_button_id
            )

            if race_button.count() == 0:
                record["status"] = "RACE_BUTTON_NOT_FOUND"

                print(
                    "レースボタンなし:",
                    race_button_id
                )

                results.append(record)
                continue

            before = get_pj0314_signature(page)

            race_button.click()

            race_wait = wait_pj0314_change(
                page,
                before
            )

            record["race_wait"] = race_wait

            print(
                "RACE WAIT:",
                race_wait
            )

            dom = inspect_line_rows(page)

            record["dom"] = dom

            if not dom["pj0314_exists"]:
                record["status"] = "PJ0314_NOT_FOUND"

            elif not dom["line_target_exists"]:
                record["status"] = "LINE_TARGET_NOT_FOUND"

            else:
                record["status"] = "ROWS_CAPTURED"

            print()
            print("STATUS:", record["status"])
            print(
                "TYPE:",
                dom.get("prediction_type")
            )
            print(
                "PROVIDER:",
                dom.get("provider")
            )
            print(
                "ROW COUNT:",
                dom.get("row_count")
            )
            print(
                "MULTI ROW:",
                dom.get("has_multi_row")
            )
            print(
                "競 TEXT:",
                dom.get("has_competition_text")
            )

            print()
            print("DISPLAY ROWS:")

            for row in dom.get(
                "display_rows",
                []
            ):
                print(
                    " ROW",
                    row["row_index"],
                    "CARS:",
                    row["car_numbers"],
                    "SEP:",
                    row["separator_cell_indexes"],
                    "TEXT:",
                    repr(row["row_text"])
                )

            print()

        except Exception as e:
            record["status"] = "ERROR"
            record["error"] = repr(e)

            print("ERROR:")
            print(repr(e))
            print()

        results.append(record)


output = {
    "program":
        "040_capture_line_display_rows.py",
    "captured_at":
        datetime.now().isoformat(),
    "target_count":
        len(TARGETS),
    "known_special":
        KNOWN_SPECIAL,
    "results":
        results,
}


with open(
    OUT_FILE,
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
print("=" * 100)
print("040 最終結果")
print("=" * 100)
print()

for item in results:

    dom = item.get("dom") or {}

    print("-" * 100)
    print("RACE:", item["race_key"])
    print("KNOWN:", item["known_special"])
    print("STATUS:", item["status"])
    print(
        "TYPE:",
        dom.get("prediction_type")
    )
    print(
        "ROW COUNT:",
        dom.get("row_count")
    )
    print(
        "MULTI ROW:",
        dom.get("has_multi_row")
    )
    print(
        "競 TEXT:",
        dom.get("has_competition_text")
    )

    for row in dom.get(
        "display_rows",
        []
    ):
        print(
            "ROW",
            row["row_index"],
            ":",
            row["car_numbers"],
            "SEP",
            row["separator_cell_indexes"]
        )

    print()


print("保存先:")
print(OUT_FILE)
print()
print("=== 040 完了 ===")