import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "149_player_stats_hunt.json"


SEARCH_WORDS = [
    "競走得点",
    "得点",
    "脚質",
    "勝率",
    "2連対",
    "二連対",
    "3連対",
    "三連対",
    "バック",
    "B回数",
    "S回数",
    "H回数",
    "逃げ",
    "捲り",
    "まくり",
    "差し",
    "マーク",
    "ギア",
    "期別",
    "卒業期",
    "直近成績",
]

KEY_HINTS = [
    "score",
    "point",
    "tokuten",
    "racepoint",
    "kyoso",
    "kyousou",
    "style",
    "kyakushitsu",
    "win",
    "rate",
    "rentai",
    "back",
    "gear",
    "sotugyou",
    "sotsugyo",
    "kimarite",
    "nige",
    "makuri",
    "sashi",
    "mark",
    "recent",
    "result",
]


def flatten(obj, path="ROOT", results=None):

    if results is None:
        results = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            new_path = f"{path}.{key}"

            if isinstance(value, (dict, list)):

                flatten(
                    value,
                    new_path,
                    results,
                )

            else:

                results.append({
                    "path": new_path,
                    "key": str(key),
                    "value": value,
                    "type": type(value).__name__,
                })

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            new_path = f"{path}[{index}]"

            if isinstance(value, (dict, list)):

                flatten(
                    value,
                    new_path,
                    results,
                )

            else:

                results.append({
                    "path": new_path,
                    "key": "",
                    "value": value,
                    "type": type(value).__name__,
                })

    return results


def is_candidate(item):

    key = str(item["key"]).lower()
    value = str(item["value"]).lower()
    path = str(item["path"]).lower()

    text = f"{key} {value} {path}"

    for word in SEARCH_WORDS:

        if word.lower() in text:

            return True

    for hint in KEY_HINTS:

        if hint in key:

            return True

    return False


def main():

    print("=" * 70)
    print("🔥 149 予想用選手成績JSON 全ファイル探索")
    print("=" * 70)

    json_files = sorted(
        BASE_DIR.glob("*.json")
    )

    print()
    print(f"探索JSON数: {len(json_files)}")

    all_candidates = []

    for file_path in json_files:

        if file_path.name.startswith("149_"):

            continue

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8",
            ) as f:

                data = json.load(f)

        except Exception as e:

            print()
            print(
                f"⚠️ 読込失敗: "
                f"{file_path.name}"
            )

            print(e)

            continue

        items = flatten(data)

        candidates = [
            item
            for item in items
            if is_candidate(item)
        ]

        if len(candidates) == 0:

            continue

        print()
        print("=" * 70)
        print(
            f"🔥 FILE: {file_path.name}"
        )
        print(
            f"候補数: {len(candidates)}"
        )
        print("=" * 70)

        for item in candidates[:100]:

            print(
                f"{item['path']} "
                f"= {item['value']}"
            )

        all_candidates.append({
            "file": file_path.name,
            "candidate_count": len(candidates),
            "candidates": candidates,
        })

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            all_candidates,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 70)
    print("🔥 149テスト終了")
    print("=" * 70)

    print(
        f"候補ありJSON数: "
        f"{len(all_candidates)}"
    )

    print()
    print("🔥 候補JSON一覧")

    for result in all_candidates:

        print(
            f"{result['file']} "
            f"→ {result['candidate_count']}件"
        )

    print()
    print(
        f"保存先: "
        f"{OUTPUT_FILE.name}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()