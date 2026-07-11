import json
from pathlib import Path
from collections import Counter

FEATURES = Path(r"C:\競輪AI\228_20260706_features_with_results.json")
RAW = Path(r"C:\競輪AI\213_20260706_all_race_raw_capture.json")
OUT = Path(r"C:\競輪AI\230_20260706_features_with_results_fixed.json")

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def race_key_of(o):
    if not isinstance(o, dict): return None
    for k in ("race_key","raceKey"):
        if o.get(k): return str(o[k])
    return None

def find_jsj012(o):
    if isinstance(o, dict):
        if "tyakujyunItemSubData" in o and "haraiGakuSubData" in o:
            return o
        for v in o.values():
            r=find_jsj012(v)
            if r is not None: return r
    elif isinstance(o,list):
        for v in o:
            r=find_jsj012(v)
            if r is not None: return r
    return None

def collect_races(o, out):
    if isinstance(o, dict):
        rk=race_key_of(o)
        j12=find_jsj012(o)
        if rk and j12 is not None:
            out[rk]=j12
            return
        for v in o.values(): collect_races(v,out)
    elif isinstance(o,list):
        for v in o: collect_races(v,out)

def find_feature_races(o):
    candidates=[]
    def walk(x):
        if isinstance(x,list) and x and all(isinstance(v,dict) for v in x):
            n=sum(1 for v in x if race_key_of(v))
            if n: candidates.append((n,x))
        if isinstance(x,dict):
            for v in x.values(): walk(v)
        elif isinstance(x,list):
            for v in x: walk(v)
    walk(o)
    return max(candidates,key=lambda z:z[0])[1] if candidates else []

def money(v):
    try: return int(str(v).replace(",","").strip())
    except: return None

def main():
    print("=== 230 3連単正式PATH修正・70レース完全接続 ===")
    feat=load(FEATURES)
    raw=load(RAW)

    raw_map={}
    collect_races(raw,raw_map)
    races=find_feature_races(feat)

    ok=0
    missing=[]
    labels=Counter()

    for race in races:
        rk=race_key_of(race)
        j12=raw_map.get(rk)
        item=None
        if j12:
            harai=j12.get("haraiGakuSubData") or {}
            rt3=harai.get("RT3HaraiGakuDispItemSubData") or []
            for x in rt3:
                if isinstance(x,dict) and x.get("kumiBan") and money(x.get("haraiGaku")) is not None:
                    item=x
                    break

        if item:
            payout=money(item["haraiGaku"])
            race["trifecta_combination"]=item["kumiBan"]
            race["trifecta_payout"]=payout
            race["trifecta_popularity"]=item.get("ninki")
            if payout < 10000: label="UNDER_10000"
            elif payout < 20000: label="10000_TO_19999"
            elif payout < 50000: label="20000_TO_49999"
            else: label="50000_PLUS"
            race["payout_class_4"]=label
            race["is_20000_plus"]=int(payout >= 20000)
            race["is_50000_plus"]=int(payout >= 50000)
            labels[label]+=1
            ok+=1
        else:
            missing.append(rk)

    OUT.write_text(json.dumps(feat,ensure_ascii=False,indent=2),encoding="utf-8")

    print("\n=== 230 結果 ===")
    print("対象レース数:",len(races))
    print("RAW JSJ012地図数:",len(raw_map))
    print("3連単組番・払戻取得:",ok)
    print("未取得:",len(missing))
    print("4分類分布:",dict(labels))
    print("2万円以上:",sum(1 for r in races if r.get("is_20000_plus")==1))
    print("5万円以上:",sum(1 for r in races if r.get("is_50000_plus")==1))
    print("問題件数:",len(missing))

    if races:
        r=races[0]
        print("\n=== 先頭1レース確認 ===")
        print("race_key:",race_key_of(r))
        print("trifecta_combination:",r.get("trifecta_combination"))
        print("trifecta_payout:",r.get("trifecta_payout"))
        print("trifecta_popularity:",r.get("trifecta_popularity"))
        print("payout_class_4:",r.get("payout_class_4"))

    if missing:
        print("\n=== 未取得一覧 ===")
        for x in missing: print(x)

    print("\n保存完了:",OUT)
    print("=== 230 完了 ===")

if __name__=="__main__":
    main()
