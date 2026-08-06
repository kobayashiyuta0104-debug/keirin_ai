import pandas as pd
from pathlib import Path

BASE = Path(r"C:\競輪AI")

PREDICTION_DIR = BASE / "csv" / "prediction"
RESULT_DIR = BASE / "csv" / "result"

TARGET_DATES = [

    "20260731",

    "20260801",

    "20260802",

    "20260803",

    "20260804",

    "20260805",

]


def get_result_class(payout):

    if payout <= 9999:

        return "0～9,999円"

    elif payout <= 29999:

        return "10,000～29,999円"

    elif payout <= 49999:

        return "30,000～49,999円"

    elif payout <= 99999:

        return "50,000～99,999円"

    else:

        return "100,000円以上"


def update_prediction(prediction_file, result_file):

    prediction_df = pd.read_csv(

        prediction_file,

        encoding="utf-8-sig",

        low_memory=False,

    )

    result_df = pd.read_csv(

        result_file,

        encoding="utf-8-sig",

        low_memory=False,

    )

    TEXT_COLUMNS = [

        "三連単\n払戻",

        "実際\nクラス",

        "的中\n判定",

        "１着",

        "２着",

        "３着",

    ]

    for col in TEXT_COLUMNS:

        prediction_df[col] = prediction_df[col].astype(object)

    ORDER_COLUMNS = {

        1: "１着",

        2: "２着",

        3: "３着",

    }

    for race_key in prediction_df["レースキー"].unique():

        race_result = result_df[

            result_df["race_key"] == race_key

        ]

        if race_result.empty:

            continue

        payout = int(

            str(

                race_result["trifecta_payout"].iloc[0]

            ).replace(",", "")

        )

        prediction_df.loc[

            prediction_df["レースキー"] == race_key,

            "三連単\n払戻"

        ] = payout

        result_class = get_result_class(

            payout

        )

        prediction_df.loc[

            prediction_df["レースキー"] == race_key,

            "実際\nクラス"

        ] = result_class

        ai_class = str(

            prediction_df.loc[

                prediction_df["レースキー"] == race_key,

                "AI予想",

            ].iloc[0]

        )

        prediction_df.loc[

            prediction_df["レースキー"] == race_key,

            "的中\n判定"

        ] = (

            "○"

            if ai_class == result_class

            else "×"

        )

        for order in [1, 2, 3]:

            row = race_result[

                race_result["finish_order"] == order

            ]

            if row.empty:

                continue

            prediction_df.loc[

                prediction_df["レースキー"] == race_key,

                ORDER_COLUMNS[order]

            ] = int(

                row["car_no"].iloc[0]

            )

    prediction_df.to_csv(

        prediction_file,

        index=False,

        encoding="utf-8-sig",

    )

    print(f"OK : {prediction_file.name}")


for target_date in TARGET_DATES:

    prediction_file = (

        PREDICTION_DIR

        / f"{target_date}_prediction.csv"

    )

    result_file = (

        RESULT_DIR

        / f"{target_date}_result.csv"

    )

    if not prediction_file.exists():

        print(f"SKIP : {prediction_file.name}")

        continue

    if not result_file.exists():

        print(f"SKIP : {result_file.name}")

        continue

    update_prediction(

        prediction_file,

        result_file,

    )

print()
print("===================================")
print("Prediction Result Update Complete")
print("===================================")