import csv
import json

from pathlib import Path

# ==========================================================
# 016_export_historical_lines_csv.py
#
# Historical Lines JSON
#         ↓
# Historical Lines CSV
# ==========================================================
BASE = Path(r"C:\競輪AI")

INPUT_DIR = (
    BASE /
    "data_official" /
    "daily" /
    "lines"
)

OUTPUT_DIR = (
    BASE /
    "csv" /
    "historical_date"/
    "historical_lines" 
)

OUTPUT_CSV = (
    OUTPUT_DIR /
    "20261027_lines.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ==========================================================
# JSON一覧
# ==========================================================

TARGET_START = "20261027"
TARGET_END   = "20261027"

json_files = sorted(
    json_file
    for json_file in INPUT_DIR.glob("*_lines.json")
    if TARGET_START <= json_file.stem.replace("_lines", "") <= TARGET_END
)

print("=" * 70)
print("016 Historical Lines CSV Export")
print("=" * 70)
print()

print("HISTORICAL JSON :", len(json_files))
print()

saved = 0
error = 0
total_rows = 0

rows = []

# ==========================================================
# 開始
# ==========================================================

for index, json_file in enumerate(json_files, start=1):

    target_date = json_file.stem.replace("_lines", "")

    print()
    print("=" * 70)
    print(f"[{index}/{len(json_files)}] {target_date}")
    print("=" * 70)

    try:

        with open(
            json_file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        for race in data["races"]:

            
            race_key = race["race_key"]

            date = data["target_date"]

            # 新しい形式: YYYYMMDD_競輪場名_レース番号R
            parts = race_key.split("_")

            if len(parts) != 3:
                raise ValueError(f"Invalid race_key: {race_key}")

            jo_name = parts[1]

            race_no = int(parts[2].removesuffix("R"))

            jo_code = race.get("jo_code")

            print("RACE_KEY:", race_key)


            cars = race.get("cars")

            if not cars:
                continue

            for car_no, info in sorted(
                cars.items(),
                key=lambda x: int(x[0])
            ):

                rows.append({

                    "race_key": race_key,

                    "date": date,

                    "jo_code": jo_code,

                    "jo_name": jo_name,

                    "race_no": race_no,

                    "car_no": int(car_no),

                    "line_no": info.get("line"),

                    "line_position": info.get("position"),

                    "is_seri": info.get("seri")

                })

    except Exception as e:

        error += 1

        print(f"ERROR {json_file.name}")
        print(type(e).__name__)
        print(e)

# ==========================================================
# CSV保存
# ==========================================================

with open(
    OUTPUT_CSV,
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.DictWriter(

        f,

        fieldnames=[

            "race_key",
            "date",
            "jo_code",
            "jo_name",
            "race_no",
            "car_no",
            "line_no",
            "line_position",
            "is_seri"

        ]

    )

    writer.writeheader()

    writer.writerows(rows)

saved = 1
total_rows = len(rows)

print()
print(f"SAVE : {OUTPUT_CSV.name}")
print(f"ROWS : {total_rows}")

# ==========================================================
# 完了
# ==========================================================

print()
print("=" * 70)
print("016 Complete")
print("=" * 70)

print(f"JSON   : {len(json_files)}")
print(f"SAVED  : {saved}")
print(f"ERROR  : {error}")
print(f"OUTPUT : {OUTPUT_DIR}")
print(f"TOTAL ROWS : {total_rows}")

print()
print("Finished.")