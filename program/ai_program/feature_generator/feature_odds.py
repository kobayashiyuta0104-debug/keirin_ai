
"""
============================================================
競輪AI
feature_odds.py

過去レースの確定オッズ特徴量を生成する

・過去オッズCSVの読み込み
・3連単オッズの人気順位算出
・仕様書の20特徴量を生成
・race_keyで既存データに結合

注意：
当日予想用の処理では使用しない。
当日分のオッズは特徴量に使用しない。
============================================================
"""

from pathlib import Path
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd


# ============================================================
# 基本設定
# ============================================================

BASE = Path(r"C:\競輪AI")

ODDS_DIR = (
    BASE
    / "csv"
    / "historical_date"
    / "historical_odds"
)

JST = timezone(timedelta(hours=9))


# ============================================================
# 3連単オッズの組み合わせ列
# ============================================================

# 9車立ての3連単504通り
ODDS_COLUMNS = [
    f"{a}-{b}-{c}"
    for a in range(1, 10)
    for b in range(1, 10)
    for c in range(1, 10)
    if a != b and a != c and b != c
]


# ============================================================
# 生成する特徴量
# ============================================================

ODDS_FEATURE_COLUMNS = [
    "odds_rank_1",
    "odds_rank_2",
    "odds_rank_3",
    "odds_rank_5",
    "odds_rank_10",
    "odds_rank_20",
    "odds_rank_30",
    "odds_rank_50",
    "odds_rank_100",
    "odds_ratio_1_2",
    "odds_ratio_1_3",
    "odds_ratio_1_5",
    "odds_ratio_1_10",
    "odds_spread_1_5",
    "odds_spread_1_10",
    "odds_spread_1_20",
    "odds_top5_mean",
    "odds_top10_mean",
    "odds_10_30_mean",
    "odds_30_100_mean",
]


# ============================================================
# オッズから20特徴量を生成
# ============================================================

def build_odds_features(odds_df):
    """
    1レース1行のオッズデータから20特徴量を生成する。

    odds_df:
        1行が1レース。
        race_keyと3連単オッズ列を持つDataFrame。
    """

    required_columns = ["race_key"] + ODDS_COLUMNS

    missing_columns = [
        col for col in required_columns
        if col not in odds_df.columns
    ]

    if missing_columns:
        raise ValueError(
            "オッズCSVに必要な列がありません。\n"
            f"不足列数: {len(missing_columns)}\n"
            f"不足列の例: {missing_columns[:10]}"
        )

    # オッズを数値化
    odds = odds_df[ODDS_COLUMNS].apply(
        pd.to_numeric,
        errors="coerce",
    )

    # 0以下の値は有効なオッズとして扱わない
    odds = odds.where(odds > 0)

    # 各レースでオッズが低い順に並べる
    # NaNは末尾に配置される
    sorted_odds = np.sort(
        odds.to_numpy(dtype=float),
        axis=1,
    )

    # 人気順位を取得
    def rank_odds(rank):
        """
        rankは1始まり。
        存在しない順位はNaN。
        """
        index = rank - 1

        if index >= sorted_odds.shape[1]:
            return np.full(len(odds_df), np.nan)

        values = sorted_odds[:, index]

        return np.where(
            np.isfinite(values),
            values,
            np.nan,
        )

    features = pd.DataFrame(
        {
            "race_key": odds_df["race_key"].astype(str).values,

            "odds_rank_1": rank_odds(1),
            "odds_rank_2": rank_odds(2),
            "odds_rank_3": rank_odds(3),
            "odds_rank_5": rank_odds(5),
            "odds_rank_10": rank_odds(10),
            "odds_rank_20": rank_odds(20),
            "odds_rank_30": rank_odds(30),
            "odds_rank_50": rank_odds(50),
            "odds_rank_100": rank_odds(100),
        }
    )

    # オッズ比
    for rank in [2, 3, 5, 10]:
        numerator = features[f"odds_rank_{rank}"]
        denominator = features["odds_rank_1"]

        features[f"odds_ratio_1_{rank}"] = (
            numerator / denominator
        ).where(denominator > 0)

    # オッズ差
    for rank in [5, 10, 20]:
        features[f"odds_spread_1_{rank}"] = (
            features[f"odds_rank_{rank}"]
            - features["odds_rank_1"]
        )

    # 人気順位の範囲を指定して平均を計算する。
    # 範囲内に欠損がある場合は平均を作らない。
    def exact_mean(start_rank, end_rank):
        values = sorted_odds[
            :,
            start_rank - 1:end_rank,
        ]

        complete = np.isfinite(values).all(axis=1)

        result = np.full(len(odds_df), np.nan)

        result[complete] = values[complete].mean(axis=1)

        return result

    features["odds_top5_mean"] = exact_mean(1, 5)
    features["odds_top10_mean"] = exact_mean(1, 10)
    features["odds_10_30_mean"] = exact_mean(10, 30)
    features["odds_30_100_mean"] = exact_mean(30, 100)

    # 列順を仕様書に合わせる
    features = features[
        ["race_key"] + ODDS_FEATURE_COLUMNS
    ]

    return features


