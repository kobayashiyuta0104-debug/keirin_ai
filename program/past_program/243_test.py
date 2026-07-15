import json
from pathlib import Path
from collections import Counter

SRC = Path(r"C:\競輪AI\242_20260705_06_model_ready_154_features.json")

print("=== 243 9車対応必要性検証 ===")

data = json.loads(SRC.read_text(encoding="utf-8"))

player_dist = Counter()
feature_dist = Counter()

need_expand = 0

for race in data:

    player_count = race.get("player_count", 0)
    player_dist[player_count] += 1

    features = race.get("features", {})

    slots = set()

    for key in features.keys():
        if key.startswith("p"):
            try:
                slot = int(key.split("_")[0][1:])
                slots.add(slot)
            except:
                pass

    feature_dist[max(slots) if slots else 0] += 1

    if player_count > max(slots):
        need_expand += 1

print()
print("=== 243 結果 ===")
print("対象レース:", len(data))
print("車立て分布:", dict(sorted(player_dist.items())))
print("特徴量最大スロット分布:", dict(sorted(feature_dist.items())))
print("9車対応拡張が必要なレース:", need_expand)

print()

if data:
    r = data[0]
    print("=== サンプル ===")
    print("race_key:", r["race_key"])
    print("player_count:", r["player_count"])
    print("特徴量数:", len(r["features"]))

    slots = sorted({
        int(k.split("_")[0][1:])
        for k in r["features"]
        if k.startswith("p")
    })

    print("存在スロット:", slots)

print("=== 243 完了 ===")