# -*- coding: utf-8 -*-

"""
006_decode_race_odds.py

目的：
005で取得したnetkeirin AplRaceOdds APIのレスポンスから、
圧縮されている3連単オッズデータを展開して、
実際のデータ構造を確認する。

対象：
2026/09/08 いわき平 12R
race_id = 202609081312

今回確認する内容：
・APIレスポンスのstatus
・nkrace_odds::race_id の取得
・Base64デコード
・ZLIB展開
・展開後JSONの構造
・キー名
・データ件数
・3連単の買い目とオッズらしき値
・_last_dt

入力：
C:\\競輪AI\\data_official\\odds_test\\
    202609081312_api_response.json

出力：
C:\\競輪AI\\data_official\\odds_test\\
    202609081312_decoded_odds.json

    202609081312_decoded_odds.txt

※ 今回はCSV化しない
※ まだ大量取得しない
※ 1レースだけ解析する
"""

from pathlib import Path
import base64
import json
import zlib


# ============================================================
# 設定
# ============================================================

RACE_ID = "202609081312"

OUTPUT_DIR = Path(
    r"C:\競輪AI\data_official\odds_test"
)

INPUT_PATH = OUTPUT_DIR / (
    f"{RACE_ID}_api_response.json"
)

DECODED_JSON_PATH = OUTPUT_DIR / (
    f"{RACE_ID}_decoded_odds.json"
)

ANALYSIS_PATH = OUTPUT_DIR / (
    f"{RACE_ID}_decoded_odds.txt"
)


# ============================================================
# JSON読み込み
# ============================================================

def load_api_response():

    print("=" * 70)
    print("APIレスポンス読み込み")
    print("=" * 70)
    print()

    print("入力ファイル:")
    print(INPUT_PATH)
    print()

    if not INPUT_PATH.exists():

        print("入力ファイルがありません。")
        print()

        print(
            "先に005を実行してください。"
        )

        return None

    try:

        data = json.loads(
            INPUT_PATH.read_text(
                encoding="utf-8"
            )
        )

    except Exception as e:

        print("JSON読み込み失敗")
        print()

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        return None

    print("JSON読み込み成功")
    print()

    print(
        f"トップレベルキー : "
        f"{list(data.keys())}"
    )

    print()

    return data


# ============================================================
# APIデータ取得
# ============================================================

def get_odds_blob(api_response):

    print("=" * 70)
    print("オッズデータ取得")
    print("=" * 70)
    print()

    status = api_response.get(
        "status"
    )

    reason = api_response.get(
        "reason"
    )

    print(
        f"status : {status}"
    )

    print(
        f"reason : {reason}"
    )

    print()

    if status != "OK":

        print(
            "API status がOKではありません。"
        )

        return None

    data = api_response.get(
        "data"
    )

    if not isinstance(data, dict):

        print(
            "data が辞書形式ではありません。"
        )

        return None

    odds_key = (
        f"nkrace_odds::{RACE_ID}"
    )

    last_dt_key = (
        f"nkrace_odds::{RACE_ID}_last_dt"
    )

    print("検索キー:")
    print(odds_key)
    print()

    if odds_key not in data:

        print(
            "オッズデータが見つかりません。"
        )

        print()

        print("data内のキー:")

        for key in data.keys():

            print(
                f"  {key}"
            )

        return None

    odds_blob = data[
        odds_key
    ]

    last_dt = data.get(
        last_dt_key
    )

    print(
        f"圧縮データサイズ : "
        f"{len(odds_blob):,}文字"
    )

    print()

    print(
        f"last_dt : {last_dt}"
    )

    print()

    return odds_blob


# ============================================================
# Base64 + ZLIB展開
# ============================================================

