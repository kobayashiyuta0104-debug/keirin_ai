import json
import urllib.parse
from pathlib import Path

BASE = Path(r"C:\競輪AI")
SRC = BASE / "205_manual_historical_navigation_capture.json"
OUT = BASE / "206_encp_transition_analysis.json"

print("=== 206 入口encp -> レース用encp 変換地点解析 ===")

with open(SRC, "r", encoding="utf-8") as f:
    obj = json.load(f)

# 205の保存形式が多少違っても拾えるよう、全JSONを再帰走査
posts = []
json_requests = []
encp_hits = []

def walk(x, path="$"):
    if isinstance(x, dict):
        url = x.get("url") or x.get("URL") or x.get("request_url")
        method = str(x.get("method") or x.get("METHOD") or "").upper()
        post_data = (x.get("post") or x.get("POST") or x.get("post_data")
                     or x.get("postData") or x.get("request_post_data"))
        typ = x.get("type") or x.get("TYPE")

        if url:
            u = str(url)
            parsed = urllib.parse.urlparse(u)
            q = urllib.parse.parse_qs(parsed.query)
            encp = q.get("encp", [None])[0]
            kday = q.get("kday", [None])[0]
            qtype = q.get("type", [typ])[0]

            if method == "POST" or post_data:
                pd = str(post_data) if post_data is not None else ""
                pq = urllib.parse.parse_qs(pd)
                posts.append({
                    "path": path,
                    "method": method,
                    "url": u,
                    "post": pd,
                    "post_encp": pq.get("encp", [None])[0],
                    "disp": pq.get("disp", [None])[0],
                })

            if "/pc/json" in u:
                json_requests.append({
                    "path": path,
                    "method": method,
                    "url": u,
                    "type": qtype,
                    "encp": encp,
                    "kday": kday,
                })

        for k, v in x.items():
            lk = str(k).lower()
            if "encp" in lk:
                encp_hits.append({"path": f"{path}.{k}", "key": k, "value": v})
            walk(v, f"{path}.{k}")

    elif isinstance(x, list):
        for i, v in enumerate(x):
            walk(v, f"{path}[{i}]")

walk(obj)

post_encps = []
for p in posts:
    if p["post_encp"] and p["post_encp"] not in post_encps:
        post_encps.append(p["post_encp"])

json_encps = []
for r in json_requests:
    if r["encp"] and r["encp"] not in json_encps:
        json_encps.append(r["encp"])

print()
print("=== POST遷移 ===")
for i, p in enumerate(posts, 1):
    print(f"[{i}] {p['method']} {p['url']}")
    print(f"    post_encp: {p['post_encp']}")
    print(f"    disp: {p['disp']}")

print()
print("=== JSON側 encp ===")
for i, e in enumerate(json_encps, 1):
    types = sorted({str(r["type"]) for r in json_requests if r["encp"] == e})
    print(f"[{i}] {e}")
    print(f"    TYPES: {types}")

print()
print("=== ENCP比較 ===")
print(f"POST側ユニークencp数: {len(post_encps)}")
print(f"JSON側ユニークencp数: {len(json_encps)}")

pairs = []
for pe in post_encps:
    for je in json_encps:
        same = pe == je
        common_prefix = 0
        for a, b in zip(pe, je):
            if a != b:
                break
            common_prefix += 1
        pairs.append({
            "post_encp": pe,
            "json_encp": je,
            "same": same,
            "common_prefix_length": common_prefix,
            "post_length": len(pe),
            "json_length": len(je),
        })
        print(f"POST: {pe}")
        print(f"JSON: {je}")
        print(f"同一: {same}")
        print(f"共通prefix長: {common_prefix}")
        print(f"長さ: POST={len(pe)} / JSON={len(je)}")
        print("-" * 70)

print()
print("=== 全encpキー出現箇所 先頭50件 ===")
for h in encp_hits[:50]:
    print(f"{h['path']} -> {h['value']}")

result = {
    "source": str(SRC),
    "post_transitions": posts,
    "json_requests": json_requests,
    "post_unique_encps": post_encps,
    "json_unique_encps": json_encps,
    "encp_comparisons": pairs,
    "all_encp_key_hits": encp_hits,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print()
print("保存完了:", OUT)
print("=== 206 完了 ===")
