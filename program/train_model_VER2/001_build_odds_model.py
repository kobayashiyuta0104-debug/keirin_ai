
"""
============================================================
競輪AI VER2
001_build_odds_model.py

オッズ特徴量予測AIの学習

【役割】
training_race_features.csv
    ↓
レース条件・選手能力・ライン特徴量を入力にする
    ↓
オッズ特徴量20列を個別に学習
    ↓
LightGBM回帰モデル20個を保存

注意：
・当日予想で使えないオッズ特徴量は入力に使用しない
・payout_classや確定結果も入力に使用しない
・日付で学習用と検証用を分割する
・VER1のモデルやファイルは変更しない
============================================================
"""

import json
import os
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd

from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# 基本設定
# ============================================================

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parents[2]


CSV_AI = BASE / "csv" / "ai"

INPUT_CSV = CSV_AI / "training_race_features.csv"

MODEL_DIR = BASE / "model" / "train_model_VER2"

MODEL_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# オッズ特徴量20列
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
# 入力に使用しない列
# ============================================================

DROP_COLUMNS = {
    "race_key",
    "date",
    "payout_class",

    # 確定結果・払戻関連
    "player_id_result",
    "finish_order",
    "result_status",
    "result_reason",
    "trifecta_1st",
    "trifecta_2nd",
    "trifecta_3rd",
    "trifecta_payout",
    "popularity",
}


# ============================================================
# ログ
# ============================================================

def log(message):
    print(f"[001_build_odds_model] {message}")


# ============================================================
# CSV読込
# ============================================================

def load_data():
    log("=" * 60)
    log("学習データ読込")
    log("=" * 60)

    if not INPUT_CSV.exists():
        raise FileNotFoundError(
            f"学習CSVがありません: {INPUT_CSV}"
        )

    df = pd.read_csv(
        INPUT_CSV,
        encoding="utf-8-sig",
        low_memory=False,
    )

    log(f"入力ファイル: {INPUT_CSV}")
    log(f"行数: {len(df):,}")
    log(f"列数: {len(df.columns):,}")

    required = ["date"] + ODDS_FEATURE_COLUMNS

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            "必要な列がありません。\n"
            f"{missing}"
        )

    # 日付を統一
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    invalid_dates = df["date"].isna().sum()

    if invalid_dates:
        log(f"日付を解釈できない行: {invalid_dates:,}")
        df = df.loc[df["date"].notna()].copy()

    if df.empty:
        raise ValueError("有効な日付を持つデータがありません。")

    log(f"有効データ行数: {len(df):,}")
    log(
        "対象期間: "
        f"{df['date'].min().date()} ～ "
        f"{df['date'].max().date()}"
    )

    return df


# ============================================================
# 学習用入力列の作成
# ============================================================


def build_features(df):
    log("=" * 60)
    log("入力特徴量の作成")
    log("=" * 60)

    excluded = DROP_COLUMNS | set(ODDS_FEATURE_COLUMNS)

    feature_columns = [
        col for col in df.columns
        if col not in excluded
    ]

    if not feature_columns:
        raise ValueError("入力に使用できる特徴量がありません。")

    X = df[feature_columns].copy()

    categorical_columns = []

    for col in X.columns:
        # 文字列型の列をカテゴリ型に変換
        if (
            pd.api.types.is_object_dtype(X[col])
            or pd.api.types.is_string_dtype(X[col])
            or isinstance(X[col].dtype, pd.CategoricalDtype)
        ):
            X[col] = (
                X[col]
                .fillna("__MISSING__")
                .astype(str)
                .astype("category")
            )

            categorical_columns.append(col)

    # 数値列の無限大を欠損値に変換
    numeric_columns = X.select_dtypes(
        include=["number"]
    ).columns

    X[numeric_columns] = X[numeric_columns].replace(
        [np.inf, -np.inf],
        np.nan,
    )

    log(f"入力特徴量数: {len(feature_columns):,}")
    log(f"カテゴリ列数: {len(categorical_columns):,}")
    log("オッズ特徴量20列は入力から除外済み")
    log("payout_class・確定結果列も入力から除外")

    if categorical_columns:
        log("カテゴリ列の例: " + ", ".join(categorical_columns[:10]))

    return X, feature_columns, categorical_columns



# ============================================================
# 日付で学習用・検証用に分割
# ============================================================

def split_by_date(df):
    log("=" * 60)
    log("日付によるデータ分割")
    log("=" * 60)

    unique_dates = np.array(
        sorted(df["date"].dt.normalize().unique())
    )

    if len(unique_dates) < 2:
        raise ValueError(
            "日付が2日分以上ないため、"
            "日付による学習・検証分割ができません。"
        )

    # 新しい日付の約20%を検証用にする
    split_index = int(len(unique_dates) * 0.8)
    split_index = max(1, min(split_index, len(unique_dates) - 1))

    cutoff_date = pd.Timestamp(unique_dates[split_index])

    train_mask = df["date"].dt.normalize() < cutoff_date
    valid_mask = ~train_mask

    train_df = df.loc[train_mask].copy()
    valid_df = df.loc[valid_mask].copy()

    if train_df.empty or valid_df.empty:
        raise ValueError("学習用または検証用データが空です。")

    log(f"学習用行数: {len(train_df):,}")
    log(f"検証用行数: {len(valid_df):,}")
    log(f"学習期間終了: {train_df['date'].max().date()}")
    log(f"検証期間開始: {valid_df['date'].min().date()}")

    return train_df, valid_df


