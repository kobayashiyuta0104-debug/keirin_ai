import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from collections import Counter


print("=== 064 20260711 JSJ005ライン直接取得確認テスト ===")


# ============================================================
# 基本設定
# ============================================================

BASE = Path(r"C:\競輪AI")

TARGET_DATE = "20260711"

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "064_jsj005_direct_live"
)

OUT_FILE = (
    OUT_DIR
    / "064_jsj005_direct_live.json"
)

BASE_URL = "https://www.keirin.jp/pc/json"

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# JSON保存
# ============================================================

def save_json(path, data):

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ============================================================
# KEIRIN.JP JSON直接取得
# ============================================================

def get_json(params):

    query = urllib.parse.urlencode(
        params
    )

    url = (
        BASE_URL
        + "?"
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
            timeout=30,
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
            "ok": True,
            "status": status,
            "url": url,
            "raw_length": len(raw),
            "data": data,
            "error": None,
        }

    except Exception as e:

        return {
            "ok": False,
            "status": None,
            "url": url,
            "raw_length": 0,
            "data": None,
            "error": repr(e),
        }


# ============================================================
# ichiから仮ライン復元
# ============================================================

def reconstruct_lines(narabiyoso):

    if not isinstance(
        narabiyoso,
        dict,
    ):

        return [], []

    rows = narabiyoso.get(
        "shaban"
    )

    if not isinstance(
        rows,
        list,
    ):

        return [], []

    positions = []

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):

            continue

        try:

            ichi = int(
                row.get("ichi")
            )

            shaban = int(
                row.get("shaban")
            )

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

            current = [
                shaban
            ]

        elif ichi == previous_ichi + 1:

            current.append(
                shaban
            )

        else:

            if current:

                lines.append(
                    current
                )

            current = [
                shaban
            ]

        previous_ichi = ichi

    if current:

        lines.append(
            current
        )

    return lines, positions


# ============================================================
# メイン
# ============================================================

