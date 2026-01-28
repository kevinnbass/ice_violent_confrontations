#!/usr/bin/env python3
"""
Source Article Scraper for ICE Incidents Database

Downloads and archives all source articles from incident JSON files.
Provides local backup and verification of cited sources.

CONCURRENT SCRAPING:
- Unlimited concurrency across different domains
- Sequential scraping within the same domain (rate limiting)
- Per-domain locks to avoid overwhelming any single server

RIGOROUS VERIFICATION:
- Multiple retry attempts with different strategies
- Archive.org Wayback Machine fallback for failed URLs
- DNS verification before marking domains as invalid
- Confidence scoring to distinguish "definitely fabricated" from "temporarily down"

Output:
- data/sources/{entry_id}/article.html - Raw HTML
- data/sources/{entry_id}/article.txt - Extracted text
- data/sources/audit_report.csv - Status of each URL with confidence scores
- data/sources/failed_urls.json - Entries with broken sources (high confidence only)
- data/sources/needs_review.json - Ambiguous cases requiring manual review
"""

import json
import csv
import sys
import asyncio
import socket
import hashlib
import re
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, quote
from typing import Optional, Tuple
from collections import defaultdict
import argparse

# Third-party imports
try:
    import aiohttp
    import aiofiles
except ImportError:
    print("ERROR: aiohttp and aiofiles required. Install with: pip install aiohttp aiofiles")
    sys.exit(1)

try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError:
    NEWSPAPER_AVAILABLE = False
    print("INFO: newspaper3k not available, using BeautifulSoup fallback")

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("WARNING: BeautifulSoup not available")


# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
INCIDENTS_DIR = DATA_DIR / "incidents"
SOURCES_DIR = DATA_DIR / "sources"

# HTTP settings
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]
REQUEST_TIMEOUT = 30
DOMAIN_RATE_LIMIT = 1.0  # Seconds between requests to SAME domain
DNS_TIMEOUT = 10

# Wayback Machine API
WAYBACK_API = "https://archive.org/wayback/available"

# Known legitimate domains
KNOWN_LEGITIMATE_DOMAINS = {
    "ice.gov": "US Immigration and Customs Enforcement (official)",
    "cbp.gov": "US Customs and Border Protection (official)",
    "dhs.gov": "Department of Homeland Security (official)",
    "aila.org": "American Immigration Lawyers Association",
    "aclu.org": "American Civil Liberties Union",
    "npr.org": "National Public Radio",
    "nbcnews.com": "NBC News",
    "cnn.com": "CNN",
    "nytimes.com": "New York Times",
    "washingtonpost.com": "Washington Post",
    "reuters.com": "Reuters",
    "apnews.com": "Associated Press",
    "pbs.org": "PBS",
    "abcnews.go.com": "ABC News",
    "cbsnews.com": "CBS News",
    "latimes.com": "Los Angeles Times",
    "politico.com": "Politico",
    "thehill.com": "The Hill",
    "axios.com": "Axios",
    "theguardian.com": "The Guardian",
    "bbc.com": "BBC",
    "bbc.co.uk": "BBC",
    "wikipedia.org": "Wikipedia",
    "en.wikipedia.org": "Wikipedia",
    "substack.com": "Substack",
    "medium.com": "Medium",
    "detentionwatchnetwork.org": "Detention Watch Network",
    "house.gov": "US House of Representatives",
    "senate.gov": "US Senate",
    "congress.gov": "US Congress",
}

# PDF indicators
PDF_INDICATORS = [".pdf", "/pdf/", "doclib/foia"]

# Confidence thresholds
CONFIDENCE_LIKELY_FABRICATED = 80


