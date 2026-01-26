#!/usr/bin/env python3
"""
Validate Deduplication Setup
============================

Validation script to check:
1. All related_incidents entries exist
2. Links are bidirectional
3. Each canonical group has exactly one primary record
4. No orphan references
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ice_arrests.data.loader import (
    load_incidents,
    validate_related_incidents,
    get_canonical_groups,
)


def validate_primary_records() -> list:
    """
    Validate that each canonical_incident_id has exactly one primary record.

    Returns:
        List of error dictionaries.
    """
    groups = get_canonical_groups()
    errors = []

    for canonical_id, incidents in groups.items():
        primaries = [i for i in incidents if i.get('is_primary_record', True)]
        non_primaries = [i for i in incidents if not i.get('is_primary_record', True)]

        if len(incidents) > 1:
            # Multi-incident group - should have exactly one primary
            if len(primaries) == 0:
                errors.append({
                    'canonical_id': canonical_id,
                    'error_type': 'no_primary',
                    'details': f"No primary record in group: {[i['id'] for i in incidents]}"
                })
            elif len(primaries) > 1:
                errors.append({
                    'canonical_id': canonical_id,
                    'error_type': 'multiple_primaries',
                    'details': f"Multiple primary records: {[i['id'] for i in primaries]}"
                })

    return errors


def validate_canonical_consistency() -> list:
    """
    Validate that related incidents share the same canonical_incident_id.

    Returns:
        List of error dictionaries.
    """
    all_incidents = load_incidents()
    id_to_incident = {i['id']: i for i in all_incidents}
    errors = []

    for incident in all_incidents:
        canonical_id = incident.get('canonical_incident_id')
        if not canonical_id:
            continue

        for related_id in incident.get('related_incidents', []):
            if related_id not in id_to_incident:
                continue

            related_incident = id_to_incident[related_id]
            related_canonical = related_incident.get('canonical_incident_id')

            if related_canonical and related_canonical != canonical_id:
                errors.append({
                    'incident_id': incident['id'],
                    'error_type': 'canonical_mismatch',
                    'details': (
                        f"Incident has canonical_id '{canonical_id}' but "
                        f"related incident '{related_id}' has '{related_canonical}'"
                    )
                })

    return errors


def check_deduplication_counts():
    """
    Compare counts with and without deduplication to verify effectiveness.
    """
    all_incidents = load_incidents()

    # Count by canonical_incident_id
    canonical_ids = set()
    for incident in all_incidents:
        canonical_id = incident.get('canonical_incident_id', incident['id'])
        canonical_ids.add(canonical_id)

    # Count primary records only
    primary_count = sum(1 for i in all_incidents if i.get('is_primary_record', True))

    return {
        'total_records': len(all_incidents),
        'unique_canonical_ids': len(canonical_ids),
        'primary_records': primary_count,
        'duplicates_removed': len(all_incidents) - primary_count,
    }


def main():
    """Main validation function."""
    print("=" * 60)
    print("Validate Deduplication Setup")
    print("=" * 60)

    all_errors = []
    all_warnings = []

    # 1. Validate related_incidents links
    print("\n[1/4] Validating related_incidents links...")
    related_errors = validate_related_incidents()
    if related_errors:
        for err in related_errors:
            if err['error_type'] == 'not_bidirectional':
                all_warnings.append(err)
            else:
                all_errors.append(err)
        print(f"  Found {len([e for e in related_errors if e['error_type'] != 'not_bidirectional'])} errors")
        print(f"  Found {len([e for e in related_errors if e['error_type'] == 'not_bidirectional'])} warnings (non-bidirectional)")
    else:
        print("  All related_incidents links valid")

    # 2. Validate primary records
    print("\n[2/4] Validating primary records...")
    primary_errors = validate_primary_records()
    all_errors.extend(primary_errors)
    if primary_errors:
        print(f"  Found {len(primary_errors)} errors")
    else:
        print("  All canonical groups have exactly one primary record")

    # 3. Validate canonical ID consistency
    print("\n[3/4] Validating canonical ID consistency...")
    canonical_errors = validate_canonical_consistency()
    all_errors.extend(canonical_errors)
    if canonical_errors:
        print(f"  Found {len(canonical_errors)} errors")
    else:
        print("  All related incidents share consistent canonical IDs")

    # 4. Check deduplication counts
    print("\n[4/4] Checking deduplication effectiveness...")
    counts = check_deduplication_counts()
    print(f"  Total records: {counts['total_records']}")
    print(f"  Unique incidents (canonical IDs): {counts['unique_canonical_ids']}")
    print(f"  Primary records: {counts['primary_records']}")
    print(f"  Duplicates marked: {counts['duplicates_removed']}")

    # Print errors
    if all_errors:
        print("\n" + "=" * 60)
        print(f"ERRORS ({len(all_errors)} found)")
        print("=" * 60)
        for err in all_errors:
            print(f"\n  [{err.get('error_type', 'unknown')}]")
            if 'incident_id' in err:
                print(f"    Incident: {err['incident_id']}")
            if 'canonical_id' in err:
                print(f"    Canonical: {err['canonical_id']}")
            print(f"    Details: {err['details']}")

    # Print warnings
    if all_warnings:
        print("\n" + "=" * 60)
        print(f"WARNINGS ({len(all_warnings)} found)")
        print("=" * 60)
        for warn in all_warnings:
            print(f"  [{warn.get('error_type', 'unknown')}] {warn.get('incident_id', '')}: {warn['details']}")

    # Summary
    print("\n" + "=" * 60)
    if all_errors:
        print(f"VALIDATION FAILED - {len(all_errors)} errors found")
        sys.exit(1)
    elif all_warnings:
        print(f"VALIDATION PASSED with {len(all_warnings)} warnings")
        sys.exit(0)
    else:
        print("VALIDATION PASSED - All checks successful")
        sys.exit(0)


if __name__ == "__main__":
    main()
