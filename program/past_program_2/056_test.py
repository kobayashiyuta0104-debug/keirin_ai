import json
import time
from pathlib import Path
from collections import Counter
import requests


# ============================================================
# 056
# 239成功方式そのまま
# 20260710 全会場・全レース JSJ012確定結果取得
# ============================================================


BASE = Path(r"C:\競輪AI")

TARGET_DATE = "20260710"

OUT_DIR = (
    BASE
    / "data_official"
    / "confirmed_results"
    / "056_jsj012_confirmed_results"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_FILE = (
    OUT_DIR
    / "056_jsj012_confirmed_results.json"
)


print(
    "=== 056 239方式 "
    "20260710 全会場JSJ012確定結果取得 ==="
)


# ============================================================
# SESSION
# ============================================================


session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.keirin.jp/pc/top",
})


# ============================================================
# JSON取得
# ============================================================


def get_json(url, retry=3):

    last_error = None

    for attempt in range(
        1,
        retry + 1,
    ):

        try:

            response = session.get(
                url,
                timeout=30,
            )

            response.raise_for_status()

            return (
                response.json(),
                response.status_code,
                len(response.text),
            )

        except Exception as e:

            last_error = repr(e)

            if attempt < retry:

                time.sleep(1)

    raise RuntimeError(
        last_error
    )


# ============================================================
# 数値変換
# ============================================================


def to_int(value):

    if value in (
        None,
        "",
    ):

        return None

    try:

        return int(
            float(
                str(value)
                .replace(",", "")
                .strip()
            )
        )

    except Exception:

        return None


def money_to_int(value):

    if value in (
        None,
        "",
    ):

        return None

    try:

        return int(
            str(value)
            .replace(",", "")
            .strip()
        )

    except Exception:

        return None


# ============================================================
# 着順解析
# ============================================================


def parse_finish_results(jsj012):

    rows = jsj012.get(
        "tyakujyunItemSubData"
    )

    if not isinstance(
        rows,
        list,
    ):

        rows = []

    results = []

    for row in rows:

        if not isinstance(
            row,
            dict,
        ):

            continue

        car_no = to_int(
            row.get("syaban")
        )

        finish_rank = to_int(
            row.get("tyakujyun")
        )

        player_id = str(
            row.get(
                "sensyuRegistNo",
                "",
            )
        ).zfill(6)

        status = "NORMAL"

        text = (
            str(
                row.get(
                    "kikaku",
                    "",
                )
            )
            +
            str(
                row.get(
                    "jyoutai",
                    "",
                )
            )
            +
            str(
                row.get(
                    "tyakusa",
                    "",
                )
            )
        )

        if "落" in text:

            status = "落車"

        elif "失" in text:

            status = "失格"

        elif "棄" in text:

            status = "棄権"

        elif "欠" in text:

            status = "欠場"

        results.append({
            "car_no": car_no,
            "player_id": player_id,
            "finish_rank": finish_rank,
            "result_status": status,
        })

    results.sort(
        key=lambda x: (
            x["finish_rank"]
            if x["finish_rank"] is not None
            else 999
        )
    )

    return results


# ============================================================
# 3連単解析
# ============================================================


def parse_trifecta(jsj012):

    harai = jsj012.get(
        "haraiGakuSubData"
    )

    if not isinstance(
        harai,
        dict,
    ):

        return {
            "combination": None,
            "payout": None,
            "popularity": None,
        }

    items = harai.get(
        "RT3HaraiGakuDispItemSubData"
    )

    if not isinstance(
        items,
        list,
    ):

        items = []

    for item in items:

        if not isinstance(
            item,
            dict,
        ):

            continue

        combination = item.get(
            "kumiBan"
        )

        payout = money_to_int(
            item.get("haraiGaku")
        )

        if (
            combination
            and payout is not None
        ):

            return {
                "combination": combination,
                "payout": payout,
                "popularity": item.get(
                    "ninki"
                ),
            }

    return {
        "combination": None,
        "payout": None,
        "popularity": None,
    }


# ============================================================
# MAIN
# ============================================================


