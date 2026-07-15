import json
import csv
from pathlib import Path

print("=== 193 AI学習用1レース1行データ 正式整形テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "190_joined_ai_training_data.json"
JSON_OUTPUT = BASE_DIR / "193_ai_training_rows.json"
CSV_OUTPUT = BASE_DIR / "193_ai_training_rows.csv"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def to_int(value):
    if value is None or value == "":
        return None
    try:
        return int(str(value).strip())
    except Exception:
        return None


def normalize_id(value):
    if value is None:
        return None
    return str(value).strip().zfill(6)


def recent_finish_values(player, limit=3):
    results = player.get("recent_meeting_results", [])
    values = []
    if isinstance(results, list):
        for item in results[:limit]:
            if isinstance(item, dict):
                values.append(to_int(item.get("finish")))
    while len(values) < limit:
        values.append(None)
    return values


raw = load_json(INPUT_FILE)
training = raw.get("training_races", {})

rows = []
id_match_races = 0
finish_complete_races = 0
rt3_complete_races = 0
problems = []

for race_key, joined in sorted(training.items()):
    pre = joined.get("pre_race", {})
    result = joined.get("result", {})

    players = pre.get("players", [])
    finish_rows = result.get("tyakujyunItemSubData", [])

    finish_by_id = {}
    if isinstance(finish_rows, list):
        for item in finish_rows:
            if not isinstance(item, dict):
                continue
            pid = normalize_id(item.get("sensyuRegistNo"))
            if pid:
                finish_by_id[pid] = item

    pre_ids = {
        normalize_id(p.get("player_id"))
        for p in players
        if isinstance(p, dict) and p.get("player_id") is not None
    }
    result_ids = set(finish_by_id.keys())

    id_match = (
        len(pre_ids) == 7
        and len(result_ids) == 7
        and pre_ids == result_ids
    )

    if id_match:
        id_match_races += 1
    else:
        problems.append({
            "race_key": race_key,
            "problem": "PLAYER_ID_MISMATCH",
            "pre_ids": sorted(pre_ids),
            "result_ids": sorted(result_ids),
        })

    row = {
        "race_key": race_key,
        "race_date": pre.get("race_date"),
        "venue": pre.get("venue"),
        "race_no": pre.get("race_no"),
        "player_count": len(players) if isinstance(players, list) else 0,
    }

    finish_count = 0

    if isinstance(players, list):
        players_sorted = sorted(
            players,
            key=lambda x: x.get("car_no", 999) if isinstance(x, dict) else 999
        )

        for player in players_sorted:
            if not isinstance(player, dict):
                continue

            car_no = to_int(player.get("car_no"))
            if car_no is None:
                continue

            prefix = f"p{car_no}_"
            pid = normalize_id(player.get("player_id"))
            finish = finish_by_id.get(pid, {})
            recent = recent_finish_values(player)

            finish_rank = to_int(finish.get("tyaku")) if finish else None
            if finish_rank is not None:
                finish_count += 1

            row[prefix + "id"] = pid
            row[prefix + "name"] = player.get("player_name")
            row[prefix + "prefecture"] = player.get("prefecture")
            row[prefix + "previous_class"] = player.get("previous_class")
            row[prefix + "class"] = player.get("class")
            row[prefix + "riding_style"] = player.get("riding_style")
            row[prefix + "graduation_term"] = player.get("graduation_term")
            row[prefix + "age"] = player.get("age")
            row[prefix + "race_score"] = player.get("race_score")
            row[prefix + "nige_count"] = player.get("nige_count")
            row[prefix + "makuri_count"] = player.get("makuri_count")
            row[prefix + "sashi_count"] = player.get("sashi_count")
            row[prefix + "mark_count"] = player.get("mark_count")
            row[prefix + "back_count"] = player.get("back_count")
            row[prefix + "home_count"] = player.get("home_count")
            row[prefix + "start_count"] = player.get("start_count")
            row[prefix + "win_rate"] = player.get("win_rate")
            row[prefix + "top2_rate"] = player.get("top2_rate")
            row[prefix + "top3_rate"] = player.get("top3_rate")
            row[prefix + "recent_finish_1"] = recent[0]
            row[prefix + "recent_finish_2"] = recent[1]
            row[prefix + "recent_finish_3"] = recent[2]
            row[prefix + "recent_venue_code"] = (
                player.get("recent_meeting", {}).get("venue_code")
                if isinstance(player.get("recent_meeting"), dict)
                else None
            )
            row[prefix + "recent_grade"] = (
                player.get("recent_meeting", {}).get("grade")
                if isinstance(player.get("recent_meeting"), dict)
                else None
            )

            # 教師データ側
            row[prefix + "finish_rank"] = finish_rank
            row[prefix + "result_car_no"] = to_int(finish.get("syaban")) if finish else None
            row[prefix + "agari"] = finish.get("agari") if finish else None
            row[prefix + "kimarite"] = finish.get("kimarite") if finish else None
            row[prefix + "BH"] = finish.get("BH") if finish else None

    if finish_count == 7:
        finish_complete_races += 1
    else:
        problems.append({
            "race_key": race_key,
            "problem": "FINISH_RANK_INCOMPLETE",
            "finish_count": finish_count,
        })

    payout = result.get("haraiGakuSubData", {})
    rt3_items = (
        payout.get("RT3HaraiGakuDispItemSubData", [])
        if isinstance(payout, dict)
        else []
    )

    rt3 = rt3_items[0] if isinstance(rt3_items, list) and rt3_items else {}

    row["trifecta_combination"] = rt3.get("kumiBan") if isinstance(rt3, dict) else None
    row["trifecta_payout"] = (
        to_int(str(rt3.get("haraiGaku")).replace(",", ""))
        if isinstance(rt3, dict) and rt3.get("haraiGaku") is not None
        else None
    )
    row["trifecta_popularity"] = rt3.get("ninki") if isinstance(rt3, dict) else None

    if row["trifecta_combination"] and row["trifecta_payout"] is not None:
        rt3_complete_races += 1
    else:
        problems.append({
            "race_key": race_key,
            "problem": "TRIFECTA_INCOMPLETE",
        })

    rows.append(row)

columns = []
seen = set()
for row in rows:
    for key in row.keys():
        if key not in seen:
            seen.add(key)
            columns.append(key)

with JSON_OUTPUT.open("w", encoding="utf-8") as f:
    json.dump({
        "row_count": len(rows),
        "column_count": len(columns),
        "player_id_7of7_match_races": id_match_races,
        "finish_rank_complete_races": finish_complete_races,
        "trifecta_complete_races": rt3_complete_races,
        "problem_count": len(problems),
        "problems": problems,
        "columns": columns,
        "rows": rows,
    }, f, ensure_ascii=False, indent=2)

with CSV_OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print()
print("=== 193 結果 ===")
print(f"学習用レース行数: {len(rows)}")
print(f"列数: {len(columns)}")
print(f"選手ID 7/7完全一致レース: {id_match_races}")
print(f"着順7人完全接続レース: {finish_complete_races}")
print(f"3連単組番・払戻取得レース: {rt3_complete_races}")
print(f"問題件数: {len(problems)}")
print(f"JSON保存: {JSON_OUTPUT}")
print(f"CSV保存: {CSV_OUTPUT}")

if rows:
    sample = rows[0]
    print()
    print("=== 先頭1レース確認 ===")
    print(f"race_key: {sample.get('race_key')}")
    print(f"player_count: {sample.get('player_count')}")
    print(f"p1_id: {sample.get('p1_id')}")
    print(f"p1_name: {sample.get('p1_name')}")
    print(f"p1_race_score: {sample.get('p1_race_score')}")
    print(f"p1_riding_style: {sample.get('p1_riding_style')}")
    print(f"p1_finish_rank: {sample.get('p1_finish_rank')}")
    print(f"trifecta_combination: {sample.get('trifecta_combination')}")
    print(f"trifecta_payout: {sample.get('trifecta_payout')}")
    print(f"trifecta_popularity: {sample.get('trifecta_popularity')}")

if problems:
    print()
    print("=== 問題一覧 先頭20件 ===")
    for problem in problems[:20]:
        print(problem)

print()
print("=== 193 完了 ===")
