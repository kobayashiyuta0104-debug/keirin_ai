import json
import os
import re
import time

from playwright.sync_api import sync_playwright


PRE_RACE_FILE = "163_dated_ai_pre_race_features.json"

OUTPUT_RAW = "166_all_venues_jsj012.json"
OUTPUT_JOIN = "166_joined_training_data.json"

TARGET_DATE = "20260707"

KEIRIN_URL = "https://www.keirin.jp/pc/top"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_id(value):
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return text.zfill(6)


def walk(obj, path="ROOT"):
    yield path, obj

    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from walk(
                value,
                f"{path}.{key}",
            )

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from walk(
                value,
                f"{path}[{index}]",
            )


def get_player_id(player):
    if not isinstance(player, dict):
        return None

    for key in [
        "player_id",
        "sensyuRegistNo",
        "numPlayer",
    ]:
        value = player.get(key)

        if value not in [None, ""]:
            return normalize_id(value)

    return None


def extract_result_players(data):
    candidates = []

    for path, obj in walk(data):
        if not isinstance(obj, dict):
            continue

        players = None

        if isinstance(obj.get("tyakujyunItemSubData"), list):
            players = obj.get("tyakujyunItemSubData")

        elif isinstance(obj.get("finish_order"), list):
            players = obj.get("finish_order")

        if not players:
            continue

        normalized = []

        for player in players:
            if not isinstance(player, dict):
                continue

            player_id = get_player_id(player)

            rank = (
                player.get("tyaku")
                or player.get("rank")
                or player.get("finish")
            )

            car_no = (
                player.get("syaban")
                or player.get("car_no")
                or player.get("carNum")
            )

            if player_id is None:
                continue

            normalized.append(
                {
                    "player_id": player_id,
                    "rank": rank,
                    "car_no": car_no,
                    "player_name": (
                        player.get("sensyuName")
                        or player.get("player_name")
                        or player.get("name")
                    ),
                    "agari": player.get("agari"),
                    "kimarite": player.get("kimarite"),
                    "bh": (
                        player.get("BH")
                        or player.get("bh")
                    ),
                }
            )

        if len(normalized) >= 5:
            candidates.append(
                {
                    "path": path,
                    "players": normalized,
                }
            )

    return candidates


def build_pre_index(pre_data):
    races = pre_data.get("races", [])

    index = {}

    for race in races:
        if not isinstance(race, dict):
            continue

        race_key = race.get("race_key")
        players = race.get("players", [])

        ids = []

        for player in players:
            player_id = get_player_id(player)

            if player_id:
                ids.append(player_id)

        id_set = frozenset(ids)

        if id_set:
            index.setdefault(id_set, [])
            index[id_set].append(race_key)

    return index


