# -*- coding: utf-8 -*-

import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# ============================================================
# 調査対象
# ============================================================

TARGET_YEAR = "2020"
TARGET_MONTH = "01"

TARGET_DATE = "20200103"
TARGET_BANK = "前橋"


# ============================================================
# KEIRIN.JP 開催日程
# ============================================================

BASE_URL = "https://keirin.jp"

SCHEDULE_URL = (
    f"{BASE_URL}/pc/raceschedule"
    f"?scym={int(TARGET_MONTH):02d}"
    f"&scyy={TARGET_YEAR}"
)


# ============================================================
# メイン
# ============================================================

def main():

    print("=" * 70)
    print("KEIRIN.JP 過去レースURL調査")
    print("=" * 70)

    print(f"TARGET_DATE : {TARGET_DATE}")
    print(f"TARGET_BANK : {TARGET_BANK}")
    print()
    print("SCHEDULE URL:")
    print(SCHEDULE_URL)
    print()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/142.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ja-JP,ja;q=0.9"
    }

    session = requests.Session()

    # ========================================================
    # 開催日程ページ取得
    # ========================================================

    try:

        response = session.get(
            SCHEDULE_URL,
            headers=headers,
            timeout=30
        )

    except Exception as e:

        print("[ERROR] 開催日程ページ取得失敗")
        print(e)
        return

    print("HTTP STATUS :", response.status_code)
    print("HTML SIZE   :", len(response.text))

    if response.status_code != 200:

        print()
        print("[ERROR] HTTP 200ではありません")
        return

    # ========================================================
    # 保存
    # ========================================================

    save_dir = Path(
        r"C:\競輪AI\data_official\historical\keirinjp_odds_test"
    )

    save_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    schedule_file = save_dir / "schedule_202001.html"

    schedule_file.write_text(
        response.text,
        encoding="utf-8"
    )

    print()
    print("開催日程HTML保存:")
    print(schedule_file)

    # ========================================================
    # HTML解析
    # ========================================================

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    print()
    print("=" * 70)
    print("前橋関連リンク調査")
    print("=" * 70)

    links = soup.find_all("a")

    found = 0

    for link in links:

        text = link.get_text(
            " ",
            strip=True
        )

        href = link.get("href")

        if not href:
            continue

        full_url = urljoin(
            BASE_URL,
            href
        )

        # 前橋という文字があるリンク
        if TARGET_BANK in text:

            found += 1

            print()
            print(f"[{found}]")
            print("TEXT :", text)
            print("HREF :", href)
            print("URL  :", full_url)

    print()
    print("前橋リンク数 :", found)

    # ========================================================
    # 20200103関連文字列調査
    # ========================================================

    print()
    print("=" * 70)
    print("20200103 関連文字列調査")
    print("=" * 70)

    html = response.text

    keywords = [
        "20200103",
        "2020/01/03",
        "1月3日",
        "前橋"
    ]

    for keyword in keywords:

        count = html.count(keyword)

        print(
            f"{keyword:<15} : {count}"
        )

    # ========================================================
    # hrefの中に前橋・日付関連があるものを全部表示
    # ========================================================

    print()
    print("=" * 70)
    print("候補URL調査")
    print("=" * 70)

    candidate_count = 0

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
        )

        if (
            "20200103" in target
            or
            "2020/01/03" in target
            or
            TARGET_BANK in target
        ):

            candidate_count += 1

            print()
            print(f"[{candidate_count}]")
            print("TEXT :", text)
            print("HREF :", href)
            print(
                "URL  :",
                urljoin(BASE_URL, href)
            )

    print()
    print("候補数 :", candidate_count)

    # ========================================================
    # 終了
    # ========================================================

    print()
    print("=" * 70)
    print("調査終了")
    print("=" * 70)


if __name__ == "__main__":
    main()