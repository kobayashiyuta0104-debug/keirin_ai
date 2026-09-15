from pathlib import Path
import csv
import json


# ============================================================
# 007
# decoded_odds.json の list_9（3連単）をCSVへ変換する
# ============================================================

RACE_ID = "202609081312"

BASE_DIR = Path(r"C:\競輪AI\data_official\odds_test")

INPUT_FILE = BASE_DIR / f"{RACE_ID}_decoded_odds.json"
OUTPUT_FILE = BASE_DIR / f"{RACE_ID}_trifecta_odds.csv"


def main():
    print("========================================")
    print("007 3連単オッズ CSV出力")
    print("========================================")
    print("RACE_ID =", RACE_ID)
    print("INPUT   =", INPUT_FILE)
    print("OUTPUT  =", OUTPUT_FILE)
    print()

    # 1. decoded_odds.json を読み込む
    if not INPUT_FILE.exists():
        print("ERROR: 入力ファイルがありません。")
        print(INPUT_FILE)
        return

    with INPUT_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. list_9 を取得
    official_dt = data.get("official_dt", "")
    list_9 = data.get("list_9")

    if list_9 is None:
        print("ERROR: list_9 がありません。")
        return

    print("official_dt =", official_dt)
    print("list_9 件数 =", len(list_9))
    print()

    # 7車立ての3連単は 7P3 = 210通り
    expected_count = 210

    if len(list_9) != expected_count:
        print("ERROR: 3連単の件数が210件ではありません。")
        print("実際の件数 =", len(list_9))
        return

    # 3. CSVデータ作成
    rows = []

    for api_order, item in enumerate(list_9, start=1):

        if not isinstance(item, list) or len(item) != 4:
            print("ERROR: 想定外のデータ形式です。")
            print("api_order =", api_order)
            print("item =", item)
            return

        combination = str(item[0])
        odds_text = str(item[1])
        api_field_2 = str(item[2])
        api_field_3 = str(item[3])

        # 010203 → 1-2-3
        if len(combination) != 6 or not combination.isdigit():
            print("ERROR: 組み合わせの形式が不正です。")
            print("api_order =", api_order)
            print("combination =", combination)
            return

        first = int(combination[0:2])
        second = int(combination[2:4])
        third = int(combination[4:6])

        # 3連単なので車番の重複がないことを確認
        if len({first, second, third}) != 3:
            print("ERROR: 車番が重複しています。")
            print("api_order =", api_order)
            print("combination =", combination)
            return

        # 今回は7車立て
        if not all(1 <= n <= 7 for n in (first, second, third)):
            print("ERROR: 車番が1～7の範囲外です。")
            print("api_order =", api_order)
            print("combination =", combination)
            return

        # オッズを数値化
        try:
            odds = float(odds_text)
        except ValueError:
            print("ERROR: オッズを数値化できません。")
            print("api_order =", api_order)
            print("odds =", odds_text)
            return

        rows.append([
            RACE_ID,
            api_order,
            combination,
            first,
            second,
            third,
            odds,
            api_field_2,
            api_field_3,
            official_dt,
        ])

    # 4. CSVへ出力
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    header = [
        "race_id",
        "api_order",
        "combination",
        "first",
        "second",
        "third",
        "odds",
        "api_field_2",
        "api_field_3",
        "official_dt",
    ]

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    # 5. 最終確認
    print("CSV出力完了")
    print()
    print("出力件数 =", len(rows))
    print("出力先   =", OUTPUT_FILE)
    print()

    print("----- 先頭5件 -----")
    for row in rows[:5]:
        print(row)

    print()
    print("----- 最終5件 -----")
    for row in rows[-5:]:
        print(row)

    print()
    print("========================================")
    print("007 完了")
    print("========================================")


if __name__ == "__main__":
    main()