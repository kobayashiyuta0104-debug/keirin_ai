import json
import time
from pathlib import Path
from collections import Counter
import requests

BASE = Path(r"C:\競輪AI")
OUT = BASE / "239_historical_multi_date_raw_capture_fixed.json"

DATES = [
    "20260705",
    "20260706",
]

print("=== 239 複数過去日 全会場・全レース RAW自動取得 修正版 ===")

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.keirin.jp/pc/top",
})

def get_json(url, retry=3):
    last_error = None
    for attempt in range(1, retry + 1):
        try:
            r = session.get(url, timeout=30)
            r.raise_for_status()
            return r.json(), r.status_code, len(r.text)
        except Exception as e:
            last_error = repr(e)
            if attempt < retry:
                time.sleep(1)
    raise RuntimeError(last_error)

all_dates = []
problems = []
total_venues = 0
total_races = 0
complete = 0
date_venue_dist = Counter()
date_race_dist = Counter()
seen_race_keys = set()

for di, kday in enumerate(DATES, 1):
    print()
    print("=" * 80)
    print(f"[日付 {di}/{len(DATES)}] {kday}")

    url057 = f"https://www.keirin.jp/pc/json?kday={kday}&type=JSJ057"

    try:
        jsj057, status057, len057 = get_json(url057)
    except Exception as e:
        print("  ❌ JSJ057取得失敗:", repr(e))
        problems.append({
            "date": kday,
            "problem": "JSJ057_FETCH_ERROR",
            "error": repr(e),
        })
        continue

    kinfo = jsj057.get("kInfo") or []
    print("  JSJ057 HTTP:", status057)
    print("  開催会場数:", len(kinfo))

    total_venues += len(kinfo)
    date_venue_dist[kday] = len(kinfo)

    date_item = {
        "kday": kday,
        "jsj057": jsj057,
        "venues": [],
    }

    for vi, venue in enumerate(kinfo, 1):
        name = venue.get("jyoName")
        code = venue.get("KeirinCd")
        enc = venue.get("encPrm")

        print()
        print(f"  [会場 {vi}/{len(kinfo)}] {name} / code={code}")

        if not enc:
            print("    ❌ encPrmなし")
            problems.append({
                "date": kday,
                "venue": name,
                "problem": "ENC_PRM_MISSING",
            })
            continue

        # 212成功方式そのまま：encp
        url001 = f"https://www.keirin.jp/pc/json?encp={enc}&type=JSJ001"

        try:
            jsj001, status001, len001 = get_json(url001)
        except Exception as e:
            print("    ❌ JSJ001取得失敗:", repr(e))
            problems.append({
                "date": kday,
                "venue": name,
                "problem": "JSJ001_FETCH_ERROR",
                "error": repr(e),
            })
            continue

        # 212成功方式そのまま：C0201data配下
        c = jsj001.get("C0201data") if isinstance(jsj001, dict) else None
        races = c.get("C0201race") or [] if isinstance(c, dict) else []
        selected_date = c.get("selKaisai") if isinstance(c, dict) else None

        print("    JSJ001 HTTP:", status001)
        print("    selKaisai:", selected_date)
        print("    レース地図件数:", len(races))

        venue_item = {
            "jyoName": name,
            "KeirinCd": code,
            "encPrm": enc,
            "jsj001": jsj001,
            "races": [],
        }

        for ri, race in enumerate(races, 1):
            enc_r = race.get("encParaR") if isinstance(race, dict) else None

            if not enc_r:
                print(f"    [{ri}/{len(races)}] ❌ encParaRなし")
                problems.append({
                    "date": kday,
                    "venue": name,
                    "race_index": ri,
                    "problem": "ENC_PARA_R_MISSING",
                })
                continue

            race_no = ri
            race_key = f"{kday}_{name}_{race_no}R"

            if race_key in seen_race_keys:
                problems.append({
                    "race_key": race_key,
                    "problem": "DUPLICATE_RACE_KEY",
                })
            seen_race_keys.add(race_key)

            # 207/213系と同じencp方式
            url006 = f"https://www.keirin.jp/pc/json?encp={enc_r}&type=JSJ006"
            url012 = f"https://www.keirin.jp/pc/json?encp={enc_r}&type=JSJ012"

            try:
                jsj006, status006, len006 = get_json(url006)
                jsj012, status012, len012 = get_json(url012)
            except Exception as e:
                print(f"    [{ri}/{len(races)}] {race_key} ❌ 取得失敗")
                problems.append({
                    "race_key": race_key,
                    "problem": "RACE_FETCH_ERROR",
                    "error": repr(e),
                })
                continue

            p006 = jsj006.get("sensyuTypeInfo") or []
            p012 = jsj012.get("tyakujyunItemSubData") or []

            ok006 = isinstance(p006, list) and len(p006) > 0
            ok012 = isinstance(p012, list) and len(p012) > 0

            total_races += 1
            date_race_dist[kday] += 1

            if ok006 and ok012:
                complete += 1
                mark = "✅"
            else:
                mark = "❌"
                problems.append({
                    "race_key": race_key,
                    "problem": "RAW_STRUCTURE_NG",
                    "jsj006_count": len(p006) if isinstance(p006, list) else None,
                    "jsj012_count": len(p012) if isinstance(p012, list) else None,
                })

            print(
                f"    [{ri}/{len(races)}] {race_key} {mark} "
                f"006={len(p006) if isinstance(p006, list) else 'NG'}人 / "
                f"012着順={len(p012) if isinstance(p012, list) else 'NG'}"
            )

            venue_item["races"].append({
                "race_key": race_key,
                "race_no": race_no,
                "encParaR": enc_r,
                "jsj006": jsj006,
                "jsj012": jsj012,
            })

            time.sleep(0.05)

        date_item["venues"].append(venue_item)

    all_dates.append(date_item)

result = {
    "target_dates": DATES,
    "date_count": len(DATES),
    "total_venue_count": total_venues,
    "total_race_count": total_races,
    "complete_race_count": complete,
    "date_venue_distribution": dict(date_venue_dist),
    "date_race_distribution": dict(date_race_dist),
    "problem_count": len(problems),
    "problems": problems,
    "dates": all_dates,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print()
print("=" * 80)
print("=== 239 結果 ===")
print("対象日数:", len(DATES))
print("開催会場総数:", total_venues)
print("取得レース総数:", total_races)
print("JSJ006+JSJ012完全取得:", complete)
print("日付別会場数:", dict(date_venue_dist))
print("日付別レース数:", dict(date_race_dist))
print("問題件数:", len(problems))

if problems:
    print()
    print("=== 問題一覧 先頭50件 ===")
    for p in problems[:50]:
        print(p)

print()
print("保存完了:", OUT)
print("=== 239 完了 ===")
