#!/usr/bin/env python3
"""Fetch and archive new sources for entries that need them."""

import requests
from bs4 import BeautifulSoup
from html import unescape
import json
from pathlib import Path
import time

def fetch_article(url, timeout=30):
    """Fetch article from URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()

        text = soup.get_text(separator='\n')
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        return unescape('\n'.join(lines)), None
    except Exception as e:
        return None, str(e)

def fetch_wayback(url, timeout=30):
    """Fetch from Wayback Machine."""
    try:
        avail_url = f'https://archive.org/wayback/available?url={url}'
        resp = requests.get(avail_url, timeout=10)
        data = resp.json()

        if data.get('archived_snapshots', {}).get('closest'):
            wayback_url = data['archived_snapshots']['closest']['url']
            return fetch_article(wayback_url, timeout)
        return None, "No wayback archive"
    except Exception as e:
        return None, str(e)

# Sources to fetch
NEW_SOURCES = {
    'T1-D-006': {
        'url': 'https://www.ice.gov/news/releases/vietnamese-national-ice-custody-dies-el-paso-long-term-acute-care-hospital',
        'name': 'ICE Official Press Release',
        'tier': 1
    },
    'T2-LL-002': {
        'url': 'https://pressfreedomtracker.us/all-incidents/reporter-struck-in-head-with-munition-by-federal-officers-at-la-protest/',
        'name': 'U.S. Press Freedom Tracker',
        'tier': 2
    },
    'T2-LL-008': {
        'url': 'https://www.cnn.com/2025/10/10/us/illinois-judge-ruling-ice-protests-pastor-chicago-hnk',
        'name': 'CNN (Judge ruling on pastor shooting)',
        'tier': 2
    },
    'T2-WD-003': {
        'url': 'https://www.democracynow.org/2025/7/2/ice_abductions_masked_men_andrea_velez',
        'name': 'Democracy Now!',
        'tier': 2
    },
    'T2-WD-005': {
        'url': 'https://ktla.com/news/79-year-old-american-citizen-files-50-million-claim-after-car-wash-ice-raid/',
        'name': 'KTLA',
        'tier': 2
    },
    'T3-049': {
        'url': 'https://baltimorebeat.com/indiscriminate-ice-arrests-have-left-baltimores-immigrant-communities-in-a-constant-state-of-fear-and-anxiety/',
        'name': 'Baltimore Beat',
        'tier': 2
    },
    'T3-051': {
        'url': 'https://www.nbcnews.com/news/latino/immigration-raid-newark-new-jersey-mayor-angry-rcna189100',
        'name': 'NBC News',
        'tier': 2
    },
    'T3-111': {
        'url': 'https://www.newhavenindependent.org/2025/07/08/immigration_officers_apprehend_woman_scheduled_for_court/',
        'name': 'New Haven Independent (July 8)',
        'tier': 2
    },
    'T3-189': {
        'url': 'https://www.cbsnews.com/miami/news/krome-detention-center-sos-immigration-miami-dade/',
        'name': 'CBS Miami',
        'tier': 2
    },
    'T3-218': {
        'url': 'https://www.kpbs.org/news/border-immigration/2025/05/01/man-arrested-in-ice-raid-near-el-cajon-is-back-with-his-family',
        'name': 'KPBS',
        'tier': 2
    },
    'T3-219': {
        'url': 'https://www.ice.gov/news/releases/ice-laredo-federal-partners-arrest-31-illegal-aliens-during-1-day-targeted-worksite',
        'name': 'ICE Official Press Release',
        'tier': 1
    },
    'T3-P013': {
        'url': 'https://lapublicpress.org/2025/06/ice-police-protest-lapd-lasd-tear-gas/',
        'name': 'LA Public Press',
        'tier': 2
    },
    'T3-P030': {
        'url': 'https://www.denvervoice.org/archive/2026/1/25/they-shot-and-killed-someone-in-broad-daylight-protesters-line-broadway-after-ice-shootings-spark-national-outrage',
        'name': 'Denver Voice (Jan 25)',
        'tier': 2
    },
    'T3-P031': {
        'url': 'https://edition.cnn.com/us/live-news/minneapolis-ice-shooting-protests-01-15-26',
        'name': 'CNN Live (Jan 15)',
        'tier': 2
    },
    'T4-014': {
        'url': 'https://coloradosun.com/2025/09/30/jeanette-vizguerra-ice-detention-six-months/',
        'name': 'Colorado Sun',
        'tier': 2
    }
}

def main():
    base_path = Path(__file__).parent.parent

    results = {'success': [], 'failed': []}

    for entry_id, source_info in NEW_SOURCES.items():
        url = source_info['url']
        name = source_info['name']

        print(f"\nFetching {entry_id}: {name}")
        print(f"  URL: {url[:60]}...")

        # Try direct fetch first, then wayback
        text, error = fetch_article(url)
        source_type = 'direct'

        if error or (text and len(text) < 500):
            print(f"  Direct fetch issue, trying Wayback...")
            text, error = fetch_wayback(url)
            source_type = 'wayback'

        if error:
            print(f"  FAILED: {error}")
            results['failed'].append({'entry_id': entry_id, 'url': url, 'error': error})
        elif len(text) < 500:
            print(f"  FAILED: Content too short ({len(text)} chars)")
            results['failed'].append({'entry_id': entry_id, 'url': url, 'error': f'Content too short ({len(text)} chars)'})
        else:
            # Save
            source_dir = base_path / 'data' / 'sources' / entry_id
            source_dir.mkdir(parents=True, exist_ok=True)

            existing = list(source_dir.glob('article*.txt'))
            next_num = len(existing) + 1
            out_file = source_dir / f'article_{next_num}_{source_type}.txt'

            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(text)

            print(f"  SUCCESS: {len(text):,} chars -> {out_file.name}")
            results['success'].append({
                'entry_id': entry_id,
                'url': url,
                'name': name,
                'tier': source_info['tier'],
                'archive_path': f'data/sources/{entry_id}/{out_file.name}',
                'chars': len(text)
            })

        time.sleep(1)  # Rate limiting

    print("\n" + "=" * 60)
    print(f"SUCCESS: {len(results['success'])}")
    print(f"FAILED: {len(results['failed'])}")

    # Save results
    results_file = base_path / 'data' / 'new_sources_fetched.json'
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")

if __name__ == '__main__':
    main()