def main():

    problems = []

    all_results = []

    venue_counter = Counter()

    status_counter = Counter()

    confirmed_count = 0

    total_races = 0


    # ========================================================
    # JSJ057
    # ========================================================


    print()

    print(
        "TARGET DATE:",
        TARGET_DATE
    )

    print()

    url057 = (
        "https://www.keirin.jp/pc/json"
        f"?kday={TARGET_DATE}"
        "&type=JSJ057"
    )

    try:

        jsj057, status057, len057 = (
            get_json(url057)
        )

    except Exception as e:

        raise RuntimeError(
            "JSJ057取得失敗: "
            + repr(e)
        )


    kinfo = jsj057.get(
        "kInfo"
    ) or []


    print(
        "JSJ057 HTTP:",
        status057
    )

    print(
        "開催会場数:",
        len(kinfo)
    )


    # ========================================================
    # VENUE
    # ========================================================


    for vi, venue in enumerate(
        kinfo,
        1,
    ):

        venue_name = venue.get(
            "jyoName"
        )

        venue_code = venue.get(
            "KeirinCd"
        )

        enc_prm = venue.get(
            "encPrm"
        )


        print()

        print(
            "=" * 100
        )

        print(
            f"[会場 {vi}/{len(kinfo)}] "
            f"{venue_name} "
            f"/ code={venue_code}"
        )


        if not enc_prm:

            print(
                "  ❌ encPrmなし"
            )

            problems.append({
                "venue": venue_name,
                "problem": "ENC_PRM_MISSING",
            })

            continue


        # ====================================================
        # JSJ001
        # 239成功方式
        # ====================================================


        url001 = (
            "https://www.keirin.jp/pc/json"
            f"?encp={enc_prm}"
            "&type=JSJ001"
        )


        try:

            jsj001, status001, len001 = (
                get_json(url001)
            )

        except Exception as e:

            print(
                "  ❌ JSJ001取得失敗:",
                repr(e)
            )

            problems.append({
                "venue": venue_name,
                "problem": "JSJ001_FETCH_ERROR",
                "error": repr(e),
            })

            continue


        c0201 = (
            jsj001.get("C0201data")
            if isinstance(
                jsj001,
                dict,
            )
            else None
        )


        races = (
            c0201.get("C0201race")
            or []
            if isinstance(
                c0201,
                dict,
            )
            else []
        )


        selected_date = (
            c0201.get("selKaisai")
            if isinstance(
                c0201,
                dict,
            )
            else None
        )


        print(
            "  JSJ001 HTTP:",
            status001
        )

        print(
            "  selKaisai:",
            selected_date
        )

        print(
            "  レース地図件数:",
            len(races)
        )


        # ====================================================
        # RACE
        # ====================================================


        for race_index, race_meta in enumerate(
            races,
            1,
        ):

            race_no = race_index

            race_key = (
                f"{TARGET_DATE}_"
                f"{venue_name}_"
                f"{race_no}R"
            )


            enc_para_r = (
                race_meta.get("encParaR")
                if isinstance(
                    race_meta,
                    dict,
                )
                else None
            )


            total_races += 1

            venue_counter[
                venue_name
            ] += 1


            if not enc_para_r:

                print(
                    f"  [{race_no}/{len(races)}] "
                    f"{race_key} "
                    "❌ encParaRなし"
                )

                status_counter[
                    "ENC_PARA_R_MISSING"
                ] += 1

                problems.append({
                    "race_key": race_key,
                    "problem": "ENC_PARA_R_MISSING",
                })

                continue


            # =================================================
            # JSJ012
            # 239成功方式
            # =================================================


            url012 = (
                "https://www.keirin.jp/pc/json"
                f"?encp={enc_para_r}"
                "&type=JSJ012"
            )


            try:

                jsj012, status012, len012 = (
                    get_json(url012)
                )

            except Exception as e:

                print(
                    f"  [{race_no}/{len(races)}] "
                    f"{race_key} "
                    "❌ JSJ012取得失敗"
                )

                status_counter[
                    "JSJ012_FETCH_ERROR"
                ] += 1

                problems.append({
                    "race_key": race_key,
                    "problem": "JSJ012_FETCH_ERROR",
                    "error": repr(e),
                })

                continue


            finish_rows = jsj012.get(
                "tyakujyunItemSubData"
            ) or []


            trifecta = parse_trifecta(
                jsj012
            )


            is_confirmed = (
                isinstance(
                    finish_rows,
                    list,
                )
                and len(finish_rows) > 0
                and trifecta[
                    "payout"
                ] is not None
            )


            if is_confirmed:

                confirmed_count += 1

                status = (
                    "CONFIRMED_RESULT_FOUND"
                )

                mark = "✅"

            else:

                status = (
                    "RESULT_NOT_CONFIRMED"
                )

                mark = "❌"


            status_counter[
                status
            ] += 1


            parsed_results = (
                parse_finish_results(
                    jsj012
                )
            )


            item = {
                "race_key": race_key,
                "race_date": TARGET_DATE,
                "venue": venue_name,
                "venue_code": venue_code,
                "race_no": race_no,
                "encParaR": enc_para_r,
                "race_meta": race_meta,
                "status": status,
                "http_status": status012,
                "finish_count": len(
                    finish_rows
                ),
                "results": parsed_results,
                "trifecta": trifecta,
                "jsj012": jsj012,
            }


            all_results.append(
                item
            )


            print(
                f"  [{race_no}/{len(races)}] "
                f"{race_key} "
                f"{mark} "
                f"着順={len(finish_rows)} "
                f"/ 3連単="
                f"{trifecta['combination']} "
                f"/ 払戻="
                f"{trifecta['payout']}"
            )


            time.sleep(0.05)


    # ========================================================
    # SAVE
    # ========================================================


    output = {
        "program": "056_test.py",
        "target_date": TARGET_DATE,
        "source_method": (
            "239_JSJ057_JSJ001_ENCP_JSJ012"
        ),
        "venue_count": len(kinfo),
        "total_race_count": total_races,
        "confirmed_result_count": confirmed_count,
        "status_summary": dict(
            status_counter
        ),
        "venue_race_distribution": dict(
            venue_counter
        ),
        "problem_count": len(
            problems
        ),
        "problems": problems,
        "races": all_results,
    }


    with open(
        OUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2,
        )


    # ========================================================
    # FINAL
    # ========================================================


    print()

    print(
        "#"
        * 100
    )

    print(
        "056 最終結果"
    )

    print(
        "#"
        * 100
    )

    print()

    print(
        "TARGET DATE:",
        TARGET_DATE
    )

    print(
        "VENUE COUNT:",
        len(kinfo)
    )

    print(
        "TOTAL RACES:",
        total_races
    )

    print(
        "CONFIRMED RESULT FOUND:",
        confirmed_count
    )

    print(
        "PROBLEM COUNT:",
        len(problems)
    )


    print()

    print(
        "★ STATUS SUMMARY ★"
    )


    for key, count in (
        status_counter.most_common()
    ):

        print(
            key,
            ":",
            count,
        )


    print()

    print(
        "★ 開催別レース数 ★"
    )


    for venue_name, count in (
        venue_counter.items()
    ):

        print(
            venue_name,
            ":",
            count,
        )


    print()

    print(
        "★ 確定結果サンプル TOP20 ★"
    )


    confirmed_results = [
        race
        for race in all_results
        if race["status"]
        == "CONFIRMED_RESULT_FOUND"
    ]


    for race in confirmed_results[:20]:

        print()

        print(
            race["race_key"]
        )

        print(
            "着順:",
            [
                (
                    result["finish_rank"],
                    result["car_no"],
                )
                for result
                in race["results"]
            ]
        )

        print(
            "3連単:",
            race["trifecta"][
                "combination"
            ]
        )

        print(
            "払戻:",
            race["trifecta"][
                "payout"
            ]
        )

        print(
            "人気:",
            race["trifecta"][
                "popularity"
            ]
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
        "=== 056 完了 ==="
    )


if __name__ == "__main__":

    main()