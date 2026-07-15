from playwright.sync_api import sync_playwright
import json
import os
import re
import threading


INPUT_FILE = "163_dated_ai_pre_race_features.json"
OUTPUT_FILE = "181_verified_jsj006_capture.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_id(value):
    if value is None:
        return ""
    s = str(value).strip()
    return s.zfill(6) if s.isdigit() else s


def find_player_ids(obj):
    """
    163側のレースOBJECTから登録番号を再帰探索。
    player_id / sensyuRegistNo / regist_no 等を拾う。
    """
    ids = []

    def walk(x):
        if isinstance(x, dict):
            for key, value in x.items():
                key_lower = str(key).lower()

                if key in ("sensyuRegistNo", "player_id", "sensyu_regist_no"):
                    pid = normalize_id(value)
                    if pid:
                        ids.append(pid)

                elif (
                    "regist" in key_lower
                    and ("no" in key_lower or "id" in key_lower)
                ):
                    pid = normalize_id(value)
                    if pid:
                        ids.append(pid)

                for value2 in x.values():
                    walk(value2)

        elif isinstance(x, list):
            for item in x:
                walk(item)

    walk(obj)
    return sorted(set(ids))


def jsj006_player_ids(data):
    """
    JSJ006 JSONから sensyuTypeInfo 内の sensyuRegistNo を取得。
    """
    ids = []

    def walk(x):
        if isinstance(x, dict):
            sensyu = x.get("sensyuTypeInfo")

            if isinstance(sensyu, list):
                for player in sensyu:
                    if not isinstance(player, dict):
                        continue

                    pid = normalize_id(
                        player.get("sensyuRegistNo")
                    )

                    if pid:
                        ids.append(pid)

            for value in x.values():
                walk(value)

        elif isinstance(x, list):
            for item in x:
                walk(item)

    walk(data)
    return sorted(set(ids))


