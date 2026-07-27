from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import json
import time


# ============================================================
# 046
#
# 043 race_key地図
#        ↓
# 同じ開催・同じRを巡回
#        ↓
# JSJ006通信監視
#        ↓
# race_key付きで生レスポンス保存
#
#
# 目的:
#
# 20260710の80レースについて
# レース前能力データ候補 JSJ006 が
# 現在も取得できるか確認する
#
#
# 注意:
#
# ・今回は解析しすぎない
# ・JSJ006レスポンスを生保存
# ・race_keyへ直接接続
# ・終了済みレースも巡回
# ・途中保存あり
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
    / "046_jsj006_by_race_key"
)


OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_FILE = (
    OUT_DIR
    / "046_jsj006_by_race_key.json"
)


CDP_URL = "http://127.0.0.1:9222"


VENUE_WAIT_SECONDS = 2.0

RACE_WAIT_SECONDS = 3.0

RESPONSE_SETTLE_SECONDS = 1.0


# ============================================================
# JSON読込
# ============================================================


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


# ============================================================
# JSON保存
# ============================================================


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
# 043レース平坦化
# ============================================================


def flatten_map_races(data):

    races = []


    for venue_data in data.get(
        "venues",
        []
    ):

        venue_name = (
            venue_data.get(
                "venue"
            )
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
                    venue_name,

                "race_no":
                    race.get(
                        "race_no"
                    ),

            })


    return races


# ============================================================
# 開催順MAP
# ============================================================


