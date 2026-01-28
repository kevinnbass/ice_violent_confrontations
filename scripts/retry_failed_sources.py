#!/usr/bin/env python3
"""
Retry Failed Sources - Advanced scraping for blocked/failed URLs

Uses multiple strategies to fetch URLs that failed initial scraping:
1. Stealth HTTP requests with browser-like headers and cookies
2. Multiple Wayback Machine snapshots (CDX API search)
3. Google Cache lookup
4. URL variations (www/non-www, http/https)

Run after scrape_sources.py to handle the "needs_review" entries.
"""

import json
import asyncio
import re
import hashlib
import random
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, quote, urlencode
from typing import Optional
import argparse

import aiohttp
import aiofiles

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
SOURCES_DIR = DATA_DIR / "sources"

WAYBACK_CDX_API = "https://web.archive.org/cdx/search/cdx"
WAYBACK_WEB = "https://web.archive.org/web"

# Realistic browser headers
BROWSER_HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
]

REQUEST_TIMEOUT = 45


class RetryResult:
    def __init__(self, entry_id: str, url: str):
        self.entry_id = entry_id
        self.url = url
        self.success = False
        self.method = None
        self.final_url = None
        self.content_length = 0
        self.title = None
        self.error = None
        self.attempts = []

    def to_dict(self):
        return {
            "entry_id": self.entry_id,
            "url": self.url,
            "success": self.success,
            "method": self.method,
            "final_url": self.final_url,
            "content_length": self.content_length,
            "title": self.title,
            "error": self.error,
            "attempts": self.attempts,
        }


