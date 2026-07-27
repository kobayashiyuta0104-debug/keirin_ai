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
    / "019_getrequestget_definition.json"
)


PATTERNS = [
    r"getRequestGet\s*[:=]\s*function",
    r"getRequestGet\s*=\s*function",
    r"function\s+getRequestGet",
    r"Com\s*=\s*\{",
    r"var\s+Com\s*=\s*\{",
    r"const\s+Com\s*=\s*\{",
    r"let\s+Com\s*=\s*\{",
    r"getRequestGet",
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
    position,
    radius=6000,
):

    left = max(
        0,
        position - radius,
    )

    right = min(
        len(text),
        position + radius,
    )

    return text[left:right]


def main():

    print(
        "=== 019 Com.getRequestGet 定義本体探索 ==="
    )

    all_files = []

    all_files.extend(
        SCRIPT_DIR.glob("*")
    )

    all_files.extend(
        BODY_DIR.glob("*")
    )

    seen = set()

    results = []

    print()

    print(
        "探索ファイル数:",
        len(all_files),
    )

    for path in all_files:

        key = str(path).lower()

        if key in seen:
            continue

        seen.add(key)

        text = read_text(path)

        if not text:
            continue

        file_hits = []

        for pattern in PATTERNS:

            matches = list(
                re.finditer(
                    pattern,
                    text,
                    flags=re.IGNORECASE,
                )
            )

            for match in matches:

                file_hits.append({
                    "pattern": pattern,
                    "position": match.start(),
                    "matched_text": match.group(0),
                    "context": make_context(
                        text,
                        match.start(),
                    ),
                })

        if not file_hits:
            continue

        result = {
            "path": str(path),
            "name": path.name,
            "length": len(text),
            "hits": file_hits,
        }

        results.append(result)


    print()

    print(
        "HITファイル数:",
        len(results),
    )


    priority_results = []

    normal_results = []


    for result in results:

        priority = False

        for hit in result["hits"]:

            pattern = hit["pattern"]

            if pattern != "getRequestGet":

                priority = True

                break

        if priority:

            priority_results.append(
                result
            )

        else:

            normal_results.append(
                result
            )


    print()

    print(
        "★ 定義候補ファイル数:",
        len(priority_results),
    )

    print(
        "★ 呼出のみ候補ファイル数:",
        len(normal_results),
    )


    print()

    print(
        "=" * 80
    )

    print(
        "最優先：定義候補"
    )

    print(
        "=" * 80
    )


    for file_index, result in enumerate(
        priority_results,
        start=1,
    ):

        print()

        print(
            "#" * 80
        )

        print(
            f"[DEFINITION FILE {file_index}]"
        )

        print(
            "FILE:",
            result["name"],
        )

        print(
            "PATH:",
            result["path"],
        )

        print(
            "LENGTH:",
            result["length"],
        )

        print(
            "#" * 80
        )


        for hit_index, hit in enumerate(
            result["hits"],
            start=1,
        ):

            print()

            print(
                "-" * 80
            )

            print(
                f"HIT {hit_index}"
            )

            print(
                "PATTERN:",
                hit["pattern"],
            )

            print(
                "MATCH:",
                hit["matched_text"],
            )

            print(
                "POSITION:",
                hit["position"],
            )

            print()

            print(
                hit["context"]
            )

            print(
                "-" * 80
            )


    print()

    print(
        "=" * 80
    )

    print(
        "参考：getRequestGet呼出ファイル一覧"
    )

    print(
        "=" * 80
    )


    for result in normal_results:

        print(
            result["name"],
            "HIT:",
            len(result["hits"]),
        )


    output = {
        "program": (
            "019_find_com_getrequestget_definition.py"
        ),
        "patterns": PATTERNS,
        "priority_results": (
            priority_results
        ),
        "normal_results": (
            normal_results
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
        "019 最終結果"
    )

    print(
        "=" * 80
    )

    print()

    print(
        "定義候補:",
        len(priority_results),
    )

    print(
        "呼出のみ:",
        len(normal_results),
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
        "=== 019 完了 ==="
    )


if __name__ == "__main__":

    main()