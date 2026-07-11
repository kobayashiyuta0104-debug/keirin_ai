from pathlib import Path
import json
import urllib.request
import urllib.parse


# ============================================================
# 030
#
# 弥彦7R 終了後 encp
# JSJ005 / JSJ002 直接取得テスト
#
# 目的:
#   ・終了後でもJSJ005のnarabiyoso本体が返るか確認
#   ・画面から消えただけなのか判定
#   ・JSJ002も比較取得
#
# 弥彦7R 終了前に確認した並び:
#   1-7 / 4-3-5 / 2-6
#
# ============================================================


BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "030_yahiko7_direct_line_test"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_JSON = (
    OUT_DIR
    / "030_yahiko7_direct_line_test.json"
)


JSON_URL = "https://www.keirin.jp/pc/json"


# 029終了後データで確認した弥彦7R encp
ENCP = "uT3_6zZe5WhDM6pyOeBlSNkwtN3m512OmuHRnzd44QE"


TARGET_TYPES = [
    "JSJ005",
    "JSJ002",
]


KNOWN_LINE = [
    [1, 7],
    [4, 3, 5],
    [2, 6],
]


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


def find_key_recursive(
    obj,
    target_key,
    path="root",
):

    hits = []


    if isinstance(obj, dict):

        for key, value in obj.items():

            current_path = (
                f"{path}.{key}"
            )


            if (
                str(key).lower()
                == target_key.lower()
            ):

                hits.append({
                    "path": current_path,
                    "key": key,
                    "value": value,
                })


            hits.extend(
                find_key_recursive(
                    value,
                    target_key,
                    current_path,
                )
            )


    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            current_path = (
                f"{path}[{index}]"
            )


            hits.extend(
                find_key_recursive(
                    value,
                    target_key,
                    current_path,
                )
            )


    return hits


def request_json(
    request_type,
):

    params = {
        "encp": ENCP,
        "type": request_type,
    }


    query = urllib.parse.urlencode(
        params
    )


    url = (
        JSON_URL
        + "?"
        + query
    )


    print()

    print(
        "=" * 100
    )

    print(
        "REQUEST TYPE:",
        request_type,
    )

    print(
        "URL:"
    )

    print(
        url
    )


    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/142.0.0.0 "
                "Safari/537.36 "
                "Edg/142.0.0.0"
            ),
            "Accept": (
                "application/json, "
                "text/javascript, "
                "*/*; q=0.01"
            ),
            "Referer": (
                "https://www.keirin.jp/pc/racelive"
            ),
            "X-Requested-With": (
                "XMLHttpRequest"
            ),
        },
        method="GET",
    )


    record = {
        "request_type": request_type,
        "encp": ENCP,
        "url": url,
    }


    try:

        with urllib.request.urlopen(
            request,
            timeout=60,
        ) as response:

            status = response.status

            headers = dict(
                response.headers.items()
            )

            body_bytes = response.read()


        body_text = body_bytes.decode(
            "utf-8",
            errors="replace",
        )


        print()

        print(
            "HTTP STATUS:",
            status,
        )

        print(
            "BODY LENGTH:",
            len(body_text),
        )


        record["status"] = status

        record["response_headers"] = (
            headers
        )

        record["body_length"] = len(
            body_text
        )

        record["body_text"] = body_text


        body_path = (
            OUT_DIR
            / (
                request_type
                + "_response.txt"
            )
        )


        body_path.write_text(
            body_text,
            encoding="utf-8",
            errors="replace",
        )


        record["body_path"] = str(
            body_path
        )


        try:

            data = json.loads(
                body_text
            )


            record["json_ok"] = True

            record["data"] = data


            json_path = (
                OUT_DIR
                / (
                    request_type
                    + "_response.json"
                )
            )


            save_json(
                json_path,
                data,
            )


            record["json_path"] = str(
                json_path
            )


            print()

            print(
                "JSON取得成功"
            )


            if isinstance(
                data,
                dict,
            ):

                top_keys = list(
                    data.keys()
                )

            else:

                top_keys = None


            record["top_keys"] = top_keys


            print()

            print(
                "TOP KEYS:"
            )

            print(
                top_keys
            )


            narabi_hits = (
                find_key_recursive(
                    data,
                    "narabiyoso",
                )
            )


            shaban_hits = (
                find_key_recursive(
                    data,
                    "shaban",
                )
            )


            line_keitai_hits = (
                find_key_recursive(
                    data,
                    "lineKeitai",
                )
            )


            ryoiki_hits = (
                find_key_recursive(
                    data,
                    "ryoikiFlg",
                )
            )


            record[
                "narabiyoso_hits"
            ] = narabi_hits

            record[
                "shaban_hits"
            ] = shaban_hits

            record[
                "lineKeitai_hits"
            ] = line_keitai_hits

            record[
                "ryoikiFlg_hits"
            ] = ryoiki_hits


            print()

            print(
                "narabiyoso HIT:",
                len(narabi_hits),
            )


            for index, hit in enumerate(
                narabi_hits,
                start=1,
            ):

                print()

                print(
                    "-" * 100
                )

                print(
                    "NARABI HIT",
                    index,
                )

                print(
                    "PATH:",
                    hit["path"],
                )

                print(
                    "VALUE:"
                )

                print(
                    json.dumps(
                        hit["value"],
                        ensure_ascii=False,
                        indent=2,
                    )
                )


            print()

            print(
                "shaban HIT:",
                len(shaban_hits),
            )


            for hit in shaban_hits:

                print()

                print(
                    "PATH:",
                    hit["path"],
                )

                print(
                    "VALUE:",
                    hit["value"],
                )


            print()

            print(
                "lineKeitai HIT:",
                len(line_keitai_hits),
            )


            for hit in line_keitai_hits:

                print()

                print(
                    "PATH:",
                    hit["path"],
                )

                print(
                    "VALUE:",
                    hit["value"],
                )


            print()

            print(
                "ryoikiFlg HIT:",
                len(ryoiki_hits),
            )


            for hit in ryoiki_hits:

                print(
                    hit["path"],
                    "=>",
                    hit["value"],
                )


            if request_type == "JSJ005":

                print()

                print(
                    "🔥 JSJ005 判定 🔥"
                )


                if not narabi_hits:

                    judgment = (
                        "NO_NARABIYOSO_KEY"
                    )


                    print(
                        "narabiyosoキーなし"
                    )


                else:

                    narabi_value = (
                        narabi_hits[0]["value"]
                    )


                    if isinstance(
                        narabi_value,
                        dict,
                    ):

                        shaban = (
                            narabi_value.get(
                                "shaban"
                            )
                        )

                        line_keitai = (
                            narabi_value.get(
                                "lineKeitai"
                            )
                        )

                        ryoiki_flg = (
                            narabi_value.get(
                                "ryoikiFlg"
                            )
                        )


                        if shaban:

                            judgment = (
                                "LINE_DATA_FOUND"
                            )


                            print()

                            print(
                                "🔥🔥🔥"
                            )

                            print(
                                "終了後でも"
                                "ライン本体あり！"
                            )

                            print(
                                "🔥🔥🔥"
                            )

                            print()

                            print(
                                "shaban:"
                            )

                            print(
                                json.dumps(
                                    shaban,
                                    ensure_ascii=False,
                                    indent=2,
                                )
                            )

                            print()

                            print(
                                "lineKeitai:",
                                line_keitai,
                            )

                            print()

                            print(
                                "既知ライン:"
                            )

                            print(
                                KNOWN_LINE
                            )


                        else:

                            judgment = (
                                "NARABI_KEY_BUT_"
                                "LINE_DATA_EMPTY"
                            )


                            print()

                            print(
                                "narabiyosoキーはある"
                            )

                            print(
                                "しかしshabanなし"
                            )

                            print()

                            print(
                                "ryoikiFlg:",
                                ryoiki_flg,
                            )

                            print(
                                "lineKeitai:",
                                line_keitai,
                            )


                    else:

                        judgment = (
                            "NARABI_VALUE_"
                            "NOT_DICT"
                        )


                record[
                    "judgment"
                ] = judgment


        except Exception as e:

            print()

            print(
                "JSON解析失敗:",
                repr(e),
            )


            record["json_ok"] = False

            record["json_error"] = repr(
                e
            )


    except Exception as e:

        print()

        print(
            "REQUEST ERROR:",
            repr(e),
        )


        record["request_error"] = repr(
            e
        )


    print()

    print(
        "=" * 100
    )


    return record


