#!/usr/bin/env python3
"""
Restore corrected entries from corrected_entries.json to the main tier files.
"""

import json
from pathlib import Path

def main():
    base_dir = Path(__file__).parent.parent
    corrections_file = base_dir / "data" / "sources" / "corrected_entries.json"

    # Load corrections
    with open(corrections_file, 'r', encoding='utf-8') as f:
        corrections = json.load(f)

    # Map entry ID prefixes to tier files
    tier_mapping = {
        "T1-": "tier1_deaths_in_custody.json",
        "T2-S": "tier2_shootings.json",
        "T2-SA": "tier2_shootings.json",
        "T2-LL": "tier2_less_lethal.json",
        "T2-WD": "tier2_less_lethal.json",
        "T3-": "tier3_incidents.json",
        "T4-": "tier4_incidents.json",
    }

    # Group corrected entries by tier file
    entries_by_file = {}
    for entry_data in corrections["corrected_entries"]:
        entry_id = entry_data["original_id"]
        corrected = entry_data["corrected_entry"]

        # Determine target file
        target_file = None
        for prefix, filename in sorted(tier_mapping.items(), key=lambda x: -len(x[0])):
            if entry_id.startswith(prefix):
                target_file = filename
                break

        if target_file:
            if target_file not in entries_by_file:
                entries_by_file[target_file] = []
            entries_by_file[target_file].append({
                "id": entry_id,
                "entry": corrected,
                "correction_notes": entry_data.get("correction_notes", ""),
                "original_claimed": entry_data.get("original_claimed", {})
            })

    # Process each tier file
    incidents_dir = base_dir / "data" / "incidents"

    for filename, entries_to_add in entries_by_file.items():
        filepath = incidents_dir / filename

        if not filepath.exists():
            print(f"WARNING: {filepath} does not exist, skipping")
            continue

        # Load existing entries
        with open(filepath, 'r', encoding='utf-8') as f:
            existing = json.load(f)

        existing_ids = {e["id"] for e in existing}

        added_count = 0
        for item in entries_to_add:
            entry_id = item["id"]
            corrected = item["entry"]

            if entry_id in existing_ids:
                # Update existing entry
                for i, e in enumerate(existing):
                    if e["id"] == entry_id:
                        # Preserve some original fields, update others
                        existing[i].update({
                            "date": corrected.get("date", e.get("date")),
                            "state": corrected.get("state", e.get("state")),
                            "city": corrected.get("city", e.get("city")),
                            "incident_type": corrected.get("incident_type", e.get("incident_type")),
                            "outcome": corrected.get("outcome", e.get("outcome")),
                            "source_url": corrected.get("source_url", e.get("source_url")),
                            "source_name": corrected.get("source_name", e.get("source_name")),
                            "verified": True,
                            "correction_applied": True,
                            "correction_notes": item["correction_notes"],
                        })
                        if "victim_name" in corrected:
                            existing[i]["victim_name"] = corrected["victim_name"]
                        if "victim_age" in corrected:
                            existing[i]["victim_age"] = corrected["victim_age"]
                        if "victim_count" in corrected:
                            existing[i]["victim_count"] = corrected["victim_count"]
                        if "verification_sources" in corrected:
                            existing[i]["verification_sources"] = corrected["verification_sources"]
                        print(f"UPDATED: {entry_id} in {filename}")
                        added_count += 1
                        break
            else:
                # Add new entry
                new_entry = {
                    "id": entry_id,
                    "date": corrected.get("date", ""),
                    "state": corrected.get("state", ""),
                    "city": corrected.get("city", ""),
                    "incident_type": corrected.get("incident_type", ""),
                    "outcome": corrected.get("outcome", ""),
                    "source_url": corrected.get("source_url", ""),
                    "source_name": corrected.get("source_name", ""),
                    "source_tier": int(entry_id[1]) if entry_id[1].isdigit() else 4,
                    "verified": True,
                    "correction_applied": True,
                    "correction_notes": item["correction_notes"],
                    "collection_method": "verified_correction",
                }

                if "victim_name" in corrected:
                    new_entry["victim_name"] = corrected["victim_name"]
                if "victim_age" in corrected:
                    new_entry["victim_age"] = corrected["victim_age"]
                if "victim_count" in corrected:
                    new_entry["victim_count"] = corrected["victim_count"]
                if "victim_nationality" in corrected:
                    new_entry["victim_nationality"] = corrected["victim_nationality"]
                if "us_citizen" in corrected:
                    new_entry["us_citizen"] = corrected["us_citizen"]
                if "verification_sources" in corrected:
                    new_entry["verification_sources"] = corrected["verification_sources"]
                if "alternative_case" in corrected:
                    new_entry["alternative_case"] = corrected["alternative_case"]

                existing.append(new_entry)
                print(f"ADDED: {entry_id} to {filename}")
                added_count += 1

        # Sort by ID
        existing.sort(key=lambda x: x["id"])

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        print(f"  -> Saved {filename} with {added_count} corrections")

    # Summary
    print("\n" + "="*60)
    print("RESTORATION SUMMARY")
    print("="*60)
    print(f"Total corrected entries: {len(corrections['corrected_entries'])}")
    print(f"Confirmed fabricated (to delete): {len(corrections['confirmed_fabricated'])}")
    print("\nFabricated IDs to remove from archive:")
    for fab in corrections["confirmed_fabricated"]:
        print(f"  - {fab['id']}: {fab['reason'][:60]}...")

if __name__ == "__main__":
    main()
