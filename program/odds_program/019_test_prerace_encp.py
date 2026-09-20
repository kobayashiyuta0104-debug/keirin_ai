import json
import urllib.request
import urllib.parse


# =========================================================
# 設定
# =========================================================

PRE_RACE_FILE = (
    r"C:\競輪AI\data_official\historical"
    r"\pre_race\20200101_pre_race.json"
)

KAIKEI = "6"
MODE = "0"
TYPE = "JST011"


# =========================================================
# JST011取得
# =========================================================

def test_jst011(encp, label):

    params = {
        "kake": KAIKEI,
        "mode": MODE,
        "encp": encp,
        "type": TYPE,
    }

    query = urllib.parse.urlencode(params)

    url = (
        "https://www.keirin.jp/pc/json?"
        + query
    )

    print("=" * 70)
    print(label)
    print("=" * 70)

    print("encp:")
    print(encp)
    print()

    print("URL:")
    print(url)
    print()

    try:

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/142.0.0.0 Safari/537.36"
                ),
                "Referer": "https://www.keirin.jp/pc/racelive",
                "Accept": (
                    "application/json, "
                    "text/javascript, */*; q=0.01"
                ),
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

            data = json.loads(
                raw.decode("utf-8")
            )

    except Exception as e:

        print("取得エラー")
        print(type(e).__name__, e)
        print()

        return False

    result_cd = data.get("resultCd")

    print("resultCd:", result_cd)

    if result_cd != 0:

        print(
            "messageCd:",
            data.get("messageCd")
        )

        print()
        return False

    root_data = data.get("data")

    if not isinstance(root_data, dict):

        print("dataなし")
        print()
        return False

    odds = root_data.get(
        "ozz3RentanData"
    )

    if not isinstance(odds, dict):

        print(
            "ozz3RentanDataなし"
        )
        print()
        return False

    valid_count = 0

    for key in odds:

        if (
            isinstance(key, str)
            and key.startswith("OZZ")
            and len(key) == 6
            and key[3:].isdigit()
        ):
            valid_count += 1

    print(
        "ozz3RentanData 件数:",
        len(odds)
    )

    print(
        "OZZ形式:",
        valid_count
    )

    print()

    if valid_count > 0:

        print(
            "★ 成功！ "
            "この値をJST011のencpとして使用可能"
        )

        print()

        for i, (key, value) in enumerate(
            odds.items()
        ):

            if i >= 5:
                break

            print(
                key,
                "=",
                value
            )

        print()

        return True

    print(
        "★ JST011は返ったが、"
        "3連単オッズなし"
    )

    print()

    return False


# =========================================================
# メイン
# =========================================================

def main():

    print("=" * 70)
    print("PRE_RACE 暗号パラメータ検証")
    print("=" * 70)
    print()

    # -----------------------------------------------------
    # PRE_RACE読み込み
    # -----------------------------------------------------

    with open(
        PRE_RACE_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    print("PRE_RACE:")
    print(PRE_RACE_FILE)
    print()

    venues = data.get("venues", [])

    print(
        "venue_count:",
        len(venues)
    )

    print()

    # -----------------------------------------------------
    # 前橋を探す
    # -----------------------------------------------------

    target_venue = None

    for venue in venues:

        if venue.get("venue") == "前橋":
            target_venue = venue
            break

    if target_venue is None:

        print("前橋が見つかりません")
        return

    print(
        "対象:",
        target_venue.get("venue")
    )

    print(
        "bank_code:",
        target_venue.get("bank_code")
    )

    print()

    jsj001 = target_venue.get(
        "jsj001",
        {}
    )

    c0201data = jsj001.get(
        "C0201data",
        {}
    )

    # -----------------------------------------------------
    # 値を取得
    # -----------------------------------------------------

    enc_prm = target_venue.get(
        "encPrm"
    )

    enc_sel_para_k = c0201data.get(
        "encSelParaK"
    )

    enc_sel_para_r = c0201data.get(
        "encSelParaR"
    )

    enc_para_s = c0201data.get(
        "encParaS"
    )

    race_list = c0201data.get(
        "C0201race",
        []
    )

    # 11R = index 10
    race_11 = None

    if len(race_list) >= 11:
        race_11 = race_list[10]

    enc_para_r = None

    if race_11:
        enc_para_r = race_11.get(
            "encParaR"
        )

    # -----------------------------------------------------
    # 表示
    # -----------------------------------------------------

    print("=" * 70)
    print("PRE_RACE内の候補")
    print("=" * 70)

    print(
        "encPrm:",
        enc_prm
    )

    print(
        "encSelParaK:",
        enc_sel_para_k
    )

    print(
        "encSelParaR:",
        enc_sel_para_r
    )

    print(
        "encParaS:",
        enc_para_s
    )

    print(
        "11R encParaR:",
        enc_para_r
    )

    print()

    # -----------------------------------------------------
    # テスト
    # -----------------------------------------------------

    results = {}

    if enc_prm:
        results["encPrm"] = test_jst011(
            enc_prm,
            "TEST 1 : encPrm"
        )

    if enc_sel_para_r:
        results["encSelParaR"] = test_jst011(
            enc_sel_para_r,
            "TEST 2 : encSelParaR"
        )

    if enc_para_r:
        results["11R encParaR"] = test_jst011(
            enc_para_r,
            "TEST 3 : 11R encParaR"
        )

    # -----------------------------------------------------
    # 結果
    # -----------------------------------------------------

    print("=" * 70)
    print("最終結果")
    print("=" * 70)

    for label, result in results.items():

        print(
            label,
            "→",
            "成功" if result else "失敗"
        )

    print()


if __name__ == "__main__":
    main()