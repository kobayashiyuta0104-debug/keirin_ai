"""Collect WINTICKET racecard HTML in the project's RACE_KEY envelope."""

import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.winticket.jp/keirin/"
RACECARD_BASE_URL = "https://www.winticket.jp/keirin/racecard/"
SITE_BASE_URL = "https://www.winticket.jp"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
)
RETRY_STATUSES = {429, 500, 502, 503, 504}
RACECARD_PATH_RE = re.compile(
    r"^/keirin/(?P<venue_slug>[^/]+)/racecard/"
    r"(?P<event_id>\d{10})/(?P<day>\d+)/(?P<race_no>\d+)/?$"
)


class WinticketClient:
    """Fetch public racecard pages with one regular HTTP session."""

    def __init__(self, timeout=30, retries=3, request_interval=0.5):
        self.timeout = timeout
        self.retries = retries
        self.request_interval = request_interval
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
            "Upgrade-Insecure-Requests": "1",
        })

    def get_html(self, url, referer):
        for attempt in range(1, self.retries + 1):
            try:
                response = self.session.get(
                    url,
                    headers={"Referer": referer},
                    timeout=self.timeout,
                )
            except requests.RequestException:
                if attempt == self.retries:
                    raise
                time.sleep(min(2 ** attempt, 8))
                continue

            if response.status_code == 403:
                raise requests.HTTPError(
                    f"WINTICKET returned HTTP 403 for {response.url}",
                    response=response,
                )

            if response.status_code in RETRY_STATUSES:
                if attempt == self.retries:
                    response.raise_for_status()
                time.sleep(min(2 ** attempt, 8))
                continue

            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").lower()
            if "html" not in content_type:
                raise RuntimeError(
                    f"WINTICKET returned non-HTML content for {response.url}: "
                    f"{content_type or 'unknown'}"
                )

            if not response.encoding or response.encoding.lower() == "iso-8859-1":
                response.encoding = response.apparent_encoding or "utf-8"

            html = response.text
            if not re.search(r"<html[\s>]", html, flags=re.IGNORECASE):
                raise RuntimeError(
                    f"WINTICKET returned an invalid HTML page: {response.url}"
                )

            if self.request_interval > 0:
                time.sleep(self.request_interval)
            return html

        raise RuntimeError(f"WINTICKET request failed for {url}")


def find_race_links(index_html, target_date):
    """Find every direct racecard link on WINTICKET's date-specific listing."""
    races = {}
    soup = BeautifulSoup(index_html, "html.parser")

    for anchor in soup.find_all("a", href=True):
        url = urljoin(SITE_BASE_URL, anchor["href"])
        parsed = urlsplit(url)
        if parsed.netloc not in {"www.winticket.jp", "winticket.jp"}:
            continue

        match = RACECARD_PATH_RE.fullmatch(parsed.path)
        if not match:
            continue

        event_id = match.group("event_id")
        venue_code = event_id[8:10]
        race_no = int(match.group("race_no"))
        race_key = f"{target_date}_{venue_code}_{race_no:02d}"
        racecard_url = parsed._replace(query="", fragment="").geturl()
        if race_key in races and races[race_key] != racecard_url:
            raise RuntimeError(
                f"Multiple WINTICKET racecard URLs found for {race_key}"
            )
        races[race_key] = racecard_url

    return sorted(races.items(), key=lambda item: item[0])


def _expected_race_ids(target_date, expected_races):
    """Normalize official race data to WINTICKET venue-code/race-number keys."""
    expected = {}
    for race in expected_races:
        race_key = str(race.get("race_key", ""))
        if race_key and not race_key.startswith(f"{target_date}_"):
            raise ValueError(
                "Expected race belongs to another date: "
                f"{race_key} (target {target_date})"
            )

        venue_code = race.get("venue_code", race.get("競輪場コード"))
        race_no = race.get("race_no", race.get("レース番号"))
        if venue_code is None or race_no is None:
            raise ValueError(f"Expected race is missing venue code or race number: {race}")

        identity = (str(venue_code).zfill(2), int(race_no))
        if identity in expected:
            raise ValueError(
                f"Duplicate expected race: venue={identity[0]} race={identity[1]}"
            )
        expected[identity] = race_key or f"{target_date}_{identity[0]}_{identity[1]}R"

    return expected


def collect_lines_html(
    target_date,
    output_file,
    generated_by,
    allow_empty=False,
    max_races=None,
    request_interval=0.5,
    expected_races=None,
):
    """Fetch all expected racecards for one date and save the RACE_KEY format.

    ``expected_races`` should come from the project's official race data. When
    supplied, collection fails before writing output if the WINTICKET racecard
    listing does not expose every expected race.
    """
    if not re.fullmatch(r"\d{8}", target_date):
        raise ValueError(f"target_date must be YYYYMMDD: {target_date}")

    client = WinticketClient(request_interval=request_interval)
    client.get_html(BASE_URL, referer=BASE_URL)

    index_url = f"{RACECARD_BASE_URL}{target_date}"
    index_html = client.get_html(index_url, referer=BASE_URL)
    discovered_races = find_race_links(index_html, target_date)
    races = discovered_races

    if expected_races is not None:
        expected = _expected_race_ids(target_date, expected_races)
        discovered_by_identity = {}
        for race_key, race_url in discovered_races:
            parts = race_key.split("_")
            discovered_by_identity[(parts[1], int(parts[2]))] = (race_key, race_url)

        missing = sorted(set(expected) - set(discovered_by_identity))
        if missing:
            formatted = ", ".join(expected[identity] for identity in missing)
            raise RuntimeError(
                "WINTICKET racecard listing is missing expected races: " + formatted
            )

        races = [discovered_by_identity[identity] for identity in sorted(expected)]

    if not races and not allow_empty:
        raise RuntimeError(f"No WINTICKET racecards found for {target_date}")

    selected_races = races if max_races is None else races[:max_races]
    output_lines = [
        "<!-- =============================================== -->",
        f"<!-- DATE={target_date} -->",
        "<!-- SOURCE=WINTICKET RaceCard -->",
        f"<!-- GENERATED BY {generated_by} -->",
        "<!-- =============================================== -->",
        "",
    ]

    for index, (race_key, race_url) in enumerate(selected_races, start=1):
        race_html = client.get_html(race_url, referer=index_url)
        output_lines.extend([
            f"<!-- RACE_KEY={race_key} -->",
            race_html,
            "<!-- END_RACE -->",
            "",
        ])
        print(f"[{index}/{len(selected_races)}] fetched {race_key}")

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = output_file.with_name(output_file.name + ".tmp")
    temporary_file.write_text("\n".join(output_lines), encoding="utf-8")
    temporary_file.replace(output_file)

    venue_count = len({key.split("_")[1] for key, _ in races})
    summary = {
        "target_date": target_date,
        "venue_count": venue_count,
        "race_count": len(races),
        "discovered_count": len(discovered_races),
        "fetched_count": len(selected_races),
        "output_file": output_file,
    }
    print(
        f"Saved {output_file}: fetched {summary['fetched_count']} of "
        f"{summary['race_count']} WINTICKET race pages"
    )
    return summary
