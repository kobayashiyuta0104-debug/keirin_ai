from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from collections import defaultdict
import json
import time


# ============================================================
# 050
#
# JSJ006 RACE CLICK ONLY CAPTURE
#
# 049結論:
#
# IGNORE_ALL_VENUE_CLICK_AUTO_JSJ006
#
#
# 正式取得候補方式:
#
# 開催切替
# ↓
# capture_enabled = False
# ↓
# 開催切替中のJSJ006は完全無視
# ↓
# 通信安定待ち
# ↓
# race_key SET
# ↓
# capture_enabled = True
# ↓
# Rボタンクリック
# ↓
# JSJ006 CAPTURE
# ↓
# 待機
# ↓
# capture_enabled = False
#
#
# 追加監査:
#
# ・同一race_key内URL重複除去
# ・別race_key同一URL検出
# ・別race_key重複URLはCONFLICT扱い
# ・正式FOUNDには混ぜない
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
    / "050_jsj006_race_click_only"
)


OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_FILE = (
    OUT_DIR
    / "050_jsj006_race_click_only.json"
)


CDP_URL = "http://127.0.0.1:9222"


VENUE_WAIT_SECONDS = 4.0

PRE_RACE_CAPTURE_WAIT_SECONDS = 0.5

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
# 043 RACE MAP
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
# LIVE VENUES
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

                    "index":
                        index,

                    "venue":
                        venue,

                    "button_id":
                        liveButton.id
                        ||
                        "",

                    "onclick":
                        liveButton.getAttribute(
                            "onclick"
                        )
                        ||
                        "",

                    "hidden_id":
                        hidden
                        ? hidden.id
                        : null,

                    "hidden_value":
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
            str,
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
# OUTPUT
# ============================================================


