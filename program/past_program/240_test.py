import json
from pathlib import Path
from collections import Counter

BASE = Path(r"C:\競輪AI")
SRC_OLD = BASE / "213_20260706_all_race_raw_capture.json"
SRC_NEW = BASE / "239_historical_multi_date_raw_capture_fixed.json"
OUT = BASE / "240_239_vs_213_20260706_exact_compare.json"

print("=== 240 239新RAW vs 213旧RAW 20260706 完全一致検証 ===")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)

def find_payload(d, names):
    for name in names:
        if name in d and isinstance(d[name], (dict, list)):
            return d[name]
    return None

def extract_races(root, target_date):
    races = {}
    for d in walk(root):
        if not isinstance(d, dict):
            continue

        race_key = d.get("race_key")
        if not isinstance(race_key, str) or not race_key.startswith(target_date + "_"):
            continue

        jsj006 = find_payload(d, ["jsj006", "JSJ006", "data006", "raw006"])
        jsj012 = find_payload(d, ["jsj012", "JSJ012", "data012", "raw012"])

        if jsj006 is not None and jsj012 is not None:
            races[race_key] = {
                "jsj006": jsj006,
                "jsj012": jsj012,
            }

    return races

old_data = load_json(SRC_OLD)
new_data = load_json(SRC_NEW)

old_races = extract_races(old_data, "20260706")
new_races = extract_races(new_data, "20260706")

print("213検出レース数:", len(old_races))
print("239検出レース数:", len(new_races))

all_keys = sorted(set(old_races) | set(new_races))

both = 0
jsj006_exact = 0
jsj012_exact = 0
both_exact = 0
problems = []
venue_dist = Counter()

for race_key in all_keys:
    old = old_races.get(race_key)
    new = new_races.get(race_key)

    parts = race_key.split("_")
    if len(parts) >= 3:
        venue_dist[parts[1]] += 1

    if old is None:
        problems.append({
            "race_key": race_key,
            "problem": "OLD_213_MISSING",
        })
        continue

    if new is None:
        problems.append({
            "race_key": race_key,
            "problem": "NEW_239_MISSING",
        })
        continue

    both += 1

    eq006 = old["jsj006"] == new["jsj006"]
    eq012 = old["jsj012"] == new["jsj012"]

    if eq006:
        jsj006_exact += 1
    if eq012:
        jsj012_exact += 1
    if eq006 and eq012:
        both_exact += 1
    else:
        problems.append({
            "race_key": race_key,
            "problem": "RAW_MISMATCH",
            "jsj006_exact": eq006,
            "jsj012_exact": eq012,
        })

result = {
    "old_213_race_count": len(old_races),
    "new_239_race_count": len(new_races),
    "common_race_count": both,
    "jsj006_exact_count": jsj006_exact,
    "jsj012_exact_count": jsj012_exact,
    "both_exact_count": both_exact,
    "problem_count": len(problems),
    "venue_distribution": dict(venue_dist),
    "problems": problems,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print()
print("=== 240 結果 ===")
print("213レース数:", len(old_races))
print("239レース数:", len(new_races))
print("共通レース数:", both)
print("JSJ006完全一致:", jsj006_exact)
print("JSJ012完全一致:", jsj012_exact)
print("JSJ006+JSJ012両方完全一致:", both_exact)
print("問題件数:", len(problems))

if problems:
    print()
    print("=== 問題一覧 先頭100件 ===")
    for p in problems[:100]:
        print(p)

print()
print("保存完了:", OUT)
print("=== 240 完了 ===")
