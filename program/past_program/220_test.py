import json
from pathlib import Path

def main():
    print("=== 220 181系JSON 自動探索・候補判定テスト ===")

    base = Path(r"C:\競輪AI")
    search_roots = [base, base / "result", base / "program"]

    files = []
    for root in search_roots:
        if root.exists():
            files.extend(root.rglob("*181*.json"))

    # 重複除去
    unique_files = []
    seen = set()
    for p in files:
        key = str(p.resolve()).lower()
        if key not in seen:
            seen.add(key)
            unique_files.append(p)

    print(f"181系JSON候補数: {len(unique_files)}")

    results = []

    for i, path in enumerate(unique_files, 1):
        print("\n" + "=" * 80)
        print(f"[{i}/{len(unique_files)}] {path}")

        item = {
            "path": str(path),
            "load_ok": False,
            "top_type": None,
            "top_keys": None,
            "race_like_count": 0,
            "jsj006_like_count": 0,
            "score": 0,
        }

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            item["load_ok"] = True
            item["top_type"] = type(data).__name__

            if isinstance(data, dict):
                item["top_keys"] = list(data.keys())[:30]
            elif isinstance(data, list):
                item["top_keys"] = None

            def walk(obj):
                race_like = 0
                jsj006_like = 0

                if isinstance(obj, dict):
                    keys = set(obj.keys())

                    if "race_key" in keys:
                        race_like += 1

                    if "sensyuTypeInfo" in keys:
                        value = obj.get("sensyuTypeInfo")
                        if isinstance(value, list) and len(value) >= 5:
                            jsj006_like += 1

                    for value in obj.values():
                        a, b = walk(value)
                        race_like += a
                        jsj006_like += b

                elif isinstance(obj, list):
                    for value in obj:
                        a, b = walk(value)
                        race_like += a
                        jsj006_like += b

                return race_like, jsj006_like

            race_like, jsj006_like = walk(data)
            item["race_like_count"] = race_like
            item["jsj006_like_count"] = jsj006_like

            score = 0
            if jsj006_like > 0:
                score += 1000 + jsj006_like
            if race_like > 0:
                score += 100 + race_like
            item["score"] = score

            print("読込: OK")
            print("TOP TYPE:", item["top_type"])
            print("TOP KEYS:", item["top_keys"])
            print("race_key候補数:", race_like)
            print("JSJ006選手構造候補数:", jsj006_like)
            print("候補スコア:", score)

        except Exception as e:
            item["error"] = repr(e)
            print("読込: NG")
            print("ERROR:", repr(e))

        results.append(item)

    ranked = sorted(
        [x for x in results if x["load_ok"]],
        key=lambda x: x["score"],
        reverse=True,
    )

    print("\n" + "=" * 80)
    print("=== 220 結果 ===")
    print(f"181系JSON候補数: {len(unique_files)}")

    if ranked:
        print("\n=== 有力候補ランキング ===")
        for i, item in enumerate(ranked[:20], 1):
            print(
                f"[{i}] score={item['score']} / "
                f"JSJ006候補={item['jsj006_like_count']} / "
                f"race_key候補={item['race_like_count']}"
            )
            print(f"    {item['path']}")

        best = ranked[0]
        print("\n🔥 最有力181 RAW候補")
        print(best["path"])
    else:
        print("読込可能な181系JSONが見つかりませんでした。")

    out_path = base / "220_181_json_auto_search_result.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "candidate_count": len(unique_files),
                "results": results,
                "ranked": ranked,
                "best_candidate": ranked[0] if ranked else None,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\n保存完了: {out_path}")
    print("=== 220 完了 ===")

if __name__ == "__main__":
    main()
