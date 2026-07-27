import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from collections import Counter

print("=== 063 JSJ005直接取得 × 正式ライン自動照合テスト ===")

BASE = Path(r"C:\競輪AI")

ABILITY_FILE = (
    BASE
    / "data_official"
    / "pre_race"
    / "046_jsj006_by_race_key"
    / "046_jsj006_by_race_key.json"
)

LINE_FILE = (
    BASE
    / "data_official"
    / "line_predictions"
    / "043_all_venues_official_lines.json"
)

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "063_jsj005_direct_line_compare"
)

OUT_FILE = OUT_DIR / "063_jsj005_direct_line_compare.json"

TARGET_DATE = "20260710"

OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


def walk(obj):
    yield obj

    if isinstance(obj, dict):
        for value in obj.values():
            yield from walk(value)

    elif isinstance(obj, list):
        for value in obj:
            yield from walk(value)


def find_race_key(obj):
    if not isinstance(obj, dict):
        return None

    race_key = obj.get("race_key")

    if isinstance(race_key, str):
        if re.fullmatch(
            r"20\d{6}_.+_\d+R",
            race_key,
        ):
            return race_key

    return None


def extract_encp_from_url(url):
    if not isinstance(url, str):
        return None

    try:
        parsed = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(
            parsed.query,
            keep_blank_values=True,
        )

        values = query.get("encp") or []

        if values:
            return values[0]

    except Exception:
        pass

    return None


def find_encp(obj):
    if not isinstance(obj, dict):
        return None

    direct_keys = [
        "encParaR",
        "race_encParaR",
        "enc_para_r",
        "encp",
    ]

    for key in direct_keys:
        value = obj.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

    url_keys = [
        "url",
        "request_url",
        "jsj006_url",
        "URL",
    ]

    for key in url_keys:
        value = obj.get(key)
        encp = extract_encp_from_url(value)

        if encp:
            return encp

    for value in obj.values():
        if isinstance(value, str):
            encp = extract_encp_from_url(value)

            if encp:
                return encp

    return None


def collect_race_encp(root):
    result = {}

    # まずrace_keyを持つ辞書単位で探す
    for obj in walk(root):
        if not isinstance(obj, dict):
            continue

        race_key = find_race_key(obj)

        if not race_key:
            continue

        if not race_key.startswith(TARGET_DATE + "_"):
            continue

        encp = find_encp(obj)

        if encp:
            result[race_key] = encp

    # race_keyがdictキーになっている形式も拾う
    for obj in walk(root):
        if not isinstance(obj, dict):
            continue

        for key, value in obj.items():
            if not isinstance(key, str):
                continue

            if not re.fullmatch(
                r"20\d{6}_.+_\d+R",
                key,
            ):
                continue

            if not key.startswith(TARGET_DATE + "_"):
                continue

            if isinstance(value, dict):
                encp = find_encp(value)

                if encp:
                    result[key] = encp

    return result


def normalize_lines(lines):
    result = []

    if not isinstance(lines, list):
        return result

    for line in lines:
        if not isinstance(line, list):
            continue

        nums = []

        for value in line:
            try:
                num = int(value)
            except Exception:
                continue

            if 1 <= num <= 9:
                nums.append(num)

        if nums:
            result.append(nums)

    return result


def collect_official_lines(root):
    result = {}

    for obj in walk(root):
        if not isinstance(obj, dict):
            continue

        race_key = find_race_key(obj)

        if not race_key:
            continue

        if not race_key.startswith(TARGET_DATE + "_"):
            continue

        if "main_lines" not in obj:
            continue

        result[race_key] = {
            "status": obj.get("status"),
            "prediction_type": obj.get(
                "prediction_type"
            ),
            "provider": obj.get("provider"),
            "main_lines": normalize_lines(
                obj.get("main_lines")
            ),
            "has_competition": obj.get(
                "has_competition",
                False,
            ),
            "competition_rows": obj.get(
                "competition_rows",
                [],
            ),
        }

    return result


def get_json(encp, typ):
    query = urllib.parse.urlencode({
        "encp": encp,
        "type": typ,
    })

    url = (
        "https://www.keirin.jp/pc/json?"
        + query
    )

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/142.0.0.0 Safari/537.36"
            ),
            "Referer": (
                "https://www.keirin.jp/pc/racelive"
            ),
            "Accept": (
                "application/json, text/javascript, "
                "*/*; q=0.01"
            ),
            "X-Requested-With": "XMLHttpRequest",
        },
    )

    try:
        with urllib.request.urlopen(
            req,
            timeout=20,
        ) as response:
            raw = response.read().decode(
                "utf-8",
                errors="replace",
            )

            status = response.status

        try:
            data = json.loads(raw)
        except Exception:
            data = None

        return {
            "status": status,
            "url": url,
            "raw_length": len(raw),
            "data": data,
            "error": None,
        }

    except Exception as e:
        return {
            "status": None,
            "url": url,
            "raw_length": 0,
            "data": None,
            "error": repr(e),
        }


