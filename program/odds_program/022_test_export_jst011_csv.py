import json
import csv
import urllib.request
import urllib.parse
import time
from itertools import permutations
from pathlib import Path


# ============================================================
# 設定
# ============================================================

PRE_RACE_FILE = (
    r"C:\競輪AI\data_official\historical"
    r"\pre_race\20220801_pre_race.json"
)

OUTPUT_FILE = (
    r"C:\競輪AI\csv\historical_date"
    r"\historical_odds"
    r"\20220801_jst011_test.csv"
)

KAIKEI = "6"
MODE = "0"
TYPE = "JST011"


# ============================================================
# CSVヘッダー
# 先頭5列 + 3連単504列
# ============================================================

BASE_HEADERS = [
    "race_key",
    "date",
    "jo_code",
    "jo_name",
    "race_no",
]

TRIFECTA_HEADERS = [
    f"{a}-{b}-{c}"
    for a, b, c in permutations(range(1, 10), 3)
]

HEADERS = BASE_HEADERS + TRIFECTA_HEADERS


# ============================================================
# JST011取得
# ============================================================

def get_jst011(encp):

    params = {
        "kake": KAIKEI,
        "mode": MODE,
        "encp": encp,
        "type": TYPE,
    }

    query = urllib.parse.urlencode(params)

    url = "https://www.keirin.jp/pc/json?" + query

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/142.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.keirin.jp/pc/racelive",
            "Accept": (
                "application/json, "
                "text/javascript, */*; q=0.01"
            ),
            "X-Requested-With": "XMLHttpRequest",
        },
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read()

    data = json.loads(raw.decode("utf-8"))

    if data.get("resultCd") != 0:
        return None

    root_data = data.get("data", {})

    return root_data.get("ozz3RentanData", {})


# ============================================================
# OZZ → 3連単列
# ============================================================

def convert_ozz_to_trifecta(odds_data):

    result = {}

    for key, value in odds_data.items():

        if not isinstance(key, str):
            continue

        if not key.startswith("OZZ"):
            continue

        if len(key) != 6:
            continue

        number = key[3:]

        if not number.isdigit():
            continue

        trifecta = (
            f"{number[0]}-"
            f"{number[1]}-"
            f"{number[2]}"
        )

        result[trifecta] = value

    return result


# ============================================================
# race_key
# ============================================================

def make_race_key(date, venue, race_no):

    return (
        f"{date}_"
        f"{venue}_"
        f"{int(race_no)}R"
    )


# ============================================================
# メイン
# ============================================================

print("=" * 70)
print("JST011 → 509列CSV テスト出力")
print("=" * 70)

print()
print("PRE_RACE:")
print(PRE_RACE_FILE)

print()
print("OUTPUT:")
print(OUTPUT_FILE)

print()
print(f"CSV列数: {len(HEADERS)}")
print(f"基本列: {len(BASE_HEADERS)}")
print(f"3連単列: {len(TRIFECTA_HEADERS)}")


# ------------------------------------------------------------
# PRE_RACE読み込み
# ------------------------------------------------------------

with open(PRE_RACE_FILE, "r", encoding="utf-8") as f:
    pre_race = json.load(f)


target_date = pre_race.get("target_date")

print()
print(f"対象日: {target_date}")


# ------------------------------------------------------------
# 出力先
# ------------------------------------------------------------

output_path = Path(OUTPUT_FILE)
output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ------------------------------------------------------------
# CSV作成
# ------------------------------------------------------------

rows = []

total_races = 0
success_races = 0
failed_races = 0

start_time = time.time()


for venue_data in pre_race.get("venues", []):

    venue = venue_data.get("venue")
    bank_code = venue_data.get("bank_code")

    jsj001 = venue_data.get("jsj001", {})
    c0201data = jsj001.get("C0201data", {})
    c0201race = c0201data.get("C0201race", [])

    print()
    print("-" * 70)
    print(f"{venue}  bank_code={bank_code}")
    print(f"race count: {len(c0201race)}")
    print("-" * 70)


    for index, race in enumerate(c0201race):

        race_no = index + 1
        enc_para_r = race.get("encParaR")

        total_races += 1

        print(
            f"{total_races:3d} "
            f"{venue} {race_no}R : ",
            end="",
            flush=True,
        )

        if not enc_para_r:

            failed_races += 1

            print("encParaRなし")

            continue


        try:

            odds_data = get_jst011(enc_para_r)

        except Exception as e:

            failed_races += 1

            print(f"取得エラー: {e}")

            continue


        if not odds_data:

            failed_races += 1

            print("OZZデータなし")

            continue


        # ----------------------------------------------------
        # OZZ → 3連単
        # ----------------------------------------------------

        trifecta_data = convert_ozz_to_trifecta(
            odds_data
        )


        # ----------------------------------------------------
        # 509列を作成
        # ----------------------------------------------------

        row = {
            header: ""
            for header in HEADERS
        }


        # 基本情報

        row["race_key"] = make_race_key(
            target_date,
            venue,
            race_no
        )

        row["date"] = target_date

        row["jo_code"] = bank_code

        row["jo_name"] = venue

        row["race_no"] = race_no


        # 3連単オッズ

        for trifecta, odds in trifecta_data.items():

            if trifecta in row:

                row[trifecta] = odds


        rows.append(row)

        success_races += 1

        print(
            f"成功 / "
            f"OZZ={len(odds_data)} / "
            f"3連単={len(trifecta_data)}"
        )


# ============================================================
# CSV保存
# ============================================================

with open(
    output_path,
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=HEADERS
    )

    writer.writeheader()

    writer.writerows(rows)


elapsed = time.time() - start_time


# ============================================================
# 保存後チェック
# ============================================================

print()
print()
print("=" * 70)
print("最終結果")
print("=" * 70)

print(f"総レース数       : {total_races}")
print(f"取得成功         : {success_races}")
print(f"取得失敗         : {failed_races}")

if total_races:
    print(
        f"成功率           : "
        f"{success_races / total_races * 100:.2f}%"
    )

print(f"CSV行数          : {len(rows)}")
print(f"CSV列数          : {len(HEADERS)}")
print(f"処理時間         : {elapsed:.2f} 秒")

print()
print("保存先:")
print(output_path)

print()
print("=" * 70)

if (
    total_races == success_races
    and len(HEADERS) == 509
):
    print("★ JST011 → 509列CSV テスト成功")
else:
    print("★ 一部に問題あり")

print("=" * 70)