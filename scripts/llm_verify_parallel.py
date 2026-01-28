#!/usr/bin/env python3
"""
LLM-Based Source Verification - Parallel Multi-Key Version

Uses multiple API keys concurrently, each with their own batch of workers.
For 4 API keys with batch_size=20, runs 80 verifications in parallel.

Usage:
    set DEEPSEEK_API_KEYS=sk-key1,sk-key2,sk-key3,sk-key4
    python scripts/llm_verify_parallel.py --batch-size 20

Features:
    - Each API key runs its own pool of workers independently
    - 4 keys × 20 batch = 80 concurrent verifications
    - Uses LOCAL archives only (no web fetching)
    - Faster throughput by parallelizing across keys
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
from dataclasses import dataclass, asdict
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
    score: int
    passed: bool
    reasoning: str
    issues: List[str]
    corrections: List[dict]
    article_says: dict
    sources_checked: int
    best_source: Optional[str]
    source_evaluations: List[dict]
    raw_response: str = ""  # Full LLM output for review
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
            "source_name": "<name from header>",
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


class KeyWorkerPool:
    """A worker pool dedicated to a single API key."""

    def __init__(self, api_key: str, key_index: int, batch_size: int = 20):
        self.api_key = api_key
        self.key_index = key_index
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(batch_size)
        self.processed = 0
        self.lock = asyncio.Lock()

    async def call_api(self, session: aiohttp.ClientSession, prompt: str) -> Tuple[bool, str]:
        """Call DeepSeek API with this pool's key."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 2500
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


