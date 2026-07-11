from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from collections import defaultdict
import json
import time


# ============================================================
# 048
#
# JSJ006 race_key 紐付けタイミング修正版
#
# 043 race_key地図
#        ↓
# 開催クリック前に 1R race_key SET
#        ↓
# 開催クリック
#        ↓
# 自動発生したJSJ006を1Rへ保存
#        ↓
# 各Rクリック前に race_key SET
#        ↓
# JSJ006保存
#
#
# 追加監査:
#
# ・同一URLの同一race_key内重複
# ・同一URLの別race_key重複
# ・CROSS_RACE_DUPLICATE_URL
#
#
# Edgeデバッグ起動必要
#
# ============================================================


BASE = Path(r"C:\競輪AI")


MAP_FILE = (
    BASE
    / "data_official"
    / "line_predictions"
    / "043_all_venues_official_lines.json"
)


OUT_DIR = (
    BASE
    / "data_official"
    / "pre_race"
    / "048_jsj006_timing_fixed"
)


OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_FILE = (
    OUT_DIR
    / "048_jsj006_timing_fixed.json"
)


CDP_URL = "http://127.0.0.1:9222"


VENUE_WAIT_SECONDS = 3.0

RACE_WAIT_SECONDS = 3.0

RESPONSE_SETTLE_SECONDS = 1.0


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
# 043 race map
# ============================================================


def flatten_map_races(data):

    races = []


    for venue_data in data.get(
        "venues",
        []
    ):

        venue = venue_data.get(
            "venue"
        )


        for race in venue_data.get(
            "races",
            []
        ):

            races.append({

                "race_key":
                    race.get(
                        "race_key"
                    ),

                "race_date":
                    race.get(
                        "race_date"
                    ),

                "venue":
                    venue,

                "race_no":
                    race.get(
                        "race_no"
                    ),

            })


    return races


def build_venue_race_map(races):

    venue_map = {}


    for race in races:

        venue = race.get(
            "venue"
        )


        venue_map.setdefault(
            venue,
            []
        ).append(
            race
        )


    for venue in venue_map:

        venue_map[
            venue
        ] = sorted(

            venue_map[
                venue
            ],

            key=lambda item: (
                item.get(
                    "race_no",
                    0
                )
            ),

        )


    return venue_map


# ============================================================
# LIVE venue
# ============================================================


def get_live_venues(page):

    return page.evaluate(
        """
        () => {

            const results = [];

            const container =
                document.getElementById(
                    "hcomRaceDiv"
                );

            if (!container) {

                return results;

            }

            const items = Array.from(
                container.querySelectorAll(
                    "li.kyotuHeader"
                )
            );

            for (
                let index = 0;
                index < items.length;
                index++
            ) {

                const item = items[index];

                const place =
                    item.querySelector(
                        "p.place"
                    );

                const liveButton =
                    item.querySelector(
                        "button[id^='hcombtnLive']"
                    );

                const hidden =
                    item.querySelector(
                        "input[id^='hcomHdnTouhyouLive']"
                    );

                if (
                    !place
                    ||
                    !liveButton
                ) {

                    continue;

                }

                const venue =
                    (
                        place.innerText
                        ||
                        ""
                    ).trim();

                if (!venue) {

                    continue;

                }

                results.push({

                    index:
                        index,

                    venue:
                        venue,

                    button_id:
                        liveButton.id
                        ||
                        "",

                    onclick:
                        liveButton.getAttribute(
                            "onclick"
                        )
                        ||
                        "",

                    hidden_id:
                        hidden
                        ? hidden.id
                        : null,

                    hidden_value:
                        hidden
                        ? hidden.value
                        : null,

                });

            }

            return results;

        }
        """
    )


# ============================================================
# PJ0314
# ============================================================


def get_pj0314_signature(page):

    try:

        return page.locator(
            "#PJ0314"
        ).inner_text(
            timeout=3000
        )

    except Exception:

        return ""


def wait_dom_change(
    page,
    before,
    timeout_seconds=10,
):

    start = time.time()


    while (
        time.time()
        -
        start
        <
        timeout_seconds
    ):

        after = get_pj0314_signature(
            page
        )


        if (
            after
            and
            after != before
        ):

            return True


        time.sleep(
            0.25
        )


    return False


