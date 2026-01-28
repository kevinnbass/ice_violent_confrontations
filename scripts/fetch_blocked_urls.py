"""Attempt to fetch blocked URLs using Scrapfly, Wayback Machine, and archive.ph."""

import os
import json
import time
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote

# Load Scrapfly API key from ttuhsc_watcher .env
SCRAPFLY_API_KEY = "scp-live-01ecacbb00e4432da6db7feef68de758"

# Blocked URLs from our testing
BLOCKED_URLS = [
    # 403 Forbidden
    ("T1-D-060", "New Jersey Monitor", "https://newjerseymonitor.com/2025/12/19/ice-detainee-newark-jail-died/"),
    ("T2-WD-006", "WGN-TV", "https://wgntv.com/news/chicago-news/wgn-employee-debbie-brockman-detained-ice/"),
    ("T2-WD-007", "KTLA", "https://ktla.com/news/local-news/u-s-citizen-detained-after-violent-struggle-with-ice-agents-at-pico-rivera-walmart/"),
    ("T2-SA-010", "Oregon Capital Chronicle", "https://oregoncapitalchronicle.com/2026/01/12/pair-shot-by-u-s-border-patrol-in-portland-charged-with-illegal-entry-assaulting-federal-officer/"),
    ("T3-052", "New Jersey Monitor", "https://newjerseymonitor.com/2025/05/09/newark-mayor-detained-by-federal-agents-during-protest-at-ice-jail/"),
    ("T3-062", "SF Chronicle", "https://www.sfchronicle.com/california/article/ice-immigration-farm-central-valley-20374476.php"),
    ("T3-113", "Axios Seattle", "https://www.axios.com/local/seattle/2025/05/23/ice-arrests-hit-seattle-home"),
    ("T3-115", "National Catholic Reporter", "https://www.ncronline.org/news/ice-agents-detain-migrants-church-grounds-2-california-parishes-diocese-says"),
    ("T3-116", "Bring Me The News", "https://bringmethenews.com/minnesota-news/ice-detains-4-columbia-heights-students-including-5-and-10-year-olds-sent-to-texas"),
    ("T3-118", "LA Public Press", "https://lapublicpress.org/2025/07/ice-agents-glendale-hospital-waiting-to-arrest-a-patient/"),
    ("T3-118", "WTTW Chicago", "https://news.wttw.com/2025/10/03/chicago-ald-jessie-fuentes-handcuffed-federal-agents-while-asking-about-patient-s-ice"),
    ("T3-122", "Louisiana Illuminator", "https://lailluminator.com/2025/10/21/ice-keeps-detaining-pregnant-immigrants-against-federal-policy/"),
    ("T3-153", "New York Times", "https://www.nytimes.com/2025/09/15/nyregion/ice-detention-conditions-federal-plaza.html"),
    ("T3-P014", "SF Chronicle", "https://www.sfchronicle.com/bayarea/article/sf-ice-protests-against-trump-sending-troops-to-la-20367057.php"),
    ("T3-P018", "Axios", "https://www.axios.com/2025/06/10/ice-protests-la-nationwide-trump-tower-arrests"),
    ("T3-P024", "WABE", "https://www.wabe.org/buford-highway-plaza-fiesta-packed-with-protestors-supporting-atlanta-immigrants/"),
    ("T3-P030", "Colorado Newsline", "https://coloradonewsline.com/2026/01/09/protestors-enver-fatal-ice-shooting/"),
    ("T3-P031", "Bring Me The News", "https://bringmethenews.com/minnesota-news/residents-hit-with-tear-gas-and-flash-bangs-as-anger-grows-in-aftermath-of-latest-federal-shooting"),
    ("T3-P033", "Bring Me The News", "https://bringmethenews.com/minnesota-news/police-arrest-clergy-members-staging-anti-ice-protest-at-msp-airport"),
    # Blocked/Paywall
    ("T3-119", "Washington Post", "https://www.washingtonpost.com/immigration/2025/11/05/chicago-preschool-ice-raid/"),
    ("T3-154", "Washington Post", "https://www.washingtonpost.com/immigration/2025/12/20/unaccompanied-minors-ice-detention/"),
    ("T3-P033", "Washington Post", "https://www.washingtonpost.com/nation/2026/01/23/minnesota-general-strike-ice/"),
    ("T3-213", "Washington Post", "https://www.washingtonpost.com/politics/2025/12/05/ice-raid-grijalva-arizona/"),
]


