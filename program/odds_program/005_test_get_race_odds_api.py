# -*- coding: utf-8 -*-

"""
005_test_get_race_odds_api.py

目的：
netkeirinのAplRaceOdds APIへ直接アクセスして、
指定race_idのオッズデータを取得する。

対象：
2026/09/08 いわき平 12R
race_id = 202609081312

今回の目的：
・AplRaceOdds APIが実際に呼び出せるか確認
・APIの生レスポンスを保存
・JSONなら構造を確認
・compress=1 の場合は Base64 + ZLIB を展開
・3連単オッズの格納形式を特定する

※ 今回はCSV化しない
※ まだ大量取得しない
※ 1レースだけテストする

出力：
C:\\競輪AI\\data_official\\odds_test\\

202609081312_api_response.txt
202609081312_api_response.json
"""

from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
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

TEXT_PATH = OUTPUT_DIR / (
    f"{RACE_ID}_api_response.txt"
)

JSON_PATH = OUTPUT_DIR / (
    f"{RACE_ID}_api_response.json"
)

API_URL = (
    "https://keirin.netkeiba.com/api/race/"
)

ODDS_CLASS = "AplRaceOdds"


# ============================================================
# APIアクセス
# ============================================================

def request_api():

    print("=" * 70)
    print("005 AplRaceOdds API テスト取得")
    print("=" * 70)
    print()

    print("API URL:")
    print(API_URL)
    print()

    print("RACE_ID:")
    print(RACE_ID)
    print()

    # --------------------------------------------------------
    # JS解析で確認できた送信パラメータ
    # --------------------------------------------------------

    data = {
        "class": ODDS_CLASS,
        "method": "get",
        "compress": "1",
        "race_id": RACE_ID,
        "input": "UTF-8",
        "output": "json",
    }

    encoded_data = urlencode(data).encode("utf-8")

    print("送信パラメータ:")
    print()

    for key, value in data.items():
        print(f"{key} = {value}")

    print()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "application/json,"
            "text/javascript,"
            "text/plain,"
            "*/*"
        ),
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Content-Type": (
            "application/x-www-form-urlencoded; "
            "charset=UTF-8"
        ),
        "Referer": (
            f"https://keirin.netkeiba.com/"
            f"race/odds/?race_id={RACE_ID}"
        ),
        "Origin": "https://keirin.netkeiba.com",
        "Connection": "keep-alive",
    }

    request = Request(
        API_URL,
        data=encoded_data,
        headers=headers,
        method="POST",
    )

    print("APIへPOSTします...")
    print()

    with urlopen(request, timeout=30) as response:

        status = response.status
        response_headers = response.headers
        raw_data = response.read()

    print("APIアクセス成功")
    print()

    print("HTTP STATUS:")
    print(status)
    print()

    print("レスポンスサイズ:")
    print(f"{len(raw_data):,} bytes")
    print()

    print("Content-Type:")
    print(response_headers.get("Content-Type"))
    print()

    return raw_data


# ============================================================
# レスポンス解析
# ============================================================

def decode_response(raw_data):

    print("=" * 70)
    print("レスポンス解析")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # まずUTF-8として読んでみる
    # --------------------------------------------------------

    raw_text = raw_data.decode(
        "utf-8",
        errors="replace"
    )

    print("UTF-8デコード後:")
    print()

    print(raw_text[:1000])
    print()

    # --------------------------------------------------------
    # JSONとして直接読めるか確認
    # --------------------------------------------------------

    try:

        data = json.loads(raw_text)

        print("JSONとして直接解析できました。")
        print()

        return data

    except Exception:

        print(
            "通常のJSONではありません。"
        )
        print()

    # --------------------------------------------------------
    # Base64 + ZLIBを試す
    # --------------------------------------------------------

    print(
        "Base64 + ZLIB展開を試します..."
    )
    print()

    try:

        decoded = base64.b64decode(
            raw_text.strip()
        )

        print(
            f"Base64デコード後 : "
            f"{len(decoded):,} bytes"
        )

        print()

        # ----------------------------------------------------
        # zlib形式
        # ----------------------------------------------------

        try:

            decompressed = zlib.decompress(
                decoded
            )

        except Exception:

            # ------------------------------------------------
            # raw deflate形式も試す
            # ------------------------------------------------

            decompressed = zlib.decompress(
                decoded,
                -zlib.MAX_WBITS
            )

        print(
            f"ZLIB展開後 : "
            f"{len(decompressed):,} bytes"
        )

        print()

        decompressed_text = decompressed.decode(
            "utf-8",
            errors="replace"
        )

        print("展開後データ:")
        print()

        print(decompressed_text[:2000])
        print()

        try:

            data = json.loads(
                decompressed_text
            )

            print(
                "展開後JSONの解析に成功しました。"
            )
            print()

            return data

        except Exception as e:

            print(
                "展開後JSON解析失敗"
            )
            print(
                type(e).__name__,
                str(e)
            )
            print()

            return decompressed_text

    except Exception as e:

        print(
            "Base64 + ZLIB展開にも失敗しました。"
        )
        print()

        print(
            type(e).__name__
        )
        print(
            str(e)
        )
        print()

        return raw_text


