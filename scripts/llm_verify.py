#!/usr/bin/env python3
"""
LLM-Based Source Verification using DeepSeek

Uses DeepSeek API to verify that source articles support database entries.
Much more accurate than keyword matching.

Usage:
    # Set API keys (comma-separated for multiple keys)
    set DEEPSEEK_API_KEYS=sk-xxx,sk-yyy,sk-zzz,sk-www

    # Run verification
    python scripts/llm_verify.py --ids T3-155,T3-157,T3-188  # Smoke test specific IDs
    python scripts/llm_verify.py --limit 20                   # First 20 entries
    python scripts/llm_verify.py                              # All entries

Features:
    - Processes entries in parallel (20 workers default)
    - Round-robins across multiple API keys for higher throughput
    - Downloads all sources for each entry
    - Returns: score (0-100), pass/fail, reasoning
"""

import json
import asyncio
import aiohttp
import os
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import time

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "incidents"
SOURCES_DIR = BASE_DIR / "data" / "sources"
REPORT_FILE = SOURCES_DIR / "llm_verification_report.json"

INCIDENT_FILES = [
    "tier1_deaths_in_custody.json",
    "tier2_shootings.json",
    "tier2_less_lethal.json",
    "tier3_incidents.json",
    "tier4_incidents.json"
]

# DeepSeek API config
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"


@dataclass
class VerificationResult:
    entry_id: str
    score: int  # 0-100
    passed: bool
    reasoning: str
    issues: List[str]
    corrections: List[dict]  # [{field, current, should_be, reason}]
    article_says: dict  # {date, location, victim_name, agency, key_facts}
    sources_checked: int
    best_source: Optional[str]
    source_evaluations: List[dict]  # [{source_name, relevant, reason, quality}]
    raw_response: str
    error: Optional[str] = None


VERIFICATION_PROMPT = """You are a fact-checker verifying that news articles support database entries about ICE (Immigration and Customs Enforcement) incidents.

## Database Entry to Verify:
```json
{entry_json}
```

## Source Article(s):
{sources_text}

## Your Task:
1. First, evaluate EACH source article individually to determine if it's relevant to the database entry
2. Then, using ONLY the relevant sources, verify the database entry claims

For each source, determine:
- Is it about the SAME incident described in the entry?
- Is it completely unrelated (wrong topic, wrong date, different event)?
- Does it provide useful supporting information?

## Response Format (JSON):
```json
{{
    "source_evaluations": [
        {{
            "source_name": "<name from header, e.g. 'Source 0' or 'Primary source'>",
            "relevant": <true/false - is this source about the same incident?>,
            "quality": "<excellent/good/partial/unrelated>",
            "reason": "<1 sentence explaining why relevant or unrelated>"
        }}
    ],
    "best_source": "<name of the most relevant/reliable source, or null if none>",
    "score": <0-100 based on ALL relevant sources combined>,
    "passed": <true if score >= 70, false otherwise>,
    "event_match": "<yes/partial/no> - brief explanation",
    "date_match": "<exact/close/wrong/not_found> - brief explanation",
    "location_match": "<yes/partial/no> - brief explanation",
    "name_match": "<yes/partial/no/not_applicable> - brief explanation",
    "details_match": "<yes/partial/no> - brief explanation",
    "agency_mentioned": <true/false>,
    "issues": ["list of specific problems or discrepancies"],
    "corrections": [
        {{
            "field": "<field_name to change>",
            "current": "<current value in entry>",
            "should_be": "<correct value from article>",
            "reason": "<why this change is needed>"
        }}
    ],
    "article_says": {{
        "date": "<date mentioned in relevant article(s) or 'not found'>",
        "location": "<location mentioned in relevant article(s)>",
        "victim_name": "<name if mentioned, or 'not mentioned'>",
        "agency": "<agency mentioned: ICE/CBP/DHS/Border Patrol/etc>",
        "key_facts": ["list 3-5 key facts from the relevant article(s)"]
    }},
    "reasoning": "2-3 sentence summary of verification result"
}}
```

Scoring guide:
- 90-100: Perfect or near-perfect match from at least one relevant source
- 70-89: Solid match with minor discrepancies
- 50-69: Partial match, some concerns
- 30-49: Weak match, significant issues
- 0-29: No relevant sources, or sources don't support entry

IMPORTANT:
- If ALL sources are unrelated to the entry, set score to 0 and mark all as relevant:false
- If SOME sources are unrelated but others support the entry, still pass if relevant sources verify it
- The "source_evaluations" array MUST have one entry per source provided
- Unrelated sources should be flagged so we can remove them from the database
- Be strict but fair. Minor date differences (few days) are OK if clearly same event.

Respond with ONLY the JSON, no other text."""