def fetch_with_scrapfly(url: str) -> tuple[bool, str, int]:
    """Fetch URL using Scrapfly API."""
    api_url = "https://api.scrapfly.io/scrape"
    params = {
        "key": SCRAPFLY_API_KEY,
        "url": url,
        "asp": "true",
        "render_js": "true",
        "country": "us",
        "retry": "true",
    }

    try:
        response = httpx.get(api_url, params=params, timeout=60)
        if response.status_code == 200:
            data = response.json()
            result = data.get("result", {})
            if result.get("success"):
                content = result.get("content", "")
                return True, content, len(content)
        return False, "", 0
    except Exception as e:
        return False, str(e), 0


def fetch_from_wayback(url: str) -> tuple[bool, str, int]:
    """Fetch URL from Wayback Machine."""
    # First check if archived
    check_url = f"https://archive.org/wayback/available?url={quote(url)}"
    try:
        resp = httpx.get(check_url, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            snapshots = data.get("archived_snapshots", {})
            closest = snapshots.get("closest", {})
            if closest.get("available"):
                wayback_url = closest.get("url", "")
                # Fetch the archived page
                wb_resp = httpx.get(wayback_url, timeout=30, follow_redirects=True)
                if wb_resp.status_code == 200:
                    return True, wb_resp.text, len(wb_resp.text)
        return False, "", 0
    except Exception as e:
        return False, str(e), 0


def fetch_from_archive_ph(url: str) -> tuple[bool, str, int]:
    """Check archive.ph/archive.is for cached version."""
    # archive.ph stores by URL hash
    search_url = f"https://archive.ph/{quote(url)}"
    try:
        resp = httpx.get(search_url, timeout=30, follow_redirects=True)
        if resp.status_code == 200 and len(resp.text) > 5000:
            # Check if it's actual content vs search page
            if "No results" not in resp.text and "Search results" not in resp.text:
                return True, resp.text, len(resp.text)
        return False, "", 0
    except Exception as e:
        return False, str(e), 0


def extract_text(html: str) -> str:
    """Extract text from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def main():
    results = {
        "scrapfly_success": [],
        "wayback_success": [],
        "archive_ph_success": [],
        "all_failed": [],
    }

    print(f"Testing {len(BLOCKED_URLS)} blocked URLs...")
    print("=" * 70)

    for entry_id, source_name, url in BLOCKED_URLS:
        print(f"\n{entry_id} - {source_name}")
        print(f"  URL: {url[:60]}...")

        # Try Scrapfly first
        print("  [Scrapfly] ", end="", flush=True)
        success, content, length = fetch_with_scrapfly(url)
        if success and length > 1000:
            print(f"SUCCESS ({length} chars)")
            results["scrapfly_success"].append((entry_id, source_name, url, length))
            continue
        else:
            print(f"FAILED")

        time.sleep(1)

        # Try Wayback Machine
        print("  [Wayback]  ", end="", flush=True)
        success, content, length = fetch_from_wayback(url)
        if success and length > 1000:
            print(f"SUCCESS ({length} chars)")
            results["wayback_success"].append((entry_id, source_name, url, length))
            continue
        else:
            print(f"FAILED")

        time.sleep(1)

        # Try archive.ph
        print("  [archive.ph] ", end="", flush=True)
        success, content, length = fetch_from_archive_ph(url)
        if success and length > 1000:
            print(f"SUCCESS ({length} chars)")
            results["archive_ph_success"].append((entry_id, source_name, url, length))
            continue
        else:
            print(f"FAILED")

        # All methods failed
        results["all_failed"].append((entry_id, source_name, url))
        print("  [ALL FAILED]")

        time.sleep(1)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Scrapfly success:   {len(results['scrapfly_success'])}")
    print(f"Wayback success:    {len(results['wayback_success'])}")
    print(f"archive.ph success: {len(results['archive_ph_success'])}")
    print(f"All methods failed: {len(results['all_failed'])}")

    if results["scrapfly_success"]:
        print("\nScrapfly can fetch:")
        for entry_id, name, url, length in results["scrapfly_success"]:
            print(f"  {entry_id}: {name}")

    if results["wayback_success"]:
        print("\nWayback can fetch:")
        for entry_id, name, url, length in results["wayback_success"]:
            print(f"  {entry_id}: {name}")

    if results["archive_ph_success"]:
        print("\narchive.ph can fetch:")
        for entry_id, name, url, length in results["archive_ph_success"]:
            print(f"  {entry_id}: {name}")

    if results["all_failed"]:
        print("\nTruly unfetchable:")
        for entry_id, name, url in results["all_failed"]:
            print(f"  {entry_id}: {name}")

    # Save results
    with open("data/sources/blocked_url_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to data/sources/blocked_url_test_results.json")


if __name__ == "__main__":
    main()
