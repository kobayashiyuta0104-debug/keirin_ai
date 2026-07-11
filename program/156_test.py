import json
import os


JSJ006_FILE = "155_all_venues_jsj006.json"
RESULT_FILE = "145_ai_training_race.json"
OUTPUT_FILE = "156_player_join_test.json"


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def normalize_id(value):

    if value is None:
        return ""

    value = str(value).strip()

    if not value:
        return ""

    return value.zfill(6)


def walk_objects(
    obj,
    path="ROOT",
):

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

    for path, obj in walk_objects(data):

        if not isinstance(obj, dict):
            continue

        player_id = normalize_id(
            obj.get("sensyuRegistNo")
            or obj.get("numPlayer")
        )

        if not player_id:
            continue

        # JSJ006能力データ判定
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

    for path, obj in walk_objects(data):

        if not isinstance(obj, dict):
            continue

        player_id = normalize_id(
            obj.get("sensyuRegistNo")
            or obj.get("numPlayer")
        )

        if not player_id:
            continue

        # 確定結果選手判定
        if "tyaku" not in obj:
            continue

        players.append({
            "path": path,
            "player_id": player_id,
            "data": obj,
        })

    return players


def main():

    print("=" * 70)
    print("🔥 156 JSJ006 × 確定結果 選手登録番号結合テスト")
    print("=" * 70)

    if not os.path.exists(
        JSJ006_FILE
    ):

        print(
            f"❌ ファイル無し: "
            f"{JSJ006_FILE}"
        )

        return

    if not os.path.exists(
        RESULT_FILE
    ):

        print(
            f"❌ ファイル無し: "
            f"{RESULT_FILE}"
        )

        return

    jsj006_data = load_json(
        JSJ006_FILE
    )

    result_data = load_json(
        RESULT_FILE
    )

    print()
    print("🔥 JSON読込成功")
    print(
        f"JSJ006: {JSJ006_FILE}"
    )
    print(
        f"RESULT: {RESULT_FILE}"
    )

    # ==================================================
    # 全選手探索
    # ==================================================

    print()
    print("🔥 JSJ006選手能力OBJECT探索")

    jsj006_players = find_jsj006_players(
        jsj006_data
    )

    print(
        "JSJ006能力選手OBJECT数:",
        len(jsj006_players),
    )

    print()
    print("🔥 確定結果選手OBJECT探索")

    result_players = find_result_players(
        result_data
    )

    print(
        "確定結果選手OBJECT数:",
        len(result_players),
    )

    # ==================================================
    # JSJ006登録番号INDEX
    # ==================================================

    jsj006_index = {}

    for player in jsj006_players:

        player_id = player[
            "player_id"
        ]

        jsj006_index.setdefault(
            player_id,
            []
        ).append(
            player
        )

    print()
    print(
        "JSJ006登録番号ユニーク数:",
        len(jsj006_index),
    )

    # ==================================================
    # 結合
    # ==================================================

    joined_players = []

    print()
    print("=" * 70)
    print("🔥 登録番号結合開始")
    print("=" * 70)

    for result_player in result_players:

        player_id = result_player[
            "player_id"
        ]

        result_obj = result_player[
            "data"
        ]

        candidates = jsj006_index.get(
            player_id,
            []
        )

        if not candidates:

            print(
                f"❌ 未一致 "
                f"ID:{player_id} "
                f"NAME:"
                f"{result_obj.get('sensyuName', '')}"
            )

            continue

        jsj006_player = candidates[0]

        ability_obj = jsj006_player[
            "data"
        ]

        joined = {
            "player_id": player_id,

            "player_name":
                result_obj.get(
                    "sensyuName",
                    ""
                ),

            "car_no":
                result_obj.get(
                    "syaban",
                    ""
                ),

            # ------------------------------
            # 予想前能力
            # ------------------------------

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

                "raw":
                    ability_obj,
            },

            # ------------------------------
            # 実際の結果
            # ------------------------------

            "result": {
                "finish":
                    result_obj.get(
                        "tyaku",
                        ""
                    ),

                "agari":
                    result_obj.get(
                        "agari",
                        ""
                    ),

                "kimarite":
                    result_obj.get(
                        "kimarite",
                        ""
                    ),

                "BH":
                    result_obj.get(
                        "BH",
                        ""
                    ),

                "raw":
                    result_obj,
            },

            # ------------------------------
            # 元PATH
            # ------------------------------

            "source_path": {
                "jsj006":
                    jsj006_player[
                        "path"
                    ],

                "result":
                    result_player[
                        "path"
                    ],
            },
        }

        joined_players.append(
            joined
        )

        print()
        print("🔥 結合成功")
        print(
            f"ID       : {player_id}"
        )
        print(
            "NAME     :",
            joined["player_name"],
        )
        print(
            "車番     :",
            joined["car_no"],
        )
        print(
            "競走得点 :",
            joined[
                "pre_race"
            ][
                "score"
            ],
        )
        print(
            "脚質     :",
            joined[
                "pre_race"
            ][
                "style"
            ],
        )
        print(
            "勝率     :",
            joined[
                "pre_race"
            ][
                "win_rate"
            ],
        )
        print(
            "2連対率  :",
            joined[
                "pre_race"
            ][
                "top2_rate"
            ],
        )
        print(
            "3連対率  :",
            joined[
                "pre_race"
            ][
                "top3_rate"
            ],
        )
        print(
            "S/H/B    :",
            joined[
                "pre_race"
            ][
                "s_count"
            ],
            "/",
            joined[
                "pre_race"
            ][
                "h_count"
            ],
            "/",
            joined[
                "pre_race"
            ][
                "back_count"
            ],
        )
        print(
            "逃捲差マ :",
            joined[
                "pre_race"
            ][
                "nige_count"
            ],
            "/",
            joined[
                "pre_race"
            ][
                "makuri_count"
            ],
            "/",
            joined[
                "pre_race"
            ][
                "sashi_count"
            ],
            "/",
            joined[
                "pre_race"
            ][
                "mark_count"
            ],
        )
        print(
            "着順     :",
            joined[
                "result"
            ][
                "finish"
            ],
        )
        print(
            "上がり   :",
            joined[
                "result"
            ][
                "agari"
            ],
        )
        print(
            "決まり手 :",
            joined[
                "result"
            ][
                "kimarite"
            ],
        )

    # ==================================================
    # 保存
    # ==================================================

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
    print("🔥 156テスト終了")
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
    print(
        f"保存先: {OUTPUT_FILE}"
    )

    print("=" * 70)


if __name__ == "__main__":

    main()