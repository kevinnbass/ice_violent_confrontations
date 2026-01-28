#!/usr/bin/env python3
"""
Robust Source Verification with Exhaustive Keyword Matching

Updated for new sources array schema. Key features:
1. Uses LOCAL archived articles first (data/sources/{id}/article.txt)
2. Falls back to web fetch only if local not available
3. Supports multiple sources per entry (sources array)
4. Incident-type-specific keyword sets
5. Name variations and aliases
6. Date proximity validation
7. Weighted evidence scoring

Usage:
    python scripts/robust_verify.py [--reset] [--local-only] [--ids T1-D-001,T3-056]
    python scripts/robust_verify.py --download-missing   # Download first, then verify
"""

import json
import asyncio
import aiohttp
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from urllib.parse import urlparse, quote
from typing import Optional, List, Set, Dict, Tuple
import time
import argparse

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "incidents"
SOURCES_DIR = BASE_DIR / "data" / "sources"
CHECKPOINT_FILE = SOURCES_DIR / "robust_checkpoint.json"
AUDIT_LOG = SOURCES_DIR / "robust_audit.jsonl"
FULL_REPORT = SOURCES_DIR / "robust_verification_report.json"

# Incident files
INCIDENT_FILES = [
    "tier1_deaths_in_custody.json",
    "tier2_shootings.json",
    "tier2_less_lethal.json",
    "tier3_incidents.json",
    "tier4_incidents.json"
]

# Rate limiting
DOMAIN_DELAY = 1.0

# ============================================================
# EXHAUSTIVE KEYWORD DEFINITIONS
# ============================================================

# Core agency keywords - MUST appear for ICE-related content
AGENCY_KEYWORDS = {
    "primary": [
        "ice", "immigration and customs enforcement",
        "cbp", "customs and border protection", "border patrol",
        "dhs", "department of homeland security",
        "ero", "enforcement and removal operations",
        "immigration agent", "federal immigration", "federal agent"
    ],
    "secondary": [
        "immigration", "deportation", "deport", "detained", "detention",
        "undocumented", "illegal alien", "unlawfully present",
        "immigration enforcement", "enforcement operation", "immigration raid"
    ]
}

# Incident type specific keywords
INCIDENT_KEYWORDS = {
    "death_in_custody": {
        "critical": ["died", "death", "dead", "passed away", "deceased", "fatality", "fatal"],
        "supporting": [
            "custody", "detention center", "detention facility", "processing center",
            "medical", "hospital", "emergency", "unresponsive",
            "autopsy", "medical examiner", "cause of death",
            "neglect", "medical care", "health", "illness", "condition"
        ]
    },
    "shooting_by_agent": {
        "critical": ["shot", "shooting", "gunfire", "fired", "gunshot", "bullet"],
        "supporting": [
            "weapon", "firearm", "gun", "pistol", "rifle",
            "wounded", "injured", "killed", "fatal",
            "vehicle", "traffic stop", "pursuit", "chase",
            "suspect", "threat", "officer-involved"
        ]
    },
    "shooting_at_agent": {
        "critical": ["shot", "shooting", "gunfire", "fired", "attack", "ambush"],
        "supporting": [
            "officer", "agent", "facility", "wounded", "injured",
            "suspect", "attacker", "shooter"
        ]
    },
    "less_lethal": {
        "critical": ["taser", "tased", "pepper spray", "pepper ball", "rubber bullet",
                    "tear gas", "flash bang", "baton", "force"],
        "supporting": [
            "protest", "protester", "demonstrator", "activist",
            "injured", "injury", "hospital", "treated",
            "confrontation", "crowd", "dispersed"
        ]
    },
    "physical_force": {
        "critical": ["force", "assault", "attacked", "beaten", "struck", "pushed",
                    "shoved", "restrained", "choke", "tackle"],
        "supporting": [
            "injury", "injured", "hospitalized", "treated",
            "excessive", "brutal", "violent"
        ]
    },
    "mass_raid": {
        "critical": ["raid", "raided", "sweep", "operation", "arrested", "detained"],
        "supporting": [
            "workplace", "factory", "farm", "restaurant", "construction",
            "workers", "employees", "multiple", "dozen", "hundreds",
            "apartment", "neighborhood", "community"
        ]
    },
    "wrongful_detention": {
        "critical": ["wrongful", "mistaken", "error", "citizen", "legal resident",
                    "daca", "released", "lawsuit"],
        "supporting": [
            "detained", "held", "hours", "days", "identification",
            "documentation", "proof", "birth certificate", "passport"
        ]
    },
    "protest": {
        "critical": ["protest", "demonstration", "rally", "march", "activist"],
        "supporting": [
            "arrested", "detained", "dispersed", "confrontation",
            "signs", "chanting", "crowd", "police"
        ]
    },
    "veteran_detention": {
        "critical": ["veteran", "military", "served", "army", "navy", "marine",
                    "air force", "soldier"],
        "supporting": [
            "detained", "deported", "service", "deployment", "honorable"
        ]
    },
    "assault_on_officer_taser_response": {
        "critical": ["assault", "attacked", "struck", "hit", "taser", "tased"],
        "supporting": [
            "officer", "agent", "self-defense", "response", "subdued",
            "resisted", "arrested"
        ]
    }
}


