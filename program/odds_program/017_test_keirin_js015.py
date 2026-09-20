import json
import urllib.request
import urllib.parse


# =========================================================
# テスト設定
# =========================================================

ENC_P = "HpFdexXEOA-CBPIVgXoV5MFckHu0CHISsx7Iq4Vqnas"

URL = "https://www.keirin.jp/pc/json"


# =========================================================
# JST015取得
# =========================================================

def get_jst015():

    params = {
        "mode": "0",
        "encp": ENC_P,
        "type": "JST015",
    }

    query = urllib.parse.urlencode(params)

    full_url = URL + "?" + query

    print("=" * 70)
    print("KEIRIN.JP JST015 テスト")
    print("=" * 70)
    print()
    print("URL:")
    print(full_url)
    print()

    try:

        request = urllib.request.Request(
            full_url,
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

            return data

    except Exception as e:

        print("取得エラー")
        print(type(e).__name__)
        print(e)

        return None


# =========================================================
# 調査
# =========================================================

def main():

    data = get_jst015()

    if data is None:
        return

    print("=" * 70)
    print("TOP LEVEL")
    print("=" * 70)

    if isinstance(data, dict):

        for key in data.keys():
            print(key)

    else:

        print("ROOT TYPE:", type(data).__name__)

        return

    print()

    # -----------------------------------------------------
    # resultCd
    # -----------------------------------------------------

    print("=" * 70)
    print("resultCd")
    print("=" * 70)

    print(data.get("resultCd"))

    print()

    # -----------------------------------------------------
    # data
    # -----------------------------------------------------

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
    print("data keys")
    print("=" * 70)

    for key in root_data.keys():

        print(key)

    print()

    # -----------------------------------------------------
    # ozz3RentanData
    # -----------------------------------------------------

    odds = root_data.get("ozz3RentanData")

    print("=" * 70)
    print("ozz3RentanData")
    print("=" * 70)

    if not isinstance(odds, dict):

        print("ozz3RentanData がありません")

        print()
        print(
            json.dumps(
                root_data,
                ensure_ascii=False,
                indent=2
            )
        )

        return

    print("件数:", len(odds))
    print()

    # 最初の10件
    print("先頭10件")
    print("-" * 70)

    for i, (key, value) in enumerate(odds.items()):

        if i >= 10:
            break

        print(key, "=", value)

    print()

    # -----------------------------------------------------
    # OZZ形式チェック
    # -----------------------------------------------------

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
    print("OZZキー検証")
    print("=" * 70)

    print("OZZ形式:", len(valid_keys))

    print()

    # -----------------------------------------------------
    # 保存
    # -----------------------------------------------------

    output_file = (
        r"C:\競輪AI\data_official\historical"
        r"\oddspark_test\debug_jst015_test.json"
    )

    try:

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

        print("保存しました:")
        print(output_file)

    except Exception as e:

        print("保存エラー:")
        print(e)

    print()

    # -----------------------------------------------------
    # 判定
    # -----------------------------------------------------

    print("=" * 70)
    print("判定")
    print("=" * 70)

    if len(valid_keys) > 0:

        print("★ KEIRIN.JPから3連単オッズ取得成功")

    else:

        print("★ 3連単オッズは取得できませんでした")


if __name__ == "__main__":
    main()