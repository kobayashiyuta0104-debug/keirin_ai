import json


def main():

    print("=== 123 JSJ012構造解析テスト ===")

    file_name = "122_all_venues_jsj012.json"

    # --------------------------------------------------
    # JSON読込
    # --------------------------------------------------

    try:

        with open(
            file_name,
            "r",
            encoding="utf-8"
        ) as f:

            all_results = json.load(f)

    except Exception as e:

        print()
        print("❌ JSON読込失敗:")
        print(e)

        input(
            "確認できたらEnter："
        )

        return

    print()
    print("🔥 JSON読込成功")

    print(
        "競輪場数:",
        len(all_results)
    )

    # --------------------------------------------------
    # 最初の1レース取得
    # --------------------------------------------------

    sample_venue = None
    sample_race = None
    sample_data = None

    for venue_name, races in all_results.items():

        for race_no, data in races.items():

            sample_venue = venue_name
            sample_race = race_no
            sample_data = data

            break

        if sample_data is not None:
            break

    if sample_data is None:

        print()
        print("❌ レースデータがありません")

        input(
            "確認できたらEnter："
        )

        return

    print()
    print("=" * 80)
    print("🔥 解析対象")
    print("=" * 80)

    print(
        "競輪場:",
        sample_venue
    )

    print(
        "レース:",
        sample_race + "R"
    )

    print(
        "ROOT TYPE:",
        type(sample_data).__name__
    )

    # --------------------------------------------------
    # JSON構造再帰解析
    # --------------------------------------------------

    paths = []

    def analyze(
        value,
        path="ROOT",
        depth=0
    ):

        value_type = type(value).__name__

        paths.append(
            {
                "path": path,
                "type": value_type
            }
        )

        indent = "  " * depth

        if isinstance(value, dict):

            print(
                f"{indent}📁 {path}"
                f"  DICT"
                f"  KEYS={len(value)}"
            )

            for key, child in value.items():

                child_path = (
                    f"{path}.{key}"
                )

                analyze(
                    child,
                    child_path,
                    depth + 1
                )

        elif isinstance(value, list):

            print(
                f"{indent}📋 {path}"
                f"  LIST"
                f"  COUNT={len(value)}"
            )

            # リストは最初の3件だけ詳しく見る
            for index, child in enumerate(
                value[:3]
            ):

                child_path = (
                    f"{path}[{index}]"
                )

                analyze(
                    child,
                    child_path,
                    depth + 1
                )

        else:

            text = repr(value)

            if len(text) > 200:

                text = (
                    text[:200]
                    + "..."
                )

            print(
                f"{indent}🔥 {path}"
                f"  TYPE={value_type}"
                f"  VALUE={text}"
            )

    print()
    print("=" * 80)
    print("🔥 JSON構造")
    print("=" * 80)

    analyze(sample_data)

    # --------------------------------------------------
    # PATH保存
    # --------------------------------------------------

    save_file = (
        "123_jsj012_structure.json"
    )

    with open(
        save_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            paths,
            f,
            ensure_ascii=False,
            indent=2
        )

    # --------------------------------------------------
    # ROOT情報
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("🔥 ROOT解析")
    print("=" * 80)

    if isinstance(sample_data, dict):

        print(
            "ROOT KEY数:",
            len(sample_data)
        )

        print()
        print("🔥 ROOT KEYS")

        for key in sample_data.keys():

            print(
                "-",
                key
            )

    elif isinstance(sample_data, list):

        print(
            "ROOT LIST数:",
            len(sample_data)
        )

    # --------------------------------------------------
    # 終了
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("🔥 123テスト終了")
    print("=" * 80)

    print(
        "解析競輪場:",
        sample_venue
    )

    print(
        "解析レース:",
        sample_race + "R"
    )

    print(
        "PATH数:",
        len(paths)
    )

    print(
        "保存先:",
        save_file
    )

    print("=" * 80)

    input(
        "確認できたらEnter："
    )


if __name__ == "__main__":
    main()