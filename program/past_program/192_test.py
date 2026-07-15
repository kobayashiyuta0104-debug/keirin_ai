import json
from pathlib import Path

print("=== 192 選手・着順フィールド名 実構造確認テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "190_joined_ai_training_data.json"
OUTPUT_FILE = BASE_DIR / "192_field_structure_analysis.json"

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def find_player_list(pre):
    preferred = ["players", "sensyu", "sensyuTypeInfo", "player_features"]
    for key in preferred:
        value = pre.get(key)
        if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
            return key, value

    for key, value in pre.items():
        if isinstance(value, list) and len(value) == 7 and all(isinstance(x, dict) for x in value):
            return key, value

    return None, None

raw = load_json(INPUT_FILE)
training = raw.get("training_races", {})

samples = []

for race_key, joined in sorted(training.items()):
    pre = joined.get("pre_race", {})
    result = joined.get("result", {})

    player_list_key, players = find_player_list(pre)
    finish_rows = result.get("tyakujyunItemSubData", []) if isinstance(result, dict) else []

    sample = {
        "race_key": race_key,
        "pre_top_level_keys": list(pre.keys()) if isinstance(pre, dict) else None,
        "player_list_key": player_list_key,
        "player_count": len(players) if isinstance(players, list) else None,
        "first_player": players[0] if isinstance(players, list) and players else None,
        "first_player_keys": list(players[0].keys()) if isinstance(players, list) and players else None,
        "finish_count": len(finish_rows) if isinstance(finish_rows, list) else None,
        "first_finish": finish_rows[0] if isinstance(finish_rows, list) and finish_rows else None,
        "first_finish_keys": list(finish_rows[0].keys()) if isinstance(finish_rows, list) and finish_rows else None,
    }
    samples.append(sample)

    # 実構造確認は先頭3レースで十分
    if len(samples) >= 3:
        break

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump({
        "sample_count": len(samples),
        "samples": samples,
    }, f, ensure_ascii=False, indent=2)

print()
for i, sample in enumerate(samples, start=1):
    print(f"=== SAMPLE {i} ===")
    print(f"race_key: {sample['race_key']}")
    print(f"pre TOPキー: {sample['pre_top_level_keys']}")
    print(f"選手リストキー: {sample['player_list_key']}")
    print(f"選手数: {sample['player_count']}")
    print(f"先頭選手キー: {sample['first_player_keys']}")
    print("先頭選手データ:")
    print(json.dumps(sample["first_player"], ensure_ascii=False, indent=2))
    print()
    print(f"着順件数: {sample['finish_count']}")
    print(f"先頭着順キー: {sample['first_finish_keys']}")
    print("先頭着順データ:")
    print(json.dumps(sample["first_finish"], ensure_ascii=False, indent=2))
    print()

print(f"保存完了: {OUTPUT_FILE}")
print("=== 192 完了 ===")
