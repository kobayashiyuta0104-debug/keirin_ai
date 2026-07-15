import json
from pathlib import Path

SRC = Path(r"C:\競輪AI\213_20260706_all_race_raw_capture.json")
OUT = Path(r"C:\競輪AI\229_jsj012_harai_structure_analysis.json")

def find_first(o):
    if isinstance(o, dict):
        if isinstance(o.get("tyakujyunItemSubData"), list) and "haraiGakuSubData" in o:
            return o
        for v in o.values():
            r=find_first(v)
            if r is not None: return r
    elif isinstance(o,list):
        for v in o:
            r=find_first(v)
            if r is not None: return r
    return None

def walk(o,path="$",rows=None):
    if rows is None: rows=[]
    if isinstance(o,dict):
        rows.append({"path":path,"type":"dict","keys":list(o.keys()),"value":None})
        for k,v in o.items(): walk(v,f"{path}.{k}",rows)
    elif isinstance(o,list):
        rows.append({"path":path,"type":"list","keys":None,"value":f"件数={len(o)}"})
        for i,v in enumerate(o): walk(v,f"{path}[{i}]",rows)
    else:
        rows.append({"path":path,"type":type(o).__name__,"keys":None,"value":o})
    return rows

def main():
    print("=== 229 JSJ012 haraiGakuSubData 払戻構造完全解析 ===")
    data=json.loads(SRC.read_text(encoding="utf-8"))
    jsj012=find_first(data)
    if jsj012 is None:
        print("JSJ012未発見"); return

    harai=jsj012.get("haraiGakuSubData")
    print("\n=== haraiGakuSubData RAW ===")
    print(json.dumps(harai,ensure_ascii=False,indent=2))

    rows=walk(harai)
    print("\n=== 全PATH・値 ===")
    for x in rows:
        if x["type"]=="dict":
            print(f'{x["path"]} / dict / KEYS={x["keys"]}')
        else:
            print(f'{x["path"]} / {x["type"]} / {x["value"]}')

    keywords=("3","san","rentan","trifecta","kumiban","harai","gaku","money")
    print("\n=== 3連単・払戻候補PATH ===")
    hits=[]
    for x in rows:
        s=(x["path"]+" "+str(x["value"])).lower()
        if any(k in s for k in keywords):
            hits.append(x)
            print(f'{x["path"]} -> {x["value"]}')

    OUT.write_text(json.dumps({
        "harai_raw":harai,
        "all_paths":rows,
        "candidate_hits":hits
    },ensure_ascii=False,indent=2),encoding="utf-8")
    print("\n保存完了:",OUT)
    print("=== 229 完了 ===")

if __name__=="__main__":
    main()
