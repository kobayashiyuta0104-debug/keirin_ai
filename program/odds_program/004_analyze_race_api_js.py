# -*- coding: utf-8 -*-

"""
004_analyze_race_api_js.py

目的：
netkeirinのオッズ取得で使用されている
AplApiRace の中身を解析する。

今回の目的は、
「3連単オッズを実際にどのAPIへ、
どんなパラメータで取得しているのか」
を特定すること。

この段階では、まだ実際のオッズ取得は行わない。

対象：
2026/09/08 いわき平 12R
race_id = 202609081312

解析対象JS：
https://cdnv2.netkeiba.com/keirin/api/race/common/js/race_api_indexdb.min.js?210616

出力：
C:\\競輪AI\\data_official\\odds_test\\
    202609081312_race_api_indexdb.min.js

    202609081312_api_analysis.txt
"""

from pathlib import Path
from urllib.request import Request, urlopen
import re


# ============================================================
# 基本設定
# ============================================================

RACE_ID = "202609081312"

OUTPUT_DIR = Path(
    r"C:\競輪AI\data_official\odds_test"
)

JS_PATH = OUTPUT_DIR / (
    f"{RACE_ID}_race_api_indexdb.min.js"
)

ANALYSIS_PATH = OUTPUT_DIR / (
    f"{RACE_ID}_api_analysis.txt"
)

TARGET_JS_URL = (
    "https://cdnv2.netkeiba.com/"
    "keirin/api/race/common/js/"
    "race_api_indexdb.min.js?210616"
)


# ============================================================
# JavaScript取得
# ============================================================

def download_js(url):

    print("JavaScriptを取得します。")
    print()
    print(url)
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
            "text/javascript,"
            "application/javascript,"
            "application/json,"
            "text/plain,"
            "*/*"
        ),
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Referer": (
            f"https://keirin.netkeiba.com/"
            f"race/odds/?race_id={RACE_ID}"
        ),
        "Connection": "keep-alive",
    }

    request = Request(
        url,
        headers=headers
    )

    with urlopen(request, timeout=30) as response:
        data = response.read()

    return data


# ============================================================
# キーワード周辺を取得
# ============================================================

def get_snippets(
    text,
    pattern,
    radius=1000,
    max_count=30
):

    results = []

    try:
        matches = list(
            re.finditer(
                pattern,
                text,
                re.IGNORECASE
            )
        )
    except re.error:
        return results

    for match in matches[:max_count]:

        start = max(
            0,
            match.start() - radius
        )

        end = min(
            len(text),
            match.end() + radius
        )

        results.append(
            text[start:end]
        )

    return results


# ============================================================
# URL候補抽出
# ============================================================

def extract_urls(text):

    urls = []

    patterns = [

        r'https?://[^"\'\s<>]+',

        r'["\'](/[^"\']*)["\']',

        r'["\']([^"\']*(?:api|ajax|odds|race)[^"\']*)["\']',

    ]

    for pattern in patterns:

        try:
            matches = re.findall(
                pattern,
                text,
                re.IGNORECASE
            )
        except re.error:
            continue

        for item in matches:

            if isinstance(item, tuple):
                item = item[0]

            item = item.strip()

            if not item:
                continue

            if item not in urls:
                urls.append(item)

    return urls


# ============================================================
# API関連文字列
# ============================================================

def extract_strings(text):

    strings = re.findall(
        r'["\']([^"\']{1,1000})["\']',
        text
    )

    candidates = []

    keywords = [
        "api",
        "ajax",
        "odds",
        "race",
        "race_id",
        "raceid",
        "json",
        "indexdb",
        "get",
        "post",
        "url",
        "method",
        "data",
        "param",
        "params",
        "shikibetsu",
        "bet",
    ]

    for value in strings:

        if any(
            keyword.lower() in value.lower()
            for keyword in keywords
        ):

            if value not in candidates:
                candidates.append(value)

    return candidates


# ============================================================
# 関数名候補
# ============================================================

