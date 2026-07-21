import json
import importlib.util
from pathlib import Path

# ==========================================================
# 015_build_historical_lines_json.py
#
# 保存済みRaceList HTML
#        ↓
# 010ライン解析
#        ↓
# JSON保存
# ==========================================================

TARGET_MONTH = "202301"

BASE = Path(r"C:\競輪AI")

HTML_DIR = (
    BASE /
    "data_official" /
    "historical" /
    "html" /
    TARGET_MONTH
)

OUTPUT_DIR = (
    BASE /
    "data_official" /
    "historical" /
    "lines" /
    TARGET_MONTH
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ==========================================================
# 010読込
# ==========================================================

PROGRAM = (
    BASE /
    "program" /
    "historical_data_program" /
    "010_extract_historical_lines.py"
)

spec = importlib.util.spec_from_file_location(
    "line_parser",
    PROGRAM
)

module = importlib.util.module_from_spec(spec)

spec.loader.exec_module(module)

parse_historical_line_html = (
    module.parse_historical_line_html
)

# ==========================================================
# HTML一覧
# ==========================================================

html_files = sorted(
    HTML_DIR.glob("*.html")
)

print("=" * 60)
print("015 Historical Line Builder")
print("=" * 60)
print()

print("TARGET MONTH :", TARGET_MONTH)
print("HTML COUNT   :", len(html_files))
print()

saved = 0
skip = 0
error = 0

# ==========================================================
# 開始
# ==========================================================

for i, html_file in enumerate(html_files, 1):

    output_json = (
        OUTPUT_DIR /
        (html_file.stem + ".json")
    )

    if output_json.exists():

        skip += 1

        print(
            f"[{i}/{len(html_files)}] "
            f"SKIP {output_json.name}"
        )

        continue

    try:

        result = parse_historical_line_html(
            html_file
        )
        with open(
            output_json,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                result,
                f,
                ensure_ascii=False,
                indent=4
            )

        saved += 1

        print(
            f"[{i}/{len(html_files)}] "
            f"SAVE {output_json.name}"
        )

    except Exception as e:

        error += 1

        print(
            f"[{i}/{len(html_files)}] "
            f"ERROR {html_file.name}"
        )

        print(type(e).__name__)
        print(e)

# ==========================================================
# 完了
# ==========================================================

print()
print("=" * 60)
print("015 Complete")
print("=" * 60)

print(f"TARGET MONTH : {TARGET_MONTH}")
print(f"HTML         : {len(html_files)}")
print(f"SAVED        : {saved}")
print(f"SKIP         : {skip}")
print(f"ERROR        : {error}")
print(f"OUTPUT DIR   : {OUTPUT_DIR}")

print()
print("Finished.")