# ============================================================
# JSJ006
# ============================================================


def is_jsj006_url(url):

    return (

        isinstance(
            url,
            str
        )

        and

        "JSJ006"
        in
        url.upper()

    )


def extract_url_parameters(url):

    try:

        parsed = urlparse(
            url
        )


        query = parse_qs(
            parsed.query
        )


        return {

            key:
                value

            for key, value
            in query.items()

        }


    except Exception:

        return {}


def safe_response_body(response):

    result = {

        "body_type":
            None,

        "json":
            None,

        "text":
            None,

        "body_error":
            None,

    }


    try:

        result[
            "json"
        ] = response.json()


        result[
            "body_type"
        ] = "JSON"


        return result


    except Exception:

        pass


    try:

        result[
            "text"
        ] = response.text()


        result[
            "body_type"
        ] = "TEXT"


        return result


    except Exception as e:

        result[
            "body_type"
        ] = "ERROR"


        result[
            "body_error"
        ] = repr(
            e
        )


        return result


# ============================================================
# 出力生成
# ============================================================


def build_output(
    source_data,
    race_records,
    cross_race_duplicates,
):

    found = [

        race

        for race in race_records

        if race.get(
            "status"
        )
        ==
        "JSJ006_FOUND"

    ]


    not_found = [

        race

        for race in race_records

        if race.get(
            "status"
        )
        ==
        "JSJ006_NOT_FOUND"

    ]


    errors = [

        race

        for race in race_records

        if race.get(
            "status"
        )
        in {

            "VENUE_NOT_FOUND",

            "VENUE_CLICK_ERROR",

            "RACE_BUTTON_NOT_FOUND",

            "RACE_CLICK_ERROR",

        }

    ]


    return {

        "program":
            "048_test.py",

        "created_at":
            datetime.now().isoformat(),

        "source_map_file":
            str(
                MAP_FILE
            ),

        "target_date":
            source_data.get(
                "race_date"
            ),

        "target_race_count":
            len(
                race_records
            ),

        "jsj006_found_count":
            len(
                found
            ),

        "jsj006_not_found_count":
            len(
                not_found
            ),

        "error_count":
            len(
                errors
            ),

        "cross_race_duplicate_url_count":
            len(
                cross_race_duplicates
            ),

        "cross_race_duplicate_urls":
            cross_race_duplicates,

        "races":
            race_records,

    }


def save_progress(
    source_data,
    race_records,
    cross_race_duplicates,
):

    output = build_output(

        source_data,

        race_records,

        cross_race_duplicates,

    )


    save_json(
        OUT_FILE,
        output,
    )


    return output


# ============================================================
# MAIN
# ============================================================


