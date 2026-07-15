import json
import csv
from pathlib import Path

print("=== 191 AI学習用1レース1行データ整形テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "190_joined_ai_training_data.json"
JSON_OUTPUT = BASE_DIR / "191_ai_training_rows.json"
CSV_OUTPUT = BASE_DIR / "191_ai_training_rows.csv"

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def first_value(d, keys):
    if not isinstance(d, dict):
        return None
    for key in keys:
        if key in d:
            return d.get(key)
    return None

def num(value):
    if value is None or value == "":
        return None
    text = str(value).replace("%", "").replace(",", "").strip()
    try:
        return float(text)
    except:
        return None

raw = load_json(INPUT_FILE)
training = raw.get("training_races", {})

rows = []

for race_key, joined in sorted(training.items()):
    pre = joined.get("pre_race", {})
    result = joined.get("result", {})

    players = first_value(pre, ["players", "sensyu", "sensyuTypeInfo", "player_features"])
    if not isinstance(players, list):
        # 163構造内の最初の7件リストを探す
        players = None
        for value in pre.values():
            if isinstance(value, list) and len(value) == 7 and all(isinstance(x, dict) for x in value):
                players = value
                break

    finish_rows = result.get("tyakujyunItemSubData", []) if isinstance(result, dict) else []
    finish_map = {}

    if isinstance(finish_rows, list):
        for finish in finish_rows:
            if not isinstance(finish, dict):
                continue
            pid = first_value(finish, ["sensyuRegistNo", "sensyuTourokuNo", "registNo"])
            rank = first_value(finish, ["tyakujyun", "tyakujyunNo", "jyuni", "rank"])
            if pid is not None:
                finish_map[str(pid).zfill(6)] = rank

    row = {
        "race_key": race_key,
        "date": first_value(pre, ["date", "race_date"]),
        "venue": first_value(pre, ["venue", "keirinjo"]),
        "race_no": first_value(pre, ["race_no", "raceNo"]),
        "player_count": len(players) if isinstance(players, list) else 0,
    }

    if isinstance(players, list):
        for index, player in enumerate(players, start=1):
            prefix = f"p{index}_"
            pid = first_value(player, ["sensyuRegistNo", "player_id", "regist_no"])
            pid_norm = str(pid).zfill(6) if pid is not None else None

            row[prefix + "id"] = pid_norm
            row[prefix + "name"] = first_value(player, ["sensyuName", "name"])
            row[prefix + "score"] = num(first_value(player, ["heikinTokuten", "score", "得点"]))
            row[prefix + "style"] = first_value(player, ["kyakusitu", "style", "脚質"])
            row[prefix + "win_rate"] = num(first_value(player, ["syouritu", "win_rate", "勝率"]))
            row[prefix + "quinella_rate"] = num(first_value(player, ["rentairitu2", "quinella_rate", "2連対率"]))
            row[prefix + "trio_rate"] = num(first_value(player, ["rentairitu3", "trio_rate", "3連対率"]))
            row[prefix + "nige"] = num(first_value(player, ["nigeCnt", "nige"]))
            row[prefix + "makuri"] = num(first_value(player, ["makuriCnt", "makuri"]))
            row[prefix + "sasi"] = num(first_value(player, ["sasiCnt", "sasi"]))
            row[prefix + "mark"] = num(first_value(player, ["markCnt", "mark"]))
            row[prefix + "back"] = num(first_value(player, ["backCnt", "back"]))
            row[prefix + "home"] = num(first_value(player, ["homeTori", "home"]))
            row[prefix + "start"] = num(first_value(player, ["stTori", "start"]))
            row[prefix + "finish_rank"] = finish_map.get(pid_norm)

    payout = result.get("haraiGakuSubData", {}) if isinstance(result, dict) else {}
    rt3 = payout.get("RT3HaraiGakuDispItemSubData", []) if isinstance(payout, dict) else []

    row["rt3_raw"] = json.dumps(rt3, ensure_ascii=False)
    rows.append(row)

all_columns = []
seen = set()
for row in rows:
    for key in row.keys():
        if key not in seen:
            seen.add(key)
            all_columns.append(key)

with JSON_OUTPUT.open("w", encoding="utf-8") as f:
    json.dump({
        "row_count": len(rows),
        "column_count": len(all_columns),
        "columns": all_columns,
        "rows": rows,
    }, f, ensure_ascii=False, indent=2)

with CSV_OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=all_columns)
    writer.writeheader()
    writer.writerows(rows)

print()
print("=== 191 結果 ===")
print(f"学習用レース行数: {len(rows)}")
print(f"列数: {len(all_columns)}")
print(f"JSON保存: {JSON_OUTPUT}")
print(f"CSV保存: {CSV_OUTPUT}")

if rows:
    sample = rows[0]
    print()
    print("=== 先頭1レース確認 ===")
    print(f"race_key: {sample.get('race_key')}")
    print(f"player_count: {sample.get('player_count')}")
    print(f"p1_id: {sample.get('p1_id')}")
    print(f"p1_name: {sample.get('p1_name')}")
    print(f"p1_score: {sample.get('p1_score')}")
    print(f"p1_finish_rank: {sample.get('p1_finish_rank')}")
    print(f"rt3_raw: {sample.get('rt3_raw')}")

print()
print("=== 191 完了 ===")
