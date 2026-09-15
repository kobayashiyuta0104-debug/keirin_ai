# -*- coding: utf-8 -*-

"""
002_find_netkeirin_odds_source.py

目的：
保存済みのnetkeirinオッズHTMLを調べ、
3連単オッズを取得している可能性のある
JavaScript / API / Ajax / JSON の情報を探す。

※ この段階ではオッズそのものの抽出は行わない。
※ 001_collect_netkeirin_odds.py は変更しない。

対象HTML：
C:\\競輪AI\\data_official\\odds_test\\202609081312_odds.html

出力：
C:\\競輪AI\\data_official\\odds_test\\202609081312_odds_source_debug.txt
"""

from pathlib import Path
import re
from html.parser import HTMLParser


# =========================================================
# 設定
# =========================================================

RACE_ID = "202609081312"

HTML_PATH = Path(
    rf"C:\競輪AI\data_official\odds_test\{RACE_ID}_odds.html"
)

OUTPUT_PATH = Path(
    rf"C:\競輪AI\data_official\odds_test\{RACE_ID}_odds_source_debug.txt"
)


# =========================================================
# HTML解析用
# =========================================================

class ScriptParser(HTMLParser):
    """HTMLからscriptタグの情報を取得する"""

    def __init__(self):
        super().__init__()
        self.script_srcs = []
        self.inline_scripts = []

        self.in_script = False
        self.current_src = None
        self.current_script = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "script":
            return

        attrs_dict = dict(attrs)

        self.in_script = True
        self.current_src = attrs_dict.get("src")
        self.current_script = []

    def handle_data(self, data):
        if self.in_script:
            self.current_script.append(data)

    def handle_endtag(self, tag):
        if tag.lower() != "script":
            return

        if self.current_src:
            self.script_srcs.append(self.current_src)
        else:
            script_text = "".join(self.current_script).strip()

            if script_text:
                self.inline_scripts.append(script_text)

        self.in_script = False
        self.current_src = None
        self.current_script = []


# =========================================================
# 周辺文字列を取得
# =========================================================

def get_snippets(text, pattern, radius=300, max_count=20):
    """
    指定文字列の前後を抜き出す
    """

    snippets = []

    try:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
    except re.error:
        return snippets

    for match in matches[:max_count]:
        start = max(0, match.start() - radius)
        end = min(len(text), match.end() + radius)

        snippet = text[start:end]

        snippets.append(snippet)

    return snippets


# =========================================================
# URL候補抽出
# =========================================================

