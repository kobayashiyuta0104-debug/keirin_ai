import os
from pathlib import Path
from datetime import datetime

import pandas as pd


BASE = Path(r"C:\競輪AI")

PREDICTION_DIR = BASE / "csv" / "prediction"


TARGET_FILES = [

    "20260731_prediction.csv",
    "20260801_prediction.csv",
    "20260802_prediction.csv",
    "20260803_prediction.csv",
    "20260804_prediction.csv",
    "20260805_prediction.csv",

]


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


for file_name in TARGET_FILES:

    path = PREDICTION_DIR / file_name

    print(f"変換中 : {file_name}")

    df = pd.read_csv(

        path,

        encoding="utf-8-sig",

    )

    df.columns = df.columns.str.replace("\r\n", "\n", regex=False)

    df["レース\n番号"] = (

        df["レース\n番号"]

        .astype(str)

    )


    df["レース\n番号"] = df["レース\n番号"].str.replace("R", "", regex=False) + "R"

    df["レースキー"] = (

        df["日付"]

        .str.replace("-", "")

        + "_"

        + df["競輪場"]

        + "_"

        + df["レース\n番号"]

    )


    # ----------------------------------------
    # 空欄列追加
    # ----------------------------------------

    df["三連単\n払戻"] = ""
    df["実際\nクラス"] = ""
    df["的中\n判定"] = ""
    df["方向性\n判定"] = ""

    for i in range(1, 10):

        df[f"{i}号車\n期待度"] = ""

    df["１着"] = ""
    df["２着"] = ""
    df["３着"] = ""

    df["予想日時"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df["AIバージョン"] = "Ver1.0"
    df["AIコメント"] = ""

    # ----------------------------------------
    # 列順変更
    # ----------------------------------------

    if "グレード" not in df.columns:
        df["グレード"] = ""

    if "レース種別" not in df.columns:
        df["レース種別"] = ""

    df = df[NEW_COLUMNS]

    # ----------------------------------------
    # 保存
    # ----------------------------------------

    df.to_csv(

        path,

        index=False,

        encoding="utf-8-sig",

    )

    print("OK")

print()
print("===================================")
print("Prediction Header Fix Complete")
print("===================================")