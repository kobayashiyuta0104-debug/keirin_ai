# -*- coding: utf-8 -*-

"""
003_analyze_race_odds_js.py

目的：
netkeirinのオッズページで使用されている
race_odds.min.js を取得して解析する。

今回の目的は、
「3連単オッズをどのAPIから取得しているのか」
を特定すること。

この段階では、まだ実際のオッズ取得は行わない。

対象：
2026/09/08 いわき平 12R
race_id = 202609081312

入力：
C:\\競輪AI\\data_official\\odds_test\\202609081312_odds.html

取得対象JS：
https://cdnv2.netkeiba.com/keirin/race/odds/tags/race_odds.min.js?20260408

出力：
C:\\競輪AI\\data_official\\odds_test\\
    202609081312_race_odds.min.js

    202609081312_js_analysis.txt
"""

from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urljoin
import re


# =========================================================
# 設定
# =========================================================

RACE_ID = "202609081312"

HTML_PATH = Path(
    rf"C:\競輪AI\data_official\odds_test\{RACE_ID}_odds.html"
)

OUTPUT_DIR = Path(
    r"C:\競輪AI\data_official\odds_test"
)

JS_PATH = OUTPUT_DIR / f"{RACE_ID}_race_odds.min.js"

ANALYSIS_PATH = OUTPUT_DIR / f"{RACE_ID}_js_analysis.txt"


# =========================================================
# 対象JavaScript
# =========================================================

TARGET_JS_URL = (
    "https://cdnv2.netkeiba.com/"
    "keirin/race/odds/tags/race_odds.min.js?20260408"
)


# =========================================================
# JS取得
# =========================================================

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
        "Referer": (
            f"https://keirin.netkeiba.com/"
            f"race/odds/?race_id={RACE_ID}"
        ),
    }

    request = Request(
        url,
        headers=headers
    )

    with urlopen(request, timeout=30) as response:

        data = response.read()

    return data


# =========================================================
# 周辺文字列取得
# =========================================================

