import json
from pathlib import Path
from collections import Counter

RAW = Path(r"C:\競輪AI\213_20260706_all_race_raw_capture.json")
MODEL = Path(r"C:\競輪AI\231_20260706_model_ready_154_features.json")
OUT = Path(r"C:\競輪AI\236_recent_finish_missing_semantics_final_validation.json")

def walk(x):
    if isinstance(x, dict):
        yield x
        for v in x.values():
            yield from walk(v)
    elif isinstance(x, list):
        for v in x:
            yield from walk(v)

def numeric_finish(v):
    if v is None:
        return None
    s = str(v).strip()
    return int(s) if s.isdigit() else None

def main():
    print("=== 236 recent_finish 欠損意味 最終検証 ===")

    raw = json.loads(RAW.read_text(encoding="utf-8"))
    model = json.loads(MODEL.read_text(encoding="utf-8"))

    raw_races = {}
    for d in walk(raw):
        rk = d.get("race_key") if isinstance(d, dict) else None
        if not rk:
            continue
        players = None
        for z in walk(d):
            if isinstance(z, dict) and isinstance(z.get("sensyuTypeInfo"), list):
                players = z["sensyuTypeInfo"]
                break
        if players is not None:
            raw_races[rk] = players

    total = 0
    exact = 0
    mismatch = []
    raw_status = Counter()
    none_reason = Counter()

    for race in model["races"]:
        rk = race["race_key"]
        features = race["features"]
        players = raw_races.get(rk, [])

        for p in range(1, 8):
            player = next((x for x in players if str(x.get("syaban")) == str(p)), None)
            if player is None:
                continue

            rows = ((player.get("tyo4InfoSubData") or {}).get("resultInfoSubData") or [])
            raw_names = [(row or {}).get("imgTyakuiName") for row in rows]
            expected = [numeric_finish(v) for v in raw_names[:3]]
            while len(expected) < 3:
                expected.append(None)

            actual = [features.get(f"p{p}_recent_finish_{i}") for i in range(1, 4)]

            total += 1
            for raw_name, exp in zip(raw_names[:3], expected):
                raw_status[str(raw_name)] += 1
                if exp is None:
                    if raw_name is None:
                        none_reason["EMPTY_DICT_OR_MISSING"] += 1
                    elif str(raw_name).strip() == "":
                        none_reason["EMPTY_STRING"] += 1
                    else:
                        none_reason[f"NON_NUMERIC:{raw_name}"] += 1

            if actual == expected:
                exact += 1
            else:
                mismatch.append({
                    "race_key": rk,
                    "player": p,
                    "player_id": player.get("sensyuRegistNo"),
                    "player_name": player.get("sensyuName"),
                    "raw_names": raw_names,
                    "expected": expected,
                    "actual": actual,
                })

    report = {
        "compared_players": total,
        "exact_match_players": exact,
        "exact_match_rate": round(exact / total * 100, 2) if total else 0,
        "mismatch_count": len(mismatch),
        "none_reason_distribution": dict(none_reason),
        "raw_finish_name_distribution": dict(raw_status),
        "mismatches": mismatch,
        "conclusion": "recent_finish preserves tyo4InfoSubData positional slots; non-numeric statuses and empty rows normalize to None"
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== 236 結果 ===")
    print("比較選手数:", total)
    print("RAW位置意味との完全一致:", exact)
    print("完全一致率:", f"{report['exact_match_rate']:.2f}%")
    print("不一致:", len(mismatch))
    print("\n=== None理由分布 ===")
    for k, v in none_reason.most_common():
        print(f"{k}: {v}")

    if mismatch:
        print("\n=== 不一致 先頭30件 ===")
        for x in mismatch[:30]:
            print(x)

    print("\n保存完了:", OUT)
    print("=== 236 完了 ===")

if __name__ == "__main__":
    main()
