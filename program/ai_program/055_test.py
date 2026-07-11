from pathlib import Path
from datetime import datetime
from collections import Counter
from playwright.sync_api import sync_playwright
import json
import re
import time


# ============================================================
# 055
#
# OFFICIAL CONFIRMED RESULT CAPTURE
#
# 目的:
#
# 043のrace_keyを対象に
# KEIRIN.JPをEdgeで巡回
#
# 当該レースの本物の確定結果JSONを取得する
#
# JSJ006の過去成績は使用しない
#
# 捕捉候補:
#
# rcvRefund
# tyakujyunItemSubData
# C0201race
# kimarite
#
# ============================================================


BASE = Path(r"C:\競輪AI")


SOURCE_FILE = (
    BASE
    / "data_official"
    / "line_predictions"
    / "043_all_venues_official_lines.json"
)


OUT_DIR = (
    BASE
    / "data_official"
    / "confirmed_results"
    / "055_official_confirmed_results"
)


OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_FILE = (
    OUT_DIR
    / "055_official_confirmed_results.json"
)


START_URL = (
    "https://www.keirin.jp/pc/raceschedule"
)


# ============================================================
# JSON
# ============================================================


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


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


# ============================================================
# RACE KEY
# ============================================================


RACE_KEY_PATTERN = re.compile(
    r"(?P<date>20\d{6})"
    r"_"
    r"(?P<venue>.+?)"
    r"_"
    r"(?P<race_no>\d{1,2})R"
)


def parse_race_key(value):

    if value is None:

        return None


    text = str(value).strip()


    match = RACE_KEY_PATTERN.fullmatch(
        text
    )


    if not match:

        return None


    return {
        "race_key": text,
        "date": match.group("date"),
        "venue": match.group("venue"),
        "race_no": int(
            match.group("race_no")
        ),
    }


# ============================================================
# RECURSIVE WALK
# ============================================================


def walk_json(
    value,
    path="root",
    depth=0,
):

    if depth > 50:

        return


    if isinstance(value, dict):

        for key, child in value.items():

            child_path = (
                f"{path}.{key}"
            )


            yield {
                "path": child_path,
                "key": str(key),
                "value": child,
            }


            yield from walk_json(
                child,
                child_path,
                depth + 1,
            )


    elif isinstance(value, list):

        for index, child in enumerate(value):

            child_path = (
                f"{path}[{index}]"
            )


            yield from walk_json(
                child,
                child_path,
                depth + 1,
            )


# ============================================================
# SOURCE RACE KEY
# ============================================================


def extract_race_keys(data):

    found = {}


    for item in walk_json(data):

        key = item.get("key")
        value = item.get("value")


        if key == "race_key":

            parsed = parse_race_key(value)


            if parsed:

                found[
                    parsed["race_key"]
                ] = parsed


        if isinstance(value, str):

            parsed = parse_race_key(value)


            if parsed:

                found[
                    parsed["race_key"]
                ] = parsed


    return sorted(
        found.values(),
        key=lambda x: (
            x["date"],
            x["venue"],
            x["race_no"],
        ),
    )


# ============================================================
# JSON RESULT EVIDENCE
# ============================================================


TRUE_RESULT_KEYS = {
    "rcvRefund",
    "tyakujyunItemSubData",
    "C0201race",
}


SUPPORT_RESULT_KEYS = {
    "kimarite",
    "rcvOdds",
}


FALSE_RESULT_KEYS = {
    "raceResult1Syaban",
    "raceResult2Syaban",
}


def inspect_result_json(data):

    true_hits = []
    support_hits = []
    false_hits = []


    for item in walk_json(data):

        key = item.get("key")


        if key in TRUE_RESULT_KEYS:

            true_hits.append({
                "path": item.get("path"),
                "key": key,
            })


        if key in SUPPORT_RESULT_KEYS:

            support_hits.append({
                "path": item.get("path"),
                "key": key,
            })


        if key in FALSE_RESULT_KEYS:

            false_hits.append({
                "path": item.get("path"),
                "key": key,
            })


    true_key_names = sorted({
        item["key"]
        for item in true_hits
    })


    support_key_names = sorted({
        item["key"]
        for item in support_hits
    })


    false_key_names = sorted({
        item["key"]
        for item in false_hits
    })


    # --------------------------------------------------------
    # 判定
    # --------------------------------------------------------


    if (
        "rcvRefund" in true_key_names
        and
        "tyakujyunItemSubData" in true_key_names
    ):

        judgement = (
            "STRONG_CONFIRMED_RESULT"
        )


    elif (
        "C0201race" in true_key_names
        and
        (
            "rcvRefund" in true_key_names
            or
            "tyakujyunItemSubData"
            in true_key_names
        )
    ):

        judgement = (
            "STRONG_CONFIRMED_RESULT"
        )


    elif true_key_names:

        judgement = (
            "RESULT_CANDIDATE"
        )


    elif (
        false_key_names
        and not true_key_names
    ):

        judgement = (
            "JSJ006_PAST_RESULT_IGNORE"
        )


    else:

        judgement = (
            "NOT_RESULT"
        )


    return {
        "judgement": judgement,
        "true_keys": true_key_names,
        "support_keys": support_key_names,
        "false_keys": false_key_names,
        "true_hit_count": len(true_hits),
        "support_hit_count": len(
            support_hits
        ),
        "false_hit_count": len(false_hits),
    }


