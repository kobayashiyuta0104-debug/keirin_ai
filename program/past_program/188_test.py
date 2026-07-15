import json
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import requests

print("=== 188 JSJ012未確定4レース 再取得テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_FILE = BASE_DIR / "181_verified_jsj006_capture.json"
RESULT_FILE = BASE_DIR / "187_verified_jsj012_capture.json"
OUTPUT_FILE = BASE_DIR / "188_jsj012_retry_analysis.json"

TIMEOUT = 30
SLEEP_SEC = 0.5

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def normalize_captures(raw):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        if isinstance(raw.get("captures"), list):
            return raw["captures"]
        rows = []
        for key, value in raw.items():
            if isinstance(value, dict):
                item = dict(value)
                item.setdefault("race_key", key)
                rows.append(item)
        return rows
    return []

def extract_encp(url):
    if not url:
        return None
    values = parse_qs(urlparse(url).query, keep_blank_values=True).get("encp")
    return values[0] if values else None

def norm_id(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.zfill(6) if text.isdigit() else text

def finish_ids(data):
    rows = data.get("tyakujyunItemSubData", [])
    ids = []
    if not isinstance(rows, list):
        return ids
    for row in rows:
        if not isinstance(row, dict):
            continue
        for key, value in row.items():
            lower = key.lower()
            if ("regist" in lower or "touroku" in lower) and value not in (None, ""):
                ids.append(norm_id(value))
                break
    return ids

source = normalize_captures(load_json(SOURCE_FILE))
previous = load_json(RESULT_FILE)

failed_keys = [
    x.get("race_key")
    for x in previous.get("failures", [])
    if x.get("reason") == "RESULT_STRUCTURE_MISSING"
]

source_map = {x.get("race_key"): x for x in source}

print(f"187の結果構造不足レース数: {len(failed_keys)}")
for key in failed_keys:
    print(f"  {key}")

session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
    ),
    "Referer": "https://www.keirin.jp/pc/race/index",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
})

results = []
success = 0

for i, race_key in enumerate(failed_keys, start=1):
    print()
    print(f"[{i}/{len(failed_keys)}] {race_key}")

    capture = source_map.get(race_key)
    if not capture:
        print("  ❌ 181側captureなし")
        results.append({"race_key": race_key, "status": "SOURCE_NOT_FOUND"})
        continue

    encp = extract_encp(capture.get("request_url"))
    target_ids = {
        norm_id(x) for x in capture.get("target_player_ids", []) if norm_id(x)
    }

    try:
        response = session.get(
            "https://www.keirin.jp/pc/json",
            params={"encp": encp, "type": "JSJ012"},
            timeout=TIMEOUT,
        )
        data = response.json()

        finish_rows = data.get("tyakujyunItemSubData")
        payout = data.get("haraiGakuSubData")
        got_ids = set(finish_ids(data))

        record = {
            "race_key": race_key,
            "status_code": response.status_code,
            "encp": encp,
            "top_level_keys": list(data.keys()) if isinstance(data, dict) else None,
            "finish_order_count": len(finish_rows) if isinstance(finish_rows, list) else None,
            "has_haraiGakuSubData": isinstance(payout, dict),
            "target_player_ids": sorted(target_ids),
            "jsj012_player_ids": sorted(got_ids),
            "data": data,
        }

        if (
            isinstance(finish_rows, list)
            and isinstance(payout, dict)
            and len(target_ids) == 7
            and len(got_ids) == 7
            and target_ids == got_ids
        ):
            record["status"] = "7_OF_7_MATCH"
            success += 1
            print("  ✅ 現在はJSJ012結果あり + 選手ID 7/7完全一致")
        else:
            record["status"] = "STILL_MISSING_OR_MISMATCH"
            print("  ⚠ まだ結果構造不足またはID比較不可")
            print(f"  TOPキー: {record['top_level_keys']}")
            print(f"  着順件数: {record['finish_order_count']}")
            print(f"  払戻構造: {record['has_haraiGakuSubData']}")
            print(f"  JSJ012選手ID数: {len(got_ids)}")

        results.append(record)

    except Exception as e:
        print(f"  ❌ ERROR: {repr(e)}")
        results.append({
            "race_key": race_key,
            "status": "ERROR",
            "error": repr(e),
        })

    time.sleep(SLEEP_SEC)

output = {
    "retry_target_count": len(failed_keys),
    "success_7_of_7_count": success,
    "still_missing_count": len(failed_keys) - success,
    "results": results,
}

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print()
print("=== 188 結果 ===")
print(f"再取得対象: {len(failed_keys)}")
print(f"現在7/7完全一致: {success}")
print(f"まだ不足: {len(failed_keys) - success}")
print(f"保存完了: {OUTPUT_FILE}")
print("=== 188 完了 ===")
