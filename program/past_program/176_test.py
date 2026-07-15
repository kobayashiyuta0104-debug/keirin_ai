from pathlib import Path


TARGET_FILE = Path("program/155_test.py")


def main():

    print("=" * 70)
    print("🔥 176 155_test.py JSJ006発火処理解析")
    print("=" * 70)

    if not TARGET_FILE.exists():

        print("❌ FILEなし")
        print(TARGET_FILE)
        return

    text = TARGET_FILE.read_text(
        encoding="utf-8"
    )

    lines = text.splitlines()

    print()
    print("🔥 FILE読込成功")
    print("総行数:", len(lines))

    hit_indexes = []

    for i, line in enumerate(lines):

        if "JSJ006" in line.upper():

            hit_indexes.append(i)

    print()
    print("=" * 70)
    print("🔥 JSJ006文字列検索")
    print("=" * 70)

    print(
        "JSJ006出現数:",
        len(hit_indexes),
    )

    output_lines = []

    for hit_no, index in enumerate(
        hit_indexes,
        start=1,
    ):

        start = max(
            0,
            index - 40,
        )

        end = min(
            len(lines),
            index + 41,
        )

        print()
        print("=" * 70)
        print(
            f"🔥 JSJ006 HIT #{hit_no}"
        )
        print(
            f"中心行: {index + 1}"
        )
        print("=" * 70)

        block = []

        for line_no in range(
            start,
            end,
        ):

            marker = (
                "🔥"
                if line_no == index
                else "  "
            )

            formatted = (
                f"{marker} "
                f"{line_no + 1:04d}: "
                f"{lines[line_no]}"
            )

            print(formatted)

            block.append(
                formatted
            )

        output_lines.extend(
            block
        )

        output_lines.append("")

    print()
    print("=" * 70)
    print("🔥 通信・発火関連キーワード探索")
    print("=" * 70)

    keywords = [
        "page.on",
        "response",
        "request",
        "goto",
        "click",
        "evaluate",
        "dispatch",
        "piInitialize",
        "JSJ006",
        "/pc/json",
        "encp",
        "type=",
    ]

    keyword_hits = []

    for i, line in enumerate(lines):

        lower_line = line.lower()

        matched = []

        for keyword in keywords:

            if keyword.lower() in lower_line:

                matched.append(
                    keyword
                )

        if matched:

            item = (
                f"{i + 1:04d}: "
                f"{line}"
            )

            keyword_hits.append(
                item
            )

            print()
            print(
                "KEY:",
                matched
            )

            print(item)

    save_file = Path(
        "176_155_jsj006_code_analysis.txt"
    )

    save_text = []

    save_text.append(
        "JSJ006 BLOCKS"
    )

    save_text.append(
        "=" * 70
    )

    save_text.extend(
        output_lines
    )

    save_text.append("")
    save_text.append(
        "KEYWORD HITS"
    )

    save_text.append(
        "=" * 70
    )

    save_text.extend(
        keyword_hits
    )

    save_file.write_text(
        "\n".join(save_text),
        encoding="utf-8",
    )

    print()
    print("=" * 70)
    print("🔥 176テスト終了")
    print("=" * 70)

    print(
        "JSJ006出現数:",
        len(hit_indexes),
    )

    print(
        "通信関連HIT数:",
        len(keyword_hits),
    )

    print(
        "保存先:",
        save_file,
    )

    print("=" * 70)


if __name__ == "__main__":
    main()