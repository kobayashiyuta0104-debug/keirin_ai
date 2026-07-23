import csv
import json

from pathlib import Path

JO_NAME = {
    "11": "函館",
    "12": "青森",
    "13": "いわき平",
    "21": "弥彦",
    "22": "前橋",
    "23": "取手",
    "24": "宇都宮",
    "25": "大宮",
    "26": "西武園",
    "27": "京王閣",
    "28": "立川",
    "31": "松戸",
    "34": "川崎",
    "35": "平塚",
    "36": "小田原",
    "37": "伊東",
    "38": "静岡",
    "42": "名古屋",
    "43": "岐阜",
    "44": "大垣",
    "45": "豊橋",
    "46": "富山",
    "47": "松阪",
    "48": "四日市",
    "51": "福井",
    "53": "奈良",
    "54": "向日町",
    "55": "和歌山",
    "56": "岸和田",
    "61": "玉野",
    "62": "広島",
    "63": "防府",
    "71": "高松",
    "73": "小松島",
    "74": "高知",
    "75": "松山",
    "81": "小倉",
    "83": "久留米",
    "84": "武雄",
    "85": "佐世保",
    "86": "別府",
    "87": "熊本"
}

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
    "historical" /
    "lines"
)

OUTPUT_DIR = (
    BASE /
    "csv" /
    "historical_lines"
)

OUTPUT_CSV = (
    OUTPUT_DIR /
    "historical_lines.csv"
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

            print("BEFORE :", race["race_key"])

            old_race_key = race["race_key"]

            date = data["target_date"]

            parts = old_race_key.split("_")

            if len(parts) != 3:
                raise ValueError(f"Invalid race_key: {old_race_key}")

            jo_code = parts[1]

            race_no = int(parts[2])

            jo_name = JO_NAME.get(jo_code, jo_code)

            if jo_name is None:
                raise ValueError(f"Unknown jo_code: {jo_code}")

            race_key = f"{date}_{jo_name}_{race_no}R"

            print("AFTER  :", race_key)

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