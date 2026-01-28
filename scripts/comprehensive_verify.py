#!/usr/bin/env python3
"""
Comprehensive Source Verification with Checkpointing

Features:
- Downloads ALL articles (not just unique URLs)
- Checkpointing: can resume from where it left off
- Strong auditing: detailed logs for every decision
- Content verification: cross-references article text against claimed details
- Multiple fetch strategies: direct, stealth, Wayback, Google Cache
"""

import json
import csv
import asyncio
import aiohttp
import hashlib
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse, quote
from typing import Optional
import time

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "incidents"
SOURCES_DIR = BASE_DIR / "data" / "sources"
CHECKPOINT_FILE = SOURCES_DIR / "checkpoint.json"
AUDIT_LOG = SOURCES_DIR / "audit_log.jsonl"
FULL_REPORT = SOURCES_DIR / "full_verification_report.json"

# Incident files
INCIDENT_FILES = [
    "tier1_deaths_in_custody.json",
    "tier2_shootings.json",
    "tier2_less_lethal.json",
    "tier3_incidents.json",
    "tier4_incidents.json"
]

# Rate limiting
DOMAIN_DELAY = 1.0  # seconds between requests to same domain

class CheckpointManager:
    """Manages checkpointing for resumable operations."""

    def __init__(self, checkpoint_file: Path):
        self.file = checkpoint_file
        self.data = self._load()

    def _load(self) -> dict:
        if self.file.exists():
            with open(self.file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "started_at": None,
            "last_updated": None,
            "processed_ids": [],
            "failed_ids": [],
            "phase": "not_started"
        }

    def save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)

    def mark_processed(self, entry_id: str):
        if entry_id not in self.data["processed_ids"]:
            self.data["processed_ids"].append(entry_id)
        self.save()

    def mark_failed(self, entry_id: str):
        if entry_id not in self.data["failed_ids"]:
            self.data["failed_ids"].append(entry_id)
        self.save()

    def is_processed(self, entry_id: str) -> bool:
        return entry_id in self.data["processed_ids"]

    def set_phase(self, phase: str):
        self.data["phase"] = phase
        if phase == "started" and not self.data["started_at"]:
            self.data["started_at"] = datetime.now().isoformat()
        self.save()

    def reset(self):
        self.data = {
            "started_at": datetime.now().isoformat(),
            "last_updated": None,
            "processed_ids": [],
            "failed_ids": [],
            "phase": "started"
        }
        self.save()


class AuditLogger:
    """Logs every decision for troubleshooting."""

    def __init__(self, log_file: Path):
        self.file = log_file
        # Start fresh log
        self.file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, entry_id: str, event: str, details: dict = None):
        record = {
            "timestamp": datetime.now().isoformat(),
            "entry_id": entry_id,
            "event": event,
            "details": details or {}
        }
        with open(self.file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + "\n")

    def log_fetch_attempt(self, entry_id: str, url: str, method: str, success: bool,
                          status_code: int = None, error: str = None, content_length: int = None):
        self.log(entry_id, "fetch_attempt", {
            "url": url[:200],
            "method": method,
            "success": success,
            "status_code": status_code,
            "error": error[:200] if error else None,
            "content_length": content_length
        })

    def log_content_check(self, entry_id: str, check_type: str, expected: str,
                          found: bool, method: str = None):
        self.log(entry_id, "content_check", {
            "check_type": check_type,
            "expected": expected[:100] if expected else None,
            "found": found,
            "method": method
        })

    def log_verdict(self, entry_id: str, verdict: str, confidence: float, reasoning: str):
        self.log(entry_id, "verdict", {
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning
        })


