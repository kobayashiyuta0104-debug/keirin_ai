import json
import time
import traceback
from pathlib import Path


# ==========================================================
# 012_merge_historical_lines_json.py
#
# 1レース1JSONを
# historical_lines.json に統合する
# ==========================================================

BASE = Path(r"C:\競輪AI")

JSON_DIR = (
    BASE
    / "data_official"
    / "historical"
    / "html"
    / "json"
)

OUTPUT_JSON = (
    BASE
    / "data_official"
    / "historical"
    / "historical_lines.json"
)

ERROR_LOG = (
    BASE
    / "data_official"
    / "historical"
    / "historical_lines_error_log.txt"
)


# ==========================================================
# JSON一覧取得
# ==========================================================

def collect_json_files():

    files = []

    for file in JSON_DIR.glob("*.json"):

        if file.name == "historical_lines.json":
            continue
        if file.name == "historical_line_test.json":
            continue

        if file.name == "error_log.txt":
            continue

        files.append(file)

    files.sort()

    return files


# ==========================================================
# JSON読込
# ==========================================================

def load_json(path):

    with open(path, "r", encoding="utf-8") as f:

        return json.load(f)


# ==========================================================
# エラーログ
# ==========================================================

def write_error(file_path, e):

    ERROR_LOG.parent.mkdir(
        parents=True,
        exist_ok=True
)

    with open(ERROR_LOG, "a", encoding="utf-8") as f:

        f.write("=" * 80 + "\n")
        f.write(str(file_path) + "\n")
        f.write(type(e).__name__ + "\n")
        f.write(str(e) + "\n")
        f.write(traceback.format_exc())
        f.write("\n")


# ==========================================================
# 保存
# ==========================================================

def save_json(data):

    OUTPUT_JSON.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


# ==========================================================
# Main
# ==========================================================

def main():

    start = time.time()

    if ERROR_LOG.exists():

        ERROR_LOG.unlink()

    json_files = collect_json_files()

    total = len(json_files)

    success = 0

    failed = 0

    line_found = 0

    seri_race = 0

    merged = []

    print("=" * 60)
    print("012 Merge Historical Lines JSON")
    print("=" * 60)
    print()

    print("JSON Files :", total)
    print()

    for index, json_file in enumerate(json_files, start=1):

        print(f"[{index}/{total}] {json_file.name}")

        try:

            data = load_json(json_file)

            merged.append(data)

            success += 1

            if data.get("line_found"):

                line_found += 1

            has_seri = False

            for car in data.get("cars", {}).values():

                if car["seri"] == 1:

                    has_seri = True
                    break

            if has_seri:

                seri_race += 1

        except Exception as e:

            failed += 1

            write_error(json_file, e)

            print("   ERROR :", type(e).__name__)
            print("   ", e)

    # race_key順
    merged.sort(
        key=lambda x: x.get("race_key", "")
    )

    save_json(merged)

    elapsed = time.time() - start

    hour = int(elapsed // 3600)

    minute = int((elapsed % 3600) // 60)

    second = int(elapsed % 60)

    print()

    print("=" * 60)
    print("Completed")
    print("=" * 60)

    print(f"JSON Files : {total}")
    print(f"Success    : {success}")
    print(f"Failed     : {failed}")
    print(f"Line Found : {line_found}")
    print(f"Seri Race  : {seri_race}")

    print()

    print("Output")

    print(OUTPUT_JSON)

    print()

    print(
        f"Elapsed : "
        f"{hour:02d}:{minute:02d}:{second:02d}"
    )

    print("=" * 60)


# ==========================================================
# 実行
# ==========================================================

if __name__ == "__main__":

    main()