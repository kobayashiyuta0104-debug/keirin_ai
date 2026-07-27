from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import json
import re


# ============================================================
# 047
#
# JSJ006 JSON 自己識別項目調査
#
# 046で保存したJSJ006レスポンスJSONを調査
#
# 目的:
#
# ・開催名候補
# ・レース番号候補
# ・日付候補
# ・race / jo / venue / place 系キー
# ・C0201race 系
#
# をレスポンスJSON自身から抽出する
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
    / "046_jsj006_by_race_key"
    / "046_jsj006_by_race_key.json"
)


OUT_DIR = (
    BASE
    / "data_official"
    / "pre_race"
    / "047_jsj006_identity_research"
)


OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUT_FILE = (
    OUT_DIR
    / "047_jsj006_identity_research.json"
)


# ============================================================
# 調査キーワード
# ============================================================


KEYWORDS = {

    "race",
    "raceno",
    "race_no",
    "racenumber",
    "race_number",

    "jo",
    "joname",
    "jo_name",

    "venue",
    "venuename",
    "venue_name",

    "place",
    "placename",
    "place_name",

    "date",
    "racedate",
    "race_date",

    "kaisai",
    "kaisainame",
    "kaisai_name",

    "jocode",
    "jo_code",

    "c0201race",

}


VENUE_NAMES = [

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
    "熊本",

]


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
# 値を短く表示
# ============================================================


def short_value(value, max_length=300):

    try:

        text = json.dumps(
            value,
            ensure_ascii=False,
        )

    except Exception:

        text = repr(
            value
        )


    if len(text) > max_length:

        return (
            text[:max_length]
            +
            "..."
        )


    return text


# ============================================================
# キー正規化
# ============================================================


def normalize_key(key):

    return re.sub(
        r"[^a-z0-9]",
        "",
        str(
            key
        ).lower(),
    )


# ============================================================
# キーが怪しいか
# ============================================================


def is_identity_key(key):

    normalized = normalize_key(
        key
    )


    for keyword in KEYWORDS:

        keyword_normalized = (
            normalize_key(
                keyword
            )
        )


        if (
            keyword_normalized
            in
            normalized
        ):

            return True


    return False


# ============================================================
# JSON再帰探索
# ============================================================


def research_json(
    obj,
    path="$",
    identity_fields=None,
    venue_hits=None,
    date_hits=None,
    race_number_hits=None,
):

    if identity_fields is None:

        identity_fields = []


    if venue_hits is None:

        venue_hits = []


    if date_hits is None:

        date_hits = []


    if race_number_hits is None:

        race_number_hits = []


    if isinstance(
        obj,
        dict,
    ):

        for key, value in obj.items():

            child_path = (
                f"{path}.{key}"
            )


            # =================================================
            # KEY候補
            # =================================================


            if is_identity_key(
                key
            ):

                identity_fields.append({

                    "path":
                        child_path,

                    "key":
                        str(
                            key
                        ),

                    "value":
                        value,

                    "value_preview":
                        short_value(
                            value
                        ),

                })


            # =================================================
            # 値TEXT調査
            # =================================================


            if isinstance(
                value,
                (
                    str,
                    int,
                    float,
                ),
            ):

                text = str(
                    value
                )


                # ---------------------------------------------
                # 開催名
                # ---------------------------------------------


                for venue in VENUE_NAMES:

                    if venue in text:

                        venue_hits.append({

                            "path":
                                child_path,

                            "key":
                                str(
                                    key
                                ),

                            "venue":
                                venue,

                            "value":
                                value,

                        })


                # ---------------------------------------------
                # YYYYMMDD
                # ---------------------------------------------


                date_matches = re.findall(
                    r"20\d{6}",
                    re.sub(
                        r"\D",
                        "",
                        text,
                    ),
                )


                for date_value in date_matches:

                    date_hits.append({

                        "path":
                            child_path,

                        "key":
                            str(
                                key
                            ),

                        "date":
                            date_value,

                        "value":
                            value,

                    })


                # ---------------------------------------------
                # race系KEYの数字
                # ---------------------------------------------


                normalized_key = (
                    normalize_key(
                        key
                    )
                )


                if (
                    "race"
                    in
                    normalized_key
                ):

                    number_match = re.search(
                        r"\d{1,2}",
                        text,
                    )


                    if number_match:

                        race_number_hits.append({

                            "path":
                                child_path,

                            "key":
                                str(
                                    key
                                ),

                            "race_number":
                                int(
                                    number_match.group(0)
                                ),

                            "value":
                                value,

                        })


            research_json(

                value,

                child_path,

                identity_fields,

                venue_hits,

                date_hits,

                race_number_hits,

            )


    elif isinstance(
        obj,
        list,
    ):

        for index, value in enumerate(
            obj
        ):

            child_path = (
                f"{path}[{index}]"
            )


            research_json(

                value,

                child_path,

                identity_fields,

                venue_hits,

                date_hits,

                race_number_hits,

            )


    return {

        "identity_fields":
            identity_fields,

        "venue_hits":
            venue_hits,

        "date_hits":
            date_hits,

        "race_number_hits":
            race_number_hits,

    }


