#!/usr/bin/env python3
"""Fix incident_scale mismatches where affected_count doesn't match scale."""

import json
from pathlib import Path

def get_correct_scale(count):
    """Calculate correct scale based on affected_count."""
    if count is None or count <= 1:
        return "single"
    elif count <= 5:
        return "small"
    elif count <= 50:
        return "medium"
    elif count <= 200:
        return "large"
    else:
        return "mass"

def fix_file(filepath: Path) -> int:
    """Fix scale mismatches in a single file. Returns count of fixes."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle different file structures
    if isinstance(data, list):
        incidents = data
        is_list = True
    elif 'incidents' in data:
        incidents = data['incidents']
        is_list = False
        key = 'incidents'
    elif 'deaths' in data:
        incidents = data['deaths']
        is_list = False
        key = 'deaths'
    elif 'shootings' in data:
        incidents = data['shootings']
        is_list = False
        key = 'shootings'
    elif 'less_lethal_incidents' in data:
        incidents = data['less_lethal_incidents']
        is_list = False
        key = 'less_lethal_incidents'
    else:
        print(f"  Unknown structure in {filepath.name}")
        return 0

    fixed_count = 0
    for inc in incidents:
        count = inc.get('affected_count')
        current_scale = inc.get('incident_scale')
        expected_scale = get_correct_scale(count)

        if current_scale and current_scale != expected_scale:
            print(f"  {inc['id']}: count={count}, '{current_scale}' -> '{expected_scale}'")
            inc['incident_scale'] = expected_scale
            fixed_count += 1

    if fixed_count > 0:
        if is_list:
            output_data = incidents
        else:
            data[key] = incidents
            output_data = data

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"  Saved {fixed_count} fixes to {filepath.name}")

    return fixed_count

def main():
    data_dir = Path(__file__).parent.parent / 'data' / 'incidents'

    print("=== Fixing incident_scale mismatches ===\n")

    total_fixed = 0
    for filepath in sorted(data_dir.glob('tier*.json')):
        print(f"Processing {filepath.name}...")
        fixed = fix_file(filepath)
        total_fixed += fixed
        if fixed == 0:
            print("  No mismatches found")
        print()

    print(f"Total fixed: {total_fixed}")
    return total_fixed

if __name__ == "__main__":
    main()
