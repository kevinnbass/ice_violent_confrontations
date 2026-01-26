#!/usr/bin/env python3
"""Link identified cross-tier duplicate incidents."""

import json
from pathlib import Path

def load_incidents(data_dir: Path) -> dict:
    """Load all incidents into a dict by ID."""
    all_incidents = {}
    file_map = {}  # id -> filepath

    for filepath in sorted(data_dir.glob('tier*.json')):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            incidents = data
            key = None
        elif 'incidents' in data:
            incidents = data['incidents']
            key = 'incidents'
        elif 'deaths' in data:
            incidents = data['deaths']
            key = 'deaths'
        elif 'shootings' in data:
            incidents = data['shootings']
            key = 'shootings'
        elif 'less_lethal_incidents' in data:
            incidents = data['less_lethal_incidents']
            key = 'less_lethal_incidents'
        else:
            continue

        for inc in incidents:
            all_incidents[inc['id']] = inc
            file_map[inc['id']] = (filepath, key)

    return all_incidents, file_map

def add_cross_reference(incident: dict, related_id: str, is_primary: bool = False):
    """Add cross-reference to an incident."""
    if 'related_incidents' not in incident:
        incident['related_incidents'] = []

    if related_id not in incident['related_incidents']:
        incident['related_incidents'].append(related_id)

    if not is_primary and 'superseded_by' not in incident:
        incident['superseded_by'] = related_id

def save_file(filepath: Path, key: str, incidents: list, data: dict = None):
    """Save incidents back to file."""
    if key is None:
        output = incidents
    else:
        if data is None:
            data = {}
        data[key] = incidents
        output = data

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

def main():
    data_dir = Path(__file__).parent.parent / 'data' / 'incidents'

    # Known duplicates to link: (primary_id, secondary_ids[])
    # Primary ID is typically the higher-tier source (T1 > T2 > T3 > T4)
    duplicates = [
        # Jaime Alanis Garcia - same person
        ("T1-D-053", ["T4-003"]),
        # Abelardo Avellaneda-Delgado - same person, different spelling
        ("T1-D-008", ["T1-D-044"]),
        # Keith Porter - same incident
        ("T1-S-006", ["T2-S-014"]),
        # Josue Castro Rivera - same person with encoding issue
        ("T1-D-052", ["T4-046"]),
        # Chanthila Souvannarath - already partially linked, verify
        ("T2-WD-022", ["T4-002"]),
        # Romeo and siblings - same incident
        ("T2-WD-021", ["T4-075"]),
    ]

    # Load all incidents
    all_incidents, file_map = load_incidents(data_dir)
    print(f"Loaded {len(all_incidents)} incidents\n")

    # Track modified files
    modified_files = set()
    linked_count = 0

    for primary_id, secondary_ids in duplicates:
        if primary_id not in all_incidents:
            print(f"WARNING: Primary ID {primary_id} not found")
            continue

        primary = all_incidents[primary_id]
        primary_name = primary.get('name', primary.get('victim_name', 'Unknown'))
        print(f"Linking: {primary_id} ({primary_name})")

        for sec_id in secondary_ids:
            if sec_id not in all_incidents:
                print(f"  WARNING: Secondary ID {sec_id} not found")
                continue

            secondary = all_incidents[sec_id]
            sec_name = secondary.get('name', secondary.get('victim_name', 'Unknown'))

            # Check if already linked
            existing_related = primary.get('related_incidents', [])
            if sec_id in existing_related:
                print(f"  Already linked: {sec_id} ({sec_name})")
                continue

            # Add cross-references
            add_cross_reference(primary, sec_id, is_primary=True)
            add_cross_reference(secondary, primary_id, is_primary=False)

            modified_files.add(file_map[primary_id][0])
            modified_files.add(file_map[sec_id][0])
            linked_count += 1
            print(f"  Linked: {sec_id} ({sec_name}) -> superseded_by {primary_id}")

    # Save modified files
    print(f"\nSaving {len(modified_files)} modified files...")

    for filepath in modified_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            incidents = data
            key = None
        elif 'incidents' in data:
            incidents = data['incidents']
            key = 'incidents'
        elif 'deaths' in data:
            incidents = data['deaths']
            key = 'deaths'
        elif 'shootings' in data:
            incidents = data['shootings']
            key = 'shootings'
        elif 'less_lethal_incidents' in data:
            incidents = data['less_lethal_incidents']
            key = 'less_lethal_incidents'
        else:
            continue

        # Update incidents from our modified dict
        for i, inc in enumerate(incidents):
            if inc['id'] in all_incidents:
                incidents[i] = all_incidents[inc['id']]

        save_file(filepath, key, incidents, data if key else None)
        print(f"  Saved: {filepath.name}")

    print(f"\nTotal links added: {linked_count}")

if __name__ == "__main__":
    main()
