# -*- coding: utf-8 -*-

"""
014_find_jsj048_page.py

目的：
KEIRIN.JP内で JSJ048 を利用している実際のページを探す。

調査対象：
・PC0101_c.js
・sh_hidden2
・shCcp
・shCurrentDisp
・shParentDisp
・kaisaibikbn
・JSJ048
・chgRaceList
・jsj048JSONRequest

今回は「ページ探索のみ」。
Odds取得処理は行わない。
"""

import os
import re
import time
import hashlib
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.request import Request, urlopen


# ============================================================
# 設定
# ============================================================

BASE_URL = "https://keirin.jp"

START_URLS = [
    "https://keirin.jp/pc/top",
    "https://keirin.jp/pc/jyosellinfo?jocd=22",
]

MAX_PAGES = 40
TIMEOUT = 15
SLEEP_SEC = 0.3

OUTPUT_DIR = r"C:\競輪AI\data_official\historical\oddspark_test\014_jsj048_search"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# HTTP
# ============================================================

def fetch(url):
    """HTMLを取得"""

    try:
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
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,*/*;q=0.8"
                ),
            },
        )

        with urlopen(req, timeout=TIMEOUT) as response:
            data = response.read()

            content_type = response.headers.get_content_charset()

            if content_type:
                encoding = content_type
            else:
                encoding = "utf-8"

            try:
                text = data.decode(encoding, errors="replace")
            except Exception:
                text = data.decode("utf-8", errors="replace")

            return response.status, response.geturl(), text

    except Exception as e:
        return None, url, f"__ERROR__ {e}"


# ============================================================
# URL
# ============================================================

def normalize_url(base_url, href):
    """相対URLを絶対URLへ変換"""

    if not href:
        return None

    href = href.strip()

    if href.startswith("#"):
        return None

    if href.lower().startswith(("javascript:", "mailto:", "tel:")):
        return None

    url = urljoin(base_url, href)

    url, _ = urldefrag(url)

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return None

    if parsed.netloc != "keirin.jp":
        return None

    # KEIRIN.JPのPCページだけを見る
    if not parsed.path.startswith("/pc/"):
        return None

    return url


# ============================================================
# HTML解析
# ============================================================

def extract_links(base_url, html):
    """HTMLから同一サイトのPCページへのリンクを抽出"""

    links = set()

    pattern = re.compile(
        r'''(?:href|action)\s*=\s*["']([^"']+)["']''',
        re.IGNORECASE
    )

    for href in pattern.findall(html):
        url = normalize_url(base_url, href)

        if url:
            links.add(url)

    return links


def extract_script_urls(base_url, html):
    """script srcを抽出"""

    scripts = set()

    pattern = re.compile(
        r'''<script[^>]+src\s*=\s*["']([^"']+)["']''',
        re.IGNORECASE
    )

    for src in pattern.findall(html):
        scripts.add(urljoin(base_url, src))

    return scripts


# ============================================================
# hidden値取得
# ============================================================

def get_value_by_id(html, target_id):
    """id属性からvalueを取得"""

    patterns = [
        rf'<input[^>]*id\s*=\s*["\']{re.escape(target_id)}["\'][^>]*value\s*=\s*["\']([^"\']*)["\']',
        rf'<input[^>]*value\s*=\s*["\']([^"\']*)["\'][^>]*id\s*=\s*["\']{re.escape(target_id)}["\']',

        rf'<[^>]*id\s*=\s*["\']{re.escape(target_id)}["\'][^>]*value\s*=\s*["\']([^"\']*)["\']',
        rf'<[^>]*value\s*=\s*["\']([^"\']*)["\'][^>]*id\s*=\s*["\']{re.escape(target_id)}["\']',
    ]

    for pattern in patterns:
        m = re.search(pattern, html, re.IGNORECASE)

        if m:
            return m.group(1)

    return None


def get_value_by_name(html, target_name):
    """name属性からvalueを取得"""

    patterns = [
        rf'<input[^>]*name\s*=\s*["\']{re.escape(target_name)}["\'][^>]*value\s*=\s*["\']([^"\']*)["\']',
        rf'<input[^>]*value\s*=\s*["\']([^"\']*)["\'][^>]*name\s*=\s*["\']{re.escape(target_name)}["\']',
    ]

    for pattern in patterns:
        m = re.search(pattern, html, re.IGNORECASE)

        if m:
            return m.group(1)

    return None


# ============================================================
# ページ評価
# ============================================================

def inspect_page(url, html):
    """JSJ048関連情報を調査"""

    scripts = extract_script_urls(url, html)

    script_names = [
        os.path.basename(urlparse(x).path)
        for x in scripts
    ]

    markers = {
        "PC0101_c.js": "PC0101_c.js" in html
        or any("PC0101_c.js" in x for x in scripts),

        "sh_hidden2": "sh_hidden2" in html,
        "shCcp": "shCcp" in html,
        "shCurrentDisp": "shCurrentDisp" in html,
        "shParentDisp": "shParentDisp" in html,

        "kaisaibikbn": "kaisaibikbn" in html,
        "JSJ048": "JSJ048" in html,
        "chgRaceList": "chgRaceList" in html,
        "jsj048JSONRequest": "jsj048JSONRequest" in html,
    }

    values = {
        "sh_hidden1": get_value_by_id(html, "sh_hidden1"),
        "sh_hidden2": get_value_by_id(html, "sh_hidden2"),
        "shCcp": get_value_by_id(html, "shCcp"),
        "shCurrentDisp": get_value_by_id(html, "shCurrentDisp"),
        "shParentDisp": get_value_by_id(html, "shParentDisp"),

        "sh_hidden1_name": get_value_by_name(html, "sh_hidden1"),
        "sh_hidden2_name": get_value_by_name(html, "sh_hidden2"),
        "shCcp_name": get_value_by_name(html, "shCcp"),
        "shCurrentDisp_name": get_value_by_name(html, "shCurrentDisp"),
    }

    score = 0

    if markers["PC0101_c.js"]:
        score += 10

    if markers["sh_hidden2"]:
        score += 5

    if markers["shCcp"]:
        score += 5

    if markers["shCurrentDisp"]:
        score += 5

    if markers["shParentDisp"]:
        score += 3

    if markers["kaisaibikbn"]:
        score += 3

    if markers["JSJ048"]:
        score += 5

    if markers["chgRaceList"]:
        score += 3

    if markers["jsj048JSONRequest"]:
        score += 5

    return {
        "url": url,
        "scripts": script_names,
        "markers": markers,
        "values": values,
        "score": score,
    }


# ============================================================
# 保存
# ============================================================

def save_html(url, html, number):
    """調査対象HTMLを保存"""

    digest = hashlib.md5(url.encode("utf-8")).hexdigest()[:10]

    filename = f"{number:03d}_{digest}.html"

    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w", encoding="utf-8", errors="replace") as f:
        f.write(html)

    return path


# ============================================================
# リンク優先順位
# ============================================================

def link_priority(url):
    """
    race / odds関連ページを優先する。
    """

    lower = url.lower()

    score = 0

    keywords = [
        ("race", 10),
        ("odds", 10),
        ("jyosell", 8),
        ("jyo", 5),
        ("kaisai", 5),
        ("result", 4),
        ("program", 4),
    ]

    for keyword, point in keywords:
        if keyword in lower:
            score += point

    return -score


# ============================================================
# メイン
# ============================================================

def main():

    print("=" * 70)
    print("014 JSJ048 実使用ページ探索")
    print("=" * 70)

    print()
    print("開始URL:")

    for url in START_URLS:
        print(" ", url)

    print()
    print(f"最大探索ページ数: {MAX_PAGES}")
    print()

    queue = deque(START_URLS)
    visited = set()

    results = []

    page_no = 0

    while queue and page_no < MAX_PAGES:

        # キューから取り出し
        url = queue.popleft()

        if url in visited:
            continue

        visited.add(url)

        page_no += 1

        print("-" * 70)
        print(f"[{page_no}/{MAX_PAGES}]")
        print(url)

        status, final_url, html = fetch(url)

        if status is None:
            print("  HTTP ERROR")
            print(" ", html)
            continue

        print(f"  HTTP: {status}")
        print(f"  FINAL: {final_url}")
        print(f"  HTML: {len(html):,} bytes")

        if html.startswith("__ERROR__"):
            continue

        # 調査
        result = inspect_page(final_url, html)

        results.append(result)

        print()
        print("  JSJ048関連:")

        for key, value in result["markers"].items():
            if value:
                print(f"    ★ {key}")

        print()
        print("  hidden / parameter:")

        for key, value in result["values"].items():
            if value is not None:
                print(f"    {key} = {value}")

        print()
        print(f"  SCORE: {result['score']}")

        # 候補ページならHTML保存
        if result["score"] >= 5:
            path = save_html(
                final_url,
                html,
                page_no
            )

            print()
            print("  ★ 調査候補としてHTML保存")
            print(f"    {path}")

        # リンク抽出
        links = extract_links(final_url, html)

        # 未訪問のみ
        new_links = [
            x for x in links
            if x not in visited
        ]

        # 関連ページを優先
        new_links.sort(key=link_priority)

        for link in new_links:
            if link not in queue:
                queue.append(link)

        print()
        print(f"  発見リンク: {len(links)}")
        print(f"  未訪問候補: {len(new_links)}")
        print(f"  キュー残り: {len(queue)}")

        time.sleep(SLEEP_SEC)

    # ========================================================
    # 結果まとめ
    # ========================================================

    print()
    print()
    print("=" * 70)
    print("探索終了")
    print("=" * 70)

    print(f"訪問ページ数: {len(visited)}")
    print(f"調査結果数: {len(results)}")

    # スコア順
    results_sorted = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    print()
    print("=" * 70)
    print("JSJ048関連候補ページ")
    print("=" * 70)

    found = False

    for result in results_sorted:

        if result["score"] <= 0:
            continue

        found = True

        print()
        print(f"SCORE: {result['score']}")
        print(result["url"])

        active = [
            key
            for key, value in result["markers"].items()
            if value
        ]

        if active:
            print("  MARKER:")
            for x in active:
                print(f"    - {x}")

        print("  PARAMETER:")

        for key, value in result["values"].items():

            if value is not None:
                print(f"    {key} = {value}")

    if not found:
        print()
        print("JSJ048関連ページは見つかりませんでした。")

    # ========================================================
    # 結果ファイル
    # ========================================================

    result_path = os.path.join(
        OUTPUT_DIR,
        "014_result.txt"
    )

    with open(
        result_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "014 JSJ048 実使用ページ探索結果\n"
        )

        f.write("=" * 70 + "\n\n")

        f.write(
            f"訪問ページ数: {len(visited)}\n"
        )

        f.write(
            f"調査結果数: {len(results)}\n\n"
        )

        for result in results_sorted:

            if result["score"] <= 0:
                continue

            f.write(
                f"SCORE: {result['score']}\n"
            )

            f.write(
                f"URL: {result['url']}\n"
            )

            f.write("MARKER:\n")

            for key, value in result["markers"].items():

                if value:
                    f.write(
                        f"  - {key}\n"
                    )

            f.write("PARAMETER:\n")

            for key, value in result["values"].items():

                if value is not None:
                    f.write(
                        f"  {key} = {value}\n"
                    )

            f.write("\n")

    print()
    print("結果ファイル:")
    print(result_path)

    print()
    print("=" * 70)
    print("014 完了")
    print("=" * 70)


if __name__ == "__main__":
    main()