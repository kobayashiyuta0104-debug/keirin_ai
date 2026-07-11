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
    / "022_raceinfolist_origin.json"
)


TARGET_WORDS = [
    "raceInfoList",
    "PJ0314MainData",
    "narabiyoso",
]


ORIGIN_PATTERNS = [
    r"var\s+raceInfoList\s*=",
    r"let\s+raceInfoList\s*=",
    r"const\s+raceInfoList\s*=",
    r"raceInfoList\s*=",
    r"raceInfoList\.push\s*\(",
    r'["\']raceInfoList["\']\s*:',
]


JSON_REQ_PATTERN = re.compile(
    r'JSON_REQ_ID\s*:\s*["\']'
    r'(JSJ\d{3})'
    r'["\']',
    re.IGNORECASE,
)


CONTROLLER_PATTERN = re.compile(
    r'var\s+'
    r'([A-Za-z_$][A-Za-z0-9_$]*Controller)'
    r'\s*=\s*\{',
    re.IGNORECASE,
)


REQUEST_PATTERN = re.compile(
    r'Com\.getRequestGet\s*\('
    r'.{0,1000}',
    re.IGNORECASE
    | re.DOTALL,
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

    results = []

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

        results.append(pos)

        start = pos + len(lower_word)

    return results


def make_context(
    text,
    pos,
    before,
    after,
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


def find_origin_matches(text):

    results = []

    for pattern in ORIGIN_PATTERNS:

        for match in re.finditer(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):

            pos = match.start()

            results.append({
                "pattern": pattern,
                "position": pos,
                "match": match.group(0),
                "context": make_context(
                    text,
                    pos,
                    5000,
                    5000,
                ),
            })

    return sorted(
        results,
        key=lambda x: x["position"],
    )


def find_previous_controllers(
    text,
    target_pos,
):

    results = []

    for match in CONTROLLER_PATTERN.finditer(
        text
    ):

        if match.start() >= target_pos:
            continue

        controller_name = match.group(1)

        block_start = match.start()

        block_end = min(
            len(text),
            block_start + 15000,
        )

        block = text[
            block_start:block_end
        ]

        jsj = JSON_REQ_PATTERN.findall(
            block
        )

        requests = REQUEST_PATTERN.findall(
            block
        )

        results.append({
            "controller": controller_name,
            "position": block_start,
            "distance_to_target": (
                target_pos - block_start
            ),
            "jsj": sorted(set(jsj)),
            "requests": requests,
            "context": block,
        })

    results = sorted(
        results,
        key=lambda x: x[
            "distance_to_target"
        ],
    )

    return results[:10]


def find_json_req_before(
    text,
    target_pos,
):

    results = []

    for match in JSON_REQ_PATTERN.finditer(
        text
    ):

        if match.start() >= target_pos:
            continue

        results.append({
            "jsj": match.group(1).upper(),
            "position": match.start(),
            "distance_to_target": (
                target_pos - match.start()
            ),
            "context": make_context(
                text,
                match.start(),
                3000,
                5000,
            ),
        })

    results = sorted(
        results,
        key=lambda x: x[
            "distance_to_target"
        ],
    )

    return results[:20]


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
        "=== 022 raceInfoList生成元追跡 ==="
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


        positions = find_positions(
            text,
            "PJ0314MainData",
        )


        if not positions:
            continue


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
            "PJ0314MainData HIT:",
            len(positions),
        )

        print(
            "=" * 100
        )


        origin_matches = find_origin_matches(
            text
        )


        file_result = {
            "name": path.name,
            "path": str(path),
            "length": len(text),
            "origin_matches": origin_matches,
            "target_hits": [],
        }


        print()

        print(
            "★ raceInfoList生成候補 ★"
        )


        if origin_matches:

            for item in origin_matches:

                print()

                print(
                    "PATTERN:",
                    item["pattern"],
                )

                print(
                    "POSITION:",
                    item["position"],
                )

                print(
                    "MATCH:",
                    item["match"],
                )

                print()

                print(
                    item["context"]
                )

                print(
                    "-" * 100
                )

        else:

            print(
                "なし"
            )


        for hit_index, pos in enumerate(
            positions,
            start=1,
        ):

            previous_controllers = (
                find_previous_controllers(
                    text,
                    pos,
                )
            )

            previous_json_req = (
                find_json_req_before(
                    text,
                    pos,
                )
            )


            hit_result = {
                "position": pos,
                "target_context": make_context(
                    text,
                    pos,
                    15000,
                    5000,
                ),
                "previous_controllers": (
                    previous_controllers
                ),
                "previous_json_req": (
                    previous_json_req
                ),
            }


            file_result[
                "target_hits"
            ].append(
                hit_result
            )


            print()

            print(
                "#" * 100
            )

            print(
                "PJ0314MainData HIT",
                hit_index,
            )

            print(
                "POSITION:",
                pos,
            )

            print(
                "#" * 100
            )


            print()

            print(
                "★ 直前Controller候補 ★"
            )


            if previous_controllers:

                for controller in (
                    previous_controllers
                ):

                    print()

                    print(
                        "CONTROLLER:",
                        controller[
                            "controller"
                        ],
                    )

                    print(
                        "POSITION:",
                        controller[
                            "position"
                        ],
                    )

                    print(
                        "DISTANCE:",
                        controller[
                            "distance_to_target"
                        ],
                    )

                    print(
                        "JSJ:",
                        controller["jsj"],
                    )

                    print()

                    print(
                        controller["context"]
                    )

                    print(
                        "-" * 100
                    )

            else:

                print(
                    "なし"
                )


            print()

            print(
                "★ 直前JSON_REQ_ID候補 ★"
            )


            if previous_json_req:

                for item in previous_json_req:

                    print()

                    print(
                        "JSJ:",
                        item["jsj"],
                    )

                    print(
                        "POSITION:",
                        item["position"],
                    )

                    print(
                        "DISTANCE:",
                        item[
                            "distance_to_target"
                        ],
                    )

                    print()

                    print(
                        item["context"]
                    )

                    print(
                        "-" * 100
                    )

            else:

                print(
                    "なし"
                )


            print()

            print(
                "★ PJ0314MainData直前15000文字 ★"
            )

            print()

            print(
                hit_result["target_context"]
            )


        results.append(
            file_result
        )


    output = {
        "program": (
            "022_trace_raceinfolist_origin.py"
        ),
        "target_words": TARGET_WORDS,
        "origin_patterns": ORIGIN_PATTERNS,
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
        "022 最終結果"
    )

    print(
        "=" * 100
    )

    print()

    print(
        "PJ0314MainData対象ファイル:",
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
        "=== 022 完了 ==="
    )


if __name__ == "__main__":

    main()