def build_venue_race_map(races):

    venue_map = {}


    for race in races:

        venue = race.get(
            "venue"
        )


        if venue not in venue_map:

            venue_map[
                venue
            ] = []


        venue_map[
            venue
        ].append(
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
# LIVE開催一覧
#
# 043成功方式
# ============================================================


def get_live_venues(page):

    return page.evaluate(
        """
        () => {

            const results = [];

            const container = (
                document.getElementById(
                    "hcomRaceDiv"
                )
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

                const place = (
                    item.querySelector(
                        "p.place"
                    )
                );

                const liveButton = (
                    item.querySelector(
                        "button[id^='hcombtnLive']"
                    )
                );

                const hidden = (
                    item.querySelector(
                        "input[id^='hcomHdnTouhyouLive']"
                    )
                );

                if (
                    !place
                    ||
                    !liveButton
                ) {

                    continue;

                }

                const venue = (
                    place.innerText || ""
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
                        liveButton.id || "",

                    onclick:
                        liveButton.getAttribute(
                            "onclick"
                        ) || "",

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
# 現在ページ署名
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


# ============================================================
# DOM変化待ち
# ============================================================


def wait_dom_change(
    page,
    before,
    timeout_seconds=10,
):

    start = time.time()


    while (
        time.time() - start
        <
        timeout_seconds
    ):

        after = (
            get_pj0314_signature(
                page
            )
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
# URLパラメータ取得
# ============================================================


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


# ============================================================
# JSJ006判定
# ============================================================


def is_jsj006_url(url):

    if not isinstance(
        url,
        str,
    ):

        return False


    return (
        "JSJ006"
        in
        url.upper()
    )


# ============================================================
# レスポンスJSON安全取得
# ============================================================


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

        data = response.json()


        result[
            "body_type"
        ] = (
            "JSON"
        )


        result[
            "json"
        ] = (
            data
        )


        return result


    except Exception:

        pass


    try:

        text = response.text()


        result[
            "body_type"
        ] = (
            "TEXT"
        )


        result[
            "text"
        ] = (
            text
        )


        return result


    except Exception as e:

        result[
            "body_type"
        ] = (
            "ERROR"
        )


        result[
            "body_error"
        ] = (
            repr(
                e
            )
        )


        return result


# ============================================================
# 出力作成
# ============================================================


def build_output(
    source_data,
    race_records,
):

    found_records = [

        race

        for race in race_records

        if (
            race.get(
                "status"
            )
            ==
            "JSJ006_FOUND"
        )

    ]


    not_found_records = [

        race

        for race in race_records

        if (
            race.get(
                "status"
            )
            ==
            "JSJ006_NOT_FOUND"
        )

    ]


    error_records = [

        race

        for race in race_records

        if (
            race.get(
                "status"
            )
            in {

                "VENUE_NOT_FOUND",

                "VENUE_CLICK_ERROR",

                "RACE_BUTTON_NOT_FOUND",

                "RACE_CLICK_ERROR",

            }
        )

    ]


    return {

        "program":
            "046_test.py",

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
                found_records
            ),

        "jsj006_not_found_count":
            len(
                not_found_records
            ),

        "error_count":
            len(
                error_records
            ),

        "races":
            race_records,

    }


# ============================================================
# 途中保存
# ============================================================


def save_progress(
    source_data,
    race_records,
):

    output = build_output(
        source_data,
        race_records,
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
        "046 043 race_key地図 × JSJ006取得テスト"
    )

    print(
        "="
        * 100
    )

    print()


    # ========================================================
    # 043読込
    # ========================================================


    print(
        "[1] 043地図読込"
    )

    print()

    print(
        MAP_FILE
    )


    if not MAP_FILE.exists():

        print()

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


    venue_race_map = (
        build_venue_race_map(
            map_races
        )
    )


    print()

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
    # Edge接続
    # ========================================================


    print()

    print(
        "[2] Edgeデバッグ接続"
    )


    with sync_playwright() as p:

        browser = (
            p.chromium.connect_over_cdp(
                CDP_URL
            )
        )


        if not browser.contexts:

            print()

            print(
                "ERROR: Edge contextなし"
            )

            return


        # ====================================================
        # racelive探索
        # ====================================================


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

            print()

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
        # 開催一覧
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
            "[3] 現在LIVE開催"
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
        # JSJ006通信保存箱
        # ====================================================


        current_race_key = {

            "value":
                None

        }


        captured_by_race = {}


        # ====================================================
        # RESPONSE監視
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


                if not race_key:

                    return


                print()

                print(
                    "★ JSJ006 RESPONSE ★"
                )

                print(
                    "RACE KEY:",
                    race_key
                )

                print(
                    "STATUS:",
                    response.status
                )

                print(
                    "URL:",
                    url
                )


                body = safe_response_body(
                    response
                )


                response_record = {

                    "captured_at":
                        datetime.now().isoformat(),

                    "race_key":
                        race_key,

                    "url":
                        url,

                    "status":
                        response.status,

                    "headers":
                        dict(
                            response.headers
                        ),

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


                if race_key not in captured_by_race:

                    captured_by_race[
                        race_key
                    ] = []


                captured_by_race[
                    race_key
                ].append(
                    response_record
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
        # 全開催巡回
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


            venue_data = (
                live_venue_map.get(
                    venue_name
                )
            )


            # =================================================
            # 開催なし
            # =================================================


            if not venue_data:

                print()

                print(
                    "VENUE NOT FOUND"
                )


                for race in races:

                    race_counter += 1


                    race_records.append({

                        "race_key":
                            race.get(
                                "race_key"
                            ),

                        "race_date":
                            race.get(
                                "race_date"
                            ),

                        "venue":
                            venue_name,

                        "race_no":
                            race.get(
                                "race_no"
                            ),

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
                )


                continue


            # =================================================
            # 開催クリック
            # =================================================


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

                print()

                print(
                    "VENUE CLICK ERROR:"
                )

                print(
                    repr(
                        e
                    )
                )


                for race in races:

                    race_counter += 1


                    race_records.append({

                        "race_key":
                            race.get(
                                "race_key"
                            ),

                        "race_date":
                            race.get(
                                "race_date"
                            ),

                        "venue":
                            venue_name,

                        "race_no":
                            race.get(
                                "race_no"
                            ),

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
                )


                continue


            # =================================================
            # 全R
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

                    "race_key":
                        race_key,

                    "race_date":
                        race.get(
                            "race_date"
                        ),

                    "venue":
                        venue_name,

                    "race_no":
                        race_no,

                    "status":
                        None,

                    "error":
                        None,

                    "jsj006_response_count":
                        0,

                    "jsj006_responses":
                        [],

                }


                current_race_key[
                    "value"
                ] = (
                    race_key
                )


                captured_by_race[
                    race_key
                ] = []


                race_button_id = (

                    "hhRaceBtn"
                    +
                    str(
                        race_no
                    )

                )


                # =============================================
                # Rボタン確認
                # =============================================


                try:

                    race_button = (
                        page.locator(
                            "#"
                            +
                            race_button_id
                        )
                    )


                    if (
                        race_button.count()
                        ==
                        0
                    ):

                        race_record[
                            "status"
                        ] = (
                            "RACE_BUTTON_NOT_FOUND"
                        )


                        race_records.append(
                            race_record
                        )


                        print(
                            "STATUS:",
                            race_record[
                                "status"
                            ]
                        )


                        save_progress(
                            source_data,
                            race_records,
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
                    ] = (
                        repr(
                            e
                        )
                    )


                    race_records.append(
                        race_record
                    )


                    save_progress(
                        source_data,
                        race_records,
                    )


                    continue


                # =============================================
                # Rクリック
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
                    ] = (
                        repr(
                            e
                        )
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
                        "ERROR:",
                        race_record[
                            "error"
                        ]
                    )


                    save_progress(
                        source_data,
                        race_records,
                    )


                    continue


                # =============================================
                # JSJ006確認
                # =============================================


                responses = (
                    captured_by_race.get(
                        race_key,
                        []
                    )
                )


                race_record[
                    "jsj006_response_count"
                ] = (
                    len(
                        responses
                    )
                )


                race_record[
                    "jsj006_responses"
                ] = (
                    responses
                )


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
                    "JSJ006 RESPONSE COUNT:",
                    race_record[
                        "jsj006_response_count"
                    ]
                )


                # =============================================
                # 途中保存
                # =============================================


                save_progress(
                    source_data,
                    race_records,
                )


        # ====================================================
        # 監視解除
        # ====================================================


        try:

            page.remove_listener(
                "response",
                on_response,
            )

        except Exception:

            pass


        current_race_key[
            "value"
        ] = None


        # ====================================================
        # 最終保存
        # ====================================================


        output = save_progress(
            source_data,
            race_records,
        )


    # ========================================================
    # 最終結果
    # ========================================================


    print()

    print(
        "#"
        * 100
    )

    print(
        "046 最終結果"
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


    print()

    print(
        "★ JSJ006 FOUND一覧 ★"
    )


    found_races = [

        race

        for race in output.get(
            "races",
            []
        )

        if (
            race.get(
                "status"
            )
            ==
            "JSJ006_FOUND"
        )

    ]


    if not found_races:

        print(
            "なし"
        )


    for race in found_races:

        print()

        print(
            race.get(
                "race_key"
            )
        )

        print(
            "RESPONSE COUNT:",
            race.get(
                "jsj006_response_count"
            )
        )


        for response in race.get(
            "jsj006_responses",
            []
        ):

            print(
                "STATUS:",
                response.get(
                    "status"
                )
            )

            print(
                "BODY TYPE:",
                response.get(
                    "body_type"
                )
            )

            print(
                "URL:",
                response.get(
                    "url"
                )
            )


    print()

    print(
        "★ JSJ006 NOT FOUND一覧 ★"
    )


    not_found_races = [

        race

        for race in output.get(
            "races",
            []
        )

        if (
            race.get(
                "status"
            )
            ==
            "JSJ006_NOT_FOUND"
        )

    ]


    if not not_found_races:

        print(
            "なし"
        )


    for race in not_found_races:

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
        "=== 046 完了 ==="
    )


if __name__ == "__main__":

    main()