class LLMVerifier:
    def __init__(self, api_keys: List[str], workers: int = 20):
        self.api_keys = api_keys
        self.workers = workers
        self.key_index = 0
        self.key_lock = asyncio.Lock()
        self.results: List[VerificationResult] = []
        self.stats = {"processed": 0, "passed": 0, "failed": 0, "errors": 0}

    def get_next_api_key(self) -> str:
        """Round-robin API key selection."""
        key = self.api_keys[self.key_index % len(self.api_keys)]
        self.key_index += 1
        return key

    def load_incidents(self) -> List[dict]:
        """Load all incidents from JSON files."""
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

    def get_sources(self, entry: dict) -> List[dict]:
        """Get sources array from entry."""
        if 'sources' in entry:
            return entry['sources']
        if entry.get('source_url'):
            return [{'url': entry.get('source_url'), 'name': entry.get('source_name'), 'primary': True}]
        return []

    def get_local_articles(self, entry_id: str) -> List[Tuple[str, str]]:
        """Get all local article texts for an entry. Returns [(source_name, text), ...]"""
        articles = []
        entry_dir = SOURCES_DIR / entry_id

        if not entry_dir.exists():
            return articles

        # Check for numbered source files first (new multi-source format)
        for i in range(10):
            txt_file = entry_dir / f"source_{i}_article.txt"
            if txt_file.exists():
                try:
                    content = txt_file.read_text(encoding='utf-8')
                    if len(content) > 200:
                        articles.append((f"Source {i}", content))
                except:
                    pass

        # Fall back to single article.txt
        if not articles:
            article_txt = entry_dir / "article.txt"
            if article_txt.exists():
                try:
                    content = article_txt.read_text(encoding='utf-8')
                    if len(content) > 200:
                        articles.append(("Primary source", content))
                except:
                    pass

        return articles

    async def fetch_article(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Fetch article from URL."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15), ssl=False) as r:
                if r.status == 200:
                    html = await r.text()
                    # Extract text from HTML
                    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.I)
                    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.I)
                    text = re.sub(r'<[^>]+>', ' ', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if len(text) > 200:
                        return text
        except:
            pass
        return None

    async def get_all_source_texts(self, session: aiohttp.ClientSession, entry: dict) -> List[Tuple[str, str]]:
        """Get texts from all sources (local first, then fetch missing ones)."""
        entry_id = entry.get('id', '')
        sources = self.get_sources(entry)
        articles = []
        entry_dir = SOURCES_DIR / entry_id

        # Process each source
        for i, source in enumerate(sources[:5]):  # Up to 5 sources
            url = source.get('url', '')
            name = source.get('name', f'Source {i}')

            # Check for local cache first
            local_file = entry_dir / f"source_{i}_article.txt"
            legacy_file = entry_dir / "article.txt" if i == 0 else None

            text = None

            # Try numbered source file first
            if local_file.exists():
                try:
                    content = local_file.read_text(encoding='utf-8')
                    if len(content) > 200:
                        text = content
                except:
                    pass

            # Try legacy article.txt for source 0
            if not text and legacy_file and legacy_file.exists():
                try:
                    content = legacy_file.read_text(encoding='utf-8')
                    if len(content) > 200:
                        text = content
                except:
                    pass

            # Fetch from web if no local cache
            if not text and url:
                text = await self.fetch_article(session, url)
                if text:
                    # Save for future use
                    entry_dir.mkdir(parents=True, exist_ok=True)
                    try:
                        with open(local_file, 'w', encoding='utf-8') as f:
                            f.write(text)
                    except:
                        pass

            if text:
                articles.append((name, text))

        return articles

    def format_entry_for_prompt(self, entry: dict) -> str:
        """Format entry as JSON for the prompt, keeping only relevant fields."""
        relevant_fields = [
            'id', 'date', 'state', 'city', 'incident_type', 'outcome', 'outcome_detail',
            'victim_name', 'name', 'victim_age', 'age', 'victim_nationality', 'nationality',
            'notes', 'circumstances', 'affected_count', 'arrest_count', 'victim_count',
            'facility', 'agency', 'weapon_used', 'injury_type', 'cause_of_death'
        ]
        filtered = {k: v for k, v in entry.items() if k in relevant_fields and v}
        return json.dumps(filtered, indent=2)

    def format_sources_for_prompt(self, articles: List[Tuple[str, str]], sources_meta: List[dict]) -> str:
        """Format source articles for the prompt with clear numbered headers."""
        if not articles:
            return "[NO SOURCE ARTICLES AVAILABLE]"

        parts = []
        for i, (name, text) in enumerate(articles):
            # Get URL from metadata if available
            url = ""
            if i < len(sources_meta):
                url = sources_meta[i].get('url', '')

            # Truncate very long articles
            if len(text) > 8000:
                text = text[:8000] + "\n[... truncated ...]"

            header = f"### Source {i}: {name}"
            if url:
                header += f"\nURL: {url}"
            parts.append(f"{header}\n\n{text}")

        return "\n\n" + "=" * 40 + "\n\n".join(parts)

    async def call_deepseek(self, session: aiohttp.ClientSession, prompt: str) -> Tuple[bool, str]:
        """Call DeepSeek API."""
        api_key = self.get_next_api_key()

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 1000
        }

        try:
            async with session.post(DEEPSEEK_API_URL, headers=headers, json=payload,
                                   timeout=aiohttp.ClientTimeout(total=60)) as r:
                if r.status == 200:
                    data = await r.json()
                    content = data['choices'][0]['message']['content']
                    return True, content
                else:
                    error_text = await r.text()
                    return False, f"HTTP {r.status}: {error_text[:200]}"
        except Exception as e:
            return False, str(e)

    def parse_llm_response(self, response: str) -> dict:
        """Parse JSON from LLM response."""
        # Try to extract JSON from response
        try:
            # Look for JSON block
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            # Try direct parse
            return json.loads(response)
        except:
            # Try to find JSON object in response
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(response[start:end])
            except:
                pass
        return {}

    async def verify_entry(self, session: aiohttp.ClientSession, entry: dict,
                          semaphore: asyncio.Semaphore) -> VerificationResult:
        """Verify a single entry using LLM."""
        entry_id = entry.get('id', 'unknown')
        sources_meta = self.get_sources(entry)

        async with semaphore:
            # Get source texts
            articles = await self.get_all_source_texts(session, entry)

            if not articles:
                return VerificationResult(
                    entry_id=entry_id,
                    score=0,
                    passed=False,
                    reasoning="No source articles available",
                    issues=["Could not fetch any source articles"],
                    corrections=[],
                    article_says={},
                    sources_checked=0,
                    best_source=None,
                    source_evaluations=[],
                    raw_response="",
                    error="no_sources"
                )

            # Build prompt
            entry_json = self.format_entry_for_prompt(entry)
            sources_text = self.format_sources_for_prompt(articles, sources_meta)
            prompt = VERIFICATION_PROMPT.format(entry_json=entry_json, sources_text=sources_text)

            # Call LLM
            success, response = await self.call_deepseek(session, prompt)

            if not success:
                return VerificationResult(
                    entry_id=entry_id,
                    score=0,
                    passed=False,
                    reasoning=f"API error: {response}",
                    issues=["LLM API call failed"],
                    corrections=[],
                    article_says={},
                    sources_checked=len(articles),
                    best_source=articles[0][0] if articles else None,
                    source_evaluations=[],
                    raw_response=response,
                    error="api_error"
                )

            # Parse response
            parsed = self.parse_llm_response(response)

            if not parsed:
                return VerificationResult(
                    entry_id=entry_id,
                    score=0,
                    passed=False,
                    reasoning="Could not parse LLM response",
                    issues=["Invalid JSON response from LLM"],
                    corrections=[],
                    article_says={},
                    sources_checked=len(articles),
                    best_source=articles[0][0] if articles else None,
                    source_evaluations=[],
                    raw_response=response,
                    error="parse_error"
                )

            score = parsed.get('score', 0)
            passed = parsed.get('passed', score >= 70)
            source_evals = parsed.get('source_evaluations', [])

            return VerificationResult(
                entry_id=entry_id,
                score=score,
                passed=passed,
                reasoning=parsed.get('reasoning', ''),
                issues=parsed.get('issues', []),
                corrections=parsed.get('corrections', []),
                article_says=parsed.get('article_says', {}),
                sources_checked=len(articles),
                best_source=parsed.get('best_source', articles[0][0] if articles else None),
                source_evaluations=source_evals,
                raw_response=response,
                error=None
            )

    async def run(self, entries: List[dict]):
        """Run verification on entries."""
        print("=" * 60)
        print("LLM SOURCE VERIFICATION (DeepSeek)")
        print("=" * 60)
        print(f"Entries to verify: {len(entries)}")
        print(f"API keys available: {len(self.api_keys)}")
        print(f"Parallel workers: {self.workers}")
        print()

        semaphore = asyncio.Semaphore(self.workers)
        connector = aiohttp.TCPConnector(limit=50)

        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [self.verify_entry(session, entry, semaphore) for entry in entries]

            # Process with progress
            for i, coro in enumerate(asyncio.as_completed(tasks), 1):
                result = await coro
                self.results.append(result)

                # Update stats
                self.stats["processed"] += 1
                if result.error:
                    self.stats["errors"] += 1
                elif result.passed:
                    self.stats["passed"] += 1
                else:
                    self.stats["failed"] += 1

                # Print progress
                icon = "[OK]" if result.passed else "[FAIL]" if not result.error else "[ERR]"
                reasoning_preview = result.reasoning[:60] if result.reasoning else "(no reasoning)"
                print(f"[{i}/{len(entries)}] {result.entry_id}: {icon} {result.score}% - {reasoning_preview}")

        self._generate_report()

    def _generate_report(self):
        """Generate verification report."""
        print("\n" + "=" * 60)
        print("VERIFICATION COMPLETE")
        print("=" * 60)

        print(f"\nResults:")
        print(f"  Passed (70%+): {self.stats['passed']}")
        print(f"  Failed (<70%): {self.stats['failed']}")
        print(f"  Errors: {self.stats['errors']}")

        # Collect unrelated sources for removal
        unrelated_sources = []
        for r in self.results:
            if r.source_evaluations:
                for se in r.source_evaluations:
                    if not se.get('relevant', True):
                        unrelated_sources.append({
                            'entry_id': r.entry_id,
                            'source_name': se.get('source_name'),
                            'reason': se.get('reason', 'marked as unrelated')
                        })

        if unrelated_sources:
            print(f"\n--- UNRELATED SOURCES TO REMOVE ({len(unrelated_sources)}) ---")
            for us in unrelated_sources[:15]:
                print(f"  {us['entry_id']}: {us['source_name']} - {us['reason'][:60]}")

        # Failed entries with corrections
        failed = [r for r in self.results if not r.passed and not r.error]
        if failed:
            print(f"\n--- FAILED ENTRIES ({len(failed)}) ---")
            for r in sorted(failed, key=lambda x: x.score)[:20]:
                print(f"\n  {r.entry_id}: {r.score}%")
                print(f"    Reasoning: {r.reasoning[:70]}")
                if r.source_evaluations:
                    print(f"    Source evaluations:")
                    for se in r.source_evaluations:
                        icon = "[+]" if se.get('relevant', False) else "[-]"
                        print(f"      {icon} {se.get('source_name')}: {se.get('quality', '?')} - {se.get('reason', '')[:50]}")
                if r.issues:
                    print(f"    Issues:")
                    for issue in r.issues[:3]:
                        print(f"      - {issue[:70]}")
                if r.corrections:
                    print(f"    Suggested corrections:")
                    for c in r.corrections[:3]:
                        print(f"      - {c.get('field')}: '{c.get('current')}' -> '{c.get('should_be')}'")
                if r.article_says:
                    print(f"    Article says:")
                    for k, v in r.article_says.items():
                        if k != 'key_facts' and v:
                            print(f"      {k}: {v}")

        # Save report
        report = {
            "generated_at": datetime.now().isoformat(),
            "stats": self.stats,
            "unrelated_sources": unrelated_sources,
            "results": [
                {
                    "entry_id": r.entry_id,
                    "score": r.score,
                    "passed": r.passed,
                    "reasoning": r.reasoning,
                    "issues": r.issues,
                    "corrections": r.corrections,
                    "article_says": r.article_says,
                    "sources_checked": r.sources_checked,
                    "best_source": r.best_source,
                    "source_evaluations": r.source_evaluations,
                    "error": r.error
                }
                for r in self.results
            ]
        }

        with open(REPORT_FILE, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved: {REPORT_FILE}")


async def main():
    parser = argparse.ArgumentParser(description="LLM-based source verification using DeepSeek")
    parser.add_argument("--ids", type=str, help="Comma-separated list of entry IDs to verify")
    parser.add_argument("--limit", type=int, help="Limit number of entries to process")
    parser.add_argument("--offset", type=int, default=0, help="Skip first N entries before applying limit")
    parser.add_argument("--workers", type=int, default=20, help="Number of parallel workers")
    parser.add_argument("--keys", type=str, help="Comma-separated API keys (or set DEEPSEEK_API_KEYS env)")

    args = parser.parse_args()

    # Get API keys
    api_keys = []
    if args.keys:
        api_keys = [k.strip() for k in args.keys.split(',') if k.strip()]
    else:
        env_keys = os.environ.get('DEEPSEEK_API_KEYS', '')
        if env_keys:
            api_keys = [k.strip() for k in env_keys.split(',') if k.strip()]

    if not api_keys:
        print("ERROR: No API keys provided.")
        print("  Set DEEPSEEK_API_KEYS environment variable (comma-separated)")
        print("  Or use --keys 'sk-xxx,sk-yyy,sk-zzz'")
        sys.exit(1)

    print(f"Using {len(api_keys)} API key(s)")

    # Create verifier
    verifier = LLMVerifier(api_keys=api_keys, workers=args.workers)

    # Load entries
    entries = verifier.load_incidents()
    print(f"Total entries loaded: {len(entries)}")

    # Filter
    if args.ids:
        ids = [i.strip() for i in args.ids.split(',')]
        entries = [e for e in entries if e.get('id') in ids]
        print(f"Filtered to {len(entries)} specific entries")

    if args.offset:
        entries = entries[args.offset:]
        print(f"Skipped first {args.offset} entries, {len(entries)} remaining")

    if args.limit:
        entries = entries[:args.limit]
        print(f"Limited to {len(entries)} entries")

    if not entries:
        print("No entries to verify!")
        sys.exit(1)

    # Run
    await verifier.run(entries)


if __name__ == "__main__":
    asyncio.run(main())
