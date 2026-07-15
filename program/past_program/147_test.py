import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "142_joined_race_data.json"
OUTPUT_FILE = BASE_DIR / "147_player_structure.json"


def print_structure(obj, path="PLAYER", depth=0, results=None):

    if results is None:
        results = []

    indent = "  " * depth

    if isinstance(obj, dict):

        for key, value in obj.items():

            new_path = f"{path}.{key}"

            if isinstance(value, dict):

                print(
                    f"{indent}🔥 KEY: {key} "
                    f"[dict / {len(value)} keys]"
                )

                results.append(
                    {
                        "path": new_path,
                        "key": key,
                        "type": "dict",
                        "value": None,
                    }
                )

                print_structure(
                    value,
                    new_path,
                    depth + 1,
                    results,
                )

            elif isinstance(value, list):

                print(
                    f"{indent}🔥 KEY: {key} "
                    f"[list / {len(value)} items]"
                )

                results.append(
                    {
                        "path": new_path,
                        "key": key,
                        "type": "list",
                        "value": None,
                    }
                )

                for index, item in enumerate(value):

                    item_path = (
                        f"{new_path}[{index}]"
                    )

                    print(
                        f"{indent}  "
                        f"📦 INDEX [{index}] "
                        f"TYPE: {type(item).__name__}"
                    )

                    if isinstance(
                        item,
                        (dict, list),
                    ):

                        print_structure(
                            item,
                            item_path,
                            depth + 2,
                            results,
                        )

                    else:

                        print(
                            f"{indent}    "
                            f"{item_path} = {item}"
                        )

                        results.append(
                            {
                                "path": item_path,
                                "key": key,
                                "type": type(
                                    item
                                ).__name__,
                                "value": item,
                            }
                        )

            else:

                print(
                    f"{indent}"
                    f"{new_path} = {value} "
                    f"[{type(value).__name__}]"
                )

                results.append(
                    {
                        "path": new_path,
                        "key": key,
                        "type": type(
                            value
                        ).__name__,
                        "value": value,
                    }
                )

    elif isinstance(obj, list):

        for index, item in enumerate(obj):

            item_path = f"{path}[{index}]"

            print(
                f"{indent}"
                f"📦 INDEX [{index}] "
                f"TYPE: {type(item).__name__}"
            )

            print_structure(
                item,
                item_path,
                depth + 1,
                results,
            )

    return results


def main():

    print("=" * 70)
    print("🔥 147 JSJ012 選手1人分 完全構造解析")
    print("=" * 70)

    if not INPUT_FILE.exists():

        print()
        print("❌ 入力JSONがありません")
        print(f"INPUT: {INPUT_FILE}")

        return

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    if not isinstance(data, list):

        print("❌ ROOTがlistではありません")
        return

    if len(data) == 0:

        print("❌ レースデータがありません")
        return

    joined = data[0]

    if not isinstance(joined, dict):

        print("❌ レースデータがdictではありません")
        return

    pre_race_data = joined.get(
        "pre_race_data"
    )

    if not isinstance(
        pre_race_data,
        dict,
    ):

        print("❌ pre_race_dataがありません")
        return

    jsj012 = pre_race_data.get(
        "jsj012"
    )

    if not isinstance(jsj012, dict):

        print("❌ jsj012がありません")
        return

    players = jsj012.get(
        "tyakujyunItemSubData"
    )

    if not isinstance(players, list):

        print(
            "❌ tyakujyunItemSubData "
            "がlistではありません"
        )

        return

    print()
    print(
        f"選手データ件数: "
        f"{len(players)}"
    )

    if len(players) == 0:

        print("❌ 選手データ0件")
        return

    player = players[0]

    print()
    print("=" * 70)
    print("🔥 PLAYER[0] 生JSON")
    print("=" * 70)

    print(
        json.dumps(
            player,
            ensure_ascii=False,
            indent=2,
        )
    )

    print()
    print("=" * 70)
    print("🔥 PLAYER[0] KEY・PATH完全展開")
    print("=" * 70)
    print()

    structure = print_structure(
        player,
        "PLAYER[0]",
    )

    output_data = {
        "source": INPUT_FILE.name,
        "player_count": len(players),
        "player_0_raw": player,
        "player_0_structure": structure,
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output_data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 70)
    print("🔥 147テスト終了")
    print("=" * 70)

    print(
        f"選手データ件数: "
        f"{len(players)}"
    )

    print(
        f"PLAYER[0] 展開ITEM数: "
        f"{len(structure)}"
    )

    print()
    print(
        f"保存先: "
        f"{OUTPUT_FILE.name}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()