def build_output(
    source_data,
    race_records,
    ignored_venue_responses,
    conflicts,
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


    conflict_races = [

        race

        for race in race_records

        if race.get(
            "status"
        )
        ==
        "JSJ006_URL_CONFLICT"

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
            "050_test.py",

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

        "jsj006_url_conflict_race_count":
            len(
                conflict_races
            ),

        "error_count":
            len(
                errors
            ),

        "ignored_venue_jsj006_count":
            len(
                ignored_venue_responses
            ),

        "conflict_count":
            len(
                conflicts
            ),

        "ignored_venue_jsj006":
            ignored_venue_responses,

        "conflicts":
            conflicts,

        "races":
            race_records,

    }


def save_progress(
    source_data,
    race_records,
    ignored_venue_responses,
    conflicts,
):

    output = build_output(

        source_data,

        race_records,

        ignored_venue_responses,

        conflicts,

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
        "050 JSJ006 RACE CLICK ONLY CAPTURE"
    )

    print(
        "="
        * 100
    )

    print()


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
        # CAPTURE STATE
        # ====================================================


        capture_enabled = {

            "value":
                False

        }


        capture_phase = {

            "value":
                "IDLE"

        }


        current_race_key = {

            "value":
                None

        }


        captured_by_race = defaultdict(
            list
        )


        ignored_venue_responses = []


        url_owner = {}


        conflicts = []


        conflict_race_keys = set()


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


                phase = capture_phase[
                    "value"
                ]


                race_key = current_race_key[
                    "value"
                ]


                # =============================================
                # CAPTURE DISABLED
                # =============================================


                if not capture_enabled[
                    "value"
                ]:

                    ignored_record = {

                        "captured_at":
                            datetime.now().isoformat(),

                        "phase":
                            phase,

                        "current_race_key":
                            race_key,

                        "url":
                            url,

                        "status":
                            response.status,

                    }


                    ignored_venue_responses.append(
                        ignored_record
                    )


                    print()

                    print(
                        "JSJ006 IGNORED"
                    )

                    print(
                        "PHASE:",
                        phase
                    )

                    print(
                        "CURRENT RACE KEY:",
                        race_key
                    )

                    print(
                        "URL:",
                        url
                    )


                    return


                # =============================================
                # RACE KEY NONE
                # =============================================


                if not race_key:

                    print()

                    print(
                        "JSJ006 IGNORED:"
                    )

                    print(
                        "CAPTURE ENABLED BUT RACE KEY NONE"
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
                        phase,

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
                # SAME RACE DUPLICATE
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
                        "SAME RACE DUPLICATE IGNORED:"
                    )

                    print(
                        race_key
                    )

                    print(
                        url
                    )


                    return


                # =============================================
                # CROSS RACE URL CONFLICT
                # =============================================


                previous_owner = url_owner.get(
                    url
                )


                if (
                    previous_owner
                    and
                    previous_owner != race_key
                ):

                    conflict = {

                        "detected_at":
                            datetime.now().isoformat(),

                        "url":
                            url,

                        "previous_race_key":
                            previous_owner,

                        "new_race_key":
                            race_key,

                        "action":
                            "NEW_RESPONSE_NOT_SAVED_AND_BOTH_RACES_MARKED_CONFLICT",

                    }


                    conflicts.append(
                        conflict
                    )


                    conflict_race_keys.add(
                        previous_owner
                    )


                    conflict_race_keys.add(
                        race_key
                    )


                    print()

                    print(
                        "!"
                        * 100
                    )

                    print(
                        "CROSS RACE JSJ006 URL CONFLICT"
                    )

                    print(
                        "PREVIOUS:",
                        previous_owner
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
                        "NEW RESPONSE NOT SAVED"
                    )

                    print(
                        "!"
                        * 100
                    )


                    return


                # =============================================
                # SAVE
                # =============================================


                url_owner[
                    url
                ] = race_key


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
                    "RACE KEY:",
                    race_key
                )

                print(
                    "PHASE:",
                    phase
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

                    ignored_venue_responses,

                    conflicts,

                )


                continue


            # =================================================
            # VENUE CLICK
            #
            # CAPTURE完全OFF
            # =================================================


            capture_enabled[
                "value"
            ] = False


            capture_phase[
                "value"
            ] = "VENUE_SWITCH_IGNORE"


            current_race_key[
                "value"
            ] = None


            print()

            print(
                "VENUE SWITCH CAPTURE OFF"
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

                    ignored_venue_responses,

                    conflicts,

                )


                continue


            # =================================================
            # RACES
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


                race_button_id = (

                    "hhRaceBtn"
                    +
                    str(
                        race_no
                    )

                )


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

                            ignored_venue_responses,

                            conflicts,

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

                        ignored_venue_responses,

                        conflicts,

                    )


                    continue


                # =============================================
                # CLICK PREPARE
                # =============================================


                capture_enabled[
                    "value"
                ] = False


                capture_phase[
                    "value"
                ] = "RACE_PREPARE"


                current_race_key[
                    "value"
                ] = race_key


                time.sleep(
                    PRE_RACE_CAPTURE_WAIT_SECONDS
                )


                captured_by_race[
                    race_key
                ] = []


                # =============================================
                # CAPTURE ON
                # =============================================


                capture_phase[
                    "value"
                ] = "RACE_CLICK_ONLY"


                capture_enabled[
                    "value"
                ] = True


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

                    capture_enabled[
                        "value"
                    ] = False


                    capture_phase[
                        "value"
                    ] = "RACE_CLICK_ERROR"


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

                        ignored_venue_responses,

                        conflicts,

                    )


                    continue


                # =============================================
                # CAPTURE OFF
                # =============================================


                capture_enabled[
                    "value"
                ] = False


                capture_phase[
                    "value"
                ] = "RACE_CAPTURE_FINISHED"


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


                if race_key in conflict_race_keys:

                    race_record[
                        "status"
                    ] = (
                        "JSJ006_URL_CONFLICT"
                    )


                elif responses:

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

                    ignored_venue_responses,

                    conflicts,

                )


        # ====================================================
        # CLEAN
        # ====================================================


        capture_enabled[
            "value"
        ] = False


        capture_phase[
            "value"
        ] = "FINISHED"


        current_race_key[
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

            ignored_venue_responses,

            conflicts,

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
        "050 最終結果"
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
        "JSJ006 URL CONFLICT RACES:",
        output[
            "jsj006_url_conflict_race_count"
        ]
    )

    print(
        "ERROR:",
        output[
            "error_count"
        ]
    )

    print(
        "IGNORED VENUE JSJ006:",
        output[
            "ignored_venue_jsj006_count"
        ]
    )

    print(
        "CONFLICT COUNT:",
        output[
            "conflict_count"
        ]
    )


    print()

    print(
        "★ 開催別結果 ★"
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

                "races":
                    0,

                "found":
                    0,

                "not_found":
                    0,

                "conflict":
                    0,

                "error":
                    0,

            },

        )


        summary = venue_summary[
            venue
        ]


        summary[
            "races"
        ] += 1


        status = race.get(
            "status"
        )


        if status == "JSJ006_FOUND":

            summary[
                "found"
            ] += 1


        elif status == "JSJ006_NOT_FOUND":

            summary[
                "not_found"
            ] += 1


        elif status == "JSJ006_URL_CONFLICT":

            summary[
                "conflict"
            ] += 1


        else:

            summary[
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
                "races"
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
            "CONFLICT:",
            summary[
                "conflict"
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
        "★ CONFLICT ★"
    )


    if not output.get(
        "conflicts"
    ):

        print(
            "なし"
        )


    for conflict in output.get(
        "conflicts",
        []
    ):

        print()

        print(
            "PREVIOUS:",
            conflict.get(
                "previous_race_key"
            )
        )

        print(
            "NEW:",
            conflict.get(
                "new_race_key"
            )
        )

        print(
            "URL:",
            conflict.get(
                "url"
            )
        )


    print()

    print(
        "★ FOUND RACE KEY ★"
    )


    for race in output.get(
        "races",
        []
    ):

        if race.get(
            "status"
        ) == "JSJ006_FOUND":

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
        "=== 050 完了 ==="
    )


if __name__ == "__main__":

    main()