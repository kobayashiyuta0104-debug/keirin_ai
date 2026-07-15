import json
from pathlib import Path
from collections import Counter

BASE = Path(r"C:\競輪AI")
RAW = BASE / "239_historical_multi_date_raw_capture_fixed.json"
OLD_MODEL = BASE / "231_20260706_model_ready_154_features.json"
OUT = BASE / "242_20260705_06_model_ready_154_features.json"
REPORT = BASE / "242_model_ready_validation_report.json"

print("=== 242 153レース -> 154特徴量 + 正解ラベル 一括正式変換 ===")

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def norm_space(v):
    if not isinstance(v, str): return v
    return " ".join(v.replace("\u3000", " ").split())

def to_int(v):
    if v in (None, ""): return None
    try: return int(float(str(v).replace("%","").strip()))
    except: return None

def to_float(v):
    if v in (None, ""): return None
    try: return float(str(v).replace("%","").strip())
    except: return None

def money(v):
    try: return int(str(v).replace(",","").strip())
    except: return None

def walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values(): yield from walk(v)
    elif isinstance(o, list):
        for v in o: yield from walk(v)

def find_payload(holder, kind):
    for d in walk(holder):
        if not isinstance(d, dict): continue
        if kind == "006" and isinstance(d.get("sensyuTypeInfo"), list):
            return d
        if kind == "012" and "tyakujyunItemSubData" in d and "haraiGakuSubData" in d:
            return d
    return None

def collect_raw(root):
    out = {}
    for d in walk(root):
        if not isinstance(d, dict): continue
        rk = d.get("race_key")
        if not isinstance(rk, str): continue
        j6 = find_payload(d, "006")
        j12 = find_payload(d, "012")
        if j6 is not None and j12 is not None:
            out[rk] = (j6, j12)
    return out

def parse_recent(p):
    t = p.get("tyo4InfoSubData")
    if not isinstance(t, dict): t = {}
    rows = t.get("resultInfoSubData")
    if not isinstance(rows, list): rows = []
    results = []
    for x in rows:
        f = str(x.get("imgTyakuiName","")).strip()
        try: f = int(f)
        except: f = None
        results.append({"finish": f, "back": to_int(x.get("backTori"))})
    meeting = {
        "venue_code": t.get("bKeirinjyoCd"),
        "venue_name": t.get("kerinjyoName"),
        "meeting_start_date": t.get("kaisaiFirst"),
        "grade": t.get("gaiTeiGrade"),
    }
    return results, meeting

def parse_player(p):
    recent, meeting = parse_recent(p)
    return {
        "car_no": to_int(p.get("syaban")),
        "player_id": str(p.get("sensyuRegistNo","")).strip().zfill(6),
        "player_name": norm_space(p.get("sensyuName")),
        "prefecture": norm_space(p.get("huKen")),
        "previous_class": p.get("prevKyuhan"),
        "class": p.get("kyuhan"),
        "riding_style": p.get("kyakusitu"),
        "graduation_term": to_int(p.get("sotugyouki")),
        "age": to_int(p.get("age")),
        "race_score": to_float(p.get("heikinTokuten")),
        "nige_count": to_int(p.get("nigeCnt")),
        "makuri_count": to_int(p.get("makuriCnt")),
        "sashi_count": to_int(p.get("sasiCnt")),
        "mark_count": to_int(p.get("markCnt")),
        "back_count": to_int(p.get("backCnt")),
        "home_count": to_int(p.get("homeTori")),
        "start_count": to_int(p.get("stTori")),
        "win_rate": to_float(p.get("syouritu")),
        "top2_rate": to_float(p.get("rentairitu2")),
        "top3_rate": to_float(p.get("rentairitu3")),
        "recent_meeting_results": recent,
        "recent_meeting": meeting,
    }

def old_races(root):
    candidates = []
    def rec(x):
        if isinstance(x, list) and x and all(isinstance(v,dict) for v in x):
            n = sum(1 for v in x if v.get("race_key") and isinstance(v.get("features"), dict))
            if n: candidates.append((n,x))
        if isinstance(x, dict):
            for v in x.values(): rec(v)
        elif isinstance(x, list):
            for v in x: rec(v)
    rec(root)
    return max(candidates, key=lambda z:z[0])[1] if candidates else []

