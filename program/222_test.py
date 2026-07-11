import json
from pathlib import Path
from collections import Counter

RAW_PATH = Path(r"C:\競輪AI\181_verified_jsj006_capture.json")
OUTPUT_PATH = Path(r"C:\競輪AI\222_tyo4_result_keys_analysis.json")

def walk(obj, path="$"):
    hits = []
    if isinstance(obj, dict):
        tyo4 = obj.get("tyo4InfoSubData")
        if isinstance(tyo4, dict):
            results = tyo4.get("resultInfoSubData")
            if isinstance(results, list):
                hits.append((path + ".tyo4InfoSubData.resultInfoSubData", results))
        for k, v in obj.items():
            hits.extend(walk(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(walk(v, f"{path}[{i}]"))
    return hits

def main():
    print("=== 222 JSJ006 tyo4InfoSubData 過去成績キー完全解析 ===")
    with RAW_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    hits = walk(data)
    print("resultInfoSubData発見数:", len(hits))

    key_counter = Counter()
    value_samples = {}
    row_count = 0
    samples = []

    for path, rows in hits:
        for row in rows:
            if not isinstance(row, dict):
                continue
            row_count += 1
            for k, v in row.items():
                key_counter[k] += 1
                value_samples.setdefault(k, [])
                if v not in value_samples[k] and len(value_samples[k]) < 30:
                    value_samples[k].append(v)
            if len(samples) < 30:
                samples.append({"path": path, "row": row})

    print("過去成績行総数:", row_count)
    print("\n=== 全キー・出現回数・値サンプル ===")
    for k, cnt in key_counter.most_common():
        print("\nKEY:", k)
        print("  出現回数:", cnt)
        print("  値サンプル:", value_samples.get(k))

    print("\n=== 生行サンプル 先頭30 ===")
    for i, item in enumerate(samples, 1):
        print("\n" + "-" * 70)
        print(f"[{i}] PATH:", item["path"])
        print("ROW:", item["row"])

    output = {
        "result_list_count": len(hits),
        "row_count": row_count,
        "key_counts": dict(key_counter),
        "value_samples": value_samples,
        "samples": samples,
    }
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n保存完了: {OUTPUT_PATH}")
    print("=== 222 完了 ===")

if __name__ == "__main__":
    main()
