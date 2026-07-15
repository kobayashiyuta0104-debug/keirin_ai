import json
from pathlib import Path
from collections import Counter

OLD_PATH = Path(r"C:\競輪AI\163_dated_ai_pre_race_features.json")
RAW_PATH = Path(r"C:\競輪AI\181_verified_jsj006_capture.json")
OUT_PATH = Path(r"C:\競輪AI\226_normalized_full_exact_compare.json")

FIELD_MAP = {
    "car_no":"syaban","player_id":"sensyuRegistNo","player_name":"sensyuName",
    "prefecture":"huKen","previous_class":"prevKyuhan","class":"kyuhan",
    "riding_style":"kyakusitu","graduation_term":"sotugyouki","age":"age",
    "race_score":"heikinTokuten","nige_count":"nigeCnt","makuri_count":"makuriCnt",
    "sashi_count":"sasiCnt","mark_count":"markCnt","back_count":"backCnt",
    "home_count":"homeTori","start_count":"stTori","win_rate":"syouritu",
    "top2_rate":"rentairitu2","top3_rate":"rentairitu3",
}
INT_FIELDS={"car_no","graduation_term","age","nige_count","makuri_count","sashi_count",
"mark_count","back_count","home_count","start_count"}
FLOAT_FIELDS={"race_score","win_rate","top2_rate","top3_rate"}

def find_race_key(o):
    if isinstance(o,dict):
        if o.get("race_key"): return o["race_key"]
        for v in o.values():
            x=find_race_key(v)
            if x: return x
    elif isinstance(o,list):
        for v in o:
            x=find_race_key(v)
            if x: return x

def find_players(o):
    if isinstance(o,dict):
        if isinstance(o.get("sensyuTypeInfo"),list): return o["sensyuTypeInfo"]
        for v in o.values():
            x=find_players(v)
            if x is not None: return x
    elif isinstance(o,list):
        for v in o:
            x=find_players(v)
            if x is not None: return x

def old_races(d):
    if isinstance(d,list): return d
    for k in ("races","data","features"):
        if isinstance(d.get(k),list): return d[k]
    return [v for v in d.values() if isinstance(v,dict) and find_race_key(v)]

def old_players(r):
    return r.get("players",[]) if isinstance(r,dict) else []

def norm_space(v):
    if not isinstance(v,str): return v
    return " ".join(v.replace("\u3000"," ").split())

def norm_id(v):
    s=str(v).strip()
    return s.zfill(6) if s.isdigit() else s

def conv(v,f):
    if v in (None,""): return None
    try:
        if f in INT_FIELDS: return int(float(str(v).replace("%","").strip()))
        if f in FLOAT_FIELDS: return float(str(v).replace("%","").strip())
    except: pass
    if f in {"player_name","prefecture"}: return norm_space(v)
    return v

def finish(v):
    s=str(v).strip() if v not in (None,"") else ""
    return int(s) if s.isdigit() else None

def back(v):
    try: return int(v)
    except: return None

def rebuild(raw):
    out={k:conv(raw.get(v),k) for k,v in FIELD_MAP.items()}
    t=raw.get("tyo4InfoSubData") if isinstance(raw.get("tyo4InfoSubData"),dict) else {}
    rows=t.get("resultInfoSubData") if isinstance(t.get("resultInfoSubData"),list) else []
    out["recent_meeting_results"]=[{"finish":finish(x.get("imgTyakuiName")),"back":back(x.get("backTori"))} for x in rows]
    out["recent_meeting"]={
        "venue_code":t.get("bKeirinjyoCd"),"venue_name":t.get("kerinjyoName"),
        "meeting_start_date":t.get("kaisaiFirst"),"grade":t.get("gaiTeiGrade")
    }
    return out

def main():
    print("=== 226 空白正規化後 JSJ006 RAW -> 163形式 完全一致最終確認 ===")
    old=json.loads(OLD_PATH.read_text(encoding="utf-8"))
    raw=json.loads(RAW_PATH.read_text(encoding="utf-8"))
    rm={}
    for c in raw.get("captures",[]):
        rk=find_race_key(c); ps=find_players(c)
        if rk and isinstance(ps,list):
            rm[rk]={norm_id(p.get("sensyuRegistNo")):p for p in ps if isinstance(p,dict)}

    fields=list(FIELD_MAP)+["recent_meeting_results","recent_meeting"]
    total=exact=missing=0
    fm=Counter(); fc=Counter(); diffs=[]

    for r in old_races(old):
        rk=find_race_key(r)
        if rk not in rm: continue
        for op in old_players(r):
            pid=norm_id(op.get("player_id"))
            rp=rm[rk].get(pid)
            if rp is None: missing+=1; continue
            total+=1; np=rebuild(rp); ds=[]
            for f in fields:
                fc[f]+=1
                ov=op.get(f)
                if f in {"player_name","prefecture"}: ov=norm_space(ov)
                if ov==np.get(f): fm[f]+=1
                else: ds.append({"field":f,"old":ov,"rebuilt":np.get(f)})
            if not ds: exact+=1
            elif len(diffs)<100: diffs.append({"race_key":rk,"player_id":pid,"diff":ds})

    print("\n=== 226 結果 ===")
    print("比較選手数:",total)
    print("全フィールド完全一致選手:",exact)
    print("完全一致率:",f"{exact/total*100:.2f}%" if total else "0%")
    print("RAW選手ID未発見:",missing)
    print("不一致選手数:",total-exact)
    print("\n=== フィールド別一致率 ===")
    for f in fields:
        print(f"{f}: {fm[f]}/{fc[f]} = {fm[f]/fc[f]*100:.2f}%")
    print("\n=== 不一致サンプル ===")
    for x in diffs[:30]: print(json.dumps(x,ensure_ascii=False,indent=2))

    OUT_PATH.write_text(json.dumps({
        "compared_players":total,"exact_players":exact,
        "exact_rate":exact/total if total else 0,"missing_raw":missing,
        "mismatches":diffs
    },ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"\n保存完了: {OUT_PATH}")
    print("=== 226 完了 ===")

if __name__=="__main__":
    main()