def reconstruct_lines(narabiyoso):
    """
    JSJ005 narabiyoso.shaban の ichi を昇順に並べる。

    062で確認した構造:
      ichi=1,2  -> 同一ライン
      ichi=4    -> 次ライン
      ichi=5    -> 次ライン
      ichi=7    -> 次ライン
      ichi=9    -> 次ライン
      ichi=11   -> 次ライン

    つまり ichi が連続している車番は同一ライン、
    1以上空いたら次ラインとして復元する。
    """

    if not isinstance(narabiyoso, dict):
        return [], []

    rows = narabiyoso.get("shaban")

    if not isinstance(rows, list):
        return [], []

    positions = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        try:
            ichi = int(row.get("ichi"))
            shaban = int(row.get("shaban"))
        except Exception:
            continue

        if ichi < 1:
            continue

        if not 1 <= shaban <= 9:
            continue

        positions.append({
            "ichi": ichi,
            "shaban": shaban,
        })

    positions.sort(
        key=lambda x: (
            x["ichi"],
            x["shaban"],
        )
    )

    lines = []
    current = []
    previous_ichi = None

    for item in positions:
        ichi = item["ichi"]
        shaban = item["shaban"]

        if previous_ichi is None:
            current = [shaban]

        elif ichi == previous_ichi + 1:
            current.append(shaban)

        else:
            if current:
                lines.append(current)

            current = [shaban]

        previous_ichi = ichi

    if current:
        lines.append(current)

    return lines, positions