class AdvancedScraper:
    """Advanced scraper with stealth techniques and multiple fallbacks."""

    def __init__(self, output_dir: Path = SOURCES_DIR):
        self.output_dir = output_dir
        self.results = []

    def _get_random_headers(self) -> dict:
        """Get random browser-like headers."""
        return random.choice(BROWSER_HEADERS_LIST).copy()

    def _sanitize_filename(self, entry_id: str) -> str:
        return entry_id.replace("/", "_").replace("\\", "_").replace(":", "_")

    def _extract_title(self, html: str) -> Optional[str]:
        if BeautifulSoup:
            try:
                soup = BeautifulSoup(html, "html.parser")
                title = soup.find("title")
                if title:
                    return title.get_text(strip=True)[:200]
            except:
                pass
        match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
        if match:
            return match.group(1).strip()[:200]
        return None

    def _extract_text(self, html: str) -> Optional[str]:
        if BeautifulSoup:
            try:
                soup = BeautifulSoup(html, "html.parser")
                for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                    tag.decompose()
                text = soup.get_text(separator="\n", strip=True)
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                return "\n".join(lines)
            except:
                pass
        return None

    def _is_valid_content(self, html: str) -> bool:
        """Check if content is valid (not an error page, captcha, etc.)."""
        if len(html) < 1000:
            return False

        lower = html.lower()

        # Common error indicators
        error_indicators = [
            "access denied",
            "403 forbidden",
            "404 not found",
            "page not found",
            "captcha",
            "please verify you are human",
            "enable javascript",
            "browser check",
            "just a moment",
            "checking your browser",
            "ray id",  # Cloudflare
        ]

        for indicator in error_indicators:
            if indicator in lower:
                return False

        return True

    async def _save_content(self, entry_id: str, html: str, method: str):
        """Save fetched content."""
        entry_dir = self.output_dir / self._sanitize_filename(entry_id)
        entry_dir.mkdir(parents=True, exist_ok=True)

        # Save HTML
        html_path = entry_dir / f"article_retry_{method}.html"
        async with aiofiles.open(html_path, "w", encoding="utf-8", errors="replace") as f:
            await f.write(html)

        # Save text
        text = self._extract_text(html)
        if text:
            text_path = entry_dir / f"article_retry_{method}.txt"
            async with aiofiles.open(text_path, "w", encoding="utf-8", errors="replace") as f:
                await f.write(text)

        # Update metadata
        meta_path = entry_dir / "metadata.json"
        metadata = {}
        if meta_path.exists():
            try:
                async with aiofiles.open(meta_path, "r") as f:
                    metadata = json.loads(await f.read())
            except:
                pass

        metadata["retry_fetch"] = {
            "method": method,
            "fetched_at": datetime.now().isoformat(),
            "content_length": len(html),
            "content_hash": hashlib.sha256(html.encode(errors="replace")).hexdigest(),
        }

        async with aiofiles.open(meta_path, "w") as f:
            await f.write(json.dumps(metadata, indent=2))

    # ==================== FETCH STRATEGIES ====================

    async def fetch_stealth_request(self, session: aiohttp.ClientSession, url: str, result: RetryResult) -> bool:
        """Strategy 1: Stealth HTTP request with browser-like behavior."""
        result.attempts.append("stealth")

        headers = self._get_random_headers()
        parsed = urlparse(url)
        headers["Host"] = parsed.netloc
        headers["Referer"] = f"{parsed.scheme}://{parsed.netloc}/"

        try:
            # Add slight random delay (human-like)
            await asyncio.sleep(random.uniform(0.5, 2.0))

            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            async with session.get(url, headers=headers, timeout=timeout,
                                   allow_redirects=True, ssl=False) as response:

                if response.status == 200:
                    html = await response.text(errors="replace")

                    if self._is_valid_content(html):
                        result.success = True
                        result.method = "stealth"
                        result.final_url = str(response.url)
                        result.content_length = len(html)
                        result.title = self._extract_title(html)
                        await self._save_content(result.entry_id, html, "stealth")
                        return True
                    else:
                        result.attempts[-1] += " (blocked/captcha)"
                else:
                    result.attempts[-1] += f" (HTTP {response.status})"

        except asyncio.TimeoutError:
            result.attempts[-1] += " (timeout)"
        except Exception as e:
            result.attempts[-1] += f" ({str(e)[:40]})"

        return False

    async def fetch_wayback_cdx(self, session: aiohttp.ClientSession, url: str, result: RetryResult) -> bool:
        """Strategy 2: Search Wayback Machine CDX API for all snapshots."""
        result.attempts.append("wayback_cdx")

        try:
            # Query CDX API for snapshots
            params = {
                "url": url,
                "output": "json",
                "limit": "20",
                "filter": "statuscode:200",
                "collapse": "digest",  # Remove duplicates
            }
            cdx_url = f"{WAYBACK_CDX_API}?{urlencode(params)}"

            timeout = aiohttp.ClientTimeout(total=30)
            async with session.get(cdx_url, timeout=timeout) as resp:
                if resp.status != 200:
                    result.attempts[-1] += f" (CDX: {resp.status})"
                    return False

                try:
                    data = await resp.json()
                except:
                    result.attempts[-1] += " (CDX: invalid JSON)"
                    return False

                if len(data) <= 1:
                    result.attempts[-1] += " (no snapshots)"
                    return False

                # Try snapshots from newest to oldest
                snapshots_tried = 0
                for row in reversed(data[1:5]):  # Try up to 5 most recent
                    timestamp = row[1]
                    snapshot_url = f"{WAYBACK_WEB}/{timestamp}id_/{url}"

                    try:
                        await asyncio.sleep(1)  # Rate limit wayback
                        async with session.get(snapshot_url, timeout=timeout,
                                               headers=self._get_random_headers()) as snap_resp:
                            if snap_resp.status == 200:
                                html = await snap_resp.text(errors="replace")

                                # Clean up Wayback-injected content
                                html = re.sub(
                                    r'<!-- BEGIN WAYBACK TOOLBAR INSERT -->.*?<!-- END WAYBACK TOOLBAR INSERT -->',
                                    '', html, flags=re.DOTALL | re.IGNORECASE
                                )

                                if len(html) > 2000:
                                    result.success = True
                                    result.method = f"wayback_{timestamp}"
                                    result.final_url = snapshot_url
                                    result.content_length = len(html)
                                    result.title = self._extract_title(html)
                                    await self._save_content(result.entry_id, html, f"wayback_{timestamp}")
                                    return True

                            snapshots_tried += 1

                    except Exception as e:
                        snapshots_tried += 1
                        continue

                result.attempts[-1] += f" (tried {snapshots_tried} snapshots)"

        except asyncio.TimeoutError:
            result.attempts[-1] += " (timeout)"
        except Exception as e:
            result.attempts[-1] += f" ({str(e)[:40]})"

        return False

    async def fetch_url_variations(self, session: aiohttp.ClientSession, url: str, result: RetryResult) -> bool:
        """Strategy 3: Try URL variations."""
        result.attempts.append("variations")

        parsed = urlparse(url)
        variations = set()

        # www/non-www
        if parsed.netloc.startswith("www."):
            variations.add(url.replace("www.", "", 1))
        else:
            variations.add(url.replace("://", "://www.", 1))

        # Trailing slash
        if url.endswith("/"):
            variations.add(url.rstrip("/"))
        else:
            variations.add(url + "/")

        # HTTP/HTTPS
        if parsed.scheme == "https":
            variations.add(url.replace("https://", "http://", 1))

        headers = self._get_random_headers()
        timeout = aiohttp.ClientTimeout(total=30)

        for var_url in variations:
            try:
                await asyncio.sleep(0.5)
                async with session.get(var_url, headers=headers, timeout=timeout,
                                       allow_redirects=True, ssl=False) as response:
                    if response.status == 200:
                        html = await response.text(errors="replace")

                        if self._is_valid_content(html):
                            result.success = True
                            result.method = "variation"
                            result.final_url = str(response.url)
                            result.content_length = len(html)
                            result.title = self._extract_title(html)
                            await self._save_content(result.entry_id, html, "variation")
                            return True

            except:
                continue

        result.attempts[-1] += f" (tried {len(variations)})"
        return False

    async def fetch_with_different_ua(self, session: aiohttp.ClientSession, url: str, result: RetryResult) -> bool:
        """Strategy 4: Try with all different user agents."""
        result.attempts.append("multi_ua")

        timeout = aiohttp.ClientTimeout(total=30)

        for i, headers in enumerate(BROWSER_HEADERS_LIST):
            try:
                await asyncio.sleep(1)
                h = headers.copy()
                parsed = urlparse(url)
                h["Host"] = parsed.netloc

                async with session.get(url, headers=h, timeout=timeout,
                                       allow_redirects=True, ssl=False) as response:
                    if response.status == 200:
                        html = await response.text(errors="replace")

                        if self._is_valid_content(html):
                            result.success = True
                            result.method = f"ua_{i}"
                            result.final_url = str(response.url)
                            result.content_length = len(html)
                            result.title = self._extract_title(html)
                            await self._save_content(result.entry_id, html, f"ua_{i}")
                            return True

            except:
                continue

        result.attempts[-1] += f" (tried {len(BROWSER_HEADERS_LIST)} UAs)"
        return False

    # ==================== MAIN PROCESSING ====================

    async def process_entry(self, session: aiohttp.ClientSession, entry: dict) -> RetryResult:
        """Process a single failed entry with all strategies."""
        entry_id = entry["entry_id"]
        url = entry["url"]
        original_status = entry.get("status", "unknown")

        result = RetryResult(entry_id, url)

        # Strategy 1: Stealth request (good for 403s)
        if await self.fetch_stealth_request(session, url, result):
            return result

        # Strategy 2: Try different User-Agents
        if await self.fetch_with_different_ua(session, url, result):
            return result

        # Strategy 3: URL variations
        if await self.fetch_url_variations(session, url, result):
            return result

        # Strategy 4: Wayback Machine (always try this)
        if await self.fetch_wayback_cdx(session, url, result):
            return result

        result.error = "All strategies failed"
        return result

    async def process_all(self, entries: list[dict]) -> list[RetryResult]:
        """Process all failed entries."""
        print(f"\nRetrying {len(entries)} failed URLs...\n")

        connector = aiohttp.TCPConnector(limit=10, ssl=False)
        timeout = aiohttp.ClientTimeout(total=60)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for i, entry in enumerate(entries, 1):
                entry_id = entry["entry_id"]
                url = entry.get("url", "")[:60]
                print(f"[{i}/{len(entries)}] {entry_id}: {url}...")

                result = await self.process_entry(session, entry)
                self.results.append(result)

                if result.success:
                    print(f"    [OK] {result.method}")
                else:
                    print(f"    [FAIL] {', '.join(result.attempts)}")

                # Brief pause between entries
                await asyncio.sleep(0.5)

        return self.results

    def generate_report(self) -> Path:
        """Generate retry report."""
        report_path = self.output_dir / "retry_report.json"

        succeeded = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_retried": len(self.results),
            "succeeded": len(succeeded),
            "still_failed": len(failed),
            "success_by_method": {},
            "succeeded_entries": [r.to_dict() for r in succeeded],
            "failed_entries": [r.to_dict() for r in failed],
        }

        for r in succeeded:
            method = r.method.split("_")[0] if r.method else "unknown"
            report["success_by_method"][method] = report["success_by_method"].get(method, 0) + 1

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return report_path

    def print_summary(self):
        """Print summary."""
        succeeded = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        print("\n" + "=" * 60)
        print("RETRY SUMMARY")
        print("=" * 60)
        print(f"Total retried: {len(self.results)}")
        print(f"Succeeded: {len(succeeded)} ({100*len(succeeded)/len(self.results):.1f}%)")
        print(f"Still failed: {len(failed)}")

        if succeeded:
            print("\nSuccessful methods:")
            methods = {}
            for r in succeeded:
                m = r.method.split("_")[0] if r.method else "unknown"
                methods[m] = methods.get(m, 0) + 1
            for m, c in sorted(methods.items(), key=lambda x: -x[1]):
                print(f"  {m}: {c}")

        if failed:
            print(f"\nStill failed ({len(failed)}):")
            for r in failed[:15]:
                domain = urlparse(r.url).netloc if r.url else "unknown"
                print(f"  {r.entry_id}: {domain}")
            if len(failed) > 15:
                print(f"  ... and {len(failed) - 15} more")


