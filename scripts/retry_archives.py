#!/usr/bin/env python3
"""
Retry with Alternative Archives - For paywall sites

Tries multiple archive services:
1. archive.ph (archive.today/archive.is) - Best for paywalled news
2. Google Cache
3. Ghostarchive.org
4. 12ft.io - Paywall bypass
5. webcitation.org
"""

import json
import asyncio
import re
import hashlib
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, quote
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
SOURCES_DIR = BASE_DIR / "data" / "sources"

# Archive services
ARCHIVE_PH_SEARCH = "https://archive.ph/"
ARCHIVE_PH_NEWEST = "https://archive.ph/newest/"
GOOGLE_CACHE = "https://webcache.googleusercontent.com/search?q=cache:"
TWELVE_FT = "https://12ft.io/"
GHOSTARCHIVE = "https://ghostarchive.org/search?term="

REQUEST_TIMEOUT = 45

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


class ArchiveRetryResult:
    def __init__(self, entry_id: str, url: str):
        self.entry_id = entry_id
        self.url = url
        self.success = False
        self.method = None
        self.archive_url = None
        self.content_length = 0
        self.title = None
        self.attempts = []

    def to_dict(self):
        return {
            "entry_id": self.entry_id,
            "url": self.url,
            "success": self.success,
            "method": self.method,
            "archive_url": self.archive_url,
            "content_length": self.content_length,
            "title": self.title,
            "attempts": self.attempts,
        }


