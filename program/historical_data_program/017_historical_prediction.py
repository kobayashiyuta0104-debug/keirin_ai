from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import sys

import joblib
import numpy as np
import pandas as pd


# C:\競輪AI に保存されたCSV・モデル・特徴量生成コードを使います
BASE = Path(r"C:\競輪AI")
CSV_DIR = BASE / "csv"
MODEL_DIR = BASE / "model"

sys.path.insert(0, str(BASE / "program" / "ai_program"))

from feature_generator.feature_player import build_feature_player
from feature_generator.feature_line import build_feature_line
from feature_generator.feature_race import build_feature_race
from feature_generator.feature_rank import build_feature_rank
from feature_generator.feature_relative import build_feature_relative


RACE_COLUMNS = [
    "race_key", "date", "jo_code", "jo_name", "race_no", "race_time",
    "weekday", "grade", "race_type", "session", "bank_type",
    "straight_type", "bank_angle",
]

PLAYER_FEATURE_COLUMNS = [
    "age", "term", "prefecture", "region", "home_bank", "class",
    "previous_class", "average_score", "win_rate", "quinella_rate",
    "trio_rate", "escape_count", "makuri_count", "sashi_count",
    "mark_count", "back_count", "home_count", "start_count",
    "style_両", "style_追", "style_逃", "is_seri", "score_rank",
    "win_rate_rank", "quinella_rate_rank", "trio_rate_rank",
    "line_score_rank", "line_win_rate_rank", "line_quinella_rate_rank",
    "line_trio_rate_rank", "score_diff_top", "win_rate_diff_top",
    "quinella_rate_diff_top", "trio_rate_diff_top",
    "line_score_diff_top", "line_win_rate_diff_top",
    "line_quinella_rate_diff_top", "line_trio_rate_diff_top",
]

CLASS_NAME = {
    0: "0～1,999円",
    1: "2,000～4,999円",
    2: "5,000～9,999円",
    3: "10,000～19,999円",
    4: "20,000～29,999円",
    5: "30,000～49,999円",
    6: "50,000～99,999円",
    7: "100,000円以上",
}

PROBABILITY_COLUMNS = [
    "0～\n1,999",
    "2,000～\n4,999",
    "5,000～\n9,999",
    "10,000～\n19,999",
    "20,000～\n29,999",
    "30,000～\n49,999",
    "50,000～\n99,999",
    "100,000\n以上",
]


def read_date_csv(folder, suffix, target_date):
    path = CSV_DIR / folder / f"{target_date}_{suffix}.csv"
    if not path.exists():
        raise FileNotFoundError(f"CSVが見つかりません: {path}")

    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)

    if "date" not in df.columns:
        raise ValueError(f"date列がありません: {path}")

    dates = (
        df["date"].astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.replace("-", "", regex=False)
    )
    df = df.loc[dates == target_date].copy()

    if df.empty:
        raise ValueError(f"{target_date} のデータがありません: {path}")

    return df


def normalize_is_seri(series):
    values = series.astype(str).str.strip().str.lower()
    values = values.replace({
        "true": "1", "false": "0",
        "はい": "1", "いいえ": "0",
        "yes": "1", "no": "0",
    })
    return pd.to_numeric(values, errors="coerce").fillna(0).astype(int)


