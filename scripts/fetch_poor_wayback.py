#!/usr/bin/env python3
"""Fetch poor quality wayback URLs with Scrapfly."""

import os
import json
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from html import unescape

SCRAPFLY_API_KEY = "scp-live-01ecacbb00e4432da6db7feef68de758"

def extract_text_from_html(html_content):
    """Extract readable text from HTML."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
        element.decompose()

    # Get text
    text = soup.get_text(separator='\n')

    # Clean up whitespace
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    text = '\n'.join(lines)

    return unescape(text)

def fetch_with_scrapfly(url, timeout=60):
    """Fetch URL using Scrapfly API."""
    api_url = "https://api.scrapfly.io/scrape"

    params = {
        "key": SCRAPFLY_API_KEY,
        "url": url,
        "render_js": "true",
        "asp": "true",
        "country": "us",
        "timeout": timeout * 1000,
    }

    try:
        response = requests.get(api_url, params=params, timeout=timeout + 10)
        response.raise_for_status()
        data = response.json()

        if data.get("result", {}).get("content"):
            return data["result"]["content"], None
        else:
            return None, "No content in response"
    except requests.exceptions.Timeout:
        return None, "Timeout"
    except requests.exceptions.RequestException as e:
        return None, str(e)
    except Exception as e:
        return None, str(e)

def main():
    base_path = Path(__file__).parent.parent

    # Load URLs to fetch (just the 3 poor quality ones)
    urls_file = base_path / "data" / "wayback_to_replace.json"
    with open(urls_file, 'r', encoding='utf-8') as f:
        urls_to_fetch = json.load(f)

    print(f"Attempting to fetch {len(urls_to_fetch)} URLs with Scrapfly...\n")

    results = {"success": [], "failed": []}

    for item in urls_to_fetch:
        entry_id = item["entry_id"]
        url = item["url"]
        source_name = item["source_name"]

        print(f"Fetching {entry_id}: {source_name}...")
        print(f"  URL: {url}")

        html_content, error = fetch_with_scrapfly(url)

        if error:
            print(f"  FAILED: {error}")
            results["failed"].append({"entry_id": entry_id, "url": url, "source_name": source_name, "error": error})
        else:
            text = extract_text_from_html(html_content)
            char_count = len(text)

            if char_count < 500:
                print(f"  FAILED: Content too short ({char_count} chars)")
                results["failed"].append({"entry_id": entry_id, "url": url, "source_name": source_name, "error": f"Content too short ({char_count} chars)"})
            else:
                # Save the file
                source_dir = base_path / "data" / "sources" / entry_id
                source_dir.mkdir(parents=True, exist_ok=True)

                # Find next available article number
                existing = list(source_dir.glob("article*.txt"))
                next_num = len(existing) + 1
                out_file = source_dir / f"article_{next_num}_scrapfly.txt"

                with open(out_file, 'w', encoding='utf-8') as f:
                    f.write(text)

                print(f"  SUCCESS: {char_count:,} chars -> {out_file.name}")
                results["success"].append({
                    "entry_id": entry_id,
                    "url": url,
                    "source_name": source_name,
                    "archive_path": f"data/sources/{entry_id}/{out_file.name}",
                    "chars": char_count
                })

        # Rate limiting
        time.sleep(1)

    print("\n" + "=" * 60)
    print(f"SUCCESS: {len(results['success'])} URLs fetched")
    print(f"FAILED: {len(results['failed'])} URLs")
    print("=" * 60)

    if results["failed"]:
        print("\nFailed URLs (these entries have other archived sources):")
        for item in results["failed"]:
            print(f"  {item['entry_id']}: {item['source_name']} - {item['error']}")

    # Save results
    results_file = base_path / "data" / "scrapfly_wayback_replacement_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")

if __name__ == "__main__":
    main()
