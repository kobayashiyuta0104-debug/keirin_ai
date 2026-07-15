import json
import urllib.request
import urllib.parse
from pathlib import Path

BASE = Path(r"C:\競輪AI")
SRC = BASE / "205_manual_historical_navigation_capture.json"
OUT = BASE / "207_historical_encpar_direct_test.json"

print("=== 207 JSJ001 encParaR -> JSJ006/JSJ012 過去レース直接取得テスト ===")

with open(SRC, "r", encoding="utf-8") as f:
    root = json.load(f)

jsj001_data = None

def walk(x):
    global jsj001_data
    if isinstance(x, dict):
        typ = x.get("type") or x.get("TYPE")
        data = x.get("data")
        if typ == "JSJ001" and isinstance(data, dict) and "C0201data" in data:
            jsj001_data = data
        for v in x.values():
            walk(v)
    elif isinstance(x, list):
        for v in x:
            walk(v)

walk(root)

if not jsj001_data:
    raise RuntimeError("205内のJSJ001 data.C0201data が見つかりません")

c = jsj001_data["C0201data"]
races = c.get("C0201race", [])
kaisai = c.get("C0201kaisai", [])

print("開催件数:", len(kaisai))
print("レースencParaR件数:", len(races))

def get_json(encp, typ):
    qs = urllib.parse.urlencode({"encp": encp, "type": typ})
    url = "https://www.keirin.jp/pc/json?" + qs
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.keirin.jp/pc/racelive",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            raw = res.read().decode("utf-8", errors="replace")
            status = res.status
        try:
            data = json.loads(raw)
        except Exception:
            data = None
        return status, url, raw, data, None
    except Exception as e:
        return None, url, "", None, repr(e)

results = []
limit = min(12, len(races))

for i, race in enumerate(races[:limit], 1):
    encp = race.get("encParaR")
    print()
    print(f"[{i}/{limit}] encParaR: {encp}")

    item = {"index": i, "race_meta": race, "encParaR": encp, "tests": {}}

    for typ in ["JSJ006", "JSJ012"]:
        status, url, raw, data, err = get_json(encp, typ)
        top_keys = list(data.keys()) if isinstance(data, dict) else None

        if typ == "JSJ006":
            player_count = 0
            if isinstance(data, dict):
                info = data.get("sensyuTypeInfo")
                if isinstance(info, list):
                    player_count = len(info)
            structure_ok = player_count > 0
            detail = f"選手構造件数={player_count}"
        else:
            finish_count = 0
            payout_ok = False
            if isinstance(data, dict):
                rows = data.get("tyakujyunItemSubData")
                if isinstance(rows, list):
                    finish_count = len(rows)
                payout_ok = bool(data.get("haraiGakuSubData"))
            structure_ok = finish_count > 0 and payout_ok
            detail = f"着順件数={finish_count} / 払戻構造={payout_ok}"

        print(f"  {typ}: HTTP={status} / 文字数={len(raw)} / 構造OK={structure_ok}")
        print(f"    {detail}")
        print(f"    TOP KEYS: {top_keys}")

        item["tests"][typ] = {
            "status": status,
            "url": url,
            "raw_length": len(raw),
            "top_keys": top_keys,
            "structure_ok": structure_ok,
            "detail": detail,
            "error": err,
            "data": data,
        }

    results.append(item)

jsj006_ok = sum(1 for x in results if x["tests"]["JSJ006"]["structure_ok"])
jsj012_ok = sum(1 for x in results if x["tests"]["JSJ012"]["structure_ok"])

print()
print("=== 207 結果 ===")
print("テストレース数:", len(results))
print("JSJ006構造OK:", jsj006_ok)
print("JSJ012構造OK:", jsj012_ok)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({
        "source": str(SRC),
        "kaisai_count": len(kaisai),
        "race_count": len(races),
        "test_count": len(results),
        "jsj006_ok": jsj006_ok,
        "jsj012_ok": jsj012_ok,
        "results": results,
    }, f, ensure_ascii=False, indent=2)

print("保存完了:", OUT)
print("=== 207 完了 ===")