def main():

    print(
        "=== 030 弥彦7R 終了後ライン直接取得テスト ==="
    )

    print()

    print(
        "対象:"
    )

    print(
        "2026/07/09 弥彦7R"
    )

    print()

    print(
        "終了前確認ライン:"
    )

    print(
        "1-7 / 4-3-5 / 2-6"
    )

    print()

    print(
        "ENCP:"
    )

    print(
        ENCP
    )


    results = []


    for request_type in TARGET_TYPES:

        result = request_json(
            request_type
        )

        results.append(
            result
        )


    jsj005_result = next(
        (
            item
            for item in results
            if item["request_type"]
            == "JSJ005"
        ),
        None,
    )


    print()

    print(
        "#" * 100
    )

    print(
        "030 最終判定"
    )

    print(
        "#" * 100
    )

    print()


    if jsj005_result is None:

        final_judgment = (
            "JSJ005_RESULT_NOT_FOUND"
        )


        print(
            "JSJ005結果なし"
        )


    else:

        final_judgment = (
            jsj005_result.get(
                "judgment",
                "UNKNOWN",
            )
        )


        print(
            "JSJ005 JUDGMENT:"
        )

        print(
            final_judgment
        )


        if (
            final_judgment
            == "LINE_DATA_FOUND"
        ):

            print()

            print(
                "🔥🔥🔥🔥🔥"
            )

            print(
                "過去ライン取得ルート"
                "の可能性あり！"
            )

            print(
                "🔥🔥🔥🔥🔥"
            )


        elif (
            final_judgment
            == (
                "NARABI_KEY_BUT_"
                "LINE_DATA_EMPTY"
            )
        ):

            print()

            print(
                "終了後はnarabiyoso"
                "構造だけ残り、"
                "ライン本体が空"
            )


        else:

            print()

            print(
                "JSJ005内容を"
                "追加確認する必要あり"
            )


    output = {
        "program": (
            "030_yahiko7_direct_line_test.py"
        ),
        "target": {
            "date": "2026/07/09",
            "venue": "弥彦",
            "race_no": 7,
            "known_pre_race_line": (
                KNOWN_LINE
            ),
            "encp": ENCP,
        },
        "final_judgment": (
            final_judgment
        ),
        "results": results,
    }


    save_json(
        OUT_JSON,
        output,
    )


    print()

    print(
        "保存先:"
    )

    print(
        OUT_JSON
    )

    print()

    print(
        "=== 030 完了 ==="
    )


if __name__ == "__main__":

    main()