# ============================================================
# 重複簡易除去
# ============================================================


def unique_records(
    records,
    keys,
):

    results = []

    seen = set()


    for record in records:

        signature = tuple(

            str(
                record.get(
                    key
                )
            )

            for key in keys

        )


        if signature in seen:

            continue


        seen.add(
            signature
        )


        results.append(
            record
        )


    return results


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
        "047 JSJ006 JSON 自己識別項目調査"
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
            "ERROR: 046 JSONがありません"
        )

        return


    data = load_json(
        SRC
    )


    races = data.get(
        "races",
        []
    )


    found_races = [

        race

        for race in races

        if (
            race.get(
                "status"
            )
            ==
            "JSJ006_FOUND"
        )

    ]


    print()

    print(
        "046 RACES:",
        len(
            races
        )
    )

    print(
        "JSJ006 FOUND RACES:",
        len(
            found_races
        )
    )


    # ========================================================
    # 全レスポンス調査
    # ========================================================


    results = []

    key_counter = Counter()

    path_counter = Counter()

    venue_counter = Counter()

    date_counter = Counter()

    race_number_counter = Counter()


    response_counter = 0


    for race in found_races:

        clicked_race_key = race.get(
            "race_key"
        )


        for response in race.get(
            "jsj006_responses",
            []
        ):

            response_counter += 1


            print()

            print(
                "-"
                * 100
            )

            print(
                "RESPONSE:",
                response_counter
            )

            print(
                "CLICKED RACE KEY:",
                clicked_race_key
            )


            body = response.get(
                "json"
            )


            if body is None:

                result = {

                    "clicked_race_key":
                        clicked_race_key,

                    "url":
                        response.get(
                            "url"
                        ),

                    "status":
                        "JSON_BODY_NONE",

                    "identity_fields":
                        [],

                    "venue_hits":
                        [],

                    "date_hits":
                        [],

                    "race_number_hits":
                        [],

                }


                results.append(
                    result
                )


                print(
                    "STATUS: JSON_BODY_NONE"
                )


                continue


            research = research_json(
                body
            )


            identity_fields = unique_records(

                research[
                    "identity_fields"
                ],

                [
                    "path",
                    "key",
                    "value_preview",
                ],

            )


            venue_hits = unique_records(

                research[
                    "venue_hits"
                ],

                [
                    "path",
                    "venue",
                    "value",
                ],

            )


            date_hits = unique_records(

                research[
                    "date_hits"
                ],

                [
                    "path",
                    "date",
                    "value",
                ],

            )


            race_number_hits = unique_records(

                research[
                    "race_number_hits"
                ],

                [
                    "path",
                    "race_number",
                    "value",
                ],

            )


            # =================================================
            # 集計
            # =================================================


            for item in identity_fields:

                key_counter[
                    item.get(
                        "key"
                    )
                ] += 1


                path_counter[
                    item.get(
                        "path"
                    )
                ] += 1


            for item in venue_hits:

                venue_counter[
                    item.get(
                        "venue"
                    )
                ] += 1


            for item in date_hits:

                date_counter[
                    item.get(
                        "date"
                    )
                ] += 1


            for item in race_number_hits:

                race_number_counter[
                    item.get(
                        "race_number"
                    )
                ] += 1


            result = {

                "clicked_race_key":
                    clicked_race_key,

                "url":
                    response.get(
                        "url"
                    ),

                "status":
                    "RESEARCHED",

                "identity_field_count":
                    len(
                        identity_fields
                    ),

                "venue_hit_count":
                    len(
                        venue_hits
                    ),

                "date_hit_count":
                    len(
                        date_hits
                    ),

                "race_number_hit_count":
                    len(
                        race_number_hits
                    ),

                "identity_fields":
                    identity_fields,

                "venue_hits":
                    venue_hits,

                "date_hits":
                    date_hits,

                "race_number_hits":
                    race_number_hits,

            }


            results.append(
                result
            )


            print(
                "IDENTITY FIELDS:",
                len(
                    identity_fields
                )
            )

            print(
                "VENUE HITS:",
                len(
                    venue_hits
                )
            )

            print(
                "DATE HITS:",
                len(
                    date_hits
                )
            )

            print(
                "RACE NUMBER HITS:",
                len(
                    race_number_hits
                )
            )


            print()

            print(
                "VENUE:"
            )


            if not venue_hits:

                print(
                    "  なし"
                )


            for item in venue_hits[:10]:

                print(

                    " ",

                    item.get(
                        "path"
                    ),

                    "=>",

                    item.get(
                        "venue"
                    ),

                    "/",

                    item.get(
                        "value"
                    ),

                )


            print()

            print(
                "DATE:"
            )


            if not date_hits:

                print(
                    "  なし"
                )


            for item in date_hits[:10]:

                print(

                    " ",

                    item.get(
                        "path"
                    ),

                    "=>",

                    item.get(
                        "date"
                    ),

                    "/",

                    item.get(
                        "value"
                    ),

                )


            print()

            print(
                "RACE NUMBER:"
            )


            if not race_number_hits:

                print(
                    "  なし"
                )


            for item in race_number_hits[:20]:

                print(

                    " ",

                    item.get(
                        "path"
                    ),

                    "KEY:",

                    item.get(
                        "key"
                    ),

                    "=>",

                    item.get(
                        "race_number"
                    ),

                    "/",

                    item.get(
                        "value"
                    ),

                )


            print()

            print(
                "IDENTITY FIELD TOP30:"
            )


            if not identity_fields:

                print(
                    "  なし"
                )


            for item in identity_fields[:30]:

                print()

                print(
                    " PATH:",
                    item.get(
                        "path"
                    )
                )

                print(
                    " KEY:",
                    item.get(
                        "key"
                    )
                )

                print(
                    " VALUE:",
                    item.get(
                        "value_preview"
                    )
                )


    # ========================================================
    # 保存
    # ========================================================


    output = {

        "program":
            "047_test.py",

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

        "found_race_count":
            len(
                found_races
            ),

        "response_count":
            response_counter,

        "summary": {

            "identity_keys":
                dict(
                    key_counter.most_common()
                ),

            "identity_paths":
                dict(
                    path_counter.most_common()
                ),

            "venue_hits":
                dict(
                    venue_counter.most_common()
                ),

            "date_hits":
                dict(
                    date_counter.most_common()
                ),

            "race_number_hits":
                {

                    str(key):
                        value

                    for key, value
                    in race_number_counter.most_common()

                },

        },

        "responses":
            results,

    }


    save_json(
        OUT_FILE,
        output,
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
        "047 最終結果"
    )

    print(
        "#"
        * 100
    )

    print()

    print(
        "FOUND RACES:",
        output[
            "found_race_count"
        ]
    )

    print(
        "RESPONSE COUNT:",
        output[
            "response_count"
        ]
    )


    print()

    print(
        "★ IDENTITY KEY TOP50 ★"
    )


    for key, count in (
        key_counter.most_common(
            50
        )
    ):

        print(
            key,
            ":",
            count
        )


    print()

    print(
        "★ VENUE HIT ★"
    )


    if not venue_counter:

        print(
            "なし"
        )


    for key, count in (
        venue_counter.most_common()
    ):

        print(
            key,
            ":",
            count
        )


    print()

    print(
        "★ DATE HIT ★"
    )


    if not date_counter:

        print(
            "なし"
        )


    for key, count in (
        date_counter.most_common()
    ):

        print(
            key,
            ":",
            count
        )


    print()

    print(
        "★ RACE NUMBER HIT ★"
    )


    if not race_number_counter:

        print(
            "なし"
        )


    for key, count in (
        race_number_counter.most_common()
    ):

        print(
            key,
            ":",
            count
        )


    print()

    print(
        "★ RESPONSE SAMPLE TOP10 ★"
    )


    for item in results[:10]:

        print()

        print(
            item.get(
                "clicked_race_key"
            )
        )

        print(
            "STATUS:",
            item.get(
                "status"
            )
        )

        print(
            "VENUE HITS:",
            item.get(
                "venue_hit_count",
                0
            )
        )

        print(
            "DATE HITS:",
            item.get(
                "date_hit_count",
                0
            )
        )

        print(
            "RACE NUMBER HITS:",
            item.get(
                "race_number_hit_count",
                0
            )
        )


        print(
            "VENUE VALUES:",
            [

                hit.get(
                    "venue"
                )

                for hit in item.get(
                    "venue_hits",
                    []
                )

            ]
        )


        print(
            "DATE VALUES:",
            [

                hit.get(
                    "date"
                )

                for hit in item.get(
                    "date_hits",
                    []
                )

            ]
        )


        print(
            "RACE NUMBER VALUES:",
            [

                hit.get(
                    "race_number"
                )

                for hit in item.get(
                    "race_number_hits",
                    []
                )

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
        "=== 047 完了 ==="
    )


if __name__ == "__main__":

    main()