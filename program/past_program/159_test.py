import json
import os
import re
from urllib.parse import urlparse, parse_qs


TARGET_DATE = "20260703"

SEARCH_FILES = [
    "155_all_venues_jsj006.json",
    "152_network_json_inventory.json",
    "122_all_venues_jsj012.json",
    "120_2venues_jsj012.json",
    "103_edge_all_races_jsj012.json",
    "097_all_races_jsj012.json",
]

OUTPUT_FILE = "159_jsj006_date_identifier_hunt.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def walk(obj, path="ROOT"):
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}"

            yield current_path, key, value

            yield from walk(
                value,
                current_path,
            )

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            current_path = f"{path}[{index}]"

            yield from walk(
                value,
                current_path,
            )


def value_text(value):
    if isinstance(
        value,
        (dict, list),
    ):
        return ""

    if value is None:
        return ""

    return str(value)


def normalize_date(value):
    text = value_text(value)

    digits = re.sub(
        r"\D",
        "",
        text,
    )

    if len(digits) >= 8:
        return digits[:8]

    return ""


def is_date_like(key, value):
    key_lower = str(key).lower()
    text = value_text(value)

    key_words = [
        "date",
        "kaisai",
        "day",
        "hiduke",
        "ymd",
        "year",
        "month",
    ]

    if any(
        word in key_lower
        for word in key_words
    ):
        return True

    digits = re.sub(
        r"\D",
        "",
        text,
    )

    if re.fullmatch(
        r"20\d{6}",
        digits,
    ):
        return True

    if re.search(
        r"20\d{2}[/-]\d{1,2}[/-]\d{1,2}",
        text,
    ):
        return True

    return False


def is_venue_like(key, value):
    key_lower = str(key).lower()
    text = value_text(value)

    key_words = [
        "venue",
        "jocode",
        "jo_code",
        "joname",
        "kaisai",
        "place",
        "stadium",
    ]

    if any(
        word in key_lower
        for word in key_words
    ):
        return True

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
        "熊本",
    ]

    if any(
        name in text
        for name in venue_names
    ):
        return True

    return False


def is_race_like(key, value):
    key_lower = str(key).lower()

    key_words = [
        "race",
        "raceno",
        "race_no",
        "selraceno",
        "rno",
    ]

    return any(
        word in key_lower
        for word in key_words
    )


def is_identifier_like(key, value):
    key_lower = str(key).lower()

    key_words = [
        "id",
        "code",
        "key",
        "enc",
        "token",
        "param",
        "type",
        "kaisai",
        "race",
        "jo",
    ]

    if not any(
        word in key_lower
        for word in key_words
    ):
        return False

    if isinstance(
        value,
        (dict, list),
    ):
        return False

    return True


def extract_urls(obj):
    urls = []

    url_pattern = re.compile(
        r"https?://[^\s\"'<>]+"
    )

    for path, key, value in walk(obj):
        text = value_text(value)

        if not text:
            continue

        found_urls = url_pattern.findall(
            text
        )

        for url in found_urls:
            urls.append({
                "path": path,
                "key": key,
                "url": url,
            })

    return urls


def analyze_url(item):
    url = item["url"]

    try:
        parsed = urlparse(url)
        query = parse_qs(
            parsed.query
        )

    except Exception:
        query = {}

    return {
        "path": item["path"],
        "url": url,
        "is_jsj006":
            "JSJ006" in url.upper(),

        "query": query,
    }


