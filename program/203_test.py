import json
import requests
from pathlib import Path
from collections import Counter

print("=== 203 JSJ004 raceUrlPrm -> JSJ006 過去開催ルート直接取得テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "202_jsj004_historical_map_analysis.json"
OUTPUT_FILE = BASE_DIR / "203_historical_venue_jsj006_analysis.json"

with INPUT_FILE.open("r", encoding="utf-8") as f:
    raw = json.load(f)

items = raw.get("items", [])
if not items:
    raise RuntimeError("202のJSJ004解析データがありません")

kaisai_data = items[0].get("kaisaiData") or []
print(f"過去日開催数: {len(kaisai_data)}")

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.keirin.jp/pc/racelive",
})

def walk(obj, path="$", out=None):
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}"
            out.append((p, k, v))
            walk(v, p, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, f"{path}[{i}]", out)
    return out

results = []
problems = []

for i, venue in enumerate(kaisai_data, 1):
    name = venue.get("bkname")
    code = venue.get("bkCode")
    race_num = venue.get("raceNum")
    encp = venue.get("raceUrlPrm")

    print()
    print(f"[{i}/{len(kaisai_data)}] {name} / code={code} / raceNum={race_num}")
    print(f"  raceUrlPrm: {encp}")

    rec = {
        "venue": name,
        "venue_code": code,
        "race_num_from_jsj004": race_num,
        "raceUrlPrm": encp,
    }

    try:
        url = "https://www.keirin.jp/pc/json"
        r = session.get(
            url,
            params={"encp": encp, "type": "JSJ006"},
            timeout=30,
        )
        rec["request_url"] = r.url
        rec["http_status"] = r.status_code
        rec["text_length"] = len(r.text)

        print(f"  HTTP: {r.status_code}")
        print(f"  文字数: {len(r.text)}")

        data = r.json()
        rec["data"] = data

        top_keys = list(data.keys()) if isinstance(data, dict) else None
        rec["top_keys"] = top_keys
        print(f"  TOP KEYS: {top_keys}")

        walked = walk(data)
        param_hits = []
        value_counter = Counter()

        for path, key, value in walked:
            kl = str(key).lower()
            if any(x in kl for x in ["parameter", "param", "encp", "race", "url", "kk"]):
                if not isinstance(value, (dict, list)):
                    param_hits.append({
                        "path": path,
                        "key": key,
                        "value": value,
                    })
                    if value not in (None, ""):
                        value_counter[str(value)] += 1

        rec["parameter_hits"] = param_hits

        print(f"  parameter系ヒット: {len(param_hits)}")
        for hit in param_hits[:20]:
            val = repr(hit["value"])
            if len(val) > 180:
                val = val[:180] + "..."
            print(f"    {hit['path']} -> {val}")

        # 選手ID数も確認
        player_ids = []
        for path, key, value in walked:
            if key in ("sensyuRegistNo", "sensyuTourokuNo", "player_id"):
                if value not in (None, ""):
                    player_ids.append(str(value).strip())
        rec["player_ids"] = sorted(set(player_ids))
        print(f"  選手ID候補数: {len(rec['player_ids'])}")

        results.append(rec)

    except Exception as e:
        rec["error"] = repr(e)
        problems.append(rec)
        results.append(rec)
        print(f"  ❌ ERROR: {e}")

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump({
        "source": str(INPUT_FILE),
        "venue_count": len(kaisai_data),
        "results": results,
        "problems": problems,
    }, f, ensure_ascii=False, indent=2)

print()
print("=== 203 結果 ===")
print(f"対象開催数: {len(kaisai_data)}")
print(f"JSJ006 HTTP 200数: {sum(1 for x in results if x.get('http_status') == 200)}")
print(f"JSON取得数: {sum(1 for x in results if isinstance(x.get('data'), dict))}")
print(f"問題件数: {len(problems)}")

print()
print("=== 開催別まとめ ===")
for x in results:
    print(
        f"{x.get('venue')} / JSJ004={x.get('race_num_from_jsj004')} "
        f"/ HTTP={x.get('http_status')} "
        f"/ parameter系={len(x.get('parameter_hits', []))} "
        f"/ 選手ID候補={len(x.get('player_ids', []))}"
    )

print()
print(f"保存完了: {OUTPUT_FILE}")
print("=== 203 完了 ===")
