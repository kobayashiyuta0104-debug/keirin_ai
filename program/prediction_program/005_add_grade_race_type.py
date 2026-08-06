"""
===========================================================
競輪AI Ver1.0

005_add_grade_race_type.py

【役割】

20260731～20260805 prediction.csv

　＋

race_data.json

↓

グレード
レース種別

追加

===========================================================
"""

import json
from pathlib import Path

import pandas as pd


# ===========================================================
# パス
# ===========================================================

BASE = Path(r"C:\競輪AI")

PREDICTION_DIR = (
    BASE
    / "csv"
    / "prediction"
)

DAILY_DIR = (
    BASE
    / "data_official"
    / "daily"
    / "race_data"
)


# ===========================================================
# 対象日
# ===========================================================

DATES = [

    "20260731",
    "20260801",
    "20260802",
    "20260803",
    "20260804",
    "20260805",

]


# ===========================================================
# メイン処理
# ===========================================================

for target_date in DATES:

    prediction_file = (
        PREDICTION_DIR
        / f"{target_date}_prediction.csv"
    )

    json_file = (
        DAILY_DIR
        / f"{target_date}_race_data.json"
    )

    if not prediction_file.exists():

        print(f"Predictionなし : {target_date}")

        continue

    if not json_file.exists():

        print(f"JSONなし : {target_date}")

        continue

    print(f"処理中 : {target_date}")

    # -------------------------------------------------------
    # Prediction
    # -------------------------------------------------------

    prediction = pd.read_csv(

        prediction_file,

        encoding="utf-8-sig",

        low_memory=False,

    )

    # -------------------------------------------------------
    # JSON
    # -------------------------------------------------------

    with open(

        json_file,

        "r",

        encoding="utf-8",

    ) as f:

        race_json = json.load(f)

    race_dict = {}

    for race in race_json["races"]:

        race_dict[

            race["race_key"]

        ] = {

            "グレード": race["グレード"],

            "レース種別": race["レース種別"],

        }

    # -------------------------------------------------------
    # グレード・レース種別追加
    # -------------------------------------------------------

    prediction["グレード"] = ""

    prediction["レース種別"] = ""

    for i in prediction.index:

        race_key = prediction.loc[

            i,

            "レースキー",

        ]

        if race_key not in race_dict:

            continue

        prediction.loc[

            i,

            "グレード",

        ] = race_dict[race_key]["グレード"]

        prediction.loc[

            i,

            "レース種別",

        ] = race_dict[race_key]["レース種別"]

    # -------------------------------------------------------
    # 列順を統一
    # -------------------------------------------------------

    NEW_COLUMNS = [

        "レースキー",
        "日付",
        "グレード",
        "競輪場",
        "レース\n番号",
        "レース種別",
        "発走\n時刻",
        "開催区分",

        "AI予想",
        "AI確信度",

        "0～\n9,999",
        "10,000～\n29,999",
        "30,000～\n49,999",
        "50,000～\n99,999",
        "100,000\n以上",

        "三連単\n払戻",
        "実際\nクラス",
        "的中\n判定",
        "方向性\n判定",

        "1号車\n期待度",
        "2号車\n期待度",
        "3号車\n期待度",
        "4号車\n期待度",
        "5号車\n期待度",
        "6号車\n期待度",
        "7号車\n期待度",
        "8号車\n期待度",
        "9号車\n期待度",

        "１着",
        "２着",
        "３着",

        "予想日時",
        "AIバージョン",
        "AIコメント",

    ]

    prediction = prediction[NEW_COLUMNS]

    # -------------------------------------------------------
    # 保存
    # -------------------------------------------------------

    prediction.to_csv(

        prediction_file,

        index=False,

        encoding="utf-8-sig",

    )

    print(

        f"完了 : {target_date}"

    )

print()

print("=======================================")

print("すべて完了")

print("=======================================")