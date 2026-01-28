#!/usr/bin/env python3
"""
URL Audit Script - Checks all source URLs in incident JSON files
Reports broken links (404s, timeouts, etc.) for data quality validation
"""

import json
import requests
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime

# Configuration
INCIDENT_DIR = Path(__file__).parent.parent / "data" / "incidents"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "incidents" / "fabricated_archive"
TIMEOUT = 15
MAX_WORKERS = 5  # Be respectful to servers
DELAY_BETWEEN_REQUESTS = 0.5

# Files to audit
JSON_FILES = [
    "tier1_deaths_in_custody.json",
    "tier2_shootings.json",
    "tier2_less_lethal.json",
    "tier3_incidents.json",
    "tier4_incidents.json"
]

# Headers to mimic browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def extract_urls_from_files():
    """Extract all source URLs with their entry IDs from JSON files"""
    entries = []

    for filename in JSON_FILES:
        filepath = INCIDENT_DIR / filename
        if not filepath.exists():
            print(f"Warning: {filename} not found")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for entry in data:
            if 'source_url' in entry and entry['source_url']:
                entries.append({
                    'file': filename,
                    'id': entry.get('id', 'UNKNOWN'),
                    'url': entry['source_url'],
                    'victim_name': entry.get('victim_name', entry.get('victim_count', 'N/A')),
                    'date': entry.get('date', 'N/A'),
                    'state': entry.get('state', 'N/A')
                })

    return entries

def check_url(entry):
    """Check if a URL is accessible"""
    url = entry['url']
    result = {
        **entry,
        'status_code': None,
        'error': None,
        'is_valid': False
    }

    try:
        response = requests.head(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        result['status_code'] = response.status_code

        # If HEAD fails, try GET
        if response.status_code >= 400:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
            result['status_code'] = response.status_code

        result['is_valid'] = response.status_code < 400

    except requests.exceptions.Timeout:
        result['error'] = 'TIMEOUT'
    except requests.exceptions.ConnectionError:
        result['error'] = 'CONNECTION_ERROR'
    except requests.exceptions.TooManyRedirects:
        result['error'] = 'TOO_MANY_REDIRECTS'
    except Exception as e:
        result['error'] = str(e)[:100]

    return result

def main():
    print("=" * 60)
    print("URL AUDIT SCRIPT - ICE Incidents Database")
    print("=" * 60)
    print()

    # Extract all URLs
    print("Extracting URLs from JSON files...")
    entries = extract_urls_from_files()

    # Deduplicate by URL (some URLs are used multiple times)
    unique_urls = {}
    for entry in entries:
        if entry['url'] not in unique_urls:
            unique_urls[entry['url']] = entry
        else:
            # Keep track that this URL is used by multiple entries
            if 'also_used_by' not in unique_urls[entry['url']]:
                unique_urls[entry['url']]['also_used_by'] = []
            unique_urls[entry['url']]['also_used_by'].append(entry['id'])

    print(f"Found {len(entries)} total URL references")
    print(f"Found {len(unique_urls)} unique URLs to check")
    print()

    # Check URLs
    print("Checking URLs (this may take a few minutes)...")
    results = []
    failed = []

    for i, (url, entry) in enumerate(unique_urls.items()):
        if i > 0 and i % 10 == 0:
            print(f"  Progress: {i}/{len(unique_urls)} ({100*i//len(unique_urls)}%)")

        result = check_url(entry)
        results.append(result)

        if not result['is_valid']:
            failed.append(result)
            print(f"  FAILED: {result['id']} - {result['status_code'] or result['error']} - {url[:60]}...")

        time.sleep(DELAY_BETWEEN_REQUESTS)

    print()
    print("=" * 60)
    print("AUDIT COMPLETE")
    print("=" * 60)
    print()
    print(f"Total unique URLs checked: {len(results)}")
    print(f"Valid URLs: {len(results) - len(failed)}")
    print(f"Failed URLs: {len(failed)}")
    print()

    if failed:
        print("FAILED URLS:")
        print("-" * 60)
        for r in failed:
            print(f"  File: {r['file']}")
            print(f"  ID: {r['id']}")
            print(f"  URL: {r['url']}")
            print(f"  Status: {r['status_code'] or r['error']}")
            print(f"  Victim/Count: {r['victim_name']}")
            if r.get('also_used_by'):
                print(f"  Also used by: {', '.join(r['also_used_by'])}")
            print()

    # Save results to CSV
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save failed URLs
    failed_csv = OUTPUT_DIR / f"failed_urls_{timestamp}.csv"
    with open(failed_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'id', 'url', 'status_code', 'error', 'victim_name', 'date', 'state'])
        writer.writeheader()
        for r in failed:
            writer.writerow({k: v for k, v in r.items() if k in writer.fieldnames})

    print(f"Failed URLs saved to: {failed_csv}")

    # Save full audit
    full_csv = OUTPUT_DIR / f"full_audit_{timestamp}.csv"
    with open(full_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'id', 'url', 'status_code', 'error', 'is_valid', 'victim_name', 'date', 'state'])
        writer.writeheader()
        for r in results:
            writer.writerow({k: v for k, v in r.items() if k in writer.fieldnames})

    print(f"Full audit saved to: {full_csv}")

    return failed

if __name__ == "__main__":
    failed = main()
