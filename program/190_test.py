import json
from pathlib import Path

print("=== 190 レース前AIデータ + 確定結果 race_key結合テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
PRE_RACE_FILE = BASE_DIR / "163_dated_ai_pre_race_features.json"
RESULT_FILE = BASE_DIR / "189_jsj012_result_registry.json"
OUTPUT_FILE = BASE_DIR / "190_joined_ai_training_data.json"

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def normalize_pre_races(raw):
    if isinstance(raw, list):
        return raw

    if isinstance(raw, dict):
        # よくあるラッパー構造
        for key in ("races", "data", "records"):
            if isinstance(raw.get(key), list):
                return raw[key]

        # race_key -> race dict 形式
        rows = []
        for key, value in raw.items():
            if isinstance(value, dict):
                item = dict(value)
                item.setdefault("race_key", key)
                rows.append(item)
        return rows

    return []

pre_raw = load_json(PRE_RACE_FILE)
registry = load_json(RESULT_FILE)

pre_races = normalize_pre_races(pre_raw)
confirmed = registry.get("confirmed", {})
pending = registry.get("pending", {})

print(f"163 レース前データ数: {len(pre_races)}")
print(f"189 CONFIRMED数: {len(confirmed)}")
print(f"189 PENDING数: {len(pending)}")

joined = {}
pending_matches = {}
no_result = {}
duplicate_pre_race_keys = []
seen = set()

for race in pre_races:
    race_key = race.get("race_key")

    if not race_key:
        continue

    if race_key in seen:
        duplicate_pre_race_keys.append(race_key)
        continue
    seen.add(race_key)

    if race_key in confirmed:
        result_record = confirmed[race_key]

        joined[race_key] = {
            "race_key": race_key,
            "date": race.get("date"),
            "venue": race.get("venue"),
            "race_no": race.get("race_no"),
            "pre_race": race,
            "result": result_record.get("data"),
            "result_status": "CONFIRMED",
            "result_match_status": result_record.get("match_status")
            or result_record.get("status"),
            "target_player_ids": result_record.get("target_player_ids"),
            "jsj012_player_ids": result_record.get("jsj012_player_ids"),
            "encp": result_record.get("encp"),
        }

    elif race_key in pending:
        pending_matches[race_key] = {
            "race_key": race_key,
            "pre_race": race,
            "pending": pending[race_key],
            "result_status": "PENDING",
        }

    else:
        no_result[race_key] = {
            "race_key": race_key,
            "pre_race": race,
            "result_status": "NO_RESULT_CONNECTION",
        }

confirmed_keys = set(confirmed.keys())
pre_keys = {x.get("race_key") for x in pre_races if x.get("race_key")}

confirmed_not_in_pre = sorted(confirmed_keys - pre_keys)
joined_keys = set(joined.keys())

output = {
    "dataset_version": "190",
    "source_pre_race": str(PRE_RACE_FILE),
    "source_result_registry": str(RESULT_FILE),
    "summary": {
        "pre_race_count": len(pre_races),
        "confirmed_registry_count": len(confirmed),
        "pending_registry_count": len(pending),
        "joined_training_race_count": len(joined),
        "pending_match_count": len(pending_matches),
        "no_result_connection_count": len(no_result),
        "duplicate_pre_race_key_count": len(duplicate_pre_race_keys),
        "confirmed_not_in_pre_count": len(confirmed_not_in_pre),
    },
    "duplicate_pre_race_keys": duplicate_pre_race_keys,
    "confirmed_not_in_pre": confirmed_not_in_pre,
    "training_races": dict(sorted(joined.items())),
    "pending_races": dict(sorted(pending_matches.items())),
    "no_result_connection_races": dict(sorted(no_result.items())),
}

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print()
print("=== 190 結果 ===")
print(f"レース前データ: {len(pre_races)}")
print(f"確定結果と結合成功: {len(joined)}")
print(f"PENDINGとして接続: {len(pending_matches)}")
print(f"結果接続なし: {len(no_result)}")
print(f"レース前race_key重複: {len(duplicate_pre_race_keys)}")
print(f"163に存在しないCONFIRMED: {len(confirmed_not_in_pre)}")

print()
if no_result:
    print("=== 結果接続なし一覧 ===")
    for race_key in sorted(no_result):
        print(race_key)

print()
if pending_matches:
    print("=== PENDING接続一覧 ===")
    for race_key in sorted(pending_matches):
        print(race_key)

print()
if duplicate_pre_race_keys:
    print("❌ レース前race_key重複あり")
else:
    print("✅ レース前race_key重複なし")

if confirmed_not_in_pre:
    print("⚠ 163に存在しないCONFIRMEDあり")
    for race_key in confirmed_not_in_pre:
        print(race_key)
else:
    print("✅ 全CONFIRMEDが163側race_keyに存在")

print()
print(f"保存完了: {OUTPUT_FILE}")
print("=== 190 完了 ===")
