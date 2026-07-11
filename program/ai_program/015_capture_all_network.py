"""
===========================================================
競輪AI 正式版
015_capture_all_network.py

目的:
・014で通信レコード0だった原因を特定
・KEIRIN.JPページの全通信URLを捕獲
・最終到達URL / TITLE / HTMLを保存
・HTML内JSJ番号を探索
・encParaR / encPrm候補を探索
・ライン / 並び候補文字列を探索
・JSON限定フィルターを使わない

重要:
・Datasetは変更しない
・Edge CDP接続方式
・通信探索専用
===========================================================
"""

import json
import re
import time
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


# ===========================================================
# 基本設定
# ===========================================================

BASE = Path(r"C:\競輪AI")

OUT_DIR = (
    BASE
    / "data_official"
    / "line_research"
    / "015_all_network_capture"
)

RESULT_FILE = (
    OUT_DIR
    / "015_all_network_analysis.json"
)

HTML_DIR = (
    OUT_DIR
    / "html"
)

BODY_DIR = (
    OUT_DIR
    / "response_bodies"
)


# ===========================================================
# Edge CDP
# ===========================================================

CDP_URL = "http://127.0.0.1:9222"


# ===========================================================
# 対象レース
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
    "並び",
    "ならび",
    "ライン",
    "yoso",
    "Yoso",
    "YOSO",
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
    "細切れ",
    "二分戦",
    "三分戦",
    "四分戦",
    "encParaR",
    "encPrm",
    "JSJ",
]


# ===========================================================
# JSON保存
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
# TEXT保存
# ===========================================================

def save_text(path, text):

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
        errors="replace",
    ) as f:

        f.write(text)


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
# JSJ TYPE抽出
# ===========================================================

def extract_jsj_types(text):

    if not text:

        return []

    values = re.findall(
        r"JSJ\d+",
        str(text),
        flags=re.IGNORECASE,
    )

    return sorted(
        set(
            value.upper()
            for value in values
        )
    )


# ===========================================================
# enc候補抽出
# ===========================================================

def extract_enc_candidates(text):

    if not text:

        return []

    patterns = [
        r'encParaR["\']?\s*[:=]\s*["\']([^"\']+)',
        r'encPrm["\']?\s*[:=]\s*["\']([^"\']+)',
        r'encp=([^&"\'\s<>]+)',
        r'encParaR=([^&"\'\s<>]+)',
        r'encPrm=([^&"\'\s<>]+)',
    ]

    results = []

    for pattern in patterns:

        for match in re.findall(
            pattern,
            text,
            flags=re.IGNORECASE,
        ):

            results.append(match)

    return sorted(
        set(results)
    )


# ===========================================================
# キーワード周辺文字列
# ===========================================================

def search_keyword_contexts(text):

    if not text:

        return []

    findings = []

    for keyword in KEYWORDS:

        start = 0

        while True:

            index = text.find(
                keyword,
                start,
            )

            if index < 0:

                break

            left = max(
                0,
                index - 200,
            )

            right = min(
                len(text),
                index + len(keyword) + 500,
            )

            context = text[
                left:right
            ]

            findings.append({
                "keyword": keyword,
                "context": context,
            })

            start = (
                index
                + len(keyword)
            )

            if len(findings) >= 5000:

                return findings

    return findings


# ===========================================================
# 車番並び文字列候補
# ===========================================================

def search_formation_candidates(text):

    if not text:

        return []

    patterns = [
        r'(?<!\d)[1-9](?:\s*[-－=＝/／→>|｜]\s*[1-9]){1,8}(?!\d)',
        r'(?<!\d)[1-9](?:\s+[1-9]){1,8}(?!\d)',
        r'(?<!\d)[1-9](?:\s*・\s*[1-9]){1,8}(?!\d)',
    ]

    results = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
        )

        for value in matches:

            value = value.strip()

            digits = re.findall(
                r"[1-9]",
                value,
            )

            if len(set(digits)) < 2:

                continue

            results.append(value)

    return sorted(
        set(results)
    )[:5000]


# ===========================================================
# URL候補
# ===========================================================

def build_page_urls(target):

    kday = target["kday"]
    venue_code = target["venue_code"]
    race_no = target["race_no"]

    return [
        {
            "name": "racecard",
            "url": (
                "https://www.keirin.jp/pc/race/"
                f"racecard?KCD={venue_code}"
                f"&KBI={kday}"
                f"&RNO={race_no}"
            ),
        },
        {
            "name": "raceresult",
            "url": (
                "https://www.keirin.jp/pc/race/"
                f"raceresult?KCD={venue_code}"
                f"&KBI={kday}"
                f"&RNO={race_no}"
            ),
        },
        {
            "name": "top",
            "url": (
                "https://www.keirin.jp/pc/top"
            ),
        },
    ]


