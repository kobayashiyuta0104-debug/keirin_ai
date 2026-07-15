import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "142_joined_race_data.json"
OUTPUT_FILE = BASE_DIR / "144_result_detail_inventory.json"


def short_value(value, limit=300):

    if value is None:
        return "None"

    text = str(value)

    if len(text) > limit:
        return text[:limit] + "..."

    return text


def walk(obj, path="ROOT", rows=None):

    if rows is None:
        rows = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            new_path = f"{path}.{key}"

            rows.append(
                {
                    "path": new_path,
                    "key": str(key),
                    "type": type(value).__name__,
                    "value": (
                        value
                        if isinstance(
                            value,
                            (str, int, float, bool),
                        )
                        or value is None
                        else None
                    ),
                }
            )

            walk(
                value,
                new_path,
                rows,
            )

    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            new_path = f"{path}[{index}]"

            rows.append(
                {
                    "path": new_path,
                    "key": f"[{index}]",
                    "type": type(value).__name__,
                    "value": (
                        value
                        if isinstance(
                            value,
                            (str, int, float, bool),
                        )
                        or value is None
                        else None
                    ),
                }
            )

            walk(
                value,
                new_path,
                rows,
            )

    return rows


def print_dict_detail(title, data):

    print()
    print("=" * 70)
    print(f"🔥 {title}")
    print("=" * 70)

    print()
    print(f"TYPE: {type(data).__name__}")

    if not isinstance(data, dict):

        print("❌ dictではない")
        print(short_value(data))
        return

    print(f"KEY数: {len(data)}")

    for key, value in data.items():

        print()
        print("-" * 70)

        print(f"KEY  : {repr(key)}")
        print(f"TYPE : {type(value).__name__}")

        if isinstance(
            value,
            (str, int, float, bool),
        ) or value is None:

            print(
                f"VALUE: {short_value(value)}"
            )

        elif isinstance(value, list):

            print(
                f"件数 : {len(value)}"
            )

        elif isinstance(value, dict):

            print(
                f"KEY数: {len(value)}"
            )

            print(
                "SUB KEYS:",
                list(value.keys()),
            )


def main():

    print("=" * 70)
    print("🔥 144 確定結果 完全分解テスト")
    print("=" * 70)

    if not INPUT_FILE.exists():

        print()
        print("❌ 入力JSONなし")
        print(INPUT_FILE)
        return

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    print()
    print(f"入力JSON: {INPUT_FILE.name}")
    print(f"ROOT TYPE: {type(data).__name__}")

    if not isinstance(data, list):

        print("❌ ROOTがlistではない")
        return

    if len(data) == 0:

        print("❌ データ0件")
        return

    race = data[0]

    print()
    print(f"レース件数: {len(data)}")

    print()
    print("🔥 対象レース")

    print(
        race.get("race_key")
        or race.get("RACE_KEY")
        or "RACE KEY不明"
    )

    confirmed = race.get(
        "confirmed_result",
        {},
    )

    print_dict_detail(
        "confirmed_result ROOT",
        confirmed,
    )

    result = confirmed.get(
        "result",
        {},
    )

    print_dict_detail(
        "confirmed_result.result",
        result,
    )

    tyakujyun = result.get(
        "tyakujyunItemSubData",
        [],
    )

    print()
    print("=" * 70)
    print("🔥 着順配列 完全表示")
    print("=" * 70)

    print()
    print(
        f"tyakujyunItemSubData件数: "
        f"{len(tyakujyun)}"
    )

    tyakujyun_inventory = []

    for index, item in enumerate(
        tyakujyun,
        start=1,
    ):

        print()
        print("=" * 70)
        print(f"🔥 選手 #{index}")
        print("=" * 70)

        print(
            f"TYPE: {type(item).__name__}"
        )

        if not isinstance(item, dict):

            print(short_value(item))
            continue

        print(
            f"KEY数: {len(item)}"
        )

        player_data = {
            "index": index,
            "keys": {},
        }

        for key, value in item.items():

            print()
            print(
                f"{repr(key)}"
                f" = "
                f"{short_value(value)}"
            )

            player_data["keys"][key] = value

        tyakujyun_inventory.append(
            player_data
        )

    print()
    print("=" * 70)
    print("🔥 RESULT内 VALUE PATH 全表示")
    print("=" * 70)

    result_rows = walk(
        result,
        "confirmed_result.result",
    )

    value_rows = [
        row
        for row in result_rows
        if row["value"] is not None
    ]

    print()
    print(
        f"VALUE入り件数: {len(value_rows)}"
    )

    for index, row in enumerate(
        value_rows,
        start=1,
    ):

        print()
        print(
            f"{index:03d} | "
            f"{row['path']} "
            f"= "
            f"{short_value(row['value'])}"
        )

    search_words = [
        "tyaku",
        "jyun",
        "rank",
        "order",
        "refund",
        "pay",
        "haito",
        "sanren",
        "rentan",
        "3ren",
        "3連",
        "払戻",
        "着",
    ]

    print()
    print("=" * 70)
    print("🔥 着順・払戻・3連単 KEY候補")
    print("=" * 70)

    candidates = []

    for row in result_rows:

        text = (
            row["path"]
            + " "
            + row["key"]
        ).lower()

        if any(
            word.lower() in text
            for word in search_words
        ):

            candidates.append(row)

    print()
    print(
        f"候補数: {len(candidates)}"
    )

    for index, row in enumerate(
        candidates,
        start=1,
    ):

        print()
        print(
            f"{index:03d} | "
            f"PATH: {row['path']}"
        )

        print(
            f"KEY  : {repr(row['key'])}"
        )

        print(
            f"TYPE : {row['type']}"
        )

        print(
            f"VALUE: {short_value(row['value'])}"
        )

    output = {
        "input_file": INPUT_FILE.name,
        "tyakujyun_count": len(tyakujyun),
        "tyakujyun_inventory": tyakujyun_inventory,
        "result_value_rows": value_rows,
        "candidate_rows": candidates,
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 70)
    print("🔥 144テスト終了")
    print("=" * 70)

    print(
        f"着順配列件数: {len(tyakujyun)}"
    )

    print(
        f"RESULT VALUE件数: "
        f"{len(value_rows)}"
    )

    print(
        f"候補数: {len(candidates)}"
    )

    print()
    print(
        f"保存先: {OUTPUT_FILE.name}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()