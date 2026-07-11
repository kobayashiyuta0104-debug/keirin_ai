import json
from pathlib import Path
import requests

BASE = Path(r"C:\競輪AI")
SRC = BASE / "210_jsj057_082_response_capture.json"
OUT = BASE / "212_all_venue_jsj001_map_test.json"

print("=== 212 JSJ057 encPrm -> JSJ001 全8会場地図 直接取得テスト ===")

with open(SRC, "r", encoding="utf-8") as f:
    captures = json.load(f)

jsj057 = next(x for x in captures if x.get("type") == "JSJ057")
kinfo = (jsj057.get("data") or {}).get("kInfo") or []

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.keirin.jp/pc/top",
})

results = []
ok_count = 0
total_races = 0

for i, venue in enumerate(kinfo, 1):
    name = venue.get("jyoName")
    code = venue.get("KeirinCd")
    enc = venue.get("encPrm")

    print()
    print("=" * 80)
    print(f"[{i}/{len(kinfo)}] {name} / code={code}")

    url = f"https://www.keirin.jp/pc/json?encp={enc}&type=JSJ001"

    try:
        r = session.get(url, timeout=30)
        text = r.text
        data = r.json()

        c = data.get("C0201data") if isinstance(data, dict) else None
        kaisai = c.get("C0201kaisai") or [] if isinstance(c, dict) else []
        races = c.get("C0201race") or [] if isinstance(c, dict) else []
        selected_date = c.get("selKaisai") if isinstance(c, dict) else None
        selected_race = c.get("selRaceNo") if isinstance(c, dict) else None

        race_encs = [
            x.get("encParaR")
            for x in races
            if isinstance(x, dict) and x.get("encParaR")
        ]

        structure_ok = isinstance(c, dict) and len(race_encs) > 0

        print("  HTTP:", r.status_code)
        print("  文字数:", len(text))
        print("  JSJ001構造OK:", structure_ok)
        print("  開催日程件数:", len(kaisai))
        print("  レース件数:", len(races))
        print("  encParaR件数:", len(race_encs))
        print("  selKaisai:", selected_date)
        print("  selRaceNo:", selected_race)

        if kaisai:
            print("  開催日程:")
            for x in kaisai:
                if isinstance(x, dict):
                    print(
                        "   ",
                        x.get("txtEventDate"),
                        x.get("txtDaily"),
                        "encParaKあり=",
                        bool(x.get("encParaK")),
                    )

        if structure_ok:
            ok_count += 1
            total_races += len(race_encs)

        results.append({
            "venue": name,
            "venue_code": code,
            "entry_encPrm": enc,
            "http_status": r.status_code,
            "text_length": len(text),
            "structure_ok": structure_ok,
            "selected_date": selected_date,
            "selected_race": selected_race,
            "kaisai": kaisai,
            "races": races,
            "race_encParaR_count": len(race_encs),
        })

    except Exception as e:
        print("  ❌ ERROR:", repr(e))
        results.append({
            "venue": name,
            "venue_code": code,
            "entry_encPrm": enc,
            "error": repr(e),
            "structure_ok": False,
        })

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print()
print("=== 212 結果 ===")
print("対象会場数:", len(kinfo))
print("JSJ001構造OK会場:", ok_count)
print("取得レースencParaR総数:", total_races)
print("保存完了:", OUT)
print("=== 212 完了 ===")
