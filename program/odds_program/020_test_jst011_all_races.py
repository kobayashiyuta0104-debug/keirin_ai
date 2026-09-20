import json
import urllib.request
import urllib.parse
import time


PRE_RACE_FILE = (
    r"C:\競輪AI\data_official\historical"
    r"\pre_race\20200101_pre_race.json"
)

KAIKEI = "6"
MODE = "0"
TYPE = "JST011"


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
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read()

        data = json.loads(raw.decode("utf-8"))

        if data.get("resultCd") != 0:
            return False, 0, data.get("messageCd")

        root_data = data.get("data", {})

        odds = root_data.get("ozz3RentanData", {})

        valid_count = sum(
            1
            for key in odds
            if (
                isinstance(key, str)
                and key.startswith("OZZ")
                and len(key) == 6
                and key[3:].isdigit()
            )
        )

        return True, valid_count, None

    except Exception as e:
        return False, 0, str(e)


# ============================================================
# メイン
# ============================================================

print("=" * 70)
print("KEIRIN.JP JST011 全レース取得検証")
print("=" * 70)

print()
print("PRE_RACE:")
print(PRE_RACE_FILE)

print()

with open(PRE_RACE_FILE, "r", encoding="utf-8") as f:
    pre_race = json.load(f)


total_races = 0
success_races = 0
failed_races = 0

car_counts = {}
car_success = {}
car_failed = {}

results = []

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

    for race in c0201race:

        race_no = race.get("raceNo")
        enc_para_r = race.get("encParaR")

        if not enc_para_r:
            print(f"{venue} {race_no}R : encParaRなし → SKIP")
            continue

        total_races += 1

        print(
            f"{total_races:3d} "
            f"{venue} {race_no}R : ",
            end="",
            flush=True,
        )

        ok, odds_count, error = get_jst011(enc_para_r)

        # 車立数を推定
        # JST011のOZZ数から判定
        if odds_count == 504:
            car_count = 9
        elif odds_count == 336:
            car_count = 8
        elif odds_count == 210:
            car_count = 7
        elif odds_count == 120:
            car_count = 6
        elif odds_count == 60:
            car_count = 5
        else:
            car_count = 0

        if car_count:
            car_counts[car_count] = car_counts.get(car_count, 0) + 1

        if ok and odds_count > 0:

            success_races += 1

            if car_count:
                car_success[car_count] = (
                    car_success.get(car_count, 0) + 1
                )

            print(f"成功 / OZZ={odds_count}")

        else:

            failed_races += 1

            if car_count:
                car_failed[car_count] = (
                    car_failed.get(car_count, 0) + 1
                )

            print(
                f"失敗 / OZZ={odds_count} / "
                f"error={error}"
            )

        results.append({
            "venue": venue,
            "bank_code": bank_code,
            "race_no": race_no,
            "encParaR": enc_para_r,
            "ok": ok,
            "odds_count": odds_count,
            "error": error,
        })


elapsed = time.time() - start_time


# ============================================================
# 結果
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
    rate = success_races / total_races * 100
    print(f"成功率           : {rate:.2f}%")

print(f"処理時間         : {elapsed:.2f} 秒")

print()
print("車立数別")
print("-" * 70)

for car_count in sorted(car_counts):
    total = car_counts[car_count]
    success = car_success.get(car_count, 0)
    failed = car_failed.get(car_count, 0)

    print(
        f"{car_count}車 : "
        f"総数={total} / "
        f"成功={success} / "
        f"失敗={failed}"
    )

print()
print("失敗レース")
print("-" * 70)

failed_results = [
    r for r in results
    if not r["ok"] or r["odds_count"] == 0
]

if not failed_results:
    print("なし")
else:
    for r in failed_results:
        print(
            f"{r['venue']} {r['race_no']}R : "
            f"OZZ={r['odds_count']} / "
            f"{r['error']}"
        )

print()
print("=" * 70)
print("検証終了")
print("=" * 70)