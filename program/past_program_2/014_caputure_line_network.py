"""
===========================================================
競輪AI 正式版
014_capture_line_network.py

目的:
・KEIRIN.JP レース前ページの通信を監視
・ライン / 並び情報を持つ通信候補を探索
・JSONレスポンスを保存
・JSJ系 type 分布を集計
・ライン候補キー / 値 / 車番構造を再帰探索

重要:
・既存Datasetは変更しない
・Edge CDP接続方式
・ライン取得元特定専用
===========================================================
"""

import json
import re
import time
from pathlib import Path
from collections import Counter, defaultdict

from playwright.sync_api import sync_playwright


# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "014_network_capture"
)

RESULT_FILE = (
    OUT_DIR
    / "014_line_network_analysis.json"
)

RAW_RESPONSE_DIR = (
    OUT_DIR
    / "responses"
)


# ===========================================================
# Edge CDP
# ===========================================================

CDP_URL = "http://127.0.0.1:9222"


# ===========================================================
# 調査対象
#
# 既存RAWで確認済みの正常レースを使用
# ===========================================================

TARGET_RACES = [
    {
        "race_key": "20260705_小松島_4R",
        "kday": "20260705",
        "venue_code": "73",
        "race_no": 4,
    },
    {
        "race_key": "20260705_小松島_10R",
        "kday": "20260705",
        "venue_code": "73",
        "race_no": 10,
    },
    {
        "race_key": "20260706_小松島_4R",
        "kday": "20260706",
        "venue_code": "73",
        "race_no": 4,
    },
]


# ===========================================================
# 探索キーワード
# ===========================================================

KEYWORDS = [
    "line",
    "Line",
    "LINE",
    "narabi",
    "Narabi",
    "NARABI",
    "nami",
    "Nami",
    "NAMI",
    "並び",
    "ならび",
    "ライン",
    "yoso",
    "Yoso",
    "YOSO",
    "forecast",
    "formation",
    "group",
    "team",
    "renkei",
    "Renkei",
    "RENKEI",
    "連携",
    "番手",
    "単騎",
    "先頭",
    "並",
]


# ===========================================================
# JSON
# ===========================================================

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
# 安全ファイル名
# ===========================================================

def safe_filename(text):

    text = re.sub(
        r"[^0-9A-Za-zぁ-んァ-ヶ一-龠_-]+",
        "_",
        str(text),
    )

    return text[:180]


# ===========================================================
# URL type
# ===========================================================

def extract_type_from_url(url):

    match = re.search(
        r"(?:\?|&)type=([^&]+)",
        url,
        re.IGNORECASE,
    )

    if match:

        return match.group(1)

    return None


# ===========================================================
# キーワード
# ===========================================================

def contains_keyword(text):

    text = str(text)

    for keyword in KEYWORDS:

        if keyword in text:

            return True

    return False


# ===========================================================
# 車番
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
# 車番LIST
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
# 並び文字列
# ===========================================================

def analyze_formation_string(value):

    if not isinstance(value, str):

        return None

    text = value.strip()

    if not text:

        return None

    digits = re.findall(
        r"[1-9]",
        text,
    )

    if len(set(digits)) < 2:

        return None

    symbols = [
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
        "|",
        "｜",
    ]

    if not any(
        symbol in text
        for symbol in symbols
    ):

        return None

    return {
        "text": text,
        "digits": digits,
    }


# ===========================================================
# PATH
# ===========================================================

def make_path(parent, key):

    if not parent:

        return f"$.{key}"

    return f"{parent}.{key}"


# ===========================================================
# 再帰探索
# ===========================================================

def search_json(
    obj,
    path,
    findings,
):

    if isinstance(obj, dict):

        for key, value in obj.items():

            child_path = make_path(
                path,
                key,
            )

            # -----------------------------------------------
            # キー名
            # -----------------------------------------------

            if contains_keyword(key):

                findings.append({
                    "type": "KEYWORD_KEY",
                    "path": child_path,
                    "key": key,
                    "value_preview":
                        str(value)[:1000],
                })

            # -----------------------------------------------
            # 値
            # -----------------------------------------------

            if (
                isinstance(value, str)
                and contains_keyword(value)
            ):

                findings.append({
                    "type": "KEYWORD_VALUE",
                    "path": child_path,
                    "key": key,
                    "value_preview":
                        value[:1000],
                })

            # -----------------------------------------------
            # 並び文字列
            # -----------------------------------------------

            formation = (
                analyze_formation_string(
                    value
                )
            )

            if formation:

                findings.append({
                    "type":
                        "FORMATION_STRING",
                    "path": child_path,
                    "key": key,
                    "value_preview":
                        formation["text"][:1000],
                    "digits":
                        formation["digits"],
                })

            search_json(
                value,
                child_path,
                findings,
            )

    elif isinstance(obj, list):

        number_list = analyze_number_list(
            obj
        )

        if number_list:

            findings.append({
                "type": "NUMBER_LIST",
                "path": path,
                "numbers": number_list,
                "value_preview":
                    str(number_list),
            })

        for index, item in enumerate(obj):

            child_path = (
                f"{path}[{index}]"
            )

            search_json(
                item,
                child_path,
                findings,
            )