# ============================================================
# 過去オッズCSVを読み込み、特徴量をまとめる
# ============================================================

def load_historical_odds_features():
    """
    historical_odds内の日別CSVから特徴量を生成する。

    当日分のオッズは除外する。
    """

    if not ODDS_DIR.exists():
        raise FileNotFoundError(
            f"オッズフォルダがありません: {ODDS_DIR}"
        )

    csv_files = sorted(ODDS_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"オッズCSVが見つかりません: {ODDS_DIR}"
        )

    today = datetime.now(JST).strftime("%Y%m%d")

    all_features = []

    print("=" * 60)
    print("過去オッズ特徴量の生成開始")
    print(f"オッズフォルダ: {ODDS_DIR}")
    print(f"当日除外日: {today}")
    print(f"CSVファイル数: {len(csv_files)}")
    print("=" * 60)

    for file_no, csv_file in enumerate(csv_files, start=1):

        print(
            f"[{file_no}/{len(csv_files)}] "
            f"読み込み: {csv_file.name}"
        )

        # 1日分ずつ読み込み、必要な列だけ使う
        odds_df = pd.read_csv(
            csv_file,
            usecols=lambda col: (
                col in {"race_key", "date"}
                or col in ODDS_COLUMNS
            ),
            low_memory=False,
        )

        if "race_key" not in odds_df.columns:
            raise ValueError(
                f"race_keyがありません: {csv_file.name}"
            )

        if "date" not in odds_df.columns:
            raise ValueError(
                f"date列がありません: {csv_file.name}"
            )

        # 日付を文字列に統一
        date_values = (
            odds_df["date"]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.replace("-", "", regex=False)
            .str.replace("/", "", regex=False)
        )

        # 当日以降のデータは学習用特徴量に入れない
        odds_df = odds_df.loc[
            date_values < today
        ].copy()

        if odds_df.empty:
            print("  対象なし（当日以降のため除外）")
            continue

        # 1レース1行であることを確認
        if odds_df["race_key"].duplicated().any():
            duplicates = odds_df.loc[
                odds_df["race_key"].duplicated(keep=False),
                "race_key",
            ].tolist()

            raise ValueError(
                f"race_keyが重複しています: {csv_file.name}\n"
                f"重複例: {duplicates[:5]}"
            )

        # 特徴量を生成
        features = build_odds_features(odds_df)

        all_features.append(features)

        print(f"  対象レース数: {len(features):,}")

    if not all_features:
        raise ValueError(
            "特徴量を生成できる過去オッズデータがありません。"
        )

    result = pd.concat(
        all_features,
        ignore_index=True,
    )

    # 日付の異なるファイル間でも重複を確認
    if result["race_key"].duplicated().any():
        duplicates = result.loc[
            result["race_key"].duplicated(keep=False),
            "race_key",
        ].tolist()

        raise ValueError(
            "複数CSV間でrace_keyが重複しています。\n"
            f"重複例: {duplicates[:10]}"
        )

    print("=" * 60)
    print("過去オッズ特徴量の生成完了")
    print(f"対象レース数: {len(result):,}")
    print(f"特徴量数: {len(ODDS_FEATURE_COLUMNS)}")
    print("=" * 60)

    return result


# ============================================================
# 既存データへ結合する関数
# ============================================================

def add_odds_features(df):
    """
    学習用DataFrameに過去オッズ特徴量を結合する。

    df:
        既存のtraining_base.csvを読み込んだDataFrame。
        race_key列が必要。

    戻り値:
        オッズ特徴量20列を追加したDataFrame。
    """

    if "race_key" not in df.columns:
        raise ValueError(
            "結合元DataFrameにrace_keyがありません。"
        )

    print("=" * 60)
    print("オッズ特徴量の結合開始")
    print("=" * 60)

    odds_features = load_historical_odds_features()

    # 既に同名の列がある場合は誤結合を防ぐ
    existing = [
        col for col in ODDS_FEATURE_COLUMNS
        if col in df.columns
    ]

    if existing:
        raise ValueError(
            "結合元にオッズ特徴量が既に存在します。\n"
            f"対象列: {existing}\n"
            "二重追加を防ぐため処理を停止しました。"
        )

    result = df.copy()

    # race_keyの型を揃えて結合
    result["race_key"] = result["race_key"].astype(str)

    result = result.merge(
        odds_features,
        on="race_key",
        how="left",
        validate="many_to_one",
        sort=False,
    )

    matched = result["odds_rank_1"].notna().sum()

    print(f"結合後行数: {len(result):,}")
    print(f"1番人気オッズありの行数: {matched:,}")
    print(
        "1番人気オッズ欠損の行数: "
        f"{result['odds_rank_1'].isna().sum():,}"
    )
    print("オッズ特徴量の結合完了")

    return result
