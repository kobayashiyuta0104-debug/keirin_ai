import json
import glob
import os
import re


# --------------------------------------------------
# 候補判定
# --------------------------------------------------

def classify_candidate(key, value):

    key_text = str(key).lower()
    value_text = str(value).strip()

    categories = []

    # ----------------------------------------------
    # raceUrlPrm
    # ----------------------------------------------

    if "raceurlprm" in key_text:

        categories.append(
            "RACE_URL_PRM"
        )

    # ----------------------------------------------
    # 日付KEY候補
    # ----------------------------------------------

    date_key_words = [
        "date",
        "ymd",
        "day",
        "kaisai",
        "targetdate",
        "racedate"
    ]

    for word in date_key_words:

        if word in key_text:

            categories.append(
                "DATE_KEY"
            )

            break

    # ----------------------------------------------
    # 値そのものが日付っぽい
    # ----------------------------------------------

    date_patterns = [
        r"20\d{2}/\d{1,2}/\d{1,2}",
        r"20\d{2}-\d{1,2}-\d{1,2}",
        r"20\d{6}",
        r"\d{4}/\d{1,2}/\d{1,2}"
    ]

    for pattern in date_patterns:

        if re.search(
            pattern,
            value_text
        ):

            categories.append(
                "DATE_VALUE"
            )

            break

    # ----------------------------------------------
    # 競輪場KEY候補
    # ----------------------------------------------

    venue_key_words = [
        "venue",
        "keirinjo",
        "keirin",
        "jocode",
        "jyo",
        "place"
    ]

    for word in venue_key_words:

        if word in key_text:

            categories.append(
                "VENUE_KEY"
            )

            break

    # ----------------------------------------------
    # 競輪場名VALUE候補
    # ----------------------------------------------

    venue_names = [
        "函館",
        "青森",
        "いわき平",
        "弥彦",
        "前橋",
        "取手",
        "宇都宮",
        "大宮",
        "西武園",
        "京王閣",
        "立川",
        "松戸",
        "千葉",
        "川崎",
        "平塚",
        "小田原",
        "伊東",
        "静岡",
        "名古屋",
        "岐阜",
        "大垣",
        "豊橋",
        "富山",
        "松阪",
        "四日市",
        "福井",
        "奈良",
        "向日町",
        "和歌山",
        "岸和田",
        "玉野",
        "広島",
        "防府",
        "高松",
        "小松島",
        "高知",
        "松山",
        "小倉",
        "久留米",
        "武雄",
        "佐世保",
        "別府",
        "熊本"
    ]

    for venue_name in venue_names:

        if venue_name in value_text:

            categories.append(
                "VENUE_VALUE"
            )

            break

    # ----------------------------------------------
    # レース番号KEY候補
    # ----------------------------------------------

    race_key_words = [
        "raceno",
        "race_no",
        "racenum",
        "racenumber",
        "rno"
    ]

    for word in race_key_words:

        if word in key_text:

            categories.append(
                "RACE_NO_KEY"
            )

            break

    # ----------------------------------------------
    # レース番号VALUE候補
    # ----------------------------------------------

    if re.fullmatch(
        r"(?:[1-9]|1[0-2])R",
        value_text,
        re.IGNORECASE
    ):

        categories.append(
            "RACE_NO_VALUE"
        )

    # 重複除去
    return list(
        dict.fromkeys(categories)
    )


# --------------------------------------------------
# JSON再帰調査
# --------------------------------------------------

