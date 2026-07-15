from playwright.sync_api import sync_playwright
import json
import os
import re


INPUT_FILE = "163_dated_ai_pre_race_features.json"
OUTPUT_JSON = "180_race_map_jsj006_capture.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 70)
    print("🔥 180 163レース地図 × JSJ006通信監視")
    print("=" * 70)

    if not os.path.exists(INPUT_FILE):
        print(f"❌ JSONなし: {INPUT_FILE}")
        return

    source = load_json(INPUT_FILE)
    races = source.get("races", [])

    if not isinstance(races, list):
        print("❌ racesがlistではない")
        return

    race_map = []
    for race in races:
        if not isinstance(race, dict):
            continue

        venue = str(race.get("venue", "")).strip()
        race_no = race.get("race_no")
        race_key = str(race.get("race_key", "")).strip()

        if not venue or race_no is None or not race_key:
            continue

        race_map.append({
            "venue": venue,
            "race_no": int(race_no),
            "race_key": race_key,
        })

    print(f"🔥 163レース地図読込数: {len(race_map)}")

    target_keys = {x["race_key"] for x in race_map}
    results = {}
    current_race = {"venue": None, "race_no": None, "race_key": None}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="msedge")
        context = browser.new_context()
        page = context.new_page()

        def handle_response(response):
            if "type=JSJ006" not in response.url:
                return

            print()
            print("🔥🔥🔥 JSJ006通信発見！🔥🔥🔥")
            print("URL:", response.url)

            try:
                data = response.json()
                request = response.request
            except Exception as e:
                print(f"❌ JSON解析失敗: {e}")
                return

            venue = current_race["venue"]
            race_no = current_race["race_no"]
            race_key = current_race["race_key"]

            if not race_key:
                print("⚠ 現在race_key未設定")
                return

            player_count = 0
            players = data.get("sensyuTypeInfo", []) if isinstance(data, dict) else []
            if isinstance(players, list):
                player_count = len(players)

            capture = {
                "race_key": race_key,
                "venue": venue,
                "race_no": race_no,
                "player_count": player_count,
                "request_url": response.url,
                "request_method": request.method,
                "request_post_data": request.post_data,
                "data": data,
            }

            results[race_key] = capture

            print(f"✅ CAPTURE {race_key} 選手数={player_count}")
            print("METHOD:", request.method)
            print("POST DATA:", request.post_data)

        context.on("response", handle_response)

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded",
            timeout=120000,
        )

        print()
        print("🔥 Edgeを163の能力データを取得した時と同じ画面まで進めてください")
        print("🔥 開催場と1R～12Rが見える画面まで進み、JSJ006が出るレース画面を開いてください")
        input("🔥 準備できたらEnter：")

        print()
        print("=" * 70)
        print("🔥 163の83レースを地図として巡回開始")
        print("=" * 70)

        for index, target in enumerate(race_map, start=1):
            venue = target["venue"]
            race_no = target["race_no"]
            race_key = target["race_key"]

            current_race["venue"] = venue
            current_race["race_no"] = race_no
            current_race["race_key"] = race_key

            print()
            print("-" * 70)
            print(f"🔥 {index}/{len(race_map)} {race_key}")

            # 163のvenue名を使い、onclickを固定セレクタで決め打ちしない
            venue_candidates = page.locator("td, button, a, div, span").filter(
                has_text=re.compile(rf"^\s*{re.escape(venue)}\s*$")
            )

            venue_element = None
            for i in range(venue_candidates.count()):
                el = venue_candidates.nth(i)
                try:
                    onclick = el.get_attribute("onclick") or ""
                    if "KeirinjoClick" in onclick or "keirinjoClick" in onclick:
                        venue_element = el
                        break
                except Exception:
                    continue

            if venue_element is None:
                print(f"❌ 開催場DOMなし: {venue}")
                continue

            try:
                print(f"🔥 開催場CLICK: {venue}")
                venue_element.click(timeout=10000, force=True)
                page.wait_for_timeout(1500)
            except Exception as e:
                print(f"❌ 開催場CLICK失敗: {e}")
                continue

            selectors = [
                f"#hhRaceBtn{race_no}",
                f"#raceBtn{race_no}",
                f"[id*='RaceBtn{race_no}']",
            ]

            race_button = None
            used_selector = None

            for selector in selectors:
                locator = page.locator(selector)
                if locator.count() == 0:
                    continue
                try:
                    if locator.first.is_visible():
                        race_button = locator.first
                        used_selector = selector
                        break
                except Exception:
                    continue

            if race_button is None:
                print(f"❌ {race_no}Rボタンなし")
                continue

            results.pop(race_key, None)

            try:
                print(f"🔥 {race_no}R CLICK: {used_selector}")
                race_button.click(timeout=10000, force=True)
            except Exception as e:
                print(f"❌ レースCLICK失敗: {e}")
                continue

            success = False
            for _ in range(40):
                page.wait_for_timeout(500)
                if race_key in results:
                    success = True
                    break

            if success:
                print(f"✅ {race_key} JSJ006取得完了")
            else:
                print(f"❌ {race_key} JSJ006通信なし")

        ordered_results = []
        for target in race_map:
            race_key = target["race_key"]
            if race_key in results:
                ordered_results.append(results[race_key])

        output = {
            "source_file": INPUT_FILE,
            "target_race_count": len(race_map),
            "target_race_key_count": len(target_keys),
            "capture_count": len(ordered_results),
            "captures": ordered_results,
        }

        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print()
        print("=" * 70)
        print("🔥 180テスト終了")
        print("=" * 70)
        print("163対象レース数:", len(race_map))
        print("JSJ006取得数:", len(ordered_results))
        print("未取得数:", len(race_map) - len(ordered_results))
        print("保存先:", OUTPUT_JSON)
        print("=" * 70)

        input("確認できたらEnter：")
        browser.close()


if __name__ == "__main__":
    main()
