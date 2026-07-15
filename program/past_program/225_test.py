import json
from pathlib import Path
from collections import Counter

OLD_PATH = Path(r"C:\競輪AI\163_dated_ai_pre_race_features.json")
RAW_PATH = Path(r"C:\競輪AI\181_verified_jsj006_capture.json")
OUT_PATH = Path(r"C:\競輪AI\225_jsj006_to_163_full_exact_compare.json")

FIELD_MAP = {
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
}

INT_FIELDS = {
    "car_no", "graduation_term", "age", "nige_count", "makuri_count",
    "sashi_count", "mark_count", "back_count", "home_count", "start_count"
}
FLOAT_FIELDS = {"race_score", "win_rate", "top2_rate", "top3_rate"}

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

def find_raw_players(obj):
    if isinstance(obj, dict):
        if isinstance(obj.get("sensyuTypeInfo"), list):
            return obj["sensyuTypeInfo"]
        for v in obj.values():
            r = find_raw_players(v)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_raw_players(v)
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

def get_old_players(race):
    if not isinstance(race, dict):
        return []
    for k in ("players", "sensyu", "riders"):
        if isinstance(race.get(k), list):
            return race[k]
    return []

def conv(v, field):
    if v in (None, ""):
        return None
    try:
        if field in INT_FIELDS:
            return int(float(str(v).replace("%", "").strip()))
        if field in FLOAT_FIELDS:
            return float(str(v).replace("%", "").strip())
    except Exception:
        return v
    return v

def conv_finish(v):
    if v in (None, ""):
        return None
    s = str(v).strip()
    return int(s) if s.isdigit() else None

def conv_back(v):
    if v in (None, ""):
        return None
    try:
        return int(v)
    except Exception:
        return None

def norm_id(v):
    if v is None:
        return None
    s = str(v).strip()
    return s.zfill(6) if s.isdigit() else s

def build_player(raw):
    out = {}
    for old_key, raw_key in FIELD_MAP.items():
        out[old_key] = conv(raw.get(raw_key), old_key)

    recent = raw.get("tyo4InfoSubData")
    if not isinstance(recent, dict):
        recent = {}

    rows = recent.get("resultInfoSubData")
    if not isinstance(rows, list):
        rows = []

    out["recent_meeting_results"] = [
        {
            "finish": conv_finish(x.get("imgTyakuiName")),
            "back": conv_back(x.get("backTori")),
        }
        for x in rows if isinstance(x, dict)
    ]

    out["recent_meeting"] = {
        "venue_code": recent.get("bKeirinjyoCd"),
        "venue_name": recent.get("kerinjyoName"),
        "meeting_start_date": recent.get("kaisaiFirst"),
        "grade": recent.get("gaiTeiGrade"),
    }
    return out

def main():
    print("=== 225 JSJ006 RAW -> 163形式 全フィールド完全再生成検証 ===")

    old_data = json.loads(OLD_PATH.read_text(encoding="utf-8"))
    raw_data = json.loads(RAW_PATH.read_text(encoding="utf-8"))

    raw_map = {}
    for cap in raw_data.get("captures", []):
        rk = find_race_key(cap)
        players = find_raw_players(cap)
        if rk and isinstance(players, list):
            raw_map[rk] = {
                norm_id(p.get("sensyuRegistNo")): p
                for p in players
                if isinstance(p, dict)
            }

    compared_players = 0
    exact_players = 0
    field_compare = Counter()
    field_match = Counter()
    mismatches = []
    missing_raw = 0

    compare_fields = list(FIELD_MAP.keys()) + [
        "recent_meeting_results", "recent_meeting"
    ]

    for race in get_old_races(old_data):
        rk = find_race_key(race)
        if rk not in raw_map:
            continue

        for old in get_old_players(race):
            pid = norm_id(old.get("player_id"))
            raw = raw_map[rk].get(pid)
            if raw is None:
                missing_raw += 1
                continue

            rebuilt = build_player(raw)
            compared_players += 1
            player_diff = []

            for field in compare_fields:
                field_compare[field] += 1
                ov = old.get(field)
                nv = rebuilt.get(field)
                if ov == nv:
                    field_match[field] += 1
                else:
                    player_diff.append({
                        "field": field,
                        "old": ov,
                        "rebuilt": nv,
                    })

            if not player_diff:
                exact_players += 1
            elif len(mismatches) < 200:
                mismatches.append({
                    "race_key": rk,
                    "player_id": pid,
                    "player_name": old.get("player_name"),
                    "diff": player_diff,
                })

    print("\n=== 225 結果 ===")
    print("比較選手数:", compared_players)
    print("全フィールド完全一致選手:", exact_players)
    print("完全一致率:", f"{exact_players / compared_players * 100:.2f}%" if compared_players else "0%")
    print("RAW選手ID未発見:", missing_raw)
    print("不一致選手数:", compared_players - exact_players)

    print("\n=== フィールド別一致率 ===")
    for field in compare_fields:
        a = field_match[field]
        b = field_compare[field]
        rate = a / b * 100 if b else 0
        print(f"{field}: {a}/{b} = {rate:.2f}%")

    print("\n=== 不一致サンプル 先頭50 ===")
    for x in mismatches[:50]:
        print("\n" + "=" * 80)
        print(x["race_key"], "/", x["player_id"], "/", x["player_name"])
        for d in x["diff"]:
            print("FIELD:", d["field"])
            print("  OLD    :", repr(d["old"]))
            print("  REBUILT:", repr(d["rebuilt"]))

    result = {
        "compared_players": compared_players,
        "exact_players": exact_players,
        "exact_rate": exact_players / compared_players if compared_players else 0,
        "missing_raw": missing_raw,
        "field_stats": {
            f: {
                "match": field_match[f],
                "compare": field_compare[f],
                "rate": field_match[f] / field_compare[f] if field_compare[f] else 0,
            }
            for f in compare_fields
        },
        "mismatches": mismatches,
    }

    OUT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\n保存完了: {OUT_PATH}")
    print("=== 225 完了 ===")

if __name__ == "__main__":
    main()
