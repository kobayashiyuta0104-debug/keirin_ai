import json
from pathlib import Path

print("=== 194 着順未接続7レース 原因確認テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "190_joined_ai_training_data.json"
OUTPUT_FILE = BASE_DIR / "194_finish_rank_problem_analysis.json"

TARGET_RACES = {
    "20260707_久留米_2R",
    "20260707_佐世保_5R",
    "20260707_取手_6R",
    "20260707_和歌山_10R",
    "20260707_和歌山_7R",
    "20260707_豊橋_1R",
    "20260707_豊橋_9R",
}

with INPUT_FILE.open("r", encoding="utf-8") as f:
    raw = json.load(f)

training = raw.get("training_races", {})
analysis = []

for race_key in sorted(TARGET_RACES):
    joined = training.get(race_key, {})
    pre = joined.get("pre_race", {})
    result = joined.get("result", {})

    players = pre.get("players", [])
    finish_rows = result.get("tyakujyunItemSubData", [])

    pre_by_id = {
        str(p.get("player_id")).zfill(6): p
        for p in players
        if isinstance(p, dict) and p.get("player_id") is not None
    }

    race_info = {
        "race_key": race_key,
        "player_count": len(players) if isinstance(players, list) else None,
        "finish_row_count": len(finish_rows) if isinstance(finish_rows, list) else None,
        "finish_rows": [],
    }

    print()
    print("=" * 70)
    print(race_key)
    print(f"レース前選手数: {race_info['player_count']}")
    print(f"JSJ012着順行数: {race_info['finish_row_count']}")
    print("-" * 70)

    if isinstance(finish_rows, list):
        for item in finish_rows:
            if not isinstance(item, dict):
                continue

            pid = str(item.get("sensyuRegistNo")).zfill(6)
            pre_player = pre_by_id.get(pid, {})

            state_rows = item.get("kojinStateItemSubData", [])
            states = []
            if isinstance(state_rows, list):
                for state in state_rows:
                    if isinstance(state, dict):
                        states.append({
                            "kojinState": state.get("kojinState"),
                            "kojinStateClass": state.get("kojinStateClass"),
                            "tyakuNote": state.get("tyakuNote"),
                        })

            row = {
                "sensyuRegistNo": pid,
                "pre_car_no": pre_player.get("car_no"),
                "pre_player_name": pre_player.get("player_name"),
                "tyaku_raw": item.get("tyaku"),
                "syaban": item.get("syaban"),
                "sensyuName": item.get("sensyuName"),
                "tyakusa": item.get("tyakusa"),
                "agari": item.get("agari"),
                "kimarite": item.get("kimarite"),
                "BH": item.get("BH"),
                "kojinStateItemSubData": states,
            }
            race_info["finish_rows"].append(row)

            print(
                f"ID:{pid} / "
                f"車番:{item.get('syaban')} / "
                f"選手:{item.get('sensyuName')} / "
                f"tyaku={repr(item.get('tyaku'))} / "
                f"tyakusa={repr(item.get('tyakusa'))} / "
                f"状態={states}"
            )

    analysis.append(race_info)

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump({
        "target_race_count": len(TARGET_RACES),
        "analysis": analysis,
    }, f, ensure_ascii=False, indent=2)

print()
print("=== 194 結果 ===")
print(f"確認対象レース数: {len(analysis)}")
print(f"保存完了: {OUTPUT_FILE}")
print("=== 194 完了 ===")
