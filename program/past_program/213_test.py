import json
import time
from pathlib import Path
import requests

BASE = Path(r"C:\競輪AI")
KDAY = "20260706"
OUT = BASE / f"213_{KDAY}_all_race_raw_capture.json"

print(f"=== 213 {KDAY} 全会場・全レース JSJ006 + JSJ012 完全自動取得テスト ===")

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.keirin.jp/pc/top",
})

def get_json(url):
    r = session.get(url, timeout=30)
    text = r.text
    try:
        data = r.json()
    except Exception:
        data = None
    return r.status_code, text, data

# 1. 日付 -> 開催会場
url057 = f"https://www.keirin.jp/pc/json?kday={KDAY}&type=JSJ057"
status, text, data057 = get_json(url057)
kinfo = (data057 or {}).get("kInfo") or []

print("JSJ057 HTTP:", status)
print("開催会場数:", len(kinfo))

captures = []
problems = []
total_map_races = 0
ok006 = 0
ok012 = 0
complete_both = 0

for vi, venue in enumerate(kinfo, 1):
    venue_name = venue.get("jyoName")
    venue_code = str(venue.get("KeirinCd") or venue.get("bKeirinCd") or "")
    entry_enc = venue.get("encPrm")

    print()
    print("=" * 80)
    print(f"[会場 {vi}/{len(kinfo)}] {venue_name} / code={venue_code}")

    url001 = f"https://www.keirin.jp/pc/json?encp={entry_enc}&type=JSJ001"
    s001, t001, d001 = get_json(url001)
    c = (d001 or {}).get("C0201data") or {}
    races = c.get("C0201race") or []

    print("  JSJ001 HTTP:", s001)
    print("  レース地図件数:", len(races))
    total_map_races += len(races)

    for ri, race in enumerate(races, 1):
        enc_r = race.get("encParaR")
        race_no = ri
        race_key = f"{KDAY}_{venue_name}_{race_no}R"

        if not enc_r:
            print(f"  [{ri}/{len(races)}] {race_key} ❌ encParaRなし")
            problems.append({"race_key": race_key, "problem": "ENCPAR_MISSING"})
            continue

        u006 = f"https://www.keirin.jp/pc/json?encp={enc_r}&type=JSJ006"
        u012 = f"https://www.keirin.jp/pc/json?encp={enc_r}&type=JSJ012"

        s006, t006, d006 = get_json(u006)
        s012, t012, d012 = get_json(u012)

        sensyu = (d006 or {}).get("sensyuTypeInfo") or []
        tyaku = (d012 or {}).get("tyakujyunItemSubData") or []
        harai = (d012 or {}).get("haraiGakuSubData")

        jsj006_ok = s006 == 200 and len(sensyu) > 0
        jsj012_ok = s012 == 200 and len(tyaku) > 0 and harai is not None

        if jsj006_ok:
            ok006 += 1
        if jsj012_ok:
            ok012 += 1
        if jsj006_ok and jsj012_ok:
            complete_both += 1

        mark = "✅" if jsj006_ok and jsj012_ok else "❌"
        print(
            f"  [{ri}/{len(races)}] {race_key} {mark} "
            f"006={len(sensyu)}人 / 012着順={len(tyaku)}"
        )

        if not jsj006_ok or not jsj012_ok:
            problems.append({
                "race_key": race_key,
                "problem": "STRUCTURE_MISSING",
                "jsj006_http": s006,
                "jsj012_http": s012,
                "sensyu_count": len(sensyu),
                "tyaku_count": len(tyaku),
                "harai_exists": harai is not None,
            })

        captures.append({
            "race_date": KDAY,
            "venue": venue_name,
            "venue_code": venue_code,
            "race_no": race_no,
            "race_key": race_key,
            "entry_encPrm": entry_enc,
            "race_encParaR": enc_r,
            "jsj006": d006,
            "jsj012": d012,
            "jsj006_ok": jsj006_ok,
            "jsj012_ok": jsj012_ok,
        })

        time.sleep(0.10)

result = {
    "race_date": KDAY,
    "venue_count": len(kinfo),
    "map_race_count": total_map_races,
    "jsj006_ok_count": ok006,
    "jsj012_ok_count": ok012,
    "complete_both_count": complete_both,
    "problem_count": len(problems),
    "problems": problems,
    "captures": captures,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print()
print("=== 213 結果 ===")
print("開催会場数:", len(kinfo))
print("地図レース総数:", total_map_races)
print("JSJ006構造OK:", ok006)
print("JSJ012構造OK:", ok012)
print("両方完全取得:", complete_both)
print("問題件数:", len(problems))

if problems:
    print()
    print("=== 問題一覧 ===")
    for x in problems:
        print(x)

print("保存完了:", OUT)
print("=== 213 完了 ===")
