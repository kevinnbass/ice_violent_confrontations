#!/usr/bin/env python3
"""
Content Verification Script

Verifies that downloaded article content actually matches the incident details
claimed in the JSON database entries.

Checks:
1. Victim name appears in article (if provided)
2. Location (city/state) appears in article
3. Date or approximate timeframe appears
4. Key incident details (shooting, death, raid, etc.)

Also re-verifies the 20 "fabricated" entries using full pipeline.
"""

import json
import re
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from urllib.parse import urlparse, quote
import sys

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "incidents"
SOURCES_DIR = BASE_DIR / "data" / "sources"
FABRICATED_FILE = DATA_DIR / "fabricated_archive" / "FABRICATED_ENTRIES.json"
OUTPUT_DIR = BASE_DIR / "data" / "sources"

# Incident files
INCIDENT_FILES = [
    "tier1_deaths_in_custody.json",
    "tier2_shootings.json",
    "tier2_less_lethal.json",
    "tier3_incidents.json",
    "tier4_incidents.json"
]

class ContentVerifier:
    def __init__(self):
        self.results = []
        self.stats = defaultdict(int)

    def load_incidents(self) -> list[dict]:
        """Load all incidents from tier JSON files."""
        incidents = []
        for filename in INCIDENT_FILES:
            filepath = DATA_DIR / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both array format and object with entries key
                    if isinstance(data, list):
                        entries = data
                    else:
                        entries = data.get('entries', data.get('incidents', []))
                    for entry in entries:
                        entry['_source_file'] = filename
                    incidents.extend(entries)
                    print(f"Loaded {len(entries)} entries from {filename}")
        return incidents

    def load_fabricated(self) -> list[dict]:
        """Load the 20 flagged fabricated entries."""
        if FABRICATED_FILE.exists():
            with open(FABRICATED_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('entries', [])
        return []

    def get_article_text(self, entry_id: str) -> str | None:
        """Load downloaded article text for an entry."""
        text_file = SOURCES_DIR / entry_id / "article.txt"
        if text_file.exists():
            with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        return None

    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        if not text:
            return ""
        # Lowercase, remove extra whitespace
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        return text

    def check_name_in_text(self, name: str, text: str) -> dict:
        """Check if a name appears in the article text."""
        if not name or not text:
            return {"found": False, "method": None}

        text_norm = self.normalize_text(text)
        name_norm = self.normalize_text(name)

        # Try exact match
        if name_norm in text_norm:
            return {"found": True, "method": "exact"}

        # Try partial match (first and last name separately)
        name_parts = name_norm.split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = name_parts[-1]

            # Check if both first and last name appear
            if first_name in text_norm and last_name in text_norm:
                return {"found": True, "method": "partial_both"}

            # Check last name only (common in news)
            if len(last_name) > 3 and last_name in text_norm:
                return {"found": True, "method": "last_name_only"}

        # Try without hyphens/special chars
        name_simple = re.sub(r'[^a-z\s]', '', name_norm)
        if name_simple and name_simple in text_norm:
            return {"found": True, "method": "simplified"}

        return {"found": False, "method": None}

    def check_location_in_text(self, city: str, state: str, text: str) -> dict:
        """Check if location appears in article."""
        if not text:
            return {"found": False, "city_found": False, "state_found": False}

        text_norm = self.normalize_text(text)

        city_found = False
        state_found = False

        if city:
            city_norm = self.normalize_text(city)
            city_found = city_norm in text_norm

        if state:
            state_norm = self.normalize_text(state)
            state_found = state_norm in text_norm

            # Also check state abbreviations
            state_abbrevs = {
                "california": "ca", "texas": "tx", "florida": "fl",
                "new york": "ny", "arizona": "az", "colorado": "co",
                "georgia": "ga", "illinois": "il", "massachusetts": "ma",
                "michigan": "mi", "minnesota": "mn", "nevada": "nv",
                "new jersey": "nj", "north carolina": "nc", "ohio": "oh",
                "oklahoma": "ok", "oregon": "or", "pennsylvania": "pa",
                "tennessee": "tn", "virginia": "va", "washington": "wa",
                "wisconsin": "wi", "maryland": "md", "indiana": "in",
                "iowa": "ia", "new mexico": "nm", "utah": "ut",
                "south carolina": "sc", "louisiana": "la", "kentucky": "ky",
                "alabama": "al", "arkansas": "ar", "connecticut": "ct",
                "delaware": "de", "hawaii": "hi", "idaho": "id",
                "kansas": "ks", "maine": "me", "mississippi": "ms",
                "missouri": "mo", "montana": "mt", "nebraska": "ne",
                "new hampshire": "nh", "north dakota": "nd", "rhode island": "ri",
                "south dakota": "sd", "vermont": "vt", "west virginia": "wv",
                "wyoming": "wy", "alaska": "ak"
            }
            if not state_found and state_norm in state_abbrevs:
                abbrev = state_abbrevs[state_norm]
                # Look for abbreviation with word boundaries
                if re.search(rf'\b{abbrev}\b', text_norm):
                    state_found = True

        return {
            "found": city_found or state_found,
            "city_found": city_found,
            "state_found": state_found
        }

    def check_date_in_text(self, date_str: str, text: str) -> dict:
        """Check if date or approximate timeframe appears in article."""
        if not date_str or not text:
            return {"found": False, "method": None}

        text_norm = self.normalize_text(text)

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return {"found": False, "method": None}

        # Try various date formats
        formats_to_try = [
            date.strftime("%B %d, %Y").lower(),  # January 15, 2025
            date.strftime("%B %d").lower(),       # January 15
            date.strftime("%b %d, %Y").lower(),   # Jan 15, 2025
            date.strftime("%b %d").lower(),       # Jan 15
            date.strftime("%m/%d/%Y"),            # 01/15/2025
            date.strftime("%m/%d/%y"),            # 01/15/25
            date.strftime("%Y-%m-%d"),            # 2025-01-15
        ]

        for fmt in formats_to_try:
            if fmt in text_norm:
                return {"found": True, "method": "exact_date"}

        # Check for month + year
        month_year = date.strftime("%B %Y").lower()
        if month_year in text_norm:
            return {"found": True, "method": "month_year"}

        # Check for just the month name near the year
        month = date.strftime("%B").lower()
        year = str(date.year)
        if month in text_norm and year in text_norm:
            return {"found": True, "method": "month_and_year_separate"}

        return {"found": False, "method": None}

    def check_incident_keywords(self, entry: dict, text: str) -> dict:
        """Check if incident-related keywords appear in text."""
        if not text:
            return {"found": False, "keywords_found": []}

        text_norm = self.normalize_text(text)
        keywords_found = []

        # Keywords based on incident type
        incident_type = entry.get('incident_type', '').lower()
        outcome = self.normalize_text(entry.get('outcome', ''))

        # General ICE-related keywords
        ice_keywords = ['ice', 'immigration', 'customs enforcement', 'deportation',
                       'detained', 'detention', 'undocumented', 'migrant']

        # Incident-specific keywords
        type_keywords = {
            'death': ['died', 'death', 'dead', 'killed', 'fatal', 'deceased', 'passed away'],
            'shooting': ['shot', 'shooting', 'gunfire', 'firearm', 'wounded', 'bullet'],
            'less_lethal': ['taser', 'tased', 'pepper spray', 'tear gas', 'rubber bullet', 'baton'],
            'physical_force': ['force', 'assault', 'beaten', 'injured', 'pushed', 'tackled'],
            'wrongful_detention': ['citizen', 'wrongful', 'mistaken', 'released', 'lawsuit'],
            'mass_raid': ['raid', 'sweep', 'detained', 'arrested', 'workplace'],
            'protest': ['protest', 'demonstrat', 'rally', 'activist', 'march']
        }

        # Check ICE keywords
        for kw in ice_keywords:
            if kw in text_norm:
                keywords_found.append(kw)

        # Check type-specific keywords
        for itype, kws in type_keywords.items():
            if itype in incident_type or itype in outcome:
                for kw in kws:
                    if kw in text_norm:
                        keywords_found.append(kw)

        # Also check outcome text for keywords
        outcome_words = outcome.split()
        for word in outcome_words:
            if len(word) > 4 and word in text_norm:
                keywords_found.append(f"outcome:{word}")

        return {
            "found": len(keywords_found) >= 2,  # Need at least 2 relevant keywords
            "keywords_found": list(set(keywords_found))[:10]  # Dedupe, limit
        }

    def calculate_confidence(self, checks: dict) -> tuple[str, float]:
        """Calculate verification confidence score."""
        score = 0
        max_score = 0

        # Name match (if applicable)
        if checks.get('name_check'):
            max_score += 30
            if checks['name_check'].get('found'):
                method = checks['name_check'].get('method')
                if method == 'exact':
                    score += 30
                elif method == 'partial_both':
                    score += 25
                elif method == 'last_name_only':
                    score += 15
                elif method == 'simplified':
                    score += 20

        # Location match
        if checks.get('location_check'):
            max_score += 25
            loc = checks['location_check']
            if loc.get('city_found') and loc.get('state_found'):
                score += 25
            elif loc.get('city_found'):
                score += 20
            elif loc.get('state_found'):
                score += 10

        # Date match
        if checks.get('date_check'):
            max_score += 20
            if checks['date_check'].get('found'):
                method = checks['date_check'].get('method')
                if method == 'exact_date':
                    score += 20
                elif method == 'month_year':
                    score += 15
                else:
                    score += 10

        # Keyword match
        if checks.get('keyword_check'):
            max_score += 25
            kw_check = checks['keyword_check']
            if kw_check.get('found'):
                num_keywords = len(kw_check.get('keywords_found', []))
                score += min(25, num_keywords * 5)

        # Calculate percentage
        if max_score == 0:
            return "unknown", 0

        confidence = score / max_score

        if confidence >= 0.7:
            verdict = "verified"
        elif confidence >= 0.4:
            verdict = "likely_valid"
        elif confidence >= 0.2:
            verdict = "weak_match"
        else:
            verdict = "no_match"

        return verdict, round(confidence * 100, 1)

    def verify_entry(self, entry: dict) -> dict:
        """Verify a single entry against its article content."""
        entry_id = entry.get('id', 'unknown')

        result = {
            "id": entry_id,
            "source_file": entry.get('_source_file', 'unknown'),
            "source_url": entry.get('source_url', ''),
            "has_article": False,
            "checks": {},
            "verdict": "no_article",
            "confidence": 0,
            "details": {}
        }

        # Get article text
        article_text = self.get_article_text(entry_id)
        if not article_text:
            return result

        result["has_article"] = True
        result["article_length"] = len(article_text)

        # Perform checks
        checks = {}

        # Name check
        victim_name = entry.get('victim_name') or entry.get('name')
        if victim_name:
            checks['name_check'] = self.check_name_in_text(victim_name, article_text)
            result['details']['victim_name'] = victim_name

        # Location check
        city = entry.get('city', '')
        state = entry.get('state', '')
        checks['location_check'] = self.check_location_in_text(city, state, article_text)
        result['details']['location'] = f"{city}, {state}"

        # Date check
        date_str = entry.get('date', '')
        checks['date_check'] = self.check_date_in_text(date_str, article_text)
        result['details']['date'] = date_str

        # Keyword check
        checks['keyword_check'] = self.check_incident_keywords(entry, article_text)

        result['checks'] = checks

        # Calculate confidence
        verdict, confidence = self.calculate_confidence(checks)
        result['verdict'] = verdict
        result['confidence'] = confidence

        return result

    async def fetch_url_with_fallbacks(self, session: aiohttp.ClientSession, url: str) -> tuple[bool, str, str]:
        """Try to fetch URL using multiple methods."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }

        # Try direct fetch
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15), ssl=False) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    if len(text) > 1000:
                        return True, "direct", text
        except:
            pass

        # Try Wayback Machine
        try:
            cdx_url = f"https://web.archive.org/cdx/search/cdx?url={quote(url, safe='')}&output=json&limit=5"
            async with session.get(cdx_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if len(data) > 1:
                        timestamp = data[1][1]
                        archive_url = f"https://web.archive.org/web/{timestamp}/{url}"
                        async with session.get(archive_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as arch_resp:
                            if arch_resp.status == 200:
                                text = await arch_resp.text()
                                if len(text) > 1000:
                                    return True, f"wayback_{timestamp}", text
        except:
            pass

        # Try Google Cache
        try:
            cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{quote(url, safe='')}"
            async with session.get(cache_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    if len(text) > 1000 and 'did not match any documents' not in text.lower():
                        return True, "google_cache", text
        except:
            pass

        return False, "failed", ""

    async def verify_fabricated_entries(self, entries: list[dict]) -> list[dict]:
        """Re-verify the flagged fabricated entries."""
        print(f"\n{'='*60}")
        print("Re-verifying {0} flagged 'fabricated' entries...".format(len(entries)))
        print('='*60)

        results = []

        async with aiohttp.ClientSession() as session:
            for i, entry in enumerate(entries, 1):
                entry_id = entry.get('id', 'unknown')
                url = entry.get('source_url', '')

                print(f"\n[{i}/{len(entries)}] {entry_id}: {url[:60]}...")

                result = {
                    "id": entry_id,
                    "original_file": entry.get('original_file', ''),
                    "source_url": url,
                    "original_reason": entry.get('FABRICATION_REASON', ''),
                    "url_accessible": False,
                    "fetch_method": None,
                    "content_checks": {},
                    "final_verdict": "unverified",
                    "confidence": 0,
                    "details": entry
                }

                # Try to fetch the URL
                accessible, method, content = await self.fetch_url_with_fallbacks(session, url)

                if accessible:
                    result["url_accessible"] = True
                    result["fetch_method"] = method
                    result["content_length"] = len(content)
                    print(f"  [OK] URL accessible via {method}")

                    # Now verify content
                    checks = {}

                    # Name check
                    victim_name = entry.get('victim_name')
                    if victim_name:
                        checks['name_check'] = self.check_name_in_text(victim_name, content)
                        if checks['name_check']['found']:
                            print(f"  [OK] Name '{victim_name}' found ({checks['name_check']['method']})")
                        else:
                            print(f"  [--] Name '{victim_name}' NOT found")

                    # Location check
                    city = entry.get('city', '')
                    state = entry.get('state', '')
                    checks['location_check'] = self.check_location_in_text(city, state, content)
                    if checks['location_check']['found']:
                        print(f"  [OK] Location found (city={checks['location_check']['city_found']}, state={checks['location_check']['state_found']})")
                    else:
                        print(f"  [--] Location '{city}, {state}' NOT found")

                    # Date check
                    date_str = entry.get('date', '')
                    checks['date_check'] = self.check_date_in_text(date_str, content)
                    if checks['date_check']['found']:
                        print(f"  [OK] Date found ({checks['date_check']['method']})")
                    else:
                        print(f"  [--] Date '{date_str}' NOT found")

                    # Keyword check
                    checks['keyword_check'] = self.check_incident_keywords(entry, content)
                    if checks['keyword_check']['found']:
                        print(f"  [OK] Keywords: {', '.join(checks['keyword_check']['keywords_found'][:5])}")
                    else:
                        print(f"  [--] Insufficient keywords found")

                    result['content_checks'] = checks

                    # Calculate confidence
                    verdict, confidence = self.calculate_confidence(checks)
                    result['final_verdict'] = verdict
                    result['confidence'] = confidence
                    print(f"  => Verdict: {verdict} ({confidence}% confidence)")

                    # Save content if accessible
                    save_dir = SOURCES_DIR / entry_id
                    save_dir.mkdir(parents=True, exist_ok=True)
                    with open(save_dir / "article.html", 'w', encoding='utf-8') as f:
                        f.write(content)

                else:
                    print(f"  [FAIL] URL not accessible")
                    result["final_verdict"] = "url_inaccessible"

                results.append(result)

                # Small delay
                await asyncio.sleep(0.5)

        return results

    def run(self):
        """Run full verification."""
        print("="*60)
        print("CONTENT VERIFICATION")
        print("="*60)

        # Load all incidents
        incidents = self.load_incidents()
        print(f"\nTotal incidents to verify: {len(incidents)}")

        # Verify each incident
        print("\nVerifying content matches...")
        verified_results = []

        for i, entry in enumerate(incidents, 1):
            result = self.verify_entry(entry)
            verified_results.append(result)

            # Progress
            if i % 50 == 0:
                print(f"  Processed {i}/{len(incidents)}...")

        # Summarize verified entries
        print(f"\n{'='*60}")
        print("VERIFICATION SUMMARY - Main Database")
        print("="*60)

        verdicts = defaultdict(list)
        for r in verified_results:
            verdicts[r['verdict']].append(r)

        for verdict, items in sorted(verdicts.items()):
            print(f"  {verdict}: {len(items)}")

        # Load and re-verify fabricated entries
        fabricated = self.load_fabricated()
        fabricated_results = []

        if fabricated:
            fabricated_results = asyncio.run(self.verify_fabricated_entries(fabricated))

            print(f"\n{'='*60}")
            print("VERIFICATION SUMMARY - Previously Flagged 'Fabricated'")
            print("="*60)

            fab_verdicts = defaultdict(list)
            for r in fabricated_results:
                fab_verdicts[r['final_verdict']].append(r)

            for verdict, items in sorted(fab_verdicts.items()):
                print(f"  {verdict}: {len(items)}")

        # Save detailed results
        output = {
            "verification_date": datetime.now().isoformat(),
            "main_database": {
                "total": len(verified_results),
                "summary": {v: len(items) for v, items in verdicts.items()},
                "entries": verified_results
            },
            "fabricated_recheck": {
                "total": len(fabricated_results),
                "summary": {v: len(items) for v, items in fab_verdicts.items()} if fabricated_results else {},
                "entries": fabricated_results
            }
        }

        output_file = OUTPUT_DIR / "content_verification_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, default=str)

        print(f"\nDetailed report saved to: {output_file}")

        # Print entries that need attention
        print(f"\n{'='*60}")
        print("ENTRIES NEEDING ATTENTION")
        print("="*60)

        no_match = [r for r in verified_results if r['verdict'] == 'no_match' and r['has_article']]
        if no_match:
            print(f"\nNo content match found ({len(no_match)} entries):")
            for r in no_match[:20]:
                print(f"  - {r['id']}: {r['details'].get('victim_name', 'N/A')} | {r['details'].get('location', 'N/A')}")
                if r['checks'].get('keyword_check', {}).get('keywords_found'):
                    print(f"    Keywords found: {', '.join(r['checks']['keyword_check']['keywords_found'][:5])}")

        no_article = [r for r in verified_results if not r['has_article']]
        if no_article:
            print(f"\nNo article downloaded ({len(no_article)} entries):")
            for r in no_article[:10]:
                print(f"  - {r['id']}: {r['source_url'][:60]}...")

        # Fabricated that might be real
        if fabricated_results:
            might_be_real = [r for r in fabricated_results if r['confidence'] >= 40]
            if might_be_real:
                print(f"\nPreviously flagged but might be legitimate ({len(might_be_real)} entries):")
                for r in might_be_real:
                    print(f"  - {r['id']}: {r['final_verdict']} ({r['confidence']}%)")
                    print(f"    Original reason: {r['original_reason']}")

            confirmed_fabricated = [r for r in fabricated_results if r['final_verdict'] in ('url_inaccessible', 'no_match') or r['confidence'] < 20]
            if confirmed_fabricated:
                print(f"\nConfirmed likely fabricated ({len(confirmed_fabricated)} entries):")
                for r in confirmed_fabricated:
                    print(f"  - {r['id']}: {r['final_verdict']} ({r['confidence']}%)")

        return output


if __name__ == "__main__":
    verifier = ContentVerifier()
    verifier.run()
