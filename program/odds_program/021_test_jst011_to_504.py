import json
import urllib.request
import urllib.parse
import time
from itertools import permutations


PRE_RACE_FILE = (
    r"C:\競輪AI\data_official\historical"
    r"\pre_race\20200101_pre_race.json"
)

KAIKEI = "6"
MODE = "0"
TYPE = "JST011"


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
# 車立数から3連単組み合わせを作る
# ============================================================

def make_trifecta_keys(car_count):

    keys = []

    for a, b, c in permutations(range(1, car_count + 1), 3):

        key = f"OZZ{a}{b}{c}"

        keys.append(key)

    return keys


# ============================================================
# OZZ → 3連単データ変換
# ============================================================

def convert_ozz(odds_data):

    converted = {}

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

        first = int(number[0])
        second = int(number[1])
        third = int(number[2])

        trifecta = f"{first}-{second}-{third}"

        converted[trifecta] = value

    return converted


# ============================================================
# メイン
# ============================================================

print("=" * 70)
print("JST011 → 3連単504形式 変換検証")
print("=" * 70)

print()
print("PRE_RACE:")
print(PRE_RACE_FILE)

with open(PRE_RACE_FILE, "r", encoding="utf-8") as f:
    pre_race = json.load(f)


total_races = 0
success_races = 0
failed_races = 0

conversion_errors = 0

count_5 = 0
count_6 = 0
count_7 = 0
count_8 = 0
count_9 = 0

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

        total_races += 1

        race_no = index + 1

        enc_para_r = race.get("encParaR")

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
        # OZZを変換
        # ----------------------------------------------------

        converted = convert_ozz(odds_data)

        ozz_count = len(converted)


        # ----------------------------------------------------
        # 車立数判定
        # ----------------------------------------------------

        if ozz_count == 504:

            car_count = 9
            count_9 += 1

        elif ozz_count == 336:

            car_count = 8
            count_8 += 1

        elif ozz_count == 210:

            car_count = 7
            count_7 += 1

        elif ozz_count == 120:

            car_count = 6
            count_6 += 1

        elif ozz_count == 60:

            car_count = 5
            count_5 += 1

        else:

            car_count = 0


        # ----------------------------------------------------
        # 期待される組み合わせと比較
        # ----------------------------------------------------

        if car_count:

            expected_keys = make_trifecta_keys(car_count)

            expected_set = set(
                key.replace("OZZ", "").replace("", "")
                for key in expected_keys
            )

            actual_set = set(converted.keys())

            # 形式を 1-2-3 に統一して比較
            expected_trifecta = set(
                f"{k[0]}-{k[1]}-{k[2]}"
                for k in [
                    key[3:]
                    for key in expected_keys
                ]
            )

            missing = expected_trifecta - actual_set
            unexpected = actual_set - expected_trifecta

        else:

            missing = set()
            unexpected = set()


        # ----------------------------------------------------
        # 結果
        # ----------------------------------------------------

        if not missing and not unexpected:

            success_races += 1

            print(
                f"成功 / "
                f"OZZ={len(odds_data)} / "
                f"変換={ozz_count} / "
                f"{car_count}車"
            )

        else:

            conversion_errors += 1

            print(
                f"変換異常 / "
                f"OZZ={len(odds_data)} / "
                f"変換={ozz_count} / "
                f"missing={len(missing)} / "
                f"unexpected={len(unexpected)}"
            )


elapsed = time.time() - start_time


# ============================================================
# 最終結果
# ============================================================

print()
print()
print("=" * 70)
print("最終結果")
print("=" * 70)

print(f"総レース数       : {total_races}")
print(f"取得・変換成功   : {success_races}")
print(f"取得失敗         : {failed_races}")
print(f"変換異常         : {conversion_errors}")

print()
print("車立数")
print("-" * 70)

print(f"9車 : {count_9}")
print(f"8車 : {count_8}")
print(f"7車 : {count_7}")
print(f"6車 : {count_6}")
print(f"5車 : {count_5}")

print()
print(f"処理時間         : {elapsed:.2f} 秒")

print()
print("=" * 70)

if (
    failed_races == 0
    and conversion_errors == 0
):
    print("★ 全レースのOZZ → 3連単変換に成功")
else:
    print("★ 一部に問題あり")

print("=" * 70)