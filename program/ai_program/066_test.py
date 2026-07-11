import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from collections import Counter


print("=== 066 Edge不要 JSJ005ライン予想 直接自動取得本番テスト ===")


# ============================================================
# 基本設定
# ============================================================

BASE = Path(r"C:\競輪AI")

TARGET_DATE = "20260711"

OUT_DIR = (
    BASE
    / "data_official"
    / "line_predictions"
    / "066_jsj005_direct_lines"
)

OUT_FILE = (
    OUT_DIR
    / "066_jsj005_direct_lines.json"
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
# JSJ005 ichiからライン並び復元
# ============================================================

def reconstruct_main_lines(narabiyoso):

    if not isinstance(
        narabiyoso,
        dict,
    ):

        return [], []

    shaban_rows = narabiyoso.get(
        "shaban"
    )

    if not isinstance(
        shaban_rows,
        list,
    ):

        return [], []

    positions = []

    for row in shaban_rows:

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

    main_lines = []

    current_line = []

    previous_ichi = None

    for item in positions:

        ichi = item["ichi"]

        shaban = item["shaban"]

        if previous_ichi is None:

            current_line = [
                shaban
            ]

        elif ichi == previous_ichi + 1:

            current_line.append(
                shaban
            )

        else:

            if current_line:

                main_lines.append(
                    current_line
                )

            current_line = [
                shaban
            ]

        previous_ichi = ichi

    if current_line:

        main_lines.append(
            current_line
        )

    return main_lines, positions


# ============================================================
# JSJ005ライン情報抽出
# ============================================================

def extract_line_prediction(
    jsj005,
):

    if not isinstance(
        jsj005,
        dict,
    ):

        return {
            "status": "LINE_EMPTY",
            "prediction_type": None,
            "provider": None,
            "main_lines": [],
            "positions": [],
            "shaban": [],
        }

    narabiyoso = jsj005.get(
        "narabiyoso"
    )

    if not isinstance(
        narabiyoso,
        dict,
    ):

        return {
            "status": "LINE_EMPTY",
            "prediction_type": None,
            "provider": None,
            "main_lines": [],
            "positions": [],
            "shaban": [],
        }

    main_lines, positions = (
        reconstruct_main_lines(
            narabiyoso
        )
    )

    shaban_rows = narabiyoso.get(
        "shaban"
    )

    if not isinstance(
        shaban_rows,
        list,
    ):

        shaban_rows = []

    if not positions:

        status = "LINE_EMPTY"

    else:

        status = "LINE_FOUND"

    return {
        "status": status,
        "prediction_type": (
            narabiyoso.get(
                "lineKeitai"
            )
        ),
        "provider": (
            narabiyoso.get(
                "teikyo"
            )
        ),
        "main_lines": main_lines,
        "positions": positions,
        "shaban": shaban_rows,
    }


# ============================================================
# メイン
# ============================================================

def main():

    print()
    print("[1] JSJ057 当日開催探索")

    print(
        "TARGET DATE:",
        TARGET_DATE,
    )

    jsj057_response = get_json({
        "kday": TARGET_DATE,
        "type": "JSJ057",
    })

    if not jsj057_response["ok"]:

        print(
            "ERROR: JSJ057取得失敗"
        )

        print(
            jsj057_response["error"]
        )

        return

    jsj057 = jsj057_response[
        "data"
    ]

    if not isinstance(
        jsj057,
        dict,
    ):

        print(
            "ERROR: JSJ057 JSONなし"
        )

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
    print(
        "[2] JSJ001 → JSJ005 "
        "ライン直接取得開始"
    )

    print(
        "Edge:",
        "使用しません",
    )

    print(
        "Playwright:",
        "使用しません",
    )

    results = []

    problems = []

    status_counter = Counter()

    total_races = 0

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

            print(
                "STATUS: ENC_PRM_MISSING"
            )

            problems.append({
                "venue": venue_name,
                "problem": "ENC_PRM_MISSING",
            })

            continue

        jsj001_response = get_json({
            "encp": enc_prm,
            "type": "JSJ001",
        })

        if not jsj001_response["ok"]:

            print(
                "STATUS: JSJ001_FETCH_ERROR"
            )

            problems.append({
                "venue": venue_name,
                "problem": "JSJ001_FETCH_ERROR",
                "error": (
                    jsj001_response[
                        "error"
                    ]
                ),
            })

            continue

        jsj001 = jsj001_response[
            "data"
        ]

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

            print(
                "STATUS: C0201DATA_MISSING"
            )

            problems.append({
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
            c0201.get(
                "selKaisai"
            ),
        )

        print(
            "RACE COUNT:",
            len(races),
        )

        for race_index, race in enumerate(
            races,
            1,
        ):

            total_races += 1

            race_no = race_index

            race_key = (
                f"{TARGET_DATE}_"
                f"{venue_name}_"
                f"{race_no}R"
            )

            print()
            print(
                f"[{race_no}/{len(races)}] "
                f"{race_key}"
            )

            if not isinstance(
                race,
                dict,
            ):

                status = "RACE_DATA_INVALID"

                status_counter[
                    status
                ] += 1

                print(
                    "STATUS:",
                    status,
                )

                problems.append({
                    "race_key": race_key,
                    "problem": status,
                })

                continue

            enc_para_r = race.get(
                "encParaR"
            )

            if not enc_para_r:

                status = "ENC_PARA_R_MISSING"

                status_counter[
                    status
                ] += 1

                print(
                    "STATUS:",
                    status,
                )

                problems.append({
                    "race_key": race_key,
                    "problem": status,
                })

                continue

            jsj005_response = get_json({
                "encp": enc_para_r,
                "type": "JSJ005",
            })

            if not jsj005_response["ok"]:

                status = "FETCH_ERROR"

                status_counter[
                    status
                ] += 1

                print(
                    "STATUS:",
                    status,
                )

                print(
                    "ERROR:",
                    jsj005_response[
                        "error"
                    ],
                )

                results.append({
                    "race_key": race_key,
                    "target_date": TARGET_DATE,
                    "venue": venue_name,
                    "venue_code": venue_code,
                    "race_no": race_no,
                    "encParaR": enc_para_r,
                    "status": status,
                    "prediction_type": None,
                    "provider": None,
                    "main_lines": [],
                    "positions": [],
                    "fetch_error": (
                        jsj005_response[
                            "error"
                        ]
                    ),
                })

                continue

            jsj005 = jsj005_response[
                "data"
            ]

            line_prediction = (
                extract_line_prediction(
                    jsj005
                )
            )

            status = line_prediction[
                "status"
            ]

            status_counter[
                status
            ] += 1

            print(
                "STATUS:",
                status,
            )

            print(
                "HTTP:",
                jsj005_response[
                    "status"
                ],
            )

            print(
                "TYPE:",
                line_prediction[
                    "prediction_type"
                ],
            )

            print(
                "PROVIDER:",
                line_prediction[
                    "provider"
                ],
            )

            print(
                "MAIN LINES:",
                line_prediction[
                    "main_lines"
                ],
            )

            results.append({
                "race_key": race_key,
                "target_date": TARGET_DATE,
                "venue": venue_name,
                "venue_code": venue_code,
                "race_no": race_no,
                "encParaR": enc_para_r,
                "status": status,
                "prediction_type": (
                    line_prediction[
                        "prediction_type"
                    ]
                ),
                "provider": (
                    line_prediction[
                        "provider"
                    ]
                ),
                "main_lines": (
                    line_prediction[
                        "main_lines"
                    ]
                ),
                "positions": (
                    line_prediction[
                        "positions"
                    ]
                ),
                "shaban": (
                    line_prediction[
                        "shaban"
                    ]
                ),
                "http_status": (
                    jsj005_response[
                        "status"
                    ]
                ),
                "raw_length": (
                    jsj005_response[
                        "raw_length"
                    ]
                ),
                "fetch_error": (
                    jsj005_response[
                        "error"
                    ]
                ),
            })

            time.sleep(0.05)

    line_found_rows = [
        item
        for item in results
        if item.get("status")
        == "LINE_FOUND"
    ]

    line_empty_rows = [
        item
        for item in results
        if item.get("status")
        == "LINE_EMPTY"
    ]

    fetch_error_rows = [
        item
        for item in results
        if item.get("status")
        == "FETCH_ERROR"
    ]

    output = {
        "program": "066_test.py",
        "purpose": (
            "JSJ057から当日開催を探索し、"
            "JSJ001から全レースencParaRを取得。"
            "同じencParaRをJSJ005のencpとして使用し、"
            "Edge・Playwrightなしで"
            "ライン予想を直接自動取得する。"
        ),
        "target_date": TARGET_DATE,
        "edge_used": False,
        "playwright_used": False,
        "venue_count": len(venues),
        "total_race_count": total_races,
        "result_count": len(results),
        "line_found_count": len(
            line_found_rows
        ),
        "line_empty_count": len(
            line_empty_rows
        ),
        "fetch_error_count": len(
            fetch_error_rows
        ),
        "status_summary": dict(
            status_counter
        ),
        "problems": problems,
        "results": results,
    }

    save_json(
        OUT_FILE,
        output,
    )

    print()
    print("=" * 100)

    print(
        "066 最終結果"
    )

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
        "TOTAL RACES:",
        total_races,
    )

    print(
        "RESULT COUNT:",
        len(results),
    )

    print()
    print(
        "LINE FOUND:",
        len(line_found_rows),
    )

    print(
        "LINE EMPTY:",
        len(line_empty_rows),
    )

    print(
        "FETCH ERROR:",
        len(fetch_error_rows),
    )

    print()
    print(
        "★ STATUS SUMMARY ★"
    )

    for key, value in (
        status_counter.most_common()
    ):

        print(
            key,
            ":",
            value,
        )

    print()
    print(
        "★ LINE FOUND一覧 ★"
    )

    if not line_found_rows:

        print(
            "なし"
        )

    else:

        for item in line_found_rows:

            print()
            print(
                item["race_key"]
            )

            print(
                "TYPE:",
                item[
                    "prediction_type"
                ],
            )

            print(
                "PROVIDER:",
                item[
                    "provider"
                ],
            )

            print(
                "MAIN LINES:",
                item[
                    "main_lines"
                ],
            )

    print()
    print(
        "★ LINE EMPTY一覧 ★"
    )

    if not line_empty_rows:

        print(
            "なし"
        )

    else:

        for item in line_empty_rows:

            print(
                item["race_key"],
                "/ HTTP",
                item.get(
                    "http_status"
                ),
                "/ RAW",
                item.get(
                    "raw_length"
                ),
            )

    print()
    print(
        "★ FETCH ERROR一覧 ★"
    )

    if not fetch_error_rows:

        print(
            "なし"
        )

    else:

        for item in fetch_error_rows:

            print(
                item["race_key"],
                "/",
                item[
                    "fetch_error"
                ],
            )

    print()
    print(
        "保存先:"
    )

    print(
        OUT_FILE
    )

    print()
    print(
        "=== 066 完了 ==="
    )


if __name__ == "__main__":

    main()