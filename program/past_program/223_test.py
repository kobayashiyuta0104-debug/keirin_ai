import json
from pathlib import Path
from collections import Counter

OLD_PATH = Path(r"C:\競輪AI\163_dated_ai_pre_race_features.json")
RAW_PATH = Path(r"C:\競輪AI\181_verified_jsj006_capture.json")
OUTPUT_PATH = Path(r"C:\競輪AI\223_old_recent_vs_jsj006_exact_compare.json")

def norm_id(v):
    if v is None:
        return None
    s = str(v).strip()
    return s.zfill(6) if s.isdigit() else s

def norm_finish(v):
    if v is None or v == "":
        return None
    s = str(v).strip()
    return int(s) if s.isdigit() else None

def norm_back(v):
    if v is None or v == "":
        return None
    s = str(v).strip()
    return int(s) if s.isdigit() else None

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
            r = find_old_players(v) if isinstance(v, (dict, list)) else None
            if r:
                return r
    elif isinstance(race, list):
        if race and all(isinstance(x, dict) for x in race):
            if any(("sensyuRegistNo" in x or "player_id" in x or "recent_meeting_results" in x) for x in race):
                return race
        for v in race:
            r = find_old_players(v) if isinstance(v, (dict, list)) else None
            if r:
                return r
    return []

def old_player_id(p):
    for k in ("sensyuRegistNo", "player_id", "regist_no", "registration_no"):
        if k in p:
            return norm_id(p.get(k))
    return None

def raw_player_id(p):
    return norm_id(p.get("sensyuRegistNo"))

def old_recent(p):
    x = p.get("recent_meeting_results")
    if not isinstance(x, list):
        return []
    out = []
    for row in x:
        if isinstance(row, dict):
            out.append({
                "finish": norm_finish(row.get("finish")),
                "back": norm_back(row.get("back"))
            })
    return out

def raw_recent(p):
    t = p.get("tyo4InfoSubData")
    if not isinstance(t, dict):
        return []
    rows = t.get("resultInfoSubData")
    if not isinstance(rows, list):
        return []
    out = []
    for row in rows:
        if isinstance(row, dict):
            out.append({
                "finish": norm_finish(row.get("imgTyakuiName")),
                "back": norm_back(row.get("backTori"))
            })
    return out

def main():
    print("=== 223 旧recent_meeting_results vs JSJ006 正式キー完全一致検証 ===")

    with OLD_PATH.open("r", encoding="utf-8") as f:
        old_data = json.load(f)
    with RAW_PATH.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)

    old_races = get_old_races(old_data)

    raw_map = {}
    captures = raw_data.get("captures", []) if isinstance(raw_data, dict) else []
    for cap in captures:
        rk = find_race_key(cap)
        players = find_players(cap)
        if rk and isinstance(players, list):
            raw_map[rk] = {raw_player_id(p): p for p in players if isinstance(p, dict) and raw_player_id(p)}

    compared = 0
    exact = 0
    finish_match = 0
    back_match = 0
    missing = 0
    mismatch = []
    old_count_dist = Counter()
    raw_count_dist = Counter()

    for race in old_races:
        rk = find_race_key(race)
        if not rk or rk not in raw_map:
            continue
        for p in find_old_players(race):
            if not isinstance(p, dict):
                continue
            pid = old_player_id(p)
            old = old_recent(p)
            old_count_dist[len(old)] += 1
            rp = raw_map[rk].get(pid)
            if rp is None:
                missing += 1
                continue
            raw = raw_recent(rp)
            raw_count_dist[len(raw)] += 1
            compared += 1

            fm = [x["finish"] for x in old] == [x["finish"] for x in raw]
            bm = [x["back"] for x in old] == [x["back"] for x in raw]
            ex = old == raw

            finish_match += int(fm)
            back_match += int(bm)
            exact += int(ex)

            if not ex and len(mismatch) < 100:
                mismatch.append({
                    "race_key": rk,
                    "player_id": pid,
                    "name": p.get("sensyuName") or p.get("name"),
                    "old": old,
                    "raw": raw,
                    "finish_match": fm,
                    "back_match": bm,
                })

    print("\n=== 223 結果 ===")
    print("比較成功:", compared)
    print("完全一致:", exact)
    print("finish一致:", finish_match)
    print("back一致:", back_match)
    print("JSJ006選手ID未発見:", missing)
    print("旧recent件数分布:", dict(old_count_dist))
    print("RAW recent件数分布:", dict(raw_count_dist))

    print("\n=== 不一致サンプル 先頭100 ===")
    for i, x in enumerate(mismatch, 1):
        print("\n" + "-" * 70)
        print(f"[{i}] {x['race_key']} / {x['player_id']} / {x['name']}")
        print("OLD:", x["old"])
        print("RAW:", x["raw"])
        print("FINISH MATCH:", x["finish_match"])
        print("BACK MATCH:", x["back_match"])

    output = {
        "compared": compared,
        "exact_match": exact,
        "finish_match": finish_match,
        "back_match": back_match,
        "missing_player": missing,
        "old_count_dist": dict(old_count_dist),
        "raw_count_dist": dict(raw_count_dist),
        "mismatch_samples": mismatch,
    }
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n保存完了: {OUTPUT_PATH}")
    print("=== 223 完了 ===")

if __name__ == "__main__":
    main()
