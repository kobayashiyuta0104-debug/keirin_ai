import json
from pathlib import Path
from collections import Counter


INPUT_PATH = Path(
    r"C:\競輪AI\163_dated_ai_pre_race_features.json"
)

OUTPUT_PATH = Path(
    r"C:\競輪AI\218_163_json_structure_analysis.json"
)


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def short_value(value, max_len=200):
    text = repr(value)

    if len(text) > max_len:
        return text[:max_len] + "..."

    return text


def main():

    print(
        "=== 218 163_dated_ai_pre_race_features JSON構造完全解析 ==="
    )

    data = load_json(INPUT_PATH)

    print("\n=== ROOT ===")
    print("TYPE:", type(data).__name__)

    if isinstance(data, dict):
        print("TOP KEYS:", list(data.keys()))

    elif isinstance(data, list):
        print("ROOT LIST件数:", len(data))

    key_counter = Counter()
    recent_hits = []
    race_key_hits = []
    dict_samples = []
    list_samples = []

    def walk(obj, path="$", depth=0):

        if isinstance(obj, dict):

            if len(dict_samples) < 100:
                dict_samples.append({
                    "path": path,
                    "depth": depth,
                    "keys": list(obj.keys()),
                })

            for key, value in obj.items():

                key_text = str(key)

                key_counter[key_text] += 1

                if "recent" in key_text.lower():
                    recent_hits.append({
                        "path": f"{path}.{key}",
                        "key": key_text,
                        "value": short_value(value),
                        "parent_keys": list(obj.keys()),
                    })

                if "race_key" in key_text.lower():
                    race_key_hits.append({
                        "path": f"{path}.{key}",
                        "key": key_text,
                        "value": short_value(value),
                        "parent_keys": list(obj.keys()),
                    })

                walk(
                    value,
                    f"{path}.{key}",
                    depth + 1
                )

        elif isinstance(obj, list):

            if len(list_samples) < 100:
                list_samples.append({
                    "path": path,
                    "depth": depth,
                    "count": len(obj),
                    "first_type": (
                        type(obj[0]).__name__
                        if obj
                        else None
                    ),
                })

            for i, value in enumerate(obj):
                walk(
                    value,
                    f"{path}[{i}]",
                    depth + 1
                )

    walk(data)

    print("\n=== 全キー種類数 ===")
    print(len(key_counter))

    print("\n=== キー出現回数 上位100 ===")

    for key, count in key_counter.most_common(100):
        print(f"  {key}: {count}")

    print("\n" + "=" * 80)
    print("=== recent系キー発見数 ===")
    print(len(recent_hits))

    for i, item in enumerate(
        recent_hits[:100],
        start=1
    ):
        print("\n" + "-" * 70)
        print(f"[{i}] PATH: {item['path']}")
        print("KEY:", item["key"])
        print("VALUE:", item["value"])
        print(
            "PARENT KEYS:",
            item["parent_keys"]
        )

    print("\n" + "=" * 80)
    print("=== race_key系キー発見数 ===")
    print(len(race_key_hits))

    for i, item in enumerate(
        race_key_hits[:50],
        start=1
    ):
        print("\n" + "-" * 70)
        print(f"[{i}] PATH: {item['path']}")
        print("KEY:", item["key"])
        print("VALUE:", item["value"])
        print(
            "PARENT KEYS:",
            item["parent_keys"]
        )

    print("\n" + "=" * 80)
    print("=== DICT構造サンプル 先頭100 ===")

    for i, item in enumerate(
        dict_samples,
        start=1
    ):
        print(
            f"[{i}] "
            f"DEPTH={item['depth']} / "
            f"PATH={item['path']}"
        )
        print(
            "    KEYS:",
            item["keys"]
        )

    print("\n" + "=" * 80)
    print("=== LIST構造サンプル 先頭100 ===")

    for i, item in enumerate(
        list_samples,
        start=1
    ):
        print(
            f"[{i}] "
            f"DEPTH={item['depth']} / "
            f"PATH={item['path']} / "
            f"件数={item['count']} / "
            f"FIRST_TYPE={item['first_type']}"
        )

    output = {
        "root_type": type(data).__name__,
        "top_keys": (
            list(data.keys())
            if isinstance(data, dict)
            else None
        ),
        "root_list_count": (
            len(data)
            if isinstance(data, list)
            else None
        ),
        "unique_key_count": len(key_counter),
        "key_counter": dict(key_counter),
        "recent_hits": recent_hits,
        "race_key_hits": race_key_hits,
        "dict_samples": dict_samples,
        "list_samples": list_samples,
    }

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"\n保存完了: {OUTPUT_PATH}"
    )

    print("=== 218 完了 ===")


if __name__ == "__main__":
    main()