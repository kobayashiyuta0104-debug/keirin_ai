import json
import re
import urllib.request
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# =====================================================
# 013_collect_oddspark_links.py
# OddsPark内リンク収集（調査用）
# =====================================================

BASE = Path(r"C:\競輪AI")

OUTPUT = BASE / "data_official" / "historical" / "oddspark_links.json"

TARGET_URL = "https://www.oddspark.com/keirin/"

HEADERS = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
}


# -----------------------------------------------------
# HTML取得
# -----------------------------------------------------
def download_html(url):

    req = urllib.request.Request(
        url,
        headers=HEADERS
    )

    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")


# -----------------------------------------------------
# href/src/action抽出
# -----------------------------------------------------
def extract_attribute_links(soup):

    links = set()

    attrs = [
        "href",
        "src",
        "action"
    ]

    for attr in attrs:

        for tag in soup.find_all(attrs={attr: True}):

            value = tag.get(attr)

            if value:

                links.add(urljoin(TARGET_URL, value))

    return links


# -----------------------------------------------------
# JavaScript文字列からURL抽出
# -----------------------------------------------------
def extract_script_links(html):

    links = set()

    pattern = re.compile(
        r'["\']([^"\']+\.(?:do|jsp|html|json)(?:\?[^"\']*)?)["\']'
    )

    for url in pattern.findall(html):

        links.add(urljoin(TARGET_URL, url))

    return links


# -----------------------------------------------------
# data-*属性抽出
# -----------------------------------------------------
def extract_data_links(soup):

    links = set()

    for tag in soup.find_all():

        for key, value in tag.attrs.items():

            if key.startswith("data"):

                if isinstance(value, str):

                    if "/" in value or ".do" in value:

                        links.add(urljoin(TARGET_URL, value))

    return links


# -----------------------------------------------------
# 保存
# -----------------------------------------------------
def save_json(data):

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


# -----------------------------------------------------
# メイン
# -----------------------------------------------------
def main():

    print("=" * 60)
    print("013 OddsPark Link Collector")
    print("=" * 60)

    print("\nDownloading...")
    html = download_html(TARGET_URL)

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    links = set()

    links |= extract_attribute_links(soup)
    links |= extract_script_links(html)
    links |= extract_data_links(soup)

    links = sorted(links)

    result = {
        "program": "013_collect_oddspark_links.py",
        "target_url": TARGET_URL,
        "link_count": len(links),
        "links": links
    }

    save_json(result)

    print("\n==============================")
    print("TOTAL LINKS :", len(links))
    print("==============================\n")

    keywords = [
        "Race",
        "List",
        "Result",
        "Odd",
        "Player",
        "keirin"
    ]

    for key in keywords:

        count = sum(
            1
            for x in links
            if key.lower() in x.lower()
        )

        print(f"{key:10} : {count}")

    print("\nSaved")
    print(OUTPUT)

    print("\n===== LINK LIST =====")

    for link in links:
        print(link)


if __name__ == "__main__":
    main()