# ============================================================
# RESPONSE BODY
# ============================================================


def response_to_json(response):

    try:

        content_type = (
            response.headers.get(
                "content-type",
                "",
            )
            .lower()
        )


        url = response.url.lower()


        if (
            "json" not in content_type
            and
            "/json?" not in url
        ):

            return None


        return response.json()


    except Exception:

        return None


# ============================================================
# CLICK HELPER
# ============================================================


def click_text_exact(
    page,
    text,
    timeout=5000,
):

    candidates = [
        page.get_by_text(
            text,
            exact=True,
        ),
        page.locator(
            "a",
            has_text=text,
        ),
        page.locator(
            "button",
            has_text=text,
        ),
    ]


    for locator in candidates:

        try:

            count = locator.count()


            for index in range(count):

                target = locator.nth(index)


                if not target.is_visible():

                    continue


                target.click(
                    timeout=timeout
                )


                return True


        except Exception:

            continue


    return False


# ============================================================
# VENUE CLICK
# ============================================================


def click_venue(
    page,
    venue,
):

    print(
        "  VENUE CLICK:",
        venue,
    )


    if click_text_exact(
        page,
        venue,
        timeout=7000,
    ):

        page.wait_for_timeout(
            1800
        )

        return True


    return False


# ============================================================
# RACE CLICK
# ============================================================


def race_text_candidates(race_no):

    return [
        f"{race_no}R",
        str(race_no),
    ]


def click_race(
    page,
    race_no,
):

    print(
        "  RACE CLICK:",
        f"{race_no}R",
    )


    # ========================================================
    # まず ○R 完全一致
    # ========================================================


    locator = page.get_by_text(
        f"{race_no}R",
        exact=True,
    )


    try:

        count = locator.count()


        for index in range(count):

            target = locator.nth(index)


            if not target.is_visible():

                continue


            target.click(
                timeout=7000
            )


            page.wait_for_timeout(
                1800
            )


            return True


    except Exception:

        pass


    # ========================================================
    # href / onclick 内 raceNo 候補
    # ========================================================


    selectors = [
        f'a[href*="raceNo={race_no}"]',
        f'a[href*="raceno={race_no}"]',
        f'[onclick*="raceNo={race_no}"]',
        f'[onclick*="raceno={race_no}"]',
    ]


    for selector in selectors:

        try:

            locator = page.locator(
                selector
            )


            count = locator.count()


            for index in range(count):

                target = locator.nth(index)


                if not target.is_visible():

                    continue


                target.click(
                    timeout=7000
                )


                page.wait_for_timeout(
                    1800
                )


                return True


        except Exception:

            continue


    return False


# ============================================================
# RESULT TAB CLICK
# ============================================================


def click_result_tab(page):

    texts = [
        "レース結果",
        "結果",
        "払戻金",
        "払戻",
    ]


    for text in texts:

        try:

            locator = page.get_by_text(
                text,
                exact=True,
            )


            count = locator.count()


            for index in range(count):

                target = locator.nth(index)


                if not target.is_visible():

                    continue


                target.click(
                    timeout=5000
                )


                page.wait_for_timeout(
                    1800
                )


                return {
                    "clicked": True,
                    "text": text,
                }


        except Exception:

            continue


    return {
        "clicked": False,
        "text": None,
    }


# ============================================================
# MAIN
# ============================================================