class URLVerificationResult:
    """Detailed verification result for a URL."""

    def __init__(self, entry_id: str, url: str):
        self.entry_id = entry_id
        self.url = url
        self.domain = self._extract_domain(url) if url else None

        # Verification stages
        self.dns_valid = None
        self.dns_error = None
        self.http_status = None
        self.http_error = None
        self.final_url = url
        self.content_type = None
        self.content_length = 0
        self.title = None
        self.redirect_chain = []

        # Archive.org
        self.wayback_available = None
        self.wayback_url = None
        self.wayback_timestamp = None

        # Validation
        self.is_known_domain = False
        self.known_domain_name = None
        self.content_hash = None

        # Final assessment
        self.status = "pending"
        self.confidence = 0
        self.verdict = "unknown"
        self.reasoning = []
        self.fetch_time = None

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            return parsed.netloc.replace("www.", "").lower()
        except Exception:
            return ""

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "url": self.url,
            "domain": self.domain,
            "dns_valid": self.dns_valid,
            "dns_error": self.dns_error,
            "http_status": self.http_status,
            "http_error": self.http_error,
            "final_url": self.final_url,
            "content_type": self.content_type,
            "content_length": self.content_length,
            "title": self.title,
            "redirect_count": len(self.redirect_chain),
            "wayback_available": self.wayback_available,
            "wayback_url": self.wayback_url,
            "wayback_timestamp": self.wayback_timestamp,
            "is_known_domain": self.is_known_domain,
            "known_domain_name": self.known_domain_name,
            "status": self.status,
            "confidence": self.confidence,
            "verdict": self.verdict,
            "reasoning": "; ".join(self.reasoning),
            "fetch_time": self.fetch_time,
        }


