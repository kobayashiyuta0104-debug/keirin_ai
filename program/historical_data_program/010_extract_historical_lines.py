import json
import re
from pathlib import Path

from bs4 import BeautifulSoup


# ==========================================================
# 010_extract_historical_lines.py
#
# 保存済みHTMLからライン予想を解析する
#
# 入力:
#   HTMLファイル
#
# 出力:
#   {
#       race_key,
#       line_found,
#       main_lines,
#       cars
#   }
# ==========================================================


def build_empty_cars():

    cars = {}

    for car in range(1, 10):

        cars[str(car)] = {
            "line": None,
            "position": None,
            "seri": 0
        }

    return cars


def race_key_from_filename(html_path):

    name = Path(html_path).stem

    return name

def parse_line_tokens(text):

    text = text.replace(" ", "")
    text = text.replace("\u3000", "")

    return re.findall(r"\(|（|\)|）|\d", text)

def parse_single_line(text):
    """
    1ライン解析

    対応例

    91
    912
    9(25)17
    9(257)1
    9(2)(5)17
    """

    tokens = parse_line_tokens(text)

    riders = []
    seri_flags = {}

    # rider -> position
    positions = {}

    current_position = 1

    in_seri = False

    seri_group = []

    for token in tokens:

        # ------------------------
        # 競り開始
        # ------------------------
        if token in ("(", "（"):

            in_seri = True
            seri_group = []

            continue

        # ------------------------
        # 競り終了
        # ------------------------
        if token in (")", "）"):

            # 括弧内は全員同順位
            for rider in seri_group:

                positions[rider] = current_position
                seri_flags[rider] = True

            current_position += 1

            in_seri = False
            seri_group = []

            continue

        rider = int(token)

        riders.append(rider)

        # ------------------------
        # 競り中
        # ------------------------
        if in_seri:

            seri_group.append(rider)

            continue

        # ------------------------
        # 通常
        # ------------------------
        positions[rider] = current_position
        seri_flags[rider] = False

        current_position += 1

    # 万一 ')' が無いHTMLでも救済
    if len(seri_group) > 0:

        for rider in seri_group:

            positions[rider] = current_position
            seri_flags[rider] = True

        current_position += 1

    return riders, seri_flags, positions

def parse_keirin_lines(ul):

    cars = build_empty_cars()

    main_lines = []

    current_line = []

    line_no = 1

    current_position = 1

    in_seri = False

    for li in ul.find_all("li"):

        span = li.find("span")

        if span is None:
            continue

        cls = ""

        for c in span.get("class", []):

            if c.startswith("no"):

                cls = c
                break

        if cls == "":
            continue

        value = span.get_text(strip=True)

        # --------------------
        # 区切り記号
        # --------------------
        if cls == "no0":

            # 競り開始
            if value in ("(", "（"):

                in_seri = True
                continue

            # 競り終了
            if value in (")", "）"):

                in_seri = False
                current_position += 1
                continue

            # &nbsp; = ライン終了
            if current_line:

                main_lines.append(current_line)

                current_line = []

                line_no += 1

                current_position = 1

            continue

        # --------------------
        # 車番
        # --------------------
        rider = int(cls.replace("no", ""))

        current_line.append(rider)

        cars[str(rider)]["line"] = line_no

        cars[str(rider)]["position"] = current_position

        cars[str(rider)]["seri"] = 1 if in_seri else 0

        if not in_seri:

            current_position += 1

    if current_line:

        main_lines.append(current_line)

    return main_lines, cars


def _has_class_prefix(tag, prefix):

    return any(
        str(class_name).startswith(prefix)
        for class_name in tag.get("class", [])
    )