def main():

    print()

    print(
        "=" * 100
    )

    print(
        "055 OFFICIAL CONFIRMED RESULT CAPTURE"
    )

    print(
        "=" * 100
    )

    print()


    if not SOURCE_FILE.exists():

        print(
            "SOURCE FILE NOT FOUND:"
        )

        print(
            SOURCE_FILE
        )

        return


    source_data = load_json(
        SOURCE_FILE
    )


    races = extract_race_keys(
        source_data
    )


    print(
        "SOURCE FILE:",
        SOURCE_FILE
    )

    print(
        "TARGET RACES:",
        len(races)
    )

    print()


    results = []

    judgement_counter = Counter()

    current_venue = None


    with sync_playwright() as p:

        browser = p.chromium.launch(
            channel="msedge",
            headless=False,
        )


        context = browser.new_context()


        page = context.new_page()


        active_capture = {
            "race_key": None,
            "responses": [],
        }


        # ====================================================
        # RESPONSE
        # ====================================================


        def on_response(response):

            race_key = active_capture.get(
                "race_key"
            )


            if race_key is None:

                return


            data = response_to_json(
                response
            )


            if data is None:

                return


            inspection = inspect_result_json(
                data
            )


            judgement = inspection.get(
                "judgement"
            )


            if judgement == "NOT_RESULT":

                return


            active_capture[
                "responses"
            ].append({
                "url": response.url,
                "status": response.status,
                "inspection": inspection,
                "body": data,
            })


        page.on(
            "response",
            on_response,
        )


        # ====================================================
        # OPEN
        # ====================================================


        print(
            "OPEN:",
            START_URL
        )


        page.goto(
            START_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )


        page.wait_for_timeout(
            3000
        )


        # ====================================================
        # RACE LOOP
        # ====================================================


        for index, race in enumerate(
            races,
            start=1,
        ):

            race_key = race["race_key"]
            venue = race["venue"]
            race_no = race["race_no"]


            print()

            print(
                "-"
                * 100
            )

            print(
                f"[{index}/{len(races)}]",
                race_key,
            )


            race_result = {
                "race_key": race_key,
                "date": race["date"],
                "venue": venue,
                "race_no": race_no,
                "status": None,
                "venue_click": None,
                "race_click": None,
                "result_tab": None,
                "response_count": 0,
                "strong_response_count": 0,
                "candidate_response_count": 0,
                "ignored_jsj006_count": 0,
                "responses": [],
            }


            # ================================================
            # VENUE
            # ================================================


            if current_venue != venue:

                venue_ok = click_venue(
                    page,
                    venue,
                )


                race_result[
                    "venue_click"
                ] = venue_ok


                if not venue_ok:

                    race_result[
                        "status"
                    ] = "VENUE_BUTTON_NOT_FOUND"

                    judgement_counter[
                        race_result["status"]
                    ] += 1

                    results.append(
                        race_result
                    )

                    continue


                current_venue = venue


            else:

                race_result[
                    "venue_click"
                ] = "CURRENT_VENUE"


            # ================================================
            # CAPTURE START
            # ================================================


            active_capture[
                "race_key"
            ] = race_key

            active_capture[
                "responses"
            ] = []


            # ================================================
            # RACE CLICK
            # ================================================


            race_ok = click_race(
                page,
                race_no,
            )


            race_result[
                "race_click"
            ] = race_ok


            if not race_ok:

                race_result[
                    "status"
                ] = "RACE_BUTTON_NOT_FOUND"

                judgement_counter[
                    race_result["status"]
                ] += 1

                active_capture[
                    "race_key"
                ] = None

                results.append(
                    race_result
                )

                continue


            # ================================================
            # RESULT TAB
            # ================================================


            result_tab = click_result_tab(
                page
            )


            race_result[
                "result_tab"
            ] = result_tab


            page.wait_for_timeout(
                2500
            )


            # ================================================
            # CAPTURE END
            # ================================================


            captured = list(
                active_capture[
                    "responses"
                ]
            )


            active_capture[
                "race_key"
            ] = None


            # ================================================
            # RESPONSE CLASSIFY
            # ================================================


            strong_responses = []

            candidate_responses = []

            ignored_jsj006 = []


            for response_item in captured:

                judgement = (
                    response_item
                    .get(
                        "inspection",
                        {},
                    )
                    .get(
                        "judgement"
                    )
                )


                if (
                    judgement
                    == "STRONG_CONFIRMED_RESULT"
                ):

                    strong_responses.append(
                        response_item
                    )


                elif (
                    judgement
                    == "RESULT_CANDIDATE"
                ):

                    candidate_responses.append(
                        response_item
                    )


                elif (
                    judgement
                    == "JSJ006_PAST_RESULT_IGNORE"
                ):

                    ignored_jsj006.append(
                        response_item
                    )


            race_result[
                "response_count"
            ] = len(captured)

            race_result[
                "strong_response_count"
            ] = len(
                strong_responses
            )

            race_result[
                "candidate_response_count"
            ] = len(
                candidate_responses
            )

            race_result[
                "ignored_jsj006_count"
            ] = len(
                ignored_jsj006
            )


            # ================================================
            # SAVE RESPONSE
            # ================================================


            race_result[
                "responses"
            ] = (
                strong_responses
                +
                candidate_responses
            )


            # ================================================
            # STATUS
            # ================================================


            if strong_responses:

                race_result[
                    "status"
                ] = "CONFIRMED_RESULT_FOUND"


            elif candidate_responses:

                race_result[
                    "status"
                ] = "RESULT_CANDIDATE_FOUND"


            elif ignored_jsj006:

                race_result[
                    "status"
                ] = "ONLY_JSJ006_PAST_RESULT"


            else:

                race_result[
                    "status"
                ] = "RESULT_NOT_FOUND"


            judgement_counter[
                race_result["status"]
            ] += 1


            print(
                "  STATUS:",
                race_result["status"]
            )

            print(
                "  STRONG:",
                len(strong_responses)
            )

            print(
                "  CANDIDATE:",
                len(candidate_responses)
            )

            print(
                "  JSJ006 IGNORE:",
                len(ignored_jsj006)
            )


            results.append(
                race_result
            )


        # ====================================================
        # CLOSE
        # ====================================================


        browser.close()


    # ========================================================
    # FOUND
    # ========================================================


    confirmed_results = [
        item
        for item in results
        if item.get("status")
        == "CONFIRMED_RESULT_FOUND"
    ]


    candidate_results = [
        item
        for item in results
        if item.get("status")
        == "RESULT_CANDIDATE_FOUND"
    ]


    not_found_results = [
        item
        for item in results
        if item.get("status")
        in {
            "RESULT_NOT_FOUND",
            "ONLY_JSJ006_PAST_RESULT",
        }
    ]


    error_results = [
        item
        for item in results
        if item.get("status")
        in {
            "VENUE_BUTTON_NOT_FOUND",
            "RACE_BUTTON_NOT_FOUND",
        }
    ]


    # ========================================================
    # OUTPUT
    # ========================================================


    output = {
        "program": "055_test.py",
        "created_at": datetime.now().isoformat(),
        "source_file": str(SOURCE_FILE),
        "target_races": len(races),
        "confirmed_result_found": len(
            confirmed_results
        ),
        "result_candidate_found": len(
            candidate_results
        ),
        "result_not_found": len(
            not_found_results
        ),
        "navigation_error": len(
            error_results
        ),
        "status_summary": dict(
            judgement_counter
        ),
        "results": results,
    }


    save_json(
        OUT_FILE,
        output,
    )


    # ========================================================
    # FINAL
    # ========================================================


    print()

    print(
        "#"
        * 100
    )

    print(
        "055 最終結果"
    )

    print(
        "#"
        * 100
    )

    print()

    print(
        "TARGET RACES:",
        len(races)
    )

    print(
        "CONFIRMED RESULT FOUND:",
        len(confirmed_results)
    )

    print(
        "RESULT CANDIDATE FOUND:",
        len(candidate_results)
    )

    print(
        "RESULT NOT FOUND:",
        len(not_found_results)
    )

    print(
        "NAVIGATION ERROR:",
        len(error_results)
    )


    print()

    print(
        "★ STATUS SUMMARY ★"
    )


    for status, count in (
        judgement_counter.most_common()
    ):

        print(
            status,
            ":",
            count,
        )


    print()

    print(
        "★ CONFIRMED RESULT FOUND ★"
    )


    if not confirmed_results:

        print(
            "なし"
        )


    for item in confirmed_results:

        print()

        print(
            item.get("race_key")
        )

        print(
            "RESPONSE COUNT:",
            item.get(
                "response_count"
            )
        )

        print(
            "STRONG:",
            item.get(
                "strong_response_count"
            )
        )


        for response_item in (
            item.get(
                "responses",
                [],
            )
        ):

            inspection = (
                response_item.get(
                    "inspection",
                    {},
                )
            )


            print(
                "URL:",
                response_item.get("url")
            )

            print(
                "JUDGEMENT:",
                inspection.get(
                    "judgement"
                )
            )

            print(
                "TRUE KEYS:",
                inspection.get(
                    "true_keys"
                )
            )

            print(
                "SUPPORT KEYS:",
                inspection.get(
                    "support_keys"
                )
            )


    print()

    print(
        "★ RESULT CANDIDATE FOUND ★"
    )


    if not candidate_results:

        print(
            "なし"
        )


    for item in candidate_results:

        print(
            item.get("race_key")
        )


    print()

    print(
        "★ RESULT NOT FOUND ★"
    )


    if not not_found_results:

        print(
            "なし"
        )


    for item in not_found_results:

        print(
            item.get("race_key"),
            ":",
            item.get("status"),
        )


    print()

    print(
        "★ NAVIGATION ERROR ★"
    )


    if not error_results:

        print(
            "なし"
        )


    for item in error_results:

        print(
            item.get("race_key"),
            ":",
            item.get("status"),
        )


    print()

    print(
        "保存先:"
    )

    print(
        OUT_FILE
    )

    print()

    print(
        "=== 055 完了 ==="
    )


if __name__ == "__main__":

    main()