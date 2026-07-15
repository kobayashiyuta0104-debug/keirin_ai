import json
import os


INPUT_FILE = "155_all_venues_jsj006.json"
OUTPUT_FILE = "162_ai_pre_race_features.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def to_int(value):
    try:
        return int(str(value).strip())
    except:
        return None


def to_float(value):
    try:
        return float(str(value).strip())
    except:
        return None


def normalize_text(value):
    if value is None:
        return ""

    return (
        str(value)
        .replace("\u3000", " ")
        .strip()
    )


def get_result_history(info):

    if not isinstance(info, dict):
        return []

    result_list = info.get(
        "resultInfoSubData",
        []
    )

    if not isinstance(result_list, list):
        return []

    history = []

    for item in result_list:

        if not isinstance(item, dict):
            continue

        finish = to_int(
            item.get("imgTyakuiName")
        )

        back = to_int(
            item.get("backTori")
        )

        history.append({
            "finish": finish,
            "back": back,
        })

    return history


def normalize_player(player):

    current_info = player.get(
        "konResultInfoSubData",
        {}
    )

    recent_info = player.get(
        "tyo4InfoSubData",
        {}
    )

    current_history = get_result_history(
        current_info
    )

    recent_history = get_result_history(
        recent_info
    )

    return {
        "car_no": to_int(
            player.get("syaban")
        ),

        "player_id": normalize_text(
            player.get("sensyuRegistNo")
        ),

        "player_name": normalize_text(
            player.get("sensyuName")
        ),

        "prefecture": normalize_text(
            player.get("huKen")
        ),

        "previous_class": normalize_text(
            player.get("prevKyuhan")
        ),

        "class": normalize_text(
            player.get("kyuhan")
        ),

        "riding_style": normalize_text(
            player.get("kyakusitu")
        ),

        "graduation_term": to_int(
            player.get("sotugyouki")
        ),

        "age": to_int(
            player.get("age")
        ),

        "race_score": to_float(
            player.get("heikinTokuten")
        ),

        "nige_count": to_int(
            player.get("nigeCnt")
        ),

        "makuri_count": to_int(
            player.get("makuriCnt")
        ),

        "sashi_count": to_int(
            player.get("sasiCnt")
        ),

        "mark_count": to_int(
            player.get("markCnt")
        ),

        "back_count": to_int(
            player.get("backCnt")
        ),

        "home_count": to_int(
            player.get("homeTori")
        ),

        "start_count": to_int(
            player.get("stTori")
        ),

        "win_rate": to_float(
            player.get("syouritu")
        ),

        "top2_rate": to_float(
            player.get("rentairitu2")
        ),

        "top3_rate": to_float(
            player.get("rentairitu3")
        ),

        "current_meeting_results":
            current_history,

        "recent_meeting_results":
            recent_history,

        "recent_meeting": {
            "venue_code": normalize_text(
                recent_info.get(
                    "bKeirinjyoCd"
                )
            ),

            "venue_name": normalize_text(
                recent_info.get(
                    "kerinjyoName"
                )
            ),

            "meeting_start_date":
                normalize_text(
                    recent_info.get(
                        "kaisaiFirst"
                    )
                ),

            "grade": normalize_text(
                recent_info.get(
                    "gaiTeiGrade"
                )
            ),
        },
    }


def main():

    print("=" * 70)
    print("🔥 162 JSJ006 AI予想特徴量 正規化")
    print("=" * 70)

    if not os.path.exists(INPUT_FILE):

        print(
            f"❌ JSONなし: {INPUT_FILE}"
        )
        return

    data = load_json(INPUT_FILE)

    normalized_races = []

    total_players = 0

    if not isinstance(data, dict):

        print("❌ ROOTがdictではない")
        return

    for venue_name, venue_data in data.items():

        if not isinstance(venue_data, dict):
            continue

        for race_no, race_data in venue_data.items():

            if not isinstance(race_data, dict):
                continue

            players = race_data.get(
                "sensyuTypeInfo",
                []
            )

            if not isinstance(players, list):
                continue

            normalized_players = []

            for player in players:

                if not isinstance(player, dict):
                    continue

                normalized_player = (
                    normalize_player(player)
                )

                normalized_players.append(
                    normalized_player
                )

            if not normalized_players:
                continue

            normalized_players.sort(
                key=lambda x: (
                    x["car_no"]
                    if x["car_no"] is not None
                    else 999
                )
            )

            race = {
                "venue": normalize_text(
                    venue_name
                ),

                "race_no": to_int(
                    race_no
                ),

                "race_key": (
                    f"{normalize_text(venue_name)}"
                    f"_{race_no}R"
                ),

                "player_count":
                    len(normalized_players),

                "players":
                    normalized_players,
            }

            normalized_races.append(race)

            total_players += len(
                normalized_players
            )

    normalized_races.sort(
        key=lambda x: (
            x["venue"],
            x["race_no"]
            if x["race_no"] is not None
            else 999
        )
    )

    print()
    print("🔥 正規化完了")
    print(
        "レース件数:",
        len(normalized_races),
    )
    print(
        "選手件数:",
        total_players,
    )

    print()
    print("=" * 70)
    print("🔥 RACE SAMPLE")
    print("=" * 70)

    if normalized_races:

        sample_race = normalized_races[0]

        print(
            "RACE KEY:",
            sample_race["race_key"],
        )

        print(
            "選手数:",
            sample_race["player_count"],
        )

        for player in sample_race["players"]:

            print()
            print(
                f'{player["car_no"]}番 '
                f'{player["player_name"]} '
                f'ID:{player["player_id"]}'
            )

            print(
                "  得点:",
                player["race_score"],
            )

            print(
                "  脚質:",
                player["riding_style"],
            )

            print(
                "  勝率:",
                player["win_rate"],
            )

            print(
                "  2連対:",
                player["top2_rate"],
            )

            print(
                "  3連対:",
                player["top3_rate"],
            )

            print(
                "  逃捲差マ:",
                player["nige_count"],
                player["makuri_count"],
                player["sashi_count"],
                player["mark_count"],
            )

            print(
                "  B/H/S:",
                player["back_count"],
                player["home_count"],
                player["start_count"],
            )

            print(
                "  今開催:",
                player[
                    "current_meeting_results"
                ],
            )

            print(
                "  直近開催:",
                player[
                    "recent_meeting_results"
                ],
            )

    output = {
        "source_file":
            INPUT_FILE,

        "race_count":
            len(normalized_races),

        "player_count":
            total_players,

        "races":
            normalized_races,
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
    print("🔥 162テスト終了")
    print("=" * 70)

    print(
        "正規化レース件数:",
        len(normalized_races),
    )

    print(
        "正規化選手件数:",
        total_players,
    )

    print()
    print(
        f"保存先: {OUTPUT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()