def main():
    print("=" * 70)
    print("🔥 159 JSJ006 日付・開催識別子 徹底探索")
    print("=" * 70)

    existing_files = [
        file_name
        for file_name in SEARCH_FILES
        if os.path.exists(file_name)
    ]

    print()
    print("🔥 探索対象JSON")
    print(
        "対象数:",
        len(existing_files),
    )

    for file_name in existing_files:
        print(
            "-",
            file_name,
        )

    all_results = {}

    global_date_hits = []
    global_venue_hits = []
    global_race_hits = []
    global_identifier_hits = []
    global_urls = []

    for file_name in existing_files:

        print()
        print("=" * 70)
        print(
            f"🔥 探索開始: {file_name}"
        )
        print("=" * 70)

        try:
            data = load_json(
                file_name
            )

        except Exception as e:
            print(
                "❌ 読込失敗:",
                e,
            )
            continue

        date_hits = []
        venue_hits = []
        race_hits = []
        identifier_hits = []

        for path, key, value in walk(data):

            text = value_text(value)

            if is_date_like(
                key,
                value,
            ):
                date_hits.append({
                    "file": file_name,
                    "path": path,
                    "key": key,
                    "value": text,
                    "normalized_date":
                        normalize_date(value),
                })

            if is_venue_like(
                key,
                value,
            ):
                venue_hits.append({
                    "file": file_name,
                    "path": path,
                    "key": key,
                    "value": text,
                })

            if is_race_like(
                key,
                value,
            ):
                race_hits.append({
                    "file": file_name,
                    "path": path,
                    "key": key,
                    "value": text,
                })

            if is_identifier_like(
                key,
                value,
            ):
                identifier_hits.append({
                    "file": file_name,
                    "path": path,
                    "key": key,
                    "value": text,
                })

        urls = [
            analyze_url(item)
            for item in extract_urls(data)
        ]

        all_results[file_name] = {
            "date_hits": date_hits,
            "venue_hits": venue_hits,
            "race_hits": race_hits,
            "identifier_hits":
                identifier_hits,
            "urls": urls,
        }

        global_date_hits.extend(
            date_hits
        )
        global_venue_hits.extend(
            venue_hits
        )
        global_race_hits.extend(
            race_hits
        )
        global_identifier_hits.extend(
            identifier_hits
        )
        global_urls.extend(
            urls
        )

        print(
            "日付候補:",
            len(date_hits),
        )
        print(
            "開催場候補:",
            len(venue_hits),
        )
        print(
            "レース候補:",
            len(race_hits),
        )
        print(
            "識別子候補:",
            len(identifier_hits),
        )
        print(
            "URL候補:",
            len(urls),
        )

    print()
    print("=" * 70)
    print("🔥 TARGET DATE 完全一致候補")
    print("=" * 70)

    target_hits = []

    for item in global_date_hits:
        if (
            item["normalized_date"]
            == TARGET_DATE
        ):
            target_hits.append(item)

    print(
        "20260703一致件数:",
        len(target_hits),
    )

    for item in target_hits[:50]:
        print()
        print(
            "FILE :",
            item["file"],
        )
        print(
            "PATH :",
            item["path"],
        )
        print(
            "KEY  :",
            item["key"],
        )
        print(
            "VALUE:",
            item["value"],
        )

    print()
    print("=" * 70)
    print("🔥 JSJ006 URL候補")
    print("=" * 70)

    jsj006_urls = []

    seen_urls = set()

    for item in global_urls:
        if not item["is_jsj006"]:
            continue

        url = item["url"]

        if url in seen_urls:
            continue

        seen_urls.add(url)
        jsj006_urls.append(item)

    print(
        "JSJ006 URL数:",
        len(jsj006_urls),
    )

    for index, item in enumerate(
        jsj006_urls[:50],
        start=1,
    ):
        print()
        print(
            f"🔥 JSJ006 URL #{index}"
        )
        print(
            "PATH:",
            item["path"],
        )
        print(
            "URL :",
            item["url"],
        )
        print(
            "QUERY:"
        )

        print(
            json.dumps(
                item["query"],
                ensure_ascii=False,
                indent=2,
            )
        )

    print()
    print("=" * 70)
    print("🔥 日付KEY種類")
    print("=" * 70)

    date_key_summary = {}

    for item in global_date_hits:
        key = item["key"]

        date_key_summary.setdefault(
            key,
            set(),
        ).add(
            item["value"]
        )

    sorted_date_keys = sorted(
        date_key_summary.items(),
        key=lambda x: len(x[1]),
        reverse=True,
    )

    for key, values in sorted_date_keys[:50]:
        sample = list(values)[:10]

        print()
        print(
            "KEY:",
            key,
        )
        print(
            "VALUE種類数:",
            len(values),
        )
        print(
            "SAMPLE:",
            sample,
        )

    print()
    print("=" * 70)
    print("🔥 開催場識別KEY種類")
    print("=" * 70)

    venue_key_summary = {}

    for item in global_venue_hits:
        key = item["key"]

        venue_key_summary.setdefault(
            key,
            set(),
        ).add(
            item["value"]
        )

    sorted_venue_keys = sorted(
        venue_key_summary.items(),
        key=lambda x: len(x[1]),
        reverse=True,
    )

    for key, values in sorted_venue_keys[:50]:
        sample = list(values)[:15]

        print()
        print(
            "KEY:",
            key,
        )
        print(
            "VALUE種類数:",
            len(values),
        )
        print(
            "SAMPLE:",
            sample,
        )

    output = {
        "target_date": TARGET_DATE,

        "summary": {
            "searched_files":
                len(existing_files),

            "target_date_hits":
                len(target_hits),

            "jsj006_unique_urls":
                len(jsj006_urls),

            "date_hits":
                len(global_date_hits),

            "venue_hits":
                len(global_venue_hits),

            "race_hits":
                len(global_race_hits),

            "identifier_hits":
                len(global_identifier_hits),
        },

        "target_date_hits":
            target_hits,

        "jsj006_urls":
            jsj006_urls,

        "date_key_summary": {
            key: list(values)
            for key, values
            in date_key_summary.items()
        },

        "venue_key_summary": {
            key: list(values)
            for key, values
            in venue_key_summary.items()
        },

        "files":
            all_results,
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 70)
    print("🔥 159テスト終了")
    print("=" * 70)
    print(
        "探索JSON数:",
        len(existing_files),
    )
    print(
        "20260703一致件数:",
        len(target_hits),
    )
    print(
        "JSJ006 URL数:",
        len(jsj006_urls),
    )
    print()
    print(
        f"保存先: {OUTPUT_FILE}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()