class ConcurrentSourceScraper:
    """Concurrent scraper with per-domain rate limiting."""

    def __init__(self, output_dir: Path = SOURCES_DIR, domain_delay: float = DOMAIN_RATE_LIMIT):
        self.output_dir = output_dir
        self.domain_delay = domain_delay
        self.results: list[URLVerificationResult] = []
        self.user_agent_index = 0

        # Per-domain locks and last request times
        self.domain_locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self.domain_last_request: dict[str, float] = defaultdict(float)

        # Progress tracking
        self.completed = 0
        self.total = 0
        self.lock = asyncio.Lock()

    def _get_headers(self) -> dict:
        """Get headers with rotating user agent."""
        ua = USER_AGENTS[self.user_agent_index % len(USER_AGENTS)]
        self.user_agent_index += 1
        return {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

    def _is_pdf_url(self, url: str) -> bool:
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in PDF_INDICATORS)

    def _sanitize_filename(self, entry_id: str) -> str:
        return entry_id.replace("/", "_").replace("\\", "_").replace(":", "_")

    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            return parsed.netloc.replace("www.", "").lower()
        except Exception:
            return "unknown"

    async def _domain_rate_limit(self, domain: str):
        """Enforce per-domain rate limiting."""
        async with self.domain_locks[domain]:
            now = asyncio.get_event_loop().time()
            elapsed = now - self.domain_last_request[domain]
            if elapsed < self.domain_delay:
                await asyncio.sleep(self.domain_delay - elapsed)
            self.domain_last_request[domain] = asyncio.get_event_loop().time()

    # ==================== VERIFICATION STAGES ====================

    def verify_dns(self, result: URLVerificationResult) -> bool:
        """Stage 1: Verify domain exists via DNS lookup (sync, but fast)."""
        if not result.domain:
            result.dns_valid = False
            result.dns_error = "No domain in URL"
            return False

        try:
            socket.setdefaulttimeout(DNS_TIMEOUT)
            socket.gethostbyname(result.domain)
            result.dns_valid = True
            result.reasoning.append(f"DNS OK: {result.domain}")
            return True
        except socket.gaierror as e:
            result.dns_valid = False
            result.dns_error = str(e)
            result.reasoning.append(f"DNS FAILED: {e}")
            return False
        except socket.timeout:
            result.dns_valid = False
            result.dns_error = "DNS timeout"
            result.reasoning.append("DNS timeout (may be temporary)")
            return False

    def check_known_domain(self, result: URLVerificationResult):
        """Check if domain is in our known legitimate sources list."""
        if not result.domain:
            return

        for known, name in KNOWN_LEGITIMATE_DOMAINS.items():
            if known in result.domain or result.domain.endswith("." + known):
                result.is_known_domain = True
                result.known_domain_name = name
                result.reasoning.append(f"Known source: {name}")
                return

    async def fetch_url(self, session: aiohttp.ClientSession, result: URLVerificationResult, source_index: int = 0) -> bool:
        """Stage 2: Attempt to fetch the URL with per-domain rate limiting."""
        domain = self._extract_domain(result.url)
        await self._domain_rate_limit(domain)

        try:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            async with session.get(result.url, headers=self._get_headers(),
                                   timeout=timeout, allow_redirects=True) as response:
                result.http_status = response.status
                result.final_url = str(response.url)
                result.content_type = response.headers.get("Content-Type", "")

                content = await response.read()
                result.content_length = len(content)
                result.redirect_chain = [str(h.url) for h in response.history]

                if response.status == 200:
                    result.reasoning.append(f"HTTP 200, {result.content_length} bytes")
                    await self._save_content(result, content, source_index=source_index)
                    return True
                elif response.status == 403:
                    result.http_error = "403 Forbidden"
                    result.reasoning.append("HTTP 403 - may block scrapers")
                    return False
                elif response.status == 404:
                    result.http_error = "404 Not Found"
                    result.reasoning.append("HTTP 404 - page not found")
                    return False
                else:
                    result.http_error = f"HTTP {response.status}"
                    result.reasoning.append(f"HTTP {response.status}")
                    return False

        except asyncio.TimeoutError:
            result.http_error = "Request timed out"
            result.reasoning.append(f"Timeout after {REQUEST_TIMEOUT}s")
            return False
        except aiohttp.ClientError as e:
            result.http_error = str(e)[:100]
            result.reasoning.append(f"Connection error: {str(e)[:50]}")
            return False
        except Exception as e:
            result.http_error = str(e)[:100]
            result.reasoning.append(f"Error: {str(e)[:50]}")
            return False

    async def check_wayback(self, session: aiohttp.ClientSession, result: URLVerificationResult) -> bool:
        """Stage 3: Check Archive.org Wayback Machine."""
        # Rate limit archive.org requests
        await self._domain_rate_limit("archive.org")

        try:
            api_url = f"{WAYBACK_API}?url={quote(result.url, safe='')}"
            timeout = aiohttp.ClientTimeout(total=15)

            async with session.get(api_url, timeout=timeout, headers=self._get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    snapshot = data.get("archived_snapshots", {}).get("closest")

                    if snapshot and snapshot.get("available"):
                        result.wayback_available = True
                        result.wayback_url = snapshot.get("url")
                        result.wayback_timestamp = snapshot.get("timestamp")
                        result.reasoning.append(f"Wayback: {result.wayback_timestamp}")
                        return True
                    else:
                        result.wayback_available = False
                        result.reasoning.append("No Wayback archive")
                        return False
                else:
                    result.reasoning.append(f"Wayback API: {response.status}")
                    return False

        except Exception as e:
            result.reasoning.append(f"Wayback error: {str(e)[:30]}")
            return False

    async def fetch_from_wayback(self, session: aiohttp.ClientSession, result: URLVerificationResult, source_index: int = 0) -> bool:
        """Fetch content from Wayback Machine if original failed."""
        if not result.wayback_url:
            return False

        await self._domain_rate_limit("web.archive.org")

        try:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            async with session.get(result.wayback_url, headers=self._get_headers(),
                                   timeout=timeout) as response:
                if response.status == 200:
                    content = await response.read()
                    result.reasoning.append("Fetched from Wayback")
                    await self._save_content(result, content, from_wayback=True, source_index=source_index)
                    return True

        except Exception as e:
            result.reasoning.append(f"Wayback fetch error: {str(e)[:30]}")

        return False

    # ==================== CONTENT HANDLING ====================

    async def _save_content(self, result: URLVerificationResult, content: bytes, from_wayback: bool = False, source_index: int = 0):
        """Save HTML and extracted text content.

        Args:
            result: The verification result object
            content: The raw content bytes
            from_wayback: Whether this was fetched from Wayback Machine
            source_index: Index of the source (0 for primary/first, 1+ for additional sources)
        """
        entry_dir = self.output_dir / self._sanitize_filename(result.entry_id)
        entry_dir.mkdir(parents=True, exist_ok=True)

        is_pdf = self._is_pdf_url(result.url) or "application/pdf" in (result.content_type or "")

        # Build filename with source index (0 = no suffix for backwards compatibility)
        index_suffix = f"_{source_index}" if source_index > 0 else ""
        wayback_suffix = "_wayback" if from_wayback else ""

        if is_pdf:
            pdf_path = entry_dir / f"document{index_suffix}.pdf"
            async with aiofiles.open(pdf_path, "wb") as f:
                await f.write(content)
            result.reasoning.append(f"Saved PDF ({len(content)} bytes)")
            result.archive_path = str(pdf_path.relative_to(self.output_dir.parent.parent))
        else:
            html_path = entry_dir / f"article{index_suffix}{wayback_suffix}.html"
            async with aiofiles.open(html_path, "wb") as f:
                await f.write(content)

            # Extract and save text (sync operations, but fast)
            text_content = self._extract_text(result.url, content)
            if text_content:
                text_path = entry_dir / f"article{index_suffix}{wayback_suffix}.txt"
                async with aiofiles.open(text_path, "w", encoding="utf-8") as f:
                    await f.write(text_content)
                result.archive_path = str(text_path.relative_to(self.output_dir.parent.parent))
            else:
                result.archive_path = str(html_path.relative_to(self.output_dir.parent.parent))

            result.title = self._extract_title(content)

        result.content_hash = hashlib.sha256(content).hexdigest()

        # Save/update metadata (append to list of sources)
        meta_path = entry_dir / "metadata.json"

        # Load existing metadata if present
        existing_metadata = {"entry_id": result.entry_id, "sources": []}
        if meta_path.exists():
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    existing_metadata = json.load(f)
                    if "sources" not in existing_metadata:
                        # Convert old format to new
                        existing_metadata["sources"] = []
            except Exception:
                pass

        source_meta = {
            "source_index": source_index,
            "url": result.url,
            "final_url": result.final_url,
            "status_code": result.http_status,
            "content_type": result.content_type,
            "content_length": result.content_length,
            "content_hash": result.content_hash,
            "title": result.title,
            "fetched_at": datetime.now().isoformat(),
            "from_wayback": from_wayback,
            "wayback_url": result.wayback_url if from_wayback else None,
            "archive_path": result.archive_path if hasattr(result, 'archive_path') else None,
        }

        # Update or append source
        found = False
        for i, s in enumerate(existing_metadata.get("sources", [])):
            if s.get("url") == result.url or s.get("source_index") == source_index:
                existing_metadata["sources"][i] = source_meta
                found = True
                break
        if not found:
            existing_metadata["sources"].append(source_meta)

        async with aiofiles.open(meta_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(existing_metadata, indent=2))

    def _extract_text(self, url: str, html_content: bytes) -> Optional[str]:
        """Extract article text from HTML."""
        if NEWSPAPER_AVAILABLE:
            try:
                article = Article(url)
                article.set_html(html_content)
                article.parse()

                parts = []
                if article.title:
                    parts.append(f"Title: {article.title}")
                if article.authors:
                    parts.append(f"Authors: {', '.join(article.authors)}")
                if article.publish_date:
                    parts.append(f"Published: {article.publish_date}")
                if article.text:
                    parts.append(f"\n{article.text}")

                return "\n".join(parts) if parts else None
            except Exception:
                pass

        if BS4_AVAILABLE:
            try:
                soup = BeautifulSoup(html_content, "html.parser")
                for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    element.decompose()
                text = soup.get_text(separator="\n", strip=True)
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                return "\n".join(lines)
            except Exception:
                pass

        return None

    def _extract_title(self, html_content: bytes) -> Optional[str]:
        """Extract page title from HTML."""
        if BS4_AVAILABLE:
            try:
                soup = BeautifulSoup(html_content, "html.parser")
                title_tag = soup.find("title")
                if title_tag:
                    return title_tag.get_text(strip=True)[:200]
            except Exception:
                pass

        match = re.search(rb"<title[^>]*>([^<]+)</title>", html_content, re.IGNORECASE)
        if match:
            return match.group(1).decode("utf-8", errors="ignore").strip()[:200]

        return None

    # ==================== VERDICT ASSESSMENT ====================

    def assess_verdict(self, result: URLVerificationResult):
        """Determine final verdict and confidence score."""
        result.fetch_time = datetime.now().isoformat()

        if not result.url:
            result.status = "no_url"
            result.verdict = "missing"
            result.confidence = 100
            result.reasoning.append("No URL in entry")
            return

        if result.http_status == 200:
            result.status = "success"
            result.verdict = "valid"
            result.confidence = 95 if not result.is_known_domain else 99
            return

        if result.dns_valid is False and "NXDOMAIN" in str(result.dns_error):
            if result.wayback_available:
                result.status = "domain_expired"
                result.verdict = "was_valid"
                result.confidence = 75
                result.reasoning.append("Domain gone but was archived")
            else:
                result.status = "invalid_domain"
                result.verdict = "likely_fabricated"
                result.confidence = 90
                result.reasoning.append("Domain never existed")
            return

        if result.is_known_domain:
            if result.http_status == 404:
                if result.wayback_available:
                    result.status = "page_removed"
                    result.verdict = "was_valid"
                    result.confidence = 85
                else:
                    result.status = "page_not_found"
                    result.verdict = "needs_review"
                    result.confidence = 50
            elif result.http_status == 403:
                result.status = "blocked"
                result.verdict = "likely_valid"
                result.confidence = 80
            else:
                result.status = "fetch_failed"
                result.verdict = "likely_valid"
                result.confidence = 70
            return

        if result.http_status == 404:
            if result.wayback_available:
                result.status = "page_removed"
                result.verdict = "was_valid"
                result.confidence = 75
            else:
                result.status = "not_found"
                result.verdict = "needs_review"
                result.confidence = 40
        elif result.http_status == 403:
            result.status = "forbidden"
            result.verdict = "needs_review"
            result.confidence = 50
        elif result.dns_valid is False:
            result.status = "dns_failed"
            result.verdict = "needs_review"
            result.confidence = 45
        elif result.http_error:
            if result.wayback_available:
                result.status = "currently_unavailable"
                result.verdict = "was_valid"
                result.confidence = 70
            else:
                result.status = "failed"
                result.verdict = "needs_review"
                result.confidence = 40
        else:
            result.status = "unknown"
            result.verdict = "needs_review"
            result.confidence = 30

    # ==================== MAIN PROCESSING ====================

    async def verify_url(self, session: aiohttp.ClientSession, entry_id: str, url: str, source_index: int = 0) -> URLVerificationResult:
        """Run full verification pipeline on a URL."""
        result = URLVerificationResult(entry_id, url)

        if not url:
            self.assess_verdict(result)
            return result

        # Stage 1: Check if known domain
        self.check_known_domain(result)

        # Stage 2: DNS verification (sync but fast)
        dns_ok = self.verify_dns(result)

        # Stage 3: HTTP fetch
        if dns_ok or result.is_known_domain:
            fetch_ok = await self.fetch_url(session, result, source_index=source_index)

            # Stage 4: Wayback check if fetch failed
            if not fetch_ok:
                wayback_ok = await self.check_wayback(session, result)
                if wayback_ok:
                    await self.fetch_from_wayback(session, result, source_index=source_index)
        else:
            await self.check_wayback(session, result)

        self.assess_verdict(result)
        return result

    async def process_single(self, session: aiohttp.ClientSession, incident: dict) -> list[URLVerificationResult]:
        """Process a single incident - archives ALL sources, not just primary."""
        entry_id = incident.get("id", "unknown")
        results = []

        # Collect all URLs to process
        urls_to_process = []

        # Support old format (source_url)
        if incident.get("source_url"):
            urls_to_process.append({"url": incident["source_url"], "index": 0})

        # Support new format (sources array) - process ALL sources
        if "sources" in incident:
            sources = incident.get("sources", [])
            for idx, source in enumerate(sources):
                url = source.get("url")
                if url:
                    # Check if already archived (skip if archived=True and not forcing re-archive)
                    if source.get("archived") and source.get("archive_path"):
                        continue  # Skip already archived sources
                    urls_to_process.append({"url": url, "index": idx, "source_name": source.get("name", "")})

        # Fallback if no URLs found
        if not urls_to_process:
            result = URLVerificationResult(entry_id, None)
            result.status = "no_url"
            result.verdict = "missing"
            result.confidence = 100
            result.reasoning.append("No URL in entry")
            results.append(result)
        else:
            # Process each URL
            for url_info in urls_to_process:
                result = await self.verify_url(session, entry_id, url_info["url"], source_index=url_info["index"])
                results.append(result)

        # Update progress
        async with self.lock:
            self.completed += 1
            self.results.extend(results)

            # Print progress (show primary result or first result)
            primary_result = results[0] if results else None
            verdict_icons = {
                "valid": "[OK]", "likely_valid": "[~OK]", "was_valid": "[WAS]",
                "needs_review": "[???]", "likely_fabricated": "[BAD]",
                "missing": "[---]", "unknown": "[???]",
            }
            if primary_result:
                icon = verdict_icons.get(primary_result.verdict, "[?]")
                sources_info = f" ({len(urls_to_process)} sources)" if len(urls_to_process) > 1 else ""
                print(f"[{self.completed}/{self.total}] {entry_id}: {icon} {primary_result.verdict} ({primary_result.confidence}%){sources_info}")

        return results

    async def process_incidents(self, incidents: list[dict]) -> list[URLVerificationResult]:
        """Process all incidents concurrently with per-domain rate limiting."""
        self.total = len(incidents)
        self.completed = 0
        self.results = []

        # Create connector with high limit
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=60)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Create all tasks - they will self-rate-limit per domain
            tasks = [self.process_single(session, inc) for inc in incidents]

            # Run all concurrently
            await asyncio.gather(*tasks, return_exceptions=True)

        return self.results

    def generate_reports(self) -> Tuple[Path, Path, Path]:
        """Generate all output reports."""
        # 1. Full audit report CSV
        audit_path = self.output_dir / "audit_report.csv"
        fieldnames = [
            "entry_id", "url", "domain", "verdict", "confidence", "status",
            "http_status", "http_error", "dns_valid", "final_url",
            "content_type", "content_length", "title",
            "wayback_available", "wayback_url", "wayback_timestamp",
            "is_known_domain", "known_domain_name",
            "reasoning", "fetch_time"
        ]

        with open(audit_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in self.results:
                writer.writerow(r.to_dict())

        # 2. Failed URLs (high confidence fabricated/invalid)
        failed_path = self.output_dir / "failed_urls.json"
        failed = [
            r.to_dict() for r in self.results
            if r.verdict == "likely_fabricated" and r.confidence >= CONFIDENCE_LIKELY_FABRICATED
        ]

        with open(failed_path, "w", encoding="utf-8") as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "description": "URLs with HIGH confidence of being fabricated/invalid (>= 80%)",
                "total": len(failed),
                "entries": failed
            }, f, indent=2)

        # 3. Needs review
        review_path = self.output_dir / "needs_review.json"
        review = [
            r.to_dict() for r in self.results
            if r.verdict == "needs_review" or (r.verdict == "likely_fabricated" and r.confidence < CONFIDENCE_LIKELY_FABRICATED)
        ]

        with open(review_path, "w", encoding="utf-8") as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "description": "Ambiguous cases requiring manual verification",
                "total": len(review),
                "entries": review
            }, f, indent=2)

        return audit_path, failed_path, review_path

    def print_summary(self):
        """Print detailed summary statistics."""
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)

        total = len(self.results)
        print(f"Total URLs processed: {total}")

        verdicts = {}
        for r in self.results:
            verdicts[r.verdict] = verdicts.get(r.verdict, 0) + 1

        print("\nVerdict breakdown:")
        for v in ["valid", "likely_valid", "was_valid", "needs_review", "likely_fabricated", "missing", "unknown"]:
            if v in verdicts:
                pct = (verdicts[v] / total) * 100
                print(f"  {v}: {verdicts[v]} ({pct:.1f}%)")

        statuses = {}
        for r in self.results:
            statuses[r.status] = statuses.get(r.status, 0) + 1

        print("\nStatus breakdown:")
        for status, count in sorted(statuses.items(), key=lambda x: -x[1]):
            pct = (count / total) * 100
            print(f"  {status}: {count} ({pct:.1f}%)")

        fabricated = [r for r in self.results if r.verdict == "likely_fabricated" and r.confidence >= 80]
        review_needed = [r for r in self.results if r.verdict == "needs_review"]

        print("\n" + "-" * 60)
        print(f"HIGH CONFIDENCE FABRICATED (>=80%): {len(fabricated)}")
        for r in fabricated:
            print(f"  {r.entry_id}: {r.url[:60]}...")

        print(f"\nNEEDS MANUAL REVIEW: {len(review_needed)}")
        if len(review_needed) <= 20:
            for r in review_needed:
                print(f"  {r.entry_id}: {r.status} ({r.confidence}%)")