def decode_odds_blob(odds_blob):

    print("=" * 70)
    print("Base64 + ZLIB 展開")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # Base64
    # --------------------------------------------------------

    print("① Base64デコード")

    try:

        decoded = base64.b64decode(
            odds_blob
        )

    except Exception as e:

        print(
            "Base64デコード失敗"
        )

        print(
            type(e).__name__,
            str(e)
        )

        return None

    print(
        f"Base64デコード後 : "
        f"{len(decoded):,} bytes"
    )

    print()

    # --------------------------------------------------------
    # ZLIB
    # --------------------------------------------------------

    print("② ZLIB展開")

    decompressed = None

    # 通常のzlib
    try:

        decompressed = zlib.decompress(
            decoded
        )

        print(
            "通常のZLIB形式で展開成功"
        )

    except Exception as e:

        print(
            "通常のZLIB展開失敗"
        )

        print(
            str(e)
        )

        print()

    # --------------------------------------------------------
    # raw deflate
    # --------------------------------------------------------

    if decompressed is None:

        try:

            decompressed = zlib.decompress(
                decoded,
                -zlib.MAX_WBITS
            )

            print(
                "raw DEFLATE形式で展開成功"
            )

        except Exception as e:

            print(
                "raw DEFLATE展開失敗"
            )

            print(
                str(e)
            )

            return None

    print()

    print(
        f"ZLIB展開後 : "
        f"{len(decompressed):,} bytes"
    )

    print()

    # --------------------------------------------------------
    # UTF-8
    # --------------------------------------------------------

    try:

        text = decompressed.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        text = decompressed.decode(
            "utf-8",
            errors="replace"
        )

    print("③ 展開後テキスト")
    print()

    print(
        text[:3000]
    )

    print()

    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    try:

        data = json.loads(
            text
        )

    except Exception as e:

        print(
            "展開後JSON解析失敗"
        )

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        return text

    print(
        "④ 展開後JSON解析成功"
    )

    print()

    return data


# ============================================================
# JSON構造を再帰表示
# ============================================================

def print_structure(
    value,
    path="root",
    depth=0,
    max_depth=8
):

    if depth > max_depth:

        print(
            f"{'  ' * depth}"
            f"{path} : "
            f"(最大深度到達)"
        )

        return

    indent = "  " * depth

    # --------------------------------------------------------
    # dict
    # --------------------------------------------------------

    if isinstance(value, dict):

        print(
            f"{indent}{path} : "
            f"DICT ({len(value)} keys)"
        )

        for key, child in list(
            value.items()
        )[:100]:

            print_structure(
                child,
                f"{path}.{key}",
                depth + 1,
                max_depth
            )

    # --------------------------------------------------------
    # list
    # --------------------------------------------------------

    elif isinstance(value, list):

        print(
            f"{indent}{path} : "
            f"LIST ({len(value)} items)"
        )

        for index, child in enumerate(
            value[:20]
        ):

            print_structure(
                child,
                f"{path}[{index}]",
                depth + 1,
                max_depth
            )

    # --------------------------------------------------------
    # その他
    # --------------------------------------------------------

    else:

        text = str(value)

        if len(text) > 200:

            text = (
                text[:200]
                + "..."
            )

        print(
            f"{indent}{path} : "
            f"{type(value).__name__} = "
            f"{text}"
        )


# ============================================================
# 買い目らしきキーを探す
# ============================================================

def find_combination_keys(
    value,
    path="root",
    results=None
):

    if results is None:

        results = []

    # --------------------------------------------------------
    # dict
    # --------------------------------------------------------

    if isinstance(value, dict):

        for key, child in value.items():

            key_text = str(key)

            # ------------------------------------------------
            # 3連単候補
            #
            # 123
            # 1-2-3
            # 1234
            # etc.
            # ------------------------------------------------

            if (
                len(key_text) in (3, 5, 6)
                and all(
                    char.isdigit()
                    or char in "-_"
                    for char in key_text
                )
            ):

                results.append(
                    (
                        f"{path}.{key}",
                        child
                    )
                )

            find_combination_keys(
                child,
                f"{path}.{key}",
                results
            )

    # --------------------------------------------------------
    # list
    # --------------------------------------------------------

    elif isinstance(value, list):

        for index, child in enumerate(
            value[:1000]
        ):

            find_combination_keys(
                child,
                f"{path}[{index}]",
                results
            )

    return results


# ============================================================
# 数値データを探す
# ============================================================

def find_numeric_values(
    value,
    path="root",
    results=None
):

    if results is None:

        results = []

    if isinstance(value, dict):

        for key, child in value.items():

            if isinstance(
                child,
                (int, float)
            ):

                results.append(
                    (
                        f"{path}.{key}",
                        child
                    )
                )

            else:

                find_numeric_values(
                    child,
                    f"{path}.{key}",
                    results
                )

    elif isinstance(value, list):

        for index, child in enumerate(
            value[:1000]
        ):

            find_numeric_values(
                child,
                f"{path}[{index}]",
                results
            )

    return results


# ============================================================
# 結果ファイル作成
# ============================================================

