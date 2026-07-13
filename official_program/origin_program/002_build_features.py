"""
===========================================================
競輪AI 正式版
002_build_features.py

Part 1
・基本設定
・正式特徴量定義
・共通変換関数
・9車対応特徴量名生成
===========================================================
"""

import json
from pathlib import Path
from collections import Counter


# ===========================================================
# Part 1
# 基本設定・特徴量定義
# ===========================================================


# ===========================================================
# ファイル設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

INPUT_FILE = (
    BASE
    / "data_official"
    / "001_official_dataset.json"
)

OUTPUT_FILE = (
    BASE
    / "data_official"
    / "002_feature_dataset.json"
)

VALIDATION_FILE = (
    BASE
    / "data_official"
    / "002_feature_validation.json"
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)


# ===========================================================
# 最大車立て
# ===========================================================

MAX_PLAYER_SLOTS = 9


# ===========================================================
# 選手特徴量正式定義
# ===========================================================

PLAYER_BASE_FEATURES = [

    "prefecture",

    "previous_class",

    "class",

    "riding_style",

    "graduation_term",

    "age",

    "race_score",

    "nige_count",

    "makuri_count",

    "sashi_count",

    "mark_count",

    "back_count",

    "home_count",

    "start_count",

    "win_rate",

    "top2_rate",

    "top3_rate",

]


# ===========================================================
# 過去開催着順特徴量
# ===========================================================

RECENT_FINISH_SLOTS = 3


# ===========================================================
# 選手1人分の正式特徴量名
# ===========================================================

def build_player_feature_names(player_slot):
    """
    指定選手スロットの特徴量名を生成

    例:
    p1_prefecture
    p1_race_score
    p1_recent_finish_1
    """

    prefix = f"p{player_slot}_"

    names = []

    for feature_name in PLAYER_BASE_FEATURES:

        names.append(
            prefix + feature_name
        )

    for recent_no in range(
        1,
        RECENT_FINISH_SLOTS + 1,
    ):

        names.append(
            prefix
            + f"recent_finish_{recent_no}"
        )

    return names


# ===========================================================
# 全選手特徴量名生成
# ===========================================================

def build_all_player_feature_names():
    """
    p1～p9の正式特徴量名を生成
    """

    names = []

    for player_slot in range(
        1,
        MAX_PLAYER_SLOTS + 1,
    ):

        names.extend(
            build_player_feature_names(
                player_slot
            )
        )

    return names


# ===========================================================
# レース共通特徴量
# ===========================================================

RACE_FEATURE_NAMES = [

    "player_count",

]


# ===========================================================
# 正式特徴量名生成
# ===========================================================

def build_official_feature_names():
    """
    正式特徴量順を生成

    順番は学習・予測で固定する
    """

    names = []

    names.extend(
        build_all_player_feature_names()
    )

    names.extend(
        RACE_FEATURE_NAMES
    )

    return names


# ===========================================================
# 共通変換
# ===========================================================

def to_int(value):
    """
    int変換
    """

    if value in (
        None,
        "",
    ):

        return None

    try:

        return int(
            float(
                str(value)
                .replace(",", "")
                .replace("%", "")
                .strip()
            )
        )

    except Exception:

        return None


def to_float(value):
    """
    float変換
    """

    if value in (
        None,
        "",
    ):

        return None

    try:

        return float(
            str(value)
            .replace(",", "")
            .replace("%", "")
            .strip()
        )

    except Exception:

        return None


# ===========================================================
# JSON読込
# ===========================================================

def load_official_dataset():
    """
    001 Official Dataset読込
    """

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        data = json.load(f)

    if not isinstance(data, list):

        raise ValueError(
            "001_official_dataset.json "
            "のTOP構造がlistではありません"
        )

    return data


# ===========================================================
# 特徴量定義検証
# ===========================================================

def validate_feature_names(feature_names):
    """
    特徴量名重複確認
    """

    counter = Counter(
        feature_names
    )

    duplicates = {

        name: count

        for name, count
        in counter.items()

        if count > 1

    }

    return duplicates


# ===========================================================
# End Part 1
# ===========================================================


# ===========================================================
# Part 2
# 選手特徴量展開
# ===========================================================