def extract_entry_keywords(entry: dict) -> Set[str]:
    """Extract relevant keywords from entry fields."""
    keywords = set()
    text_fields = ['outcome', 'notes', 'circumstances', 'outcome_detail']

    for field in text_fields:
        text = entry.get(field, '')
        if not text:
            continue
        text_lower = text.lower()

        common_words = {'that', 'this', 'with', 'from', 'were', 'been', 'have',
                       'their', 'which', 'would', 'there', 'about', 'into',
                       'them', 'than', 'then', 'some', 'what', 'when', 'your',
                       'said', 'each', 'after', 'before', 'during', 'being',
                       'verified', 'exhaustive'}

        words = re.findall(r'\b[a-z]{4,}\b', text_lower)
        for word in words:
            if word not in common_words:
                keywords.add(word)

        numbers = re.findall(r'\b\d+\b', text)
        for num in numbers:
            if len(num) <= 3:
                keywords.add(num)

        names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', entry.get(field, ''))
        for name in names:
            keywords.add(name.lower())

    if entry.get('victim_age'):
        keywords.add(str(entry['victim_age']))
    if entry.get('victim_nationality'):
        keywords.add(entry['victim_nationality'].lower())
    if entry.get('agency'):
        keywords.add(entry['agency'].lower())

    return keywords


def get_name_variations(name: str) -> List[str]:
    """Generate name variations for matching."""
    if not name:
        return []

    variations = [name.lower()]
    parts = name.split()

    if len(parts) >= 2:
        variations.append(f"{parts[0]} {parts[-1]}".lower())
        variations.append(f"{parts[-1]}, {parts[0]}".lower())
        if len(parts[-1]) >= 4:
            variations.append(parts[-1].lower())
        if len(parts[0]) >= 4:
            variations.append(parts[0].lower())

    if '-' in name:
        variations.append(name.replace('-', ' ').lower())
        for part in name.split('-'):
            if len(part) >= 4:
                variations.append(part.lower())

    return list(set(variations))


def check_date_proximity(article_text: str, target_date: str, tolerance_days: int = 30) -> dict:
    """Check if article mentions dates near the target date."""
    result = {"found": False, "exact": False, "proximity": None, "matches": []}

    if not target_date:
        return result

    try:
        target = datetime.strptime(target_date, "%Y-%m-%d")
    except:
        for fmt in ["%Y-%m", "%Y"]:
            try:
                target = datetime.strptime(target_date, fmt)
                break
            except:
                continue
        else:
            return result

    text_lower = article_text.lower()

    months = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12,
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }

    pattern = r'\b(' + '|'.join(months.keys()) + r')\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})?\b'

    for match in re.finditer(pattern, text_lower):
        month_name = match.group(1)
        day = int(match.group(2))
        year = int(match.group(3)) if match.group(3) else target.year
        month = months.get(month_name.lower())

        if month and 1 <= day <= 31:
            try:
                article_date = datetime(year, month, day)
                diff = abs((article_date - target).days)

                if diff == 0:
                    result["exact"] = True
                    result["found"] = True
                    result["matches"].append(match.group(0))
                elif diff <= tolerance_days:
                    result["found"] = True
                    if result["proximity"] is None or diff < result["proximity"]:
                        result["proximity"] = diff
                    result["matches"].append(match.group(0))
            except:
                pass

    return result