# ============================================================
# 1特徴量分の回帰モデルを学習
# ============================================================

def train_one_model(
    feature_name,
    X_train,
    X_valid,
    y_train,
    y_valid,
    categorical_columns,
):
    # 欠損値を持つ教師データは対象外
    train_mask = y_train.notna() & np.isfinite(y_train)
    valid_mask = y_valid.notna() & np.isfinite(y_valid)

    X_tr = X_train.loc[train_mask]
    y_tr = y_train.loc[train_mask].astype(float)

    X_va = X_valid.loc[valid_mask]
    y_va = y_valid.loc[valid_mask].astype(float)

    if len(X_tr) < 100:
        log(f"[スキップ] {feature_name}: 学習データが少なすぎます")
        return None

    if len(X_va) == 0:
        log(f"[スキップ] {feature_name}: 検証データがありません")
        return None

    # オッズ特徴量は0以上を想定。
    # log1p変換により、大きな値の影響を抑える。
    if (y_tr < 0).any() or (y_va < 0).any():
        raise ValueError(
            f"{feature_name} に負の値があります。"
            "特徴量の定義を確認してください。"
        )

    y_tr_log = np.log1p(y_tr)
    y_va_log = np.log1p(y_va)

    model = lgb.LGBMRegressor(
        objective="regression",
        n_estimators=500,
        learning_rate=0.03,
        num_leaves=31,
        random_state=42,
        n_jobs=-1,
        verbosity=-1,
    )

    model.fit(
        X_tr,
        y_tr_log,
        categorical_feature=categorical_columns,
        eval_set=[(X_va, y_va_log)],
        callbacks=[
            lgb.early_stopping(
                stopping_rounds=50,
                verbose=False,
            ),
            lgb.log_evaluation(period=0),
        ],
    )

    # 予測値を元の尺度に戻す
    pred_log = model.predict(X_va)
    pred = np.maximum(np.expm1(pred_log), 0)

    mae = mean_absolute_error(y_va, pred)
    rmse = np.sqrt(mean_squared_error(y_va, pred))

    log(
        f"{feature_name}: "
        f"MAE={mae:.4f}, RMSE={rmse:.4f}, "
        f"学習件数={len(X_tr):,}, 検証件数={len(X_va):,}"
    )

    return {
        "model": model,
        "mae": float(mae),
        "rmse": float(rmse),
        "train_rows": int(len(X_tr)),
        "valid_rows": int(len(X_va)),
    }


# ============================================================
# 全20モデルの学習・保存
# ============================================================

def train_all_models(df):
    X, feature_columns, categorical_columns = build_features(df)

    train_df, valid_df = split_by_date(df)

    X_train = X.loc[train_df.index].copy()
    X_valid = X.loc[valid_df.index].copy()

    results = []
    saved_models = []

    log("=" * 60)
    log("オッズ特徴量20モデルの学習開始")
    log("=" * 60)

    for index, target in enumerate(
        ODDS_FEATURE_COLUMNS,
        start=1,
    ):
        print()
        log(f"[{index}/20] 学習対象: {target}")

        y_train = pd.to_numeric(
            train_df[target],
            errors="coerce",
        )

        y_valid = pd.to_numeric(
            valid_df[target],
            errors="coerce",
        )

        result = train_one_model(
            target,
            X_train,
            X_valid,
            y_train,
            y_valid,
            categorical_columns,
        )

        if result is None:
            continue

        model_file = MODEL_DIR / f"{target}.pkl"

        joblib.dump(
            result["model"],
            model_file,
        )

        saved_models.append(target)

        results.append({
            "target": target,
            "mae": result["mae"],
            "rmse": result["rmse"],
            "train_rows": result["train_rows"],
            "valid_rows": result["valid_rows"],
            "best_iteration": getattr(
                result["model"],
                "best_iteration_",
                None,
            ),
            "model_file": model_file.name,
        })

        log(f"モデル保存: {model_file}")

    if not results:
        raise RuntimeError(
            "学習できたモデルがありません。"
            "データと特徴量を確認してください。"
        )

    # 予測時に必要な情報を保存
    metadata = {
        "feature_columns": feature_columns,
        "categorical_columns": categorical_columns,
        "target_columns": saved_models,
        "target_transform": "log1p",
        "prediction_inverse_transform": "expm1",
        "date_split": "chronological 80/20 by unique date",
    }

    metadata_file = MODEL_DIR / "odds_model_metadata.json"

    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(
            metadata,
            f,
            ensure_ascii=False,
            indent=4,
        )

    metrics_df = pd.DataFrame(results)

    metrics_file = MODEL_DIR / "odds_model_metrics.csv"

    metrics_df.to_csv(
        metrics_file,
        index=False,
        encoding="utf-8-sig",
    )

    log("=" * 60)
    log("オッズ特徴量AIの学習完了")
    log(f"学習成功モデル数: {len(saved_models)}/20")
    log(f"メタデータ: {metadata_file}")
    log(f"評価結果: {metrics_file}")
    log("=" * 60)

    print()
    print(metrics_df.to_string(index=False))


# ============================================================
# Main
# ============================================================

def main():
    print()

    log("=" * 60)
    log("競輪AI VER2 - 001 オッズ特徴量AI学習")
    log("=" * 60)

    df = load_data()

    train_all_models(df)

    log("処理完了")


if __name__ == "__main__":
    main()
