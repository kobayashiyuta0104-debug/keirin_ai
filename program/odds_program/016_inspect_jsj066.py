import json
import urllib.request
import urllib.parse


# =========================
# 設定
# =========================

TARGET_DATE = "20260916"
JO_CODE = "22"       # 伊東
RACE_NO = "1"


# =========================
# JSJ066取得
# =========================

def get_jsj066():

    url = "https://keirin.jp/pc/json"

    params = {
        "func": "JSJ066",
        "date": TARGET_DATE,
        "jyoCd": JO_CODE,
        "raceNo": RACE_NO,
    }

    query = urllib.parse.urlencode(params)

    full_url = url + "?" + query

    print("=" * 70)
    print("JSJ066 調査")
    print("=" * 70)
    print("URL:")
    print(full_url)
    print()

    try:
        req = urllib.request.Request(
            full_url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read()

        print("HTTP:", response.status)
        print("SIZE:", len(raw), "bytes")
        print()

        text = raw.decode("utf-8")

        data = json.loads(text)

        return data

    except Exception as e:
        print("取得エラー:")
        print(type(e).__name__, e)
        return None


# =========================
# 再帰表示
# =========================

def inspect_value(value, path="root", depth=0, max_depth=4):

    indent = "  " * depth

    if depth > max_depth:
        print(indent + "... depth limit ...")
        return

    if isinstance(value, dict):

        print(
            f"{indent}{path}: dict "
            f"({len(value)} keys)"
        )

        for key, val in value.items():

            print(
                f"{indent}  KEY: {key} "
                f"TYPE: {type(val).__name__}"
            )

            if isinstance(val, (dict, list)):
                inspect_value(
                    val,
                    f"{path}.{key}",
                    depth + 1,
                    max_depth
                )
            else:
                print(
                    f"{indent}    VALUE: {repr(val)}"
                )

    elif isinstance(value, list):

        print(
            f"{indent}{path}: list "
            f"({len(value)} items)"
        )

        for i, item in enumerate(value[:5]):

            print(
                f"{indent}  [{i}] "
                f"TYPE: {type(item).__name__}"
            )

            if isinstance(item, (dict, list)):
                inspect_value(
                    item,
                    f"{path}[{i}]",
                    depth + 1,
                    max_depth
                )
            else:
                print(
                    f"{indent}    VALUE: {repr(item)}"
                )

        if len(value) > 5:
            print(
                f"{indent}  ... "
                f"{len(value) - 5} more items ..."
            )

    else:

        print(
            f"{indent}{path}: "
            f"{type(value).__name__} = {repr(value)}"
        )


# =========================
# メイン
# =========================

def main():

    data = get_jsj066()

    if data is None:
        return

    print("=" * 70)
    print("TOP LEVEL")
    print("=" * 70)

    if isinstance(data, dict):

        print("keys:")
        for key in data.keys():
            print(" ", key)

    else:

        print("ROOT TYPE:", type(data).__name__)

    print()

    # -------------------------
    # sanrentanShijiList検索
    # -------------------------

    found = []

    def search(obj, path="root"):

        if isinstance(obj, dict):

            for key, value in obj.items():

                current_path = f"{path}.{key}"

                if key == "sanrentanShijiList":
                    found.append(
                        (current_path, value)
                    )

                search(value, current_path)

        elif isinstance(obj, list):

            for i, item in enumerate(obj):

                search(
                    item,
                    f"{path}[{i}]"
                )

    search(data)

    print("=" * 70)
    print("sanrentanShijiList SEARCH")
    print("=" * 70)

    print("FOUND:", len(found))
    print()

    if not found:

        print("sanrentanShijiList は見つかりませんでした。")
        return

    # -------------------------
    # 発見したものを表示
    # -------------------------

    for index, (path, value) in enumerate(found, 1):

        print("=" * 70)
        print(f"FOUND #{index}")
        print("=" * 70)

        print("PATH:")
        print(path)
        print()

        print("TYPE:")
        print(type(value).__name__)
        print()

        if isinstance(value, list):
            print("COUNT:")
            print(len(value))
            print()

        print("CONTENT:")
        print()

        inspect_value(
            value,
            path="sanrentanShijiList",
            depth=0,
            max_depth=5
        )

        print()

        # JSONとしても保存
        output_file = (
            f"C:\\競輪AI\\data_official\\"
            f"historical\\oddspark_test\\"
            f"debug_jsj066_{TARGET_DATE}_"
            f"{JO_CODE}_{RACE_NO}_"
            f"{index}.json"
        )

        try:

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    value,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

            print("保存:")
            print(output_file)

        except Exception as e:

            print("保存失敗:", e)

        print()


if __name__ == "__main__":
    main()