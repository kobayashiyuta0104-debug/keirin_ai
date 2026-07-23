import csv
import json

from pathlib import Path

JO_NAME = {
    "11": "函館",
    "12": "青森",
    "13": "いわき平",
    "14": "弥彦",
    "15": "前橋",
    "16": "取手",
    "17": "宇都宮",
    "18": "大宮",
    "19": "西武園",
    "20": "京王閣",
    "21": "立川",
    "22": "松戸",
    "23": "川崎",
    "24": "平塚",
    "25": "小田原",
    "26": "伊東",
    "27": "静岡",
    "28": "名古屋",
    "29": "岐阜",
    "30": "大垣",
    "31": "豊橋",
    "32": "富山",
    "33": "松阪",
    "34": "四日市",
    "35": "福井",
    "36": "奈良",
    "37": "向日町",
    "38": "和歌山",
    "39": "岸和田",
    "40": "玉野",
    "41": "広島",
    "42": "防府",
    "43": "高松",
    "44": "小松島",
    "45": "高知",
    "46": "松山",
    "47": "小倉",
    "48": "久留米",
    "49": "武雄",
    "50": "佐世保",
    "51": "別府",
    "52": "熊本"
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

# ==========================================================
# 開始
# ==========================================================

for index, json_file in enumerate(json_files, start=1):

    target_date = json_file.stem.replace("_lines", "")

    output_csv = (
        OUTPUT_DIR /
        f"{target_date}_lines.csv"
    )

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

        rows = []

        for race in data["races"]:

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

        total_rows += len(rows)

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
print("016 Complete")
print("=" * 70)

print(f"JSON   : {len(json_files)}")
print(f"SAVED  : {saved}")
print(f"ERROR  : {error}")
print(f"OUTPUT : {OUTPUT_DIR}")
print(f"TOTAL ROWS : {total_rows}")

print()
print("Finished.")