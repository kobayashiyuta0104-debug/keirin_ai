# -*- coding: utf-8 -*-

"""
015_inspect_jsj079_080.py

目的
----
JSJ079 / JSJ080 のレスポンスに含まれる
oList の中身を確認する。

今回は調査のみ。
既存のPRE_RACEやCSVは変更しない。

確認すること
------------
1. JSJ079 が正常取得できるか
2. JSJ080 が正常取得できるか
3. oList が存在するか
4. oList の件数
5. oList の実際の中身
6. 3連単オッズと思われるデータが存在するか
"""

import json
import os
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# ============================================================
# 設定
# ============================================================

BASE_URL = "https://keirin.jp"

# 前回と同じ調査対象
JOCD = "22"

# 現在の確認用レース
# 2026/09/16 伊東1R
# まずは現在サイトで正常に取得できる条件を使う
RACE_DATE = "20260916"
RACE_NO = "1"

OUTPUT_DIR = (
    r"C:\競輪AI\data_official"
    r"\historical\oddspark_test"
    r"\015_jsj079_080"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# HTTP
# ============================================================

def request_json(jsj_id, params):
    """
    KEIRIN.JPのJSON APIをGETで呼び出す。
    """

    query = params.copy()
    query["type"] = jsj_id

    url = BASE_URL + "/pc/json?" + urlencode(query)

    print()
    print("=" * 70)
    print(jsj_id)
    print("=" * 70)
    print("URL:")
    print(url)

    req = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0 Safari/537.36"
            ),
            "Accept": "application/json,text/plain,*/*",
            "Referer": BASE_URL + "/pc/top",
        },
    )

    try:

        with urlopen(req, timeout=20) as response:

            raw = response.read()

            print()
            print("HTTP:", response.status)
            print("RAW SIZE:", len(raw), "bytes")

            text = raw.decode(
                "utf-8",
                errors="replace"
            )

            print()
            print("先頭500文字:")
            print(text[:500])

            try:
                data = json.loads(text)
            except Exception as e:

                print()
                print("JSON解析失敗")
                print("ERROR:", e)

                # 念のため生データ保存
                raw_path = os.path.join(
                    OUTPUT_DIR,
                    f"{jsj_id}_raw.txt"
                )

                with open(
                    raw_path,
                    "w",
                    encoding="utf-8"
                ) as f:
                    f.write(text)

                print("RAW保存:")
                print(raw_path)

                return None

            return data

    except Exception as e:

        print()
        print("HTTP ERROR")
        print(e)

        return None


# ============================================================
# 再帰的に oList を探す
# ============================================================

def find_key(obj, target_key, path="root"):
    """
    JSONの中から target_key を再帰的に探す。
    """

    results = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            current_path = f"{path}.{key}"

            if key == target_key:
                results.append(
                    (current_path, value)
                )

            results.extend(
                find_key(
                    value,
                    target_key,
                    current_path
                )
            )

    elif isinstance(obj, list):

        for i, value in enumerate(obj):

            current_path = f"{path}[{i}]"

            results.extend(
                find_key(
                    value,
                    target_key,
                    current_path
                )
            )

    return results


# ============================================================
# JSONの構造を確認
# ============================================================

def print_structure(obj, path="root", depth=0, max_depth=4):
    """
    JSON構造を簡易表示。
    """

    if depth > max_depth:
        return

    indent = "  " * depth

    if isinstance(obj, dict):

        print(
            f"{indent}{path}: dict "
            f"({len(obj)} keys)"
        )

        for key, value in obj.items():

            child_path = f"{path}.{key}"

            if isinstance(value, (dict, list)):

                print_structure(
                    value,
                    child_path,
                    depth + 1,
                    max_depth
                )

            else:

                print(
                    f"{indent}  "
                    f"{key} = {repr(value)[:200]}"
                )

    elif isinstance(obj, list):

        print(
            f"{indent}{path}: list "
            f"({len(obj)} items)"
        )

        # 最初の3件だけ構造確認
        for i, value in enumerate(obj[:3]):

            print_structure(
                value,
                f"{path}[{i}]",
                depth + 1,
                max_depth
            )

    else:

        print(
            f"{indent}{path}: "
            f"{repr(obj)[:200]}"
        )


# ============================================================
# oList解析
# ============================================================

