import json
from pathlib import Path
from collections import Counter, defaultdict

OLD_PATH = Path(r"C:\競輪AI\163_dated_ai_pre_race_features.json")
RAW_PATH = Path(r"C:\競輪AI\181_verified_jsj006_capture.json")
OUTPUT_PATH = Path(r"C:\競輪AI\224_recent_meeting_source_analysis.json")

TARGET_FIELDS = ["venue_code", "venue_name", "meeting_start_date", "grade"]

def norm_id(v):
    if v is None:
        return None
    s = str(v).strip()
    return s.zfill(6) if s.isdigit() else s

def find_race_key(obj):
    if isinstance(obj, dict):
        if obj.get("race_key"):
            return obj["race_key"]
        for v in obj.values():
            r = find_race_key(v)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_race_key(v)
            if r:
                return r
    return None

def find_players(obj):
    if isinstance(obj, dict):
        x = obj.get("sensyuTypeInfo")
        if isinstance(x, list):
            return x
        for v in obj.values():
            r = find_players(v)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_players(v)
            if r is not None:
                return r
    return None

def get_old_races(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in ("races", "data", "features"):
            if isinstance(data.get(k), list):
                return data[k]
        vals = [v for v in data.values() if isinstance(v, dict)]
        if vals and any(find_race_key(v) for v in vals):
            return vals
    return []

def find_old_players(race):
    if isinstance(race, dict):
        for k in ("players", "sensyu", "riders"):
            if isinstance(race.get(k), list):
                return race[k]
        for v in race.values():
            if isinstance(v, (dict, list)):
                r = find_old_players(v)
                if r:
                    return r
    elif isinstance(race, list):
        if race and all(isinstance(x, dict) for x in race):
            if any(("player_id" in x or "recent_meeting" in x) for x in race):
                return race
        for v in race:
            if isinstance(v, (dict, list)):
                r = find_old_players(v)
                if r:
                    return r
    return []

def flatten_scalars(obj, prefix="$"):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}"
            if isinstance(v, (dict, list)):
                out.extend(flatten_scalars(v, p))
            else:
                out.append((p, v))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{prefix}[{i}]"
            if isinstance(v, (dict, list)):
                out.extend(flatten_scalars(v, p))
            else:
                out.append((p, v))
    return out

def canon(v):
    if v is None:
        return None
    return str(v).replace(" ", "").replace("　", "").strip()

def main():
    print("=== 224 recent_meeting 4項目 JSJ006生成元探索テスト ===")

    with OLD_PATH.open("r", encoding="utf-8") as f:
        old_data = json.load(f)
    with RAW_PATH.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)

    raw_map = {}
    captures = raw_data.get("captures", []) if isinstance(raw_data, dict) else []
    for cap in captures:
        rk = find_race_key(cap)
        players = find_players(cap)
        if rk and isinstance(players, list):
            raw_map[rk] = {
                norm_id(p.get("sensyuRegistNo")): p
                for p in players
                if isinstance(p, dict) and norm_id(p.get("sensyuRegistNo"))
            }

    comparisons = 0
    target_nonempty = Counter()
    exact_path_hits = {f: Counter() for f in TARGET_FIELDS}
    sample_rows = []
    tyo4_keys = Counter()
    result_row_keys = Counter()

    for race in get_old_races(old_data):
        rk = find_race_key(race)
        if not rk or rk not in raw_map:
            continue

        for op in find_old_players(race):
            if not isinstance(op, dict):
                continue
            pid = norm_id(op.get("player_id") or op.get("sensyuRegistNo"))
            rp = raw_map[rk].get(pid)
            if rp is None:
                continue

            old_meeting = op.get("recent_meeting")
            if not isinstance(old_meeting, dict):
                continue

            comparisons += 1
            for f in TARGET_FIELDS:
                if old_meeting.get(f) not in (None, ""):
                    target_nonempty[f] += 1

            tyo4 = rp.get("tyo4InfoSubData")
            if isinstance(tyo4, dict):
                tyo4_keys.update(tyo4.keys())
                rows = tyo4.get("resultInfoSubData")
                if isinstance(rows, list):
                    for row in rows:
                        if isinstance(row, dict):
                            result_row_keys.update(row.keys())

            scalars = flatten_scalars(rp)
            field_hits = {}
            for f in TARGET_FIELDS:
                target = old_meeting.get(f)
                hits = []
                if target not in (None, ""):
                    ct = canon(target)
                    for path, value in scalars:
                        if value not in (None, "") and canon(value) == ct:
                            hits.append({"path": path, "value": value})
                            exact_path_hits[f][path] += 1
                field_hits[f] = hits

            if len(sample_rows) < 30:
                sample_rows.append({
                    "race_key": rk,
                    "player_id": pid,
                    "player_name": op.get("player_name") or op.get("sensyuName"),
                    "old_recent_meeting": old_meeting,
                    "tyo4InfoSubData": tyo4,
                    "exact_hits": field_hits,
                })

    print("\n=== 224 結果 ===")
    print("比較選手数:", comparisons)
    print("recent_meeting 非空件数:", dict(target_nonempty))

    print("\n=== tyo4InfoSubData キー出現回数 ===")
    for k, n in tyo4_keys.most_common():
        print(f"  {k}: {n}")

    print("\n=== resultInfoSubData 行キー出現回数 ===")
    for k, n in result_row_keys.most_common():
        print(f"  {k}: {n}")

    print("\n=== OLD 4項目とRAW値の完全一致PATHランキング ===")
    for f in TARGET_FIELDS:
        print(f"\n[{f}]")
        if exact_path_hits[f]:
            for path, n in exact_path_hits[f].most_common(20):
                print(f"  {n}件一致 / {path}")
        else:
            print("  完全一致PATHなし")

    print("\n=== サンプル先頭10選手 ===")
    for i, x in enumerate(sample_rows[:10], 1):
        print("\n" + "=" * 80)
        print(f"[{i}] {x['race_key']} / {x['player_id']} / {x['player_name']}")
        print("OLD recent_meeting:")
        print(json.dumps(x["old_recent_meeting"], ensure_ascii=False, indent=2))
        print("RAW tyo4InfoSubData:")
        print(json.dumps(x["tyo4InfoSubData"], ensure_ascii=False, indent=2))
        print("完全一致HIT:")
        print(json.dumps(x["exact_hits"], ensure_ascii=False, indent=2))

    output = {
        "comparisons": comparisons,
        "target_nonempty": dict(target_nonempty),
        "tyo4_keys": dict(tyo4_keys),
        "result_row_keys": dict(result_row_keys),
        "exact_path_hits": {
            f: [{"path": p, "count": n} for p, n in exact_path_hits[f].most_common()]
            for f in TARGET_FIELDS
        },
        "samples": sample_rows,
    }

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n保存完了: {OUTPUT_PATH}")
    print("=== 224 完了 ===")

if __name__ == "__main__":
    main()
