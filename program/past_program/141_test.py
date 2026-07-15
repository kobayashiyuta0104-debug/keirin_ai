import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "139_official_race_match.json"


def main():

    print("=" * 70)
    print("🔥 141 139照合JSON構造確認")
    print("=" * 70)

    if not INPUT_FILE.exists():
        print("❌ ファイルなし")
        print(INPUT_FILE)
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print()
    print(f"ROOT TYPE: {type(data).__name__}")

    if isinstance(data, dict):

        print(f"ROOT KEY数: {len(data)}")

        print()
        print("🔥 ROOT KEYS")

        for key in data.keys():
            print(f"- {repr(key)}")

        print()
        print("=" * 70)
        print("🔥 ROOT直下 詳細")
        print("=" * 70)

        for key, value in data.items():

            print()
            print("-" * 70)

            print(f"KEY: {repr(key)}")
            print(f"TYPE: {type(value).__name__}")

            if isinstance(value, list):

                print(f"件数: {len(value)}")

                if value:

                    print()
                    print("🔥 先頭1件")
                    print(
                        json.dumps(
                            value[0],
                            ensure_ascii=False,
                            indent=2,
                        )
                    )

            elif isinstance(value, dict):

                print(f"KEY数: {len(value)}")

                print()
                print("🔥 KEYS")

                for sub_key in value.keys():
                    print(f"- {repr(sub_key)}")

                print()
                print("🔥 内容")

                print(
                    json.dumps(
                        value,
                        ensure_ascii=False,
                        indent=2,
                    )[:5000]
                )

            else:

                print(f"VALUE: {repr(value)}")

    elif isinstance(data, list):

        print(f"ROOT件数: {len(data)}")

        if data:

            print()
            print("🔥 先頭1件")

            print(
                json.dumps(
                    data[0],
                    ensure_ascii=False,
                    indent=2,
                )
            )

    else:

        print(f"ROOT VALUE: {repr(data)}")

    print()
    print("=" * 70)
    print("🔥 141テスト終了")
    print("=" * 70)


if __name__ == "__main__":
    main()