raw_map = collect_raw(load(RAW))
old = old_races(load(OLD_MODEL))
if not old:
    raise RuntimeError("231の154特徴量テンプレートを検出できません")

feature_order = list(old[0]["features"].keys())
print("RAWレース数:", len(raw_map))
print("231正式特徴量数:", len(feature_order))

def build_features(players):
    vals = {}
    base_fields = [
        "prefecture","previous_class","class","riding_style","graduation_term","age",
        "race_score","nige_count","makuri_count","sashi_count","mark_count","back_count",
        "home_count","start_count","win_rate","top2_rate","top3_rate"
    ]
    for slot in range(1, 8):
        p = next((x for x in players if x["car_no"] == slot), None)
        for field in base_fields:
            vals[f"p{slot}_{field}"] = p.get(field) if p else None
        recent = p.get("recent_meeting_results", []) if p else []
        for i in range(3):
            vals[f"p{slot}_recent_finish_{i+1}"] = recent[i].get("finish") if i < len(recent) else None
        meeting = p.get("recent_meeting", {}) if p else {}
        vals[f"p{slot}_recent_venue_code"] = meeting.get("venue_code")
        vals[f"p{slot}_recent_meeting_start_date"] = meeting.get("meeting_start_date")
        vals[f"p{slot}_recent_grade"] = meeting.get("grade")
    return {k: vals.get(k) for k in feature_order}

results = []
problems = []
dist = Counter()
vehicle_dist = Counter()

for rk in sorted(raw_map):
    j6, j12 = raw_map[rk]
    players = [parse_player(p) for p in j6.get("sensyuTypeInfo", [])]
    players.sort(key=lambda x: x["car_no"] if x["car_no"] is not None else 99)
    vehicle_dist[len(players)] += 1

    harai = j12.get("haraiGakuSubData") or {}
    rt3 = harai.get("RT3HaraiGakuDispItemSubData") or []
    item = next((x for x in rt3 if isinstance(x,dict) and x.get("kumiBan") and money(x.get("haraiGaku")) is not None), None)
    if item is None:
        problems.append({"race_key":rk, "problem":"TRIFECTA_NOT_FOUND"})
        continue

    payout = money(item["haraiGaku"])
    if payout < 10000: label = "UNDER_10000"
    elif payout < 20000: label = "10000_TO_19999"
    elif payout < 50000: label = "20000_TO_49999"
    else: label = "50000_PLUS"
    dist[label] += 1

    features = build_features(players)
    if len(features) != 154:
        problems.append({"race_key":rk, "problem":"FEATURE_COUNT", "count":len(features)})

    results.append({
        "race_key": rk,
        "player_count": len(players),
        "features": features,
        "labels": {
            "trifecta_combination": item["kumiBan"],
            "trifecta_payout": payout,
            "payout_class_4": label,
            "is_20000_plus": int(payout >= 20000),
            "is_50000_plus": int(payout >= 50000),
        }
    })

OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

report = {
    "raw_race_count": len(raw_map),
    "generated_race_count": len(results),
    "formal_feature_count": len(feature_order),
    "feature_order": feature_order,
    "vehicle_distribution": dict(vehicle_dist),
    "label_distribution": dict(dist),
    "problem_count": len(problems),
    "problems": problems,
}
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

print()
print("=== 242 結果 ===")
print("対象RAWレース数:", len(raw_map))
print("生成レース数:", len(results))
print("正式特徴量数:", len(feature_order))
print("154特徴量レース数:", sum(len(r["features"]) == 154 for r in results))
print("車立て分布:", dict(sorted(vehicle_dist.items())))
print("4分類分布:", dict(dist))
print("2万円以上:", sum(r["labels"]["is_20000_plus"] for r in results))
print("5万円以上:", sum(r["labels"]["is_50000_plus"] for r in results))
print("問題件数:", len(problems))

if results:
    r = results[0]
    print()
    print("=== 先頭1レース確認 ===")
    print("race_key:", r["race_key"])
    print("player_count:", r["player_count"])
    print("features数:", len(r["features"]))
    print("labels:", r["labels"])

if problems:
    print()
    print("=== 問題一覧 先頭100件 ===")
    for p in problems[:100]: print(p)

print()
print("保存完了:", OUT)
print("検証保存:", REPORT)
print("=== 242 完了 ===")