def search_data(
    data,
    path="ROOT",
    findings=None,
    depth=0
):

    if findings is None:

        findings = []

    if depth > 20:

        return findings

    if isinstance(data, dict):

        for key, value in data.items():

            current_path = (
                f"{path}.{key}"
            )

            # --------------------------------------
            # 単純VALUEだけ候補判定
            # --------------------------------------

            if isinstance(
                value,
                (
                    str,
                    int,
                    float,
                    bool
                )
            ):

                categories = (
                    classify_candidate(
                        key,
                        value
                    )
                )

                if categories:

                    findings.append(
                        {
                            "path": current_path,
                            "key": str(key),
                            "value": str(value),
                            "categories": (
                                categories
                            )
                        }
                    )

            # --------------------------------------
            # 再帰
            # --------------------------------------

            search_data(
                value,
                current_path,
                findings,
                depth + 1
            )

    elif isinstance(data, list):

        # 今回は構造調査なので
        # 最初の10件まで見る

        for index, value in enumerate(
            data[:10]
        ):

            current_path = (
                f"{path}[{index}]"
            )

            search_data(
                value,
                current_path,
                findings,
                depth + 1
            )

    return findings


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print(
        "=== 128 開催日 × 競輪場 × "
        "レース番号 結合キー詳細調査 ==="
    )

    # --------------------------------------------------
    # JSON検索
    # --------------------------------------------------

    json_files = []

    json_files.extend(
        glob.glob("*.json")
    )

    json_files.extend(
        glob.glob(
            "result/*.json"
        )
    )

    json_files = sorted(
        set(json_files)
    )

    exclude_words = [
        "122_all_venues_jsj012",
        "123_jsj012_structure",
        "125_extracted_results",
        "127_join_key_candidates",
        "128_join_key_detail"
    ]

    target_files = []

    for file_path in json_files:

        file_name = os.path.basename(
            file_path
        )

        excluded = False

        for word in exclude_words:

            if word in file_name:

                excluded = True
                break

        if excluded:

            continue

        target_files.append(
            file_path
        )

    print()
    print(
        "🔥 調査JSON数:",
        len(target_files)
    )

    # --------------------------------------------------
    # 全ファイル調査
    # --------------------------------------------------

    all_results = {}

    category_counts = {
        "DATE_KEY": 0,
        "DATE_VALUE": 0,
        "VENUE_KEY": 0,
        "VENUE_VALUE": 0,
        "RACE_NO_KEY": 0,
        "RACE_NO_VALUE": 0,
        "RACE_URL_PRM": 0
    }

    for file_path in target_files:

        print()
        print("=" * 80)
        print(
            "🔥 調査:",
            file_path
        )
        print("=" * 80)

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

        except Exception as e:

            print(
                "❌ 読み込み失敗:",
                e
            )

            continue

        findings = search_data(
            data
        )

        # ------------------------------------------
        # 完全重複除去
        # ------------------------------------------

        unique_findings = []

        seen = set()

        for item in findings:

            signature = (
                item["path"],
                item["value"],
                tuple(
                    item["categories"]
                )
            )

            if signature in seen:

                continue

            seen.add(signature)

            unique_findings.append(
                item
            )

        all_results[
            file_path
        ] = unique_findings

        print(
            "候補数:",
            len(unique_findings)
        )

        # ------------------------------------------
        # 表示
        # ------------------------------------------

        for item in unique_findings:

            print()
            print(
                "🔥 CATEGORY:",
                ", ".join(
                    item["categories"]
                )
            )

            print(
                "PATH:",
                item["path"]
            )

            print(
                "KEY:",
                item["key"]
            )

            print(
                "VALUE:",
                repr(
                    item["value"]
                )
            )

            for category in (
                item["categories"]
            ):

                if category in category_counts:

                    category_counts[
                        category
                    ] += 1

    # --------------------------------------------------
    # JSON保存
    # --------------------------------------------------

    save_file = (
        "128_join_key_detail.json"
    )

    with open(
        save_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            all_results,
            f,
            ensure_ascii=False,
            indent=2
        )

    # --------------------------------------------------
    # 最終結果
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("🔥 128テスト終了")
    print("=" * 80)

    print(
        "調査JSON数:",
        len(target_files)
    )

    print()

    print(
        "DATE_KEY:",
        category_counts[
            "DATE_KEY"
        ]
    )

    print(
        "DATE_VALUE:",
        category_counts[
            "DATE_VALUE"
        ]
    )

    print(
        "VENUE_KEY:",
        category_counts[
            "VENUE_KEY"
        ]
    )

    print(
        "VENUE_VALUE:",
        category_counts[
            "VENUE_VALUE"
        ]
    )

    print(
        "RACE_NO_KEY:",
        category_counts[
            "RACE_NO_KEY"
        ]
    )

    print(
        "RACE_NO_VALUE:",
        category_counts[
            "RACE_NO_VALUE"
        ]
    )

    print(
        "RACE_URL_PRM:",
        category_counts[
            "RACE_URL_PRM"
        ]
    )

    print()
    print(
        "保存先:",
        save_file
    )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()