# ===========================================================
# main
# ===========================================================

def main():

    print(
        "=== 015 KEIRIN.JP "
        "全通信・到達ページ調査 ==="
    )

    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    HTML_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    BODY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_page_records = []
    all_response_records = []

    resource_type_distribution = Counter()
    domain_distribution = Counter()
    status_distribution = Counter()
    jsj_distribution = Counter()
    content_type_distribution = Counter()

    problems = []

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

        page = context.new_page()

        print(
            "Edge接続成功"
        )

        # ===================================================
        # レース
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

            for page_index, page_item in enumerate(
                page_urls,
                start=1,
            ):

                page_name = page_item["name"]
                requested_url = page_item["url"]

                print()
                print(
                    f"  [PAGE {page_index}/"
                    f"{len(page_urls)}]"
                )
                print(
                    "  page_name:",
                    page_name,
                )
                print(
                    "  requested URL:",
                    requested_url,
                )

                captured_requests = []
                captured_responses = []

                # ===========================================
                # REQUEST
                # ===========================================

                def on_request(request):

                    try:

                        captured_requests.append({
                            "url": request.url,
                            "method": request.method,
                            "resource_type":
                                request.resource_type,
                        })

                    except Exception:

                        pass

                # ===========================================
                # RESPONSE
                # ===========================================

                def on_response(response):

                    try:

                        request = response.request

                        captured_responses.append({
                            "response": response,
                            "url": response.url,
                            "status": response.status,
                            "resource_type":
                                request.resource_type,
                            "method": request.method,
                            "content_type":
                                response.headers.get(
                                    "content-type",
                                    "",
                                ),
                        })

                    except Exception:

                        pass

                page.on(
                    "request",
                    on_request,
                )

                page.on(
                    "response",
                    on_response,
                )

                goto_error = None

                try:

                    page.goto(
                        requested_url,
                        wait_until="domcontentloaded",
                        timeout=60000,
                    )

                    time.sleep(10)

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

                    goto_error = repr(e)

                    print(
                        "  ❌ PAGE ERROR:",
                        goto_error,
                    )

                    problems.append({
                        "race_key": race_key,
                        "page_name": page_name,
                        "requested_url":
                            requested_url,
                        "problem":
                            "PAGE_GOTO_ERROR",
                        "error":
                            goto_error,
                    })

                finally:

                    page.remove_listener(
                        "request",
                        on_request,
                    )

                    page.remove_listener(
                        "response",
                        on_response,
                    )

                # ===========================================
                # 到達ページ
                # ===========================================

                try:

                    final_url = page.url

                except Exception:

                    final_url = None

                try:

                    title = page.title()

                except Exception:

                    title = None

                try:

                    html = page.content()

                except Exception as e:

                    html = ""

                    problems.append({
                        "race_key": race_key,
                        "page_name": page_name,
                        "problem":
                            "PAGE_CONTENT_ERROR",
                        "error":
                            repr(e),
                    })

                html_jsj_types = (
                    extract_jsj_types(
                        html
                    )
                )

                html_enc_candidates = (
                    extract_enc_candidates(
                        html
                    )
                )

                html_keyword_findings = (
                    search_keyword_contexts(
                        html
                    )
                )

                html_formation_candidates = (
                    search_formation_candidates(
                        html
                    )
                )

                html_file = (
                    HTML_DIR
                    / (
                        safe_filename(race_key)
                        + "__"
                        + safe_filename(page_name)
                        + ".html"
                    )
                )

                save_text(
                    html_file,
                    html,
                )

                page_record = {
                    "race_key": race_key,
                    "page_name": page_name,
                    "requested_url":
                        requested_url,
                    "final_url":
                        final_url,
                    "title":
                        title,
                    "goto_error":
                        goto_error,
                    "request_count":
                        len(captured_requests),
                    "response_count":
                        len(captured_responses),
                    "html_length":
                        len(html),
                    "html_jsj_types":
                        html_jsj_types,
                    "html_enc_candidates":
                        html_enc_candidates,
                    "html_keyword_finding_count":
                        len(
                            html_keyword_findings
                        ),
                    "html_keyword_findings":
                        html_keyword_findings[
                            :500
                        ],
                    "html_formation_candidate_count":
                        len(
                            html_formation_candidates
                        ),
                    "html_formation_candidates":
                        html_formation_candidates[
                            :500
                        ],
                    "html_file":
                        str(html_file),
                    "requests":
                        captured_requests,
                }

                all_page_records.append(
                    page_record
                )

                print(
                    "  final URL:",
                    final_url,
                )

                print(
                    "  title:",
                    title,
                )

                print(
                    "  request数:",
                    len(captured_requests),
                )

                print(
                    "  response数:",
                    len(captured_responses),
                )

                print(
                    "  HTML長:",
                    len(html),
                )

                print(
                    "  HTML JSJ:",
                    html_jsj_types,
                )

                print(
                    "  HTML enc候補数:",
                    len(html_enc_candidates),
                )

                print(
                    "  HTML keyword候補数:",
                    len(html_keyword_findings),
                )

                print(
                    "  HTML 並び候補数:",
                    len(
                        html_formation_candidates
                    ),
                )

                if html_enc_candidates:

                    print(
                        "  enc候補:",
                        html_enc_candidates[:20],
                    )

                if html_formation_candidates:

                    print(
                        "  並び候補:",
                        html_formation_candidates[:30],
                    )

                # ===========================================
                # 全レスポンス解析
                # ===========================================

                seen_response_urls = set()

                for response_index, item in enumerate(
                    captured_responses,
                    start=1,
                ):

                    response = item["response"]
                    url = item["url"]

                    duplicate_url = (
                        url in seen_response_urls
                    )

                    seen_response_urls.add(
                        url
                    )

                    parsed = urlparse(
                        url
                    )

                    domain = parsed.netloc

                    resource_type = item[
                        "resource_type"
                    ]

                    content_type = item[
                        "content_type"
                    ]

                    status = item["status"]

                    resource_type_distribution[
                        resource_type
                    ] += 1

                    domain_distribution[
                        domain
                    ] += 1

                    status_distribution[
                        str(status)
                    ] += 1

                    if content_type:

                        content_type_distribution[
                            content_type
                        ] += 1

                    url_jsj_types = (
                        extract_jsj_types(
                            url
                        )
                    )

                    for jsj_type in url_jsj_types:

                        jsj_distribution[
                            jsj_type
                        ] += 1

                    response_record = {
                        "race_key":
                            race_key,
                        "page_name":
                            page_name,
                        "response_index":
                            response_index,
                        "url":
                            url,
                        "status":
                            status,
                        "method":
                            item["method"],
                        "resource_type":
                            resource_type,
                        "content_type":
                            content_type,
                        "domain":
                            domain,
                        "duplicate_url":
                            duplicate_url,
                        "url_jsj_types":
                            url_jsj_types,
                        "body_success":
                            False,
                        "body_length":
                            0,
                        "body_jsj_types":
                            [],
                        "body_enc_candidates":
                            [],
                        "body_keyword_finding_count":
                            0,
                        "body_keyword_findings":
                            [],
                        "body_formation_candidate_count":
                            0,
                        "body_formation_candidates":
                            [],
                        "saved_body_file":
                            None,
                    }

                    # ---------------------------------------
                    # BODY取得
                    # ---------------------------------------

                    try:

                        body = response.text()

                        response_record[
                            "body_success"
                        ] = True

                        response_record[
                            "body_length"
                        ] = len(body)

                    except Exception as e:

                        response_record[
                            "body_error"
                        ] = repr(e)

                        all_response_records.append(
                            response_record
                        )

                        continue

                    body_jsj_types = (
                        extract_jsj_types(
                            body
                        )
                    )

                    body_enc_candidates = (
                        extract_enc_candidates(
                            body
                        )
                    )

                    body_keyword_findings = (
                        search_keyword_contexts(
                            body
                        )
                    )

                    body_formation_candidates = (
                        search_formation_candidates(
                            body
                        )
                    )

                    response_record[
                        "body_jsj_types"
                    ] = body_jsj_types

                    response_record[
                        "body_enc_candidates"
                    ] = body_enc_candidates

                    response_record[
                        "body_keyword_finding_count"
                    ] = len(
                        body_keyword_findings
                    )

                    response_record[
                        "body_keyword_findings"
                    ] = body_keyword_findings[
                        :500
                    ]

                    response_record[
                        "body_formation_candidate_count"
                    ] = len(
                        body_formation_candidates
                    )

                    response_record[
                        "body_formation_candidates"
                    ] = body_formation_candidates[
                        :500
                    ]

                    for jsj_type in body_jsj_types:

                        jsj_distribution[
                            jsj_type
                        ] += 1

                    # ---------------------------------------
                    # 候補BODY保存
                    # ---------------------------------------

                    is_candidate = any([
                        url_jsj_types,
                        body_jsj_types,
                        body_enc_candidates,
                        body_keyword_findings,
                        body_formation_candidates,
                        "json" in content_type.lower(),
                        "/json" in url.lower(),
                        "api" in url.lower(),
                    ])

                    if is_candidate:

                        suffix = ".txt"

                        if "json" in content_type.lower():

                            suffix = ".json"

                        file_name = (
                            safe_filename(race_key)
                            + "__"
                            + safe_filename(page_name)
                            + "__"
                            + f"{response_index:04d}"
                            + "__"
                            + safe_filename(
                                resource_type
                            )
                            + suffix
                        )

                        body_file = (
                            BODY_DIR
                            / file_name
                        )

                        save_text(
                            body_file,
                            body,
                        )

                        response_record[
                            "saved_body_file"
                        ] = str(body_file)

                    all_response_records.append(
                        response_record
                    )

                print()
                print(
                    "  === 通信URL 先頭50 ==="
                )

                for request_index, request_item in enumerate(
                    captured_requests[:50],
                    start=1,
                ):

                    print(
                        f"    {request_index:03d}",
                        request_item[
                            "resource_type"
                        ],
                        request_item["url"],
                    )

    # =======================================================
    # 候補レスポンス
    # =======================================================

    candidate_responses = []

    for record in all_response_records:

        if any([
            record["url_jsj_types"],
            record["body_jsj_types"],
            record["body_enc_candidates"],
            record[
                "body_keyword_finding_count"
            ] > 0,
            record[
                "body_formation_candidate_count"
            ] > 0,
        ]):

            candidate_responses.append(
                record
            )

    # =======================================================
    # 結果
    # =======================================================

    result = {
        "target_race_count":
            len(TARGET_RACES),
        "page_record_count":
            len(all_page_records),
        "response_record_count":
            len(all_response_records),
        "candidate_response_count":
            len(candidate_responses),
        "resource_type_distribution":
            dict(
                resource_type_distribution
            ),
        "domain_distribution":
            dict(
                domain_distribution
            ),
        "status_distribution":
            dict(
                status_distribution
            ),
        "content_type_distribution":
            dict(
                content_type_distribution
            ),
        "jsj_distribution":
            dict(
                jsj_distribution
            ),
        "problem_count":
            len(problems),
        "problems":
            problems,
        "page_records":
            all_page_records,
        "candidate_responses":
            candidate_responses,
        "all_response_records":
            all_response_records,
    }

    save_json(
        RESULT_FILE,
        result,
    )

    # =======================================================
    # 最終表示
    # =======================================================

    print()
    print("=" * 100)
    print("=== 015 結果 ===")

    print(
        "対象レース数:",
        len(TARGET_RACES),
    )

    print(
        "調査ページ数:",
        len(all_page_records),
    )

    print(
        "全通信レスポンス数:",
        len(all_response_records),
    )

    print(
        "候補レスポンス数:",
        len(candidate_responses),
    )

    print(
        "RESOURCE TYPE分布:",
        dict(
            resource_type_distribution
        ),
    )

    print(
        "DOMAIN分布:",
        dict(
            domain_distribution
        ),
    )

    print(
        "STATUS分布:",
        dict(
            status_distribution
        ),
    )

    print(
        "JSJ分布:",
        dict(
            jsj_distribution
        ),
    )

    print(
        "問題件数:",
        len(problems),
    )

    print()
    print(
        "=== ページ到達結果 ==="
    )

    for record in all_page_records:

        print()
        print(
            "race_key:",
            record["race_key"],
        )

        print(
            "page_name:",
            record["page_name"],
        )

        print(
            "requested:",
            record["requested_url"],
        )

        print(
            "final:",
            record["final_url"],
        )

        print(
            "title:",
            record["title"],
        )

        print(
            "request_count:",
            record["request_count"],
        )

        print(
            "response_count:",
            record["response_count"],
        )

        print(
            "HTML JSJ:",
            record["html_jsj_types"],
        )

        print(
            "HTML enc候補:",
            record["html_enc_candidates"][:20],
        )

        print(
            "HTML 並び候補:",
            record[
                "html_formation_candidates"
            ][:30],
        )

    print()
    print(
        "=== 候補レスポンス 先頭100 ==="
    )

    for index, record in enumerate(
        candidate_responses[:100],
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
            "page_name:",
            record["page_name"],
        )

        print(
            "resource_type:",
            record["resource_type"],
        )

        print(
            "URL:",
            record["url"],
        )

        print(
            "URL JSJ:",
            record["url_jsj_types"],
        )

        print(
            "BODY JSJ:",
            record["body_jsj_types"],
        )

        print(
            "enc候補:",
            record[
                "body_enc_candidates"
            ][:20],
        )

        print(
            "keyword候補数:",
            record[
                "body_keyword_finding_count"
            ],
        )

        print(
            "並び候補:",
            record[
                "body_formation_candidates"
            ][:30],
        )

        if record["body_keyword_findings"]:

            print(
                "keyword context:"
            )

            for finding in record[
                "body_keyword_findings"
            ][:10]:

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
        "HTML保存:"
    )

    print(
        HTML_DIR
    )

    print()
    print(
        "候補BODY保存:"
    )

    print(
        BODY_DIR
    )

    print()
    print("=== 015 完了 ===")


if __name__ == "__main__":

    main()