def main():
    print("=" * 70)
    print("🔥 181 163選手ID × JSJ006 7/7完全一致取得")
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
        target_ids = find_player_ids(race)

        if not venue or race_no is None or not race_key:
            continue

        race_map.append({
            "venue": venue,
            "race_no": int(race_no),
            "race_key": race_key,
            "target_ids": target_ids,
        })

    print("🔥 163レース地図:", len(race_map), "件")

    bad_map = [
        x for x in race_map
        if len(x["target_ids"]) == 0
    ]

    print("🔥 選手ID取得可能レース:", len(race_map) - len(bad_map))
    print("⚠ 選手ID 0件レース:", len(bad_map))

    if bad_map:
        print()
        print("⚠ IDなしSAMPLE")
        for x in bad_map[:10]:
            print(x["race_key"])

    captures = {}
    mismatch_log = []

    state_lock = threading.Lock()

    state = {
        "armed": False,
        "race_key": None,
        "venue": None,
        "race_no": None,
        "target_ids": [],
        "candidate_count": 0,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="msedge",
        )

        context = browser.new_context()
        page = context.new_page()

        def handle_response(response):
            if "type=JSJ006" not in response.url:
                return

            with state_lock:
                if not state["armed"]:
                    print("⚪ JSJ006無視: RボタンCLICK待機外")
                    return

                race_key = state["race_key"]
                venue = state["venue"]
                race_no = state["race_no"]
                target_ids = list(state["target_ids"])
                state["candidate_count"] += 1
                candidate_no = state["candidate_count"]

            try:
                data = response.json()
            except Exception as e:
                print("❌ JSJ006 JSON解析失敗:", e)
                return

            got_ids = jsj006_player_ids(data)
            common_ids = sorted(
                set(target_ids) & set(got_ids)
            )

            print()
            print("🔥 JSJ006候補受信")
            print("RACE KEY:", race_key)
            print("候補番号:", candidate_no)
            print("URL:", response.url)
            print("163 ID数:", len(target_ids))
            print("JSJ006 ID数:", len(got_ids))
            print("一致:", len(common_ids), "/", len(target_ids))

            if target_ids:
                print("TARGET:", target_ids)
                print("GOT   :", got_ids)

            if (
                len(target_ids) == 7
                and len(got_ids) == 7
                and target_ids == got_ids
            ):
                try:
                    request = response.request

                    capture = {
                        "race_key": race_key,
                        "venue": venue,
                        "race_no": race_no,
                        "target_player_ids": target_ids,
                        "jsj006_player_ids": got_ids,
                        "match_count": 7,
                        "match_status": "7/7_FULL_MATCH",
                        "request_url": response.url,
                        "request_method": request.method,
                        "request_post_data": request.post_data,
                        "data": data,
                    }

                    captures[race_key] = capture

                    with state_lock:
                        state["armed"] = False

                    print("🔥🔥🔥 7/7完全一致！保存成功:", race_key)

                except Exception as e:
                    print("❌ 保存処理失敗:", e)

            else:
                mismatch_log.append({
                    "race_key": race_key,
                    "candidate_no": candidate_no,
                    "target_ids": target_ids,
                    "got_ids": got_ids,
                    "common_ids": common_ids,
                    "request_url": response.url,
                })

                print("⚠ 不一致JSJ006なので保存しない")

        context.on("response", handle_response)

        page.goto(
            "https://www.keirin.jp/pc/top",
            wait_until="domcontentloaded",
            timeout=120000,
        )

        print()
        print("🔥 162/180と同じ開催場・Rボタン画面まで進めてください")
        input("🔥 準備できたらEnter：")

        print()
        print("=" * 70)
        print("🔥 83レース完全一致巡回開始")
        print("=" * 70)

        for index, target in enumerate(race_map, start=1):
            venue = target["venue"]
            race_no = target["race_no"]
            race_key = target["race_key"]
            target_ids = target["target_ids"]

            print()
            print("-" * 70)
            print(
                f"🔥 {index}/{len(race_map)} "
                f"{race_key}"
            )
            print("163選手ID:", target_ids)

            if len(target_ids) != 7:
                print(
                    "❌ 163側IDが7件ではないためSKIP:",
                    len(target_ids),
                )
                continue

            # 開催場CLICK中は絶対に保存しない
            with state_lock:
                state["armed"] = False
                state["race_key"] = None
                state["venue"] = None
                state["race_no"] = None
                state["target_ids"] = []
                state["candidate_count"] = 0

            venue_candidates = (
                page.locator("td, button, a, div, span")
                .filter(
                    has_text=re.compile(
                        rf"^\s*{re.escape(venue)}\s*$"
                    )
                )
            )

            venue_element = None

            try:
                count = venue_candidates.count()
            except Exception as e:
                print("❌ 開催場候補探索失敗:", e)
                continue

            for i in range(count):
                el = venue_candidates.nth(i)

                try:
                    onclick = (
                        el.get_attribute("onclick")
                        or ""
                    )

                    if (
                        "KeirinjoClick" in onclick
                        or "keirinjoClick" in onclick
                    ):
                        venue_element = el
                        break

                except Exception:
                    continue

            if venue_element is None:
                print("❌ 開催場DOMなし:", venue)
                continue

            try:
                print("🔥 開催場CLICK:", venue)
                venue_element.click(
                    timeout=10000,
                    force=True,
                )
                page.wait_for_timeout(1800)

            except Exception as e:
                print("❌ 開催場CLICK失敗:", e)
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

                try:
                    if locator.count() == 0:
                        continue

                    if locator.first.is_visible():
                        race_button = locator.first
                        used_selector = selector
                        break

                except Exception:
                    continue

            if race_button is None:
                print(f"❌ {race_no}Rボタンなし")
                continue

            # RボタンCLICK直前にだけ受信許可
            with state_lock:
                state["armed"] = True
                state["race_key"] = race_key
                state["venue"] = venue
                state["race_no"] = race_no
                state["target_ids"] = list(target_ids)
                state["candidate_count"] = 0

            try:
                print(
                    f"🔥 {race_no}R CLICK:",
                    used_selector,
                )

                race_button.click(
                    timeout=10000,
                    force=True,
                )

            except Exception as e:
                with state_lock:
                    state["armed"] = False

                print("❌ レースCLICK失敗:", e)
                continue

            success = False

            for _ in range(50):
                page.wait_for_timeout(500)

                if race_key in captures:
                    success = True
                    break

            with state_lock:
                state["armed"] = False

            if success:
                print(
                    "✅ 7/7完全一致取得完了:",
                    race_key,
                )
            else:
                print(
                    "❌ 完全一致JSJ006なし:",
                    race_key,
                )

        ordered_captures = []

        for target in race_map:
            race_key = target["race_key"]

            if race_key in captures:
                ordered_captures.append(
                    captures[race_key]
                )

        missing = []

        for target in race_map:
            if target["race_key"] not in captures:
                missing.append({
                    "race_key": target["race_key"],
                    "venue": target["venue"],
                    "race_no": target["race_no"],
                    "target_player_ids": target["target_ids"],
                })

        output = {
            "source_file": INPUT_FILE,
            "target_race_count": len(race_map),
            "verified_capture_count": len(ordered_captures),
            "missing_count": len(missing),
            "verification_rule": (
                "163 player IDs 7/7 == "
                "JSJ006 sensyuRegistNo 7/7"
            ),
            "captures": ordered_captures,
            "missing": missing,
            "mismatch_log": mismatch_log,
        }

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                output,
                f,
                ensure_ascii=False,
                indent=2,
            )

        print()
        print("=" * 70)
        print("🔥 181テスト終了")
        print("=" * 70)
        print("163対象レース数:", len(race_map))
        print(
            "🔥 7/7完全一致取得数:",
            len(ordered_captures),
        )
        print("未取得数:", len(missing))
        print("不一致候補数:", len(mismatch_log))

        if missing:
            print()
            print("🔥 未取得race_key一覧")
            for item in missing:
                print(item["race_key"])

        print()
        print("保存先:", OUTPUT_FILE)
        print("=" * 70)

        input("確認できたらEnter：")
        browser.close()


if __name__ == "__main__":
    main()
