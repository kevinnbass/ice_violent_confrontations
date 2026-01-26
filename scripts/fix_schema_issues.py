#!/usr/bin/env python3
"""
Fix schema inconsistencies across all incident JSON files.

Issues fixed:
1. Date placeholders (00) converted to valid dates with date_precision field added
2. Missing required fields added with appropriate defaults
3. Standardize field values across files
"""

import json
import os
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "incidents"

# Required fields for all incident records
REQUIRED_FIELDS = {
    "id": None,
    "date": None,
    "state": None,
    "incident_type": None,
    "source_tier": None,
    "verified": True,
    "affected_count": 1,
    "incident_scale": "single",
    "outcome": None,
    "outcome_detail": None,
    "outcome_category": None,
    "victim_category": None,
}


def fix_date_placeholder(date_str):
    """
    Fix date placeholders like 2025-00-00 or 2025-09-00.
    Returns (fixed_date, date_precision).
    """
    if not date_str or not isinstance(date_str, str):
        return date_str, None

    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", date_str)
    if not match:
        return date_str, None

    year, month, day = match.groups()

    if month == "00" and day == "00":
        # Unknown month and day - use mid-year
        return f"{year}-06-15", "year"
    elif day == "00":
        # Unknown day - use 15th of month (middle)
        return f"{year}-{month}-15", "month"
    else:
        return date_str, "day"


def get_incident_scale(affected_count):
    """Determine incident_scale based on affected_count."""
    if affected_count is None or affected_count <= 1:
        return "single"
    elif affected_count <= 5:
        return "small"
    elif affected_count <= 50:
        return "medium"
    elif affected_count <= 200:
        return "large"
    else:
        return "mass"


def infer_outcome_category(record):
    """Infer outcome_category from other fields."""
    outcome = (record.get("outcome") or "").lower()
    incident_type = record.get("incident_type", "")

    if "death" in outcome or incident_type == "death_in_custody":
        return "death"
    elif "arrest" in outcome:
        return "arrest"
    elif "detained" in outcome:
        return "detained"
    elif "released" in outcome:
        return "released"
    elif any(x in outcome for x in ["injury", "injuries", "injured", "wound", "burns", "concussion"]):
        return "injury"
    elif "no" in outcome and any(x in outcome for x in ["injury", "injuries", "force"]):
        return "none"
    elif "peaceful" in outcome:
        return "none"
    else:
        return "injury"  # default


def fix_record(record, file_name):
    """Fix a single record and return the fixed version."""
    fixed = record.copy()
    changes = []

    # Fix date placeholder and ensure date_precision exists
    if "date" in fixed:
        orig_date = fixed["date"]
        new_date, precision = fix_date_placeholder(orig_date)
        if new_date != orig_date:
            fixed["date"] = new_date
            fixed["date_precision"] = precision
            changes.append(f"date: {orig_date} -> {new_date} (precision: {precision})")
        elif "date_precision" not in fixed:
            # Add date_precision for valid dates
            if precision:
                fixed["date_precision"] = precision
            else:
                fixed["date_precision"] = "day"
            changes.append(f"added date_precision: {fixed['date_precision']}")

    # Ensure affected_count is present and matches incident_scale
    affected_count = fixed.get("affected_count", 1)
    expected_scale = get_incident_scale(affected_count)
    if fixed.get("incident_scale") != expected_scale:
        if "incident_scale" not in fixed:
            fixed["incident_scale"] = expected_scale
            changes.append(f"added incident_scale: {expected_scale}")

    # Ensure outcome_detail is present
    if "outcome_detail" not in fixed and "outcome" in fixed:
        fixed["outcome_detail"] = fixed["outcome"]
        changes.append(f"added outcome_detail from outcome")

    # Ensure outcome_category is present
    if "outcome_category" not in fixed:
        fixed["outcome_category"] = infer_outcome_category(fixed)
        changes.append(f"added outcome_category: {fixed['outcome_category']}")

    # Ensure victim_category is present
    if "victim_category" not in fixed:
        # Try to infer from incident_type
        incident_type = fixed.get("incident_type", "")
        if incident_type == "death_in_custody":
            fixed["victim_category"] = "detainee"
        elif fixed.get("protest_related"):
            fixed["victim_category"] = "protester"
        elif "wrongful" in incident_type:
            fixed["victim_category"] = "us_citizen_collateral"
        else:
            fixed["victim_category"] = "enforcement_target"
        changes.append(f"added victim_category: {fixed['victim_category']}")

    return fixed, changes


def process_file(file_path):
    """Process a single JSON file and fix all records."""
    print(f"\nProcessing: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        records = json.load(f)

    total_changes = 0
    fixed_records = []

    for record in records:
        fixed, changes = fix_record(record, file_path.name)
        fixed_records.append(fixed)
        if changes:
            total_changes += len(changes)
            print(f"  {record.get('id')}: {len(changes)} changes")
            for change in changes:
                print(f"    - {change}")

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(fixed_records, f, indent=2, ensure_ascii=False)

    print(f"  Total changes: {total_changes}")
    return total_changes


def main():
    """Main function to process all incident files."""
    print("=" * 60)
    print("Schema Standardization Script")
    print("=" * 60)

    json_files = list(DATA_DIR.glob("tier*.json"))

    if not json_files:
        print(f"No JSON files found in {DATA_DIR}")
        return

    total_all_changes = 0
    for file_path in sorted(json_files):
        changes = process_file(file_path)
        total_all_changes += changes

    print("\n" + "=" * 60)
    print(f"COMPLETE: {total_all_changes} total changes across {len(json_files)} files")
    print("=" * 60)


if __name__ == "__main__":
    main()
