import json
from pprint import pprint


def main():

    print(
        "=== 131 128JSON ROOT構造確認テスト ==="
    )

    input_file = (
        "128_join_key_detail.json"
    )

    print()
    print("=" * 70)
    print("🔥 128詳細JSON読込")
    print("=" * 70)

    try:

        with open(
            input_file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

    except Exception as e:

        print()
        print(
            "❌ JSON読込失敗:",
            e
        )

        return

    print()
    print(
        "ROOT TYPE:",
        type(data).__name__
    )

    # --------------------------------------------------
    # ROOT が dict
    # --------------------------------------------------

    if isinstance(data, dict):

        print(
            "ROOT KEY数:",
            len(data)
        )

        print()
        print("🔥 ROOT KEYS")

        for key in data.keys():

            print(
                "-",
                repr(key)
            )

        print()
        print("=" * 70)
        print("🔥 ROOT直下 詳細")
        print("=" * 70)

        for key, value in data.items():

            print()
            print("-" * 70)

            print(
                "🔥 ROOT KEY:",
                repr(key)
            )

            print(
                "TYPE:",
                type(value).__name__
            )

            if isinstance(value, list):

                print(
                    "件数:",
                    len(value)
                )

                if value:

                    print()
                    print(
                        "🔥 先頭1件"
                    )

                    pprint(
                        value[0],
                        sort_dicts=False
                    )

            elif isinstance(value, dict):

                print(
                    "KEY数:",
                    len(value)
                )

                print()
                print(
                    "🔥 CHILD KEYS"
                )

                child_keys = list(
                    value.keys()
                )

                for child_key in (
                    child_keys[:30]
                ):

                    print(
                        "-",
                        repr(child_key)
                    )

                if child_keys:

                    first_key = (
                        child_keys[0]
                    )

                    print()
                    print(
                        "🔥 最初のCHILD"
                    )

                    print(
                        "CHILD KEY:",
                        repr(first_key)
                    )

                    print(
                        "CHILD TYPE:",
                        type(
                            value[first_key]
                        ).__name__
                    )

                    print()
                    print(
                        "🔥 CHILD VALUE"
                    )

                    pprint(
                        value[first_key],
                        sort_dicts=False
                    )

            else:

                print(
                    "VALUE:",
                    repr(value)
                )

    # --------------------------------------------------
    # ROOT が list
    # --------------------------------------------------

    elif isinstance(data, list):

        print(
            "ROOT 件数:",
            len(data)
        )

        print()
        print("=" * 70)
        print("🔥 ROOT LIST 先頭10件")
        print("=" * 70)

        for index, item in enumerate(
            data[:10],
            start=1
        ):

            print()
            print("-" * 70)

            print(
                f"🔥 ITEM #{index}"
            )

            print(
                "TYPE:",
                type(item).__name__
            )

            pprint(
                item,
                sort_dicts=False
            )

    else:

        print()
        print(
            "ROOT VALUE:",
            repr(data)
        )

    print()
    print("=" * 70)
    print("🔥 131テスト終了")
    print("=" * 70)


if __name__ == "__main__":
    main()