def parse_winticket_lines(soup):
    """Parse WINTICKET lines and its explicit contest start/end markers."""

    label = soup.find(
        lambda tag: (
            tag.name == "span"
            and tag.get_text(" ", strip=True) == "並び予想"
        )
    )

    empty_cars = build_empty_cars()
    if label is None:
        return [], empty_cars

    wrapper = label.find_parent("div")
    if wrapper is None:
        return [], empty_cars

    line_wrapper = next(
        (
            child
            for child in wrapper.find_all("div", recursive=False)
            if _has_class_prefix(child, "LinePrediction___LineWrapper")
        ),
        None,
    )
    if line_wrapper is None:
        return [], empty_cars

    bib_group = line_wrapper.find(
        lambda tag: (
            tag.name == "div"
            and _has_class_prefix(tag, "BibGroup___Wrapper")
        )
    )
    if bib_group is None:
        return [], empty_cars

    main_lines = []
    current_line = []
    cars = build_empty_cars()
    line_no = 1
    current_position = 1
    in_seri = False
    seri_group = []

    def finish_seri_group():
        nonlocal current_position, in_seri, seri_group

        for rider in seri_group:
            cars[str(rider)] = {
                "line": line_no,
                "position": current_position,
                "seri": 1,
            }

        if seri_group:
            current_position += 1

        in_seri = False
        seri_group = []

    for child in bib_group.find_all(["span", "div"], recursive=False):
        marker = child.get("aria-label", "")

        if marker == "ライン区切り":
            if in_seri:
                finish_seri_group()

            if current_line:
                main_lines.append(current_line)
                current_line = []
                line_no += 1

            current_position = 1
            continue

        if marker == "競り開始":
            in_seri = True
            seri_group = []
            continue

        if marker == "競り終了":
            if in_seri:
                finish_seri_group()
            continue

        aria_label = marker
        if not aria_label:
            rider_tag = child.find(
                attrs={"aria-label": re.compile(r"^[1-9]番$")}
            )
            aria_label = rider_tag.get("aria-label", "") if rider_tag else ""

        match = re.fullmatch(r"([1-9])番", aria_label)
        if not match:
            continue

        rider = int(match.group(1))
        current_line.append(rider)

        if in_seri:
            seri_group.append(rider)
            continue

        cars[str(rider)] = {
            "line": line_no,
            "position": current_position,
            "seri": 0,
        }
        current_position += 1

    if in_seri:
        finish_seri_group()

    if current_line:
        main_lines.append(current_line)

    return main_lines, cars


def extract_venue_name(html_text):
    """Extract the venue name from either OddsPark or WINTICKET HTML."""

    soup = BeautifulSoup(html_text, "html.parser")

    for heading in soup.find_all(["h1", "h2"]):
        text = heading.get_text(" ", strip=True)
        match = re.match(r"^(.+?)競輪(?:場|[\s\u3000]|$)", text)
        if match:
            return match.group(1).strip()

    if soup.title:
        title = soup.title.get_text(" ", strip=True)
        match = re.match(r"^(.+?)競輪", title)
        if match:
            return match.group(1).strip()

    return ""

def parse_historical_line_html(html_path):

    html_path = Path(html_path)

    if not html_path.exists():

        raise FileNotFoundError(html_path)

    with open(html_path, "r", encoding="utf-8") as f:

        soup = BeautifulSoup(f.read(), "html.parser")

    race_key = race_key_from_filename(html_path)

    result = {

        "race_key": race_key,

        "line_found": False,

        "main_lines": [],

        "cars": build_empty_cars()

    }

    # ---------- ラインHTML取得 ----------

    line_container = soup.find("ul", class_="keirinRyosouline")

    if line_container is None:

        # class名が変わっている場合に備えて保険を掛ける
        for ul in soup.find_all("ul"):

            cls = " ".join(ul.get("class", []))

            if "keirinRyosouline" in cls:

                line_container = ul
                break

    if line_container is None:

        main_lines, cars = parse_winticket_lines(soup)

        result["line_found"] = len(main_lines) > 0
        result["main_lines"] = main_lines
        result["cars"] = cars

        return result

    # ---------- ライン解析 ----------
    main_lines, cars = parse_keirin_lines(line_container)

    result["line_found"] = len(main_lines) > 0
    result["main_lines"] = main_lines
    result["cars"] = cars

    return result


# ==========================================================
# JSON保存
# ==========================================================

def save_json(data, output_path):

    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


# ==========================================================
# デバッグ表示
# ==========================================================

def print_result(result):

    print()

    print("=" * 60)
    print("race_key :", result["race_key"])
    print("line_found :", result["line_found"])
    print("=" * 60)

    print()

    print("main_lines")

    for line in result["main_lines"]:

        print(" ", line)

    print()

    print("cars")

    for car in range(1, 10):

        info = result["cars"][str(car)]

        print(
            f"{car}: "
            f"line={info['line']} "
            f"position={info['position']} "
            f"seri={info['seri']}"
        )


# ==========================================================
# 単体テスト
# ==========================================================

if __name__ == "__main__":

    HTML_FILE = Path(
        r"C:\競輪AI\data_official\historical\html\【出走表】Ｓ級選抜｜2026年7月19日(日) 高知競輪 6R｜競輪（KEIRIN）ならオッズパーク競輪.html"
        )

    OUTPUT_JSON = Path(
        r"C:\競輪AI\data_official\historical\html\json\historical_line_test.json"
    )

    print("=" * 60)
    print("010 Historical Line Parser")
    print("=" * 60)

    print()
    print("Input :", HTML_FILE)

    try:

        result = parse_historical_line_html(HTML_FILE)

        print_result(result)

        save_json(result, OUTPUT_JSON)

        print()
        print("Saved :", OUTPUT_JSON)

    except Exception as e:

        print()
        print("ERROR")
        print(type(e).__name__)
        print(e)
