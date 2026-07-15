import json
import urllib.request
import urllib.parse
import time
from pathlib import Path
from collections import Counter

BASE = Path(r"C:\競輪AI")
OUT = BASE / "238_historical_multi_date_raw_capture.json"

DATES = [
    "20260705",
    "20260706",
]

BASE_URL = "https://www.keirin.jp/pc/json"

def get_json(params, retry=3):
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    last_error = None
    for attempt in range(1, retry + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as res:
                body = res.read().decode("utf-8")
            return json.loads(body), url
        except Exception as e:
            last_error = repr(e)
            if attempt < retry:
                time.sleep(1.0)
    raise RuntimeError(f"取得失敗: {url} / {last_error}")

def main():
    print("=== 238 複数過去日 全会場・全レース RAW自動取得テスト ===")

    all_dates = []
    problems = []
    seen_race_keys = set()
    total_venues = 0
    total_races = 0
    complete = 0
    date_race_dist = Counter()
    date_venue_dist = Counter()

    for di, kday in enumerate(DATES, 1):
        print("\n" + "=" * 80)
        print(f"[日付 {di}/{len(DATES)}] {kday}")

        try:
            jsj057, url057 = get_json({
                "kday": kday,
                "type": "JSJ057",
            })
        except Exception as e:
            print("  JSJ057取得失敗:", e)
            problems.append({
                "date": kday,
                "problem": "JSJ057_FETCH_ERROR",
                "error": repr(e),
            })
            continue

        kinfo = jsj057.get("kInfo") or []
        print("  開催会場数:", len(kinfo))
        total_venues += len(kinfo)
        date_venue_dist[kday] = len(kinfo)

        date_item = {
            "kday": kday,
            "jsj057_url": url057,
            "jsj057": jsj057,
            "venues": [],
        }

        for vi, venue in enumerate(kinfo, 1):
            jyo_name = venue.get("jyoName")
            code = venue.get("KeirinCd") or venue.get("bKeirinCd")
            enc_prm = venue.get("encPrm")

            print(f"\n  [会場 {vi}/{len(kinfo)}] {jyo_name} / code={code}")

            if not enc_prm:
                print("    encPrmなし")
                problems.append({
                    "date": kday,
                    "venue": jyo_name,
                    "problem": "ENC_PRM_MISSING",
                })
                continue

            try:
                jsj001, url001 = get_json({
                    "encParaK": enc_prm,
                    "type": "JSJ001",
                })
            except Exception as e:
                print("    JSJ001取得失敗:", e)
                problems.append({
                    "date": kday,
                    "venue": jyo_name,
                    "problem": "JSJ001_FETCH_ERROR",
                    "error": repr(e),
                })
                continue

            races = jsj001.get("C0201race") or []
            print("    レース地図件数:", len(races))

            venue_item = {
                "jyoName": jyo_name,
                "KeirinCd": code,
                "encPrm": enc_prm,
                "jsj001_url": url001,
                "jsj001": jsj001,
                "races": [],
            }

            for ri, race in enumerate(races, 1):
                race_no = ri
                enc_para_r = race.get("encParaR")

                if not enc_para_r:
                    problems.append({
                        "date": kday,
                        "venue": jyo_name,
                        "race_no": race_no,
                        "problem": "ENC_PARA_R_MISSING",
                    })
                    print(f"    [{ri}/{len(races)}] {race_no}R ❌ encParaRなし")
                    continue

                race_key = f"{kday}_{jyo_name}_{race_no}R"

                if race_key in seen_race_keys:
                    problems.append({
                        "race_key": race_key,
                        "problem": "DUPLICATE_RACE_KEY",
                    })
                seen_race_keys.add(race_key)

                try:
                    jsj006, url006 = get_json({
                        "encParaR": enc_para_r,
                        "type": "JSJ006",
                    })
                    jsj012, url012 = get_json({
                        "encParaR": enc_para_r,
                        "type": "JSJ012",
                    })
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
                    "encParaR": enc_para_r,
                    "jsj006_url": url006,
                    "jsj012_url": url012,
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

    OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("\n" + "=" * 80)
    print("=== 238 結果 ===")
    print("対象日数:", len(DATES))
    print("開催会場総数:", total_venues)
    print("取得レース総数:", total_races)
    print("JSJ006+JSJ012完全取得:", complete)
    print("日付別会場数:", dict(date_venue_dist))
    print("日付別レース数:", dict(date_race_dist))
    print("問題件数:", len(problems))

    if problems:
        print("\n=== 問題一覧 先頭50件 ===")
        for p in problems[:50]:
            print(p)

    print("\n保存完了:", OUT)
    print("=== 238 完了 ===")

if __name__ == "__main__":
    main()
