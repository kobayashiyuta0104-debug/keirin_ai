import json
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests

print("=== 187 全76レース JSJ012直接取得・race_key接続検証 ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "181_verified_jsj006_capture.json"
OUTPUT_FILE = BASE_DIR / "187_verified_jsj012_capture.json"

TIMEOUT = 30
SLEEP_SEC = 0.25

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def normalize_captures(raw):
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        if isinstance(raw.get("captures"), list):
            return raw["captures"]
        result = []
        for key, value in raw.items():
            if isinstance(value, dict):
                item = dict(value)
                item.setdefault("race_key", key)
                result.append(item)
        return result
    return []

def extract_encp(request_url):
    if not request_url:
        return None
    query = parse_qs(urlparse(request_url).query, keep_blank_values=True)
    values = query.get("encp")
    return values[0] if values else None

def normalize_id(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.zfill(6) if text.isdigit() else text

def extract_finish_ids(data):
    rows = data.get("tyakujyunItemSubData", []) if isinstance(data, dict) else []
    ids = []
    id_keys_found = []

    if not isinstance(rows, list):
        return ids, id_keys_found

    candidate_keys = (
        "sensyuRegistNo",
        "sensyuTourokuNo",
        "sensyuNo",
        "registNo",
    )

    for row in rows:
        found = None
        found_key = None

        if isinstance(row, dict):
            for key in candidate_keys:
                if key in row and row.get(key) not in (None, ""):
                    found = normalize_id(row.get(key))
                    found_key = key
                    break

            if found is None:
                for key, value in row.items():
                    lower = key.lower()
                    if (
                        ("regist" in lower or "touroku" in lower)
                        and value not in (None, "")
                    ):
                        found = normalize_id(value)
                        found_key = key
                        break

        if found is not None:
            ids.append(found)
            id_keys_found.append(found_key)

    return ids, id_keys_found

raw = load_json(INPUT_FILE)
captures = normalize_captures(raw)

print(f"181 capture数: {len(captures)}")
if not captures:
    raise RuntimeError("181 captureを認識できませんでした。")

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

verified = {}
failures = []
http_200_count = 0
json_count = 0
structure_count = 0
id_7_7_match_count = 0
id_compare_unavailable_count = 0

for i, capture in enumerate(captures, start=1):
    race_key = capture.get("race_key")
    target_ids = {
        normalize_id(x)
        for x in capture.get("target_player_ids", [])
        if normalize_id(x)
    }
    encp = extract_encp(capture.get("request_url"))

    print(f"[{i}/{len(captures)}] {race_key}")

    if not encp:
        print("  ❌ encpなし")
        failures.append({"race_key": race_key, "reason": "NO_ENCP"})
        continue

    try:
        response = session.get(
            "https://www.keirin.jp/pc/json",
            params={"encp": encp, "type": "JSJ012"},
            timeout=TIMEOUT,
        )

        if response.status_code == 200:
            http_200_count += 1
        else:
            print(f"  ❌ HTTP {response.status_code}")
            failures.append({
                "race_key": race_key,
                "reason": "HTTP_ERROR",
                "status_code": response.status_code,
            })
            continue

        try:
            data = response.json()
            json_count += 1
        except Exception as e:
            print(f"  ❌ JSON解析失敗: {repr(e)}")
            failures.append({
                "race_key": race_key,
                "reason": "JSON_ERROR",
                "error": repr(e),
            })
            continue

        finish_rows = data.get("tyakujyunItemSubData")
        payout_data = data.get("haraiGakuSubData")

        if not isinstance(finish_rows, list) or not isinstance(payout_data, dict):
            print("  ❌ JSJ012結果構造不足")
            failures.append({
                "race_key": race_key,
                "reason": "RESULT_STRUCTURE_MISSING",
                "top_level_keys": list(data.keys()) if isinstance(data, dict) else None,
            })
            continue

        structure_count += 1
        finish_ids, id_keys_found = extract_finish_ids(data)
        finish_id_set = set(finish_ids)

        if len(target_ids) == 7 and len(finish_id_set) == 7:
            if target_ids == finish_id_set:
                match_status = "7_OF_7_MATCH"
                id_7_7_match_count += 1
                print("  ✅ JSJ012取得 + 選手ID 7/7完全一致")
            else:
                match_status = "ID_MISMATCH"
                print("  ❌ 選手ID不一致")
        else:
            match_status = "ID_COMPARE_UNAVAILABLE"
            id_compare_unavailable_count += 1
            print(
                f"  ⚠ JSJ012取得成功 / ID比較保留 "
                f"(target={len(target_ids)}, finish={len(finish_id_set)})"
            )

        record = {
            "race_key": race_key,
            "venue": capture.get("venue"),
            "race_no": capture.get("race_no"),
            "encp": encp,
            "jsj012_request_url": response.url,
            "target_player_ids": sorted(target_ids),
            "jsj012_player_ids": sorted(finish_id_set),
            "jsj012_id_keys_found": id_keys_found,
            "match_status": match_status,
            "finish_order_count": len(finish_rows),
            "data": data,
        }

        if match_status == "ID_MISMATCH":
            failures.append({
                "race_key": race_key,
                "reason": "ID_MISMATCH",
                "target_player_ids": sorted(target_ids),
                "jsj012_player_ids": sorted(finish_id_set),
            })
        else:
            verified[race_key] = record

    except Exception as e:
        print(f"  ❌ REQUEST ERROR: {repr(e)}")
        failures.append({
            "race_key": race_key,
            "reason": "REQUEST_ERROR",
            "error": repr(e),
        })

    time.sleep(SLEEP_SEC)

output = {
    "source": str(INPUT_FILE),
    "capture_count": len(captures),
    "http_200_count": http_200_count,
    "json_count": json_count,
    "result_structure_count": structure_count,
    "id_7_7_match_count": id_7_7_match_count,
    "id_compare_unavailable_count": id_compare_unavailable_count,
    "verified_count": len(verified),
    "failure_count": len(failures),
    "failures": failures,
    "captures": verified,
}

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print()
print("=== 187 結果 ===")
print(f"対象レース数: {len(captures)}")
print(f"HTTP 200数: {http_200_count}")
print(f"JSON取得数: {json_count}")
print(f"JSJ012結果構造あり: {structure_count}")
print(f"選手ID 7/7完全一致: {id_7_7_match_count}")
print(f"ID比較保留: {id_compare_unavailable_count}")
print(f"保存レース数: {len(verified)}")
print(f"失敗数: {len(failures)}")

if failures:
    print()
    print("=== 失敗・不一致一覧 ===")
    for item in failures:
        print(f"{item.get('race_key')} -> {item.get('reason')}")

print()
print(f"保存完了: {OUTPUT_FILE}")
print("=== 187 完了 ===")