def main():
    print()
    print("[1] 完成済み046から race_key + encp 読込")

    if not ABILITY_FILE.exists():
        print("ERROR: 046ファイルなし")
        print(ABILITY_FILE)
        return

    ability_root = load_json(ABILITY_FILE)

    race_encp = collect_race_encp(
        ability_root
    )

    print("RACE + ENCP:", len(race_encp))

    if not race_encp:
        print("ERROR: race_key + encp を取得できません")
        return

    print()
    print("[2] 043正式ライン読込")

    if not LINE_FILE.exists():
        print("ERROR: 043正式ラインファイルなし")
        print(LINE_FILE)
        return

    line_root = load_json(LINE_FILE)

    official_lines = collect_official_lines(
        line_root
    )

    print(
        "OFFICIAL LINE RACES:",
        len(official_lines),
    )

    print()
    print("[3] JSJ005直接取得開始")
    print(
        "Edge:",
        "使用しません",
    )
    print(
        "Playwright:",
        "使用しません",
    )

    results = []

    status_counter = Counter()
    type_match_counter = Counter()
    provider_match_counter = Counter()

    target_keys = sorted(
        set(race_encp.keys())
        & set(official_lines.keys())
    )

    print("COMPARE TARGET:", len(target_keys))

    for index, race_key in enumerate(
        target_keys,
        1,
    ):
        encp = race_encp[race_key]
        official = official_lines[race_key]

        print()
        print("-" * 100)
        print(
            f"[{index}/{len(target_keys)}] "
            f"{race_key}"
        )

        response = get_json(
            encp,
            "JSJ005",
        )

        data = response.get("data")

        narabiyoso = None

        if isinstance(data, dict):
            narabiyoso = data.get(
                "narabiyoso"
            )

        direct_type = None
        direct_provider = None
        direct_lines = []
        positions = []

        if isinstance(narabiyoso, dict):
            direct_type = narabiyoso.get(
                "lineKeitai"
            )

            direct_provider = narabiyoso.get(
                "teikyo"
            )

            direct_lines, positions = (
                reconstruct_lines(
                    narabiyoso
                )
            )

        official_main = normalize_lines(
            official.get("main_lines")
        )

        line_exact = (
            direct_lines
            == official_main
        )

        type_match = (
            direct_type
            == official.get(
                "prediction_type"
            )
        )

        provider_match = (
            direct_provider
            == official.get(
                "provider"
            )
        )

        if response.get("error"):
            status = "FETCH_ERROR"

        elif not isinstance(data, dict):
            status = "JSON_NOT_FOUND"

        elif not isinstance(
            narabiyoso,
            dict,
        ):
            status = "NARABIYOSO_NOT_FOUND"

        elif not direct_lines:
            status = "DIRECT_LINE_EMPTY"

        elif line_exact:
            status = "EXACT_MATCH"

        else:
            status = "LINE_MISMATCH"

        status_counter[status] += 1

        type_match_counter[
            str(type_match)
        ] += 1

        provider_match_counter[
            str(provider_match)
        ] += 1

        print("STATUS:", status)
        print("HTTP:", response.get("status"))
        print("TYPE:", direct_type)
        print("PROVIDER:", direct_provider)
        print("ICHI:", positions)
        print("DIRECT:", direct_lines)
        print("043:", official_main)
        print("LINE EXACT:", line_exact)
        print("TYPE MATCH:", type_match)
        print(
            "PROVIDER MATCH:",
            provider_match,
        )

        results.append({
            "race_key": race_key,
            "encp": encp,
            "status": status,
            "jsj005_url": response.get("url"),
            "http_status": response.get(
                "status"
            ),
            "raw_length": response.get(
                "raw_length"
            ),
            "fetch_error": response.get(
                "error"
            ),
            "direct": {
                "prediction_type": direct_type,
                "provider": direct_provider,
                "positions": positions,
                "main_lines": direct_lines,
            },
            "official_043": official,
            "comparison": {
                "line_exact_match": line_exact,
                "type_match": type_match,
                "provider_match": provider_match,
            },
            "jsj005": data,
        })

        time.sleep(0.05)

    exact_count = status_counter[
        "EXACT_MATCH"
    ]

    mismatch_count = status_counter[
        "LINE_MISMATCH"
    ]

    direct_success = sum(
        1
        for item in results
        if item["status"]
        in {
            "EXACT_MATCH",
            "LINE_MISMATCH",
        }
    )

    output = {
        "program": "063_test.py",
        "purpose": (
            "完成済み046のencpをそのままJSJ005へ使用し、"
            "Edgeなしでラインを直接取得。"
            "ichi連続位置からラインを復元し、"
            "043正式ラインと全レース自動照合する。"
        ),
        "target_date": TARGET_DATE,
        "ability_source": str(
            ABILITY_FILE
        ),
        "official_line_source": str(
            LINE_FILE
        ),
        "race_encp_count": len(
            race_encp
        ),
        "official_line_count": len(
            official_lines
        ),
        "compare_target_count": len(
            target_keys
        ),
        "direct_success_count": (
            direct_success
        ),
        "exact_match_count": exact_count,
        "line_mismatch_count": (
            mismatch_count
        ),
        "status_summary": dict(
            status_counter
        ),
        "type_match_summary": dict(
            type_match_counter
        ),
        "provider_match_summary": dict(
            provider_match_counter
        ),
        "results": results,
    }

    save_json(
        OUT_FILE,
        output,
    )

    print()
    print("=" * 100)
    print("063 最終結果")
    print("=" * 100)
    print()
    print("TARGET DATE:", TARGET_DATE)
    print(
        "RACE + ENCP:",
        len(race_encp),
    )
    print(
        "043 LINE RACES:",
        len(official_lines),
    )
    print(
        "COMPARE TARGET:",
        len(target_keys),
    )
    print(
        "JSJ005 DIRECT SUCCESS:",
        direct_success,
    )
    print(
        "EXACT MATCH:",
        exact_count,
    )
    print(
        "LINE MISMATCH:",
        mismatch_count,
    )

    print()
    print("★ STATUS SUMMARY ★")

    for key, value in (
        status_counter.most_common()
    ):
        print(key, ":", value)

    print()
    print("★ TYPE MATCH ★")

    for key, value in (
        type_match_counter.most_common()
    ):
        print(key, ":", value)

    print()
    print("★ PROVIDER MATCH ★")

    for key, value in (
        provider_match_counter.most_common()
    ):
        print(key, ":", value)

    print()
    print("★ LINE MISMATCH ★")

    mismatch_rows = [
        item
        for item in results
        if item["status"]
        == "LINE_MISMATCH"
    ]

    if not mismatch_rows:
        print("なし")

    else:
        for item in mismatch_rows[:50]:
            print()
            print(item["race_key"])
            print(
                "TYPE:",
                item["direct"][
                    "prediction_type"
                ],
            )
            print(
                "ICHI:",
                item["direct"][
                    "positions"
                ],
            )
            print(
                "DIRECT:",
                item["direct"][
                    "main_lines"
                ],
            )
            print(
                "043:",
                item["official_043"][
                    "main_lines"
                ],
            )
            print(
                "COMPETITION:",
                item["official_043"].get(
                    "has_competition"
                ),
            )

    print()
    print("★ DIRECT ERROR / EMPTY ★")

    error_rows = [
        item
        for item in results
        if item["status"]
        not in {
            "EXACT_MATCH",
            "LINE_MISMATCH",
        }
    ]

    if not error_rows:
        print("なし")

    else:
        for item in error_rows[:50]:
            print(
                item["race_key"],
                ":",
                item["status"],
                "/ HTTP",
                item["http_status"],
                "/",
                item["fetch_error"],
            )

    print()
    print("保存先:")
    print(OUT_FILE)
    print()
    print("=== 063 完了 ===")


if __name__ == "__main__":
    main()