# ===========================================================
# recent_finish取得
# ===========================================================

def get_recent_finish_values(player):
    """
    選手のrecent_meeting_resultsから
    recent_finish_1～3を正式取得する

    元RAW上のスロット位置をそのまま維持する
    非数値着順はNoneとして保持する
    """

    recent_results = player.get(
        "recent_meeting_results"
    )

    if not isinstance(
        recent_results,
        list,
    ):

        recent_results = []

    values = []

    for recent_no in range(
        RECENT_FINISH_SLOTS
    ):

        if recent_no >= len(
            recent_results
        ):

            values.append(None)

            continue

        result = recent_results[
            recent_no
        ]

        if not isinstance(
            result,
            dict,
        ):

            values.append(None)

            continue

        finish = to_int(
            result.get("finish")
        )

        values.append(finish)

    return values


# ===========================================================
# 選手1人分特徴量生成
# ===========================================================

def build_player_features(
    player,
    player_slot,
):
    """
    選手1人を正式特徴量へ変換

    player_slot:
    1～9
    """

    prefix = f"p{player_slot}_"

    features = {}

    for feature_name in PLAYER_BASE_FEATURES:

        features[
            prefix + feature_name
        ] = player.get(
            feature_name
        )

    recent_finish_values = (
        get_recent_finish_values(
            player
        )
    )

    for recent_no, finish in enumerate(
        recent_finish_values,
        1,
    ):

        features[
            prefix
            + f"recent_finish_{recent_no}"
        ] = finish

    return features


# ===========================================================
# 欠損選手スロット生成
# ===========================================================

def build_empty_player_features(
    player_slot,
):
    """
    存在しない車番スロット用の
    None特徴量を生成

    例:
    5車立ての場合
    p6～p9をすべてNoneにする
    """

    feature_names = (
        build_player_feature_names(
            player_slot
        )
    )

    return {

        feature_name: None

        for feature_name
        in feature_names

    }


# ===========================================================
# p1～p9特徴量生成
# ===========================================================

def build_all_player_features(players):
    """
    playersをp1～p9へ正式展開

    車番をスロット番号として使用する

    例:
    車番1 -> p1
    車番7 -> p7
    車番9 -> p9
    """

    features = {}

    player_map = {}

    problems = []

    for player in players:

        if not isinstance(
            player,
            dict,
        ):

            problems.append(
                "INVALID_PLAYER_STRUCTURE"
            )

            continue

        car_no = to_int(
            player.get("car_no")
        )

        if car_no is None:

            problems.append(
                "EMPTY_CAR_NO"
            )

            continue

        if not (
            1
            <= car_no
            <= MAX_PLAYER_SLOTS
        ):

            problems.append(
                f"INVALID_CAR_NO:{car_no}"
            )

            continue

        if car_no in player_map:

            problems.append(
                f"DUPLICATE_CAR_NO:{car_no}"
            )

            continue

        player_map[
            car_no
        ] = player

    for player_slot in range(
        1,
        MAX_PLAYER_SLOTS + 1,
    ):

        player = player_map.get(
            player_slot
        )

        if player is None:

            slot_features = (
                build_empty_player_features(
                    player_slot
                )
            )

        else:

            slot_features = (
                build_player_features(
                    player,
                    player_slot,
                )
            )

        features.update(
            slot_features
        )

    return features, problems


# ===========================================================
# 選手スロット整合性検証
# ===========================================================

def validate_player_slots(
    race,
    player_features,
):
    """
    player_countと実選手数、
    p1～p9特徴量構造を検証
    """

    problems = []

    players = race.get(
        "players"
    )

    if not isinstance(
        players,
        list,
    ):

        players = []

    player_count = to_int(
        race.get("player_count")
    )

    if player_count != len(
        players
    ):

        problems.append(
            "PLAYER_COUNT_MISMATCH"
        )

    expected_names = (
        build_all_player_feature_names()
    )

    actual_names = set(
        player_features.keys()
    )

    missing_names = [

        name

        for name
        in expected_names

        if name not in actual_names

    ]

    extra_names = [

        name

        for name
        in actual_names

        if name not in expected_names

    ]

    if missing_names:

        problems.append(
            "PLAYER_FEATURE_MISSING"
        )

    if extra_names:

        problems.append(
            "PLAYER_FEATURE_EXTRA"
        )

    return (
        problems,
        missing_names,
        extra_names,
    )


