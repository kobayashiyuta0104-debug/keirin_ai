import json
import re
from collections import Counter


VENUES = [
    "函館", "青森", "いわき平", "弥彦", "前橋",
    "取手", "宇都宮", "大宮", "西武園", "京王閣",
    "立川", "松戸", "千葉", "川崎", "平塚",
    "小田原", "伊東", "静岡", "名古屋", "岐阜",
    "大垣", "豊橋", "富山", "松阪", "四日市",
    "福井", "奈良", "向日町", "和歌山", "岸和田",
    "玉野", "広島", "防府", "高松", "小松島",
    "高知", "松山", "小倉", "久留米", "武雄",
    "佐世保", "別府", "熊本"
]


def text(value):
    if value is None:
        return ""

    return str(value).strip()


def date_score(value):

    value = text(value)

    score = 0
    reasons = []

    patterns = [
        r"^20\d{6}$",
        r"^20\d{2}/\d{1,2}/\d{1,2}$",
        r"^20\d{2}-\d{1,2}-\d{1,2}$",
        r"^20\d{2}\.\d{1,2}\.\d{1,2}$",
        r"^20\d{2}年\d{1,2}月\d{1,2}日$",
    ]

    for pattern in patterns:

        if re.fullmatch(pattern, value):
            score += 1000
            reasons.append("開催日形式")
            break

    if re.search(
        r"20\d{2}[/\-\.年]\d{1,2}",
        value
    ):
        score += 100
        reasons.append("年月あり")

    if "更新" in value:
        score -= 1000
        reasons.append("更新日時ペナルティ")

    if "&nbsp;" in value:
        score -= 300
        reasons.append("HTML文字ペナルティ")

    if ":" in value:
        score -= 100
        reasons.append("時刻ペナルティ")

    return score, reasons


def venue_score(value):

    value = text(value)

    score = 0
    reasons = []

    if value in VENUES:
        score += 1000
        reasons.append("競輪場名完全一致")

    for venue in VENUES:

        if venue in value:
            score += 100
            reasons.append(
                f"競輪場名含有:{venue}"
            )
            break

    if len(value) <= 5:
        score += 20
        reasons.append("短文字列")

    return score, reasons


def race_no_score(value):

    value = text(value)

    score = 0
    reasons = []

    if re.fullmatch(
        r"(?:[1-9]|1[0-2])",
        value
    ):
        score += 1000
        reasons.append("1〜12完全一致")

    if re.fullmatch(
        r"(?:[1-9]|1[0-2])R",
        value,
        re.IGNORECASE
    ):
        score += 900
        reasons.append("1R〜12R形式")

    if "race" in value.lower():
        score += 20
        reasons.append("race文字あり")

    return score, reasons


def url_prm_score(value):

    value = text(value)

    score = 0
    reasons = []

    if len(value) >= 20:
        score += 100
        reasons.append("長文字列")

    if re.fullmatch(
        r"[A-Za-z0-9_\-]+",
        value
    ):
        score += 100
        reasons.append("URL安全文字")

    if len(set(value)) >= 10:
        score += 50
        reasons.append("文字種類多い")

    return score, reasons


def main():

    print("=== 134 VALUE形状判定テスト ===")

    input_file = "132_category_candidates.json"
    output_file = "134_value_shape_rankings.json"

    categories = [
        "DATE_VALUE",
        "VENUE_VALUE",
        "RACE_NO_KEY",
        "RACE_NO_VALUE",
        "RACE_URL_PRM",
    ]

    try:

        with open(
            input_file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

    except Exception as e:

        print(
            "❌ JSON読込失敗:",
            e
        )

        return

    result = {}

    for category in categories:

        print()
        print("=" * 70)
        print(
            "🔥🔥🔥 CATEGORY:",
            category
        )
        print("=" * 70)

        items = data.get(
            category,
            {}
        ).get(
            "items",
            []
        )

        rankings = []

        for item in items:

            if not isinstance(item, dict):
                continue

            value = item.get("value")

            if category == "DATE_VALUE":

                score, reasons = date_score(
                    value
                )

            elif category == "VENUE_VALUE":

                score, reasons = venue_score(
                    value
                )

            elif category in [
                "RACE_NO_KEY",
                "RACE_NO_VALUE",
            ]:

                score, reasons = race_no_score(
                    value
                )

            elif category == "RACE_URL_PRM":

                score, reasons = url_prm_score(
                    value
                )

            else:

                score = 0
                reasons = []

            rankings.append({
                "score": score,
                "file": item.get("file"),
                "path": item.get("path"),
                "key": item.get("key"),
                "value": value,
                "reasons": reasons,
            })

        rankings.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        positive_count = sum(
            1
            for item in rankings
            if item["score"] > 0
        )

        print(
            "総候補数:",
            len(rankings)
        )

        print(
            "正スコア数:",
            positive_count
        )

        print()
        print("🔥 TOP20")

        for index, item in enumerate(
            rankings[:20],
            start=1
        ):

            print()
            print("-" * 70)

            print(
                f"🔥 候補 #{index}"
            )

            print(
                "SCORE:",
                item["score"]
            )

            print(
                "FILE:",
                item["file"]
            )

            print(
                "KEY:",
                repr(item["key"])
            )

            print(
                "PATH:",
                item["path"]
            )

            print(
                "VALUE:",
                repr(item["value"])
            )

            print(
                "理由:",
                item["reasons"]
            )

        key_counter = Counter(
            item["key"]
            for item in rankings
            if item["score"] > 0
        )

        path_counter = Counter(
            item["path"]
            for item in rankings
            if item["score"] > 0
        )

        result[category] = {
            "total_count": len(rankings),
            "positive_count": positive_count,
            "key_top": key_counter.most_common(),
            "path_top": path_counter.most_common(),
            "rankings": rankings,
        }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print()
    print("=" * 70)
    print("🔥 134テスト終了")
    print("=" * 70)

    for category in categories:

        category_result = result.get(
            category,
            {}
        )

        rankings = category_result.get(
            "rankings",
            []
        )

        positive_rankings = [
            item
            for item in rankings
            if item["score"] > 0
        ]

        print()
        print("🔥", category)

        print(
            "総候補数:",
            category_result.get(
                "total_count",
                0
            )
        )

        print(
            "正スコア数:",
            category_result.get(
                "positive_count",
                0
            )
        )

        if positive_rankings:

            top = positive_rankings[0]

            print(
                "TOP SCORE:",
                top["score"]
            )

            print(
                "TOP FILE:",
                top["file"]
            )

            print(
                "TOP KEY:",
                repr(top["key"])
            )

            print(
                "TOP PATH:",
                top["path"]
            )

            print(
                "TOP VALUE:",
                repr(top["value"])
            )

            print(
                "TOP 理由:",
                top["reasons"]
            )

        else:

            print(
                "❌ 正スコア候補なし"
            )

    print()
    print(
        "保存先:",
        output_file
    )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()