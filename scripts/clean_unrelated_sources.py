#!/usr/bin/env python3
"""Remove unrelated sources from entries that passed verification."""

import json
from pathlib import Path

def main():
    base_path = Path(__file__).parent.parent

    # Load verification report
    with open(base_path / 'data' / 'sources' / 'llm_verification_report.json', 'r', encoding='utf-8') as f:
        report = json.load(f)

    # Map verification results
    results_by_entry = {r['entry_id']: r for r in report.get('results', [])}

    # Get unrelated sources grouped by entry
    unrelated_by_entry = {}
    for src in report.get('unrelated_sources', []):
        entry_id = src['entry_id']
        if entry_id not in unrelated_by_entry:
            unrelated_by_entry[entry_id] = set()
        unrelated_by_entry[entry_id].add(src['source_name'])

    # Only remove from entries that PASSED
    entries_to_clean = []
    for entry_id, unrelated_names in unrelated_by_entry.items():
        result = results_by_entry.get(entry_id, {})
        if result.get('passed'):
            entries_to_clean.append((entry_id, unrelated_names))

    print(f"Cleaning unrelated sources from {len(entries_to_clean)} entries that passed verification")
    print()

    # Load and update all incident files
    incidents_path = base_path / 'data' / 'incidents'
    modified_files = {}

    for json_file in incidents_path.glob('tier*.json'):
        if 'backup' in str(json_file):
            continue

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        file_modified = False

        for entry in data:
            entry_id = entry['id']
            if entry_id not in dict(entries_to_clean):
                continue

            unrelated_names = dict(entries_to_clean)[entry_id]
            original_count = len(entry.get('sources', []))

            # Keep only sources NOT in unrelated list
            new_sources = []
            removed = []
            for src in entry.get('sources', []):
                src_name = src.get('name', '')
                # Check if matches any unrelated source name
                is_unrelated = any(
                    unrel in src_name or src_name in unrel
                    for unrel in unrelated_names
                )
                if is_unrelated:
                    removed.append(src_name)
                else:
                    new_sources.append(src)

            if removed:
                entry['sources'] = new_sources
                file_modified = True
                print(f"{entry_id}: Removed {len(removed)} source(s): {removed}")

        if file_modified:
            modified_files[json_file] = data

    # Save modified files
    for json_file, data in modified_files.items():
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"\nSaved {json_file.name}")

    print(f"\n{len(modified_files)} file(s) updated")

if __name__ == '__main__':
    main()