class ArchiveScraper:
    def __init__(self, output_dir: Path = SOURCES_DIR):
        self.output_dir = output_dir
        self.results = []

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

    def _is_valid_content(self, html: str, min_length: int = 3000) -> bool:
        """Check if we got real article content."""
        if len(html) < min_length:
            return False

        lower = html.lower()
        # Error indicators
        bad = ["404", "not found", "page not found", "access denied", "captcha",
               "no results", "nothing found", "did not match"]
        for b in bad:
            if b in lower[:2000]:  # Check beginning of page
                return False
        return True

    async def _save_content(self, entry_id: str, html: str, method: str, archive_url: str):
        """Save fetched content."""
        entry_dir = self.output_dir / self._sanitize_filename(entry_id)
        entry_dir.mkdir(parents=True, exist_ok=True)

        # Save HTML
        html_path = entry_dir / f"article_{method}.html"
        async with aiofiles.open(html_path, "w", encoding="utf-8", errors="replace") as f:
            await f.write(html)

        # Save text
        text = self._extract_text(html)
        if text:
            text_path = entry_dir / f"article_{method}.txt"
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

        metadata["archive_fetch"] = {
            "method": method,
            "archive_url": archive_url,
            "fetched_at": datetime.now().isoformat(),
            "content_length": len(html),
        }

        async with aiofiles.open(meta_path, "w") as f:
            await f.write(json.dumps(metadata, indent=2))

    # ==================== ARCHIVE SERVICES ====================

    async def try_archive_ph(self, session: aiohttp.ClientSession, url: str, result: ArchiveRetryResult) -> bool:
        """Try archive.ph (archive.today)."""
        result.attempts.append("archive.ph")

        # archive.ph/newest/URL redirects to most recent snapshot
        archive_url = f"{ARCHIVE_PH_NEWEST}{url}"

        try:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            async with session.get(archive_url, headers=HEADERS, timeout=timeout,
                                   allow_redirects=True, ssl=False) as response:

                # archive.ph redirects to the actual archived page
                final_url = str(response.url)

                if response.status == 200 and "archive.ph" in final_url or "archive.today" in final_url or "archive.is" in final_url:
                    html = await response.text(errors="replace")

                    if self._is_valid_content(html):
                        result.success = True
                        result.method = "archive.ph"
                        result.archive_url = final_url
                        result.content_length = len(html)
                        result.title = self._extract_title(html)
                        await self._save_content(result.entry_id, html, "archive_ph", final_url)
                        return True
                    else:
                        result.attempts[-1] += " (no valid content)"
                else:
                    result.attempts[-1] += f" (HTTP {response.status})"

        except asyncio.TimeoutError:
            result.attempts[-1] += " (timeout)"
        except Exception as e:
            result.attempts[-1] += f" ({str(e)[:30]})"

        return False

    async def try_archive_ph_search(self, session: aiohttp.ClientSession, url: str, result: ArchiveRetryResult) -> bool:
        """Search archive.ph for the URL."""
        result.attempts.append("archive.ph_search")

        # Direct search URL
        search_url = f"https://archive.ph/{quote(url, safe='')}"

        try:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            async with session.get(search_url, headers=HEADERS, timeout=timeout,
                                   allow_redirects=True, ssl=False) as response:

                if response.status == 200:
                    html = await response.text(errors="replace")

                    # Look for archived links in the search results
                    if BeautifulSoup:
                        soup = BeautifulSoup(html, "html.parser")
                        # Find archive links
                        links = soup.find_all("a", href=re.compile(r"archive\.(ph|today|is)/\w+"))

                        for link in links[:3]:  # Try first 3 results
                            archive_link = link.get("href")
                            if archive_link and not archive_link.endswith("/submit/"):
                                try:
                                    async with session.get(archive_link, headers=HEADERS,
                                                          timeout=timeout, ssl=False) as arch_resp:
                                        if arch_resp.status == 200:
                                            arch_html = await arch_resp.text(errors="replace")
                                            if self._is_valid_content(arch_html):
                                                result.success = True
                                                result.method = "archive.ph_search"
                                                result.archive_url = archive_link
                                                result.content_length = len(arch_html)
                                                result.title = self._extract_title(arch_html)
                                                await self._save_content(result.entry_id, arch_html,
                                                                        "archive_ph_search", archive_link)
                                                return True
                                except:
                                    continue

                    result.attempts[-1] += " (no archives found)"
                else:
                    result.attempts[-1] += f" (HTTP {response.status})"

        except Exception as e:
            result.attempts[-1] += f" ({str(e)[:30]})"

        return False

    async def try_google_cache(self, session: aiohttp.ClientSession, url: str, result: ArchiveRetryResult) -> bool:
        """Try Google Cache."""
        result.attempts.append("google_cache")

        cache_url = f"{GOOGLE_CACHE}{quote(url, safe='')}"

        try:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            async with session.get(cache_url, headers=HEADERS, timeout=timeout,
                                   allow_redirects=True, ssl=False) as response:

                if response.status == 200:
                    html = await response.text(errors="replace")

                    if self._is_valid_content(html) and "cache" in str(response.url).lower():
                        result.success = True
                        result.method = "google_cache"
                        result.archive_url = cache_url
                        result.content_length = len(html)
                        result.title = self._extract_title(html)
                        await self._save_content(result.entry_id, html, "google_cache", cache_url)
                        return True
                    else:
                        result.attempts[-1] += " (not cached or blocked)"
                else:
                    result.attempts[-1] += f" (HTTP {response.status})"

        except Exception as e:
            result.attempts[-1] += f" ({str(e)[:30]})"

        return False

    async def try_12ft(self, session: aiohttp.ClientSession, url: str, result: ArchiveRetryResult) -> bool:
        """Try 12ft.io paywall bypass."""
        result.attempts.append("12ft.io")

        bypass_url = f"{TWELVE_FT}{url}"

        try:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            async with session.get(bypass_url, headers=HEADERS, timeout=timeout,
                                   allow_redirects=True, ssl=False) as response:

                if response.status == 200:
                    html = await response.text(errors="replace")

                    if self._is_valid_content(html):
                        result.success = True
                        result.method = "12ft.io"
                        result.archive_url = bypass_url
                        result.content_length = len(html)
                        result.title = self._extract_title(html)
                        await self._save_content(result.entry_id, html, "12ft", bypass_url)
                        return True
                    else:
                        result.attempts[-1] += " (blocked or no content)"
                else:
                    result.attempts[-1] += f" (HTTP {response.status})"

        except Exception as e:
            result.attempts[-1] += f" ({str(e)[:30]})"

        return False

    async def try_ghostarchive(self, session: aiohttp.ClientSession, url: str, result: ArchiveRetryResult) -> bool:
        """Try Ghostarchive.org."""
        result.attempts.append("ghostarchive")

        search_url = f"{GHOSTARCHIVE}{quote(url, safe='')}"

        try:
            timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
            async with session.get(search_url, headers=HEADERS, timeout=timeout,
                                   allow_redirects=True, ssl=False) as response:

                if response.status == 200:
                    html = await response.text(errors="replace")

                    # Look for archive links
                    if BeautifulSoup:
                        soup = BeautifulSoup(html, "html.parser")
                        links = soup.find_all("a", href=re.compile(r"ghostarchive\.org/archive/"))

                        for link in links[:2]:
                            archive_link = link.get("href")
                            if archive_link:
                                try:
                                    async with session.get(archive_link, headers=HEADERS,
                                                          timeout=timeout, ssl=False) as arch_resp:
                                        if arch_resp.status == 200:
                                            arch_html = await arch_resp.text(errors="replace")
                                            if self._is_valid_content(arch_html, min_length=2000):
                                                result.success = True
                                                result.method = "ghostarchive"
                                                result.archive_url = archive_link
                                                result.content_length = len(arch_html)
                                                result.title = self._extract_title(arch_html)
                                                await self._save_content(result.entry_id, arch_html,
                                                                        "ghostarchive", archive_link)
                                                return True
                                except:
                                    continue

                    result.attempts[-1] += " (no archives found)"
                else:
                    result.attempts[-1] += f" (HTTP {response.status})"

        except Exception as e:
            result.attempts[-1] += f" ({str(e)[:30]})"

        return False

    # ==================== MAIN PROCESSING ====================

    async def process_entry(self, session: aiohttp.ClientSession, entry: dict) -> ArchiveRetryResult:
        """Try all archive services for one entry."""
        entry_id = entry["entry_id"]
        url = entry["url"]

        result = ArchiveRetryResult(entry_id, url)

        # Try archive.ph first (best for newspapers)
        if await self.try_archive_ph(session, url, result):
            return result
        await asyncio.sleep(1)

        # Try archive.ph search
        if await self.try_archive_ph_search(session, url, result):
            return result
        await asyncio.sleep(1)

        # Try Google Cache
        if await self.try_google_cache(session, url, result):
            return result
        await asyncio.sleep(1)

        # Try 12ft.io
        if await self.try_12ft(session, url, result):
            return result
        await asyncio.sleep(1)

        # Try Ghostarchive
        if await self.try_ghostarchive(session, url, result):
            return result

        return result

    async def process_all(self, entries: list[dict]) -> list[ArchiveRetryResult]:
        """Process all entries."""
        print(f"\nTrying alternative archives for {len(entries)} URLs...\n")

        connector = aiohttp.TCPConnector(limit=5, ssl=False)
        timeout = aiohttp.ClientTimeout(total=90)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            for i, entry in enumerate(entries, 1):
                entry_id = entry["entry_id"]
                url = entry.get("url", "")
                domain = urlparse(url).netloc if url else "unknown"

                print(f"[{i}/{len(entries)}] {entry_id}: {domain}...")

                result = await self.process_entry(session, entry)
                self.results.append(result)

                if result.success:
                    print(f"    [OK] {result.method}")
                else:
                    print(f"    [FAIL] {', '.join(result.attempts)}")

                await asyncio.sleep(2)  # Be nice to archive services

        return self.results

    def generate_report(self) -> Path:
        """Generate report."""
        report_path = self.output_dir / "archive_retry_report.json"

        succeeded = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        report = {
            "generated_at": datetime.now().isoformat(),
            "total": len(self.results),
            "succeeded": len(succeeded),
            "still_failed": len(failed),
            "success_by_method": {},
            "succeeded_entries": [r.to_dict() for r in succeeded],
            "failed_entries": [r.to_dict() for r in failed],
        }

        for r in succeeded:
            m = r.method or "unknown"
            report["success_by_method"][m] = report["success_by_method"].get(m, 0) + 1

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        return report_path

    def print_summary(self):
        """Print summary."""
        succeeded = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        print("\n" + "=" * 60)
        print("ARCHIVE RETRY SUMMARY")
        print("=" * 60)
        print(f"Total: {len(self.results)}")
        print(f"Succeeded: {len(succeeded)}")
        print(f"Still failed: {len(failed)}")

        if succeeded:
            print("\nBy method:")
            methods = {}
            for r in succeeded:
                methods[r.method] = methods.get(r.method, 0) + 1
            for m, c in sorted(methods.items(), key=lambda x: -x[1]):
                print(f"  {m}: {c}")

        if failed:
            print(f"\nStill failed ({len(failed)}):")
            for r in failed:
                domain = urlparse(r.url).netloc if r.url else "?"
                print(f"  {r.entry_id}: {domain}")