def main():

    print()

    print(
        "="
        * 100
    )

    print(
        "048 JSJ006 race_key 紐付けタイミング修正版"
    )

    print(
        "="
        * 100
    )

    print()


    # ========================================================
    # MAP
    # ========================================================


    if not MAP_FILE.exists():

        print(
            "ERROR: 043 JSONがありません"
        )

        return


    source_data = load_json(
        MAP_FILE
    )


    map_races = flatten_map_races(
        source_data
    )


    venue_race_map = build_venue_race_map(
        map_races
    )


    print(
        "TARGET DATE:",
        source_data.get(
            "race_date"
        )
    )

    print(
        "TARGET VENUES:",
        len(
            venue_race_map
        )
    )

    print(
        "TARGET RACES:",
        len(
            map_races
        )
    )


    # ========================================================
    # Edge
    # ========================================================


    with sync_playwright() as p:

        browser = (
            p.chromium.connect_over_cdp(
                CDP_URL
            )
        )


        if not browser.contexts:

            print(
                "ERROR: Edge contextなし"
            )

            return


        page = None


        for context in browser.contexts:

            for candidate in context.pages:

                try:

                    print(
                        "PAGE:",
                        candidate.url
                    )


                    if (
                        "keirin.jp"
                        in candidate.url.lower()
                        and
                        "racelive"
                        in candidate.url.lower()
                    ):

                        page = candidate


                except Exception:

                    pass


        if page is None:

            print(
                "ERROR: raceliveページなし"
            )

            return


        print()

        print(
            "TARGET PAGE:"
        )

        print(
            page.url
        )


        # ====================================================
        # VENUE MAP
        # ====================================================


        live_venues = get_live_venues(
            page
        )


        live_venue_map = {

            item.get(
                "venue"
            ):
                item

            for item in live_venues

        }


        print()

        print(
            "LIVE VENUES:"
        )


        for item in live_venues:

            print(

                item.get(
                    "venue"
                ),

                "->",

                item.get(
                    "button_id"
                ),

            )


        # ====================================================
        # CAPTURE BOX
        # ====================================================


        current_race_key = {

            "value":
                None

        }


        current_capture_phase = {

            "value":
                None

        }


        captured_by_race = defaultdict(
            list
        )


        url_race_keys = defaultdict(
            set
        )


        cross_duplicate_signatures = set()

        cross_race_duplicates = []


        # ====================================================
        # RESPONSE
        # ====================================================


        def on_response(response):

            try:

                url = response.url


                if not is_jsj006_url(
                    url
                ):

                    return


                race_key = (
                    current_race_key[
                        "value"
                    ]
                )


                capture_phase = (
                    current_capture_phase[
                        "value"
                    ]
                )


                if not race_key:

                    print()

                    print(
                        "JSJ006 IGNORED:"
                    )

                    print(
                        "CURRENT RACE KEY NONE"
                    )

                    print(
                        url
                    )


                    return


                body = safe_response_body(
                    response
                )


                response_record = {

                    "captured_at":
                        datetime.now().isoformat(),

                    "assigned_race_key":
                        race_key,

                    "capture_phase":
                        capture_phase,

                    "url":
                        url,

                    "status":
                        response.status,

                    "url_parameters":
                        extract_url_parameters(
                            url
                        ),

                    "body_type":
                        body.get(
                            "body_type"
                        ),

                    "json":
                        body.get(
                            "json"
                        ),

                    "text":
                        body.get(
                            "text"
                        ),

                    "body_error":
                        body.get(
                            "body_error"
                        ),

                }


                # =============================================
                # 同一race_key内URL重複
                # =============================================


                existing_urls = {

                    item.get(
                        "url"
                    )

                    for item
                    in captured_by_race[
                        race_key
                    ]

                }


                if url in existing_urls:

                    print()

                    print(
                        "JSJ006 SAME RACE DUPLICATE:"
                    )

                    print(
                        race_key
                    )

                    print(
                        url
                    )


                    return


                # =============================================
                # 別race_key URL監査
                # =============================================


                previous_race_keys = set(
                    url_race_keys[
                        url
                    ]
                )


                other_race_keys = sorted(

                    previous_race_keys
                    -
                    {
                        race_key
                    }

                )


                if other_race_keys:

                    signature = (

                        url,

                        tuple(
                            other_race_keys
                        ),

                        race_key,

                    )


                    if (
                        signature
                        not in
                        cross_duplicate_signatures
                    ):

                        cross_duplicate_signatures.add(
                            signature
                        )


                        duplicate_record = {

                            "url":
                                url,

                            "previous_race_keys":
                                other_race_keys,

                            "new_race_key":
                                race_key,

                            "detected_at":
                                datetime.now().isoformat(),

                        }


                        cross_race_duplicates.append(
                            duplicate_record
                        )


                        print()

                        print(
                            "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                        )

                        print(
                            "CROSS_RACE_DUPLICATE_URL"
                        )

                        print(
                            "PREVIOUS:",
                            other_race_keys
                        )

                        print(
                            "NEW:",
                            race_key
                        )

                        print(
                            "URL:",
                            url
                        )

                        print(
                            "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                        )


                url_race_keys[
                    url
                ].add(
                    race_key
                )


                captured_by_race[
                    race_key
                ].append(
                    response_record
                )


                print()

                print(
                    "★ JSJ006 CAPTURE ★"
                )

                print(
                    "ASSIGNED RACE KEY:",
                    race_key
                )

                print(
                    "PHASE:",
                    capture_phase
                )

                print(
                    "STATUS:",
                    response.status
                )

                print(
                    "URL:",
                    url
                )


            except Exception as e:

                print()

                print(
                    "RESPONSE HANDLER ERROR:"
                )

                print(
                    repr(
                        e
                    )
                )


        page.on(
            "response",
            on_response,
        )


        # ====================================================
        # RUN
        # ====================================================


        race_records = []


        total_races = len(
            map_races
        )


        race_counter = 0


        for venue_name, races in (
            venue_race_map.items()
        ):

            print()

            print(
                "#"
                * 100
            )

            print(
                "VENUE:",
                venue_name
            )

            print(
                "#"
                * 100
            )


            venue_data = live_venue_map.get(
                venue_name
            )


            if not venue_data:

                for race in races:

                    race_counter += 1


                    race_records.append({

                        **race,

                        "status":
                            "VENUE_NOT_FOUND",

                        "error":
                            None,

                        "jsj006_response_count":
                            0,

                        "jsj006_responses":
                            [],

                    })


                save_progress(

                    source_data,

                    race_records,

                    cross_race_duplicates,

                )


                continue


            # =================================================
            # 重要
            #
            # 開催クリック前に1R race_keyをセット
            # =================================================


            first_race = races[0]


            first_race_key = (
                first_race.get(
                    "race_key"
                )
            )


            current_race_key[
                "value"
            ] = (
                first_race_key
            )


            current_capture_phase[
                "value"
            ] = (
                "VENUE_CLICK_AUTO_FIRST_RACE"
            )


            print()

            print(
                "PRESET BEFORE VENUE CLICK:"
            )

            print(
                first_race_key
            )


            before = get_pj0314_signature(
                page
            )


            try:

                page.locator(

                    "#"
                    +
                    venue_data[
                        "button_id"
                    ]

                ).click(
                    timeout=30000
                )


                wait_dom_change(

                    page,

                    before,

                    timeout_seconds=10,

                )


                time.sleep(
                    VENUE_WAIT_SECONDS
                )


            except Exception as e:

                for race in races:

                    race_counter += 1


                    race_records.append({

                        **race,

                        "status":
                            "VENUE_CLICK_ERROR",

                        "error":
                            repr(
                                e
                            ),

                        "jsj006_response_count":
                            0,

                        "jsj006_responses":
                            [],

                    })


                save_progress(

                    source_data,

                    race_records,

                    cross_race_duplicates,

                )


                continue


            # =================================================
            # RACE LOOP
            # =================================================


            for race in races:

                race_counter += 1


                race_key = race.get(
                    "race_key"
                )


                race_no = race.get(
                    "race_no"
                )


                print()

                print(
                    "-"
                    * 100
                )

                print(

                    f"[{race_counter}/"
                    f"{total_races}]"

                )

                print(
                    race_key
                )


                # =============================================
                # 重要
                #
                # クリック前SET
                # =============================================


                current_race_key[
                    "value"
                ] = (
                    race_key
                )


                current_capture_phase[
                    "value"
                ] = (
                    "RACE_CLICK"
                )


                race_button_id = (

                    "hhRaceBtn"
                    +
                    str(
                        race_no
                    )

                )


                race_record = {

                    **race,

                    "status":
                        None,

                    "error":
                        None,

                    "jsj006_response_count":
                        0,

                    "jsj006_responses":
                        [],

                }


                try:

                    race_button = page.locator(

                        "#"
                        +
                        race_button_id

                    )


                    if race_button.count() == 0:

                        race_record[
                            "status"
                        ] = (
                            "RACE_BUTTON_NOT_FOUND"
                        )


                        race_records.append(
                            race_record
                        )


                        save_progress(

                            source_data,

                            race_records,

                            cross_race_duplicates,

                        )


                        continue


                except Exception as e:

                    race_record[
                        "status"
                    ] = (
                        "RACE_BUTTON_NOT_FOUND"
                    )


                    race_record[
                        "error"
                    ] = repr(
                        e
                    )


                    race_records.append(
                        race_record
                    )


                    save_progress(

                        source_data,

                        race_records,

                        cross_race_duplicates,

                    )


                    continue


                # =============================================
                # CLICK
                # =============================================


                before = get_pj0314_signature(
                    page
                )


                try:

                    race_button.click(
                        timeout=30000
                    )


                    wait_dom_change(

                        page,

                        before,

                        timeout_seconds=10,

                    )


                    time.sleep(
                        RACE_WAIT_SECONDS
                    )


                    time.sleep(
                        RESPONSE_SETTLE_SECONDS
                    )


                except Exception as e:

                    race_record[
                        "status"
                    ] = (
                        "RACE_CLICK_ERROR"
                    )


                    race_record[
                        "error"
                    ] = repr(
                        e
                    )


                    race_records.append(
                        race_record
                    )


                    save_progress(

                        source_data,

                        race_records,

                        cross_race_duplicates,

                    )


                    continue


                # =============================================
                # CAPTURE RESULT
                # =============================================


                responses = list(

                    captured_by_race.get(
                        race_key,
                        []
                    )

                )


                race_record[
                    "jsj006_response_count"
                ] = len(
                    responses
                )


                race_record[
                    "jsj006_responses"
                ] = responses


                if responses:

                    race_record[
                        "status"
                    ] = (
                        "JSJ006_FOUND"
                    )


                else:

                    race_record[
                        "status"
                    ] = (
                        "JSJ006_NOT_FOUND"
                    )


                race_records.append(
                    race_record
                )


                print()

                print(
                    "STATUS:",
                    race_record[
                        "status"
                    ]
                )

                print(
                    "RESPONSE COUNT:",
                    race_record[
                        "jsj006_response_count"
                    ]
                )


                save_progress(

                    source_data,

                    race_records,

                    cross_race_duplicates,

                )


        # ====================================================
        # CLEAN
        # ====================================================


        current_race_key[
            "value"
        ] = None


        current_capture_phase[
            "value"
        ] = None


        try:

            page.remove_listener(
                "response",
                on_response,
            )

        except Exception:

            pass


        output = save_progress(

            source_data,

            race_records,

            cross_race_duplicates,

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
        "048 最終結果"
    )

    print(
        "#"
        * 100
    )

    print()

    print(
        "TARGET DATE:",
        output[
            "target_date"
        ]
    )

    print(
        "TARGET RACES:",
        output[
            "target_race_count"
        ]
    )

    print(
        "JSJ006 FOUND:",
        output[
            "jsj006_found_count"
        ]
    )

    print(
        "JSJ006 NOT FOUND:",
        output[
            "jsj006_not_found_count"
        ]
    )

    print(
        "ERROR:",
        output[
            "error_count"
        ]
    )

    print(
        "CROSS RACE DUPLICATE URL:",
        output[
            "cross_race_duplicate_url_count"
        ]
    )


    print()

    print(
        "★ CROSS RACE DUPLICATE URL ★"
    )


    duplicates = output.get(
        "cross_race_duplicate_urls",
        []
    )


    if not duplicates:

        print(
            "なし"
        )


    for item in duplicates:

        print()

        print(
            "PREVIOUS:",
            item.get(
                "previous_race_keys"
            )
        )

        print(
            "NEW:",
            item.get(
                "new_race_key"
            )
        )

        print(
            "URL:",
            item.get(
                "url"
            )
        )


    print()

    print(
        "★ 開催別FOUND ★"
    )


    venue_summary = {}


    for race in output.get(
        "races",
        []
    ):

        venue = race.get(
            "venue"
        )


        venue_summary.setdefault(

            venue,

            {

                "race_count":
                    0,

                "found":
                    0,

                "not_found":
                    0,

                "error":
                    0,

            },

        )


        venue_summary[
            venue
        ][
            "race_count"
        ] += 1


        status = race.get(
            "status"
        )


        if status == "JSJ006_FOUND":

            venue_summary[
                venue
            ][
                "found"
            ] += 1


        elif status == "JSJ006_NOT_FOUND":

            venue_summary[
                venue
            ][
                "not_found"
            ] += 1


        else:

            venue_summary[
                venue
            ][
                "error"
            ] += 1


    for venue, summary in (
        venue_summary.items()
    ):

        print()

        print(
            venue
        )

        print(
            "RACES:",
            summary[
                "race_count"
            ]
        )

        print(
            "FOUND:",
            summary[
                "found"
            ]
        )

        print(
            "NOT FOUND:",
            summary[
                "not_found"
            ]
        )

        print(
            "ERROR:",
            summary[
                "error"
            ]
        )


    print()

    print(
        "★ FOUND RACE KEY ★"
    )


    for race in output.get(
        "races",
        []
    ):

        if (
            race.get(
                "status"
            )
            ==
            "JSJ006_FOUND"
        ):

            print(
                race.get(
                    "race_key"
                )
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
        "=== 048 完了 ==="
    )


if __name__ == "__main__":

    main()