def find_function_candidates(text):

    candidates = []

    patterns = [

        r'function\s+([A-Za-z0-9_$]+)\s*\(',

        r'([A-Za-z0-9_$]+)\s*=\s*function\s*\(',

        r'this\.([A-Za-z0-9_$]+)\s*=\s*function',

        r'prototype\.([A-Za-z0-9_$]+)\s*=\s*function',

    ]

    for pattern in patterns:

        try:
            matches = re.findall(
                pattern,
                text
            )
        except re.error:
            continue

        for value in matches:

            if value not in candidates:
                candidates.append(value)

    return candidates


# ============================================================
# API通信らしきコードを抽出
# ============================================================

def find_api_code(text):

    keywords = [

        "AplApiRace",

        "get_race_odds",

        "race_odds",

        "odds",

        "api_url",

        "XMLHttpRequest",

        "$.ajax",

        "$.get",

        "$.post",

        "ajax",

        "open(",

        "send(",

        "method",

        "GET",

        "POST",

        "race_id",

        "raceId",

        "jsonp",

        "json",

        "indexdb",

        "indexedDB",

    ]

    results = []

    for keyword in keywords:

        snippets = get_snippets(
            text,
            re.escape(keyword),
            radius=1200,
            max_count=10
        )

        if not snippets:
            continue

        results.append("")
        results.append("=" * 70)
        results.append(
            f"【{keyword} 周辺コード】"
        )
        results.append("=" * 70)

        for number, snippet in enumerate(
            snippets,
            start=1
        ):

            snippet = (
                snippet
                .replace("\r", " ")
                .replace("\n", " ")
            )

            results.append(
                f"\n--- snippet {number} ---"
            )

            results.append(snippet)

    return results


# ============================================================
# main
# ============================================================

