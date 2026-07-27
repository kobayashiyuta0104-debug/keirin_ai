"""
===========================================================
競輪AI 正式版
013_search_line_data.py

目的:
・保存済みHistorical RAWからライン・並び情報候補を探索
・JSJ001 / JSJ006 / JSJ012を再帰走査
・キー名によるライン候補探索
・値による並び候補探索
・車番配列らしいLIST構造探索
・全2565 NORMALレース横断調査
・候補PATH頻度集計
・代表サンプル保存

重要:
・RAWは変更しない
・ライン情報の存在確認専用
===========================================================
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict


# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

HISTORICAL_RAW_DIR = (
    BASE
    / "data_official"
    / "historical_raw"
)

CLASSIFICATION_FILE = (
    BASE
    / "data_official"
    / "historical_raw"
    / "006_classified_historical_races.json"
)
OUT_DIR = (
    BASE
    / "data_official"
    / "models"
    / "013_line_data_search"
)

RESULT_FILE = (
    OUT_DIR
    / "013_line_data_search_results.json"
)


# ===========================================================
# 探索設定
# ===========================================================

KEYWORDS = [
    "line",
    "LINE",
    "Line",
    "narabi",
    "NARABI",
    "Narabi",
    "nami",
    "並び",
    "ならび",
    "ライン",
    "yoso",
    "YOSO",
    "Yoso",
    "forecast",
    "formation",
    "group",
    "team",
    "renkei",
    "RENKEI",
    "連携",
    "番手",
    "単騎",
    "先頭",
]


MAX_SAMPLES_PER_PATH = 10


# ===========================================================
# JSON
# ===========================================================

def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def save_json(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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


# ===========================================================
# NORMAL race_key取得
# ===========================================================

def extract_normal_race_keys(data):

    normal_keys = []

    def walk(obj):

        if isinstance(obj, dict):

            race_key = obj.get("race_key")

            classification = (
                obj.get("classification")
                or obj.get("race_classification")
                or obj.get("status")
            )

            if (
                race_key
                and classification == "NORMAL"
            ):

                normal_keys.append(
                    race_key
                )

            for value in obj.values():

                walk(value)

        elif isinstance(obj, list):

            for item in obj:

                walk(item)

    walk(data)

    return sorted(
        set(normal_keys)
    )


# ===========================================================
# RAWファイル探索
# ===========================================================

def find_raw_json_files():

    files = []

    for path in HISTORICAL_RAW_DIR.rglob(
        "*.json"
    ):

        if path.name.startswith(
            "004_collection_"
        ):

            continue

        if path.name.startswith(
            "005_"
        ):

            continue

        if path.name.startswith(
            "006_"
        ):

            continue

        files.append(path)

    return sorted(files)


# ===========================================================
# race_key索引
# ===========================================================

def build_race_index(
    raw_files,
    target_race_keys,
):

    target_set = set(
        target_race_keys
    )

    race_index = {}

    for file_index, path in enumerate(
        raw_files,
        start=1,
    ):

        try:

            data = load_json(path)

        except Exception:

            continue

        def walk(obj):

            if isinstance(obj, dict):

                race_key = obj.get(
                    "race_key"
                )

                if (
                    race_key in target_set
                    and race_key not in race_index
                ):

                    race_index[race_key] = {
                        "file": str(path),
                        "data": obj,
                    }

                for value in obj.values():

                    walk(value)

            elif isinstance(obj, list):

                for item in obj:

                    walk(item)

        walk(data)

        if (
            file_index % 20 == 0
            or file_index == len(raw_files)
        ):

            print(
                "RAW索引:",
                file_index,
                "/",
                len(raw_files),
                "| 発見race:",
                len(race_index),
            )

    return race_index


# ===========================================================
# PATH
# ===========================================================

def make_path(
    parent,
    key,
):

    if not parent:

        return f"$.{key}"

    return f"{parent}.{key}"


# ===========================================================
# キーワード判定
# ===========================================================

def contains_keyword(text):

    text = str(text)

    for keyword in KEYWORDS:

        if keyword in text:

            return True

    return False


# ===========================================================
# 車番らしい値
# ===========================================================

def normalize_number(value):

    if isinstance(value, bool):

        return None

    if isinstance(value, int):

        if 1 <= value <= 9:

            return value

    if isinstance(value, float):

        if (
            value.is_integer()
            and 1 <= int(value) <= 9
        ):

            return int(value)

    if isinstance(value, str):

        text = value.strip()

        if re.fullmatch(
            r"[1-9]",
            text,
        ):

            return int(text)

    return None


# ===========================================================
# 車番LIST判定
# ===========================================================

def analyze_number_list(obj):

    if not isinstance(obj, list):

        return None

    if len(obj) < 2:

        return None

    numbers = []

    for item in obj:

        number = normalize_number(item)

        if number is None:

            return None

        numbers.append(number)

    if len(set(numbers)) != len(numbers):

        return None

    return numbers


# ===========================================================
# 文字列並び候補
# ===========================================================

def analyze_string_formation(value):

    if not isinstance(value, str):

        return None

    text = value.strip()

    if not text:

        return None

    digits = re.findall(
        r"[1-9]",
        text,
    )

    unique_digits = set(digits)

    if len(unique_digits) < 2:

        return None

    formation_symbols = [
        "-",
        "－",
        "=",
        "＝",
        "/",
        "／",
        ",",
        "，",
        " ",
        "→",
        ">",
        "＞",
        "・",
    ]

    if not any(
        symbol in text
        for symbol in formation_symbols
    ):

        return None

    return {
        "text": text,
        "digits": digits,
    }


# ===========================================================
# 再帰探索
# ===========================================================

def search_object(
    obj,
    race_key,
    source_name,
    path,
    findings,
):

    if isinstance(obj, dict):

        for key, value in obj.items():

            child_path = make_path(
                path,
                key,
            )

            # キー名候補
            if contains_keyword(key):

                findings.append({
                    "race_key": race_key,
                    "source": source_name,
                    "type": "KEYWORD_KEY",
                    "path": child_path,
                    "key": key,
                    "value_preview":
                        str(value)[:500],
                })

            # 文字列キーワード候補
            if (
                isinstance(value, str)
                and contains_keyword(value)
            ):

                findings.append({
                    "race_key": race_key,
                    "source": source_name,
                    "type": "KEYWORD_VALUE",
                    "path": child_path,
                    "key": key,
                    "value_preview":
                        value[:500],
                })

            # 文字列並び候補
            formation = (
                analyze_string_formation(
                    value
                )
            )

            if formation:

                findings.append({
                    "race_key": race_key,
                    "source": source_name,
                    "type":
                        "FORMATION_STRING",
                    "path": child_path,
                    "key": key,
                    "value_preview":
                        formation["text"][:500],
                    "digits":
                        formation["digits"],
                })

            search_object(
                value,
                race_key,
                source_name,
                child_path,
                findings,
            )

    elif isinstance(obj, list):

        number_list = analyze_number_list(
            obj
        )

        if number_list:

            findings.append({
                "race_key": race_key,
                "source": source_name,
                "type": "NUMBER_LIST",
                "path": path,
                "value_preview":
                    str(number_list),
                "numbers": number_list,
            })

        for index, item in enumerate(obj):

            child_path = (
                f"{path}[{index}]"
            )

            search_object(
                item,
                race_key,
                source_name,
                child_path,
                findings,
            )


# ===========================================================
# source抽出
# ===========================================================

def extract_sources(race_data):

    sources = {}

    source_candidates = {
        "jsj001_race": [
            "jsj001_race",
            "jsj001",
            "JSJ001",
        ],
        "jsj006": [
            "jsj006",
            "JSJ006",
        ],
        "jsj012": [
            "jsj012",
            "JSJ012",
        ],
    }

    for source_name, keys in (
        source_candidates.items()
    ):

        for key in keys:

            if key in race_data:

                sources[source_name] = (
                    race_data[key]
                )

                break

    return sources


# ===========================================================
# main
# ===========================================================

def main():

    print(
        "=== 013 保存済みRAW "
        "ライン・並び情報候補探索 ==="
    )

    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    classification = load_json(
        CLASSIFICATION_FILE
    )

    normal_race_keys = (
        extract_normal_race_keys(
            classification
        )
    )

    print()
    print(
        "NORMAL race_key数:",
        len(normal_race_keys),
    )

    raw_files = find_raw_json_files()

    print(
        "探索RAW JSON数:",
        len(raw_files),
    )

    print()
    print(
        "=== race_key索引生成 ==="
    )

    race_index = build_race_index(
        raw_files,
        normal_race_keys,
    )

    print()
    print(
        "RAW発見race_key数:",
        len(race_index),
    )

    missing_race_keys = sorted(
        set(normal_race_keys)
        - set(race_index.keys())
    )

    print(
        "RAW未発見race_key数:",
        len(missing_race_keys),
    )

    # =======================================================
    # 全レース探索
    # =======================================================

    print()
    print(
        "=== ライン候補探索開始 ==="
    )

    all_findings = []

    race_with_findings = set()

    source_distribution = Counter()
    type_distribution = Counter()
    path_distribution = Counter()
    source_path_distribution = Counter()

    path_samples = defaultdict(list)

    for index, race_key in enumerate(
        normal_race_keys,
        start=1,
    ):

        race_entry = race_index.get(
            race_key
        )

        if not race_entry:

            continue

        race_data = race_entry["data"]

        sources = extract_sources(
            race_data
        )

        race_findings = []

        for (
            source_name,
            source_data
        ) in sources.items():

            source_findings = []

            search_object(
                source_data,
                race_key,
                source_name,
                "",
                source_findings,
            )

            for finding in source_findings:

                race_findings.append(
                    finding
                )

                source_distribution[
                    source_name
                ] += 1

                type_distribution[
                    finding["type"]
                ] += 1

                path_distribution[
                    finding["path"]
                ] += 1

                source_path_key = (
                    source_name
                    + " | "
                    + finding["path"]
                )

                source_path_distribution[
                    source_path_key
                ] += 1

                samples = path_samples[
                    source_path_key
                ]

                if (
                    len(samples)
                    < MAX_SAMPLES_PER_PATH
                ):

                    samples.append({
                        "race_key":
                            race_key,
                        "type":
                            finding["type"],
                        "value_preview":
                            finding.get(
                                "value_preview"
                            ),
                    })

        if race_findings:

            race_with_findings.add(
                race_key
            )

            all_findings.extend(
                race_findings
            )

        if (
            index % 500 == 0
            or index
            == len(normal_race_keys)
        ):

            print(
                "探索:",
                index,
                "/",
                len(normal_race_keys),
                "| 候補race:",
                len(
                    race_with_findings
                ),
                "| 候補件数:",
                len(all_findings),
            )

    # =======================================================
    # PATH集計
    # =======================================================

    path_summary = []

    for (
        source_path,
        count
    ) in source_path_distribution.most_common():

        source_name, path = (
            source_path.split(
                " | ",
                1,
            )
        )

        path_summary.append({
            "source": source_name,
            "path": path,
            "count": count,
            "samples":
                path_samples[
                    source_path
                ],
        })

    # =======================================================
    # 保存
    # =======================================================

    result = {
        "normal_race_key_count":
            len(normal_race_keys),
        "raw_found_race_key_count":
            len(race_index),
        "raw_missing_race_key_count":
            len(missing_race_keys),
        "raw_missing_race_keys":
            missing_race_keys,
        "race_with_findings_count":
            len(race_with_findings),
        "finding_count":
            len(all_findings),
        "source_distribution":
            dict(source_distribution),
        "type_distribution":
            dict(type_distribution),
        "top_paths":
            path_summary[:200],
        "findings":
            all_findings,
    }

    save_json(
        RESULT_FILE,
        result,
    )

    # =======================================================
    # 表示
    # =======================================================

    print()
    print("=" * 100)
    print("=== 013 結果 ===")
    print(
        "NORMAL race_key数:",
        len(normal_race_keys),
    )
    print(
        "RAW発見race_key数:",
        len(race_index),
    )
    print(
        "RAW未発見race_key数:",
        len(missing_race_keys),
    )
    print(
        "候補ありrace_key数:",
        len(race_with_findings),
    )
    print(
        "候補総件数:",
        len(all_findings),
    )
    print(
        "SOURCE分布:",
        dict(source_distribution),
    )
    print(
        "TYPE分布:",
        dict(type_distribution),
    )

    print()
    print(
        "=== 候補PATH TOP100 ==="
    )

    for rank, item in enumerate(
        path_summary[:100],
        start=1,
    ):

        print()
        print(
            f"[{rank}]",
            item["source"],
            item["path"],
        )

        print(
            "件数:",
            item["count"],
        )

        for sample in item[
            "samples"
        ][:3]:

            print(
                " ",
                sample,
            )

    print()
    print(
        "結果保存:"
    )
    print(RESULT_FILE)

    print()
    print("=== 013 完了 ===")


if __name__ == "__main__":

    main()