def build_features(target_date):
    player_df = read_date_csv("player", "player", target_date)
    race_df = read_date_csv("race", "race", target_date)
    lines_df = read_date_csv("lines", "lines", target_date)

    required_player = {
        "race_key", "date", "car_no", "player_id", "prefecture",
        "age", "term", "class", "previous_class", "style",
        "average_score", "win_rate", "quinella_rate", "trio_rate",
        "escape_count", "makuri_count", "sashi_count", "mark_count",
        "back_count", "home_count", "start_count",
    }
    required_race = {
        "race_key", "jo_name", "event_name", "grade", "race_no",
        "track_length", "straight_length", "bank_angle", "race_type",
        "session",
    }
    required_lines = {
        "race_key", "car_no", "line_no", "line_position", "is_seri",
    }

    for label, df, required in [
        ("player", player_df, required_player),
        ("race", race_df, required_race),
        ("lines", lines_df, required_lines),
    ]:
        missing = sorted(required - set(df.columns))
        if missing:
            raise ValueError(f"{label} CSVに必要な列がありません: {missing}")

    # 日付を023と同じ形式にし、車番の型を合わせて結合します
    player_df["date"] = target_date
    player_df["car_no"] = pd.to_numeric(
        player_df["car_no"], errors="raise"
    ).astype(int)

    race_df["race_key"] = race_df["race_key"].astype(str)
    player_df["race_key"] = player_df["race_key"].astype(str)
    lines_df["race_key"] = lines_df["race_key"].astype(str)

    lines_df["car_no"] = pd.to_numeric(
        lines_df["car_no"], errors="raise"
    ).astype(int)
    lines_df["line_no"] = pd.to_numeric(
        lines_df["line_no"], errors="coerce"
    )
    lines_df["line_position"] = pd.to_numeric(
        lines_df["line_position"], errors="coerce"
    )
    lines_df["is_seri"] = normalize_is_seri(lines_df["is_seri"])

    if lines_df.duplicated(["race_key", "car_no"]).any():
        raise ValueError("lines CSVで race_key と car_no が重複しています")

    if player_df.duplicated(["race_key", "car_no"]).any():
        raise ValueError("player CSVで race_key と car_no が重複しています")

    # race CSVには発走時刻列がない場合があるため、出力用に空欄を用意します
    if "race_time" not in race_df.columns:
        race_df["race_time"] = ""

    # 023と同じく、選手CSV側の日付・競輪場コード・レース番号を残します
    race_drop_columns = ["date", "jo_code", "race_no"]
    if "jo_name" in player_df.columns:
        race_drop_columns.append("jo_name")
    race_df = race_df.drop(columns=race_drop_columns, errors="ignore")

    df = player_df.merge(
        race_df,
        on="race_key",
        how="left",
        validate="many_to_one",
    )

    if df["event_name"].isna().any():
        missing_keys = df.loc[df["event_name"].isna(), "race_key"].unique()
        raise ValueError(f"race CSVに対応するレースがありません: {list(missing_keys[:10])}")

    lines_for_merge = lines_df[
        ["race_key", "car_no", "line_no", "line_position", "is_seri"]
    ]

    df = df.merge(
        lines_for_merge,
        on=["race_key", "car_no"],
        how="left",
        validate="one_to_one",
    )

    if df[["line_no", "line_position"]].isna().any().any():
        missing_keys = df.loc[
            df["line_no"].isna() | df["line_position"].isna(),
            ["race_key", "car_no"],
        ]
        raise ValueError(
            "ライン情報がない選手がいます。lines CSVを確認してください:\n"
            + missing_keys.head(20).to_string(index=False)
        )

    df["date"] = target_date
    df = df.sort_values(["race_key", "car_no"]).reset_index(drop=True)

    # 023と同じ特徴量生成処理
    df = build_feature_player(df)
    df = build_feature_line(df)
    df = build_feature_race(df)
    df = build_feature_rank(df)
    df = build_feature_relative(df)

    return df


def build_race_rows(features_df):
    race_rows = []

    for race_key, race_df in features_df.groupby("race_key", sort=False):
        race_row = {}
        first_row = race_df.iloc[0]

        for column in RACE_COLUMNS:
            race_row[column] = first_row[column] if column in race_df.columns else pd.NA

        for line_no in range(1, 10):
            line_df = race_df[race_df["line_no"] == line_no].copy()
            if not line_df.empty:
                line_df = line_df.sort_values("line_position")

            for position in range(1, 10):
                prefix = f"L{line_no}_P{position}"

                if position <= len(line_df):
                    player = line_df.iloc[position - 1]
                    for feature in PLAYER_FEATURE_COLUMNS:
                        race_row[f"{prefix}_{feature}"] = (
                            player[feature] if feature in player.index else pd.NA
                        )
                else:
                    for feature in PLAYER_FEATURE_COLUMNS:
                        race_row[f"{prefix}_{feature}"] = pd.NA

        race_rows.append(race_row)

    result = pd.DataFrame(race_rows)
    result = result.where(pd.notna(result), np.nan)

    # 027のCSV保存・025の再読込後に近い型に整えます
    text_columns = {
        "race_key", "date", "jo_name", "race_time", "weekday",
        "grade", "race_type", "session", "bank_type",
    }

    for column in result.columns:
        if (
            column not in text_columns
            and not column.endswith("_prefecture")
            and not column.endswith("_region")
        ):
            result[column] = pd.to_numeric(result[column], errors="coerce")

    return result


