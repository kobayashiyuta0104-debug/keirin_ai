# -*- coding: utf-8 -*-

import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# ============================================================
# 設定
# ============================================================

BASE_URL = "https://keirin.jp"

TARGET_URL = (
    "https://keirin.jp/pc/jyosellinfo?jocd=22"
)

SAVE_DIR = Path(
    r"C:\競輪AI\data_official\historical\keirinjp_odds_test"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja-JP,ja;q=0.9",
}


# ============================================================
# 調査キーワード
# ============================================================

KEYWORDS = [
    "JSJ",
    "ajax",
    "$.ajax",
    "$.post",
    "$.get",
    "getJSON",
    "postJSON",
    "json",
    "url",
    "URL",
    "race",
    "raceList",
    "raceInfo",
    "odds",
    "Odds",
    "kaisai",
    "kaisaiBi",
    "jocd",
    "raceNo",
    "race_no",
    "raceKey",
    "racekey",
    "data",
    "submit",
    "location.href",
]


# ============================================================
# キーワード周辺を表示
# ============================================================

def print_keyword_matches(
    name,
    text,
    max_matches=20
):

    print()
    print("-" * 70)
    print(name)
    print("-" * 70)

    lines = text.splitlines()

    found = 0

    for line_no, line in enumerate(lines, 1):

        line_lower = line.lower()

        matched = False

        for keyword in KEYWORDS:

            if keyword.lower() in line_lower:

                matched = True
                break

        if not matched:
            continue

        found += 1

        print(
            f"[{line_no}] {line.strip()}"
        )

        if found >= max_matches:
            print(
                f"... 最大 {max_matches} 件まで表示"
            )
            break

    print()
    print("MATCH COUNT :", found)


# ============================================================
# メイン
# ============================================================

def main():

    print("=" * 70)
    print("KEIRIN.JP JavaScript 調査")
    print("=" * 70)

    print()
    print("TARGET URL:")
    print(TARGET_URL)

    SAVE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    js_dir = SAVE_DIR / "javascript"

    js_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    session = requests.Session()

    # ========================================================
    # jyoページ取得
    # ========================================================

    try:

        response = session.get(
            TARGET_URL,
            headers=HEADERS,
            timeout=30
        )

    except Exception as e:

        print()
        print("[ERROR] ページ取得失敗")
        print(e)
        return

    print()
    print("HTTP STATUS :", response.status_code)
    print("HTML SIZE   :", len(response.text))

    if response.status_code != 200:

        print()
        print("[ERROR] HTTP 200ではありません")
        return

    # ========================================================
    # HTML解析
    # ========================================================

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    scripts = soup.find_all("script")

    print()
    print("SCRIPT COUNT :", len(scripts))

    # ========================================================
    # INLINE SCRIPT調査
    # ========================================================

    inline_count = 0

    for i, script in enumerate(
        scripts,
        1
    ):

        src = script.get("src")

        if src:
            continue

        text = script.get_text()

        if not text.strip():
            continue

        inline_count += 1

        filename = (
            js_dir
            / f"inline_{inline_count:02d}.js"
        )

        filename.write_text(
            text,
            encoding="utf-8"
        )

        print()
        print(
            f"[INLINE {inline_count}]"
        )
        print(
            "SIZE :",
            len(text)
        )
        print(
            "FILE :",
            filename
        )

        print_keyword_matches(
            f"INLINE {inline_count}",
            text,
            max_matches=30
        )

    # ========================================================
    # 外部JavaScript調査
    # ========================================================

    external_count = 0

    for i, script in enumerate(
        scripts,
        1
    ):

        src = script.get("src")

        if not src:
            continue

        full_url = urljoin(
            BASE_URL,
            src
        )

        external_count += 1

        print()
        print("=" * 70)
        print(
            f"EXTERNAL JS {external_count}"
        )
        print("=" * 70)

        print("URL :", full_url)

        try:

            js_response = session.get(
                full_url,
                headers=HEADERS,
                timeout=30
            )

        except Exception as e:

            print(
                "[ERROR] JS取得失敗:",
                e
            )

            continue

        print(
            "HTTP STATUS :",
            js_response.status_code
        )

        print(
            "SIZE        :",
            len(js_response.text)
        )

        if js_response.status_code != 200:

            continue

        # ----------------------------------------------------
        # ファイル名
        # ----------------------------------------------------

        src_name = Path(
            src.split("?")[0]
        ).name

        if not src_name:

            src_name = (
                f"script_{external_count:02d}.js"
            )

        filename = (
            js_dir
            / src_name
        )

        filename.write_text(
            js_response.text,
            encoding="utf-8"
        )

        print(
            "FILE        :",
            filename
        )

        # ----------------------------------------------------
        # キーワード検索
        # ----------------------------------------------------

        print_keyword_matches(
            src_name,
            js_response.text,
            max_matches=30
        )

    # ========================================================
    # HTML内のscript関連情報を保存
    # ========================================================

    script_list_file = (
        SAVE_DIR
        / "javascript_script_list.txt"
    )

    with script_list_file.open(
        "w",
        encoding="utf-8"
    ) as f:

        for i, script in enumerate(
            scripts,
            1
        ):

            src = script.get("src")

            if src:

                f.write(
                    f"[{i}] EXTERNAL\n"
                )

                f.write(
                    f"{urljoin(BASE_URL, src)}\n\n"
                )

            else:

                text = script.get_text()

                f.write(
                    f"[{i}] INLINE\n"
                )

                f.write(
                    f"SIZE={len(text)}\n\n"
                )

    print()
    print("=" * 70)
    print("保存先")
    print("=" * 70)

    print(
        "JavaScript:",
        js_dir
    )

    print(
        "Script一覧:",
        script_list_file
    )

    print()
    print("=" * 70)
    print("調査終了")
    print("=" * 70)


if __name__ == "__main__":
    main()