class RobustVerifier:
    """Robust verification with local-first approach and multiple sources support."""

    def __init__(self, local_only: bool = False, specific_ids: List[str] = None,
                 download_missing: bool = False):
        self.local_only = local_only
        self.specific_ids = specific_ids
        self.download_missing = download_missing
        self.checkpoint = self._load_checkpoint()
        self.results = []
        self.domain_locks = defaultdict(asyncio.Lock)
        self.domain_last_request = defaultdict(float)
        self.download_progress = {"completed": 0, "total": 0}
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]

    def _load_checkpoint(self) -> dict:
        if CHECKPOINT_FILE.exists():
            with open(CHECKPOINT_FILE, 'r') as f:
                return json.load(f)
        return {"processed_ids": [], "started_at": None}

    def _save_checkpoint(self):
        self.checkpoint["last_updated"] = datetime.now().isoformat()
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)

    def _log_audit(self, entry_id: str, event: str, details: dict):
        record = {
            "timestamp": datetime.now().isoformat(),
            "entry_id": entry_id,
            "event": event,
            "details": details
        }
        with open(AUDIT_LOG, 'a') as f:
            f.write(json.dumps(record) + "\n")

    def get_sources_from_entry(self, entry: dict) -> List[dict]:
        """Extract sources from entry, supporting both old and new schema."""
        # New schema: sources array
        if 'sources' in entry:
            return entry['sources']

        # Old schema: flat fields (backward compatibility)
        if entry.get('source_url'):
            return [{
                'url': entry.get('source_url'),
                'name': entry.get('source_name'),
                'tier': entry.get('source_tier'),
                'primary': True
            }]

        return []

    def get_local_article(self, entry_id: str) -> Tuple[bool, str, str]:
        """
        Try to load article from local archive first.
        Returns: (success, content, source_path)
        """
        entry_dir = SOURCES_DIR / entry_id

        # Try article.txt first (plain text, preferred)
        article_txt = entry_dir / "article.txt"
        if article_txt.exists():
            try:
                content = article_txt.read_text(encoding='utf-8')
                if len(content) > 200:  # Minimum viable content
                    return True, content, str(article_txt)
            except Exception as e:
                pass

        # Try retry_stealth version
        stealth_txt = entry_dir / "article_retry_stealth.txt"
        if stealth_txt.exists():
            try:
                content = stealth_txt.read_text(encoding='utf-8')
                if len(content) > 200:
                    return True, content, str(stealth_txt)
            except:
                pass

        # Try HTML files and extract text
        for html_file in [entry_dir / "article.html", entry_dir / "article_retry_stealth.html"]:
            if html_file.exists():
                try:
                    html_content = html_file.read_text(encoding='utf-8')
                    text = self.extract_text(html_content)
                    if len(text) > 200:
                        return True, text, str(html_file)
                except:
                    pass

        return False, "", ""

    def load_all_incidents(self) -> list:
        incidents = []
        for filename in INCIDENT_FILES:
            filepath = DATA_DIR / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    entries = data if isinstance(data, list) else data.get('entries', [])
                    for e in entries:
                        e['_source_file'] = filename
                    incidents.extend(entries)
                    print(f"Loaded {len(entries)} from {filename}")
        return incidents

    async def _rate_limit(self, domain: str):
        async with self.domain_locks[domain]:
            now = time.time()
            elapsed = now - self.domain_last_request[domain]
            if elapsed < DOMAIN_DELAY:
                await asyncio.sleep(DOMAIN_DELAY - elapsed)
            self.domain_last_request[domain] = time.time()

    async def fetch_article(self, session: aiohttp.ClientSession,
                           entry_id: str, url: str) -> tuple:
        """Fetch article from web with multiple strategies."""
        domain = urlparse(url).netloc

        strategies = [
            ("direct", self._fetch_direct),
            ("stealth", self._fetch_stealth),
            ("wayback", self._fetch_wayback),
        ]

        for method, fetch_fn in strategies:
            await self._rate_limit(domain)
            try:
                success, content, error = await fetch_fn(session, url)
                if success and content and len(content) > 500:
                    self._log_audit(entry_id, "fetch_success", {"method": method, "length": len(content)})
                    return True, method, content
            except Exception as e:
                self._log_audit(entry_id, "fetch_error", {"method": method, "error": str(e)[:200]})

        return False, "failed", ""

    async def _fetch_direct(self, session, url):
        headers = {'User-Agent': self.user_agents[0]}
        try:
            async with session.get(url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=20), ssl=False) as r:
                if r.status == 200:
                    return True, await r.text(), None
                return False, "", f"HTTP {r.status}"
        except Exception as e:
            return False, "", str(e)

    async def _fetch_stealth(self, session, url):
        headers = {
            'User-Agent': self.user_agents[1],
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        try:
            async with session.get(url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=20), ssl=False) as r:
                if r.status == 200:
                    return True, await r.text(), None
                return False, "", f"HTTP {r.status}"
        except Exception as e:
            return False, "", str(e)

    async def _fetch_wayback(self, session, url):
        try:
            cdx_url = f"https://web.archive.org/cdx/search/cdx?url={quote(url, safe='')}&output=json&limit=3"
            async with session.get(cdx_url, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status != 200:
                    return False, "", "CDX failed"
                data = await r.json()
                if len(data) <= 1:
                    return False, "", "No snapshots"

                for row in data[1:]:
                    ts = row[1]
                    arch_url = f"https://web.archive.org/web/{ts}id_/{url}"
                    async with session.get(arch_url, timeout=aiohttp.ClientTimeout(total=20), ssl=False) as ar:
                        if ar.status == 200:
                            content = await ar.text()
                            if len(content) > 500:
                                return True, content, None
                return False, "", "Archives not accessible"
        except Exception as e:
            return False, "", str(e)

    # ============================================================
    # HIGH-CONCURRENCY DOWNLOAD PHASE
    # ============================================================

    def find_missing_archives(self, incidents: list) -> list:
        """Find entries that don't have local archives."""
        missing = []
        for entry in incidents:
            entry_id = entry.get('id', '')
            sources = self.get_sources_from_entry(entry)
            if not sources:
                continue

            # Check if local archive exists
            entry_dir = SOURCES_DIR / entry_id
            article_txt = entry_dir / "article.txt"
            if not article_txt.exists() or article_txt.stat().st_size < 200:
                # Get primary source URL
                primary = next((s for s in sources if s.get('primary')), sources[0])
                url = primary.get('url', '')
                if url:
                    missing.append({
                        'id': entry_id,
                        'url': url,
                        'domain': urlparse(url).netloc
                    })
        return missing

    async def download_single(self, session: aiohttp.ClientSession, item: dict) -> dict:
        """Download a single article with rate limiting per domain."""
        entry_id = item['id']
        url = item['url']
        domain = item['domain']

        # Rate limit per domain
        await self._rate_limit(domain)

        result = {'id': entry_id, 'url': url, 'success': False, 'method': None, 'error': None}

        # Try multiple strategies
        strategies = [
            ("direct", self._fetch_direct),
            ("stealth", self._fetch_stealth),
            ("wayback", self._fetch_wayback),
        ]

        for method, fetch_fn in strategies:
            try:
                if method != "direct":
                    await self._rate_limit(domain if method == "stealth" else "archive.org")

                success, content, error = await fetch_fn(session, url)

                if success and content and len(content) > 500:
                    # Save content
                    text = self.extract_text(content)
                    if len(text) > 200:
                        entry_dir = SOURCES_DIR / entry_id
                        entry_dir.mkdir(parents=True, exist_ok=True)

                        # Save both HTML and text
                        with open(entry_dir / "article.html", 'w', encoding='utf-8') as f:
                            f.write(content)
                        with open(entry_dir / "article.txt", 'w', encoding='utf-8') as f:
                            f.write(text)

                        result['success'] = True
                        result['method'] = method
                        result['length'] = len(text)
                        break
            except Exception as e:
                result['error'] = str(e)[:100]
                continue

        # Update progress
        self.download_progress["completed"] += 1
        completed = self.download_progress["completed"]
        total = self.download_progress["total"]
        status = "[OK]" if result['success'] else "[FAIL]"
        method_str = result.get('method', 'none')
        print(f"  [{completed}/{total}] {entry_id}: {status} {method_str}")

        return result

    async def download_missing_phase(self, session: aiohttp.ClientSession, missing: list) -> dict:
        """Download all missing archives with high concurrency across domains."""
        print("\n" + "=" * 60)
        print("PHASE 1: DOWNLOADING MISSING ARCHIVES")
        print("=" * 60)
        print(f"Entries missing local archives: {len(missing)}")

        if not missing:
            print("All entries have local archives. Skipping download phase.")
            return {"downloaded": 0, "failed": 0}

        # Count unique domains
        domains = set(item['domain'] for item in missing)
        print(f"Unique domains: {len(domains)}")
        print("Concurrency: UNLIMITED across domains, rate-limited within each domain")
        print()

        self.download_progress = {"completed": 0, "total": len(missing)}

        # Create all download tasks - they will self-rate-limit per domain
        tasks = [self.download_single(session, item) for item in missing]

        # Run all concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        elapsed = time.time() - start_time

        # Summarize
        successful = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
        failed = len(missing) - successful

        print(f"\nDownload phase complete in {elapsed:.1f}s")
        print(f"  Successfully downloaded: {successful}")
        print(f"  Failed: {failed}")

        return {"downloaded": successful, "failed": failed}

    def extract_text(self, html: str) -> str:
        """Extract text from HTML."""
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.I)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.I)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def verify_content(self, entry: dict, text: str) -> dict:
        """Comprehensive content verification."""
        text_lower = text.lower()
        checks = {
            "agency": {"found": False, "matches": []},
            "name": {"found": False, "method": None, "matches": []},
            "location": {"found": False, "city": False, "state": False},
            "date": {"found": False, "exact": False, "proximity": None},
            "incident_keywords": {"critical_found": 0, "critical_required": 0,
                                 "supporting_found": 0, "matches": []},
            "entry_keywords": {"found": 0, "total": 0, "matches": []}
        }

        # 1. AGENCY CHECK
        for kw in AGENCY_KEYWORDS["primary"]:
            if kw in text_lower:
                checks["agency"]["found"] = True
                checks["agency"]["matches"].append(kw)

        if not checks["agency"]["found"]:
            for kw in AGENCY_KEYWORDS["secondary"]:
                if kw in text_lower:
                    checks["agency"]["matches"].append(kw)
            if len(checks["agency"]["matches"]) >= 2:
                checks["agency"]["found"] = True

        # 2. NAME CHECK with variations
        victim_name = entry.get('victim_name') or entry.get('name', '')
        if victim_name and 'unknown' not in victim_name.lower() and 'multiple' not in victim_name.lower():
            variations = get_name_variations(victim_name)
            for var in variations:
                if var in text_lower:
                    checks["name"]["found"] = True
                    checks["name"]["matches"].append(var)
                    if var == victim_name.lower():
                        checks["name"]["method"] = "exact"
                    elif len(var.split()) >= 2:
                        checks["name"]["method"] = "partial"
                    else:
                        checks["name"]["method"] = "fragment"
        else:
            checks["name"]["method"] = "not_applicable"
            checks["name"]["found"] = True

        # 3. LOCATION CHECK
        city = entry.get('city', '')
        state = entry.get('state', '')

        if city:
            city_clean = re.sub(r'\([^)]+\)', '', city).strip()
            city_parts = [city_clean.lower()]
            if '/' in city:
                city_parts.extend([p.strip().lower() for p in city.split('/')])
            for cp in city_parts:
                if cp and len(cp) > 2 and cp in text_lower:
                    checks["location"]["city"] = True
                    break

        if state:
            checks["location"]["state"] = state.lower() in text_lower

        checks["location"]["found"] = checks["location"]["city"] or checks["location"]["state"]

        # 4. DATE CHECK
        date_str = entry.get('date', '')
        date_check = check_date_proximity(text, date_str)
        checks["date"] = date_check

        # 5. INCIDENT TYPE KEYWORDS
        incident_type = entry.get('incident_type', '').lower().replace('-', '_').replace(' ', '_')

        keyword_set = None
        for key in INCIDENT_KEYWORDS:
            if key in incident_type or incident_type in key:
                keyword_set = INCIDENT_KEYWORDS[key]
                break

        if not keyword_set:
            outcome = (entry.get('outcome', '') + ' ' + entry.get('outcome_detail', '')).lower()
            if 'death' in outcome or 'died' in outcome:
                keyword_set = INCIDENT_KEYWORDS["death_in_custody"]
            elif 'shot' in outcome or 'shooting' in outcome:
                keyword_set = INCIDENT_KEYWORDS["shooting_by_agent"]
            elif 'raid' in outcome:
                keyword_set = INCIDENT_KEYWORDS["mass_raid"]
            elif 'protest' in outcome:
                keyword_set = INCIDENT_KEYWORDS["protest"]
            else:
                keyword_set = {"critical": [], "supporting": []}

        if keyword_set:
            critical = keyword_set.get("critical", [])
            supporting = keyword_set.get("supporting", [])
            checks["incident_keywords"]["critical_required"] = min(2, len(critical))

            for kw in critical:
                if kw in text_lower:
                    checks["incident_keywords"]["critical_found"] += 1
                    checks["incident_keywords"]["matches"].append(f"critical:{kw}")

            for kw in supporting:
                if kw in text_lower:
                    checks["incident_keywords"]["supporting_found"] += 1
                    checks["incident_keywords"]["matches"].append(f"supporting:{kw}")

        # 6. ENTRY-SPECIFIC KEYWORDS
        entry_kws = extract_entry_keywords(entry)
        checks["entry_keywords"]["total"] = len(entry_kws)

        for kw in entry_kws:
            if kw in text_lower:
                checks["entry_keywords"]["found"] += 1
                if len(checks["entry_keywords"]["matches"]) < 10:
                    checks["entry_keywords"]["matches"].append(kw)

        return checks

    def calculate_verdict(self, entry: dict, url_ok: bool, method: str, checks: dict) -> tuple:
        """Calculate verdict with weighted scoring."""
        if not url_ok:
            return "url_inaccessible", 0, "Could not fetch article"

        score = 0
        max_score = 100
        reasons = []

        # Agency mention (20 points)
        if checks["agency"]["found"]:
            score += 20
            reasons.append(f"Agency: {len(checks['agency']['matches'])} matches")
        else:
            reasons.append("Agency: NOT FOUND (critical)")
            return "no_match", score, "; ".join(reasons)

        # Name match (25 points)
        if checks["name"]["method"] == "not_applicable":
            score += 25
            reasons.append("Name: N/A")
        elif checks["name"]["found"]:
            method = checks["name"]["method"]
            if method == "exact":
                score += 25
            elif method == "partial":
                score += 20
            else:
                score += 12
            reasons.append(f"Name: {method}")
        else:
            reasons.append("Name: NOT FOUND")

        # Location (15 points)
        if checks["location"]["found"]:
            if checks["location"]["city"] and checks["location"]["state"]:
                score += 15
            elif checks["location"]["city"]:
                score += 12
            else:
                score += 8
            reasons.append("Location: found")
        else:
            reasons.append("Location: NOT FOUND")

        # Date (15 points)
        if checks["date"]["exact"]:
            score += 15
            reasons.append("Date: exact match")
        elif checks["date"]["found"]:
            prox = checks["date"].get("proximity", 30)
            if prox and prox <= 7:
                score += 12
            elif prox and prox <= 14:
                score += 8
            else:
                score += 5
            reasons.append(f"Date: within {prox} days")
        else:
            reasons.append("Date: NOT FOUND")

        # Incident keywords (15 points)
        critical_found = checks["incident_keywords"]["critical_found"]
        critical_req = checks["incident_keywords"]["critical_required"]
        supporting = checks["incident_keywords"]["supporting_found"]

        if critical_req > 0 and critical_found >= critical_req:
            score += 10
            reasons.append(f"Critical keywords: {critical_found}")
        elif critical_found > 0:
            score += 5
            reasons.append(f"Critical keywords: partial ({critical_found})")
        else:
            reasons.append("Critical keywords: NONE")

        if supporting >= 3:
            score += 5
        elif supporting >= 1:
            score += 2
        reasons.append(f"Supporting: {supporting}")

        # Entry-specific keywords (10 points)
        entry_found = checks["entry_keywords"]["found"]
        entry_total = checks["entry_keywords"]["total"]
        if entry_total > 0:
            ratio = entry_found / entry_total
            if ratio >= 0.3:
                score += 10
            elif ratio >= 0.15:
                score += 5
            elif ratio > 0:
                score += 2
            reasons.append(f"Entry keywords: {entry_found}/{entry_total}")

        # Determine verdict
        confidence = round((score / max_score) * 100, 1)

        if confidence >= 70:
            verdict = "verified"
        elif confidence >= 50:
            verdict = "likely_valid"
        elif confidence >= 35:
            verdict = "weak_match"
        else:
            verdict = "no_match"

        return verdict, confidence, "; ".join(reasons)

    async def process_entry(self, session: aiohttp.ClientSession, entry: dict) -> dict:
        """Process single entry with local-first approach."""
        entry_id = entry.get('id', 'unknown')
        sources = self.get_sources_from_entry(entry)

        result = {
            "id": entry_id,
            "source_file": entry.get('_source_file'),
            "sources_count": len(sources),
            "verdict": "not_processed",
            "confidence": 0,
            "reasoning": "",
            "checks": {},
            "source_used": None,
            "fetch_method": None
        }

        if not sources:
            result["verdict"] = "no_url"
            result["reasoning"] = "No sources defined"
            return result

        # Try local archive FIRST
        local_ok, local_content, local_path = self.get_local_article(entry_id)

        if local_ok:
            self._log_audit(entry_id, "local_archive_found", {"path": local_path, "length": len(local_content)})
            text = local_content
            result["fetch_method"] = "local_archive"
            result["source_used"] = local_path
        elif self.local_only:
            result["verdict"] = "no_local_archive"
            result["reasoning"] = "Local archive not found (--local-only mode)"
            return result
        else:
            # Fall back to web fetch - try primary source first
            primary_source = next((s for s in sources if s.get('primary')), sources[0])
            url = primary_source.get('url', '')

            if not url:
                result["verdict"] = "no_url"
                result["reasoning"] = "No valid URL in sources"
                return result

            success, method, content = await self.fetch_article(session, entry_id, url)

            if not success:
                result["verdict"] = "url_inaccessible"
                result["reasoning"] = "All fetch methods failed"
                return result

            text = self.extract_text(content)
            result["fetch_method"] = f"web_{method}"
            result["source_used"] = url

            # Save fetched content for future local use
            entry_dir = SOURCES_DIR / entry_id
            entry_dir.mkdir(parents=True, exist_ok=True)
            with open(entry_dir / "article.txt", 'w', encoding='utf-8') as f:
                f.write(text)

        # Verify content
        checks = self.verify_content(entry, text)
        result["checks"] = checks

        # Calculate verdict
        verdict, confidence, reasoning = self.calculate_verdict(entry, True, result["fetch_method"], checks)
        result["verdict"] = verdict
        result["confidence"] = confidence
        result["reasoning"] = reasoning

        self._log_audit(entry_id, "verdict", {
            "verdict": verdict,
            "confidence": confidence,
            "fetch_method": result["fetch_method"],
            "checks_summary": {
                "agency": checks["agency"]["found"],
                "name": checks["name"]["found"],
                "location": checks["location"]["found"],
                "date": checks["date"]["found"],
                "critical_kw": checks["incident_keywords"]["critical_found"],
                "supporting_kw": checks["incident_keywords"]["supporting_found"]
            }
        })

        return result

    async def run(self, reset: bool = False):
        """Run verification."""
        print("=" * 60)
        print("ROBUST SOURCE VERIFICATION (Local-First)")
        print("=" * 60)
        print(f"Local-only mode: {self.local_only}")
        print(f"Download missing: {self.download_missing}")
        if self.specific_ids:
            print(f"Specific IDs: {self.specific_ids}")

        if reset:
            self.checkpoint = {"processed_ids": [], "started_at": datetime.now().isoformat()}
            if AUDIT_LOG.exists():
                AUDIT_LOG.unlink()

        if not self.checkpoint.get("started_at"):
            self.checkpoint["started_at"] = datetime.now().isoformat()

        # Load incidents
        incidents = self.load_all_incidents()
        print(f"\nTotal entries: {len(incidents)}")

        # Filter to specific IDs if provided
        if self.specific_ids:
            incidents = [e for e in incidents if e.get('id') in self.specific_ids]
            print(f"Filtered to {len(incidents)} specific entries")

        # High concurrency connector for download phase
        download_connector = aiohttp.TCPConnector(limit=100, limit_per_host=5)

        # If --download-missing, run download phase first
        if self.download_missing:
            async with aiohttp.ClientSession(connector=download_connector) as session:
                missing = self.find_missing_archives(incidents)
                await self.download_missing_phase(session, missing)

            print("\n" + "=" * 60)
            print("PHASE 2: VERIFICATION")
            print("=" * 60)

        # Filter processed (unless specific IDs provided)
        if not self.specific_ids:
            to_process = [e for e in incidents if e.get('id') not in self.checkpoint["processed_ids"]]
        else:
            to_process = incidents

        print(f"Already processed: {len(incidents) - len(to_process)}")
        print(f"To process: {len(to_process)}")

        if not to_process:
            print("\nAll processed. Use --reset to start fresh.")
            self._generate_report()
            return

        # Process with lower concurrency for verification
        verify_connector = aiohttp.TCPConnector(limit=20, limit_per_host=2)
        async with aiohttp.ClientSession(connector=verify_connector) as session:
            for i, entry in enumerate(to_process, 1):
                entry_id = entry.get('id', 'unknown')

                # Get primary source URL for display
                sources = self.get_sources_from_entry(entry)
                url_display = sources[0].get('url', '')[:40] if sources else 'no-url'

                print(f"\n[{i}/{len(to_process)}] {entry_id}: {url_display}...")

                result = await self.process_entry(session, entry)
                self.results.append(result)

                v = result['verdict']
                c = result['confidence']
                m = result.get('fetch_method', 'unknown')
                icon = "[OK]" if v in ('verified', 'likely_valid') else "[??]" if v == 'weak_match' else "[XX]"
                print(f"  {icon} {v} ({c}%) via {m}")
                print(f"      {result['reasoning'][:70]}")

                if not self.specific_ids:
                    self.checkpoint["processed_ids"].append(entry_id)
                    self._save_checkpoint()

                await asyncio.sleep(0.05)

        self._generate_report()

    def _generate_report(self):
        """Generate verification report."""
        print("\n" + "=" * 60)
        print("VERIFICATION COMPLETE")
        print("=" * 60)

        verdicts = defaultdict(list)
        fetch_methods = defaultdict(int)

        for r in self.results:
            verdicts[r['verdict']].append(r)
            if r.get('fetch_method'):
                fetch_methods[r['fetch_method']] += 1

        print("\nResults by verdict:")
        for v in ['verified', 'likely_valid', 'weak_match', 'no_match', 'url_inaccessible', 'no_local_archive', 'no_url']:
            if v in verdicts:
                print(f"  {v}: {len(verdicts[v])}")

        print("\nFetch methods used:")
        for m, count in sorted(fetch_methods.items()):
            print(f"  {m}: {count}")

        # Problem entries
        problems = verdicts.get('no_match', []) + verdicts.get('weak_match', [])
        if problems:
            print(f"\n--- ENTRIES NEEDING REVIEW ({len(problems)}) ---")
            for r in problems[:15]:
                print(f"  {r['id']}: {r['verdict']} ({r['confidence']}%)")

        # Save report
        report = {
            "generated_at": datetime.now().isoformat(),
            "config": {
                "local_only": self.local_only,
                "specific_ids": self.specific_ids
            },
            "summary": {v: len(items) for v, items in verdicts.items()},
            "fetch_methods": dict(fetch_methods),
            "entries": self.results
        }

        with open(FULL_REPORT, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\nReport saved: {FULL_REPORT}")


async def main():
    parser = argparse.ArgumentParser(description="Robust source verification with local-first approach")
    parser.add_argument("--reset", action="store_true", help="Reset and start fresh")
    parser.add_argument("--local-only", action="store_true", help="Only use local archives, no web fetching")
    parser.add_argument("--download-missing", action="store_true",
                        help="Download missing archives first (high concurrency), then verify")
    parser.add_argument("--ids", type=str, help="Comma-separated list of specific entry IDs to verify")

    args = parser.parse_args()

    if args.local_only and args.download_missing:
        print("ERROR: --local-only and --download-missing are mutually exclusive")
        sys.exit(1)

    specific_ids = args.ids.split(',') if args.ids else None

    verifier = RobustVerifier(
        local_only=args.local_only,
        specific_ids=specific_ids,
        download_missing=args.download_missing
    )
    await verifier.run(reset=args.reset)


if __name__ == "__main__":
    asyncio.run(main())