def predict(race_df, target_date):
    model_path = MODEL_DIR / "lightgbm_model.pkl"
    feature_path = MODEL_DIR / "feature_columns.json"

    if not model_path.exists():
        raise FileNotFoundError(f"モデルが見つかりません: {model_path}")
    if not feature_path.exists():
        raise FileNotFoundError(f"特徴量一覧が見つかりません: {feature_path}")

    model = joblib.load(model_path)
    with feature_path.open("r", encoding="utf-8") as f:
        feature_columns = json.load(f)

    missing = [column for column in feature_columns if column not in race_df.columns]
    if missing:
        raise ValueError(f"予測用特徴量が不足しています: {missing}")

    X = race_df[feature_columns].copy()

    categorical_columns = [
        "jo_name", "grade", "race_type", "session",
        "weekday", "bank_type", "straight_type",
    ]
    categorical_columns.extend(
        column for column in X.columns
        if column.endswith("_prefecture") or column.endswith("_region")
    )

    for column in categorical_columns:
        if column in X.columns:
            X[column] = X[column].astype("category")

    predicted_class = model.predict(X)
    probabilities = model.predict_proba(X)

    if probabilities.shape[1] != 8:
        raise ValueError(
            f"モデルの確率列が8個ではありません: {probabilities.shape[1]}"
        )

    result = race_df.copy()
    result["predict_class"] = predicted_class
    result["predict_probability"] = probabilities.max(axis=1)
    result["AI予想"] = result["predict_class"].map(CLASS_NAME)
    result["AI確信度"] = (
        (result["predict_probability"] * 100)
        .round(0).astype(int).astype(str) + "%"
    )

    for index, column in enumerate(PROBABILITY_COLUMNS):
        result[column] = (
            (probabilities[:, index] * 100)
            .round(0).astype(int).astype(str) + "%"
        )

    return save_prediction(result, target_date)


def save_prediction(result, target_date):
    session_order = {
        "モーニング": 0,
        "デイ": 1,
        "ナイター": 2,
        "ミッドナイト": 3,
    }

    result["session_order"] = result["session"].map(session_order)
    result = result.sort_values(
        ["session_order", "jo_name", "race_no"]
    ).drop(columns=["session_order"])

    result["日付"] = target_date[:4] + "-" + target_date[4:6] + "-" + target_date[6:]
    result = result.rename(columns={
        "grade": "グレード",
        "jo_name": "競輪場",
        "race_no": "レース\n番号",
        "race_type": "レース種別",
        "race_time": "発走\n時刻",
        "session": "開催区分",
    })

    result["レース\n番号"] = (
        pd.to_numeric(result["レース\n番号"], errors="raise")
        .astype(int).astype(str) + "R"
    )
    result["レースキー"] = (
        target_date + "_" + result["競輪場"].astype(str)
        + "_" + result["レース\n番号"]
    )

    result["三連単\n払戻"] = ""
    result["実際\nクラス"] = ""
    result["的中\n判定"] = ""
    result["方向性\n判定"] = ""

    for car_no in range(1, 10):
        result[f"{car_no}号車\n期待度"] = ""

    result["１着"] = ""
    result["２着"] = ""
    result["３着"] = ""

    jst = timezone(timedelta(hours=9))
    result["予想日時"] = datetime.now(jst).strftime("%Y-%m-%d %H:%M:%S")
    result["AIバージョン"] = "Ver1.0"
    result["AIコメント"] = ""

    output_columns = [
        "レースキー", "日付", "グレード", "競輪場", "レース\n番号",
        "レース種別", "発走\n時刻", "開催区分", "AI予想", "AI確信度",
        *PROBABILITY_COLUMNS,
        "三連単\n払戻", "実際\nクラス", "的中\n判定", "方向性\n判定",
        *[f"{i}号車\n期待度" for i in range(1, 10)],
        "１着", "２着", "３着", "予想日時", "AIバージョン", "AIコメント",
    ]

    output_dir = CSV_DIR / "prediction"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{target_date}_prediction.csv"

    result[output_columns].to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"予測レース数: {len(result):,}")
    print(f"保存先: {output_path}")
    return output_path


def main():
    target_date = input("対象日付を入力してください（YYYYMMDD）: ").strip()

    try:
        datetime.strptime(target_date, "%Y%m%d")
    except ValueError:
        raise ValueError("日付はYYYYMMDD形式で入力してください（例: 20261026）")

    print(f"対象日: {target_date}")
    features_df = build_features(target_date)
    race_df = build_race_rows(features_df)
    predict(race_df, target_date)


if __name__ == "__main__":
    main()