class ParallelLLMVerifier:
    """Verifier that runs multiple API keys concurrently."""

    def __init__(self, api_keys: List[str], batch_size: int = 20):
        self.api_keys = api_keys
        self.batch_size = batch_size
        self.pools = [KeyWorkerPool(key, i, batch_size) for i, key in enumerate(api_keys)]
        self.results: List[VerificationResult] = []
        self.results_lock = asyncio.Lock()
        self.stats = {"processed": 0, "passed": 0, "failed": 0, "errors": 0}
        self.total_entries = 0
        self.pool_index = 0
        self.pool_lock = asyncio.Lock()

    def get_next_pool(self) -> KeyWorkerPool:
        """Round-robin pool selection."""
        pool = self.pools[self.pool_index % len(self.pools)]
        self.pool_index += 1
        return pool

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

    def get_local_articles(self, entry_id: str, sources: List[dict]) -> List[Tuple[str, str]]:
        """Get all local article texts for an entry. Returns [(source_name, text), ...]

        ONLY uses local archives - does not fetch from web.
        """
        articles = []
        entry_dir = SOURCES_DIR / entry_id

        if not entry_dir.exists():
            return articles

        # Try to match sources to archived files
        for i, source in enumerate(sources[:5]):
            name = source.get('name', f'Source {i}')
            archive_path = source.get('archive_path', '')

            text = None

            # Try explicit archive_path first
            if archive_path:
                # Handle both forward and back slashes
                archive_path = archive_path.replace('\\', '/')
                full_path = BASE_DIR / archive_path
                if full_path.exists():
                    try:
                        content = full_path.read_text(encoding='utf-8', errors='ignore')
                        if len(content) > 200:
                            text = content
                    except:
                        pass

            # Try numbered source files
            if not text:
                for pattern in [f"source_{i}_article.txt", f"article_{i}.txt", f"article_{i}_scrapfly.txt"]:
                    txt_file = entry_dir / pattern
                    if txt_file.exists():
                        try:
                            content = txt_file.read_text(encoding='utf-8', errors='ignore')
                            if len(content) > 200:
                                text = content
                                break
                        except:
                            pass

            # Try article.txt for first source
            if not text and i == 0:
                for pattern in ["article.txt", "article_wayback.txt"]:
                    txt_file = entry_dir / pattern
                    if txt_file.exists():
                        try:
                            content = txt_file.read_text(encoding='utf-8', errors='ignore')
                            if len(content) > 200:
                                text = content
                                break
                        except:
                            pass

            if text:
                articles.append((name, text))

        # If no articles matched sources, try to get any .txt files in the directory
        if not articles:
            for txt_file in sorted(entry_dir.glob("*.txt"))[:3]:
                if txt_file.name == "metadata.json":
                    continue
                try:
                    content = txt_file.read_text(encoding='utf-8', errors='ignore')
                    if len(content) > 200:
                        articles.append((txt_file.stem, content))
                except:
                    pass

        return articles

    def format_entry_for_prompt(self, entry: dict) -> str:
        """Format entry as JSON for the prompt."""
        relevant_fields = [
            'id', 'date', 'state', 'city', 'incident_type', 'outcome', 'outcome_detail',
            'victim_name', 'name', 'victim_age', 'age', 'victim_nationality', 'nationality',
            'notes', 'circumstances', 'affected_count', 'arrest_count', 'victim_count',
            'facility', 'agency', 'weapon_used', 'injury_type', 'cause_of_death'
        ]
        filtered = {k: v for k, v in entry.items() if k in relevant_fields and v}
        return json.dumps(filtered, indent=2)

    def format_sources_for_prompt(self, articles: List[Tuple[str, str]], sources_meta: List[dict]) -> str:
        """Format source articles for the prompt."""
        if not articles:
            return "[NO SOURCE ARTICLES AVAILABLE]"

        parts = []
        for i, (name, text) in enumerate(articles):
            url = sources_meta[i].get('url', '') if i < len(sources_meta) else ''

            # Truncate very long articles
            if len(text) > 6000:
                text = text[:6000] + "\n[... truncated ...]"

            header = f"### Source {i}: {name}"
            if url:
                header += f"\nURL: {url}"
            parts.append(f"{header}\n\n{text}")

        return "\n\n" + "=" * 40 + "\n\n".join(parts)

    def parse_llm_response(self, response: str) -> dict:
        """Parse JSON from LLM response."""
        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(response)
        except:
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    return json.loads(response[start:end])
            except:
                pass
        return {}

    async def verify_entry(self, session: aiohttp.ClientSession, entry: dict, pool: KeyWorkerPool) -> VerificationResult:
        """Verify a single entry using LLM via the assigned pool."""
        entry_id = entry.get('id', 'unknown')
        sources_meta = self.get_sources(entry)

        async with pool.semaphore:
            # Get local source texts only
            articles = self.get_local_articles(entry_id, sources_meta)

            if not articles:
                return VerificationResult(
                    entry_id=entry_id,
                    score=0,
                    passed=False,
                    reasoning="No local source articles available",
                    issues=["No archived sources found"],
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

            # Call LLM via pool
            success, response = await pool.call_api(session, prompt)

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
                source_evaluations=parsed.get('source_evaluations', []),
                raw_response=response,
                error=None
            )

    async def process_entry(self, session: aiohttp.ClientSession, entry: dict) -> VerificationResult:
        """Process an entry, assigning it to the next available pool."""
        async with self.pool_lock:
            pool = self.get_next_pool()

        result = await self.verify_entry(session, entry, pool)

        # Update stats and results
        async with self.results_lock:
            self.results.append(result)
            self.stats["processed"] += 1

            if result.error:
                self.stats["errors"] += 1
            elif result.passed:
                self.stats["passed"] += 1
            else:
                self.stats["failed"] += 1

            # Print progress
            icon = "[OK]" if result.passed else "[FAIL]" if not result.error else "[ERR]"
            key_info = f"K{pool.key_index}"
            progress = f"[{self.stats['processed']}/{self.total_entries}]"
            reasoning = result.reasoning[:50] if result.reasoning else "(no reasoning)"
            print(f"{progress} {key_info} {result.entry_id}: {icon} {result.score}% - {reasoning}")

        return result

    async def run(self, entries: List[dict]):
        """Run verification on all entries with parallel key pools."""
        self.total_entries = len(entries)

        print("=" * 70)
        print("LLM SOURCE VERIFICATION - PARALLEL MULTI-KEY")
        print("=" * 70)
        print(f"Entries to verify: {len(entries)}")
        print(f"API keys: {len(self.api_keys)}")
        print(f"Batch size per key: {self.batch_size}")
        print(f"Total concurrent workers: {len(self.api_keys) * self.batch_size}")
        print(f"Using LOCAL archives only (no web fetching)")
        print()

        connector = aiohttp.TCPConnector(limit=200, limit_per_host=50)

        start_time = time.time()

        async with aiohttp.ClientSession(connector=connector) as session:
            # Create all tasks - they will self-distribute across pools
            tasks = [self.process_entry(session, entry) for entry in entries]

            # Run all concurrently
            await asyncio.gather(*tasks, return_exceptions=True)

        elapsed = time.time() - start_time
        rate = len(entries) / elapsed if elapsed > 0 else 0

        print(f"\n{'=' * 70}")
        print(f"Completed {len(entries)} entries in {elapsed:.1f}s ({rate:.1f}/sec)")
        print(f"{'=' * 70}")

        self._generate_report()

    def _generate_report(self):
        """Generate verification report."""
        print(f"\nResults:")
        print(f"  Passed (70%+): {self.stats['passed']}")
        print(f"  Failed (<70%): {self.stats['failed']}")
        print(f"  Errors: {self.stats['errors']}")

        # Collect unrelated sources
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
            print(f"\n--- UNRELATED SOURCES ({len(unrelated_sources)}) ---")
            for us in unrelated_sources[:10]:
                print(f"  {us['entry_id']}: {us['source_name']} - {us['reason'][:50]}")
            if len(unrelated_sources) > 10:
                print(f"  ... and {len(unrelated_sources) - 10} more")

        # Failed entries
        failed = [r for r in self.results if not r.passed and not r.error]
        if failed:
            print(f"\n--- FAILED ENTRIES ({len(failed)}) ---")
            for r in sorted(failed, key=lambda x: x.score)[:10]:
                print(f"  {r.entry_id}: {r.score}% - {r.reasoning[:60]}")
            if len(failed) > 10:
                print(f"  ... and {len(failed) - 10} more")

        # Save report
        report = {
            "generated_at": datetime.now().isoformat(),
            "stats": self.stats,
            "config": {
                "api_keys": len(self.api_keys),
                "batch_size": self.batch_size,
                "total_workers": len(self.api_keys) * self.batch_size
            },
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
                    "raw_response": r.raw_response,
                    "error": r.error
                }
                for r in self.results
            ]
        }

        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved: {REPORT_FILE}")


async def main():
    parser = argparse.ArgumentParser(description="Parallel LLM verification with multiple API keys")
    parser.add_argument("--ids", type=str, help="Comma-separated list of entry IDs to verify")
    parser.add_argument("--limit", type=int, help="Limit number of entries to process")
    parser.add_argument("--offset", type=int, default=0, help="Skip first N entries")
    parser.add_argument("--batch-size", type=int, default=20, help="Workers per API key (default: 20)")
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
        print("  Or use --keys 'sk-xxx,sk-yyy,sk-zzz,sk-www'")
        sys.exit(1)

    print(f"Using {len(api_keys)} API key(s), {args.batch_size} workers each = {len(api_keys) * args.batch_size} total workers")

    # Create verifier
    verifier = ParallelLLMVerifier(api_keys=api_keys, batch_size=args.batch_size)

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