def main():

    print("=" * 70)
    print("004 netkeirin race API JavaScript 解析")
    print("=" * 70)
    print()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # JS取得
    # --------------------------------------------------------

    try:

        js_data = download_js(
            TARGET_JS_URL
        )

    except Exception as e:

        print("JavaScript取得失敗")
        print()
        print(
            type(e).__name__
        )
        print(
            str(e)
        )
        print()

        return

    print(
        f"JavaScript取得成功 : "
        f"{len(js_data):,} bytes"
    )

    try:

        js_text = js_data.decode(
            "utf-8"
        )

    except UnicodeDecodeError:

        js_text = js_data.decode(
            "utf-8",
            errors="ignore"
        )

    print(
        f"JavaScript文字数 : "
        f"{len(js_text):,}"
    )

    print()

    # --------------------------------------------------------
    # 保存
    # --------------------------------------------------------

    JS_PATH.write_text(
        js_text,
        encoding="utf-8"
    )

    print("JavaScript保存 OK")
    print(JS_PATH)
    print()

    # --------------------------------------------------------
    # 解析結果
    # --------------------------------------------------------

    output = []

    output.append("=" * 70)
    output.append(
        "004 netkeirin race API JavaScript 解析結果"
    )
    output.append("=" * 70)
    output.append("")

    output.append(
        f"RACE_ID : {RACE_ID}"
    )

    output.append(
        f"JS URL : {TARGET_JS_URL}"
    )

    output.append(
        f"JS文字数 : {len(js_text):,}"
    )

    output.append("")

    # --------------------------------------------------------
    # キーワード件数
    # --------------------------------------------------------

    output.append("=" * 70)
    output.append("【1】キーワード件数")
    output.append("=" * 70)

    keywords = [

        "AplApiRace",
        "get_race_odds",
        "race_odds",
        "api",
        "api_url",
        "ajax",
        "XMLHttpRequest",
        "$.ajax",
        "$.get",
        "$.post",
        "fetch",
        "odds",
        "race_id",
        "raceId",
        "jsonp",
        "json",
        "indexdb",
        "indexedDB",
        "open(",
        "send(",
        "GET",
        "POST",
        "method",
        "params",
        "data",

    ]

    for keyword in keywords:

        count = len(
            re.findall(
                re.escape(keyword),
                js_text,
                re.IGNORECASE
            )
        )

        output.append(
            f"{keyword:<20} : {count}件"
        )

    output.append("")

    # --------------------------------------------------------
    # URL候補
    # --------------------------------------------------------

    output.append("=" * 70)
    output.append("【2】URL候補")
    output.append("=" * 70)

    urls = extract_urls(
        js_text
    )

    for number, url in enumerate(
        urls,
        start=1
    ):

        output.append(
            f"{number:03d}: {url}"
        )

    output.append("")

    output.append(
        f"URL候補数 : {len(urls)}"
    )

    output.append("")

    # --------------------------------------------------------
    # 関数名
    # --------------------------------------------------------

    output.append("=" * 70)
    output.append("【3】関数名候補")
    output.append("=" * 70)

    functions = find_function_candidates(
        js_text
    )

    for number, name in enumerate(
        functions,
        start=1
    ):

        output.append(
            f"{number:03d}: {name}"
        )

    output.append("")

    output.append(
        f"関数候補数 : {len(functions)}"
    )

    output.append("")

    # --------------------------------------------------------
    # API関連コード
    # --------------------------------------------------------

    output.append("=" * 70)
    output.append(
        "【4】API / AplApiRace / オッズ関連コード"
    )
    output.append("=" * 70)

    api_code = find_api_code(
        js_text
    )

    output.extend(
        api_code
    )

    output.append("")

    # --------------------------------------------------------
    # API関連文字列
    # --------------------------------------------------------

    output.append("=" * 70)
    output.append(
        "【5】API関連文字列候補"
    )
    output.append("=" * 70)

    strings = extract_strings(
        js_text
    )

    for number, value in enumerate(
        strings,
        start=1
    ):

        output.append(
            f"{number:03d}: {value}"
        )

    output.append("")

    output.append(
        f"文字列候補数 : {len(strings)}"
    )

    output.append("")

    # --------------------------------------------------------
    # 重要調査ポイント
    # --------------------------------------------------------

    output.append("=" * 70)
    output.append(
        "【6】今回特に確認したいもの"
    )
    output.append("=" * 70)

    output.append(
        "1. AplApiRace の定義"
    )

    output.append(
        "2. AplApiRace の constructor"
    )

    output.append(
        "3. odds取得用メソッド"
    )

    output.append(
        "4. API URL"
    )

    output.append(
        "5. race_id の渡し方"
    )

    output.append(
        "6. GET / POST"
    )

    output.append(
        "7. パラメータ名"
    )

    output.append(
        "8. JSONの返却形式"
    )

    output.append(
        "9. 3連単を示す番号"
    )

    output.append("")

    # --------------------------------------------------------
    # 次のステップ
    # --------------------------------------------------------

    output.append("=" * 70)
    output.append(
        "【7】次のステップ"
    )
    output.append("=" * 70)

    output.append(
        "この解析結果から、"
    )

    output.append(
        "AplApiRaceが実際にアクセスするAPIを特定します。"
    )

    output.append("")

    output.append(
        "APIが特定できたら、次のプログラムで"
    )

    output.append(
        "実際にrace_idを指定して"
    )

    output.append(
        "3連単210通りのオッズを取得します。"
    )

    output.append("")

    # --------------------------------------------------------
    # 保存
    # --------------------------------------------------------

    ANALYSIS_PATH.write_text(
        "\n".join(output),
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # 完了
    # --------------------------------------------------------

    print("=" * 70)
    print("解析完了")
    print("=" * 70)
    print()

    print("JavaScript:")
    print(JS_PATH)
    print()

    print("解析結果:")
    print(ANALYSIS_PATH)
    print()

    print(
        "このTXTの内容を貼ってください。"
    )

    print(
        "次にAPIを特定して005を作ります。"
    )


if __name__ == "__main__":
    main()