import urllib.request
from pathlib import Path
from datetime import datetime


# ============================================================
# netkeirin オッズ取得テスト
# 対象：2026/09/08 いわき平 12R
# ============================================================

RACE_ID = "202609081312"

URL = (
    "https://keirin.netkeiba.com/race/odds/"
    f"?race_id={RACE_ID}"
)


# 保存先
SAVE_DIR = Path(r"C:\競輪AI\data_official\odds_test")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

HTML_FILE = SAVE_DIR / f"{RACE_ID}_odds.html"


# User-Agent
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/142.0.0.0 Safari/537.36"
    )
}


print("=" * 60)
print("netkeirin オッズ取得テスト")
print("=" * 60)

print("RACE_ID =", RACE_ID)
print("URL     =", URL)
print()


try:
    request = urllib.request.Request(
        URL,
        headers=headers
    )

    with urllib.request.urlopen(request, timeout=30) as response:

        status = response.status
        data = response.read()

    print("HTTP STATUS =", status)
    print("取得バイト数 =", len(data))

    # HTML保存
    HTML_FILE.write_bytes(data)

    print()
    print("HTML保存成功")
    print("保存先 =", HTML_FILE)

    print()
    print("=" * 60)
    print("取得テスト成功")
    print("=" * 60)


except Exception as e:

    print()
    print("=" * 60)
    print("取得エラー")
    print("=" * 60)

    print(type(e).__name__)
    print(e)