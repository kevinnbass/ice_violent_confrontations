#!/usr/bin/env python3
"""
Deep Investigation of Problematic Entries

Investigates:
1. The 43 no_match entries - why doesn't content match?
2. The 19 fabricated entries that failed verification
3. Documents precise causes for each issue
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "incidents"
SOURCES_DIR = BASE_DIR / "data" / "sources"
REPORT_FILE = SOURCES_DIR / "full_verification_report.json"
FABRICATED_FILE = DATA_DIR / "fabricated_archive" / "FABRICATED_ENTRIES.json"

# Incident files for loading full entry details
INCIDENT_FILES = [
    "tier1_deaths_in_custody.json",
    "tier2_shootings.json",
    "tier2_less_lethal.json",
    "tier3_incidents.json",
    "tier4_incidents.json"
]

def load_all_incidents():
    """Load all incidents into a dict by ID."""
    incidents = {}
    for filename in INCIDENT_FILES:
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for entry in data:
                    entry['_source_file'] = filename
                    incidents[entry.get('id')] = entry
    return incidents

def load_fabricated():
    """Load fabricated entries into a dict by ID."""
    if FABRICATED_FILE.exists():
        with open(FABRICATED_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {e.get('id'): e for e in data.get('entries', [])}
    return {}

def get_article_text(entry_id):
    """Get the downloaded article text."""
    text_file = SOURCES_DIR / entry_id / "article.txt"
    if text_file.exists():
        with open(text_file, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    return None

def get_article_snippet(text, search_term, context=100):
    """Get a snippet of text around a search term."""
    if not text or not search_term:
        return None
    text_lower = text.lower()
    term_lower = search_term.lower()
    pos = text_lower.find(term_lower)
    if pos == -1:
        return None
    start = max(0, pos - context)
    end = min(len(text), pos + len(search_term) + context)
    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet

def analyze_no_match_entry(entry_id, verification_result, incident_data, article_text):
    """Deep analysis of why a no_match entry failed."""
    analysis = {
        "id": entry_id,
        "source_url": verification_result.get('source_url', ''),
        "fetch_method": verification_result.get('fetch_method', ''),
        "content_length": verification_result.get('content_length', 0),
        "confidence": verification_result.get('confidence', 0),
        "claimed_details": {},
        "verification_checks": verification_result.get('checks', {}),
        "diagnosis": [],
        "article_preview": "",
        "evidence": {}
    }

    # Get claimed details from incident data
    if incident_data:
        analysis["claimed_details"] = {
            "victim_name": incident_data.get('victim_name') or incident_data.get('name'),
            "date": incident_data.get('date'),
            "city": incident_data.get('city'),
            "state": incident_data.get('state'),
            "incident_type": incident_data.get('incident_type'),
            "outcome": incident_data.get('outcome'),
            "source_name": incident_data.get('source_name')
        }

    if not article_text:
        analysis["diagnosis"].append("NO_ARTICLE_TEXT: Article file is empty or missing")
        return analysis

    # Preview of article
    analysis["article_preview"] = article_text[:500] + "..." if len(article_text) > 500 else article_text

    # Check what's actually in the article
    text_lower = article_text.lower()

    # Name analysis
    victim_name = analysis["claimed_details"].get("victim_name")
    if victim_name:
        name_lower = victim_name.lower()
        if name_lower in text_lower:
            analysis["evidence"]["name_found"] = True
            analysis["evidence"]["name_snippet"] = get_article_snippet(article_text, victim_name)
        else:
            analysis["evidence"]["name_found"] = False
            # Check partial matches
            parts = name_lower.split()
            partial_found = []
            for part in parts:
                if len(part) > 2 and part in text_lower:
                    partial_found.append(part)
                    analysis["evidence"][f"partial_name_{part}"] = get_article_snippet(article_text, part, 50)

            if partial_found:
                analysis["diagnosis"].append(f"NAME_PARTIAL_MATCH: Found parts: {partial_found}, but not full name '{victim_name}'")
            else:
                analysis["diagnosis"].append(f"NAME_NOT_FOUND: '{victim_name}' not found anywhere in article")

    # Location analysis
    city = analysis["claimed_details"].get("city", "")
    state = analysis["claimed_details"].get("state", "")

    if city:
        if city.lower() in text_lower:
            analysis["evidence"]["city_found"] = True
            analysis["evidence"]["city_snippet"] = get_article_snippet(article_text, city)
        else:
            analysis["evidence"]["city_found"] = False
            analysis["diagnosis"].append(f"CITY_NOT_FOUND: '{city}' not found in article")

    if state:
        if state.lower() in text_lower:
            analysis["evidence"]["state_found"] = True
            analysis["evidence"]["state_snippet"] = get_article_snippet(article_text, state)
        else:
            analysis["evidence"]["state_found"] = False
            analysis["diagnosis"].append(f"STATE_NOT_FOUND: '{state}' not found in article")

    # Date analysis
    date_str = analysis["claimed_details"].get("date", "")
    if date_str:
        analysis["evidence"]["date_found"] = False
        # Check year at minimum
        year = date_str[:4] if len(date_str) >= 4 else None
        if year and year in article_text:
            analysis["evidence"]["year_found"] = True
        else:
            analysis["evidence"]["year_found"] = False
            analysis["diagnosis"].append(f"DATE_NOT_FOUND: No date matching '{date_str}' found")

    # What IS in the article?
    ice_keywords = ['ice', 'immigration', 'customs enforcement', 'detained', 'deportation', 'arrest']
    found_keywords = [kw for kw in ice_keywords if kw in text_lower]
    analysis["evidence"]["ice_keywords_found"] = found_keywords

    if not found_keywords:
        analysis["diagnosis"].append("NO_ICE_KEYWORDS: Article doesn't appear to be about ICE at all")

    # Determine root cause
    if len(analysis["diagnosis"]) == 0:
        analysis["diagnosis"].append("UNCLEAR: Need manual review")

    # Determine likely cause
    checks = verification_result.get('checks', {})
    name_found = checks.get('name', {}).get('found', False)
    location_found = checks.get('location', {}).get('found', False)
    date_found = checks.get('date', {}).get('found', False)

    if not name_found and not location_found and not date_found:
        if found_keywords:
            analysis["root_cause"] = "WRONG_ARTICLE: URL returns generic ICE content, not the specific incident"
        else:
            analysis["root_cause"] = "UNRELATED_CONTENT: URL returns content unrelated to the claimed incident"
    elif not name_found and location_found:
        analysis["root_cause"] = "WRONG_INCIDENT: Article is about ICE activity in same location but different incident/person"
    elif name_found and not location_found:
        analysis["root_cause"] = "LOCATION_MISMATCH: Found the name but location doesn't match"
    else:
        analysis["root_cause"] = "PARTIAL_MATCH: Some details match but not enough for verification"

    return analysis

def analyze_fabricated_entry(entry_id, verification_result, fabricated_data, article_text):
    """Deep analysis of a fabricated entry."""
    analysis = {
        "id": entry_id,
        "source_url": fabricated_data.get('source_url', ''),
        "original_fabrication_reason": fabricated_data.get('FABRICATION_REASON', ''),
        "verification_verdict": verification_result.get('verdict', 'unknown') if verification_result else 'not_in_report',
        "confidence": verification_result.get('confidence', 0) if verification_result else 0,
        "fetch_method": verification_result.get('fetch_method') if verification_result else None,
        "claimed_details": {
            "victim_name": fabricated_data.get('victim_name'),
            "date": fabricated_data.get('date'),
            "city": fabricated_data.get('city'),
            "state": fabricated_data.get('state'),
            "incident_type": fabricated_data.get('incident_type'),
            "outcome": fabricated_data.get('outcome'),
            "original_file": fabricated_data.get('original_file')
        },
        "url_analysis": {},
        "content_analysis": {},
        "final_determination": ""
    }

    # Analyze URL structure
    url = analysis["source_url"]
    if url:
        # Check for incomplete URL patterns
        if '/story/news/' in url and not any(c.isdigit() for c in url.split('/')[-1]):
            analysis["url_analysis"]["pattern"] = "INCOMPLETE_GANNETT_URL"
            analysis["url_analysis"]["explanation"] = "Gannett (USA Today network) URLs require numeric article IDs"
        elif '/article-' in url or '/article/' in url:
            if not any(c.isdigit() for c in url.split('/')[-1]):
                analysis["url_analysis"]["pattern"] = "INCOMPLETE_ARTICLE_URL"
                analysis["url_analysis"]["explanation"] = "Article URL missing numeric identifier"
        elif url.endswith('/'):
            analysis["url_analysis"]["pattern"] = "TRAILING_SLASH_ONLY"
            analysis["url_analysis"]["explanation"] = "URL appears to be a category/section page, not a specific article"
        else:
            analysis["url_analysis"]["pattern"] = "STANDARD"
            analysis["url_analysis"]["explanation"] = "URL structure appears normal"

    # Analyze content if available
    if article_text:
        text_lower = article_text.lower()
        analysis["content_analysis"]["has_content"] = True
        analysis["content_analysis"]["content_length"] = len(article_text)
        analysis["content_analysis"]["preview"] = article_text[:300] + "..."

        # Check what's in the content
        victim_name = analysis["claimed_details"]["victim_name"]
        if victim_name:
            if victim_name.lower() in text_lower:
                analysis["content_analysis"]["name_in_article"] = True
            else:
                analysis["content_analysis"]["name_in_article"] = False
                # Check if it's a generic landing page
                generic_indicators = ['subscribe', 'sign up', 'log in', 'create account', 'trending', 'most popular']
                generic_found = [g for g in generic_indicators if g in text_lower]
                if generic_found:
                    analysis["content_analysis"]["appears_generic"] = True
                    analysis["content_analysis"]["generic_indicators"] = generic_found

        # Check for ICE content
        ice_mentions = text_lower.count('ice') + text_lower.count('immigration')
        analysis["content_analysis"]["ice_mentions"] = ice_mentions
    else:
        analysis["content_analysis"]["has_content"] = False
        analysis["content_analysis"]["reason"] = "URL could not be fetched or returned empty content"

    # Final determination
    verdict = analysis["verification_verdict"]
    if verdict == "url_inaccessible":
        analysis["final_determination"] = "LIKELY_FABRICATED: URL does not exist and cannot be found in any archive"
        analysis["fabrication_evidence"] = "URL is inaccessible via direct fetch, Wayback Machine, and Google Cache"
    elif verdict == "no_match":
        if analysis["content_analysis"].get("appears_generic"):
            analysis["final_determination"] = "FABRICATED: URL returns generic website content, not a real article"
            analysis["fabrication_evidence"] = "Incomplete URL redirects to generic landing page"
        else:
            analysis["final_determination"] = "LIKELY_FABRICATED: Article exists but doesn't contain claimed incident details"
            analysis["fabrication_evidence"] = f"Name '{victim_name}' not found in article content"
    elif verdict == "weak_match":
        analysis["final_determination"] = "SUSPICIOUS: Some keywords match but specific incident details missing"
        analysis["fabrication_evidence"] = "Article may be about ICE generally but not this specific incident"
    elif verdict in ("verified", "likely_valid"):
        analysis["final_determination"] = "POSSIBLY_LEGITIMATE: Content matches claimed details"
        analysis["fabrication_evidence"] = "None - entry may have been incorrectly flagged"
    else:
        analysis["final_determination"] = "UNKNOWN: Requires manual review"

    return analysis

def main():
    print("=" * 70)
    print("DEEP INVESTIGATION OF PROBLEMATIC ENTRIES")
    print("=" * 70)

    # Load data
    print("\nLoading data...")
    with open(REPORT_FILE, 'r', encoding='utf-8') as f:
        report = json.load(f)

    incidents = load_all_incidents()
    fabricated = load_fabricated()

    entries = report.get('entries', [])
    entries_by_id = {e['id']: e for e in entries}

    # Separate by verdict
    no_match_entries = [e for e in entries if e['verdict'] == 'no_match']
    inaccessible_entries = [e for e in entries if e['verdict'] == 'url_inaccessible']

    print(f"  Total entries in report: {len(entries)}")
    print(f"  No match entries: {len(no_match_entries)}")
    print(f"  URL inaccessible: {len(inaccessible_entries)}")
    print(f"  Fabricated archive entries: {len(fabricated)}")

    # =========================================================================
    # PART 1: Investigate 43 no_match entries
    # =========================================================================
    print("\n" + "=" * 70)
    print("PART 1: INVESTIGATING NO_MATCH ENTRIES")
    print("=" * 70)

    no_match_analyses = []
    root_cause_counts = defaultdict(int)

    for entry in no_match_entries:
        entry_id = entry['id']
        incident_data = incidents.get(entry_id) or fabricated.get(entry_id)
        article_text = get_article_text(entry_id)

        analysis = analyze_no_match_entry(entry_id, entry, incident_data, article_text)
        no_match_analyses.append(analysis)
        root_cause_counts[analysis.get('root_cause', 'UNKNOWN')] += 1

    print(f"\nRoot Cause Summary for {len(no_match_entries)} no_match entries:")
    for cause, count in sorted(root_cause_counts.items(), key=lambda x: -x[1]):
        print(f"  {cause}: {count}")

    print("\n" + "-" * 50)
    print("DETAILED NO_MATCH FINDINGS:")
    print("-" * 50)

    for analysis in no_match_analyses:
        print(f"\n[{analysis['id']}]")
        print(f"  URL: {analysis['source_url'][:70]}...")
        print(f"  Claimed: {analysis['claimed_details'].get('victim_name', 'N/A')} | {analysis['claimed_details'].get('city', 'N/A')}, {analysis['claimed_details'].get('state', 'N/A')} | {analysis['claimed_details'].get('date', 'N/A')}")
        print(f"  Root Cause: {analysis.get('root_cause', 'UNKNOWN')}")
        for diag in analysis.get('diagnosis', [])[:3]:
            print(f"    - {diag}")

    # =========================================================================
    # PART 2: Investigate 20 fabricated entries
    # =========================================================================
    print("\n" + "=" * 70)
    print("PART 2: INVESTIGATING FABRICATED ARCHIVE ENTRIES")
    print("=" * 70)

    fabricated_analyses = []
    determination_counts = defaultdict(int)

    for entry_id, fab_data in fabricated.items():
        verification_result = entries_by_id.get(entry_id)
        article_text = get_article_text(entry_id)

        analysis = analyze_fabricated_entry(entry_id, verification_result, fab_data, article_text)
        fabricated_analyses.append(analysis)
        determination_counts[analysis.get('final_determination', 'UNKNOWN').split(':')[0]] += 1

    print(f"\nFinal Determination Summary for {len(fabricated)} fabricated entries:")
    for det, count in sorted(determination_counts.items(), key=lambda x: -x[1]):
        print(f"  {det}: {count}")

    print("\n" + "-" * 50)
    print("DETAILED FABRICATED ENTRY FINDINGS:")
    print("-" * 50)

    for analysis in fabricated_analyses:
        print(f"\n[{analysis['id']}]")
        print(f"  Original File: {analysis['claimed_details'].get('original_file', 'N/A')}")
        print(f"  URL: {analysis['source_url'][:70]}...")
        print(f"  Claimed: {analysis['claimed_details'].get('victim_name', 'N/A')} | {analysis['claimed_details'].get('city', 'N/A')}, {analysis['claimed_details'].get('state', 'N/A')}")
        print(f"  Original Flagging Reason: {analysis['original_fabrication_reason'][:80]}...")
        print(f"  Verification Verdict: {analysis['verification_verdict']} ({analysis['confidence']}%)")
        print(f"  URL Pattern: {analysis['url_analysis'].get('pattern', 'N/A')}")
        print(f"  FINAL DETERMINATION: {analysis['final_determination']}")
        if analysis.get('fabrication_evidence'):
            print(f"  Evidence: {analysis['fabrication_evidence']}")

    # =========================================================================
    # Save detailed report
    # =========================================================================
    detailed_report = {
        "investigation_date": datetime.now().isoformat(),
        "summary": {
            "no_match_entries": {
                "total": len(no_match_entries),
                "root_causes": dict(root_cause_counts)
            },
            "fabricated_entries": {
                "total": len(fabricated),
                "determinations": dict(determination_counts)
            }
        },
        "no_match_analyses": no_match_analyses,
        "fabricated_analyses": fabricated_analyses
    }

    output_file = SOURCES_DIR / "investigation_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_report, f, indent=2, default=str)

    print(f"\n\nDetailed report saved to: {output_file}")

    # =========================================================================
    # Generate actionable summary
    # =========================================================================
    print("\n" + "=" * 70)
    print("ACTIONABLE SUMMARY")
    print("=" * 70)

    # Entries that should definitely be removed
    definitely_remove = []
    needs_review = []
    possibly_legitimate = []

    for analysis in fabricated_analyses:
        det = analysis['final_determination']
        if 'FABRICATED' in det or 'LIKELY_FABRICATED' in det:
            definitely_remove.append(analysis['id'])
        elif 'SUSPICIOUS' in det:
            needs_review.append(analysis['id'])
        elif 'LEGITIMATE' in det:
            possibly_legitimate.append(analysis['id'])

    for analysis in no_match_analyses:
        cause = analysis.get('root_cause', '')
        if 'WRONG_ARTICLE' in cause or 'UNRELATED' in cause:
            if analysis['id'] not in definitely_remove:
                needs_review.append(analysis['id'])

    print(f"\n1. DEFINITELY REMOVE ({len(definitely_remove)} entries):")
    print(f"   IDs: {', '.join(definitely_remove)}")

    print(f"\n2. NEEDS MANUAL REVIEW ({len(needs_review)} entries):")
    print(f"   IDs: {', '.join(needs_review[:20])}")
    if len(needs_review) > 20:
        print(f"   ... and {len(needs_review) - 20} more")

    print(f"\n3. POSSIBLY INCORRECTLY FLAGGED ({len(possibly_legitimate)} entries):")
    print(f"   IDs: {', '.join(possibly_legitimate)}")

    return detailed_report

if __name__ == "__main__":
    main()
