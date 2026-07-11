from pathlib import Path
import json
import re


BASE = Path(r"C:\競輪AI")

CAPTURE_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "016_official_syusou_capture"
)

SCRIPT_DIR = CAPTURE_DIR / "scripts"
BODY_DIR = CAPTURE_DIR / "response_bodies"

OUT_JSON = (
    CAPTURE_DIR
    / "020_jsj003_params_trace.json"
)


TARGET_WORDS = [
    "JSJ003",
    "PJ0314Controller",
    "PJ0314MainData",
    "narabiyoso",
    "stCreateList",
]


ASSIGN_PATTERNS = [
    r"prm\.[A-Za-z_$][A-Za-z0-9_$]*\s*=",
    r"params\.[A-Za-z_$][A-Za-z0-9_$]*\s*=",
    r"reqPrm\.[A-Za-z_$][A-Za-z0-9_$]*\s*=",
    r"param\.[A-Za-z_$][A-Za-z0-9_$]*\s*=",
]


def read_text(path):

    try:

        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    except Exception:

        return ""


def save_json(path, data):

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


def find_positions(
    text,
    word,
):

    result = []

    start = 0

    while True:

        pos = text.find(
            word,
            start,
        )

        if pos < 0:
            break

        result.append(pos)

        start = pos + len(word)

    return result


def make_context(
    text,
    pos,
    word,
    before=12000,
    after=12000,
):

    left = max(
        0,
        pos - before,
    )

    right = min(
        len(text),
        pos + len(word) + after,
    )

    return text[left:right]


def extract_assignments(text):

    results = []

    for pattern in ASSIGN_PATTERNS:

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):

            pos = match.start()

            line_start = text.rfind(
                "\n",
                0,
                pos,
            )

            line_end = text.find(
                "\n",
                pos,
            )

            if line_start < 0:
                line_start = 0
            else:
                line_start += 1

            if line_end < 0:
                line_end = len(text)

            line = text[
                line_start:line_end
            ].strip()

            results.append({
                "pattern": pattern,
                "position": pos,
                "line": line,
            })

    return results


def find_target_files():

    result = []

    all_files = []

    all_files.extend(
        SCRIPT_DIR.glob("*FPJ0315*")
    )

    all_files.extend(
        BODY_DIR.glob("*FPJ0315*")
    )

    seen = set()

    for path in all_files:

        key = str(path).lower()

        if key in seen:
            continue

        seen.add(key)

        result.append(path)

    return sorted(result)


def main():

    print(
        "=== 020 JSJ003 prm生成元追跡 ==="
    )

    print()

    target_files = find_target_files()

    print(
        "FPJ0315候補ファイル数:",
        len(target_files),
    )

    all_results = []


    for file_index, path in enumerate(
        target_files,
        start=1,
    ):

        text = read_text(path)

        print()

        print(
            "=" * 80
        )

        print(
            f"[FILE {file_index}]"
        )

        print(
            "FILE:",
            path.name,
        )

        print(
            "PATH:",
            path,
        )

        print(
            "LENGTH:",
            len(text),
        )

        print(
            "=" * 80
        )


        file_result = {
            "name": path.name,
            "path": str(path),
            "length": len(text),
            "hits": [],
        }


        for word in TARGET_WORDS:

            positions = find_positions(
                text,
                word,
            )

            print()

            print(
                "WORD:",
                word,
            )

            print(
                "HIT:",
                len(positions),
            )


            for hit_index, pos in enumerate(
                positions,
                start=1,
            ):

                context = make_context(
                    text,
                    pos,
                    word,
                )

                assignments = (
                    extract_assignments(
                        context
                    )
                )


                hit_result = {
                    "word": word,
                    "position": pos,
                    "context": context,
                    "assignments": assignments,
                }

                file_result[
                    "hits"
                ].append(
                    hit_result
                )


                print()

                print(
                    "-" * 80
                )

                print(
                    f"{word} HIT {hit_index}"
                )

                print(
                    "POSITION:",
                    pos,
                )

                print()

                print(
                    context
                )

                print()

                print(
                    "★ prm代入候補 ★"
                )

                if assignments:

                    for assignment in assignments:

                        print(
                            assignment["line"]
                        )

                else:

                    print(
                        "なし"
                    )

                print(
                    "-" * 80
                )


        all_results.append(
            file_result
        )


    print()

    print(
        "=" * 80
    )

    print(
        "JSJ003直前Controller抽出"
    )

    print(
        "=" * 80
    )


    controller_results = []


    for path in target_files:

        text = read_text(path)

        positions = find_positions(
            text,
            "JSJ003",
        )

        for pos in positions:

            left = text.rfind(
                "var ",
                0,
                pos,
            )

            if left < 0:

                left = max(
                    0,
                    pos - 5000,
                )


            right = text.find(
                "};",
                pos,
            )

            if right < 0:

                right = min(
                    len(text),
                    pos + 5000,
                )

            else:

                right += 2


            controller_text = text[
                left:right
            ]


            result = {
                "file": path.name,
                "position": pos,
                "controller_text": (
                    controller_text
                ),
                "assignments": (
                    extract_assignments(
                        controller_text
                    )
                ),
            }


            controller_results.append(
                result
            )


            print()

            print(
                "FILE:",
                path.name,
            )

            print(
                "POSITION:",
                pos,
            )

            print()

            print(
                controller_text
            )

            print()

            print(
                "★ Controller内prm代入 ★"
            )


            if result["assignments"]:

                for assignment in (
                    result["assignments"]
                ):

                    print(
                        assignment["line"]
                    )

            else:

                print(
                    "なし"
                )


    output = {
        "program": (
            "020_trace_jsj003_params.py"
        ),
        "target_words": TARGET_WORDS,
        "file_results": all_results,
        "controller_results": (
            controller_results
        ),
    }


    save_json(
        OUT_JSON,
        output,
    )


    print()

    print(
        "=" * 80
    )

    print(
        "020 最終結果"
    )

    print(
        "=" * 80
    )

    print()

    print(
        "解析FPJ0315:",
        len(target_files),
    )

    print(
        "JSJ003 Controller候補:",
        len(controller_results),
    )

    print()

    print(
        "保存先:"
    )

    print(
        OUT_JSON
    )

    print()

    print(
        "=== 020 完了 ==="
    )


if __name__ == "__main__":

    main()