def main():

    print()
    print("[1] JSJ057直接取得")
    print("TARGET DATE:", TARGET_DATE)

    jsj057_response = get_json({
        "kday": TARGET_DATE,
        "type": "JSJ057",
    })

    if not jsj057_response["ok"]:

        print("ERROR: JSJ057取得失敗")
        print(jsj057_response["error"])

        return

    jsj057 = jsj057_response["data"]

    if not isinstance(
        jsj057,
        dict,
    ):

        print("ERROR: JSJ057 JSONなし")

        return

    venues = jsj057.get(
        "kInfo"
    ) or []

    print(
        "JSJ057 HTTP:",
        jsj057_response["status"],
    )

    print(
        "VENUE COUNT:",
        len(venues),
    )

    print()
    print("[2] JSJ001から全レースencParaR探索")

    race_map = []

    map_problems = []

    for venue_index, venue in enumerate(
        venues,
        1,
    ):

        venue_name = venue.get(
            "jyoName"
        )

        venue_code = (
            venue.get("KeirinCd")
            or venue.get("bKeirinCd")
        )

        enc_prm = venue.get(
            "encPrm"
        )

        print()
        print("=" * 100)

        print(
            f"[会場 {venue_index}/{len(venues)}] "
            f"{venue_name} / code={venue_code}"
        )

        if not enc_prm:

            print("ENC_PRM_MISSING")

            map_problems.append({
                "venue": venue_name,
                "problem": "ENC_PRM_MISSING",
            })

            continue

        jsj001_response = get_json({
            "encp": enc_prm,
            "type": "JSJ001",
        })

        if not jsj001_response["ok"]:

            print("JSJ001 FETCH ERROR")

            map_problems.append({
                "venue": venue_name,
                "problem": "JSJ001_FETCH_ERROR",
                "error": jsj001_response["error"],
            })

            continue

        jsj001 = jsj001_response["data"]

        c0201 = None

        if isinstance(
            jsj001,
            dict,
        ):

            c0201 = jsj001.get(
                "C0201data"
            )

        if not isinstance(
            c0201,
            dict,
        ):

            print("C0201dataなし")

            map_problems.append({
                "venue": venue_name,
                "problem": "C0201DATA_MISSING",
            })

            continue

        races = c0201.get(
            "C0201race"
        ) or []

        print(
            "JSJ001 HTTP:",
            jsj001_response["status"],
        )

        print(
            "selKaisai:",
            c0201.get("selKaisai"),
        )

        print(
            "RACE COUNT:",
            len(races),
        )

        for race_index, race in enumerate(
            races,
            1,
        ):

            if not isinstance(
                race,
                dict,
            ):

                continue

            enc_para_r = race.get(
                "encParaR"
            )

            race_no = race_index

            race_key = (
                f"{TARGET_DATE}_"
                f"{venue_name}_"
                f"{race_no}R"
            )

            if not enc_para_r:

                print(
                    race_key,
                    ": ENC_PARA_R_MISSING",
                )

                map_problems.append({
                    "race_key": race_key,
                    "problem": "ENC_PARA_R_MISSING",
                })

                continue

            race_map.append({
                "race_key": race_key,
                "venue": venue_name,
                "venue_code": venue_code,
                "race_no": race_no,
                "encp": enc_para_r,
                "encParaR": enc_para_r,
                "jsj001_race": race,
            })

        time.sleep(0.05)

    print()
    print(
        "TOTAL RACE + ENCP:",
        len(race_map),
    )

    if not race_map:

        print(
            "ERROR: race_key + encParaRを取得できません"
        )

        return

    print()
    print("[3] 全レースJSJ005直接取得開始")

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

    for index, race_item in enumerate(
        race_map,
        1,
    ):

        race_key = race_item[
            "race_key"
        ]

        encp = race_item[
            "encp"
        ]

        print()
        print("-" * 100)

        print(
            f"[{index}/{len(race_map)}] "
            f"{race_key}"
        )

        response = get_json({
            "encp": encp,
            "type": "JSJ005",
        })

        data = response.get(
            "data"
        )

        narabiyoso = None

        if isinstance(
            data,
            dict,
        ):

            narabiyoso = data.get(
                "narabiyoso"
            )

        line_type = None

        provider = None

        positions = []

        main_lines = []

        shaban_raw = []

        if isinstance(
            narabiyoso,
            dict,
        ):

            line_type = narabiyoso.get(
                "lineKeitai"
            )

            provider = narabiyoso.get(
                "teikyo"
            )

            raw_rows = narabiyoso.get(
                "shaban"
            )

            if isinstance(
                raw_rows,
                list,
            ):

                shaban_raw = raw_rows

            main_lines, positions = (
                reconstruct_lines(
                    narabiyoso
                )
            )

        if response.get("error"):

            status = "FETCH_ERROR"

        elif not isinstance(
            data,
            dict,
        ):

            status = "JSJ005_EMPTY"

        elif not isinstance(
            narabiyoso,
            dict,
        ):

            status = "JSJ005_EMPTY"

        elif not positions:

            status = "JSJ005_EMPTY"

        else:

            status = "JSJ005_DIRECT_FOUND"

        status_counter[
            status
        ] += 1

        print(
            "STATUS:",
            status,
        )

        print(
            "HTTP:",
            response.get("status"),
        )

        print(
            "NARABIYOSO:",
            isinstance(
                narabiyoso,
                dict,
            ),
        )

        print(
            "TYPE:",
            line_type,
        )

        print(
            "PROVIDER:",
            provider,
        )

        print(
            "SHABAN:",
            shaban_raw,
        )

        print(
            "ICHI:",
            positions,
        )

        print(
            "MAIN LINES:",
            main_lines,
        )

        results.append({
            "race_key": race_key,
            "venue": race_item["venue"],
            "venue_code": race_item[
                "venue_code"
            ],
            "race_no": race_item[
                "race_no"
            ],
            "encp": encp,
            "encParaR": encp,
            "status": status,
            "http_status": response.get(
                "status"
            ),
            "jsj005_url": response.get(
                "url"
            ),
            "raw_length": response.get(
                "raw_length"
            ),
            "fetch_error": response.get(
                "error"
            ),
            "narabiyoso_exists": isinstance(
                narabiyoso,
                dict,
            ),
            "lineKeitai": line_type,
            "teikyo": provider,
            "shaban": shaban_raw,
            "ichi": positions,
            "main_lines": main_lines,
            "jsj005": data,
        })

        time.sleep(0.05)

    output = {
        "program": "064_test.py",
        "purpose": (
            "20260711の全開催・全レースを"
            "JSJ057→JSJ001で直接探索し、"
            "レース固有encParaRをそのまま"
            "JSJ005のencpへ使用して、"
            "Edge・Playwrightなしで"
            "現役ライン予想を直接取得できるか確認する。"
        ),
        "target_date": TARGET_DATE,
        "edge_used": False,
        "playwright_used": False,
        "venue_count": len(venues),
        "race_encp_count": len(race_map),
        "status_summary": dict(
            status_counter
        ),
        "map_problems": map_problems,
        "results": results,
    }

    save_json(
        OUT_FILE,
        output,
    )

    print()
    print("=" * 100)
    print("064 最終結果")
    print("=" * 100)

    print()
    print(
        "TARGET DATE:",
        TARGET_DATE,
    )

    print(
        "VENUE COUNT:",
        len(venues),
    )

    print(
        "RACE + ENCP:",
        len(race_map),
    )

    print()
    print("★ STATUS SUMMARY ★")

    for key, value in (
        status_counter.most_common()
    ):

        print(
            key,
            ":",
            value,
        )

    found_rows = [
        item
        for item in results
        if item["status"]
        == "JSJ005_DIRECT_FOUND"
    ]

    empty_rows = [
        item
        for item in results
        if item["status"]
        == "JSJ005_EMPTY"
    ]

    error_rows = [
        item
        for item in results
        if item["status"]
        == "FETCH_ERROR"
    ]

    print()
    print(
        "JSJ005 DIRECT FOUND:",
        len(found_rows),
    )

    print(
        "JSJ005 EMPTY:",
        len(empty_rows),
    )

    print(
        "FETCH ERROR:",
        len(error_rows),
    )

    print()
    print("★ JSJ005 DIRECT FOUND一覧 ★")

    if not found_rows:

        print("なし")

    else:

        for item in found_rows:

            print()
            print(
                item["race_key"]
            )

            print(
                "TYPE:",
                item["lineKeitai"],
            )

            print(
                "PROVIDER:",
                item["teikyo"],
            )

            print(
                "ICHI:",
                item["ichi"],
            )

            print(
                "MAIN LINES:",
                item["main_lines"],
            )

    print()
    print("★ JSJ005 EMPTY一覧 ★")

    if not empty_rows:

        print("なし")

    else:

        for item in empty_rows:

            print(
                item["race_key"],
                "/ HTTP",
                item["http_status"],
                "/ RAW",
                item["raw_length"],
            )

    print()
    print("★ FETCH ERROR一覧 ★")

    if not error_rows:

        print("なし")

    else:

        for item in error_rows:

            print(
                item["race_key"],
                "/",
                item["fetch_error"],
            )

    print()
    print("保存先:")
    print(
        OUT_FILE
    )

    print()
    print("=== 064 完了 ===")


if __name__ == "__main__":

    main()