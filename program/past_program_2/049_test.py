from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import json


# ============================================================
# 049
#
# 048 CROSS_RACE_DUPLICATE_URL
# capture_phase 監査
#
# 目的:
#
# 同じJSJ006 URLが別race_keyへ保存された5件について
#
# ・VENUE_CLICK_AUTO_FIRST_RACE
# ・RACE_CLICK
#
# のどちらで取得されたか確認する
#
#
# 仮説:
#
# 開催切替時
# ↓
# 実際には現在表示中RのJSJ006が発生
# ↓
# 048が開催1Rへ誤登録
#
# その後
# ↓
# 本当のRをクリック
# ↓
# 同じJSJ006 URLが再発生
# ↓
# 正しいrace_keyへ登録
#
#
# Edge不要
# サイトアクセスなし
#
# ============================================================


BASE = Path(r"C:\競輪AI")


SRC = (
    BASE
    / "data_official"
    / "pre_race"
    / "048_jsj006_timing_fixed"
    / "048_jsj006_timing_fixed.json"
)


OUT_DIR = (
    BASE
    / "data_official"
    / "pre_race"
    / "049_duplicate_phase_audit"
)


OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_FILE = (
    OUT_DIR
    / "049_duplicate_phase_audit.json"
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
# URL INDEX
# ============================================================


def build_url_index(races):

    url_index = defaultdict(
        list
    )


    for race in races:

        race_key = race.get(
            "race_key"
        )


        race_status = race.get(
            "status"
        )


        for response in race.get(
            "jsj006_responses",
            []
        ):

            url = response.get(
                "url"
            )


            if not url:

                continue


            url_index[
                url
            ].append({

                "race_key":
                    race_key,

                "race_status":
                    race_status,

                "capture_phase":
                    response.get(
                        "capture_phase"
                    ),

                "assigned_race_key":
                    response.get(
                        "assigned_race_key"
                    ),

                "captured_at":
                    response.get(
                        "captured_at"
                    ),

                "status":
                    response.get(
                        "status"
                    ),

                "body_type":
                    response.get(
                        "body_type"
                    ),

            })


    return url_index


# ============================================================
# RACE NO
# ============================================================


def get_race_no(race_key):

    if not isinstance(
        race_key,
        str,
    ):

        return None


    try:

        race_text = race_key.rsplit(
            "_",
            1
        )[-1]


        if not race_text.endswith(
            "R"
        ):

            return None


        return int(
            race_text[:-1]
        )


    except Exception:

        return None


# ============================================================
# VENUE
# ============================================================


def get_venue(race_key):

    if not isinstance(
        race_key,
        str,
    ):

        return None


    parts = race_key.split(
        "_"
    )


    if len(parts) < 3:

        return None


    return parts[-2]


# ============================================================
# 判定
# ============================================================


def judge_duplicate(entries):

    phases = [

        item.get(
            "capture_phase"
        )

        for item in entries

    ]


    race_keys = [

        item.get(
            "race_key"
        )

        for item in entries

    ]


    venue_entries = [

        item

        for item in entries

        if (
            item.get(
                "capture_phase"
            )
            ==
            "VENUE_CLICK_AUTO_FIRST_RACE"
        )

    ]


    race_click_entries = [

        item

        for item in entries

        if (
            item.get(
                "capture_phase"
            )
            ==
            "RACE_CLICK"
        )

    ]


    # ========================================================
    # 仮説完全一致
    # ========================================================


    if (
        venue_entries
        and
        race_click_entries
    ):

        venue_race_keys = sorted({

            item.get(
                "race_key"
            )

            for item in venue_entries

        })


        race_click_race_keys = sorted({

            item.get(
                "race_key"
            )

            for item in race_click_entries

        })


        if (
            set(
                venue_race_keys
            )
            !=
            set(
                race_click_race_keys
            )
        ):

            return {

                "judgement":
                    "VENUE_AUTO_MISASSIGN_CONFIRMED",

                "venue_auto_race_keys":
                    venue_race_keys,

                "race_click_race_keys":
                    race_click_race_keys,

                "recommended_true_race_keys":
                    race_click_race_keys,

            }


        return {

            "judgement":
                "SAME_RACE_MULTI_PHASE",

            "venue_auto_race_keys":
                venue_race_keys,

            "race_click_race_keys":
                race_click_race_keys,

            "recommended_true_race_keys":
                race_click_race_keys,

        }


    # ========================================================
    # RACE CLICKだけ
    # ========================================================


    if (
        race_click_entries
        and
        not venue_entries
    ):

        return {

            "judgement":
                "RACE_CLICK_CROSS_DUPLICATE",

            "venue_auto_race_keys":
                [],

            "race_click_race_keys":
                sorted({

                    item.get(
                        "race_key"
                    )

                    for item in race_click_entries

                }),

            "recommended_true_race_keys":
                [],

        }


    # ========================================================
    # VENUE AUTOだけ
    # ========================================================


    if (
        venue_entries
        and
        not race_click_entries
    ):

        return {

            "judgement":
                "VENUE_AUTO_ONLY_DUPLICATE",

            "venue_auto_race_keys":
                sorted({

                    item.get(
                        "race_key"
                    )

                    for item in venue_entries

                }),

            "race_click_race_keys":
                [],

            "recommended_true_race_keys":
                [],

        }


    return {

        "judgement":
            "UNKNOWN_PHASE_PATTERN",

        "venue_auto_race_keys":
            [],

        "race_click_race_keys":
            [],

        "recommended_true_race_keys":
            [],

    }


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
        "049 048 CROSS_RACE_DUPLICATE_URL capture_phase監査"
    )

    print(
        "="
        * 100
    )

    print()

    print(
        "INPUT:"
    )

    print(
        SRC
    )


    if not SRC.exists():

        print()

        print(
            "ERROR: 048 JSONがありません"
        )

        return


    data = load_json(
        SRC
    )


    races = data.get(
        "races",
        []
    )


    source_duplicates = data.get(
        "cross_race_duplicate_urls",
        []
    )


    url_index = build_url_index(
        races
    )


    print()

    print(
        "SOURCE RACES:",
        len(
            races
        )
    )

    print(
        "SOURCE DUPLICATES:",
        len(
            source_duplicates
        )
    )

    print(
        "INDEX URL COUNT:",
        len(
            url_index
        )
    )


    # ========================================================
    # 重複URL抽出
    # ========================================================


    duplicate_urls = []


    for url, entries in url_index.items():

        race_keys = {

            item.get(
                "race_key"
            )

            for item in entries

        }


        if len(
            race_keys
        ) <= 1:

            continue


        duplicate_urls.append(
            (
                url,
                entries,
            )
        )


    print()

    print(
        "RECALCULATED CROSS DUPLICATES:",
        len(
            duplicate_urls
        )
    )


    # ========================================================
    # 監査
    # ========================================================


    audit_results = []

    judgement_counter = Counter()

    phase_pair_counter = Counter()


    for index, (
        url,
        entries,
    ) in enumerate(
        duplicate_urls,
        start=1,
    ):

        print()

        print(
            "#"
            * 100
        )

        print(
            "DUPLICATE:",
            index
        )

        print(
            "#"
            * 100
        )

        print()

        print(
            "URL:"
        )

        print(
            url
        )


        # ====================================================
        # 時刻順
        # ====================================================


        sorted_entries = sorted(

            entries,

            key=lambda item: (
                item.get(
                    "captured_at"
                )
                or
                ""
            ),

        )


        print()

        print(
            "★ CAPTURE TIMELINE ★"
        )


        for capture_index, item in enumerate(
            sorted_entries,
            start=1,
        ):

            print()

            print(
                "CAPTURE:",
                capture_index
            )

            print(
                "RACE KEY:",
                item.get(
                    "race_key"
                )
            )

            print(
                "ASSIGNED RACE KEY:",
                item.get(
                    "assigned_race_key"
                )
            )

            print(
                "VENUE:",
                get_venue(
                    item.get(
                        "race_key"
                    )
                )
            )

            print(
                "RACE NO:",
                get_race_no(
                    item.get(
                        "race_key"
                    )
                )
            )

            print(
                "PHASE:",
                item.get(
                    "capture_phase"
                )
            )

            print(
                "CAPTURED AT:",
                item.get(
                    "captured_at"
                )
            )

            print(
                "HTTP STATUS:",
                item.get(
                    "status"
                )
            )

            print(
                "BODY TYPE:",
                item.get(
                    "body_type"
                )
            )


        # ====================================================
        # PHASE PAIR
        # ====================================================


        phase_signature = tuple(

            sorted({

                str(
                    item.get(
                        "capture_phase"
                    )
                )

                for item in entries

            })

        )


        phase_pair_counter[
            phase_signature
        ] += 1


        # ====================================================
        # JUDGE
        # ====================================================


        judgement = judge_duplicate(
            entries
        )


        judgement_counter[
            judgement[
                "judgement"
            ]
        ] += 1


        print()

        print(
            "★ JUDGEMENT ★"
        )

        print(
            judgement[
                "judgement"
            ]
        )

        print(
            "VENUE AUTO RACE KEYS:",
            judgement[
                "venue_auto_race_keys"
            ]
        )

        print(
            "RACE CLICK RACE KEYS:",
            judgement[
                "race_click_race_keys"
            ]
        )

        print(
            "RECOMMENDED TRUE RACE KEYS:",
            judgement[
                "recommended_true_race_keys"
            ]
        )


        audit_results.append({

            "url":
                url,

            "entry_count":
                len(
                    entries
                ),

            "race_keys":
                sorted({

                    item.get(
                        "race_key"
                    )

                    for item in entries

                }),

            "capture_phases":
                sorted({

                    str(
                        item.get(
                            "capture_phase"
                        )
                    )

                    for item in entries

                }),

            "timeline":
                sorted_entries,

            "judgement":
                judgement[
                    "judgement"
                ],

            "venue_auto_race_keys":
                judgement[
                    "venue_auto_race_keys"
                ],

            "race_click_race_keys":
                judgement[
                    "race_click_race_keys"
                ],

            "recommended_true_race_keys":
                judgement[
                    "recommended_true_race_keys"
                ],

        })


    # ========================================================
    # 結論判定
    # ========================================================


    confirmed_count = judgement_counter.get(
        "VENUE_AUTO_MISASSIGN_CONFIRMED",
        0
    )


    if (
        duplicate_urls
        and
        confirmed_count
        ==
        len(
            duplicate_urls
        )
    ):

        final_conclusion = (
            "IGNORE_ALL_VENUE_CLICK_AUTO_JSJ006"
        )


    elif confirmed_count > 0:

        final_conclusion = (
            "VENUE_AUTO_MISASSIGN_PARTIALLY_CONFIRMED"
        )


    else:

        final_conclusion = (
            "VENUE_AUTO_MISASSIGN_NOT_CONFIRMED"
        )


    # ========================================================
    # SAVE
    # ========================================================


    output = {

        "program":
            "049_test.py",

        "created_at":
            datetime.now().isoformat(),

        "source_file":
            str(
                SRC
            ),

        "source_target_date":
            data.get(
                "target_date"
            ),

        "source_race_count":
            len(
                races
            ),

        "source_duplicate_count":
            len(
                source_duplicates
            ),

        "recalculated_cross_duplicate_count":
            len(
                duplicate_urls
            ),

        "judgement_summary":
            dict(
                judgement_counter
            ),

        "phase_pair_summary": {

            " + ".join(
                signature
            ):
                count

            for signature, count
            in phase_pair_counter.items()

        },

        "final_conclusion":
            final_conclusion,

        "audits":
            audit_results,

    }


    save_json(
        OUT_FILE,
        output
    )


    # ========================================================
    # FINAL
    # ========================================================


    print()

    print(
        "="
        * 100
    )

    print(
        "049 最終結果"
    )

    print(
        "="
        * 100
    )

    print()

    print(
        "SOURCE DUPLICATES:",
        output[
            "source_duplicate_count"
        ]
    )

    print(
        "RECALCULATED CROSS DUPLICATES:",
        output[
            "recalculated_cross_duplicate_count"
        ]
    )


    print()

    print(
        "★ JUDGEMENT SUMMARY ★"
    )


    if not judgement_counter:

        print(
            "なし"
        )


    for judgement, count in (
        judgement_counter.items()
    ):

        print(
            judgement,
            ":",
            count
        )


    print()

    print(
        "★ PHASE PAIR SUMMARY ★"
    )


    if not phase_pair_counter:

        print(
            "なし"
        )


    for signature, count in (
        phase_pair_counter.items()
    ):

        print(

            " + ".join(
                signature
            ),

            ":",

            count,

        )


    print()

    print(
        "★ DUPLICATE AUDIT ★"
    )


    if not audit_results:

        print(
            "なし"
        )


    for item in audit_results:

        print()

        print(
            "-"
            * 100
        )

        print(
            "RACE KEYS:",
            item[
                "race_keys"
            ]
        )

        print(
            "PHASES:",
            item[
                "capture_phases"
            ]
        )

        print(
            "JUDGEMENT:",
            item[
                "judgement"
            ]
        )

        print(
            "VENUE AUTO:",
            item[
                "venue_auto_race_keys"
            ]
        )

        print(
            "RACE CLICK:",
            item[
                "race_click_race_keys"
            ]
        )

        print(
            "TRUE RACE KEY:",
            item[
                "recommended_true_race_keys"
            ]
        )


    print()

    print(
        "★ FINAL CONCLUSION ★"
    )

    print(
        output[
            "final_conclusion"
        ]
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
        "=== 049 完了 ==="
    )


if __name__ == "__main__":

    main()