def load_incidents(incidents_dir: Path) -> list[dict]:
    """Load all incidents from tier JSON files."""
    all_incidents = []

    tier_files = sorted(incidents_dir.glob("tier*.json"))

    if not tier_files:
        print(f"ERROR: No tier*.json files found in {incidents_dir}")
        return []

    for tier_file in tier_files:
        print(f"Loading {tier_file.name}...")
        try:
            with open(tier_file, "r", encoding="utf-8") as f:
                incidents = json.load(f)
                all_incidents.extend(incidents)
                print(f"  Loaded {len(incidents)} incidents")
        except Exception as e:
            print(f"  ERROR: Failed to load {tier_file}: {e}")

    return all_incidents


def get_primary_url(incident: dict) -> str:
    """Extract primary URL from incident (supports both old and new format)."""
    url = incident.get("source_url")
    if not url and "sources" in incident:
        sources = incident.get("sources", [])
        if sources:
            primary = next((s for s in sources if s.get("primary")), None)
            url = primary.get("url") if primary else sources[0].get("url")
    return url or ""


def deduplicate_urls(incidents: list[dict]) -> list[dict]:
    """Remove duplicate source URLs, keeping first occurrence."""
    seen_urls = set()
    unique = []

    for incident in incidents:
        url = get_primary_url(incident)
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(incident)
        elif not url:
            unique.append(incident)

    print(f"Deduplicated: {len(incidents)} -> {len(unique)} unique URLs")
    return unique


