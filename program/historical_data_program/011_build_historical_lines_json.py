import importlib.util
import traceback
import time
from pathlib import Path


# ==========================================================
# 011_build_historical_lines_json.py
#
# historical/html 内の全HTMLを解析し、
# historical/html/json に1レース1JSONとして保存する
# ==========================================================


BASE = Path(r"C:\競輪AI")

PROGRAM = (
    BASE
    / "program"
    / "historical_data_program"
    / "010_extract_historical_lines.py"
)

HTML_DIR = (
    BASE
    / "data_official"
    / "historical"
    / "html"
)

OUTPUT_DIR = HTML_DIR / "json"

ERROR_LOG = OUTPUT_DIR / "error_log.txt"


# ==========================================================
# 010読込
# ==========================================================

spec = importlib.util.spec_from_file_location(
    "historical_lines",
    PROGRAM
)

parser = importlib.util.module_from_spec(spec)

spec.loader.exec_module(parser)


# ==========================================================
# HTML一覧取得
# ==========================================================

def collect_html_files():

    html_files = []

    for file in HTML_DIR.rglob("*.html"):

        if file.is_file():

            html_files.append(file)

    html_files.sort()

    return html_files


# ==========================================================
# JSON保存先
# ==========================================================

def build_output_path(html_file):

    return OUTPUT_DIR / f"{html_file.stem}.json"


# ==========================================================
# エラーログ
# ==========================================================

def write_error(html_file, e):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(ERROR_LOG, "a", encoding="utf-8") as f:

        f.write("=" * 80 + "\n")

        f.write(str(html_file) + "\n")

        f.write(type(e).__name__ + "\n")

        f.write(str(e) + "\n")

        f.write(traceback.format_exc())

        f.write("\n")


# ==========================================================
# メイン
# ==========================================================

def main():

    start = time.time()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if ERROR_LOG.exists():

        ERROR_LOG.unlink()

    html_files = collect_html_files()

    total = len(html_files)

    success = 0

    failed = 0

    line_found = 0

    seri_race = 0

    print("=" * 60)

    print("011 Historical Lines Builder")

    print("=" * 60)

    print()

    print("HTML Files :", total)

    print()

    for index, html_file in enumerate(html_files, start=1):

        print(f"[{index}/{total}] {html_file.name}")

        try:

            result = parser.parse_historical_line_html(html_file)

            output_json = build_output_path(html_file)

            parser.save_json(result, output_json)

            success += 1

            if result["line_found"]:
                line_found += 1

            # -----------------------------
            # 競りレース判定
            # -----------------------------
            has_seri = False

            for car in result["cars"].values():

                if car["seri"] == 1:

                    has_seri = True
                    break

            if has_seri:

                seri_race += 1

        except Exception as e:

            failed += 1

            write_error(html_file, e)

            print("   ERROR :", type(e).__name__)
            print("   ", e)

    elapsed = time.time() - start

    hour = int(elapsed // 3600)

    minute = int((elapsed % 3600) // 60)

    second = int(elapsed % 60)

    print()

    print("=" * 60)

    print("Completed")

    print("=" * 60)

    print(f"HTML Files : {total}")
    print(f"Success    : {success}")
    print(f"Failed     : {failed}")
    print(f"Line Found : {line_found}")
    print(f"Seri Race  : {seri_race}")

    print()

    print("Output Folder")

    print(OUTPUT_DIR)

    print()

    print(
        "Elapsed : "
        f"{hour:02d}:{minute:02d}:{second:02d}"
    )

    print("=" * 60)


# ==========================================================
# 実行
# ==========================================================

if __name__ == "__main__":

    main()