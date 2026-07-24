import csv
import json

from pathlib import Path

# ==========================================================
# 013_export_daily_lines_csv.py
#
# Daily Lines JSON
#        ↓
# Daily Lines CSV
# ==========================================================

import os

if os.name == "nt":
    BASE = Path(r"C:\競輪AI")
else:
    BASE = Path(__file__).resolve().parent.parent

INPUT_DIR = (
    BASE /
    "data_official" /
    "daily" /
    "lines"
)

OUTPUT_DIR = (
    BASE /
    "csv" /
    "lines"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ==========================================================
# JSON一覧
# ==========================================================

json_files = sorted(
    INPUT_DIR.glob("*_lines.json")
)

if json_files:

    json_files = [json_files[-1]]

print("=" * 70)
print("013 Daily Lines CSV Export")
print("=" * 70)
print()

print("JSON :", len(json_files))
print()

saved = 0
error = 0

# ==========================================================
# 開始
# ==========================================================

for json_file in json_files:

    target_date = json_file.stem.replace("_lines", "")

    output_csv = (
        OUTPUT_DIR /
        f"{target_date}_lines.csv"
    )

    print()
    print("=" * 70)
    print(target_date)
    print("=" * 70)

    try:

        with open(
            json_file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        rows = []

        for race in data["races"]:

            race_key = race["race_key"]

            date = data["target_date"]

            jo_code = str(
                race["jo_code"]
            )

            jo_name = race["jo_name"]

            race_no = race["race_no"]

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

        with open(
            output_csv,
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

        saved += 1

        print(f"SAVE {output_csv.name}")
        print(f"ROWS {len(rows)}")

    except Exception as e:

        error += 1

        print(f"ERROR {json_file.name}")
        print(type(e).__name__)
        print(e)

# ==========================================================
# 完了
# ==========================================================

print()
print("=" * 70)
print("013 Complete")
print("=" * 70)

print(f"JSON   : {len(json_files)}")
print(f"SAVED  : {saved}")
print(f"ERROR  : {error}")
print(f"OUTPUT : {OUTPUT_DIR}")

print()
print("Finished.")