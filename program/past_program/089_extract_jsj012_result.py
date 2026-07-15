import json


INPUT_FILE = "087_jsj012_response.json"


def main():
    print("=== JSJ012 確定結果抽出 ===")
    print()

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # -------------------------
    # 着順
    # -------------------------
    finish_items = data.get("tyakujyunItemSubData", [])

    finish_order = []

    for item in finish_items:
        tyaku = str(item.get("tyaku", "")).strip()
        syaban = str(item.get("syaban", "")).strip()
        sensyu_name = str(item.get("sensyuName", "")).strip()

        if tyaku in ["1", "2", "3"]:
            finish_order.append(
                {
                    "着順": int(tyaku),
                    "車番": syaban,
                    "選手名": sensyu_name,
                }
            )

    finish_order.sort(key=lambda x: x["着順"])

    # -------------------------
    # 3連単払戻
    # -------------------------
    harai_data = data.get("haraiGakuSubData", {})

    rt3_items = harai_data.get(
        "RT3HaraiGakuDispItemSubData",
        []
    )

    sanrentan = []

    for item in rt3_items:
        kumi_ban = str(item.get("kumiBan", "")).strip()
        harai_gaku = str(item.get("haraiGaku", "")).strip()
        ninki = str(item.get("ninki", "")).strip()

        if kumi_ban:
            sanrentan.append(
                {
                    "組番": kumi_ban,
                    "払戻金": harai_gaku,
                    "人気": ninki,
                }
            )

    # -------------------------
    # 表示
    # -------------------------
    print("【着順】")

    for item in finish_order:
        print(
            f'{item["着順"]}着 '
            f'{item["車番"]}番 '
            f'{item["選手名"]}'
        )

    print()
    print("【3連単】")

    for item in sanrentan:
        print(
            f'{item["組番"]} '
            f'{item["払戻金"]}円 '
            f'{item["人気"]}'
        )

    print()
    print("=== 抽出完了 ===")


if __name__ == "__main__":
    main()