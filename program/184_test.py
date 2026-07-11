import json
from pathlib import Path
from collections import Counter, defaultdict
from urllib.parse import urlparse, parse_qs

print("=== 184 JSJ006レース固有パラメータ解析テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "181_verified_jsj006_capture.json"
OUTPUT_FILE = BASE_DIR / "184_jsj006_parameter_analysis.json"

KEYWORDS = [
    "encp",
    "encPrm",
    "kkrParameter",
    "kkParameter",
    "raceBasicURL",
    "race",
    "keirinjo",
    "joCode",
    "jocode",
    "kaisai",
    "date",
    "raceNo",
    "raceno",
    "race_no",
]

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def walk(obj, path="$"):
    if isinstance(obj, dict):
        for key, value in obj.items():
            child_path = f"{path}.{key}"
            yield child_path, key, value
            yield from walk(value, child_path)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            child_path = f"{path}[{i}]"
            yield from walk(value, child_path)

def keyword_hit(key, path):
    text = f"{key} {path}".lower()
    return any(word.lower() in text for word in KEYWORDS)

def short_value(value, limit=500):
    if isinstance(value, (dict, list)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value)
    if len(text) > limit:
        return text[:limit] + "...<truncated>"
    return text

def normalize_captures(raw):
    if isinstance(raw, list):
        return raw

    if isinstance(raw, dict):
        if "captures" in raw and isinstance(raw["captures"], list):
            return raw["captures"]

        captures = []
        for key, value in raw.items():
            if isinstance(value, dict):
                item = dict(value)
                item.setdefault("race_key", key)
                captures.append(item)
        return captures

    return []

raw = load_json(INPUT_FILE)
captures = normalize_captures(raw)

print(f"入力ファイル: {INPUT_FILE}")
print(f"解析対象capture数: {len(captures)}")

if not captures:
    raise RuntimeError("captureを1件も認識できませんでした。181 JSONの構造確認が必要です。")

records = []
path_values = defaultdict(list)
post_data_counter = Counter()
url_path_counter = Counter()

for index, capture in enumerate(captures, start=1):
    race_key = capture.get("race_key", f"UNKNOWN_{index}")
    request_url = capture.get("request_url")
    request_method = capture.get("request_method")
    request_post_data = capture.get("request_post_data")
    data = capture.get("data")

    url_info = {}
    if request_url:
        parsed = urlparse(request_url)
        url_info = {
            "scheme": parsed.scheme,
            "netloc": parsed.netloc,
            "path": parsed.path,
            "query": parse_qs(parsed.query, keep_blank_values=True),
        }
        url_path_counter[parsed.path] += 1

    if request_post_data is not None:
        post_data_counter[str(request_post_data)] += 1

    hits = []

    # capture全体を再帰探索
    for path, key, value in walk(capture):
        if keyword_hit(key, path):
            item = {
                "path": path,
                "key": key,
                "value": short_value(value),
                "value_type": type(value).__name__,
            }
            hits.append(item)
            path_values[path].append((race_key, short_value(value)))

    records.append({
        "race_key": race_key,
        "venue": capture.get("venue"),
        "race_no": capture.get("race_no"),
        "request_method": request_method,
        "request_url": request_url,
        "url_info": url_info,
        "request_post_data": request_post_data,
        "keyword_hits": hits,
        "top_level_keys": list(capture.keys()),
        "data_top_level_keys": list(data.keys()) if isinstance(data, dict) else None,
    })

# パスごとの変化数を集計
path_analysis = []
for path, values in path_values.items():
    unique_values = []
    seen = set()

    for race_key, value in values:
        marker = value
        if marker not in seen:
            seen.add(marker)
            unique_values.append({
                "race_key": race_key,
                "value": value,
            })

    path_analysis.append({
        "path": path,
        "occurrence_count": len(values),
        "unique_value_count": len(unique_values),
        "changes_by_race": len(unique_values) > 1,
        "sample_unique_values": unique_values[:20],
    })

path_analysis.sort(
    key=lambda x: (
        not x["changes_by_race"],
        -x["unique_value_count"],
        x["path"],
    )
)

changing_paths = [x for x in path_analysis if x["changes_by_race"]]
fixed_paths = [x for x in path_analysis if not x["changes_by_race"]]

result = {
    "input_file": str(INPUT_FILE),
    "capture_count": len(captures),
    "keyword_list": KEYWORDS,
    "summary": {
        "changing_candidate_path_count": len(changing_paths),
        "fixed_candidate_path_count": len(fixed_paths),
        "unique_request_post_data_count": len(post_data_counter),
        "request_url_path_counts": dict(url_path_counter),
    },
    "changing_candidate_paths": changing_paths,
    "fixed_candidate_paths": fixed_paths,
    "request_post_data_variations": [
        {
            "value": value,
            "count": count,
        }
        for value, count in post_data_counter.most_common()
    ],
    "records": records,
}

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print()
print("=== 解析結果 ===")
print(f"race_keyごとに値が変化する候補パス数: {len(changing_paths)}")
print(f"固定値候補パス数: {len(fixed_paths)}")
print(f"request_post_data種類数: {len(post_data_counter)}")
print()

print("=== race_keyごとに変化する重要候補 TOP30 ===")
for item in changing_paths[:30]:
    print(
        f"[変化 {item['unique_value_count']}種類 / 出現 {item['occurrence_count']}件] "
        f"{item['path']}"
    )
    for sample in item["sample_unique_values"][:3]:
        print(f"  {sample['race_key']} -> {sample['value']}")
    print()

print("=== request_post_data 種類 TOP10 ===")
for value, count in post_data_counter.most_common(10):
    display = value if len(value) <= 300 else value[:300] + "...<truncated>"
    print(f"件数 {count}: {display}")

print()
print(f"保存完了: {OUTPUT_FILE}")
print("=== 184 完了 ===")
