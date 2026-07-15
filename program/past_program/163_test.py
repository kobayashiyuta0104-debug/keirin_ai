import json
import os


INPUT_FILE = "162_ai_pre_race_features.json"
OUTPUT_FILE = "163_dated_ai_pre_race_features.json"

# 155のJSJ006を取得した対象開催日
RACE_DATE = "20260707"


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def main():

    print("=" * 70)
    print("🔥 163 AI予想データ 開催日付与・race_key再構築")
    print("=" * 70)

    if not os.path.exists(INPUT_FILE):

        print(
            f"❌ JSONなし: {INPUT_FILE}"
        )
        return

    data = load_json(INPUT_FILE)

    races = data.get(
        "races",
        []
    )

    if not isinstance(races, list):

        print("❌ racesがlistではない")
        return

    print()
    print("🔥 読込成功")
    print(
        "入力レース数:",
        len(races),
    )
    print(
        "付与開催日:",
        RACE_DATE,
    )

    dated_races = []

    duplicate_check = {}

    for race in races:

        if not isinstance(race, dict):
            continue

        venue = str(
            race.get(
                "venue",
                ""
            )
        ).strip()

        race_no = race.get(
            "race_no"
        )

        if not venue:
            print(
                "⚠ 開催場なしレースを除外"
            )
            continue

        if race_no is None:
            print(
                f"⚠ R番号なし: {venue}"
            )
            continue

        race_key = (
            f"{RACE_DATE}_"
            f"{venue}_"
            f"{race_no}R"
        )

        new_race = dict(race)

        new_race[
            "race_date"
        ] = RACE_DATE

        new_race[
            "race_key"
        ] = race_key

        dated_races.append(
            new_race
        )

        duplicate_check.setdefault(
            race_key,
            0
        )

        duplicate_check[
            race_key
        ] += 1

    duplicate_keys = [
        race_key
        for race_key, count
        in duplicate_check.items()
        if count > 1
    ]

    dated_races.sort(
        key=lambda x: (
            x.get(
                "race_date",
                ""
            ),
            x.get(
                "venue",
                ""
            ),
            x.get(
                "race_no",
                999
            ),
        )
    )

    print()
    print("=" * 70)
    print("🔥 race_key SAMPLE")
    print("=" * 70)

    for race in dated_races[:20]:

        print(
            race["race_key"],
            "選手数:",
            race.get(
                "player_count",
                0
            ),
        )

    print()
    print("=" * 70)
    print("🔥 重複CHECK")
    print("=" * 70)

    print(
        "race_key数:",
        len(duplicate_check),
    )

    print(
        "重複race_key数:",
        len(duplicate_keys),
    )

    if duplicate_keys:

        print()
        print("⚠ 重複KEY一覧")

        for race_key in duplicate_keys:

            print(
                race_key,
                "件数:",
                duplicate_check[
                    race_key
                ],
            )

    else:

        print(
            "🔥 race_key重複なし！"
        )

    output = {
        "source_file":
            INPUT_FILE,

        "race_date":
            RACE_DATE,

        "race_count":
            len(dated_races),

        "player_count":
            sum(
                race.get(
                    "player_count",
                    0
                )
                for race in dated_races
            ),

        "race_key_format":
            "YYYYMMDD_開催場_R",

        "races":
            dated_races,
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
    print("🔥 163テスト終了")
    print("=" * 70)

    print(
        "開催日:",
        RACE_DATE,
    )

    print(
        "レース件数:",
        len(dated_races),
    )

    print(
        "選手件数:",
        output[
            "player_count"
        ],
    )

    print(
        "race_key数:",
        len(duplicate_check),
    )

    print(
        "重複race_key数:",
        len(duplicate_keys),
    )

    print()
    print(
        f"保存先: {OUTPUT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()