def main():
    print("=" * 70)
    print("🔥 166 7月7日 JSJ012取得 × 163自動結合")
    print("=" * 70)

    if not os.path.exists(PRE_RACE_FILE):
        print("❌ ファイルなし:", PRE_RACE_FILE)
        return

    pre_data = load_json(PRE_RACE_FILE)
    pre_index = build_pre_index(pre_data)

    print()
    print("🔥 163読込成功")
    print("race_key IDセット数:", len(pre_index))

    captured = []

    with sync_playwright() as p:
        print()
        print("🔥 Edge起動")

        browser = p.chromium.launch(
            channel="msedge",
            headless=False,
        )

        context = browser.new_context()

        page = context.new_page()

        def on_response(response):
            url = response.url

            if "type=JSJ012" not in url:
                return

            try:
                data = response.json()
            except Exception:
                return

            captured.append(
                {
                    "url": url,
                    "data": data,
                }
            )

            print()
            print("🔥 JSJ012取得")
            print("COUNT:", len(captured))
            print("URL:", url[:150])

        page.on("response", on_response)

        print()
        print("🔥 KEIRIN.JPを開く")

        page.goto(
            KEIRIN_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        time.sleep(5)

        print()
        print("=" * 70)
        print("🔥 自動レース巡回開始")
        print("=" * 70)

        venue_buttons = page.locator(
            "a, button, input"
        )

        venue_count = venue_buttons.count()

        print("初期ELEMENT数:", venue_count)

        clicked_races = set()

        for loop_no in range(1, 500):
            print()
            print(
                f"🔥 巡回 LOOP {loop_no} "
                f"JSJ012={len(captured)}"
            )

            race_clicked = False

            for race_no in range(1, 13):
                selectors = [
                    f"#hhRaceBtn{race_no}",
                    f"[id*='RaceBtn{race_no}']",
                ]

                target = None

                for selector in selectors:
                    locator = page.locator(selector)

                    if locator.count() > 0:
                        target = locator.first
                        break

                if target is None:
                    continue

                try:
                    if not target.is_visible():
                        continue

                    key = (
                        page.url,
                        race_no,
                    )

                    if key in clicked_races:
                        continue

                    clicked_races.add(key)

                    print(
                        f"🔥 {race_no}Rクリック"
                    )

                    target.click(
                        timeout=5000,
                    )

                    time.sleep(1.2)

                    result_targets = page.get_by_text(
                        re.compile(
                            r"競走結果|レース結果|結果"
                        )
                    )

                    for i in range(
                        min(
                            result_targets.count(),
                            20,
                        )
                    ):
                        result_button = (
                            result_targets.nth(i)
                        )

                        try:
                            if not result_button.is_visible():
                                continue

                            text = (
                                result_button.inner_text()
                                .strip()
                            )

                            if "結果" not in text:
                                continue

                            print(
                                "🔥 結果クリック:",
                                text,
                            )

                            result_button.click(
                                timeout=5000,
                            )

                            time.sleep(1.2)

                            break

                        except Exception:
                            continue

                    race_clicked = True

                except Exception as e:
                    print(
                        "⚠ RACE CLICK ERROR:",
                        race_no,
                        str(e)[:100],
                    )

            venue_targets = page.locator(
                "a, button"
            )

            venue_moved = False

            for i in range(
                min(
                    venue_targets.count(),
                    300,
                )
            ):
                item = venue_targets.nth(i)

                try:
                    if not item.is_visible():
                        continue

                    text = item.inner_text().strip()

                    if not text:
                        continue

                    if text in [
                        "豊橋",
                        "和歌山",
                        "防府",
                        "弥彦",
                        "取手",
                        "玉野",
                        "久留米",
                        "佐世保",
                    ]:
                        marker = (
                            "VENUE",
                            text,
                            loop_no,
                        )

                        if marker in clicked_races:
                            continue

                        clicked_races.add(marker)

                        print(
                            "🔥 開催場クリック:",
                            text,
                        )

                        item.click(
                            timeout=5000,
                        )

                        time.sleep(2)

                        venue_moved = True
                        break

                except Exception:
                    continue

            if (
                len(captured) >= 83
                or loop_no >= 100
            ):
                break

            if not race_clicked and not venue_moved:
                print(
                    "⚠ クリック対象なし"
                )
                break

        print()
        print("🔥 追加待機 5秒")
        time.sleep(5)

        browser.close()

    print()
    print("=" * 70)
    print("🔥 JSJ012保存")
    print("=" * 70)

    with open(
        OUTPUT_RAW,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            captured,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print("JSJ012取得数:", len(captured))

    print()
    print("=" * 70)
    print("🔥 163 × JSJ012 選手ID照合")
    print("=" * 70)

    result_candidates = []

    for response_index, item in enumerate(captured):
        candidates = extract_result_players(
            item["data"]
        )

        for candidate in candidates:
            candidate["response_index"] = (
                response_index
            )

            result_candidates.append(candidate)

    print(
        "確定結果候補数:",
        len(result_candidates),
    )

    joined = []

    for candidate in result_candidates:
        ids = [
            player["player_id"]
            for player in candidate["players"]
        ]

        id_set = frozenset(ids)

        matched_race_keys = pre_index.get(
            id_set,
            [],
        )

        if not matched_race_keys:
            continue

        for race_key in matched_race_keys:
            players = sorted(
                candidate["players"],
                key=lambda x: (
                    int(x["rank"])
                    if str(x["rank"]).isdigit()
                    else 999
                ),
            )

            sanrentan = "-".join(
                str(player["car_no"])
                for player in players[:3]
            )

            print()
            print("🔥 結合成功")
            print("RACE KEY:", race_key)
            print("3連単:", sanrentan)
            print(
                "RESULT PATH:",
                candidate["path"],
            )

            joined.append(
                {
                    "race_key": race_key,
                    "sanrentan": sanrentan,
                    "finish_order": players,
                    "response_index": (
                        candidate["response_index"]
                    ),
                    "result_path": candidate["path"],
                }
            )

    output = {
        "target_date": TARGET_DATE,
        "pre_race_count": len(pre_index),
        "jsj012_response_count": len(captured),
        "result_candidate_count": len(
            result_candidates
        ),
        "joined_count": len(joined),
        "joined": joined,
    }

    with open(
        OUTPUT_JOIN,
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
    print("🔥 166テスト終了")
    print("=" * 70)

    print(
        "163予想レース数:",
        len(pre_index),
    )

    print(
        "JSJ012取得数:",
        len(captured),
    )

    print(
        "確定結果候補数:",
        len(result_candidates),
    )

    print(
        "🔥 自動結合成功数:",
        len(joined),
    )

    print()
    print("RAW保存先:", OUTPUT_RAW)
    print("結合保存先:", OUTPUT_JOIN)

    print("=" * 70)


if __name__ == "__main__":
    main()