# ===========================================================
# End Part 2
# ===========================================================


# ===========================================================
# Part 3
# レース特徴量・正式Feature Dataset生成
# ===========================================================


# ===========================================================
# レース共通特徴量生成
# ===========================================================

def build_race_features(race):
    """
    レース単位の共通特徴量を生成
    """

    return {

        "player_count":
            to_int(
                race.get("player_count")
            ),

    }


# ===========================================================
# labels取得
# ===========================================================

def build_labels(race):
    """
    001 Official Datasetのlabelsを
    Feature Dataset用に正式取得する
    """

    labels = race.get("labels")

    if not isinstance(
        labels,
        dict,
    ):

        labels = {}

    return {

        "trifecta_combination":
            labels.get(
                "trifecta_combination"
            ),

        "trifecta_payout":
            to_int(
                labels.get(
                    "trifecta_payout"
                )
            ),

        "trifecta_popularity":
            labels.get(
                "trifecta_popularity"
            ),

        "payout_class_4":
            labels.get(
                "payout_class_4"
            ),

        "is_20000_plus":
            to_int(
                labels.get(
                    "is_20000_plus"
                )
            ),

        "is_50000_plus":
            to_int(
                labels.get(
                    "is_50000_plus"
                )
            ),

    }


# ===========================================================
# 1レース特徴量生成
# ===========================================================

def build_race_feature_record(race):
    """
    Official Datasetの1レースを

    race情報
    +
    181正式特徴量
    +
    labels

    へ変換する
    """

    race_key = race.get(
        "race_key"
    )

    players = race.get(
        "players"
    )

    if not isinstance(
        players,
        list,
    ):

        players = []

    player_features, player_problems = (
        build_all_player_features(
            players
        )
    )

    race_features = (
        build_race_features(
            race
        )
    )

    features = {}

    features.update(
        player_features
    )

    features.update(
        race_features
    )

    labels = build_labels(
        race
    )

    return {

        "race_key":
            race_key,

        "race_date":
            race.get(
                "race_date"
            ),

        "venue":
            race.get(
                "venue"
            ),

        "race_no":
            to_int(
                race.get(
                    "race_no"
                )
            ),

        "player_count":
            to_int(
                race.get(
                    "player_count"
                )
            ),

        "features":
            features,

        "labels":
            labels,

    }, player_problems


# ===========================================================
# 特徴量順正式整列
# ===========================================================

def order_features(features, feature_names):
    """
    特徴量を正式定義順へ並べ直す

    Python dictの挿入順を利用し、
    JSON保存後も正式列順を維持する
    """

    ordered = {}

    for feature_name in feature_names:

        ordered[
            feature_name
        ] = features.get(
            feature_name
        )

    return ordered


# ===========================================================
# 1レース特徴量検証
# ===========================================================

def validate_race_feature_record(
    source_race,
    feature_record,
    official_feature_names,
):
    """
    1レース分の正式特徴量構造を検証
    """

    problems = []

    features = feature_record.get(
        "features"
    )

    if not isinstance(
        features,
        dict,
    ):

        return [
            "INVALID_FEATURE_STRUCTURE"
        ]

    actual_names = list(
        features.keys()
    )

    if len(features) != len(
        official_feature_names
    ):

        problems.append(
            "FEATURE_COUNT_MISMATCH"
        )

    if actual_names != official_feature_names:

        problems.append(
            "FEATURE_ORDER_MISMATCH"
        )

    player_feature_names = (
        build_all_player_feature_names()
    )

    player_features_only = {

        name: features.get(name)

        for name in player_feature_names

    }

    slot_problems, missing_names, extra_names = (
        validate_player_slots(
            source_race,
            player_features_only,
        )
    )

    problems.extend(
        slot_problems
    )

    if missing_names:

        problems.append(
            "MISSING_FEATURE_NAMES:"
            + ",".join(
                missing_names[:10]
            )
        )

    if extra_names:

        problems.append(
            "EXTRA_FEATURE_NAMES:"
            + ",".join(
                extra_names[:10]
            )
        )

    labels = feature_record.get(
        "labels"
    )

    if not isinstance(
        labels,
        dict,
    ):

        problems.append(
            "INVALID_LABEL_STRUCTURE"
        )

    else:

        if labels.get(
            "trifecta_payout"
        ) is None:

            problems.append(
                "TRIFECTA_PAYOUT_MISSING"
            )

        if labels.get(
            "payout_class_4"
        ) is None:

            problems.append(
                "PAYOUT_CLASS_MISSING"
            )

    return problems