def inspect_olist(jsj_id, data):

    print()
    print("=" * 70)
    print(f"{jsj_id} oList解析")
    print("=" * 70)

    if data is None:

        print("データなし")
        return

    # --------------------------------------------------------
    # 全体構造
    # --------------------------------------------------------

    print()
    print("【JSON構造】")

    print_structure(
        data,
        max_depth=3
    )

    # --------------------------------------------------------
    # oList検索
    # --------------------------------------------------------

    olist_results = find_key(
        data,
        "oList"
    )

    print()
    print("【oList検索結果】")

    print(
        "oList発見数:",
        len(olist_results)
    )

    if not olist_results:

        print()
        print("★ oListは見つかりませんでした。")

        return

    # --------------------------------------------------------
    # oListの中身
    # --------------------------------------------------------

    for index, (path, value) in enumerate(
        olist_results,
        start=1
    ):

        print()
        print("-" * 70)
        print(f"oList #{index}")
        print("PATH:", path)

        if isinstance(value, list):

            print(
                "TYPE: list"
            )

            print(
                "COUNT:",
                len(value)
            )

            print()
            print("【最初の10件】")

            for i, item in enumerate(
                value[:10]
            ):

                print()
                print(
                    f"[{i}]"
                )

                if isinstance(item, dict):

                    for key, val in item.items():

                        print(
                            f"  {key} = "
                            f"{repr(val)[:500]}"
                        )

                else:

                    print(
                        " ",
                        repr(item)[:1000]
                    )

        elif isinstance(value, dict):

            print(
                "TYPE: dict"
            )

            print(
                "KEY COUNT:",
                len(value)
            )

            print()
            print(
                json.dumps(
                    value,
                    ensure_ascii=False,
                    indent=2
                )[:10000]
            )

        else:

            print(
                "TYPE:",
                type(value).__name__
            )

            print(
                "VALUE:",
                repr(value)[:5000]
            )

        # ----------------------------------------------------
        # そのまま保存
        # ----------------------------------------------------

        save_path = os.path.join(
            OUTPUT_DIR,
            f"{jsj_id}_olist_{index}.json"
        )

        with open(
            save_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                value,
                f,
                ensure_ascii=False,
                indent=2
            )

        print()
        print(
            "oList保存:",
            save_path
        )


# ============================================================
# 文字列として odds 関連キーを探す
# ============================================================

def find_odds_related(obj, path="root"):

    keywords = [
        "odds",
        "odds",
        "倍率",
        "オッズ",
        "sanrentan",
        "3ren",
        "3連単",
        "kumi",
        "kaime",
        "combination",
    ]

    results = []

    if isinstance(obj, dict):

        for key, value in obj.items():

            current_path = f"{path}.{key}"

            key_lower = str(key).lower()

            if any(
                keyword.lower() in key_lower
                for keyword in keywords
            ):

                results.append(
                    (
                        current_path,
                        value
                    )
                )

            results.extend(
                find_odds_related(
                    value,
                    current_path
                )
            )

    elif isinstance(obj, list):

        for i, value in enumerate(obj):

            results.extend(
                find_odds_related(
                    value,
                    f"{path}[{i}]"
                )
            )

    return results


# ============================================================
# メイン
# ============================================================

def main():

    print("=" * 70)
    print("015 JSJ079 / JSJ080 oList調査")
    print("=" * 70)

    print()
    print("対象:")
    print("開催日:", RACE_DATE)
    print("競輪場コード:", JOCD)
    print("レース番号:", RACE_NO)

    # --------------------------------------------------------
    # パラメータ
    # --------------------------------------------------------
    #
    # JSJ079 / 080 の正確なパラメータは、
    # 前回の全JSJ調査で使った条件をまず基本にする。
    #
    # ここでは複数候補を試して、
    # レスポンスそのものを確認する。
    #

    parameter_sets = [

        {
            "jocd": JOCD,
            "kaisaiDate": RACE_DATE,
            "raceNo": RACE_NO,
        },

        {
            "jocd": JOCD,
            "kaisaiBi": RACE_DATE,
            "raceNo": RACE_NO,
        },

        {
            "jocd": JOCD,
            "kaisaiDate": RACE_DATE,
        },

        {
            "jocd": JOCD,
        },
    ]

    all_results = {}

    # --------------------------------------------------------
    # JSJ079
    # --------------------------------------------------------

    for params in parameter_sets:

        data = request_json(
            "JSJ079",
            params
        )

        if data is None:
            continue

        key = json.dumps(
            params,
            sort_keys=True,
            ensure_ascii=False
        )

        all_results[
            f"JSJ079_{key}"
        ] = data

        inspect_olist(
            "JSJ079",
            data
        )

        # odds関連
        related = find_odds_related(data)

        print()
        print("【オッズ関連キー】")

        if related:

            for path, value in related[:50]:

                print()
                print(
                    path,
                    "=",
                    repr(value)[:500]
                )

        else:

            print(
                "オッズ関連と思われるキーなし"
            )

    # --------------------------------------------------------
    # JSJ080
    # --------------------------------------------------------

    for params in parameter_sets:

        data = request_json(
            "JSJ080",
            params
        )

        if data is None:
            continue

        key = json.dumps(
            params,
            sort_keys=True,
            ensure_ascii=False
        )

        all_results[
            f"JSJ080_{key}"
        ] = data

        inspect_olist(
            "JSJ080",
            data
        )

        # odds関連
        related = find_odds_related(data)

        print()
        print("【オッズ関連キー】")

        if related:

            for path, value in related[:50]:

                print()
                print(
                    path,
                    "=",
                    repr(value)[:500]
                )

        else:

            print(
                "オッズ関連と思われるキーなし"
            )

    # --------------------------------------------------------
    # 全レスポンス保存
    # --------------------------------------------------------

    all_path = os.path.join(
        OUTPUT_DIR,
        "015_all_response.json"
    )

    with open(
        all_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_results,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 70)
    print("015 完了")
    print("=" * 70)

    print()
    print("全レスポンス保存:")
    print(all_path)

    print()
    print(
        "次に確認するポイント："
    )

    print(
        "① oListが存在するか"
    )

    print(
        "② oListの件数"
    )

    print(
        "③ oListの各項目に車番・組合せがあるか"
    )

    print(
        "④ オッズ倍率があるか"
    )

    print(
        "⑤ 3連単504通りに対応できそうか"
    )


if __name__ == "__main__":
    main()