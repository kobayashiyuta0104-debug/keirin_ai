import json
from pathlib import Path

RAW = Path(r"C:\競輪AI\181_verified_jsj006_capture.json")
MODEL = Path(r"C:\競輪AI\231_20260706_model_ready_154_features.json")
OUT = Path(r"C:\競輪AI\234_recent_finish_gap_raw_analysis.json")

TARGETS = {
    ("20260706_京王閣_4R", 1), ("20260706_京王閣_4R", 2),
    ("20260706_京王閣_7R", 6), ("20260706_伊東_1R", 5),
    ("20260706_伊東_2R", 3), ("20260706_伊東_4R", 1),
    ("20260706_伊東_7R", 2), ("20260706_佐世保_4R", 3),
    ("20260706_別府_6R", 1), ("20260706_取手_8R", 6),
    ("20260706_取手_9R", 1), ("20260706_取手_9R", 6),
    ("20260706_和歌山_5R", 3), ("20260706_和歌山_10R", 6),
    ("20260706_岸和田_3R", 4), ("20260706_豊橋_5R", 7),
}

def walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)

def main():
    print("=== 234 RECENT_FINISH_GAP 16選手 RAW構造直接解析 ===")

    raw = json.loads(RAW.read_text(encoding="utf-8"))
    model = json.loads(MODEL.read_text(encoding="utf-8"))

    model_races = {r["race_key"]: r for r in model.get("races", [])}

    raw_races = {}
    for d in walk(raw):
        rk = d.get("race_key")
        if rk and "sensyuTypeInfo" in d:
            raw_races[rk] = d
        elif rk:
            for x in walk(d):
                if isinstance(x, dict) and "sensyuTypeInfo" in x:
                    raw_races.setdefault(rk, x)
                    break

    results = []
    problems = []

    for race_key, p in sorted(TARGETS):
        mr = model_races.get(race_key)
        rr = raw_races.get(race_key)

        print("\n" + "=" * 80)
        print("race_key:", race_key, "/ p", p)

        if not mr:
            print("MODEL RACE NOT FOUND")
            problems.append({"race_key": race_key, "player": p, "problem": "MODEL_NOT_FOUND"})
            continue
        if not rr:
            print("RAW RACE NOT FOUND")
            problems.append({"race_key": race_key, "player": p, "problem": "RAW_NOT_FOUND"})
            continue

        f = mr["features"]
        model_vals = [f.get(f"p{p}_recent_finish_{i}") for i in range(1, 4)]

        players = rr.get("sensyuTypeInfo", [])
        player = None
        for x in players:
            try:
                if int(x.get("syaban")) == p:
                    player = x
                    break
            except:
                pass

        if player is None:
            print("RAW PLAYER NOT FOUND")
            problems.append({"race_key": race_key, "player": p, "problem": "PLAYER_NOT_FOUND"})
            continue

        print("選手:", player.get("syaban"), player.get("sensyuRegistNo"), player.get("sensyuName"))
        print("MODEL recent_finish:", model_vals)

        kon = player.get("konResultInfoSubData")
        tyo = player.get("tyo4InfoSubData")

        print("\n--- konResultInfoSubData RAW ---")
        print(json.dumps(kon, ensure_ascii=False, indent=2))

        print("\n--- tyo4InfoSubData RAW ---")
        print(json.dumps(tyo, ensure_ascii=False, indent=2))

        item = {
            "race_key": race_key,
            "player": p,
            "player_id": player.get("sensyuRegistNo"),
            "player_name": player.get("sensyuName"),
            "model_recent_finish": model_vals,
            "konResultInfoSubData": kon,
            "tyo4InfoSubData": tyo,
        }
        results.append(item)

    report = {
        "source_raw": str(RAW),
        "source_model": str(MODEL),
        "target_count": len(TARGETS),
        "analyzed_count": len(results),
        "problem_count": len(problems),
        "problems": problems,
        "results": results,
    }

    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== 234 結果 ===")
    print("対象:", len(TARGETS))
    print("解析成功:", len(results))
    print("問題件数:", len(problems))
    print("保存完了:", OUT)
    print("=== 234 完了 ===")

if __name__ == "__main__":
    main()
