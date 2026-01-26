#!/usr/bin/env python3
"""
Validate schema consistency across all incident JSON files.
Run this after adding new incidents to ensure data quality.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "data" / "incidents"

# Required fields for all records
REQUIRED_FIELDS = [
    "id",
    "date",
    "state",
    "incident_type",
    "source_tier",
    "verified",
    "affected_count",
    "incident_scale",
    "outcome",
    "outcome_detail",
    "outcome_category",
    "victim_category",
    "date_precision",
]

# Valid values for enum fields
VALID_INCIDENT_TYPES = {
    "death_in_custody", "shooting_by_agent", "shooting_at_agent",
    "less_lethal", "physical_force", "wrongful_detention",
    "wrongful_deportation", "mass_raid", "protest"
}

VALID_VICTIM_CATEGORIES = {
    "detainee", "enforcement_target", "protester", "journalist",
    "bystander", "us_citizen_collateral", "officer", "multiple"
}

VALID_INCIDENT_SCALES = {"single", "small", "medium", "large", "mass"}

VALID_DATE_PRECISIONS = {"day", "month", "year"}

VALID_OUTCOME_CATEGORIES = {
    "death", "serious_injury", "injury", "no_injury", "none",
    "arrest", "arrested", "detained", "released", "deported", "multiple"
}


def validate_date(date_str):
    """Validate date format YYYY-MM-DD with no 00 placeholders."""
    if not date_str:
        return "missing date"

    match = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", date_str)
    if not match:
        return f"invalid date format: {date_str}"

    year, month, day = match.groups()
    if month == "00" or day == "00":
        return f"date has 00 placeholder: {date_str}"

    # Basic range validation
    if not (1 <= int(month) <= 12):
        return f"invalid month: {date_str}"
    if not (1 <= int(day) <= 31):
        return f"invalid day: {date_str}"

    return None


def validate_affected_count(record):
    """Validate affected_count matches incident_scale."""
    count = record.get("affected_count")
    scale = record.get("incident_scale")

    if count is None:
        return "missing affected_count"

    if scale is None:
        return "missing incident_scale"

    # Check consistency
    expected_scale = None
    if count <= 1:
        expected_scale = "single"
    elif count <= 5:
        expected_scale = "small"
    elif count <= 50:
        expected_scale = "medium"
    elif count <= 200:
        expected_scale = "large"
    else:
        expected_scale = "mass"

    if scale != expected_scale:
        return f"incident_scale mismatch: count={count} but scale={scale} (expected {expected_scale})"

    return None


def validate_record(record, file_name):
    """Validate a single record and return list of issues."""
    issues = []
    record_id = record.get("id", "UNKNOWN")

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in record:
            issues.append(f"missing required field: {field}")

    # Validate date
    date_issue = validate_date(record.get("date"))
    if date_issue:
        issues.append(date_issue)

    # Validate enum values
    incident_type = record.get("incident_type")
    if incident_type and incident_type not in VALID_INCIDENT_TYPES:
        issues.append(f"unknown incident_type: {incident_type}")

    victim_category = record.get("victim_category")
    if victim_category and victim_category not in VALID_VICTIM_CATEGORIES:
        issues.append(f"unknown victim_category: {victim_category}")

    incident_scale = record.get("incident_scale")
    if incident_scale and incident_scale not in VALID_INCIDENT_SCALES:
        issues.append(f"unknown incident_scale: {incident_scale}")

    date_precision = record.get("date_precision")
    if date_precision and date_precision not in VALID_DATE_PRECISIONS:
        issues.append(f"unknown date_precision: {date_precision}")

    outcome_category = record.get("outcome_category")
    if outcome_category and outcome_category not in VALID_OUTCOME_CATEGORIES:
        issues.append(f"unknown outcome_category: {outcome_category}")

    # Validate affected_count vs incident_scale
    count_issue = validate_affected_count(record)
    if count_issue:
        issues.append(count_issue)

    # Check for plural victim_name with affected_count=1
    victim_name = record.get("victim_name", "")
    affected_count = record.get("affected_count", 1)
    if affected_count == 1 and victim_name:
        plural_indicators = ["Multiple", "Bystanders", "protesters", "officers", "citizens"]
        for indicator in plural_indicators:
            if indicator in victim_name and "N/A" not in victim_name:
                issues.append(f"affected_count=1 but victim_name suggests plural: '{victim_name}'")
                break

    return record_id, issues


def validate_file(file_path):
    """Validate all records in a JSON file."""
    print(f"\nValidating: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        records = json.load(f)

    all_issues = {}

    for record in records:
        record_id, issues = validate_record(record, file_path.name)
        if issues:
            all_issues[record_id] = issues

    if all_issues:
        print(f"  ISSUES FOUND: {len(all_issues)} records with problems")
        for record_id, issues in all_issues.items():
            print(f"  {record_id}:")
            for issue in issues:
                print(f"    - {issue}")
    else:
        print(f"  OK: All {len(records)} records valid")

    return all_issues


def get_field_coverage(file_path):
    """Get coverage stats for optional fields."""
    with open(file_path, 'r', encoding='utf-8') as f:
        records = json.load(f)

    field_counts = defaultdict(int)
    for record in records:
        for field in record.keys():
            field_counts[field] += 1

    return field_counts, len(records)


def main():
    """Main validation function."""
    print("=" * 60)
    print("Schema Validation Report")
    print("=" * 60)

    json_files = list(DATA_DIR.glob("tier*.json"))

    if not json_files:
        print(f"No JSON files found in {DATA_DIR}")
        return 1

    total_issues = 0
    for file_path in sorted(json_files):
        issues = validate_file(file_path)
        total_issues += len(issues)

    print("\n" + "=" * 60)
    if total_issues == 0:
        print("VALIDATION PASSED: All records are valid")
        return 0
    else:
        print(f"VALIDATION FAILED: {total_issues} records have issues")
        return 1


if __name__ == "__main__":
    exit(main())