async def async_main(args):
    print("=" * 60)
    print("Alternative Archive Services Retry")
    print("=" * 60)

    # Load failed entries from previous retry
    if args.input:
        input_path = args.input
    else:
        # Try to load from retry_report.json
        retry_report = SOURCES_DIR / "retry_report.json"
        if retry_report.exists():
            with open(retry_report) as f:
                data = json.load(f)
                entries = data.get("failed_entries", [])
        else:
            print("No retry_report.json found. Run retry_failed_sources.py first.")
            return 1

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
            entries = data.get("failed_entries", data.get("entries", []))

    if not entries:
        print("No entries to retry.")
        return 0

    if args.limit > 0:
        entries = entries[:args.limit]

    print(f"Loaded {len(entries)} entries")

    scraper = ArchiveScraper(output_dir=args.output)
    await scraper.process_all(entries)

    report_path = scraper.generate_report()
    print(f"\nReport: {report_path}")

    scraper.print_summary()
    return 0


def main():
    parser = argparse.ArgumentParser(description="Retry with alternative archives")
    parser.add_argument("--input", "-i", type=Path)
    parser.add_argument("--output", "-o", type=Path, default=SOURCES_DIR)
    parser.add_argument("--limit", "-l", type=int, default=0)

    args = parser.parse_args()
    return asyncio.run(async_main(args))


if __name__ == "__main__":
    exit(main())
