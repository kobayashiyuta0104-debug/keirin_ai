import json
from collections import Counter, defaultdict
from pathlib import Path

print("=== 214 213全70レース 車立て・JSJ006/JSJ012接続構造解析 ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "213_20260706_all_race_raw_capture.json"
OUTPUT_FILE = BASE_DIR / "214_213_structure_and_player_count_analysis.json"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def normalize_id(value):
    if value is None:
        return None
    s = str(value).strip()
    return s.zfill(6) if s else None


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


def find_player_list(jsj006):
    candidates = []

    def walk(x, path="$"):
        if isinstance(x, list):
            dicts = [v for v in x if isinstance(v, dict)]
            if dicts:
                score = 0
                all_keys = set()
                for d in dicts:
                    all_keys.update(d.keys())
                id_keys = {"sensyuRegistNo", "sensyuNo", "player_id", "sensyuId"}
                car_keys = {"syaban", "car_no", "syabanNo"}
                if all_keys & id_keys:
                    score += 5
                if all_keys & car_keys:
                    score += 5
                if 4 <= len(dicts) <= 9:
                    score += 3
                if score:
                    candidates.append((score, len(dicts), path, x, sorted(all_keys)))
            for i, v in enumerate(x):
                walk(v, f"{path}[{i}]")
        elif isinstance(x, dict):
            for k, v in x.items():
                walk(v, f"{path}.{k}")

    walk(jsj006)
    if not candidates:
        return None, None, []
    candidates.sort(key=lambda t: (t[0], t[1]), reverse=True)
    _, _, path, values, keys = candidates[0]
    return path, values, keys


def find_finish_list(jsj012):
    if isinstance(jsj012, dict):
        rows = jsj012.get("tyakujyunItemSubData")
        if isinstance(rows, list):
            return "$.tyakujyunItemSubData", rows

    candidates = []

    def walk(x, path="$"):
        if isinstance(x, list):
            dicts = [v for v in x if isinstance(v, dict)]
            if dicts:
                keys = set()
                for d in dicts:
                    keys.update(d.keys())
                score = 0
                if "sensyuRegistNo" in keys:
                    score += 5
                if "syaban" in keys:
                    score += 5
                if "tyaku" in keys:
                    score += 5
                if score:
                    candidates.append((score, len(dicts), path, x))
            for i, v in enumerate(x):
                walk(v, f"{path}[{i}]")
        elif isinstance(x, dict):
            for k, v in x.items():
                walk(v, f"{path}.{k}")

    walk(jsj012)
    if not candidates:
        return None, None
    candidates.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return candidates[0][2], candidates[0][3]


raw = load_json(INPUT_FILE)
records = find_race_records(raw)

print(f"検出レース候補数: {len(records)}")

analyses = []
player_count_dist = Counter()
venue_count_dist = defaultdict(Counter)
id_complete = 0
count_match = 0
problems = []

for index, (source_path, rec) in enumerate(records, 1):
    race_key = pick(rec, "race_key", "raceKey", "key")
    venue = pick(rec, "venue", "jyoName", "venue_name")
    race_no = pick(rec, "race_no", "raceNo", "race_number")

    jsj006 = pick(rec, "jsj006", "JSJ006", "data006", "pre_race")
    jsj012 = pick(rec, "jsj012", "JSJ012", "data012", "result")

    p_path, players, player_keys = find_player_list(jsj006)
    f_path, finishes = find_finish_list(jsj012)

    player_count = len(players) if isinstance(players, list) else 0
    finish_count = len(finishes) if isinstance(finishes, list) else 0

    player_count_dist[player_count] += 1
    venue_count_dist[str(venue)][player_count] += 1

    player_ids = set()
    if isinstance(players, list):
        for p in players:
            if not isinstance(p, dict):
                continue
            pid = normalize_id(
                p.get("sensyuRegistNo")
                or p.get("sensyuNo")
                or p.get("player_id")
                or p.get("sensyuId")
            )
            if pid:
                player_ids.add(pid)

    finish_ids = set()
    if isinstance(finishes, list):
        for f in finishes:
            if not isinstance(f, dict):
                continue
            pid = normalize_id(f.get("sensyuRegistNo") or f.get("player_id"))
            if pid:
                finish_ids.add(pid)

    same_count = player_count > 0 and player_count == finish_count
    same_ids = (
        player_count > 0
        and len(player_ids) == player_count
        and len(finish_ids) == finish_count
        and player_ids == finish_ids
    )

    if same_count:
        count_match += 1
    if same_ids:
        id_complete += 1

    if not race_key:
        problems.append({"index": index, "problem": "RACE_KEY_MISSING", "source_path": source_path})
    if not players:
        problems.append({"race_key": race_key, "problem": "PLAYER_LIST_NOT_FOUND"})
    if not finishes:
        problems.append({"race_key": race_key, "problem": "FINISH_LIST_NOT_FOUND"})
    if players and finishes and not same_count:
        problems.append({
            "race_key": race_key,
            "problem": "PLAYER_FINISH_COUNT_MISMATCH",
            "player_count": player_count,
            "finish_count": finish_count,
        })
    if players and finishes and not same_ids:
        problems.append({
            "race_key": race_key,
            "problem": "PLAYER_ID_SET_MISMATCH",
            "player_ids": sorted(player_ids),
            "finish_ids": sorted(finish_ids),
        })

    analyses.append({
        "source_path": source_path,
        "race_key": race_key,
        "venue": venue,
        "race_no": race_no,
        "jsj006_player_list_path": p_path,
        "jsj006_player_keys": player_keys,
        "jsj012_finish_list_path": f_path,
        "player_count": player_count,
        "finish_count": finish_count,
        "player_finish_count_match": same_count,
        "player_id_complete_match": same_ids,
    })

out = {
    "detected_race_count": len(records),
    "player_count_distribution": dict(sorted(player_count_dist.items())),
    "player_finish_count_match_races": count_match,
    "player_id_complete_match_races": id_complete,
    "problem_count": len(problems),
    "venue_player_count_distribution": {
        venue: dict(sorted(counter.items()))
        for venue, counter in venue_count_dist.items()
    },
    "problems": problems,
    "races": analyses,
}

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print()
print("=== 214 結果 ===")
print(f"検出レース数: {len(records)}")
print(f"車立て分布: {dict(sorted(player_count_dist.items()))}")
print(f"JSJ006人数 = JSJ012着順行数: {count_match}")
print(f"選手ID完全一致レース: {id_complete}")
print(f"問題件数: {len(problems)}")

print()
print("=== 会場別 車立て分布 ===")
for venue, counter in venue_count_dist.items():
    print(f"{venue}: {dict(sorted(counter.items()))}")

if analyses:
    sample = analyses[0]
    print()
    print("=== 先頭1レース 構造確認 ===")
    print(f"race_key: {sample['race_key']}")
    print(f"JSJ006選手リストPATH: {sample['jsj006_player_list_path']}")
    print(f"JSJ006選手キー: {sample['jsj006_player_keys']}")
    print(f"JSJ012着順PATH: {sample['jsj012_finish_list_path']}")
    print(f"player_count: {sample['player_count']}")
    print(f"finish_count: {sample['finish_count']}")

if problems:
    print()
    print("=== 問題一覧 先頭30件 ===")
    for problem in problems[:30]:
        print(problem)

print()
print(f"保存完了: {OUTPUT_FILE}")
print("=== 214 完了 ===")