# ===========================================================
# Feature Dataset一括生成
# ===========================================================

def build_feature_dataset(
    official_dataset,
):
    """
    Official Dataset全レースから
    正式Feature Datasetを生成
    """

    official_feature_names = (
        build_official_feature_names()
    )

    dataset = []

    problems = []

    feature_count_dist = Counter()

    player_count_dist = Counter()

    payout_class_dist = Counter()

    for race in official_dataset:

        race_key = race.get(
            "race_key"
        )

        feature_record, build_problems = (
            build_race_feature_record(
                race
            )
        )

        feature_record["features"] = (
            order_features(
                feature_record[
                    "features"
                ],
                official_feature_names,
            )
        )

        for problem in build_problems:

            problems.append({

                "race_key":
                    race_key,

                "problem":
                    problem,

            })

        validation_problems = (
            validate_race_feature_record(
                race,
                feature_record,
                official_feature_names,
            )
        )

        for problem in validation_problems:

            problems.append({

                "race_key":
                    race_key,

                "problem":
                    problem,

            })

        feature_count = len(
            feature_record[
                "features"
            ]
        )

        feature_count_dist[
            feature_count
        ] += 1

        player_count = (
            feature_record.get(
                "player_count"
            )
        )

        player_count_dist[
            player_count
        ] += 1

        payout_class = (
            feature_record[
                "labels"
            ].get(
                "payout_class_4"
            )
        )

        payout_class_dist[
            payout_class
        ] += 1

        dataset.append(
            feature_record
        )

    return (

        dataset,

        official_feature_names,

        feature_count_dist,

        player_count_dist,

        payout_class_dist,

        problems,

    )


# ===========================================================
# End Part 3
# ===========================================================


# ===========================================================
# Part 4
# 保存・検証レポート・main
# ===========================================================


# ===========================================================
# Feature Dataset保存
# ===========================================================

def save_feature_dataset(dataset):
    """
    正式Feature DatasetをJSON保存
    """

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            dataset,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ===========================================================
# 検証レポート生成
# ===========================================================

def build_validation_report(
    dataset,
    official_feature_names,
    feature_count_dist,
    player_count_dist,
    payout_class_dist,
    problems,
):
    """
    002正式検証レポート生成
    """

    feature_name_duplicates = (
        validate_feature_names(
            official_feature_names
        )
    )

    race_key_counter = Counter(

        race.get("race_key")

        for race in dataset

    )

    duplicate_race_keys = {

        race_key: count

        for race_key, count
        in race_key_counter.items()

        if count > 1

    }

    complete_feature_count = sum(

        1

        for race in dataset

        if len(
            race.get(
                "features",
                {},
            )
        )
        == len(
            official_feature_names
        )

    )

    exact_feature_order_count = sum(

        1

        for race in dataset

        if list(
            race.get(
                "features",
                {}
            ).keys()
        )
        == official_feature_names

    )

    nine_player_races = [

        race

        for race in dataset

        if race.get(
            "player_count"
        )
        == 9

    ]

    nine_player_complete_count = sum(

        1

        for race in nine_player_races

        if all(

            race.get(
                "features",
                {}
            ).get(
                f"p{slot}_race_score"
            )
            is not None

            for slot in range(
                1,
                MAX_PLAYER_SLOTS + 1,
            )

        )

    )

    report = {

        "input_file":
            str(INPUT_FILE),

        "output_file":
            str(OUTPUT_FILE),

        "race_count":
            len(dataset),

        "official_feature_count":
            len(
                official_feature_names
            ),

        "official_feature_names":
            official_feature_names,

        "feature_name_duplicates":
            feature_name_duplicates,

        "feature_count_distribution":
            dict(
                feature_count_dist
            ),

        "player_count_distribution":
            dict(
                player_count_dist
            ),

        "payout_class_distribution":
            dict(
                payout_class_dist
            ),

        "complete_feature_count":
            complete_feature_count,

        "exact_feature_order_count":
            exact_feature_order_count,

        "duplicate_race_keys":
            duplicate_race_keys,

        "nine_player_race_count":
            len(
                nine_player_races
            ),

        "nine_player_complete_count":
            nine_player_complete_count,

        "problem_count":
            len(problems),

        "problems":
            problems,

    }

    return report


