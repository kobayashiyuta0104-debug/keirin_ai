from pathlib import Path
import json
from urllib.parse import urlparse, parse_qs


BASE = Path(r"C:\競輪AI")

CAPTURE_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "016_official_syusou_capture"
)

OUT_JSON = (
    CAPTURE_DIR
    / "024_real_jsj002_capture.json"
)


TARGET_TYPE = "JSJ002"


def read_json(path):

    try:

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    except Exception:

        return None


def read_text(path):

    try:

        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    except Exception:

        return ""


def find_json_files():

    results = []

    for path in CAPTURE_DIR.rglob("*.json"):

        if path == OUT_JSON:
            continue

        results.append(path)

    return sorted(results)


def find_jsj002_in_object(
    obj,
    source_path,
    location="root",
):

    results = []


    if isinstance(obj, dict):

        url = obj.get("url")

        if isinstance(url, str):

            if TARGET_TYPE.lower() in url.lower():

                parsed = urlparse(url)

                results.append({
                    "source_path": str(source_path),
                    "location": location,
                    "record": obj,
                    "url": url,
                    "scheme": parsed.scheme,
                    "netloc": parsed.netloc,
                    "path": parsed.path,
                    "query": parsed.query,
                    "query_params": parse_qs(
                        parsed.query
                    ),
                })


        for key, value in obj.items():

            child_location = (
                f"{location}.{key}"
            )

            results.extend(
                find_jsj002_in_object(
                    value,
                    source_path,
                    child_location,
                )
            )


    elif isinstance(obj, list):

        for index, value in enumerate(obj):

            child_location = (
                f"{location}[{index}]"
            )

            results.extend(
                find_jsj002_in_object(
                    value,
                    source_path,
                    child_location,
                )
            )


    return results


def find_body_candidates():

    results = []

    body_dir = (
        CAPTURE_DIR
        / "response_bodies"
    )

    if not body_dir.exists():

        return results


    for path in sorted(body_dir.glob("*")):

        text = read_text(path)

        if not text:
            continue


        lower = text.lower()


        if (
            '"raceinfo"' in lower
            or '"pj0314maindata"' in lower
            or '"narabiyoso"' in lower
        ):

            results.append({
                "name": path.name,
                "path": str(path),
                "length": len(text),
                "has_raceInfo": (
                    '"raceinfo"' in lower
                ),
                "has_PJ0314MainData": (
                    '"pj0314maindata"' in lower
                ),
                "has_narabiyoso": (
                    '"narabiyoso"' in lower
                ),
                "head": text[:5000],
            })


    return results


def main():

    print(
        "=== 024 実JSJ002通信抽出 ==="
    )

    print()


    json_files = find_json_files()

    print(
        "探索JSON数:",
        len(json_files),
    )


    jsj002_hits = []


    for path in json_files:

        data = read_json(path)

        if data is None:
            continue


        hits = find_jsj002_in_object(
            data,
            path,
        )


        jsj002_hits.extend(hits)


    print()

    print(
        "★ JSJ002通信HIT:",
        len(jsj002_hits),
    )


    for index, hit in enumerate(
        jsj002_hits,
        start=1,
    ):

        print()

        print(
            "=" * 100
        )

        print(
            f"[JSJ002 HIT {index}]"
        )

        print(
            "SOURCE:",
            hit["source_path"],
        )

        print(
            "LOCATION:",
            hit["location"],
        )

        print(
            "URL:",
            hit["url"],
        )

        print(
            "PATH:",
            hit["path"],
        )

        print(
            "QUERY:",
            hit["query"],
        )

        print(
            "QUERY PARAMS:"
        )

        print(
            json.dumps(
                hit["query_params"],
                ensure_ascii=False,
                indent=2,
            )
        )

        print()

        print(
            "FULL RECORD:"
        )

        print(
            json.dumps(
                hit["record"],
                ensure_ascii=False,
                indent=2,
            )
        )


    body_candidates = (
        find_body_candidates()
    )


    print()

    print(
        "#" * 100
    )

    print(
        "★ raceInfo / PJ0314MainData "
        "/ narabiyoso BODY候補:",
        len(body_candidates),
    )

    print(
        "#" * 100
    )


    for index, item in enumerate(
        body_candidates,
        start=1,
    ):

        print()

        print(
            "-" * 100
        )

        print(
            f"[BODY {index}]"
        )

        print(
            "FILE:",
            item["name"],
        )

        print(
            "PATH:",
            item["path"],
        )

        print(
            "LENGTH:",
            item["length"],
        )

        print(
            "raceInfo:",
            item["has_raceInfo"],
        )

        print(
            "PJ0314MainData:",
            item[
                "has_PJ0314MainData"
            ],
        )

        print(
            "narabiyoso:",
            item["has_narabiyoso"],
        )

        print()

        print(
            "HEAD:"
        )

        print(
            item["head"]
        )


    output = {
        "program": (
            "024_extract_real_jsj002_capture.py"
        ),
        "target_type": TARGET_TYPE,
        "jsj002_hits": jsj002_hits,
        "body_candidates": body_candidates,
    }


    with open(
        OUT_JSON,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2,
        )


    print()

    print(
        "=" * 100
    )

    print(
        "024 最終結果"
    )

    print(
        "=" * 100
    )

    print()

    print(
        "JSJ002通信HIT:",
        len(jsj002_hits),
    )

    print(
        "BODY候補:",
        len(body_candidates),
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
        "=== 024 完了 ==="
    )


if __name__ == "__main__":

    main()