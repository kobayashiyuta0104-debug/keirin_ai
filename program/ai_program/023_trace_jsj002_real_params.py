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
    / "023_jsj002_real_params.json"
)


TARGET_WORDS = [
    "apController.apCreateList",
    'gReqPrmsObject["PJ0307"]',
    "gReqPrmsObject['PJ0307']",
    "PJ0307",
    "JSJ002",
]


PATTERNS = [
    r'apController\.apCreateList\s*\(',
    r'gReqPrmsObject\s*\[\s*["\']PJ0307["\']\s*\]',
    r'PJ0307',
    r'JSJ002',
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


def make_context(
    text,
    pos,
    before=10000,
    after=10000,
):

    left = max(
        0,
        pos - before,
    )

    right = min(
        len(text),
        pos + after,
    )

    return text[left:right]


def extract_param_assignments(text):

    patterns = [
        r'params\s*\[\s*["\'][^"\']+["\']\s*\]\s*=[^;\n]+',
        r'para\s*\[\s*["\'][^"\']+["\']\s*\]\s*=[^;\n]+',
        r'prm\s*\[\s*["\'][^"\']+["\']\s*\]\s*=[^;\n]+',
        r'params\.[A-Za-z_$][A-Za-z0-9_$]*\s*=[^;\n]+',
        r'para\.[A-Za-z_$][A-Za-z0-9_$]*\s*=[^;\n]+',
        r'prm\.[A-Za-z_$][A-Za-z0-9_$]*\s*=[^;\n]+',
    ]

    results = []

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):

            results.append({
                "pattern": pattern,
                "position": match.start(),
                "text": match.group(0),
            })

    return sorted(
        results,
        key=lambda x: x["position"],
    )


def extract_object_assignments(text):

    patterns = [
        r'gReqPrmsObject\s*\[[^\]]+\]\s*=[^;\n]+',
        r'gReqPrmsObject\.[A-Za-z_$][A-Za-z0-9_$]*\s*=[^;\n]+',
        r'var\s+gReqPrmsObject\s*=[^;\n]+',
        r'gReqPrmsObject\s*=[^;\n]+',
    ]

    results = []

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):

            results.append({
                "pattern": pattern,
                "position": match.start(),
                "text": match.group(0),
            })

    return sorted(
        results,
        key=lambda x: x["position"],
    )


def all_files():

    paths = []

    paths.extend(
        SCRIPT_DIR.glob("*")
    )

    paths.extend(
        BODY_DIR.glob("*")
    )

    seen = set()

    results = []

    for path in paths:

        key = str(path).lower()

        if key in seen:
            continue

        seen.add(key)

        results.append(path)

    return sorted(results)


def main():

    print(
        "=== 023 JSJ002 実params追跡 ==="
    )

    print()

    files = all_files()

    print(
        "探索ファイル数:",
        len(files),
    )


    results = []


    for path in files:

        text = read_text(path)

        if not text:
            continue


        file_hits = []


        for pattern in PATTERNS:

            for match in re.finditer(
                pattern,
                text,
                flags=re.IGNORECASE,
            ):

                pos = match.start()

                context = make_context(
                    text,
                    pos,
                )


                file_hits.append({
                    "pattern": pattern,
                    "match": match.group(0),
                    "position": pos,
                    "context": context,
                    "param_assignments": (
                        extract_param_assignments(
                            context
                        )
                    ),
                    "object_assignments": (
                        extract_object_assignments(
                            context
                        )
                    ),
                })


        if not file_hits:
            continue


        file_result = {
            "name": path.name,
            "path": str(path),
            "length": len(text),
            "hits": file_hits,
        }


        results.append(
            file_result
        )


        print()

        print(
            "=" * 100
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
            "HIT:",
            len(file_hits),
        )

        print(
            "=" * 100
        )


        for hit_index, hit in enumerate(
            file_hits,
            start=1,
        ):

            print()

            print(
                "#" * 100
            )

            print(
                "HIT",
                hit_index,
            )

            print(
                "PATTERN:",
                hit["pattern"],
            )

            print(
                "MATCH:",
                hit["match"],
            )

            print(
                "POSITION:",
                hit["position"],
            )

            print(
                "#" * 100
            )


            print()

            print(
                "★ PARAM代入候補 ★"
            )


            if hit["param_assignments"]:

                for item in hit[
                    "param_assignments"
                ]:

                    print(
                        item["text"]
                    )

            else:

                print(
                    "なし"
                )


            print()

            print(
                "★ gReqPrmsObject代入候補 ★"
            )


            if hit["object_assignments"]:

                for item in hit[
                    "object_assignments"
                ]:

                    print(
                        item["text"]
                    )

            else:

                print(
                    "なし"
                )


            print()

            print(
                "★ CONTEXT ★"
            )

            print()

            print(
                hit["context"]
            )

            print(
                "-" * 100
            )


    output = {
        "program": (
            "023_trace_jsj002_real_params.py"
        ),
        "target_words": TARGET_WORDS,
        "patterns": PATTERNS,
        "results": results,
    }


    save_json(
        OUT_JSON,
        output,
    )


    print()

    print(
        "=" * 100
    )

    print(
        "023 最終結果"
    )

    print(
        "=" * 100
    )

    print()

    print(
        "HITファイル:",
        len(results),
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
        "=== 023 完了 ==="
    )


if __name__ == "__main__":

    main()