async def async_main(args):
    """Async main."""
    print("=" * 60)
    print("Advanced Source Retry (HTTP-based)")
    print("=" * 60)

    # Load needs_review entries
    review_path = args.input or (SOURCES_DIR / "needs_review.json")
    if not review_path.exists():
        print(f"ERROR: {review_path} not found. Run scrape_sources.py first.")
        return 1

    with open(review_path) as f:
        data = json.load(f)
        entries = data.get("entries", [])

    if not entries:
        print("No entries to retry.")
        return 0

    if args.limit > 0:
        entries = entries[:args.limit]
        print(f"Limited to {args.limit} entries")

    print(f"Loaded {len(entries)} entries to retry")

    scraper = AdvancedScraper(output_dir=args.output)
    await scraper.process_all(entries)

    report_path = scraper.generate_report()
    print(f"\nReport: {report_path}")

    scraper.print_summary()
    return 0


def main():
    parser = argparse.ArgumentParser(description="Retry failed source URLs")
    parser.add_argument("--input", "-i", type=Path, help="Input JSON file")
    parser.add_argument("--output", "-o", type=Path, default=SOURCES_DIR)
    parser.add_argument("--limit", "-l", type=int, default=0)

    args = parser.parse_args()
    return asyncio.run(async_main(args))


if __name__ == "__main__":
    exit(main())
