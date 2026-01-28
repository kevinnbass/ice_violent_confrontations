#!/usr/bin/env python3
"""
Analyze verification results and generate recommendations.
Does NOT delete anything - only creates reports for manual review.
"""

import json
from pathlib import Path
from collections import defaultdict

def main():
    base_path = Path(__file__).parent.parent

    # Load verification report
    report_path = base_path / "data" / "sources" / "llm_verification_report.json"
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)

    # Load all incident files to check source counts
    incidents_path = base_path / "data" / "incidents"
    all_entries = {}
    for json_file in incidents_path.glob("tier*.json"):
        if "backup" in str(json_file):
            continue
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for entry in data:
            all_entries[entry["id"]] = entry

    # Categorize results
    passed = []
    failed_no_sources = []  # Score 0, no valid sources at all
    failed_partial = []     # Score > 0 but < 70, some issues
    errors_parse = []
    errors_api = []
    errors_no_sources = []

    for result in report["results"]:
        entry_id = result["entry_id"]
        error = result.get("error")

        if error:
            if error == "parse_error":
                errors_parse.append(result)
            elif error == "api_error":
                errors_api.append(result)
            elif error == "no_sources":
                errors_no_sources.append(result)
            else:
                errors_api.append(result)
        elif result.get("passed"):
            passed.append(result)
        elif result.get("score", 0) == 0:
            failed_no_sources.append(result)
        else:
            failed_partial.append(result)

    # Analyze unrelated sources
    unrelated_by_entry = defaultdict(list)
    for src in report.get("unrelated_sources", []):
        unrelated_by_entry[src["entry_id"]].append(src)

    # Generate report
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("ICE INCIDENTS DATABASE - VERIFICATION ANALYSIS")
    output_lines.append("=" * 80)
    output_lines.append(f"\nTotal entries: {len(report['results'])}")
    output_lines.append(f"Passed: {len(passed)} ({len(passed)*100/len(report['results']):.1f}%)")
    output_lines.append(f"Failed (no valid sources): {len(failed_no_sources)}")
    output_lines.append(f"Failed (partial issues): {len(failed_partial)}")
    output_lines.append(f"Errors (parse): {len(errors_parse)}")
    output_lines.append(f"Errors (API): {len(errors_api)}")
    output_lines.append(f"Errors (no sources): {len(errors_no_sources)}")
    output_lines.append(f"\nUnrelated sources flagged: {len(report.get('unrelated_sources', []))}")

    # SECTION 1: Critical - Entries with no valid sources
    output_lines.append("\n" + "=" * 80)
    output_lines.append("SECTION 1: ENTRIES NEEDING NEW SOURCES (score=0)")
    output_lines.append("These entries have NO valid archived sources. Need to find new sources or archive.")
    output_lines.append("=" * 80)

    for result in sorted(failed_no_sources, key=lambda x: x["entry_id"]):
        entry_id = result["entry_id"]
        entry = all_entries.get(entry_id, {})
        output_lines.append(f"\n{entry_id}:")
        output_lines.append(f"  Title: {entry.get('title', 'N/A')[:70]}")
        output_lines.append(f"  Date: {entry.get('date', 'N/A')}")
        output_lines.append(f"  Location: {entry.get('location', entry.get('city', 'N/A'))}")
        output_lines.append(f"  Sources in DB: {len(entry.get('sources', []))}")

        # Show what sources exist
        for src in entry.get("sources", []):
            archived = "ARCHIVED" if src.get("archive_path") else "NOT ARCHIVED"
            output_lines.append(f"    - {src.get('name', 'unknown')}: {archived}")
            if src.get("url"):
                output_lines.append(f"      URL: {src['url'][:80]}")

        output_lines.append(f"  LLM Issue: {result.get('issues', ['N/A'])[0][:100]}")

    # SECTION 2: Entries with partial issues (score > 0 but failed)
    output_lines.append("\n" + "=" * 80)
    output_lines.append("SECTION 2: ENTRIES WITH PARTIAL ISSUES (score > 0 but < 70)")
    output_lines.append("These entries have some support but need corrections or additional sources.")
    output_lines.append("=" * 80)

    for result in sorted(failed_partial, key=lambda x: -x.get("score", 0)):
        entry_id = result["entry_id"]
        entry = all_entries.get(entry_id, {})
        output_lines.append(f"\n{entry_id} (score={result.get('score', 0)}):")
        output_lines.append(f"  Title: {entry.get('title', 'N/A')[:70]}")
        output_lines.append(f"  Issue: {result.get('issues', ['N/A'])[0][:100]}")

        # Show corrections if any
        for correction in result.get("corrections", []):
            output_lines.append(f"  Correction: {correction.get('field', '?')}: '{correction.get('current', '?')[:30]}' -> '{correction.get('suggested', '?')[:30]}'")

    # SECTION 3: Parse/API errors - need re-verification
    output_lines.append("\n" + "=" * 80)
    output_lines.append("SECTION 3: ENTRIES NEEDING RE-VERIFICATION (errors)")
    output_lines.append("=" * 80)

    for result in errors_parse + errors_api:
        entry_id = result["entry_id"]
        output_lines.append(f"  {entry_id}: {result.get('error', 'unknown')}")

    if errors_no_sources:
        output_lines.append("\nNo sources attached:")
        for result in errors_no_sources:
            output_lines.append(f"  {result['entry_id']}")

    # SECTION 4: Unrelated sources by category
    output_lines.append("\n" + "=" * 80)
    output_lines.append("SECTION 4: UNRELATED SOURCES (consider removing)")
    output_lines.append("These sources don't support their entries but entries may have other valid sources.")
    output_lines.append("=" * 80)

    # Group by reason type
    generic_overview = []
    wrong_incident = []
    wrong_date = []
    other = []

    for src in report.get("unrelated_sources", []):
        reason = src.get("reason", "").lower()
        if "general" in reason or "overview" in reason or "generic" in reason or "multiple" in reason:
            generic_overview.append(src)
        elif "different incident" in reason or "different event" in reason or "different" in reason:
            wrong_incident.append(src)
        elif "different date" in reason or "dated" in reason:
            wrong_date.append(src)
        else:
            other.append(src)

    output_lines.append(f"\nGeneric/Overview articles attached to specific incidents: {len(generic_overview)}")
    for src in generic_overview[:10]:  # Show first 10
        output_lines.append(f"  {src['entry_id']}: {src['source_name']}")
    if len(generic_overview) > 10:
        output_lines.append(f"  ... and {len(generic_overview) - 10} more")

    output_lines.append(f"\nWrong incident/date: {len(wrong_incident) + len(wrong_date)}")
    for src in (wrong_incident + wrong_date)[:10]:
        output_lines.append(f"  {src['entry_id']}: {src['source_name']}")
        output_lines.append(f"    Reason: {src['reason'][:100]}")

    # SECTION 5: Shooting entries analysis
    output_lines.append("\n" + "=" * 80)
    output_lines.append("SECTION 5: SHOOTING ENTRIES (T2-S-xxx) ANALYSIS")
    output_lines.append("Many shooting entries only have generic NBC overview - need incident-specific sources")
    output_lines.append("=" * 80)

    shooting_entries = [r for r in failed_no_sources if r["entry_id"].startswith("T2-S-")]
    output_lines.append(f"\nShooting entries with no valid source: {len(shooting_entries)}")

    for result in shooting_entries:
        entry_id = result["entry_id"]
        entry = all_entries.get(entry_id, {})
        output_lines.append(f"\n  {entry_id}: {entry.get('victim_name', 'Unknown victim')}")
        output_lines.append(f"    Date: {entry.get('date')}, Location: {entry.get('city')}, {entry.get('state')}")
        # Check for non-archived URLs that might help
        for src in entry.get("sources", []):
            if not src.get("archive_path"):
                output_lines.append(f"    Non-archived source: {src.get('url', 'no url')[:70]}")

    # Write report
    report_text = "\n".join(output_lines)
    output_path = base_path / "data" / "sources" / "verification_analysis.txt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text)
    print(f"\n\nReport saved to: {output_path}")

    # Also create a JSON summary for programmatic use
    summary = {
        "stats": {
            "total": len(report["results"]),
            "passed": len(passed),
            "failed_no_sources": len(failed_no_sources),
            "failed_partial": len(failed_partial),
            "errors": len(errors_parse) + len(errors_api) + len(errors_no_sources),
            "unrelated_sources": len(report.get("unrelated_sources", []))
        },
        "entries_needing_new_sources": [r["entry_id"] for r in failed_no_sources],
        "entries_with_partial_issues": [{"id": r["entry_id"], "score": r.get("score", 0), "issues": r.get("issues", [])} for r in failed_partial],
        "entries_needing_reverification": [r["entry_id"] for r in errors_parse + errors_api],
        "entries_without_sources": [r["entry_id"] for r in errors_no_sources],
        "unrelated_sources": report.get("unrelated_sources", [])
    }

    summary_path = base_path / "data" / "sources" / "verification_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"Summary saved to: {summary_path}")

if __name__ == "__main__":
    main()
