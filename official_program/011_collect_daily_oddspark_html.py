"""Collect OddsPark keirin line pages into the legacy HTML envelope."""

import time
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.oddspark.com/keirin/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
)
RETRY_STATUSES = {429, 500, 502, 503, 504}


class OddsParkClient:
    """Use one cookie-bearing session and follow the site's normal page flow."""

    def __init__(self, timeout=30, retries=3, request_interval=0.25):
        self.timeout = timeout
        self.retries = retries
        self.request_interval = request_interval
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;"
                "q=0.9,image/avif,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
            "Upgrade-Insecure-Requests": "1",
        })
        self._warmed = False

    def get_html(self, url, referer=None):
        headers = {"Referer": referer or BASE_URL}
        last_error = None

        for attempt in range(1, self.retries + 1):
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                )

                if response.status_code == 403:
                    raise requests.HTTPError(
                        f"OddsPark returned HTTP 403 for {response.url}",
                        response=response,
                    )

                if response.status_code in RETRY_STATUSES:
                    response.raise_for_status()

                response.raise_for_status()
                if "html" not in response.headers.get("Content-Type", "").lower():
                    raise RuntimeError(
                        f"OddsPark returned non-HTML content for {response.url}: "
                        f"{response.headers.get('Content-Type', 'unknown')}"
                    )

                response.encoding = "utf-8"
                if self.request_interval > 0:
                    time.sleep(self.request_interval)
                return response.text

            except requests.RequestException as exc:
                last_error = exc
                status = getattr(getattr(exc, "response", None), "status_code", None)
                if status == 403 or (status is not None and status not in RETRY_STATUSES):
                    raise
                if attempt == self.retries:
                    raise
                time.sleep(min(2 ** attempt, 8))

        raise RuntimeError(f"OddsPark request failed for {url}: {last_error}")

    def warm_up(self):
        if not self._warmed:
            self.get_html(BASE_URL, referer=BASE_URL)
            self._warmed = True


def _query_values(url):
    return parse_qs(urlsplit(url).query, keep_blank_values=True)


def _first(values, key):
    items = values.get(key, [])
    return items[0] if items else None


def _calendar_venues(html, target_date):
    venues = {}
    soup = BeautifulSoup(html, "html.parser")

    for anchor in soup.find_all("a", href=True):
        url = urljoin(BASE_URL, anchor["href"])
        if not urlsplit(url).path.endswith("AllRaceList.do"):
            continue

        query = _query_values(url)
        race_date = _first(query, "kaisaiBi")
        venue_code = _first(query, "joCode")
        if race_date == target_date and venue_code:
            venues[venue_code] = url

    return sorted(venues.items(), key=lambda item: item[0])


def _race_links(html, all_race_url, target_date):
    races = {}
    soup = BeautifulSoup(html, "html.parser")

    for anchor in soup.find_all("a", href=True):
        url = urljoin(all_race_url, anchor["href"])
        if not urlsplit(url).path.endswith("RaceList.do"):
            continue

        query = _query_values(url)
        race_date = _first(query, "kaisaiBi")
        venue_code = _first(query, "joCode")
        race_no = _first(query, "raceNo")
        if race_date != target_date or not venue_code or not race_no:
            continue

        try:
            race_number = int(race_no)
        except ValueError:
            continue

        race_key = f"{race_date}_{venue_code}_{race_number:02d}"
        races[race_key] = url

    return sorted(races.items(), key=lambda item: item[0])


def collect_lines_html(
    target_date,
    output_file,
    generated_by,
    allow_empty=False,
    request_interval=0.25,
):
    """Fetch all OddsPark RaceList pages and write the existing RACE_KEY format.

    Requests use a single warmed session, following the same homepage,
    calendar, event list, and race detail flow as a normal browser visit.
    Files are written only after every requested page has been fetched.
    """
    client = OddsParkClient(request_interval=request_interval)
    client.warm_up()

    calendar_url = f"{BASE_URL}KaisaiCalendar.do?target={target_date[:6]}"
    calendar_html = client.get_html(calendar_url, referer=BASE_URL)
    venues = _calendar_venues(calendar_html, target_date)

    if not venues and not allow_empty:
        raise RuntimeError(f"No OddsPark events found for {target_date}")

    race_urls = {}
    for venue_code, all_race_url in venues:
        all_race_html = client.get_html(all_race_url, referer=calendar_url)
        for race_key, race_url in _race_links(
            all_race_html,
            all_race_url,
            target_date,
        ):
            race_urls[race_key] = (race_url, all_race_url)

    race_urls = sorted(race_urls.items(), key=lambda item: item[0])
    if not race_urls and not allow_empty:
        raise RuntimeError(
            f"OddsPark listed venues but no race pages for {target_date}"
        )

    output_lines = [
        "<!-- =============================================== -->",
        f"<!-- DATE={target_date} -->",
        "<!-- SOURCE=ODDSPARK RaceList -->",
        f"<!-- GENERATED BY {generated_by} -->",
        "<!-- =============================================== -->",
        "",
    ]

    for index, (race_key, page_info) in enumerate(race_urls, start=1):
        race_url, referer = page_info
        race_html = client.get_html(race_url, referer=referer)
        if "<html" not in race_html.lower():
            raise RuntimeError(f"OddsPark returned an invalid race page: {race_key}")

        output_lines.extend([
            f"<!-- RACE_KEY={race_key} -->",
            race_html,
            "<!-- END_RACE -->",
            "",
        ])
        print(f"[{index}/{len(race_urls)}] fetched {race_key}")

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = output_file.with_name(output_file.name + ".tmp")
    temporary_file.write_text("\n".join(output_lines), encoding="utf-8")
    temporary_file.replace(output_file)

    summary = {
        "target_date": target_date,
        "venue_count": len(venues),
        "race_count": len(race_urls),
        "fetched_count": len(race_urls),
        "output_file": output_file,
    }
    print(
        f"Saved {output_file}: {summary['race_count']} OddsPark race pages "
        f"from {summary['venue_count']} venues"
    )
    return summary

import os
from datetime import datetime, timedelta, timezone

if os.name == "nt":
    BASE_DIR = Path(r"C:\競輪AI")
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

SAVE_DIR = BASE_DIR / "data_official" / "daily" / "html"
LOG_DIR = BASE_DIR / "data_official" / "daily" / "log"
FAILED_LOG = LOG_DIR / "failed_daily_html.txt"
SAVE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

JST = timezone(timedelta(hours=9))
TARGET_DATE = (datetime.now(JST) - timedelta(days=1)).strftime("%Y%m%d")
OUTPUT_FILE = SAVE_DIR / f"{TARGET_DATE}.html"

print("=" * 70)
print("011 Collect Daily OddsPark Lines HTML")
print("SOURCE: ODDSPARK RaceList")
print("TARGET DATE:", TARGET_DATE)
print("=" * 70)

try:
    summary = collect_lines_html(
        TARGET_DATE,
        OUTPUT_FILE,
        generated_by="011_collect_daily_oddspark_html.py",
        allow_empty=True,
    )
except Exception as exc:
    with FAILED_LOG.open("a", encoding="utf-8") as log:
        log.write(f"{TARGET_DATE}\t{type(exc).__name__}: {exc}\n")
    raise

if summary["race_count"] == 0:
    print("対象日の開催がありません。空のHTMLを保存しました。")