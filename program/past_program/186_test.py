import json
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests

print("=== 186 JSJ006 encp -> JSJ012直接取得テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "181_verified_jsj006_capture.json"
OUTPUT_FILE = BASE_DIR / "186_jsj012_direct_test.json"

TEST_LIMIT = 10
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

def find_keys(obj, target_keys, path="$"):
    hits = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            child = f"{path}.{key}"
            if key in target_keys:
                hits.append({
                    "path": child,
                    "key": key,
                    "value": value,
                })
            hits.extend(find_keys(value, target_keys, child))
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            hits.extend(find_keys(value, target_keys, f"{path}[{i}]"))
    return hits

raw = load_json(INPUT_FILE)
captures = normalize_captures(raw)

print(f"181 capture数: {len(captures)}")
print(f"今回のテスト上限: {TEST_LIMIT}レース")
print()

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
success_count = 0
json_count = 0
result_structure_count = 0

targets = captures[:TEST_LIMIT]

for i, capture in enumerate(targets, start=1):
    race_key = capture.get("race_key")
    request_url = capture.get("request_url")
    encp = extract_encp(request_url)

    print(f"[{i}/{len(targets)}] {race_key}")

    record = {
        "race_key": race_key,
        "source_jsj006_url": request_url,
        "encp": encp,
    }

    if not encp:
        print("  ❌ encpなし")
        record["status"] = "NO_ENCP"
        results.append(record)
        continue

    url = "https://www.keirin.jp/pc/json"
    params = {
        "encp": encp,
        "type": "JSJ012",
    }

    try:
        response = session.get(url, params=params, timeout=TIMEOUT)

        record["requested_url"] = response.url
        record["status_code"] = response.status_code
        record["content_type"] = response.headers.get("content-type")
        record["text_length"] = len(response.text)
        record["text_head"] = response.text[:500]

        print(f"  HTTP: {response.status_code}")
        print(f"  文字数: {len(response.text)}")

        if response.status_code == 200:
            success_count += 1

        try:
            data = response.json()
            json_count += 1
            record["json_ok"] = True
            record["data"] = data

            top_keys = list(data.keys()) if isinstance(data, dict) else None
            record["top_level_keys"] = top_keys

            hits = find_keys(
                data,
                {
                    "tyakujyunItemSubData",
                    "haraiGakuSubData",
                    "RT3HaraiGakuDispItemSubData",
                },
            )
            record["result_structure_hits"] = [
                {
                    "path": hit["path"],
                    "key": hit["key"],
                    "value_type": type(hit["value"]).__name__,
                    "item_count": (
                        len(hit["value"])
                        if isinstance(hit["value"], (list, dict))
                        else None
                    ),
                }
                for hit in hits
            ]

            if hits:
                result_structure_count += 1
                record["status"] = "RESULT_STRUCTURE_FOUND"
                print("  🔥 JSJ012結果構造あり")
                for hit in record["result_structure_hits"][:10]:
                    print(
                        f"    {hit['path']} "
                        f"({hit['key']} / 件数:{hit['item_count']})"
                    )
            else:
                record["status"] = "JSON_BUT_NO_RESULT_STRUCTURE"
                print(f"  ⚠ JSON取得成功 / 結果構造なし / TOPキー: {top_keys}")

        except Exception as e:
            record["json_ok"] = False
            record["json_error"] = repr(e)
            record["status"] = "NOT_JSON"
            print(f"  ❌ JSON解析失敗: {repr(e)}")

    except Exception as e:
        record["status"] = "REQUEST_ERROR"
        record["request_error"] = repr(e)
        print(f"  ❌ REQUEST ERROR: {repr(e)}")

    results.append(record)
    print()
    time.sleep(SLEEP_SEC)

output = {
    "test_name": "JSJ006 encp reused with type=JSJ012",
    "input_capture_count": len(captures),
    "tested_count": len(targets),
    "http_200_count": success_count,
    "json_count": json_count,
    "result_structure_count": result_structure_count,
    "results": results,
}

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("=== 186 結果 ===")
print(f"テスト数: {len(targets)}")
print(f"HTTP 200数: {success_count}")
print(f"JSON取得数: {json_count}")
print(f"JSJ012結果構造あり: {result_structure_count}")
print(f"保存完了: {OUTPUT_FILE}")
print("=== 186 完了 ===")
