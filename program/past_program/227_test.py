import json
from pathlib import Path
from collections import Counter

SRC = Path(r"C:\競輪AI\213_20260706_all_race_raw_capture.json")
OUT = Path(r"C:\競輪AI\227_20260706_pre_race_features.json")

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

def find_races(o, out):
    if isinstance(o, dict):
        rk = o.get("race_key")
        jsj006 = None
        for k, v in o.items():
            if isinstance(v, dict) and isinstance(v.get("sensyuTypeInfo"), list):
                jsj006 = v
                break
        if rk and jsj006:
            out.append((rk, o, jsj006))
            return
        for v in o.values(): find_races(v, out)
    elif isinstance(o, list):
        for v in o: find_races(v, out)

def parse_recent(raw):
    t = raw.get("tyo4InfoSubData")
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
    recent_results, recent_meeting = parse_recent(p)
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
        "current_meeting_results": [],
        "recent_meeting_results": recent_results,
        "recent_meeting": recent_meeting,
    }

def main():
    print("=== 227 213 RAW -> 20260706 レース前能力データ正式再生成 ===")
    data = json.loads(SRC.read_text(encoding="utf-8"))
    found = []
    find_races(data, found)

    races = []
    problems = []
    counts = Counter()

    for rk, holder, jsj006 in found:
        players_raw = jsj006.get("sensyuTypeInfo", [])
        players = [parse_player(p) for p in players_raw]
        players.sort(key=lambda x: x["car_no"] if x["car_no"] is not None else 99)

        parts = rk.split("_")
        race_date = parts[0] if parts else "20260706"
        venue = parts[1] if len(parts) >= 2 else None
        race_no_text = parts[2] if len(parts) >= 3 else None
        race_no = to_int(str(race_no_text).replace("R","")) if race_no_text else None

        ids = [p["player_id"] for p in players]
        counts[len(players)] += 1
        if len(ids) != len(set(ids)):
            problems.append({"race_key": rk, "problem": "DUPLICATE_PLAYER_ID"})
        if any(not x for x in ids):
            problems.append({"race_key": rk, "problem": "EMPTY_PLAYER_ID"})

        races.append({
            "venue": venue,
            "race_no": race_no,
            "race_key": rk,
            "player_count": len(players),
            "players": players,
            "race_date": race_date,
        })

    races.sort(key=lambda r: (r["race_key"].split("_")[1], r["race_no"] or 0))
    OUT.write_text(json.dumps(races, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== 227 結果 ===")
    print("検出RAWレース数:", len(found))
    print("生成レース数:", len(races))
    print("車立て分布:", dict(sorted(counts.items())))
    print("生成選手総数:", sum(len(r["players"]) for r in races))
    print("問題件数:", len(problems))
    print("保存完了:", OUT)

    if races:
        r = races[0]
        p = r["players"][0]
        print("\n=== 先頭1レース確認 ===")
        print("race_key:", r["race_key"])
        print("player_count:", r["player_count"])
        print("先頭選手:", p["car_no"], p["player_id"], p["player_name"])
        print("race_score:", p["race_score"])
        print("recent_meeting_results:", p["recent_meeting_results"])
        print("recent_meeting:", p["recent_meeting"])

    if problems:
        print("\n=== 問題一覧 先頭30件 ===")
        for x in problems[:30]: print(x)

    print("=== 227 完了 ===")

if __name__ == "__main__":
    main()
