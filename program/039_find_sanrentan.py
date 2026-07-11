import json

FILE = "036_result.json"

with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


def search(obj, path="root"):

    if isinstance(obj, dict):

        if "kumiBan" in obj and "haraiGaku" in obj:

            kumi = str(obj.get("kumiBan", ""))
            harai = obj.get("haraiGaku")
            ninki = obj.get("ninki")

            if kumi.count("-") == 2:

                print()
                print("=== 3連単候補発見 ===")
                print("場所:", path)
                print("組み合わせ:", kumi)
                print("払戻金:", harai)
                print("人気:", ninki)

        for key, value in obj.items():
            search(value, f"{path}.{key}")

    elif isinstance(obj, list):

        for i, item in enumerate(obj):
            search(item, f"{path}[{i}]")


print("=== 3連単データ検索開始 ===")

search(data)

print()
print("=== 検索終了 ===")