def save_analysis(
    api_response,
    odds_data
):

    print("=" * 70)
    print("解析結果保存")
    print("=" * 70)
    print()

    output = []

    output.append(
        "=" * 70
    )

    output.append(
        "006 netkeirin 3連単オッズ展開解析"
    )

    output.append(
        "=" * 70
    )

    output.append("")

    output.append(
        f"RACE_ID : {RACE_ID}"
    )

    output.append("")

    output.append(
        "【API status】"
    )

    output.append(
        str(
            api_response.get("status")
        )
    )

    output.append("")

    output.append(
        "【展開後JSON構造】"
    )

    output.append("")

    # --------------------------------------------------------
    # 構造を一旦文字列化
    # --------------------------------------------------------

    import io
    import contextlib

    buffer = io.StringIO()

    with contextlib.redirect_stdout(
        buffer
    ):

        print_structure(
            odds_data
        )

    output.append(
        buffer.getvalue()
    )

    output.append("")

    # --------------------------------------------------------
    # JSONそのもの
    # --------------------------------------------------------

    output.append(
        "=" * 70
    )

    output.append(
        "【展開後JSON】"
    )

    output.append(
        "=" * 70
    )

    output.append("")

    try:

        output.append(
            json.dumps(
                odds_data,
                ensure_ascii=False,
                indent=2
            )
        )

    except Exception:

        output.append(
            str(odds_data)
        )

    output.append("")

    # --------------------------------------------------------
    # 買い目候補
    # --------------------------------------------------------

    combinations = (
        find_combination_keys(
            odds_data
        )
    )

    output.append(
        "=" * 70
    )

    output.append(
        "【買い目らしきキー】"
    )

    output.append(
        "=" * 70
    )

    output.append("")

    output.append(
        f"候補件数 : "
        f"{len(combinations)}"
    )

    output.append("")

    for path, value in combinations[
        :300
    ]:

        output.append(
            f"{path} = {value}"
        )

    output.append("")

    # --------------------------------------------------------
    # 数値
    # --------------------------------------------------------

    numbers = find_numeric_values(
        odds_data
    )

    output.append(
        "=" * 70
    )

    output.append(
        "【数値データ】"
    )

    output.append(
        "=" * 70
    )

    output.append("")

    output.append(
        f"数値件数 : "
        f"{len(numbers)}"
    )

    output.append("")

    for path, value in numbers[
        :300
    ]:

        output.append(
            f"{path} = {value}"
        )

    output.append("")

    ANALYSIS_PATH.write_text(
        "\n".join(output),
        encoding="utf-8"
    )

    print(
        ANALYSIS_PATH
    )

    print()


# ============================================================
# メイン
# ============================================================

def main():

    print("=" * 70)
    print("006 netkeirin 3連単オッズ展開解析")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # 005のJSONを読む
    # --------------------------------------------------------

    api_response = (
        load_api_response()
    )

    if api_response is None:

        return

    # --------------------------------------------------------
    # 圧縮データを取得
    # --------------------------------------------------------

    odds_blob = (
        get_odds_blob(
            api_response
        )
    )

    if odds_blob is None:

        return

    # --------------------------------------------------------
    # 展開
    # --------------------------------------------------------

    odds_data = (
        decode_odds_blob(
            odds_blob
        )
    )

    if odds_data is None:

        print(
            "オッズデータの展開に失敗しました。"
        )

        return

    # --------------------------------------------------------
    # 展開後JSON保存
    # --------------------------------------------------------

    if isinstance(
        odds_data,
        (dict, list)
    ):

        DECODED_JSON_PATH.write_text(
            json.dumps(
                odds_data,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print("=" * 70)
        print("展開後JSON保存")
        print("=" * 70)
        print()

        print(
            DECODED_JSON_PATH
        )

        print()

        # ----------------------------------------------------
        # 構造表示
        # ----------------------------------------------------

        print("=" * 70)
        print("展開後JSON構造")
        print("=" * 70)
        print()

        print_structure(
            odds_data
        )

        print()

        # ----------------------------------------------------
        # 買い目候補
        # ----------------------------------------------------

        combinations = (
            find_combination_keys(
                odds_data
            )
        )

        print("=" * 70)
        print("買い目らしきキー")
        print("=" * 70)
        print()

        print(
            f"候補件数 : "
            f"{len(combinations)}"
        )

        print()

        for path, value in combinations[
            :100
        ]:

            print(
                f"{path} = {value}"
            )

        print()

    # --------------------------------------------------------
    # 解析結果保存
    # --------------------------------------------------------

    save_analysis(
        api_response,
        odds_data
    )

    # --------------------------------------------------------
    # 完了
    # --------------------------------------------------------

    print("=" * 70)
    print("006 完了")
    print("=" * 70)
    print()

    print(
        "展開後JSON:"
    )

    print(
        DECODED_JSON_PATH
    )

    print()

    print(
        "解析結果:"
    )

    print(
        ANALYSIS_PATH
    )

    print()

    print(
        "この実行結果を貼ってください。"
    )

    print(
        "特に「展開後JSON構造」と"
        "「買い目らしきキー」の部分を確認します。"
    )


if __name__ == "__main__":
    main()