# ===========================================================
# ページURL候補
# ===========================================================

def build_page_urls(target):

    kday = target["kday"]
    venue_code = target["venue_code"]
    race_no = target["race_no"]

    return [
        (
            "https://www.keirin.jp/pc/race/"
            f"racecard?KCD={venue_code}"
            f"&KBI={kday}"
            f"&RNO={race_no}"
        ),
        (
            "https://www.keirin.jp/pc/race/"
            f"raceresult?KCD={venue_code}"
            f"&KBI={kday}"
            f"&RNO={race_no}"
        ),
    ]


# ===========================================================
# main
# ===========================================================

def main():

    print(
        "=== 014 KEIRIN.JP "
        "ライン・並び通信探索 ==="
    )

    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    RAW_RESPONSE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_records = []

    type_distribution = Counter()
    content_type_distribution = Counter()
    finding_type_distribution = Counter()
    finding_path_distribution = Counter()
    url_distribution = Counter()

    response_errors = []

    with sync_playwright() as p:

        print()
        print(
            "Edge CDP接続:",
            CDP_URL,
        )

        browser = (
            p.chromium.connect_over_cdp(
                CDP_URL
            )
        )

        contexts = browser.contexts

        if not contexts:

            raise RuntimeError(
                "Edge contextがありません"
            )

        context = contexts[0]

        pages = context.pages

        if pages:

            page = pages[0]

        else:

            page = context.new_page()

        print(
            "接続成功"
        )

        # ===================================================
        # レース単位
        # ===================================================

        for target_index, target in enumerate(
            TARGET_RACES,
            start=1,
        ):

            race_key = target["race_key"]

            print()
            print("=" * 100)
            print(
                f"[対象 {target_index}/"
                f"{len(TARGET_RACES)}]"
            )
            print(
                "race_key:",
                race_key,
            )

            page_urls = build_page_urls(
                target
            )

            for page_index, page_url in enumerate(
                page_urls,
                start=1,
            ):

                print()
                print(
                    f"  [PAGE {page_index}/"
                    f"{len(page_urls)}]"
                )
                print(
                    "  URL:",
                    page_url,
                )

                captured_responses = []

                # ===========================================
                # response handler
                # ===========================================

                def on_response(response):

                    url = response.url

                    content_type = (
                        response.headers.get(
                            "content-type",
                            ""
                        )
                    )

                    jsj_type = extract_type_from_url(
                        url
                    )

                    is_candidate = (
                        "json" in content_type.lower()
                        or "/json" in url.lower()
                        or "type=JSJ" in url
                        or "api" in url.lower()
                    )

                    if not is_candidate:

                        return

                    captured_responses.append({
                        "response": response,
                        "url": url,
                        "content_type":
                            content_type,
                        "jsj_type":
                            jsj_type,
                    })

                page.on(
                    "response",
                    on_response,
                )

                try:

                    page.goto(
                        page_url,
                        wait_until="domcontentloaded",
                        timeout=60000,
                    )

                    print(
                        "  ページ読込完了"
                    )

                    # 動的通信待機
                    time.sleep(8)

                    # 少しスクロール
                    try:

                        page.evaluate(
                            """
                            window.scrollTo(
                                0,
                                document.body.scrollHeight
                            )
                            """
                        )

                    except Exception:

                        pass

                    time.sleep(3)

                except Exception as e:

                    print(
                        "  ❌ PAGE ERROR:",
                        repr(e),
                    )

                    response_errors.append({
                        "race_key": race_key,
                        "page_url": page_url,
                        "problem": "PAGE_ERROR",
                        "error": repr(e),
                    })

                finally:

                    page.remove_listener(
                        "response",
                        on_response,
                    )

                print(
                    "  通信候補数:",
                    len(captured_responses),
                )

                # ===========================================
                # response解析
                # ===========================================

                seen_urls = set()

                for response_index, item in enumerate(
                    captured_responses,
                    start=1,
                ):

                    response = item["response"]
                    url = item["url"]
                    content_type = item[
                        "content_type"
                    ]
                    jsj_type = item["jsj_type"]

                    if url in seen_urls:

                        continue

                    seen_urls.add(url)

                    url_distribution[url] += 1

                    if jsj_type:

                        type_distribution[
                            jsj_type
                        ] += 1

                    if content_type:

                        content_type_distribution[
                            content_type
                        ] += 1

                    record = {
                        "race_key": race_key,
                        "page_url": page_url,
                        "response_url": url,
                        "status": response.status,
                        "content_type":
                            content_type,
                        "jsj_type": jsj_type,
                        "json_success": False,
                        "finding_count": 0,
                        "findings": [],
                        "saved_file": None,
                    }

                    try:

                        data = response.json()

                        record[
                            "json_success"
                        ] = True

                    except Exception as e:

                        record[
                            "json_error"
                        ] = repr(e)

                        all_records.append(
                            record
                        )

                        continue

                    findings = []

                    search_json(
                        data,
                        "",
                        findings,
                    )

                    record[
                        "finding_count"
                    ] = len(findings)

                    record[
                        "findings"
                    ] = findings

                    for finding in findings:

                        finding_type_distribution[
                            finding["type"]
                        ] += 1

                        path_key = (
                            str(jsj_type)
                            + " | "
                            + finding["path"]
                        )

                        finding_path_distribution[
                            path_key
                        ] += 1

                    # =======================================
                    # JSON保存
                    # =======================================

                    type_name = (
                        jsj_type
                        or
                        f"response_{response_index}"
                    )

                    file_name = (
                        safe_filename(race_key)
                        + "__"
                        + safe_filename(type_name)
                        + "__"
                        + str(page_index)
                        + ".json"
                    )

                    save_path = (
                        RAW_RESPONSE_DIR
                        / file_name
                    )

                    save_json(
                        save_path,
                        data,
                    )

                    record[
                        "saved_file"
                    ] = str(save_path)

                    all_records.append(
                        record
                    )

                    if findings:

                        print()
                        print(
                            "    🔎 候補通信"
                        )
                        print(
                            "    type:",
                            jsj_type,
                        )
                        print(
                            "    URL:",
                            url,
                        )
                        print(
                            "    候補数:",
                            len(findings),
                        )

                        for finding in findings[:10]:

                            print(
                                "      ",
                                finding,
                            )

    # =======================================================
    # 集計
    # =======================================================

    candidate_records = [
        record
        for record in all_records
        if record["finding_count"] > 0
    ]

    top_paths = [
        {
            "path_key": path_key,
            "count": count,
        }
        for (
            path_key,
            count
        ) in finding_path_distribution.most_common(
            200
        )
    ]

    result = {
        "target_race_count":
            len(TARGET_RACES),
        "response_record_count":
            len(all_records),
        "json_success_count":
            sum(
                1
                for record in all_records
                if record["json_success"]
            ),
        "candidate_response_count":
            len(candidate_records),
        "type_distribution":
            dict(type_distribution),
        "content_type_distribution":
            dict(
                content_type_distribution
            ),
        "finding_type_distribution":
            dict(
                finding_type_distribution
            ),
        "top_finding_paths":
            top_paths,
        "response_error_count":
            len(response_errors),
        "response_errors":
            response_errors,
        "candidate_records":
            candidate_records,
        "all_records":
            all_records,
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
    print("=== 014 結果 ===")

    print(
        "対象レース数:",
        len(TARGET_RACES),
    )

    print(
        "通信レコード数:",
        len(all_records),
    )

    print(
        "JSON解析成功:",
        result[
            "json_success_count"
        ],
    )

    print(
        "候補通信数:",
        len(candidate_records),
    )

    print(
        "JSJ TYPE分布:",
        dict(type_distribution),
    )

    print(
        "候補TYPE分布:",
        dict(
            finding_type_distribution
        ),
    )

    print(
        "通信エラー数:",
        len(response_errors),
    )

    print()
    print(
        "=== 候補PATH TOP100 ==="
    )

    for rank, item in enumerate(
        top_paths[:100],
        start=1,
    ):

        print(
            f"{rank:03d}",
            item["count"],
            item["path_key"],
        )

    print()
    print(
        "=== 候補通信一覧 ==="
    )

    for index, record in enumerate(
        candidate_records,
        start=1,
    ):

        print()
        print(
            f"[{index}]"
        )

        print(
            "race_key:",
            record["race_key"],
        )

        print(
            "JSJ type:",
            record["jsj_type"],
        )

        print(
            "response URL:",
            record["response_url"],
        )

        print(
            "候補数:",
            record["finding_count"],
        )

        for finding in record[
            "findings"
        ][:20]:

            print(
                " ",
                finding,
            )

    print()
    print(
        "結果保存:"
    )
    print(
        RESULT_FILE
    )

    print()
    print(
        "RAW response保存:"
    )
    print(
        RAW_RESPONSE_DIR
    )

    print()
    print("=== 014 完了 ===")


if __name__ == "__main__":

    main()