import json
import os


JSJ006_FILE = "155_all_venues_jsj006.json"
RESULT_FILE = "145_ai_training_race.json"
OUTPUT_FILE = "157_player_join_test.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_id(value):
    if value is None:
        return ""

    value = str(value).strip()

    if not value:
        return ""

    return value.zfill(6)


def walk_objects(obj, path="ROOT"):
    if isinstance(obj, dict):
        yield path, obj

        for key, value in obj.items():
            yield from walk_objects(
                value,
                f"{path}.{key}",
            )

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from walk_objects(
                value,
                f"{path}[{index}]",
            )


def find_jsj006_players(data):
    players = []

    ability_keys = {
        "heikinTokuten",
        "kyakusitu",
        "syouritu",
        "rentairitu2",
        "rentairitu3",
        "backCnt",
        "homeTori",
        "stTori",
        "nigeCnt",
        "makuriCnt",
        "sasiCnt",
        "markCnt",
    }

    for path, obj in walk_objects(data):
        if not isinstance(obj, dict):
            continue

        player_id = normalize_id(
            obj.get("sensyuRegistNo")
            or obj.get("numPlayer")
            or obj.get("player_id")
        )

        if not player_id:
            continue

        if not any(
            key in obj
            for key in ability_keys
        ):
            continue

        players.append({
            "path": path,
            "player_id": player_id,
            "data": obj,
        })

    return players


def find_result_players(data):
    players = []

    id_keys = [
        "player_id",
        "sensyuRegistNo",
        "numPlayer",
        "playerId",
        "registration_no",
    ]

    finish_keys = [
        "finish",
        "tyaku",
        "rank",
        "finish_position",
        "arrival",
    ]

    for path, obj in walk_objects(data):
        if not isinstance(obj, dict):
            continue

        player_id = ""

        for key in id_keys:
            if key in obj:
                player_id = normalize_id(
                    obj.get(key)
                )

                if player_id:
                    break

        if not player_id:
            continue

        finish_key = None
        finish_value = ""

        for key in finish_keys:
            if key in obj:
                finish_key = key
                finish_value = obj.get(key)
                break

        if finish_key is None:
            continue

        players.append({
            "path": path,
            "player_id": player_id,
            "finish_key": finish_key,
            "finish": finish_value,
            "data": obj,
        })

    return players


def main():
    print("=" * 70)
    print("🔥 157 正規化結果 × JSJ006 登録番号結合")
    print("=" * 70)

    if not os.path.exists(JSJ006_FILE):
        print(f"❌ ファイル無し: {JSJ006_FILE}")
        return

    if not os.path.exists(RESULT_FILE):
        print(f"❌ ファイル無し: {RESULT_FILE}")
        return

    jsj006_data = load_json(JSJ006_FILE)
    result_data = load_json(RESULT_FILE)

    print()
    print("🔥 JSON読込成功")
    print(f"JSJ006: {JSJ006_FILE}")
    print(f"RESULT: {RESULT_FILE}")

    jsj006_players = find_jsj006_players(
        jsj006_data
    )

    result_players = find_result_players(
        result_data
    )

    print()
    print("🔥 探索結果")
    print(
        "JSJ006能力選手OBJECT数:",
        len(jsj006_players),
    )
    print(
        "確定結果選手OBJECT数:",
        len(result_players),
    )

    print()
    print("=" * 70)
    print("🔥 確定結果選手候補")
    print("=" * 70)

    for index, player in enumerate(
        result_players[:20],
        start=1,
    ):
        print()
        print(f"🔥 RESULT PLAYER #{index}")
        print("PATH:", player["path"])
        print("ID:", player["player_id"])
        print(
            "FINISH KEY:",
            player["finish_key"],
        )
        print(
            "FINISH:",
            player["finish"],
        )
        print(
            json.dumps(
                player["data"],
                ensure_ascii=False,
                indent=2,
            )
        )

    jsj006_index = {}

    for player in jsj006_players:
        player_id = player["player_id"]

        jsj006_index.setdefault(
            player_id,
            []
        ).append(player)

    joined_players = []

    print()
    print("=" * 70)
    print("🔥 登録番号結合開始")
    print("=" * 70)

    for result_player in result_players:
        player_id = result_player["player_id"]

        candidates = jsj006_index.get(
            player_id,
            []
        )

        if not candidates:
            continue

        ability_player = candidates[0]

        ability_obj = ability_player["data"]
        result_obj = result_player["data"]

        joined = {
            "player_id": player_id,

            "finish":
                result_player["finish"],

            "finish_key":
                result_player["finish_key"],

            "pre_race": {
                "score":
                    ability_obj.get(
                        "heikinTokuten",
                        ""
                    ),

                "style":
                    ability_obj.get(
                        "kyakusitu",
                        ""
                    ),

                "win_rate":
                    ability_obj.get(
                        "syouritu",
                        ""
                    ),

                "top2_rate":
                    ability_obj.get(
                        "rentairitu2",
                        ""
                    ),

                "top3_rate":
                    ability_obj.get(
                        "rentairitu3",
                        ""
                    ),

                "back_count":
                    ability_obj.get(
                        "backCnt",
                        ""
                    ),

                "h_count":
                    ability_obj.get(
                        "homeTori",
                        ""
                    ),

                "s_count":
                    ability_obj.get(
                        "stTori",
                        ""
                    ),

                "nige_count":
                    ability_obj.get(
                        "nigeCnt",
                        ""
                    ),

                "makuri_count":
                    ability_obj.get(
                        "makuriCnt",
                        ""
                    ),

                "sashi_count":
                    ability_obj.get(
                        "sasiCnt",
                        ""
                    ),

                "mark_count":
                    ability_obj.get(
                        "markCnt",
                        ""
                    ),
            },

            "result": result_obj,

            "source_path": {
                "jsj006":
                    ability_player["path"],

                "result":
                    result_player["path"],
            },
        }

        joined_players.append(joined)

        if len(joined_players) <= 20:
            print()
            print("🔥🔥🔥 結合成功")
            print("ID       :", player_id)
            print(
                "着順     :",
                result_player["finish"],
            )
            print(
                "競走得点 :",
                joined["pre_race"]["score"],
            )
            print(
                "脚質     :",
                joined["pre_race"]["style"],
            )
            print(
                "勝率     :",
                joined["pre_race"]["win_rate"],
            )
            print(
                "2連対率  :",
                joined["pre_race"]["top2_rate"],
            )
            print(
                "3連対率  :",
                joined["pre_race"]["top3_rate"],
            )

    output = {
        "summary": {
            "jsj006_player_objects":
                len(jsj006_players),

            "result_player_objects":
                len(result_players),

            "joined_player_count":
                len(joined_players),
        },

        "joined_players":
            joined_players,
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
    print("🔥 157テスト終了")
    print("=" * 70)

    print(
        "JSJ006能力選手OBJECT数:",
        len(jsj006_players),
    )

    print(
        "確定結果選手OBJECT数:",
        len(result_players),
    )

    print(
        "🔥 登録番号結合成功数:",
        len(joined_players),
    )

    print()
    print(f"保存先: {OUTPUT_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()