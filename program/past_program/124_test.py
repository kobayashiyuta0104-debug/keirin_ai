import json
from pprint import pprint


def main():

    print("=== 124 着順データ × 払戻データ 中身確認テスト ===")

    # --------------------------------------------------
    # 122で保存したJSONを読む
    # --------------------------------------------------

    load_file = "122_all_venues_jsj012.json"

    try:

        with open(
            load_file,
            "r",
            encoding="utf-8"
        ) as f:

            all_results = json.load(f)

    except Exception as e:

        print()
        print("❌ JSON読込失敗")
        print(e)

        input(
            "確認できたらEnter："
        )

        return

    # --------------------------------------------------
    # 最初の1レースを取得
    # --------------------------------------------------

    target_venue = None
    target_race = None
    target_data = None

    for venue_name, races in all_results.items():

        if not races:
            continue

        for race_no, data in races.items():

            target_venue = venue_name
            target_race = race_no
            target_data = data

            break

        if target_data is not None:
            break

    if target_data is None:

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
        target_venue
    )

    print(
        "レース:",
        f"{target_race}R"
    )

    # --------------------------------------------------
    # tyakujyunItemSubData
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("🔥 tyakujyunItemSubData")
    print("=" * 80)

    if "tyakujyunItemSubData" in target_data:

        tyakujyun_data = target_data[
            "tyakujyunItemSubData"
        ]

        print(
            "TYPE:",
            type(tyakujyun_data).__name__
        )

        if isinstance(
            tyakujyun_data,
            list
        ):

            print(
                "件数:",
                len(tyakujyun_data)
            )

            for i, item in enumerate(
                tyakujyun_data
            ):

                print()
                print("-" * 70)

                print(
                    f"🔥 着順DATA #{i + 1}"
                )

                print("-" * 70)

                pprint(
                    item,
                    sort_dicts=False
                )

        else:

            pprint(
                tyakujyun_data,
                sort_dicts=False
            )

    else:

        print(
            "❌ tyakujyunItemSubDataなし"
        )

    # --------------------------------------------------
    # haraiGakuSubData
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("🔥 haraiGakuSubData")
    print("=" * 80)

    if "haraiGakuSubData" in target_data:

        harai_data = target_data[
            "haraiGakuSubData"
        ]

        print(
            "TYPE:",
            type(harai_data).__name__
        )

        if isinstance(
            harai_data,
            list
        ):

            print(
                "件数:",
                len(harai_data)
            )

            for i, item in enumerate(
                harai_data
            ):

                print()
                print("-" * 70)

                print(
                    f"🔥 払戻DATA #{i + 1}"
                )

                print("-" * 70)

                pprint(
                    item,
                    sort_dicts=False
                )

        else:

            pprint(
                harai_data,
                sort_dicts=False
            )

    else:

        print(
            "❌ haraiGakuSubDataなし"
        )

    # --------------------------------------------------
    # 124結果
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("🔥 124テスト終了")
    print("=" * 80)

    print(
        "解析競輪場:",
        target_venue
    )

    print(
        "解析レース:",
        f"{target_race}R"
    )

    print()
    print(
        "🔥 上の tyakujyunItemSubData と"
    )

    print(
        "🔥 haraiGakuSubData を確認してください"
    )

    print("=" * 80)

    input(
        "確認できたらEnter："
    )


if __name__ == "__main__":
    main()