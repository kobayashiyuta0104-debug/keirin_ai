import json


def main():

    print(
        "=== 125 全レース "
        "着順 × 3連単払戻 自動抽出テスト ==="
    )

    # --------------------------------------------------
    # 読み込み
    # --------------------------------------------------

    load_file = (
        "122_all_venues_jsj012.json"
    )

    with open(
        load_file,
        "r",
        encoding="utf-8"
    ) as f:

        all_results = json.load(f)

    print()
    print(
        "🔥 読み込み成功:",
        load_file
    )

    extracted_results = {}

    total_races = 0
    success_races = 0
    error_races = 0

    # --------------------------------------------------
    # 全競輪場 × 全レース
    # --------------------------------------------------

    for venue_name, races in (
        all_results.items()
    ):

        extracted_results[
            venue_name
        ] = {}

        print()
        print("=" * 70)
        print(
            "🔥 競輪場:",
            venue_name
        )
        print("=" * 70)

        for race_no, data in (
            races.items()
        ):

            total_races += 1

            print()
            print("-" * 60)
            print(
                f"🔥 {venue_name} "
                f"{race_no}R 解析"
            )
            print("-" * 60)

            try:

                # --------------------------------------
                # 着順DATA
                # --------------------------------------

                finish_data = (
                    data.get(
                        "tyakujyunItemSubData",
                        []
                    )
                )

                finish_order = []

                for item in finish_data:

                    tyaku = (
                        item.get("tyaku", "")
                    )

                    syaban = (
                        item.get("syaban", "")
                    )

                    sensyu_name = (
                        item.get(
                            "sensyuName",
                            ""
                        )
                    )

                    tyakusa = (
                        item.get(
                            "tyakusa",
                            ""
                        )
                    )

                    agari = (
                        item.get(
                            "agari",
                            ""
                        )
                    )

                    kimarite = (
                        item.get(
                            "kimarite",
                            ""
                        )
                    )

                    finish_order.append(
                        {
                            "rank": tyaku,
                            "car_no": syaban,
                            "rider_name": (
                                sensyu_name
                            ),
                            "margin": tyakusa,
                            "agari": agari,
                            "kimarite": kimarite
                        }
                    )

                # --------------------------------------
                # 3連単払戻
                # --------------------------------------

                payout_root = (
                    data.get(
                        "haraiGakuSubData",
                        {}
                    )
                )

                trifecta_data = (
                    payout_root.get(
                        "RT3HaraiGakuDispItemSubData",
                        []
                    )
                )

                trifecta_results = []

                for item in trifecta_data:

                    combination = (
                        item.get(
                            "kumiBan",
                            ""
                        )
                    )

                    payout = (
                        item.get(
                            "haraiGaku",
                            ""
                        )
                    )

                    popularity = (
                        item.get(
                            "ninki",
                            ""
                        )
                    )

                    trifecta_results.append(
                        {
                            "combination": (
                                combination
                            ),
                            "payout": payout,
                            "popularity": (
                                popularity
                            )
                        }
                    )

                # --------------------------------------
                # 保存
                # --------------------------------------

                extracted_results[
                    venue_name
                ][
                    race_no
                ] = {
                    "finish_order": (
                        finish_order
                    ),
                    "trifecta": (
                        trifecta_results
                    )
                }

                print(
                    "🔥 着順件数:",
                    len(finish_order)
                )

                if len(finish_order) >= 3:

                    print(
                        "🥇",
                        finish_order[0][
                            "car_no"
                        ]
                    )

                    print(
                        "🥈",
                        finish_order[1][
                            "car_no"
                        ]
                    )

                    print(
                        "🥉",
                        finish_order[2][
                            "car_no"
                        ]
                    )

                print(
                    "🔥 3連単件数:",
                    len(trifecta_results)
                )

                for trifecta in (
                    trifecta_results
                ):

                    print(
                        "🎯",
                        trifecta[
                            "combination"
                        ],
                        trifecta[
                            "payout"
                        ],
                        "円",
                        trifecta[
                            "popularity"
                        ]
                    )

                success_races += 1

            except Exception as e:

                error_races += 1

                print(
                    "❌ 解析失敗:",
                    e
                )

    # --------------------------------------------------
    # JSON保存
    # --------------------------------------------------

    save_file = (
        "125_extracted_results.json"
    )

    with open(
        save_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            extracted_results,
            f,
            ensure_ascii=False,
            indent=2
        )

    # --------------------------------------------------
    # 最終結果
    # --------------------------------------------------

    print()
    print("=" * 70)
    print("🔥 125テスト終了")
    print("=" * 70)

    print(
        "総レース数:",
        total_races
    )

    print(
        "解析成功:",
        success_races
    )

    print(
        "解析失敗:",
        error_races
    )

    print()
    print(
        "保存先:",
        save_file
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()