# ============================================================
# JSON構造表示
# ============================================================

def inspect_structure(data, indent=0):

    prefix = " " * indent

    if isinstance(data, dict):

        print(
            f"{prefix}DICT "
            f"({len(data)} keys)"
        )

        for key, value in data.items():

            if isinstance(value, dict):

                print(
                    f"{prefix}  {key} : "
                    f"DICT ({len(value)} keys)"
                )

            elif isinstance(value, list):

                print(
                    f"{prefix}  {key} : "
                    f"LIST ({len(value)} items)"
                )

            else:

                value_text = str(value)

                if len(value_text) > 150:
                    value_text = (
                        value_text[:150]
                        + "..."
                    )

                print(
                    f"{prefix}  {key} : "
                    f"{value_text}"
                )

    elif isinstance(data, list):

        print(
            f"{prefix}LIST "
            f"({len(data)} items)"
        )

        for index, value in enumerate(
            data[:10]
        ):

            print(
                f"{prefix}  [{index}]"
            )

            inspect_structure(
                value,
                indent + 4
            )

    else:

        print(
            f"{prefix}{data}"
        )


# ============================================================
# 3連単候補を探す
# ============================================================

def find_odds_candidates(data):

    print("=" * 70)
    print("3連単・オッズ候補検索")
    print("=" * 70)
    print()

    results = []

    def recursive_search(
        obj,
        path="root"
    ):

        if isinstance(obj, dict):

            for key, value in obj.items():

                key_text = str(key).lower()

                if (
                    "odds" in key_text
                    or "3tan" in key_text
                    or "sanren" in key_text
                    or "trifecta" in key_text
                ):

                    results.append(
                        (
                            f"{path}.{key}",
                            value
                        )
                    )

                recursive_search(
                    value,
                    f"{path}.{key}"
                )

        elif isinstance(obj, list):

            for index, value in enumerate(
                obj[:1000]
            ):

                recursive_search(
                    value,
                    f"{path}[{index}]"
                )

    recursive_search(data)

    if not results:

        print(
            "キー名から直接オッズ候補は"
            "見つかりませんでした。"
        )

        print()

        return

    print(
        f"候補 : {len(results)}件"
    )

    print()

    for path, value in results[:30]:

        print("-" * 70)
        print(path)
        print()

        try:

            print(
                json.dumps(
                    value,
                    ensure_ascii=False,
                    indent=2
                )[:3000]
            )

        except Exception:

            print(str(value)[:3000])

        print()


# ============================================================
# メイン
# ============================================================

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # API取得
    # --------------------------------------------------------

    try:

        raw_data = request_api()

    except Exception as e:

        print("=" * 70)
        print("APIアクセス失敗")
        print("=" * 70)
        print()

        print(
            type(e).__name__
        )

        print(
            str(e)
        )

        print()

        print(
            "今回はここで終了します。"
        )

        return

    # --------------------------------------------------------
    # 生レスポンス保存
    # --------------------------------------------------------

    raw_text = raw_data.decode(
        "utf-8",
        errors="replace"
    )

    TEXT_PATH.write_text(
        raw_text,
        encoding="utf-8"
    )

    print("=" * 70)
    print("生レスポンス保存")
    print("=" * 70)
    print()

    print(TEXT_PATH)
    print()

    # --------------------------------------------------------
    # レスポンス解析
    # --------------------------------------------------------

    data = decode_response(
        raw_data
    )

    # --------------------------------------------------------
    # JSON保存
    # --------------------------------------------------------

    if isinstance(
        data,
        (dict, list)
    ):

        JSON_PATH.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print("=" * 70)
        print("JSON保存")
        print("=" * 70)
        print()

        print(JSON_PATH)
        print()

        # ----------------------------------------------------
        # 構造表示
        # ----------------------------------------------------

        print("=" * 70)
        print("JSON構造")
        print("=" * 70)
        print()

        inspect_structure(data)

        print()

        # ----------------------------------------------------
        # オッズ候補検索
        # ----------------------------------------------------

        find_odds_candidates(data)

    else:

        print(
            "JSONオブジェクトとして"
            "認識できなかったため、"
            "構造解析は行いません。"
        )

    # --------------------------------------------------------
    # 完了
    # --------------------------------------------------------

    print("=" * 70)
    print("005 完了")
    print("=" * 70)
    print()

    print(
        "今回のテストでは、"
        "実際のオッズデータを取得できたかを確認します。"
    )

    print()

    print(
        "次に確認したいのは、"
    )

    print(
        "① APIアクセス成功/失敗"
    )

    print(
        "② JSONの中身"
    )

    print(
        "③ 3連単データの格納場所"
    )

    print(
        "④ 組み合わせとオッズの対応"
    )

    print()

    print(
        "この画面の結果、または"
        "api_response.json の内容を貼ってください。"
    )


if __name__ == "__main__":
    main()