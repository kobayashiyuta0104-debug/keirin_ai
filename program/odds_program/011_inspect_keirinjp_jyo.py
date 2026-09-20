# -*- coding: utf-8 -*-

import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# ============================================================
# 調査対象
# ============================================================

BANK_CODE = "22"
BANK_NAME = "前橋"

BASE_URL = "https://keirin.jp"

TARGET_URL = (
    f"{BASE_URL}/pc/jyosellinfo"
    f"?jocd={BANK_CODE}"
)


# ============================================================
# 保存先
# ============================================================

SAVE_DIR = Path(
    r"C:\競輪AI\data_official\historical\keirinjp_odds_test"
)


# ============================================================
# HTTP設定
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja-JP,ja;q=0.9",
}


# ============================================================
# メイン
# ============================================================

def main():

    print("=" * 70)
    print("KEIRIN.JP 競輪場ページ調査")
    print("=" * 70)

    print(f"BANK_CODE : {BANK_CODE}")
    print(f"BANK_NAME : {BANK_NAME}")
    print()
    print("TARGET URL:")
    print(TARGET_URL)
    print()

    SAVE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    session = requests.Session()

    # ========================================================
    # ページ取得
    # ========================================================

    try:

        response = session.get(
            TARGET_URL,
            headers=HEADERS,
            timeout=30
        )

    except Exception as e:

        print("[ERROR] ページ取得失敗")
        print(e)
        return

    print("HTTP STATUS :", response.status_code)
    print("HTML SIZE   :", len(response.text))

    # ========================================================
    # HTML保存
    # ========================================================

    html_file = SAVE_DIR / "jyo_22.html"

    html_file.write_text(
        response.text,
        encoding="utf-8"
    )

    print()
    print("HTML保存先:")
    print(html_file)

    if response.status_code != 200:

        print()
        print("[ERROR] HTTP 200ではありません")
        return

    # ========================================================
    # BeautifulSoup
    # ========================================================

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # ========================================================
    # TITLE
    # ========================================================

    print()
    print("=" * 70)
    print("TITLE")
    print("=" * 70)

    if soup.title:

        print(
            soup.title.get_text(
                " ",
                strip=True
            )
        )

    else:

        print("TITLEなし")

    # ========================================================
    # SCRIPT一覧
    # ========================================================

    print()
    print("=" * 70)
    print("SCRIPT一覧")
    print("=" * 70)

    scripts = soup.find_all("script")

    print("SCRIPT COUNT :", len(scripts))

    for i, script in enumerate(scripts, 1):

        src = script.get("src")

        if src:

            print(
                f"[{i}] "
                f"{urljoin(BASE_URL, src)}"
            )

        else:

            text = script.get_text(
                " ",
                strip=True
            )

            if text:

                print(
                    f"[{i}] INLINE SCRIPT "
                    f"length={len(text)}"
                )

    # ========================================================
    # LINK一覧
    # ========================================================

    print()
    print("=" * 70)
    print("LINK調査")
    print("=" * 70)

    links = soup.find_all("a")

    print("LINK COUNT :", len(links))

    link_count = 0

    for link in links:

        href = link.get("href")

        if not href:
            continue

        text = link.get_text(
            " ",
            strip=True
        )

        full_url = urljoin(
            BASE_URL,
            href
        )

        link_count += 1

        print()
        print(f"[{link_count}]")
        print("TEXT :", text)
        print("HREF :", href)
        print("URL  :", full_url)

    # ========================================================
    # 重要キーワード調査
    # ========================================================

    print()
    print("=" * 70)
    print("重要キーワード調査")
    print("=" * 70)

    keywords = [
        "オッズ",
        "3連単",
        "単勝",
        "2車単",
        "2車複",
        "3連複",
        "レース",
        "開催",
        "race",
        "odds",
        "Odds",
        "JSJ",
        "ajax",
        "json",
        "api",
        "race_id",
        "jocd",
        "kaisaiBi",
    ]

    html_lower = response.text.lower()

    for keyword in keywords:

        count = html_lower.count(
            keyword.lower()
        )

        print(
            f"{keyword:<12} : {count}"
        )

    # ========================================================
    # FORM調査
    # ========================================================

    print()
    print("=" * 70)
    print("FORM調査")
    print("=" * 70)

    forms = soup.find_all("form")

    print("FORM COUNT :", len(forms))

    for i, form in enumerate(forms, 1):

        print()
        print(f"FORM {i}")

        print(
            "action :",
            form.get("action")
        )

        print(
            "method :",
            form.get("method")
        )

        inputs = form.find_all("input")

        for inp in inputs:

            print(
                "  type=",
                inp.get("type"),
                "name=",
                inp.get("name"),
                "value=",
                inp.get("value")
            )

    # ========================================================
    # URL候補抽出
    # ========================================================

    print()
    print("=" * 70)
    print("レース・オッズ関連URL候補")
    print("=" * 70)

    candidates = []

    for link in links:

        href = link.get("href")

        if not href:
            continue

        text = link.get_text(
            " ",
            strip=True
        )

        target = (
            href
            + " "
            + text
        ).lower()

        keywords_for_url = [
            "race",
            "odds",
            "raceinfo",
            "racelist",
            "raceodds",
            "kaisai",
            "jyo",
            "ajax",
            "jsj",
        ]

        if any(
            keyword in target
            for keyword in keywords_for_url
        ):

            full_url = urljoin(
                BASE_URL,
                href
            )

            candidates.append(
                (
                    text,
                    href,
                    full_url
                )
            )

    print(
        "候補数 :",
        len(candidates)
    )

    for i, (text, href, full_url) in enumerate(
        candidates,
        1
    ):

        print()
        print(f"[{i}]")
        print("TEXT :", text)
        print("HREF :", href)
        print("URL  :", full_url)

    # ========================================================
    # 2020関連調査
    # ========================================================

    print()
    print("=" * 70)
    print("2020関連文字列調査")
    print("=" * 70)

    for keyword in [
        "2020",
        "20200103",
        "令和2",
        "R02",
        "H31",
        "前橋",
    ]:

        print(
            f"{keyword:<12} : "
            f"{response.text.count(keyword)}"
        )

    # ========================================================
    # HTML内のURL文字列を保存
    # ========================================================

    url_text_file = SAVE_DIR / "jyo_22_links.txt"

    with url_text_file.open(
        "w",
        encoding="utf-8"
    ) as f:

        for i, link in enumerate(
            links,
            1
        ):

            href = link.get("href")

            if not href:
                continue

            text = link.get_text(
                " ",
                strip=True
            )

            full_url = urljoin(
                BASE_URL,
                href
            )

            f.write(
                f"[{i}]\n"
                f"TEXT : {text}\n"
                f"HREF : {href}\n"
                f"URL  : {full_url}\n\n"
            )

    print()
    print("リンク一覧保存:")
    print(url_text_file)

    # ========================================================
    # 終了
    # ========================================================

    print()
    print("=" * 70)
    print("調査終了")
    print("=" * 70)


if __name__ == "__main__":
    main()