def extract_urls(text):
    """
    HTML / JavaScript内に存在するURLらしき文字列を抽出
    """

    urls = []

    patterns = [
        r'https?://[^"\'>\s]+',
        r'["\']([^"\']*(?:odds|ajax|api|json)[^"\']*)["\']',
        r'["\']([^"\']*race[^"\']*)["\']',
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

            if item and item not in urls:
                urls.append(item)

    return urls


# =========================================================
# メイン
# =========================================================

def main():

    print("=" * 70)
    print("002 netkeirin オッズ取得元調査")
    print("=" * 70)

    print()
    print(f"RACE_ID     : {RACE_ID}")
    print(f"HTML_PATH   : {HTML_PATH}")
    print(f"OUTPUT_PATH : {OUTPUT_PATH}")
    print()

    # -----------------------------------------------------
    # HTML確認
    # -----------------------------------------------------

    if not HTML_PATH.exists():

        print("ERROR：HTMLファイルがありません。")
        print()
        print(HTML_PATH)
        return

    print("HTMLファイル確認 OK")

    html = HTML_PATH.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    print(f"HTML文字数 : {len(html):,}")
    print()

    # -----------------------------------------------------
    # HTML解析
    # -----------------------------------------------------

    parser = ScriptParser()

    parser.feed(html)

    script_srcs = parser.script_srcs
    inline_scripts = parser.inline_scripts

    print(f"外部script数 : {len(script_srcs)}")
    print(f"inline script数 : {len(inline_scripts)}")
    print()

    # -----------------------------------------------------
    # 検索キーワード
    # -----------------------------------------------------

    keywords = [
        "odds",
        "race_odds",
        "RaceOdds",
        "ajax",
        "fetch",
        "XMLHttpRequest",
        "$.ajax",
        "$.get",
        "$.post",
        "json",
        "api",
        "race_id",
        "raceId",
        "raceID",
        "odds_data",
        "oddsData",
        "odds_table",
        "bet",
    ]

    # -----------------------------------------------------
    # 結果を保存する文字列
    # -----------------------------------------------------

    output = []

    output.append("=" * 70)
    output.append("002 netkeirin オッズ取得元調査")
    output.append("=" * 70)
    output.append("")

    output.append(f"RACE_ID = {RACE_ID}")
    output.append(f"HTML_PATH = {HTML_PATH}")
    output.append(f"HTML文字数 = {len(html):,}")
    output.append("")

    # -----------------------------------------------------
    # script src一覧
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append("【1】外部JavaScript一覧")
    output.append("=" * 70)

    for i, src in enumerate(script_srcs, 1):

        output.append(f"{i:03d}: {src}")

    output.append("")

    # -----------------------------------------------------
    # HTML全体に対するキーワード検索
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append("【2】HTML全体のキーワード検索")
    output.append("=" * 70)

    for keyword in keywords:

        count = len(
            re.findall(
                re.escape(keyword),
                html,
                re.IGNORECASE
            )
        )

        output.append(
            f"{keyword:<20} : {count}件"
        )

    output.append("")

    # -----------------------------------------------------
    # 外部script URLからオッズ関連を探す
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append("【3】外部JavaScript URLのオッズ/API関連候補")
    output.append("=" * 70)

    for src in script_srcs:

        if re.search(
            r"odds|ajax|api|json|race",
            src,
            re.IGNORECASE
        ):

            output.append(src)

    output.append("")

    # -----------------------------------------------------
    # inline script検索
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append("【4】inline JavaScriptの調査")
    output.append("=" * 70)

    found_inline = 0

    for i, script in enumerate(inline_scripts, 1):

        matched_keywords = []

        for keyword in keywords:

            if re.search(
                re.escape(keyword),
                script,
                re.IGNORECASE
            ):

                matched_keywords.append(keyword)

        if matched_keywords:

            found_inline += 1

            output.append("")
            output.append("-" * 70)
            output.append(
                f"INLINE SCRIPT #{i}"
            )
            output.append(
                "該当キーワード : "
                + ", ".join(matched_keywords)
            )
            output.append("-" * 70)

            # 長すぎるscriptをそのまま出さない
            if len(script) <= 10000:

                output.append(script)

            else:

                output.append(
                    script[:10000]
                )

                output.append(
                    "\n・・・長いため10000文字で切っています・・・"
                )

    output.append("")
    output.append(
        f"キーワード該当inline script数 : {found_inline}"
    )
    output.append("")

    # -----------------------------------------------------
    # HTML内のURL候補
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append("【5】HTML / JavaScript内のURL候補")
    output.append("=" * 70)

    urls = extract_urls(html)

    for i, url in enumerate(urls, 1):

        output.append(
            f"{i:03d}: {url}"
        )

    output.append("")
    output.append(
        f"URL候補数 : {len(urls)}"
    )
    output.append("")

    # -----------------------------------------------------
    # キーワード周辺
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append("【6】重要キーワード周辺のHTML")
    output.append("=" * 70)

    important_keywords = [
        "odds",
        "race_odds",
        "RaceOdds",
        "ajax",
        "fetch",
        "XMLHttpRequest",
        "json",
        "api",
        "race_id",
        "raceId",
        "odds_data",
        "oddsData",
    ]

    for keyword in important_keywords:

        snippets = get_snippets(
            html,
            re.escape(keyword),
            radius=500,
            max_count=10
        )

        if not snippets:
            continue

        output.append("")
        output.append("-" * 70)
        output.append(
            f"【{keyword}】"
        )
        output.append("-" * 70)

        for n, snippet in enumerate(snippets, 1):

            output.append(
                f"\n--- {keyword} snippet {n} ---"
            )

            # 改行を整理
            snippet = snippet.replace(
                "\r",
                " "
            ).replace(
                "\n",
                " "
            )

            output.append(snippet)

    output.append("")

    # -----------------------------------------------------
    # data-* 属性調査
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append("【7】data-* 属性のオッズ/API関連候補")
    output.append("=" * 70)

    data_attributes = re.findall(
        r'\s(data-[a-zA-Z0-9_-]+)\s*=\s*["\']([^"\']*)["\']',
        html
    )

    found_data = []

    for name, value in data_attributes:

        if re.search(
            r"odds|race|api|ajax|json|bet",
            name + " " + value,
            re.IGNORECASE
        ):

            item = f'{name}="{value}"'

            if item not in found_data:
                found_data.append(item)

    for item in found_data:

        output.append(item)

    output.append("")
    output.append(
        f"該当data-*属性数 : {len(found_data)}"
    )
    output.append("")

    # -----------------------------------------------------
    # HTML内のscriptタグ周辺
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append("【8】scriptタグ情報")
    output.append("=" * 70)

    output.append(
        f"scriptタグ総数 : {len(script_srcs) + len(inline_scripts)}"
    )

    output.append(
        f"外部script     : {len(script_srcs)}"
    )

    output.append(
        f"inline script  : {len(inline_scripts)}"
    )

    output.append("")

    # -----------------------------------------------------
    # 最終メモ
    # -----------------------------------------------------

    output.append("=" * 70)
    output.append("【9】今回の調査について")
    output.append("=" * 70)

    output.append(
        "このプログラムでは、まだ3連単オッズの抽出は行っていません。"
    )

    output.append(
        "目的は、netkeirinがオッズをどこから取得しているのかを特定することです。"
    )

    output.append(
        "外部JavaScript、Ajax、fetch、JSON、APIなどの情報を確認してください。"
    )

    output.append("")

    # -----------------------------------------------------
    # ファイル保存
    # -----------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT_PATH.write_text(
        "\n".join(output),
        encoding="utf-8"
    )

    # -----------------------------------------------------
    # 画面表示
    # -----------------------------------------------------

    print("=" * 70)
    print("調査完了")
    print("=" * 70)

    print()
    print(f"外部script数      : {len(script_srcs)}")
    print(f"inline script数    : {len(inline_scripts)}")
    print(f"URL候補数          : {len(urls)}")
    print(f"data-*候補数       : {len(found_data)}")
    print()

    print("結果ファイル：")
    print(OUTPUT_PATH)

    print()
    print("このTXTの内容を貼ってください。")
    print("次に、実際のオッズ取得元を特定します。")


# =========================================================
# 実行
# =========================================================

if __name__ == "__main__":
    main()