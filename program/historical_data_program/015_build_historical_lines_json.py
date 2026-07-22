import json
import re
import tempfile
import importlib.util

from pathlib import Path

# ==========================================================
# 015_build_historical_lines_json.py
#
# 1日HTML
#      ↓
# RACE_KEYごとに分割
#      ↓
# 010ライン解析
#      ↓
# 1日JSON保存
# ==========================================================

BASE = Path(r"C:\競輪AI")

HTML_DIR = (
    BASE /
    "data_official" /
    "historical" /
    "html"
)

OUTPUT_DIR = (
    BASE /
    "data_official" /
    "historical" /
    "lines"
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

print("=" * 70)
print("015 Historical Line Builder")
print("=" * 70)
print()

print("DAY HTML :", len(html_files))
print()

saved = 0
skip = 0
error = 0

# ==========================================================
# 開始
# ==========================================================

for day_index, html_file in enumerate(html_files, 1):

    target_date = html_file.stem

    output_json = (
        OUTPUT_DIR /
        f"{target_date}_lines.json"
    )

    if output_json.exists():

        skip += 1

        print(
            f"[{day_index}/{len(html_files)}] "
            f"SKIP {output_json.name}"
        )

        continue

    print()
    print("=" * 70)
    print(target_date)
    print("=" * 70)

    with open(
        html_file,
        "r",
        encoding="utf-8"
    ) as f:

        html_text = f.read()

    # ------------------------------------------------------
    # RACE_KEY位置検索
    # ------------------------------------------------------

    matches = list(

        re.finditer(

            r"<!-- RACE_KEY=(.*?) -->",

            html_text

        )

    )

    races = []

    line_found_count = 0

    # ------------------------------------------------------
    # レースごとに解析
    # ------------------------------------------------------

    for idx, match in enumerate(matches):

        race_key = match.group(1).strip()

        start = match.end()

        if idx + 1 < len(matches):

            end = matches[idx + 1].start()

        else:

            end = len(html_text)

        race_html = html_text[start:end]
        race_html = race_html.replace("<!-- END_RACE -->", "")

        # 一時HTML作成
        with tempfile.TemporaryDirectory() as temp_dir:

            temp_file = (
                Path(temp_dir) /
                f"{race_key}.html"
            )

            with open(
                temp_file,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(race_html)

            try:

                result = parse_historical_line_html(
                    temp_file
                )

                races.append(result)

                if result["line_found"]:

                    line_found_count += 1

                print(
                    f"  OK  {race_key}"
                )

            except Exception as e:

                races.append({

                    "race_key": race_key,

                    "line_found": False,

                    "error": str(e)

                })

                print(
                    f"  ERROR {race_key}"
                )

                print(type(e).__name__)
                print(e)

    # ------------------------------------------------------
    # JSON保存
    # ------------------------------------------------------

    output = {

        "target_date": target_date,

        "race_count": len(races),

        "line_found_count": line_found_count,

        "races": races

    }

    try:

        with open(
            output_json,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                output,
                f,
                ensure_ascii=False,
                indent=4
            )

        saved += 1

        print()
        print(
            f"SAVE {output_json.name}"
        )

    except Exception as e:

        error += 1

        print()
        print(
            f"ERROR {output_json.name}"
        )

        print(type(e).__name__)
        print(e)

# ==========================================================
# 完了
# ==========================================================

print()
print("=" * 70)
print("015 Complete")
print("=" * 70)

print(f"DAY HTML : {len(html_files)}")
print(f"SAVED    : {saved}")
print(f"SKIP     : {skip}")
print(f"ERROR    : {error}")
print(f"OUTPUT   : {OUTPUT_DIR}")

print()
print("Finished.")