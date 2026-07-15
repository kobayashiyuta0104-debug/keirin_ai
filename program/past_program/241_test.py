import json
from pathlib import Path
from collections import Counter

BASE = Path(r"C:\競輪AI")
SRC = BASE / "239_historical_multi_date_raw_capture_fixed.json"
OUT = BASE / "241_multi_date_raw_integrity_validation.json"

print("=== 241 複数過去日RAW 完全性・重複・接続 最終検証 ===")

with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)

def payload(d, names):
    for name in names:
        v = d.get(name)
        if isinstance(v, (dict, list)):
            return v
    return None

races = []
seen_obj = set()

for d in walk(data):
    if not isinstance(d, dict):
        continue
    race_key = d.get("race_key")
    if not isinstance(race_key, str):
        continue

    jsj006 = payload(d, ["jsj006", "JSJ006", "data006", "raw006"])
    jsj012 = payload(d, ["jsj012", "JSJ012", "data012", "raw012"])

    if jsj006 is not None and jsj012 is not None:
        marker = id(d)
        if marker not in seen_obj:
            seen_obj.add(marker)
            races.append({
                "race_key": race_key,
                "jsj006": jsj006,
                "jsj012": jsj012,
            })

def find_list_by_key(obj, key):
    if isinstance(obj, dict):
        if key in obj and isinstance(obj[key], list):
            return obj[key]
        for v in obj.values():
            r = find_list_by_key(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_list_by_key(v, key)
            if r is not None:
                return r
    return None

key_counts = Counter(r["race_key"] for r in races)
date_counts = Counter()
venue_counts = Counter()
player_count_dist = Counter()
finish_count_dist = Counter()
problems = []

for r in races:
    race_key = r["race_key"]
    parts = race_key.split("_")
    date = parts[0] if len(parts) >= 1 else "UNKNOWN"
    venue = parts[1] if len(parts) >= 2 else "UNKNOWN"

    date_counts[date] += 1
    venue_counts[f"{date}_{venue}"] += 1

    players = find_list_by_key(r["jsj006"], "sensyuTypeInfo")
    finishes = find_list_by_key(r["jsj012"], "tyakujyunItemSubData")

    pc = len(players) if isinstance(players, list) else None
    fc = len(finishes) if isinstance(finishes, list) else None

    player_count_dist[pc] += 1
    finish_count_dist[fc] += 1

    if pc is None:
        problems.append({"race_key": race_key, "problem": "JSJ006_PLAYER_LIST_NOT_FOUND"})
    if fc is None:
        problems.append({"race_key": race_key, "problem": "JSJ012_FINISH_LIST_NOT_FOUND"})
    if pc is not None and fc is not None and pc != fc:
        problems.append({
            "race_key": race_key,
            "problem": "PLAYER_FINISH_COUNT_MISMATCH",
            "player_count": pc,
            "finish_count": fc,
        })

duplicates = {k: v for k, v in key_counts.items() if v != 1}
for k, v in duplicates.items():
    problems.append({
        "race_key": k,
        "problem": "RACE_KEY_DUPLICATE",
        "count": v,
    })

expected = {
    "20260705": 83,
    "20260706": 70,
}
for date, count in expected.items():
    actual = date_counts.get(date, 0)
    if actual != count:
        problems.append({
            "date": date,
            "problem": "DATE_RACE_COUNT_MISMATCH",
            "expected": count,
            "actual": actual,
        })

result = {
    "detected_race_count": len(races),
    "unique_race_key_count": len(key_counts),
    "duplicate_race_keys": duplicates,
    "date_race_counts": dict(date_counts),
    "venue_race_counts": dict(venue_counts),
    "player_count_distribution": {str(k): v for k, v in player_count_dist.items()},
    "finish_count_distribution": {str(k): v for k, v in finish_count_dist.items()},
    "problem_count": len(problems),
    "problems": problems,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print()
print("=== 241 結果 ===")
print("検出レース数:", len(races))
print("一意race_key数:", len(key_counts))
print("race_key重複:", duplicates)
print("日付別レース数:", dict(date_counts))
print("JSJ006人数分布:", dict(player_count_dist))
print("JSJ012着順人数分布:", dict(finish_count_dist))
print("問題件数:", len(problems))

if problems:
    print()
    print("=== 問題一覧 先頭100件 ===")
    for p in problems[:100]:
        print(p)

print()
print("保存完了:", OUT)
print("=== 241 完了 ===")
