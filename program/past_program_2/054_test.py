from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import json
import re


# ============================================================
# 054
#
# TRUE CONFIRMED RESULT SOURCE RESEARCH
#
# 目的:
#
# 20260710 の本物の当該レース確定結果ファイルを探す
#
# JSJ006内の
# 選手過去成績 raceResult1Syaban / raceResult2Syaban
# を当該レース結果と誤認しない
#
# 探すもの:
#
# ・race_key
# ・当該レース着順
# ・1着 / 2着 / 3着車番
# ・3連単組番
# ・3連単払戻
# ・rcvRefund
# ・rcvOdds
# ・tyakujyunItemSubData
# ・confirmed_result
#
# Edge不要
# サイトアクセスなし
#
# ============================================================


BASE = Path(r"C:\競輪AI")

TARGET_DATE = "20260710"


OUT_DIR = (
    BASE
    / "data_ai"
    / "merge_research"
    / "054_true_result_source_research"
)

OUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUT_FILE = (
    OUT_DIR
    / "054_true_result_source_research.json"
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


def safe_load_json(path):

    try:

        return load_json(path)

    except Exception:

        return None


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


    match = RACE_KEY_PATTERN.fullmatch(text)


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
# PATH SKIP
# ============================================================


SKIP_DIR_NAMES = {
    "__pycache__",
    ".git",
    ".vscode",
    "node_modules",
}


SKIP_FILE_NAMES = {
    OUT_FILE.name,
}


def should_skip_path(path):

    for part in path.parts:

        if part in SKIP_DIR_NAMES:

            return True


    if path.name in SKIP_FILE_NAMES:

        return True


    return False


# ============================================================
# RECURSIVE WALK
# ============================================================


def walk_json(
    value,
    path="root",
    depth=0,
):

    if depth > 40:

        return


    if isinstance(value, dict):

        yield {
            "path": path,
            "key": None,
            "value": value,
            "value_type": "dict",
        }


        for key, child in value.items():

            child_path = (
                f"{path}.{key}"
            )


            yield {
                "path": child_path,
                "key": str(key),
                "value": child,
                "value_type": type(child).__name__,
            }


            yield from walk_json(
                child,
                child_path,
                depth + 1,
            )


    elif isinstance(value, list):

        yield {
            "path": path,
            "key": None,
            "value": value,
            "value_type": "list",
        }


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
# RACE KEY EXTRACT
# ============================================================


def extract_target_race_keys(data):

    found = set()


    for item in walk_json(data):

        key = item.get("key")
        value = item.get("value")


        if key == "race_key":

            parsed = parse_race_key(value)


            if (
                parsed
                and parsed.get("date") == TARGET_DATE
            ):

                found.add(
                    parsed.get("race_key")
                )


        if isinstance(value, str):

            parsed = parse_race_key(value)


            if (
                parsed
                and parsed.get("date") == TARGET_DATE
            ):

                found.add(
                    parsed.get("race_key")
                )


    return sorted(found)


# ============================================================
# RESULT KEY GROUPS
# ============================================================


PAYOUT_KEYS = {
    "rcvRefund",
    "refund",
    "refundAmount",
    "haraimodoshi",
    "payout",
    "payoff",
}


ODDS_KEYS = {
    "rcvOdds",
    "odds",
}


FINISH_KEYS = {
    "tyakujyunItemSubData",
    "tyakujyun",
    "chakujun",
    "finishOrder",
    "finish_order",
    "rank",
    "arrival",
}


CONFIRMED_KEYS = {
    "confirmed_result",
    "confirmedResult",
    "official_result",
    "officialResult",
}


BET_KEYS = {
    "sanrentan",
    "sanrentanResult",
    "trifecta",
    "betType",
    "kumi",
    "kumiban",
    "combination",
}


RESULT_CONTAINER_KEYS = {
    "C0201race",
    "rcvRefund",
    "tyakujyunItemSubData",
    "raceResult",
    "result",
    "results",
    "confirmed_result",
}


FALSE_POSITIVE_KEYS = {
    "raceResult1Syaban",
    "raceResult2Syaban",
}


def normalized(text):

    return str(text).lower()


def exact_or_contains(
    key,
    keywords,
):

    if key is None:

        return False


    key_text = normalized(key)


    for keyword in keywords:

        keyword_text = normalized(keyword)


        if (
            key_text == keyword_text
            or keyword_text in key_text
        ):

            return True


    return False


# ============================================================
# RESULT EVIDENCE
# ============================================================


def research_result_evidence(data):

    counters = {
        "payout": 0,
        "odds": 0,
        "finish": 0,
        "confirmed": 0,
        "bet": 0,
        "result_container": 0,
        "false_positive": 0,
    }


    hit_keys = {
        "payout": set(),
        "odds": set(),
        "finish": set(),
        "confirmed": set(),
        "bet": set(),
        "result_container": set(),
        "false_positive": set(),
    }


    samples = {
        "payout": [],
        "odds": [],
        "finish": [],
        "confirmed": [],
        "bet": [],
        "result_container": [],
        "false_positive": [],
    }


    for item in walk_json(data):

        key = item.get("key")
        value = item.get("value")
        path = item.get("path")


        checks = [
            (
                "payout",
                PAYOUT_KEYS,
            ),
            (
                "odds",
                ODDS_KEYS,
            ),
            (
                "finish",
                FINISH_KEYS,
            ),
            (
                "confirmed",
                CONFIRMED_KEYS,
            ),
            (
                "bet",
                BET_KEYS,
            ),
            (
                "result_container",
                RESULT_CONTAINER_KEYS,
            ),
            (
                "false_positive",
                FALSE_POSITIVE_KEYS,
            ),
        ]


        for category, keywords in checks:

            if not exact_or_contains(
                key,
                keywords,
            ):

                continue


            counters[category] += 1

            hit_keys[category].add(
                str(key)
            )


            if len(samples[category]) < 20:

                sample_value = value


                if isinstance(
                    sample_value,
                    (dict, list),
                ):

                    try:

                        sample_value = json.dumps(
                            sample_value,
                            ensure_ascii=False,
                        )[:1000]

                    except Exception:

                        sample_value = str(
                            sample_value
                        )[:1000]


                else:

                    sample_value = str(
                        sample_value
                    )[:1000]


                samples[category].append({
                    "path": path,
                    "key": key,
                    "value_sample": sample_value,
                })


    return {
        "counters": counters,
        "hit_keys": {
            key: sorted(values)
            for key, values in hit_keys.items()
        },
        "samples": samples,
    }


# ============================================================
# TRUE RESULT SCORE
# ============================================================


def calculate_true_result_score(
    counters,
):

    score = 0


    # 払戻は非常に強い証拠

    score += (
        counters.get("payout", 0)
        * 20
    )


    # 着順構造も強い証拠

    score += (
        counters.get("finish", 0)
        * 15
    )


    # confirmed_result

    score += (
        counters.get("confirmed", 0)
        * 20
    )


    # 3連単等

    score += (
        counters.get("bet", 0)
        * 8
    )


    # odds

    score += (
        counters.get("odds", 0)
        * 3
    )


    # 結果コンテナ

    score += (
        counters.get(
            "result_container",
            0,
        )
        * 5
    )


    # JSJ006過去成績誤検出は減点

    score -= (
        counters.get(
            "false_positive",
            0,
        )
        * 10
    )


    return score


# ============================================================
# JUDGEMENT
# ============================================================


def judge_candidate(
    counters,
):

    payout = counters.get(
        "payout",
        0,
    )

    finish = counters.get(
        "finish",
        0,
    )

    confirmed = counters.get(
        "confirmed",
        0,
    )

    bet = counters.get(
        "bet",
        0,
    )

    false_positive = counters.get(
        "false_positive",
        0,
    )


    if (
        payout > 0
        and finish > 0
    ):

        return (
            "STRONG_TRUE_RESULT_CANDIDATE"
        )


    if (
        confirmed > 0
        and (
            payout > 0
            or finish > 0
        )
    ):

        return (
            "STRONG_TRUE_RESULT_CANDIDATE"
        )


    if (
        payout > 0
        and bet > 0
    ):

        return (
            "TRUE_RESULT_CANDIDATE"
        )


    if (
        finish > 0
        and bet > 0
    ):

        return (
            "TRUE_RESULT_CANDIDATE"
        )


    if (
        false_positive > 0
        and payout == 0
        and finish == 0
        and confirmed == 0
    ):

        return (
            "LIKELY_JSJ006_PAST_RESULT"
        )


    return (
        "WEAK_OR_UNKNOWN"
    )


# ============================================================
# MAIN
# ============================================================


def main():

    print()

    print(
        "=" * 100
    )

    print(
        "054 TRUE CONFIRMED RESULT SOURCE RESEARCH"
    )

    print(
        "=" * 100
    )

    print()

    print(
        "TARGET DATE:",
        TARGET_DATE,
    )


    # ========================================================
    # JSON SCAN
    # ========================================================


    json_files = []


    for path in BASE.rglob("*.json"):

        if should_skip_path(path):

            continue


        json_files.append(path)


    print()

    print(
        "JSON FILES:",
        len(json_files),
    )


    candidates = []

    load_error_count = 0

    target_date_file_count = 0


    judgement_counter = Counter()


    for file_index, path in enumerate(
        json_files,
        start=1,
    ):

        if (
            file_index == 1
            or file_index % 100 == 0
            or file_index == len(json_files)
        ):

            print(
                f"[SCAN] "
                f"{file_index}"
                f"/"
                f"{len(json_files)} "
                f"{path.name}"
            )


        data = safe_load_json(path)


        if data is None:

            load_error_count += 1

            continue


        race_keys = extract_target_race_keys(
            data
        )


        if not race_keys:

            continue


        target_date_file_count += 1


        evidence = research_result_evidence(
            data
        )


        counters = evidence.get(
            "counters",
            {},
        )


        score = calculate_true_result_score(
            counters
        )


        judgement = judge_candidate(
            counters
        )


        judgement_counter[
            judgement
        ] += 1


        candidates.append({
            "file": str(path),
            "file_name": path.name,
            "race_key_count": len(race_keys),
            "race_keys": race_keys,
            "true_result_score": score,
            "judgement": judgement,
            "evidence_counters": counters,
            "evidence_hit_keys": evidence.get(
                "hit_keys",
                {},
            ),
            "evidence_samples": evidence.get(
                "samples",
                {},
            ),
        })


    # ========================================================
    # SORT
    # ========================================================


    candidates = sorted(
        candidates,
        key=lambda x: (
            x.get(
                "true_result_score",
                0,
            ),
            x.get(
                "race_key_count",
                0,
            ),
        ),
        reverse=True,
    )


    strong_candidates = [
        item
        for item in candidates
        if item.get("judgement")
        == "STRONG_TRUE_RESULT_CANDIDATE"
    ]


    true_candidates = [
        item
        for item in candidates
        if item.get("judgement")
        in {
            "STRONG_TRUE_RESULT_CANDIDATE",
            "TRUE_RESULT_CANDIDATE",
        }
    ]


    jsj006_past_result_files = [
        item
        for item in candidates
        if item.get("judgement")
        == "LIKELY_JSJ006_PAST_RESULT"
    ]


    # ========================================================
    # OUTPUT
    # ========================================================


    output = {
        "program": "054_test.py",
        "created_at": datetime.now().isoformat(),
        "target_date": TARGET_DATE,
        "json_scan_files": len(json_files),
        "json_load_errors": load_error_count,
        "target_date_files": target_date_file_count,
        "judgement_summary": dict(
            judgement_counter
        ),
        "strong_candidate_count": len(
            strong_candidates
        ),
        "true_candidate_count": len(
            true_candidates
        ),
        "jsj006_past_result_file_count": len(
            jsj006_past_result_files
        ),
        "strong_candidates": strong_candidates,
        "true_candidates": true_candidates,
        "jsj006_past_result_files": (
            jsj006_past_result_files
        ),
        "all_candidates": candidates,
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
        "054 最終結果"
    )

    print(
        "#"
        * 100
    )

    print()

    print(
        "TARGET DATE:",
        TARGET_DATE,
    )

    print(
        "JSON SCAN FILES:",
        len(json_files),
    )

    print(
        "TARGET DATE FILES:",
        target_date_file_count,
    )

    print(
        "LOAD ERROR:",
        load_error_count,
    )

    print()

    print(
        "STRONG TRUE RESULT CANDIDATES:",
        len(strong_candidates),
    )

    print(
        "TRUE RESULT CANDIDATES:",
        len(true_candidates),
    )

    print(
        "LIKELY JSJ006 PAST RESULT FILES:",
        len(jsj006_past_result_files),
    )


    # ========================================================
    # JUDGEMENT SUMMARY
    # ========================================================


    print()

    print(
        "★ JUDGEMENT SUMMARY ★"
    )


    for key, count in (
        judgement_counter.most_common()
    ):

        print(
            key,
            ":",
            count,
        )


    # ========================================================
    # TOP CANDIDATE
    # ========================================================


    print()

    print(
        "★ TRUE RESULT CANDIDATE TOP20 ★"
    )


    if not true_candidates:

        print(
            "なし"
        )


    for item in true_candidates[:20]:

        print()

        print(
            "-"
            * 100
        )

        print(
            "FILE:",
            item.get("file"),
        )

        print(
            "JUDGEMENT:",
            item.get("judgement"),
        )

        print(
            "SCORE:",
            item.get("true_result_score"),
        )

        print(
            "RACE KEYS:",
            item.get("race_key_count"),
        )

        print(
            "COUNTERS:",
            item.get("evidence_counters"),
        )

        print(
            "HIT KEYS:",
            item.get("evidence_hit_keys"),
        )


        samples = item.get(
            "evidence_samples",
            {},
        )


        print()

        print(
            "PAYOUT SAMPLE:"
        )


        payout_samples = samples.get(
            "payout",
            [],
        )


        if not payout_samples:

            print(
                "なし"
            )


        for sample in payout_samples[:5]:

            print(
                sample
            )


        print()

        print(
            "FINISH SAMPLE:"
        )


        finish_samples = samples.get(
            "finish",
            [],
        )


        if not finish_samples:

            print(
                "なし"
            )


        for sample in finish_samples[:5]:

            print(
                sample
            )


        print()

        print(
            "BET SAMPLE:"
        )


        bet_samples = samples.get(
            "bet",
            [],
        )


        if not bet_samples:

            print(
                "なし"
            )


        for sample in bet_samples[:5]:

            print(
                sample
            )


    # ========================================================
    # JSJ006 FALSE POSITIVE
    # ========================================================


    print()

    print(
        "★ LIKELY JSJ006 PAST RESULT FILE TOP20 ★"
    )


    if not jsj006_past_result_files:

        print(
            "なし"
        )


    for item in jsj006_past_result_files[:20]:

        print()

        print(
            item.get("file")
        )

        print(
            "RACE KEYS:",
            item.get("race_key_count"),
        )

        print(
            "FALSE POSITIVE COUNT:",
            item.get(
                "evidence_counters",
                {},
            ).get(
                "false_positive",
                0,
            ),
        )

        print(
            "FALSE POSITIVE KEYS:",
            item.get(
                "evidence_hit_keys",
                {},
            ).get(
                "false_positive",
                [],
            ),
        )


    # ========================================================
    # BEST SOURCE
    # ========================================================


    print()

    print(
        "★ BEST RESULT SOURCE ★"
    )


    if true_candidates:

        best = true_candidates[0]


        print(
            "FILE:",
            best.get("file"),
        )

        print(
            "JUDGEMENT:",
            best.get("judgement"),
        )

        print(
            "SCORE:",
            best.get("true_result_score"),
        )

        print(
            "RACE KEYS:",
            best.get("race_key_count"),
        )

        print(
            "HIT KEYS:",
            best.get("evidence_hit_keys"),
        )


    else:

        print(
            "本物の確定結果候補を自動確定できませんでした"
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
        "=== 054 完了 ==="
    )


if __name__ == "__main__":

    main()