async def async_main(args):
    """Async main function."""
    print("=" * 60)
    print("ICE Incidents CONCURRENT Source Verifier")
    print("=" * 60)
    print(f"Output directory: {args.output}")
    print(f"Per-domain rate limit: {args.domain_delay}s")
    print(f"Concurrency: UNLIMITED across domains, sequential within domain")
    print()

    args.output.mkdir(parents=True, exist_ok=True)

    incidents = load_incidents(INCIDENTS_DIR)
    if not incidents:
        print("No incidents loaded. Exiting.")
        return 1

    if not args.no_dedupe:
        incidents = deduplicate_urls(incidents)

    if args.skip_existing:
        scraper_temp = ConcurrentSourceScraper(args.output)
        original = len(incidents)
        incidents = [
            inc for inc in incidents
            if not (args.output / scraper_temp._sanitize_filename(inc.get("id", "unknown"))).exists()
        ]
        print(f"Skipping existing: {original} -> {len(incidents)} to process")

    if args.limit > 0:
        incidents = incidents[:args.limit]
        print(f"Limited to first {args.limit} URLs")

    # Count domains for info
    domains = set(urlparse(get_primary_url(inc)).netloc for inc in incidents if get_primary_url(inc))
    print(f"\nProcessing {len(incidents)} URLs across {len(domains)} unique domains...\n")

    scraper = ConcurrentSourceScraper(output_dir=args.output, domain_delay=args.domain_delay)

    import time
    start = time.time()
    await scraper.process_incidents(incidents)
    elapsed = time.time() - start

    print("\n" + "=" * 60)
    print(f"Completed in {elapsed:.1f} seconds ({len(incidents)/elapsed:.1f} URLs/sec)")
    print("Generating reports...")

    audit_path, failed_path, review_path = scraper.generate_reports()
    print(f"  Audit report: {audit_path}")
    print(f"  Failed URLs (high confidence): {failed_path}")
    print(f"  Needs review: {review_path}")

    scraper.print_summary()
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Concurrent source verification for ICE incidents database"
    )
    parser.add_argument("--output", "-o", type=Path, default=SOURCES_DIR)
    parser.add_argument("--domain-delay", "-d", type=float, default=DOMAIN_RATE_LIMIT,
                        help=f"Seconds between requests to same domain (default: {DOMAIN_RATE_LIMIT})")
    parser.add_argument("--limit", "-l", type=int, default=0)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--no-dedupe", action="store_true")

    args = parser.parse_args()

    return asyncio.run(async_main(args))


if __name__ == "__main__":
    sys.exit(main())