class ComprehensiveVerifier:
    """Main verification class with all strategies."""

    def __init__(self):
        self.checkpoint = CheckpointManager(CHECKPOINT_FILE)
        self.audit = AuditLogger(AUDIT_LOG)
        self.domain_locks = defaultdict(asyncio.Lock)
        self.domain_last_request = defaultdict(float)
        self.results = []

        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]

    def load_all_incidents(self) -> list[dict]:
        """Load all incidents from all tier files."""
        incidents = []
        for filename in INCIDENT_FILES:
            filepath = DATA_DIR / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
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
        """Load fabricated entries for re-verification."""
        fab_file = DATA_DIR / "fabricated_archive" / "FABRICATED_ENTRIES.json"
        if fab_file.exists():
            with open(fab_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                entries = data.get('entries', [])
                for entry in entries:
                    entry['_source_file'] = 'fabricated_archive'
                return entries
        return []

    async def _rate_limit(self, domain: str):
        """Per-domain rate limiting."""
        async with self.domain_locks[domain]:
            now = time.time()
            elapsed = now - self.domain_last_request[domain]
            if elapsed < DOMAIN_DELAY:
                await asyncio.sleep(DOMAIN_DELAY - elapsed)
            self.domain_last_request[domain] = time.time()

    def _get_domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc
        except:
            return "unknown"

    async def fetch_with_strategies(self, session: aiohttp.ClientSession,
                                     entry_id: str, url: str) -> tuple[bool, str, str, str]:
        """
        Try multiple fetch strategies.
        Returns: (success, method, content, error)
        """
        domain = self._get_domain(url)

        strategies = [
            ("direct", self._fetch_direct),
            ("stealth", self._fetch_stealth),
            ("wayback", self._fetch_wayback),
            ("google_cache", self._fetch_google_cache),
        ]

        for method_name, fetch_func in strategies:
            await self._rate_limit(domain)

            try:
                success, content, error = await fetch_func(session, url)

                self.audit.log_fetch_attempt(
                    entry_id, url, method_name, success,
                    content_length=len(content) if content else 0,
                    error=error
                )

                if success and content and len(content) > 500:
                    return True, method_name, content, None

            except Exception as e:
                self.audit.log_fetch_attempt(
                    entry_id, url, method_name, False,
                    error=str(e)
                )

        return False, "all_failed", "", "All fetch strategies failed"

    async def _fetch_direct(self, session: aiohttp.ClientSession, url: str) -> tuple[bool, str, str]:
        """Direct fetch with basic headers."""
        headers = {
            'User-Agent': self.user_agents[0],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        try:
            async with session.get(url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=20),
                                   ssl=False) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    if len(content) > 500:
                        return True, content, None
                return False, "", f"HTTP {resp.status}"
        except Exception as e:
            return False, "", str(e)

    async def _fetch_stealth(self, session: aiohttp.ClientSession, url: str) -> tuple[bool, str, str]:
        """Stealth fetch with browser-like headers."""
        headers = {
            'User-Agent': self.user_agents[1],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        try:
            async with session.get(url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=20),
                                   ssl=False) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    if len(content) > 500:
                        return True, content, None
                return False, "", f"HTTP {resp.status}"
        except Exception as e:
            return False, "", str(e)

    async def _fetch_wayback(self, session: aiohttp.ClientSession, url: str) -> tuple[bool, str, str]:
        """Fetch from Wayback Machine."""
        try:
            # Get available snapshots
            cdx_url = f"https://web.archive.org/cdx/search/cdx?url={quote(url, safe='')}&output=json&limit=3"
            async with session.get(cdx_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return False, "", f"CDX HTTP {resp.status}"
                data = await resp.json()
                if len(data) <= 1:
                    return False, "", "No snapshots"

                # Try snapshots
                for row in data[1:]:
                    timestamp = row[1]
                    archive_url = f"https://web.archive.org/web/{timestamp}id_/{url}"

                    async with session.get(archive_url,
                                          timeout=aiohttp.ClientTimeout(total=20),
                                          ssl=False) as arch_resp:
                        if arch_resp.status == 200:
                            content = await arch_resp.text()
                            if len(content) > 500:
                                return True, content, None

                return False, "", "Snapshots not accessible"
        except Exception as e:
            return False, "", str(e)

    async def _fetch_google_cache(self, session: aiohttp.ClientSession, url: str) -> tuple[bool, str, str]:
        """Fetch from Google Cache."""
        cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{quote(url, safe='')}"
        headers = {
            'User-Agent': self.user_agents[2],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        try:
            async with session.get(cache_url, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=20),
                                   ssl=False) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    if len(content) > 500 and 'did not match any documents' not in content.lower():
                        return True, content, None
                return False, "", f"HTTP {resp.status}"
        except Exception as e:
            return False, "", str(e)

    def extract_text(self, html: str) -> str:
        """Extract readable text from HTML."""
        # Simple extraction - remove tags, normalize whitespace
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def verify_content(self, entry: dict, text: str) -> dict:
        """Verify that article content matches entry claims."""
        checks = {}
        text_lower = text.lower() if text else ""

        # Name check
        victim_name = entry.get('victim_name') or entry.get('name')
        if victim_name:
            name_lower = victim_name.lower()
            name_found = name_lower in text_lower

            # Try partial match
            method = None
            if name_found:
                method = "exact"
            else:
                parts = name_lower.split()
                if len(parts) >= 2:
                    if parts[0] in text_lower and parts[-1] in text_lower:
                        name_found = True
                        method = "partial"
                    elif parts[-1] in text_lower and len(parts[-1]) > 3:
                        name_found = True
                        method = "last_name"

            checks['name'] = {"expected": victim_name, "found": name_found, "method": method}
            self.audit.log_content_check(entry.get('id'), 'name', victim_name, name_found, method)

        # Location check
        city = entry.get('city', '')
        state = entry.get('state', '')
        city_found = city.lower() in text_lower if city else False
        state_found = state.lower() in text_lower if state else False

        checks['location'] = {
            "city": city, "state": state,
            "city_found": city_found, "state_found": state_found,
            "found": city_found or state_found
        }
        self.audit.log_content_check(entry.get('id'), 'location', f"{city}, {state}",
                                     city_found or state_found)

        # Date check
        date_str = entry.get('date', '')
        date_found = False
        if date_str:
            try:
                from datetime import datetime as dt
                date = dt.strptime(date_str, "%Y-%m-%d")
                date_patterns = [
                    date.strftime("%B %d, %Y").lower(),
                    date.strftime("%B %d").lower(),
                    date.strftime("%b %d, %Y").lower(),
                    date.strftime("%B %Y").lower(),
                ]
                for pattern in date_patterns:
                    if pattern in text_lower:
                        date_found = True
                        break
            except:
                pass

        checks['date'] = {"expected": date_str, "found": date_found}
        self.audit.log_content_check(entry.get('id'), 'date', date_str, date_found)

        # Keywords check
        keywords = ['ice', 'immigration', 'customs enforcement', 'detained', 'detention']
        incident_type = entry.get('incident_type', '').lower()
        if 'death' in incident_type or 'death' in entry.get('outcome', '').lower():
            keywords.extend(['died', 'death', 'dead', 'killed'])
        if 'shooting' in incident_type:
            keywords.extend(['shot', 'shooting', 'gunfire'])
        if 'raid' in incident_type or 'raid' in entry.get('outcome', '').lower():
            keywords.extend(['raid', 'raided', 'sweep'])

        found_keywords = [kw for kw in keywords if kw in text_lower]
        checks['keywords'] = {"found": found_keywords, "count": len(found_keywords)}

        return checks

    def calculate_verdict(self, entry: dict, url_accessible: bool,
                          fetch_method: str, checks: dict) -> tuple[str, float, str]:
        """Calculate final verdict and confidence."""
        if not url_accessible:
            return "url_inaccessible", 0, "Could not fetch URL with any method"

        score = 0
        max_score = 0
        reasoning_parts = []

        # URL accessible
        score += 20
        max_score += 20
        reasoning_parts.append(f"URL accessible via {fetch_method}")

        # Name check
        if 'name' in checks:
            max_score += 30
            if checks['name']['found']:
                method = checks['name']['method']
                if method == 'exact':
                    score += 30
                elif method == 'partial':
                    score += 25
                elif method == 'last_name':
                    score += 15
                reasoning_parts.append(f"Name found ({method})")
            else:
                reasoning_parts.append("Name NOT found")

        # Location check
        max_score += 20
        if checks.get('location', {}).get('found'):
            if checks['location'].get('city_found') and checks['location'].get('state_found'):
                score += 20
            elif checks['location'].get('city_found'):
                score += 15
            elif checks['location'].get('state_found'):
                score += 10
            reasoning_parts.append("Location found")
        else:
            reasoning_parts.append("Location NOT found")

        # Date check
        max_score += 15
        if checks.get('date', {}).get('found'):
            score += 15
            reasoning_parts.append("Date found")
        else:
            reasoning_parts.append("Date NOT found")

        # Keywords
        max_score += 15
        kw_count = checks.get('keywords', {}).get('count', 0)
        if kw_count >= 3:
            score += 15
        elif kw_count >= 2:
            score += 10
        elif kw_count >= 1:
            score += 5
        reasoning_parts.append(f"{kw_count} keywords found")

        # Calculate confidence
        confidence = round((score / max_score) * 100, 1) if max_score > 0 else 0

        # Determine verdict
        if confidence >= 70:
            verdict = "verified"
        elif confidence >= 50:
            verdict = "likely_valid"
        elif confidence >= 30:
            verdict = "weak_match"
        else:
            verdict = "no_match"

        reasoning = "; ".join(reasoning_parts)
        return verdict, confidence, reasoning

    async def process_entry(self, session: aiohttp.ClientSession, entry: dict) -> dict:
        """Process a single entry."""
        entry_id = entry.get('id', 'unknown')
        url = entry.get('source_url', '')

        result = {
            "id": entry_id,
            "source_file": entry.get('_source_file'),
            "source_url": url,
            "url_accessible": False,
            "fetch_method": None,
            "content_length": 0,
            "checks": {},
            "verdict": "not_processed",
            "confidence": 0,
            "reasoning": ""
        }

        if not url:
            result["verdict"] = "no_url"
            result["reasoning"] = "Entry has no source URL"
            self.audit.log_verdict(entry_id, "no_url", 0, "No source URL")
            return result

        # Fetch content
        success, method, content, error = await self.fetch_with_strategies(session, entry_id, url)

        result["url_accessible"] = success
        result["fetch_method"] = method

        if success:
            result["content_length"] = len(content)

            # Save content
            entry_dir = SOURCES_DIR / entry_id
            entry_dir.mkdir(parents=True, exist_ok=True)

            with open(entry_dir / "article.html", 'w', encoding='utf-8') as f:
                f.write(content)

            # Extract text
            text = self.extract_text(content)
            with open(entry_dir / "article.txt", 'w', encoding='utf-8') as f:
                f.write(text)

            # Verify content
            checks = self.verify_content(entry, text)
            result["checks"] = checks

            # Calculate verdict
            verdict, confidence, reasoning = self.calculate_verdict(
                entry, True, method, checks
            )
            result["verdict"] = verdict
            result["confidence"] = confidence
            result["reasoning"] = reasoning

            self.audit.log_verdict(entry_id, verdict, confidence, reasoning)
        else:
            result["verdict"] = "url_inaccessible"
            result["reasoning"] = error or "All fetch methods failed"
            self.audit.log_verdict(entry_id, "url_inaccessible", 0, error)

        return result

    async def run(self, reset: bool = False):
        """Run the full verification."""
        print("=" * 60)
        print("COMPREHENSIVE SOURCE VERIFICATION")
        print("=" * 60)

        if reset:
            print("\nResetting checkpoint...")
            self.checkpoint.reset()
            # Clear audit log
            if AUDIT_LOG.exists():
                AUDIT_LOG.unlink()

        self.checkpoint.set_phase("loading")

        # Load all incidents
        incidents = self.load_all_incidents()
        fabricated = self.load_fabricated()
        all_entries = incidents + fabricated

        print(f"\nTotal entries: {len(all_entries)}")
        print(f"  Main database: {len(incidents)}")
        print(f"  Fabricated archive: {len(fabricated)}")

        # Filter already processed
        to_process = [e for e in all_entries if not self.checkpoint.is_processed(e.get('id'))]
        print(f"  Already processed: {len(all_entries) - len(to_process)}")
        print(f"  To process: {len(to_process)}")

        if not to_process:
            print("\nAll entries already processed. Use --reset to start fresh.")
            return

        self.checkpoint.set_phase("fetching")

        # Process entries
        print(f"\nProcessing {len(to_process)} entries...")

        connector = aiohttp.TCPConnector(limit=20, limit_per_host=2)
        async with aiohttp.ClientSession(connector=connector) as session:
            for i, entry in enumerate(to_process, 1):
                entry_id = entry.get('id', 'unknown')
                url = entry.get('source_url', '')

                print(f"\n[{i}/{len(to_process)}] {entry_id}: {url[:50]}...")

                result = await self.process_entry(session, entry)
                self.results.append(result)

                # Print summary
                v = result['verdict']
                c = result['confidence']
                icon = "[OK]" if v in ('verified', 'likely_valid') else "[--]" if v == 'weak_match' else "[XX]"
                print(f"  {icon} {v} ({c}%)")

                # Update checkpoint
                self.checkpoint.mark_processed(entry_id)

                # Small delay
                await asyncio.sleep(0.1)

        self.checkpoint.set_phase("complete")

        # Generate report
        self._generate_report()

    def _generate_report(self):
        """Generate final report."""
        print("\n" + "=" * 60)
        print("VERIFICATION COMPLETE")
        print("=" * 60)

        # Load all results (including previously processed)
        all_results = self.results

        # Summary by verdict
        verdicts = defaultdict(list)
        for r in all_results:
            verdicts[r['verdict']].append(r)

        print("\nResults by verdict:")
        for v in ['verified', 'likely_valid', 'weak_match', 'no_match', 'url_inaccessible', 'no_url']:
            if v in verdicts:
                print(f"  {v}: {len(verdicts[v])}")

        # Summary by source file
        print("\nResults by source file:")
        by_file = defaultdict(lambda: defaultdict(int))
        for r in all_results:
            by_file[r.get('source_file', 'unknown')][r['verdict']] += 1

        for f, v_counts in sorted(by_file.items()):
            total = sum(v_counts.values())
            verified = v_counts.get('verified', 0) + v_counts.get('likely_valid', 0)
            print(f"  {f}: {verified}/{total} verified/likely_valid")

        # Entries needing attention
        print("\n" + "-" * 40)
        print("ENTRIES NEEDING ATTENTION")
        print("-" * 40)

        no_match = verdicts.get('no_match', [])
        if no_match:
            print(f"\nNo content match ({len(no_match)}):")
            for r in no_match[:10]:
                print(f"  - {r['id']}: {r['reasoning'][:60]}")

        inaccessible = verdicts.get('url_inaccessible', [])
        if inaccessible:
            print(f"\nURL inaccessible ({len(inaccessible)}):")
            for r in inaccessible[:10]:
                print(f"  - {r['id']}: {r['source_url'][:50]}...")

        # Save full report
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total": len(all_results),
                "by_verdict": {v: len(items) for v, items in verdicts.items()},
                "by_file": {f: dict(v) for f, v in by_file.items()}
            },
            "entries": all_results
        }

        with open(FULL_REPORT, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\nFull report: {FULL_REPORT}")
        print(f"Audit log: {AUDIT_LOG}")
        print(f"Checkpoint: {CHECKPOINT_FILE}")


async def main():
    reset = "--reset" in sys.argv
    verifier = ComprehensiveVerifier()
    await verifier.run(reset=reset)


if __name__ == "__main__":
    asyncio.run(main())
