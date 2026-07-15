import json
from collections import Counter
from pathlib import Path

print("=== 215 JSJ006 生フィールド・154特徴量対応構造 完全解析 ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "213_20260706_all_race_raw_capture.json"
OUTPUT_FILE = BASE_DIR / "215_jsj006_raw_field_mapping_analysis.json"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_race_records(obj):
    found = []

    def walk(x, path="$"):
        if isinstance(x, dict):
            keys = set(x.keys())
            has_006 = any(k in keys for k in ("jsj006", "JSJ006", "data006", "pre_race"))
            has_012 = any(k in keys for k in ("jsj012", "JSJ012", "data012", "result"))
            if has_006 and has_012:
                found.append((path, x))
                return
            for k, v in x.items():
                walk(v, f"{path}.{k}")
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, f"{path}[{i}]")

    walk(obj)
    return found


def pick(d, *names):
    if not isinstance(d, dict):
        return None
    for name in names:
        if name in d:
            return d[name]
    return None


raw = load_json(INPUT_FILE)
records = find_race_records(raw)

print(f"検出レース数: {len(records)}")

all_players = []
samples = []
top_key_counts = Counter()
player_key_counts = Counter()
kon_key_counts = Counter()
tyo4_key_counts = Counter()
kon_lengths = Counter()
tyo4_lengths = Counter()

for source_path, rec in records:
    race_key = pick(rec, "race_key", "raceKey", "key")
    jsj006 = pick(rec, "jsj006", "JSJ006", "data006", "pre_race")

    if not isinstance(jsj006, dict):
        continue

    top_key_counts.update(jsj006.keys())
    players = jsj006.get("sensyuTypeInfo", [])

    if not isinstance(players, list):
        continue

    for p in players:
        if not isinstance(p, dict):
            continue

        all_players.append((race_key, p))
        player_key_counts.update(p.keys())

        kon = p.get("konResultInfoSubData", [])
        tyo4 = p.get("tyo4InfoSubData", [])

        if isinstance(kon, list):
            kon_lengths[len(kon)] += 1
            for item in kon:
                if isinstance(item, dict):
                    kon_key_counts.update(item.keys())

        if isinstance(tyo4, list):
            tyo4_lengths[len(tyo4)] += 1
            for item in tyo4:
                if isinstance(item, dict):
                    tyo4_key_counts.update(item.keys())

        if len(samples) < 12:
            samples.append({
                "race_key": race_key,
                "player": p,
            })

mapping_candidates = {
    "car_no": "syaban",
    "player_id": "sensyuRegistNo",
    "player_name": "sensyuName",
    "prefecture": "huKen",
    "previous_class": "prevKyuhan",
    "class": "kyuhan",
    "riding_style": "kyakusitu",
    "graduation_term": "sotugyouki",
    "age": "age",
    "race_score": "heikinTokuten",
    "nige_count": "nigeCnt",
    "makuri_count": "makuriCnt",
    "sashi_count": "sasiCnt",
    "mark_count": "markCnt",
    "back_count": "backCnt",
    "home_count": "homeTori",
    "start_count": "stTori",
    "win_rate": "syouritu",
    "top2_rate": "rentairitu2",
    "top3_rate": "rentairitu3",
    "recent_meeting_results": "konResultInfoSubData",
    "recent_meeting": "tyo4InfoSubData",
}

mapping_check = {}
for target, source in mapping_candidates.items():
    present = sum(1 for _, p in all_players if source in p)
    nonempty = sum(
        1 for _, p in all_players
        if source in p and p.get(source) not in (None, "", [], {})
    )
    mapping_check[target] = {
        "source_field": source,
        "present_count": present,
        "nonempty_count": nonempty,
        "total_players": len(all_players),
    }

output = {
    "race_count": len(records),
    "player_sample_count": len(all_players),
    "jsj006_top_key_counts": dict(top_key_counts),
    "player_key_counts": dict(player_key_counts),
    "konResultInfoSubData_length_distribution": dict(sorted(kon_lengths.items())),
    "konResultInfoSubData_key_counts": dict(kon_key_counts),
    "tyo4InfoSubData_length_distribution": dict(sorted(tyo4_lengths.items())),
    "tyo4InfoSubData_key_counts": dict(tyo4_key_counts),
    "mapping_candidates": mapping_check,
    "samples": samples,
}

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print()
print("=== 215 結果 ===")
print(f"レース数: {len(records)}")
print(f"解析選手数: {len(all_players)}")

print()
print("=== JSJ006 TOPキー ===")
for key, count in top_key_counts.items():
    print(f"{key}: {count}")

print()
print("=== sensyuTypeInfo 選手キー ===")
for key, count in player_key_counts.items():
    print(f"{key}: {count}/{len(all_players)}")

print()
print("=== 195形式への対応候補 ===")
for target, info in mapping_check.items():
    print(
        f"{target} <- {info['source_field']} / "
        f"存在={info['present_count']}/{info['total_players']} / "
        f"非空={info['nonempty_count']}/{info['total_players']}"
    )

print()
print("=== konResultInfoSubData ===")
print(f"件数分布: {dict(sorted(kon_lengths.items()))}")
print("内部キー:")
for key, count in kon_key_counts.items():
    print(f"  {key}: {count}")

print()
print("=== tyo4InfoSubData ===")
print(f"件数分布: {dict(sorted(tyo4_lengths.items()))}")
print("内部キー:")
for key, count in tyo4_key_counts.items():
    print(f"  {key}: {count}")

print()
print("=== 選手実データサンプル 先頭12人 ===")
for i, sample in enumerate(samples, 1):
    print()
    print("=" * 70)
    print(f"[SAMPLE {i}] race_key: {sample['race_key']}")
    print(json.dumps(sample["player"], ensure_ascii=False, indent=2))

print()
print(f"保存完了: {OUTPUT_FILE}")
print("=== 215 完了 ===")
