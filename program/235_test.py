import json
from pathlib import Path

RAW = Path(r"C:\競輪AI\213_20260706_all_race_raw_capture.json")
MODEL = Path(r"C:\競輪AI\231_20260706_model_ready_154_features.json")
OUT = Path(r"C:\競輪AI\235_recent_finish_gap_213raw_analysis.json")

TARGETS = [
("20260706_京王閣_4R",1),("20260706_京王閣_4R",2),("20260706_京王閣_7R",6),
("20260706_伊東_1R",5),("20260706_伊東_2R",3),("20260706_伊東_4R",1),
("20260706_伊東_7R",2),("20260706_佐世保_4R",3),("20260706_別府_6R",1),
("20260706_取手_8R",6),("20260706_取手_9R",1),("20260706_取手_9R",6),
("20260706_和歌山_5R",3),("20260706_和歌山_10R",6),
("20260706_岸和田_3R",4),("20260706_豊橋_5R",7)]

def walk(x):
    if isinstance(x, dict):
        yield x
        for v in x.values(): yield from walk(v)
    elif isinstance(x, list):
        for v in x: yield from walk(v)

def main():
    print("=== 235 213RAW RECENT_FINISH_GAP 16選手直接解析 ===")
    raw=json.loads(RAW.read_text(encoding="utf-8"))
    model=json.loads(MODEL.read_text(encoding="utf-8"))
    models={r["race_key"]:r for r in model["races"]}

    # race_keyを持つ辞書ごと保存し、その配下からsensyuTypeInfoを探す
    raw_races={}
    for d in walk(raw):
        rk=d.get("race_key") if isinstance(d,dict) else None
        if rk:
            sensyu=None
            for z in walk(d):
                if isinstance(z,dict) and isinstance(z.get("sensyuTypeInfo"),list):
                    sensyu=z["sensyuTypeInfo"]; break
            if sensyu is not None:
                raw_races[rk]=sensyu

    print("213 RAW race_key+選手構造発見数:",len(raw_races))
    results=[]; problems=[]

    for rk,p in TARGETS:
        print("\n"+"="*80)
        print("race_key:",rk,"/ p",p)
        players=raw_races.get(rk)
        if players is None:
            print("RAW RACE NOT FOUND")
            problems.append({"race_key":rk,"player":p,"problem":"RAW_NOT_FOUND"})
            continue
        player=next((x for x in players if str(x.get("syaban"))==str(p)),None)
        if player is None:
            print("RAW PLAYER NOT FOUND")
            problems.append({"race_key":rk,"player":p,"problem":"PLAYER_NOT_FOUND"})
            continue

        f=models[rk]["features"]
        vals=[f.get(f"p{p}_recent_finish_{i}") for i in range(1,4)]
        print("選手:",player.get("sensyuRegistNo"),player.get("sensyuName"))
        print("MODEL recent_finish:",vals)
        print("--- konResultInfoSubData RAW ---")
        print(json.dumps(player.get("konResultInfoSubData"),ensure_ascii=False,indent=2))
        print("--- tyo4InfoSubData RAW ---")
        print(json.dumps(player.get("tyo4InfoSubData"),ensure_ascii=False,indent=2))
        results.append({
            "race_key":rk,"player":p,"player_id":player.get("sensyuRegistNo"),
            "player_name":player.get("sensyuName"),"model_recent_finish":vals,
            "konResultInfoSubData":player.get("konResultInfoSubData"),
            "tyo4InfoSubData":player.get("tyo4InfoSubData")
        })

    report={"target_count":len(TARGETS),"raw_race_found_count":len(raw_races),
            "analyzed_count":len(results),"problem_count":len(problems),
            "problems":problems,"results":results}
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\n=== 235 結果 ===")
    print("対象:",len(TARGETS))
    print("解析成功:",len(results))
    print("問題件数:",len(problems))
    print("保存完了:",OUT)
    print("=== 235 完了 ===")

if __name__=="__main__":
    main()
