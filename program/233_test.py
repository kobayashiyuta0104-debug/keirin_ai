import json
from pathlib import Path
from collections import Counter

SRC = Path(r"C:\競輪AI\231_20260706_model_ready_154_features.json")
OUT = Path(r"C:\競輪AI\233_missing_semantics_validation.json")

def main():
    print("=== 233 欠損値 正常意味検証・recent_finish対応確認 ===")

    with open(SRC, "r", encoding="utf-8") as f:
        data = json.load(f)

    races = data.get("races", [])
    problems = []
    structural_ok = 0
    recent_missing_ok = 0
    recent_present_ok = 0
    recent_pattern = Counter()

    for race in races:
        race_key = race.get("race_key")
        player_count = int(race.get("player_count", 0))
        features = race.get("features", {})

        # 存在しない車番枠 p(player_count+1)～p7 が全22特徴量 None か確認
        for p in range(player_count + 1, 8):
            cols = [k for k in features if k.startswith(f"p{p}_")]
            bad = [k for k in cols if features.get(k) is not None]
            if bad:
                problems.append({
                    "race_key": race_key,
                    "type": "STRUCTURAL_SLOT_NOT_NONE",
                    "player": p,
                    "columns": bad,
                })
            else:
                structural_ok += 1

        # 実在選手の recent_finish_1～3 の欠損パターンを検証
        # 正常形は、途中だけ抜けず「値...値,None...None」の連続形
        for p in range(1, player_count + 1):
            vals = [
                features.get(f"p{p}_recent_finish_1"),
                features.get(f"p{p}_recent_finish_2"),
                features.get(f"p{p}_recent_finish_3"),
            ]

            pattern = tuple(v is None for v in vals)
            recent_pattern[str(pattern)] += 1

            seen_none = False
            bad_gap = False
            for v in vals:
                if v is None:
                    seen_none = True
                    recent_missing_ok += 1
                else:
                    recent_present_ok += 1
                    if seen_none:
                        bad_gap = True

            if bad_gap:
                problems.append({
                    "race_key": race_key,
                    "type": "RECENT_FINISH_GAP",
                    "player": p,
                    "values": vals,
                })

        # 実在選手の recent_finish以外がNoneなら異常候補
        for p in range(1, player_count + 1):
            for key, value in features.items():
                if not key.startswith(f"p{p}_"):
                    continue
                if value is None and "recent_finish_" not in key:
                    problems.append({
                        "race_key": race_key,
                        "type": "REAL_PLAYER_NON_RECENT_MISSING",
                        "player": p,
                        "column": key,
                    })

    print("\n=== 233 結果 ===")
    print("対象レース数:", len(races))
    print("構造欠損スロット正常数:", structural_ok)
    print("recent_finish 欠損セル数:", recent_missing_ok)
    print("recent_finish 値ありセル数:", recent_present_ok)
    print("問題件数:", len(problems))

    print("\n=== recent_finish 欠損パターン分布 ===")
    for pattern, cnt in recent_pattern.most_common():
        print(f"{pattern}: {cnt}")

    print("\n=== 問題一覧 先頭100件 ===")
    for x in problems[:100]:
        print(x)

    report = {
        "source_file": str(SRC),
        "race_count": len(races),
        "structural_slot_ok_count": structural_ok,
        "recent_finish_missing_cell_count": recent_missing_ok,
        "recent_finish_present_cell_count": recent_present_ok,
        "recent_finish_pattern_distribution": dict(recent_pattern),
        "problem_count": len(problems),
        "problems": problems,
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n保存完了:", OUT)
    print("=== 233 完了 ===")

if __name__ == "__main__":
    main()