def get_snippets(
    text,
    pattern,
    radius=500,
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

        snippet = text[start:end]

        results.append(
            snippet
        )

    return results


# =========================================================
# URL抽出
# =========================================================

def extract_urls(text):

    urls = []

    patterns = [

        # 完全URL
        r'https?://[^"\'\s<>]+',

        # /api/... のような相対URL
        r'["\'](/[^"\']*(?:api|ajax|odds)[^"\']*)["\']',

        # API URLっぽい文字列
        r'["\']([^"\']*(?:api|ajax|odds)[^"\']*)["\']',

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


# =========================================================
# API関連行を探す
# =========================================================

def find_api_lines(text):

    lines = text.splitlines()

    results = []

    keywords = [
        "api",
        "ajax",
        "odds",
        "race_id",
        "raceid",
        "raceID",
        "jsonp",
        "json",
        "XMLHttpRequest",
        "$.ajax",
        "$.get",
        "$.post",
        "url:",
        "data:",
        "GET",
        "POST",
    ]

    for line_number, line in enumerate(
        lines,
        start=1
    ):

        line_lower = line.lower()

        matched = False

        for keyword in keywords:

            if keyword.lower() in line_lower:

                matched = True
                break

        if matched:

            results.append(
                (line_number, line)
            )

    return results


# =========================================================
# 文字列候補を探す
# =========================================================

def find_string_candidates(text):

    strings = re.findall(
        r'["\']([^"\']{1,500})["\']',
        text
    )

    candidates = []

    for value in strings:

        if re.search(
            r"api|ajax|odds|race|json|bet|ticket",
            value,
            re.IGNORECASE
        ):

            if value not in candidates:

                candidates.append(value)

    return candidates


# =========================================================
# メイン
# =========================================================

def main():

    print("=" * 70)
    print("003 netkeirin race_odds.min.js 解析")
    print("=" * 70)
    print()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # HTML確認
    # -----------------------------------------------------

    if not HTML_PATH.exists():

        print("ERROR")
        print()
        print("対象HTMLがありません。")
        print(HTML_PATH)
        print()

        return

    print("対象HTML確認 OK")
    print(HTML_PATH)
    print()

    # -----------------------------------------------------
    # JS取得
    # -----------------------------------------------------

    try:

        js_data = download_js(
            TARGET_JS_URL
        )

    except Exception as e:

        print("JavaScript取得失敗")
        print()
        print(type(e).__name__)
        print(str(e))
        print()

        return

    print(
        f"JavaScript取得成功 : {len(js_data):,} bytes"
    )

    # -----------------------------------------------------
    # 文字コード
    # -----------------------------------------------------

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
        f"JavaScript文字数 : {len(js_text):,}"
    )

    print()

    # -----------------------------------------------------
    # JS保存
    # -----------------------------------------------------

    JS_PATH.write_text(
        js_text,
        encoding="utf-8"
    )

    print("JavaScript保存 OK")
    print(JS_PATH)
    print()

    # -----------------------------------------------------
    # 調査
    # -----------------------------------------------------

    output = []

    output.append("=" * 70)
    output.append(
        "003 netkeirin race_odds.min.js 解析結果"
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

    # -----------------------------------------------------
    # キーワード件数
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append(
        "【1】キーワード件数"
    )
    output.append("=" * 70)

    keywords = [
        "api",
        "ajax",
        "odds",
        "race_odds",
        "RaceOdds",
        "race_id",
        "raceId",
        "raceID",
        "jsonp",
        "json",
        "XMLHttpRequest",
        "$.ajax",
        "$.get",
        "$.post",
        "fetch",
        "bet",
        "ticket",
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

    # -----------------------------------------------------
    # URL
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append(
        "【2】URL候補"
    )
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

    # -----------------------------------------------------
    # API関連行
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append(
        "【3】API / Ajax / オッズ関連コード"
    )
    output.append("=" * 70)

    api_lines = find_api_lines(
        js_text
    )

    output.append(
        f"該当行数 : {len(api_lines)}"
    )

    output.append("")

    for line_number, line in api_lines:

        output.append(
            f"[{line_number}] {line}"
        )

    output.append("")

    # -----------------------------------------------------
    # 周辺コード
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append(
        "【4】重要キーワード周辺コード"
    )
    output.append("=" * 70)

    important_patterns = [

        "api",

        "odds",

        "race_odds",

        "race_id",

        "raceId",

        "ajax",

        "XMLHttpRequest",

        "jsonp",

        "json",

        "fetch",

    ]

    for keyword in important_patterns:

        snippets = get_snippets(
            js_text,
            re.escape(keyword),
            radius=700,
            max_count=10
        )

        if not snippets:

            continue

        output.append("")
        output.append(
            "-" * 70
        )
        output.append(
            f"【{keyword}】"
        )
        output.append(
            "-" * 70
        )

        for number, snippet in enumerate(
            snippets,
            start=1
        ):

            snippet = (
                snippet
                .replace("\r", " ")
                .replace("\n", " ")
            )

            output.append(
                f"\n--- snippet {number} ---"
            )

            output.append(
                snippet
            )

    output.append("")

    # -----------------------------------------------------
    # 文字列候補
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append(
        "【5】API / オッズ関連文字列候補"
    )
    output.append("=" * 70)

    candidates = find_string_candidates(
        js_text
    )

    for number, value in enumerate(
        candidates,
        start=1
    ):

        output.append(
            f"{number:03d}: {value}"
        )

    output.append("")

    output.append(
        f"文字列候補数 : {len(candidates)}"
    )

    output.append("")

    # -----------------------------------------------------
    # 先頭・末尾情報
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append(
        "【6】JavaScript基本情報"
    )
    output.append("=" * 70)

    output.append(
        f"文字数 : {len(js_text):,}"
    )

    output.append(
        f"行数 : {len(js_text.splitlines()):,}"
    )

    output.append("")

    # -----------------------------------------------------
    # 結論
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append(
        "【7】次の調査ポイント"
    )
    output.append("=" * 70)

    output.append(
        "この結果から、3連単オッズ取得に使用されている"
    )

    output.append(
        "API / URL / パラメータを特定します。"
    )

    output.append("")

    output.append(
        "特に以下を確認してください。"
    )

    output.append(
        "・api/race/"
    )

    output.append(
        "・odds"
    )

    output.append(
        "・race_id"
    )

    output.append(
        "・ajax"
    )

    output.append(
        "・jsonp"
    )

    output.append(
        "・json"
    )

    output.append("")

    output.append(
        "APIが特定できれば、次のプログラムで"
    )

    output.append(
        "3連単210通りのオッズ取得を行います。"
    )

    output.append("")

    # -----------------------------------------------------
    # 保存
    # -----------------------------------------------------

    ANALYSIS_PATH.write_text(
        "\n".join(output),
        encoding="utf-8"
    )

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
        "次にAPIを特定して004を作ります。"
    )


# =========================================================
# 実行
# =========================================================

if __name__ == "__main__":
    main()