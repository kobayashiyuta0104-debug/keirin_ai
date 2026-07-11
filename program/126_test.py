import json
import csv


def main():

    print(
        "=== 126 AI学習用 "
        "1レース1行CSV作成テスト ==="
    )

    # --------------------------------------------------
    # 読み込み
    # --------------------------------------------------

    load_file = (
        "125_extracted_results.json"
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

    rows = []

    total_races = 0
    complete_races = 0
    incomplete_races = 0

    # --------------------------------------------------
    # 全競輪場 × 全レース
    # --------------------------------------------------

    for venue_name, races in (
        all_results.items()
    ):

        for race_no, data in (
            races.items()
        ):

            total_races += 1

            finish_order = data.get(
                "finish_order",
                []
            )

            trifecta = data.get(
                "trifecta",
                []
            )

            # ------------------------------------------
            # 1着・2着・3着
            # tyakuを見て正確に取得
            # ------------------------------------------

            first_car = ""
            second_car = ""
            third_car = ""

            first_name = ""
            second_name = ""
            third_name = ""

            for item in finish_order:

                rank = str(
                    item.get(
                        "rank",
                        ""
                    )
                ).strip()

                car_no = str(
                    item.get(
                        "car_no",
                        ""
                    )
                ).strip()

                rider_name = str(
                    item.get(
                        "rider_name",
                        ""
                    )
                ).strip()

                if rank == "1":

                    first_car = car_no
                    first_name = rider_name

                elif rank == "2":

                    second_car = car_no
                    second_name = rider_name

                elif rank == "3":

                    third_car = car_no
                    third_name = rider_name

            # ------------------------------------------
            # 3連単
            # ------------------------------------------

            trifecta_combination = ""
            trifecta_payout = ""
            trifecta_popularity = ""

            if len(trifecta) > 0:

                trifecta_item = trifecta[0]

                trifecta_combination = str(
                    trifecta_item.get(
                        "combination",
                        ""
                    )
                ).strip()

                trifecta_payout = str(
                    trifecta_item.get(
                        "payout",
                        ""
                    )
                ).strip()

                trifecta_popularity = str(
                    trifecta_item.get(
                        "popularity",
                        ""
                    )
                ).strip()

            # ------------------------------------------
            # 払戻金を数字化
            # ------------------------------------------

            payout_number = ""

            if trifecta_payout:

                try:

                    payout_number = int(
                        trifecta_payout
                        .replace(",", "")
                    )

                except:

                    payout_number = ""

            # ------------------------------------------
            # 人気を数字化
            # ------------------------------------------

            popularity_number = ""

            if trifecta_popularity:

                try:

                    popularity_number = int(
                        trifecta_popularity
                        .replace("(", "")
                        .replace(")", "")
                    )

                except:

                    popularity_number = ""

            # ------------------------------------------
            # 完全レース判定
            # ------------------------------------------

            is_complete = (
                first_car != ""
                and second_car != ""
                and third_car != ""
                and trifecta_combination != ""
                and payout_number != ""
            )

            if is_complete:

                complete_races += 1

            else:

                incomplete_races += 1

            # ------------------------------------------
            # 1レース1行
            # ------------------------------------------

            row = {
                "venue": venue_name,
                "race_no": race_no,
                "first_car": first_car,
                "second_car": second_car,
                "third_car": third_car,
                "first_rider": first_name,
                "second_rider": second_name,
                "third_rider": third_name,
                "trifecta": (
                    trifecta_combination
                ),
                "trifecta_payout": (
                    payout_number
                ),
                "trifecta_popularity": (
                    popularity_number
                ),
                "is_complete": is_complete
            }

            rows.append(row)

            print()
            print("-" * 60)

            print(
                f"🔥 {venue_name} "
                f"{race_no}R"
            )

            print(
                "着順:",
                first_car,
                "-",
                second_car,
                "-",
                third_car
            )

            print(
                "3連単:",
                trifecta_combination
            )

            print(
                "払戻:",
                payout_number
            )

            print(
                "人気:",
                popularity_number
            )

            print(
                "完全:",
                is_complete
            )

    # --------------------------------------------------
    # CSV保存
    # --------------------------------------------------

    save_file = (
        "126_ai_race_results.csv"
    )

    fieldnames = [
        "venue",
        "race_no",
        "first_car",
        "second_car",
        "third_car",
        "first_rider",
        "second_rider",
        "third_rider",
        "trifecta",
        "trifecta_payout",
        "trifecta_popularity",
        "is_complete"
    ]

    with open(
        save_file,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(rows)

    # --------------------------------------------------
    # 最終結果
    # --------------------------------------------------

    print()
    print("=" * 70)
    print("🔥 126テスト終了")
    print("=" * 70)

    print(
        "総レース数:",
        total_races
    )

    print(
        "完全レース:",
        complete_races
    )

    print(
        "不完全レース:",
        incomplete_races
    )

    print(
        "CSV行数:",
        len(rows)
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