#!/usr/bin/env python3
"""
Populate Canonical IDs for Cross-Tier Deduplication
====================================================

One-time migration script to:
1. Group incidents by related_incidents links
2. Generate canonical_incident_id for each group
3. Mark highest-tier record as is_primary_record=True
4. Update all incident JSON files
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ice_arrests.data.loader import (
    load_incidents,
    generate_canonical_id,
    _INCIDENTS_DIR,
)


def find_connected_groups(incidents: list) -> list:
    """
    Find groups of incidents connected via related_incidents.

    Uses union-find to group all transitively connected incidents.

    Returns:
        List of groups, where each group is a list of incident IDs.
    """
    # Build adjacency from related_incidents
    id_to_incident = {i['id']: i for i in incidents}

    # Union-find data structure
    parent = {}

    def find(x):
        if x not in parent:
            parent[x] = x
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    # Initialize all incidents
    for inc in incidents:
        find(inc['id'])

    # Union related incidents
    for inc in incidents:
        inc_id = inc['id']
        for related_id in inc.get('related_incidents', []):
            if related_id in id_to_incident:
                union(inc_id, related_id)

    # Group by root
    groups = defaultdict(list)
    for inc in incidents:
        root = find(inc['id'])
        groups[root].append(inc['id'])

    return list(groups.values())


def select_primary_record(incident_ids: list, id_to_incident: dict) -> str:
    """
    Select the primary record from a group of related incidents.

    Priority:
    1. Lowest tier number (Tier 1 > Tier 2 > etc.)
    2. If tie, prefer the first ID alphabetically

    Returns:
        The ID of the primary record.
    """
    incidents = [id_to_incident[inc_id] for inc_id in incident_ids]

    # Sort by tier (ascending), then by ID
    incidents.sort(key=lambda x: (x.get('source_tier', 4), x['id']))

    return incidents[0]['id']


def generate_group_canonical_id(incident_ids: list, id_to_incident: dict) -> str:
    """
    Generate a canonical ID for a group of related incidents.

    Uses the primary (highest tier) incident's data.
    """
    primary_id = select_primary_record(incident_ids, id_to_incident)
    primary_incident = id_to_incident[primary_id]
    return generate_canonical_id(primary_incident)


def load_json_file(filepath: Path) -> list:
    """Load a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(filepath: Path, data: list):
    """Save data to a JSON file with pretty printing."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    """Main migration function."""
    print("=" * 60)
    print("Populate Canonical IDs for Cross-Tier Deduplication")
    print("=" * 60)

    # Load all incidents
    all_incidents = load_incidents()
    id_to_incident = {i['id']: i for i in all_incidents}

    print(f"\nLoaded {len(all_incidents)} total incidents")

    # Find connected groups
    groups = find_connected_groups(all_incidents)

    # Separate single-incident groups from multi-incident groups
    single_groups = [g for g in groups if len(g) == 1]
    multi_groups = [g for g in groups if len(g) > 1]

    print(f"Found {len(single_groups)} unique incidents (no duplicates)")
    print(f"Found {len(multi_groups)} groups of related incidents:")

    for group in multi_groups:
        print(f"  - {group}")

    # Generate canonical IDs and determine primary records
    canonical_assignments = {}  # incident_id -> (canonical_id, is_primary)

    for group in groups:
        if len(group) == 1:
            # Single incident - it's its own canonical
            inc_id = group[0]
            canonical_id = generate_canonical_id(id_to_incident[inc_id])
            canonical_assignments[inc_id] = (canonical_id, True)
        else:
            # Multi-incident group
            canonical_id = generate_group_canonical_id(group, id_to_incident)
            primary_id = select_primary_record(group, id_to_incident)

            for inc_id in group:
                is_primary = (inc_id == primary_id)
                canonical_assignments[inc_id] = (canonical_id, is_primary)

    print(f"\nGenerated canonical IDs for {len(canonical_assignments)} incidents")

    # Update JSON files
    tier_files = {
        1: ["tier1_deaths_in_custody.json"],
        2: ["tier2_shootings.json", "tier2_less_lethal.json"],
        3: ["tier3_incidents.json"],
        4: ["tier4_incidents.json"],
    }

    updated_count = 0

    for tier, filenames in tier_files.items():
        for filename in filenames:
            filepath = _INCIDENTS_DIR / filename
            if not filepath.exists():
                print(f"  Skipping {filename} (not found)")
                continue

            incidents = load_json_file(filepath)
            modified = False

            for incident in incidents:
                inc_id = incident['id']
                if inc_id in canonical_assignments:
                    canonical_id, is_primary = canonical_assignments[inc_id]

                    # Only update if changed
                    if (incident.get('canonical_incident_id') != canonical_id or
                        incident.get('is_primary_record', True) != is_primary):
                        incident['canonical_incident_id'] = canonical_id
                        incident['is_primary_record'] = is_primary
                        modified = True
                        updated_count += 1

            if modified:
                save_json_file(filepath, incidents)
                print(f"  Updated {filename}")

    print(f"\nUpdated {updated_count} incident records")

    # Print summary of duplicates
    print("\n" + "=" * 60)
    print("Cross-Tier Duplicate Summary")
    print("=" * 60)

    for group in multi_groups:
        canonical_id, _ = canonical_assignments[group[0]]
        primary_id = select_primary_record(group, id_to_incident)

        print(f"\nCanonical ID: {canonical_id}")
        print(f"  Primary: {primary_id}")
        print(f"  Duplicates: {[i for i in group if i != primary_id]}")

        # Show details
        for inc_id in group:
            inc = id_to_incident[inc_id]
            tier = inc.get('source_tier', '?')
            name = inc.get('victim_name', 'Unknown')
            is_primary = inc_id == primary_id
            marker = " (PRIMARY)" if is_primary else ""
            print(f"    - {inc_id} [Tier {tier}] {name}{marker}")

    print("\n" + "=" * 60)
    print("Migration complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
