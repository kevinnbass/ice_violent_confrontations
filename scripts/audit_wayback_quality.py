#!/usr/bin/env python3
"""Audit wayback archives for quality issues."""

import os
from pathlib import Path
import re

# Indicators of poor quality content
PAYWALL_INDICATORS = [
    "subscribe to continue",
    "subscription required",
    "sign in to read",
    "create an account",
    "start your free trial",
    "subscribers only",
    "to continue reading",
    "unlock this article",
    "already a subscriber",
    "become a member",
    "premium content",
    "please log in",
    "register to read",
    "for full access",
]

ERROR_INDICATORS = [
    "page not found",
    "404 error",
    "403 forbidden",
    "access denied",
    "this page isn't available",
    "content no longer available",
    "article has been removed",
    "wayback machine",  # Sometimes wayback returns its own error page
    "the wayback machine has not archived",
]

BOT_BLOCK_INDICATORS = [
    "enable javascript",
    "please verify you are human",
    "captcha",
    "checking your browser",
    "ddos protection",
    "cloudflare",
    "please wait while we verify",
    "access to this page has been denied",
    "automated access",
]

def check_file_quality(filepath):
    """Check a wayback archive file for quality issues."""
    issues = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return ["read_error"], 0, str(e)

    content_lower = content.lower()
    char_count = len(content)
    line_count = len(content.split('\n'))

    # Check file size
    if char_count < 500:
        issues.append("very_short")
    elif char_count < 1500:
        issues.append("short")

    # Check for paywall indicators
    paywall_matches = [p for p in PAYWALL_INDICATORS if p in content_lower]
    if paywall_matches:
        issues.append(f"paywall:{paywall_matches[0][:20]}")

    # Check for error indicators
    error_matches = [e for e in ERROR_INDICATORS if e in content_lower]
    if error_matches:
        issues.append(f"error:{error_matches[0][:20]}")

    # Check for bot block indicators
    bot_matches = [b for b in BOT_BLOCK_INDICATORS if b in content_lower]
    if bot_matches:
        issues.append(f"bot_block:{bot_matches[0][:20]}")

    # Check content-to-boilerplate ratio (rough heuristic)
    # If most lines are very short, it's likely navigation/boilerplate
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    if lines:
        avg_line_len = sum(len(l) for l in lines) / len(lines)
        if avg_line_len < 30 and char_count < 5000:
            issues.append("mostly_boilerplate")

    return issues, char_count, None

def main():
    base_path = Path(__file__).parent.parent / "data" / "sources"

    # Find all wayback files
    wayback_files = list(base_path.glob("**/*_wayback.txt"))

    print(f"Found {len(wayback_files)} wayback archive files\n")

    # Categorize by quality
    good = []
    needs_review = []
    poor = []

    for filepath in sorted(wayback_files):
        rel_path = filepath.relative_to(base_path)
        entry_id = rel_path.parts[0]

        issues, char_count, error = check_file_quality(filepath)

        if error:
            poor.append((entry_id, str(rel_path), ["read_error"], 0))
        elif not issues:
            good.append((entry_id, str(rel_path), char_count))
        elif "very_short" in issues or any("error:" in i for i in issues) or any("bot_block:" in i for i in issues):
            poor.append((entry_id, str(rel_path), issues, char_count))
        else:
            needs_review.append((entry_id, str(rel_path), issues, char_count))

    # Print results
    print("=" * 80)
    print(f"GOOD QUALITY ({len(good)} files)")
    print("=" * 80)
    for entry_id, path, chars in good[:10]:  # Show first 10
        print(f"  {entry_id}: {chars:,} chars")
    if len(good) > 10:
        print(f"  ... and {len(good) - 10} more")

    print("\n" + "=" * 80)
    print(f"NEEDS REVIEW ({len(needs_review)} files)")
    print("=" * 80)
    for entry_id, path, issues, chars in needs_review:
        print(f"  {entry_id}: {chars:,} chars - {', '.join(issues)}")

    print("\n" + "=" * 80)
    print(f"POOR QUALITY - REPLACE WITH SCRAPFLY ({len(poor)} files)")
    print("=" * 80)
    for entry_id, path, issues, chars in poor:
        print(f"  {entry_id}: {chars:,} chars - {', '.join(issues)}")

    # Extract URLs for poor quality files
    print("\n" + "=" * 80)
    print("URLs TO FETCH WITH SCRAPFLY:")
    print("=" * 80)

    # We need to get the URLs from the JSON files
    import json

    incidents_path = base_path.parent / "incidents"
    poor_entry_ids = set(p[0] for p in poor)

    urls_to_fetch = []

    for json_file in incidents_path.glob("tier*.json"):
        if "backup" in str(json_file):
            continue
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for entry in data:
            entry_id = entry.get("id", "")
            if entry_id not in poor_entry_ids:
                continue

            for source in entry.get("sources", []):
                archive_path = source.get("archive_path", "")
                if "_wayback" in archive_path:
                    url = source.get("url", "")
                    if url:
                        urls_to_fetch.append({
                            "entry_id": entry_id,
                            "url": url,
                            "source_name": source.get("name", "unknown"),
                            "current_path": archive_path
                        })

    for item in urls_to_fetch:
        print(f"  {item['entry_id']}: {item['source_name']}")
        print(f"    {item['url']}")

    print(f"\nTotal URLs to fetch: {len(urls_to_fetch)}")

    # Save to JSON for the fetch script
    output_file = base_path.parent / "wayback_to_replace.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(urls_to_fetch, f, indent=2)
    print(f"\nSaved URL list to: {output_file}")

if __name__ == "__main__":
    main()
