import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


# ============================================================
# 設定
# ============================================================

JYO_CODE = "22"

BASE_URL = "https://keirin.jp"

VENUE_URL = (
    f"{BASE_URL}/pc/jyosellinfo"
    f"?jocd={JYO_CODE}"
)

SAVE_DIR = Path(
    r"C:\競輪AI\data_official\historical\keirinjp_odds_test"
)

SAVE_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    ),
    "Referer": VENUE_URL,
}

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# 共通
# ============================================================

def separator(title):
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


# ============================================================
# 1. 競輪場ページ取得
# ============================================================

separator("1. KEIRIN.JP 競輪場ページ取得")

print("URL:")
print(VENUE_URL)

try:
    response = session.get(
        VENUE_URL,
        timeout=30
    )
except Exception as e:
    print("HTTP ERROR")
    print(e)
    raise SystemExit

print()
print("HTTP STATUS :", response.status_code)
print("HTML SIZE   :", len(response.text))

html = response.text

html_path = SAVE_DIR / f"jyo_{JYO_CODE}.html"

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print("HTML SAVE   :", html_path)


# ============================================================
# 2. hidden inputを「id」で調査
# ============================================================

separator("2. hidden input 調査（id基準）")

soup = BeautifulSoup(html, "html.parser")


target_ids = [
    "sh_hidden1",
    "sh_hidden2",
    "shCcp",
    "shCurrentDisp",
    "shParentDisp",
]


hidden_values = {}


for target_id in target_ids:

    tag = soup.find(id=target_id)

    if tag is None:
        print(f"{target_id} = [NOT FOUND]")
        continue

    value = tag.get("value")

    hidden_values[target_id] = value

    print(f"{target_id} = {value}")


# ============================================================
# 3. 該当HTMLそのものを表示
# ============================================================

separator("3. 該当input HTML")

for target_id in target_ids:

    tag = soup.find(id=target_id)

    if tag is None:
        continue

    print()
    print(f"[{target_id}]")
    print(str(tag))


# ============================================================
# 4. すべてのinputを調査
# ============================================================

separator("4. input一覧（id / name / value）")

for tag in soup.find_all("input"):

    input_id = tag.get("id")
    name = tag.get("name")
    value = tag.get("value")
    input_type = tag.get("type")

    if (
        input_id
        or name
        or value
    ):
        print(
            f"type={input_type!r} "
            f"id={input_id!r} "
            f"name={name!r} "
            f"value={value!r}"
        )


# ============================================================
# 5. JavaScript取得
# ============================================================

separator("5. JavaScript取得")

script_urls = []

for script in soup.find_all("script"):

    src = script.get("src")

    if not src:
        continue

    if src.startswith("//"):
        src = "https:" + src

    elif src.startswith("/"):
        src = BASE_URL + src

    elif not src.startswith("http"):
        src = BASE_URL + "/" + src

    script_urls.append(src)


target_scripts = {}

for src in script_urls:

    filename = src.split("/")[-1].split("?")[0]

    if filename in (
        "PC0101_c.js",
        "commonJSON.js",
    ):
        target_scripts[filename] = src


for filename, url in target_scripts.items():

    print()
    print("FILE   :", filename)
    print("URL    :", url)

    try:

        r = session.get(
            url,
            timeout=30
        )

        print("STATUS :", r.status_code)
        print("SIZE   :", len(r.text))

        save_path = SAVE_DIR / filename

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(r.text)

        print("SAVE   :", save_path)

    except Exception as e:

        print("ERROR :", e)


# ============================================================
# 6. PC0101_c.js のJSJ048処理確認
# ============================================================

separator("6. PC0101_c.js JSJ048処理")

pc0101_path = SAVE_DIR / "PC0101_c.js"

if pc0101_path.exists():

    js = pc0101_path.read_text(
        encoding="utf-8"
    )

    lines = js.splitlines()

    for i, line in enumerate(lines):

        if (
            "JSJ048" in line
            or "jsj048JSONRequest" in line
            or "getRequestGet" in line
        ):

            start = max(0, i - 8)
            end = min(len(lines), i + 20)

            print()

            for j in range(start, end):
                print(
                    f"{j + 1:5}: {lines[j]}"
                )

            print("-" * 60)


else:

    print("PC0101_c.js がありません。")


# ============================================================
# 7. commonJSON.js の通信処理確認
# ============================================================

separator("7. commonJSON.js 通信処理")

common_path = SAVE_DIR / "commonJSON.js"

if common_path.exists():

    js = common_path.read_text(
        encoding="utf-8"
    )

    lines = js.splitlines()

    keywords = [
        "getRequestGet",
        "getRequestPost",
        "ajaxCfg",
        "ajax",
        "/json",
        "/ana",
    ]

    found = set()

    for i, line in enumerate(lines):

        for keyword in keywords:

            if keyword in line:

                # 同じ場所を何度も出さない
                key = (i, keyword)

                if key in found:
                    continue

                found.add(key)

                start = max(0, i - 5)
                end = min(len(lines), i + 15)

                print()
                print(
                    f"### keyword: {keyword}"
                )

                for j in range(start, end):
                    print(
                        f"{j + 1:5}: {lines[j]}"
                    )

                print("-" * 60)

else:

    print("commonJSON.js がありません。")


# ============================================================
# 8. HTML内のJSJ048関連文字列
# ============================================================

separator("8. HTML内 JSJ048関連情報")

for keyword in [
    "JSJ048",
    "sh_hidden1",
    "sh_hidden2",
    "shCcp",
    "shCurrentDisp",
    "kaisaibikbn",
]:

    print()
    print(f"--- {keyword} ---")

    matches = []

    for match in re.finditer(
        re.escape(keyword),
        html,
        re.IGNORECASE
    ):

        start = max(
            0,
            match.start() - 200
        )

        end = min(
            len(html),
            match.end() + 300
        )

        snippet = html[start:end]

        matches.append(snippet)

        if len(matches) >= 5:
            break

    if not matches:

        print("該当なし")

    else:

        for snippet in matches:
            print(snippet)
            print("-" * 40)


# ============================================================
# 9. 現時点で取得できた値
# ============================================================

separator("9. JSJ048パラメータ候補")

for key in target_ids:

    print(
        f"{key:15} = "
        f"{hidden_values.get(key, '[NOT FOUND]')}"
    )


print()
print("※ここではまだJSJ048本体を呼びません。")
print("※まず正しい通信パラメータを確定します。")


# ============================================================
# 終了
# ============================================================

separator("調査終了")

print("今回の調査で確認するもの：")
print()
print("  ① sh_hidden2")
print("  ② sh_hidden1")
print("  ③ shCcp")
print("  ④ shCurrentDisp")
print("  ⑤ PC0101_c.js")
print("  ⑥ commonJSON.js")
print("  ⑦ Com.getRequestGet()")
print()
print("この結果をそのまま確認してから")
print("次のJSJ048通信コードを確定します。")

input("\nEnterで終了...")