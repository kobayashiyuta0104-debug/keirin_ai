import json
from pathlib import Path

print("=== 189 JSJ012確定結果統合・PENDING管理テスト ===")

BASE_DIR = Path(__file__).resolve().parent.parent
FILE_187 = BASE_DIR / "187_verified_jsj012_capture.json"
FILE_188 = BASE_DIR / "188_jsj012_retry_analysis.json"
OUTPUT_FILE = BASE_DIR / "189_jsj012_result_registry.json"

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

data187 = load_json(FILE_187)
data188 = load_json(FILE_188)

confirmed = {}

# 187で保存済みの7/7一致結果
captures187 = data187.get("captures", {})
if isinstance(captures187, dict):
    for race_key, record in captures187.items():
        if isinstance(record, dict):
            item = dict(record)
            item["result_status"] = "CONFIRMED"
            item["confirmed_source"] = "187"
            confirmed[race_key] = item

# 187の結果構造不足をPENDING候補にする
pending = {}
for failure in data187.get("failures", []):
    if failure.get("reason") == "RESULT_STRUCTURE_MISSING":
        race_key = failure.get("race_key")
        if race_key:
            pending[race_key] = {
                "race_key": race_key,
                "result_status": "PENDING",
                "pending_reason": "RESULT_STRUCTURE_MISSING",
                "last_checked_source": "187",
            }

# 188の再取得結果を反映
for record in data188.get("results", []):
    race_key = record.get("race_key")
    status = record.get("status")

    if not race_key:
        continue

    if status == "7_OF_7_MATCH":
        item = dict(record)
        item["result_status"] = "CONFIRMED"
        item["confirmed_source"] = "188"
        confirmed[race_key] = item
        pending.pop(race_key, None)

    else:
        pending[race_key] = {
            "race_key": race_key,
            "result_status": "PENDING",
            "pending_reason": status,
            "last_checked_source": "188",
            "top_level_keys": record.get("top_level_keys"),
            "finish_order_count": record.get("finish_order_count"),
            "has_haraiGakuSubData": record.get("has_haraiGakuSubData"),
            "encp": record.get("encp"),
            "target_player_ids": record.get("target_player_ids"),
            "data": record.get("data"),
        }

# race_key重複確認
confirmed_keys = set(confirmed.keys())
pending_keys = set(pending.keys())
overlap = sorted(confirmed_keys & pending_keys)

output = {
    "registry_version": "189",
    "confirmed_count": len(confirmed),
    "pending_count": len(pending),
    "confirmed_pending_overlap_count": len(overlap),
    "confirmed_pending_overlap": overlap,
    "confirmed": dict(sorted(confirmed.items())),
    "pending": dict(sorted(pending.items())),
}

with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print()
print("=== 189 結果 ===")
print(f"確定結果 CONFIRMED: {len(confirmed)}")
print(f"結果待ち PENDING: {len(pending)}")
print(f"CONFIRMED/PENDING重複: {len(overlap)}")

print()
print("=== PENDING一覧 ===")
if pending:
    for race_key, record in sorted(pending.items()):
        print(
            f"{race_key} -> {record.get('pending_reason')} "
            f"/ 最終確認:{record.get('last_checked_source')}"
        )
else:
    print("PENDINGなし")

if overlap:
    print()
    print("❌ 重複race_keyあり")
    for race_key in overlap:
        print(race_key)
else:
    print()
    print("✅ CONFIRMEDとPENDINGのrace_key重複なし")

print()
print(f"保存完了: {OUTPUT_FILE}")
print("=== 189 完了 ===")
