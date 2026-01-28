"""Archive blocked URLs using Scrapfly."""

import os
import json
import time
import httpx
from bs4 import BeautifulSoup

SCRAPFLY_API_KEY = "scp-live-01ecacbb00e4432da6db7feef68de758"

# URLs that Scrapfly can fetch (from our test)
SCRAPFLY_URLS = [
    ("T1-D-060", "New Jersey Monitor", "https://newjerseymonitor.com/2025/12/19/ice-detainee-newark-jail-died/"),
    ("T2-SA-010", "Oregon Capital Chronicle", "https://oregoncapitalchronicle.com/2026/01/12/pair-shot-by-u-s-border-patrol-in-portland-charged-with-illegal-entry-assaulting-federal-officer/"),
    ("T3-052", "New Jersey Monitor", "https://newjerseymonitor.com/2025/05/09/newark-mayor-detained-by-federal-agents-during-protest-at-ice-jail/"),
    ("T3-062", "SF Chronicle", "https://www.sfchronicle.com/california/article/ice-immigration-farm-central-valley-20374476.php"),
    ("T3-115", "National Catholic Reporter", "https://www.ncronline.org/news/ice-agents-detain-migrants-church-grounds-2-california-parishes-diocese-says"),
    ("T3-116", "Bring Me The News", "https://bringmethenews.com/minnesota-news/ice-detains-4-columbia-heights-students-including-5-and-10-year-olds-sent-to-texas"),
    ("T3-118-1", "LA Public Press", "https://lapublicpress.org/2025/07/ice-agents-glendale-hospital-waiting-to-arrest-a-patient/"),
    ("T3-118-2", "WTTW Chicago", "https://news.wttw.com/2025/10/03/chicago-ald-jessie-fuentes-handcuffed-federal-agents-while-asking-about-patient-s-ice"),
    ("T3-122", "Louisiana Illuminator", "https://lailluminator.com/2025/10/21/ice-keeps-detaining-pregnant-immigrants-against-federal-policy/"),
    ("T3-P014", "SF Chronicle", "https://www.sfchronicle.com/bayarea/article/sf-ice-protests-against-trump-sending-troops-to-la-20367057.php"),
    ("T3-P018", "Axios", "https://www.axios.com/2025/06/10/ice-protests-la-nationwide-trump-tower-arrests"),
    ("T3-P024", "WABE", "https://www.wabe.org/buford-highway-plaza-fiesta-packed-with-protestors-supporting-atlanta-immigrants/"),
    ("T3-P030", "Colorado Newsline", "https://coloradonewsline.com/2026/01/09/protestors-enver-fatal-ice-shooting/"),
    ("T3-P031", "Bring Me The News", "https://bringmethenews.com/minnesota-news/residents-hit-with-tear-gas-and-flash-bangs-as-anger-grows-in-aftermath-of-latest-federal-shooting"),
    ("T3-P033", "Bring Me The News", "https://bringmethenews.com/minnesota-news/police-arrest-clergy-members-staging-anti-ice-protest-at-msp-airport"),
    ("T3-213", "Washington Post", "https://www.washingtonpost.com/politics/2025/12/05/ice-raid-grijalva-arizona/"),
]


def fetch_with_scrapfly(url: str) -> str | None:
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
                return result.get("content", "")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def extract_text(html: str) -> str:
    """Extract text from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def main():
    print(f"Archiving {len(SCRAPFLY_URLS)} URLs with Scrapfly...")
    print("=" * 70)

    archived = []

    for entry_id, source_name, url in SCRAPFLY_URLS:
        # Handle T3-118 which has two sources
        actual_entry_id = entry_id.split("-")[0] + "-" + entry_id.split("-")[1]
        if "-1" in entry_id or "-2" in entry_id:
            actual_entry_id = "T3-118"

        print(f"\n{entry_id} - {source_name}")
        print(f"  URL: {url[:60]}...")

        html = fetch_with_scrapfly(url)
        if not html:
            print("  FAILED to fetch")
            continue

        text = extract_text(html)
        if len(text) < 500:
            print(f"  WARNING: Short content ({len(text)} chars)")

        # Determine archive path
        folder = f"data/sources/{actual_entry_id}"
        os.makedirs(folder, exist_ok=True)

        # Find next available filename
        existing = [f for f in os.listdir(folder) if f.startswith("article") and f.endswith(".txt")]
        if not existing:
            filename = "article.txt"
        else:
            max_idx = 0
            for f in existing:
                if f == "article.txt":
                    max_idx = max(max_idx, 0)
                elif f.startswith("article_"):
                    try:
                        idx = int(f.replace("article_", "").replace(".txt", ""))
                        max_idx = max(max_idx, idx)
                    except:
                        pass
            filename = f"article_{max_idx + 1}.txt"

        filepath = f"{folder}/{filename}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"  Saved: {filepath} ({len(text)} chars)")
        archived.append({
            "entry_id": actual_entry_id,
            "source_name": source_name,
            "url": url,
            "archive_path": filepath,
            "chars": len(text),
        })

        time.sleep(2)  # Rate limiting

    print("\n" + "=" * 70)
    print(f"Archived {len(archived)} URLs")

    # Save archive info for updating JSON
    with open("data/sources/scrapfly_archived.json", "w") as f:
        json.dump(archived, f, indent=2)
    print("Archive info saved to data/sources/scrapfly_archived.json")


if __name__ == "__main__":
    main()
