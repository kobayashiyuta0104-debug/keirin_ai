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
    / "021_real_narabiyoso_source.json"
)


TARGET_WORDS = [
    "PJ0314MainData",
    "narabiyoso",
    "sllblNarabiMei",
    "trNarabiDigest",
    "narabiMei",
    "edtNarabi",
]


JSJ_PATTERN = re.compile(
    r"\bJSJ\d{3}\b",
    re.IGNORECASE,
)


CONTROLLER_PATTERN = re.compile(
    r"\b[A-Za-z_$][A-Za-z0-9_$]*Controller\b"
)


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

    lower_text = text.lower()
    lower_word = word.lower()

    start = 0

    while True:

        pos = lower_text.find(
            lower_word,
            start,
        )

        if pos < 0:
            break

        result.append(pos)

        start = pos + len(lower_word)

    return result


def make_context(
    text,
    pos,
    word,
    before=20000,
    after=20000,
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


def extract_jsj(text):

    return sorted({
        value.upper()
        for value in JSJ_PATTERN.findall(
            text
        )
    })


def extract_controllers(text):

    return sorted({
        value
        for value in CONTROLLER_PATTERN.findall(
            text
        )
    })


def extract_request_calls(text):

    patterns = [
        r"Com\.getRequestGet\s*\([^;]{0,1000}",
        r"Com\.getRequest\s*\([^;]{0,1000}",
        r"getRequestGet\s*\([^;]{0,1000}",
        r"getRequest\s*\([^;]{0,1000}",
    ]

    results = []

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE
            | re.DOTALL,
        ):

            results.append(
                match.group(0)
            )

    return results


def extract_json_req_blocks(text):

    results = []

    for match in re.finditer(
        r'JSON_REQ_ID\s*:\s*["\']JSJ\d{3}["\']',
        text,
        flags=re.IGNORECASE,
    ):

        pos = match.start()

        left = max(
            0,
            pos - 3000,
        )

        right = min(
            len(text),
            pos + 5000,
        )

        results.append({
            "position": pos,
            "match": match.group(0),
            "context": text[left:right],
        })

    return results


def all_target_files():

    files = []

    files.extend(
        SCRIPT_DIR.glob("*")
    )

    files.extend(
        BODY_DIR.glob("*")
    )

    seen = set()

    result = []

    for path in files:

        key = str(path).lower()

        if key in seen:
            continue

        seen.add(key)

        result.append(path)

    return sorted(result)


def main():

    print(
        "=== 021 本物のnarabiyoso取得元特定 ==="
    )

    print()

    files = all_target_files()

    print(
        "探索ファイル数:",
        len(files),
    )

    hit_files = []


    for path in files:

        text = read_text(path)

        if not text:
            continue

        file_hits = []


        for word in TARGET_WORDS:

            positions = find_positions(
                text,
                word,
            )


            for pos in positions:

                context = make_context(
                    text,
                    pos,
                    word,
                )


                hit = {
                    "word": word,
                    "position": pos,
                    "context": context,
                    "jsj_types": extract_jsj(
                        context
                    ),
                    "controllers": (
                        extract_controllers(
                            context
                        )
                    ),
                    "request_calls": (
                        extract_request_calls(
                            context
                        )
                    ),
                    "json_req_blocks": (
                        extract_json_req_blocks(
                            context
                        )
                    ),
                }


                file_hits.append(
                    hit
                )


        if file_hits:

            hit_files.append({
                "name": path.name,
                "path": str(path),
                "length": len(text),
                "hits": file_hits,
            })


    print()

    print(
        "★ HITファイル数:",
        len(hit_files),
    )


    for file_index, result in enumerate(
        hit_files,
        start=1,
    ):

        print()

        print(
            "=" * 100
        )

        print(
            f"[HIT FILE {file_index}]"
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
            "HIT数:",
            len(result["hits"]),
        )

        print(
            "=" * 100
        )


        for hit_index, hit in enumerate(
            result["hits"],
            start=1,
        ):

            print()

            print(
                "-" * 100
            )

            print(
                f"HIT {hit_index}"
            )

            print(
                "WORD:",
                hit["word"],
            )

            print(
                "POSITION:",
                hit["position"],
            )

            print(
                "JSJ:",
                hit["jsj_types"],
            )

            print(
                "CONTROLLERS:",
                hit["controllers"],
            )

            print()

            print(
                "★ REQUEST CALLS ★"
            )


            if hit["request_calls"]:

                for call in hit[
                    "request_calls"
                ]:

                    print()

                    print(call)

            else:

                print(
                    "なし"
                )


            print()

            print(
                "★ JSON_REQ_ID BLOCKS ★"
            )


            if hit["json_req_blocks"]:

                for block in hit[
                    "json_req_blocks"
                ]:

                    print()

                    print(
                        block["match"]
                    )

                    print()

                    print(
                        block["context"]
                    )

            else:

                print(
                    "なし"
                )


            print()

            print(
                "★ TARGET CONTEXT ★"
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
            "021_find_real_narabiyoso_source.py"
        ),
        "target_words": TARGET_WORDS,
        "hit_files": hit_files,
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
        "021 最終結果"
    )

    print(
        "=" * 100
    )

    print()

    print(
        "探索ファイル:",
        len(files),
    )

    print(
        "HITファイル:",
        len(hit_files),
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
        "=== 021 完了 ==="
    )


if __name__ == "__main__":

    main()