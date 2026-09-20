import json
import urllib.request


# =========================================================
# ブラウザで実際に成功したURL
# =========================================================

URL = (
    "https://www.keirin.jp/pc/json"
    "?kake=6"
    "&mode=0"
    "&encp=HpFdexXEOA-CBPIVgXoV5Az55-MtjBfIa8SsUats-u4"
    "&type=JST011"
)


# =========================================================
# 取得
# =========================================================

def main():

    print("=" * 70)
    print("KEIRIN.JP JST011 完全URLテスト")
    print("=" * 70)
    print()

    print("URL:")
    print(URL)
    print()

    try:

        request = urllib.request.Request(
            URL,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/142.0.0.0 Safari/537.36"
                ),
                "Referer": "https://www.keirin.jp/pc/racelive",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "X-Requested-With": "XMLHttpRequest",
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=20
        ) as response:

            raw = response.read()

            print("HTTP:", response.status)
            print("SIZE:", len(raw), "bytes")
            print()

            text = raw.decode("utf-8")

            data = json.loads(text)

    except Exception as e:

        print("取得エラー")
        print(type(e).__name__)
        print(e)

        return

    # =====================================================
    # 基本情報
    # =====================================================

    print("=" * 70)
    print("基本情報")
    print("=" * 70)

    print("resultCd:", data.get("resultCd"))
    print("writeANA:", data.get("writeANA"))
    print()

    # =====================================================
    # data
    # =====================================================

    root_data = data.get("data")

    if not isinstance(root_data, dict):

        print("data がありません")

        print()
        print("RAW:")
        print(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            )
        )

        return

    print("=" * 70)
    print("data")
    print("=" * 70)

    for key in root_data.keys():
        print(key)

    print()

    # =====================================================
    # 3連単オッズ
    # =====================================================

    odds = root_data.get("ozz3RentanData")

    if not isinstance(odds, dict):

        print("=" * 70)
        print("3連単オッズ")
        print("=" * 70)
        print("ozz3RentanData がありません")

        return

    print("=" * 70)
    print("3連単オッズ")
    print("=" * 70)

    print("件数:", len(odds))
    print()

    # 先頭10件

    print("先頭10件")
    print("-" * 70)

    for i, (key, value) in enumerate(odds.items()):

        if i >= 10:
            break

        print(key, "=", value)

    print()

    # =====================================================
    # OZZキー数
    # =====================================================

    valid_keys = []

    for key in odds.keys():

        if (
            isinstance(key, str)
            and key.startswith("OZZ")
            and len(key) == 6
            and key[3:].isdigit()
        ):
            valid_keys.append(key)

    print("=" * 70)
    print("OZZキー")
    print("=" * 70)

    print("OZZ形式:", len(valid_keys))
    print()

    # =====================================================
    # 更新日時
    # =====================================================

    print("=" * 70)
    print("更新日時")
    print("=" * 70)

    print(
        "UP_DATE:",
        odds.get("UP_DATE")
    )

    print()

    # =====================================================
    # 判定
    # =====================================================

    print("=" * 70)
    print("判定")
    print("=" * 70)

    if data.get("resultCd") == 0 and len(valid_keys) > 0:

        print("★ KEIRIN.JP JST011 取得成功")

    else:

        print("★ 取得失敗")

    print()


if __name__ == "__main__":
    main()