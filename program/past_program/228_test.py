import json
from pathlib import Path
from collections import Counter

FEATURE_PATH = Path(r"C:\競輪AI\227_20260706_pre_race_features.json")
RAW_PATH = Path(r"C:\競輪AI\213_20260706_all_race_raw_capture.json")
OUT_PATH = Path(r"C:\競輪AI\228_20260706_features_with_results.json")

def find_races(o, out):
    if isinstance(o, dict):
        rk = o.get("race_key")
        jsj012 = None
        for v in o.values():
            if isinstance(v, dict) and isinstance(v.get("tyakujyunItemSubData"), list) and "haraiGakuSubData" in v:
                jsj012 = v
                break
        if rk and jsj012:
            out[rk] = jsj012
            return
        for v in o.values(): find_races(v, out)
    elif isinstance(o, list):
        for v in o: find_races(v, out)

def norm_id(v):
    s = str(v or "").strip()
    return s.zfill(6) if s.isdigit() else s

def to_int(v):
    if v in (None, ""): return None
    s = str(v).replace(",", "").replace("円", "").strip()
    try: return int(float(s))
    except: return None

def text(v):
    return str(v or "").strip()

def player_id(row):
    for k in ("sensyuRegistNo","sensyuNo","sensyuId","sensyuID"):
        if row.get(k) not in (None, ""): return norm_id(row.get(k))
    return ""

def finish_status(row):
    vals = [text(row.get(k)) for k in row.keys()]
    joined = " ".join(vals)
    for word in ("失格","落車棄権","途中棄権","欠場","棄権"):
        if word in joined: return None, word
    for k in ("tyakujyun","tyakujyunName","tyakui","rank","finish"):
        n = to_int(row.get(k))
        if n is not None: return n, "NORMAL"
    for v in vals:
        if v.isdigit() and 1 <= int(v) <= 9: return int(v), "NORMAL"
    return None, "UNKNOWN"

def find_trifecta(o):
    hits = []
    def walk(x):
        if isinstance(x, dict):
            vals = {k:text(v) for k,v in x.items() if not isinstance(v,(dict,list))}
            joined = " ".join(vals.values())
            if any(w in joined for w in ("3連単","３連単")):
                hits.append(vals)
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(o)
    for h in hits:
        comb = None; payout = None
        for v in h.values():
            s = v.replace("－","-").replace("‐","-")
            parts = s.split("-")
            if len(parts)==3 and all(p.strip().isdigit() for p in parts):
                comb = "-".join(p.strip() for p in parts)
            n = to_int(v)
            if n is not None and n >= 100: payout = max(payout or 0, n)
        if comb and payout: return comb, payout
    return None, None

def main():
    print("=== 228 227レース前能力 + JSJ012確定結果 自動接続テスト ===")
    races = json.loads(FEATURE_PATH.read_text(encoding="utf-8"))
    raw = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    result_map = {}
    find_races(raw, result_map)

    out=[]; problems=[]; status_count=Counter()
    full_id=0; full_result=0; payout_ok=0

    for race in races:
        rk=race["race_key"]; jsj012=result_map.get(rk)
        if jsj012 is None:
            problems.append({"race_key":rk,"problem":"JSJ012_NOT_FOUND"}); continue
        rows=jsj012.get("tyakujyunItemSubData",[])
        by_id={player_id(x):x for x in rows if player_id(x)}
        if len(by_id)==len(race["players"]): full_id+=1

        connected=0
        for p in race["players"]:
            rr=by_id.get(norm_id(p["player_id"]))
            if rr is None: continue
            rank,status=finish_status(rr)
            p["finish_rank"]=rank
            p["result_status"]=status
            connected+=1; status_count[status]+=1
        if connected==len(race["players"]): full_result+=1

        comb,payout=find_trifecta(jsj012.get("haraiGakuSubData"))
        race["trifecta_combination"]=comb
        race["trifecta_payout"]=payout
        if comb and payout is not None: payout_ok+=1
        else: problems.append({"race_key":rk,"problem":"TRIFECTA_NOT_FOUND"})
        out.append(race)

    OUT_PATH.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\n=== 228 結果 ===")
    print("対象レース数:",len(races))
    print("結果接続レース数:",len(out))
    print("選手ID完全一致レース:",full_id)
    print("結果人数完全接続レース:",full_result)
    print("3連単組番・払戻取得レース:",payout_ok)
    print("結果status分布:",dict(status_count))
    print("問題件数:",len(problems))
    print("保存完了:",OUT_PATH)
    if problems:
        print("\n=== 問題一覧 先頭30件 ===")
        for x in problems[:30]: print(x)
    if out:
        r=out[0]
        print("\n=== 先頭1レース確認 ===")
        print("race_key:",r["race_key"])
        print("trifecta_combination:",r["trifecta_combination"])
        print("trifecta_payout:",r["trifecta_payout"])
        print("先頭選手:",r["players"][0])
    print("=== 228 完了 ===")

if __name__=="__main__":
    main()