# ===========================================================
# 検証レポート保存
# ===========================================================

def save_validation_report(report):
    """
    検証結果をJSON保存
    """

    with open(
        VALIDATION_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ===========================================================
# 9車立てサンプル表示
# ===========================================================

def print_nine_player_sample(dataset):
    """
    9車立てレースを1件表示
    """

    nine_player_race = None

    for race in dataset:

        if race.get(
            "player_count"
        ) == 9:

            nine_player_race = race

            break

    if nine_player_race is None:

        print()
        print(
            "9車立てサンプル: なし"
        )

        return

    print()
    print(
        "=== 9車立てサンプル確認 ==="
    )

    print(
        "race_key:",
        nine_player_race.get(
            "race_key"
        ),
    )

    print(
        "player_count:",
        nine_player_race.get(
            "player_count"
        ),
    )

    features = nine_player_race.get(
        "features",
        {},
    )

    for slot in range(
        1,
        MAX_PLAYER_SLOTS + 1,
    ):

        print(
            f"p{slot}:",
            "race_score=",
            features.get(
                f"p{slot}_race_score"
            ),
            "/ recent=",
            [
                features.get(
                    f"p{slot}_recent_finish_{n}"
                )
                for n in range(
                    1,
                    RECENT_FINISH_SLOTS + 1,
                )
            ],
        )


# ===========================================================
# main
# ===========================================================

def main():

    print(
        "=== 002 正式9車対応 "
        "Feature Dataset生成 ==="
    )

    official_dataset = (
        load_official_dataset()
    )

    print(
        "001 Official Datasetレース数:",
        len(official_dataset),
    )

    (

        dataset,

        official_feature_names,

        feature_count_dist,

        player_count_dist,

        payout_class_dist,

        problems,

    ) = build_feature_dataset(
        official_dataset
    )

    report = build_validation_report(

        dataset,

        official_feature_names,

        feature_count_dist,

        player_count_dist,

        payout_class_dist,

        problems,

    )

    save_feature_dataset(
        dataset
    )

    save_validation_report(
        report
    )

    print()
    print("=== 002 結果 ===")

    print(
        "生成レース数:",
        len(dataset),
    )

    print(
        "正式特徴量数:",
        len(
            official_feature_names
        ),
    )

    print(
        "特徴量数分布:",
        dict(
            feature_count_dist
        ),
    )

    print(
        "車立て分布:",
        dict(
            player_count_dist
        ),
    )

    print(
        "4分類分布:",
        dict(
            payout_class_dist
        ),
    )

    print(
        "正式特徴量数完全一致:",
        report[
            "complete_feature_count"
        ],
    )

    print(
        "特徴量順完全一致:",
        report[
            "exact_feature_order_count"
        ],
    )

    print(
        "特徴量名重複:",
        report[
            "feature_name_duplicates"
        ],
    )

    print(
        "race_key重複:",
        report[
            "duplicate_race_keys"
        ],
    )

    print(
        "9車立てレース数:",
        report[
            "nine_player_race_count"
        ],
    )

    print(
        "問題件数:",
        report[
            "problem_count"
        ],
    )

    print_nine_player_sample(
        dataset
    )

    if problems:

        print()
        print(
            "=== 問題一覧 先頭50件 ==="
        )

        for problem in problems[:50]:

            print(problem)

    print()
    print(
        "Feature Dataset保存:"
    )
    print(
        OUTPUT_FILE
    )

    print()
    print(
        "検証レポート保存:"
    )
    print(
        VALIDATION_FILE
    )

    print()
    print(
        "=== 002 完了 ==="
    )


if __name__ == "__main__":

    main()


# ===========================================================
# End Part 4
# ===========================================================