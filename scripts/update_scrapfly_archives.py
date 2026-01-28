#!/usr/bin/env python3
"""Update JSON files to use Scrapfly archive paths."""

import json
from pathlib import Path

# Mapping of (entry_id, url_partial) -> new archive_path
SCRAPFLY_UPDATES = [
    # tier1_deaths_in_custody.json
    {
        "file": "tier1_deaths_in_custody.json",
        "entry_id": "T1-D-060",
        "url_contains": "newjerseymonitor.com/2025/12/19/ice-detainee-newark-jail-died",
        "new_archive_path": "data/sources/T1-D-060/article_4.txt"
    },
    # tier2_shootings.json
    {
        "file": "tier2_shootings.json",
        "entry_id": "T2-SA-010",
        "url_contains": "oregoncapitalchronicle.com/2026/01/12/pair-shot-by-u-s-border-patrol",
        "new_archive_path": "data/sources/T2-SA-010/article_4.txt"
    },
    # tier3_incidents.json
    {
        "file": "tier3_incidents.json",
        "entry_id": "T3-115",
        "url_contains": "ncronline.org/news/ice-agents-detain-migrants-church-grounds",
        "new_archive_path": "data/sources/T3-115/article_3.txt"
    },
    {
        "file": "tier3_incidents.json",
        "entry_id": "T3-116",
        "url_contains": "bringmethenews.com/minnesota-news/ice-detains-4-columbia-heights-students",
        "new_archive_path": "data/sources/T3-116/article_3.txt"
    },
    {
        "file": "tier3_incidents.json",
        "entry_id": "T3-122",
        "url_contains": "lailluminator.com/2025/10/21/ice-keeps-detaining-pregnant-immigrants",
        "new_archive_path": "data/sources/T3-122/article_2.txt"
    },
    {
        "file": "tier3_incidents.json",
        "entry_id": "T3-052",
        "url_contains": "newjerseymonitor.com/2025/05/09/newark-mayor-detained",
        "new_archive_path": "data/sources/T3-052/article_4.txt",
        "add_new_source": {
            "url": "https://newjerseymonitor.com/2025/05/09/newark-mayor-detained-by-federal-agents-during-protest-at-ice-jail/",
            "name": "New Jersey Monitor",
            "tier": 2,
            "archived": True,
            "archive_path": "data/sources/T3-052/article_4.txt"
        }
    },
    {
        "file": "tier3_incidents.json",
        "entry_id": "T3-P018",
        "url_contains": "axios.com/2025/06/10/ice-protests-la-nationwide",
        "new_archive_path": "data/sources/T3-P018/article_3.txt"
    },
    {
        "file": "tier3_incidents.json",
        "entry_id": "T3-P024",
        "url_contains": "wabe.org/buford-highway-plaza-fiesta",
        "new_archive_path": "data/sources/T3-P024/article_2.txt"
    },
    {
        "file": "tier3_incidents.json",
        "entry_id": "T3-P031",
        "url_contains": "bringmethenews.com/minnesota-news/residents-hit-with-tear-gas",
        "new_archive_path": "data/sources/T3-P031/article_1.txt"
    },
]

def update_json_files():
    base_path = Path(__file__).parent.parent / "data" / "incidents"

    # Group updates by file
    updates_by_file = {}
    for update in SCRAPFLY_UPDATES:
        file = update["file"]
        if file not in updates_by_file:
            updates_by_file[file] = []
        updates_by_file[file].append(update)

    for filename, updates in updates_by_file.items():
        filepath = base_path / filename
        print(f"\nProcessing {filename}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        update_count = 0
        for entry in data:
            entry_id = entry.get("id", "")

            for update in updates:
                if entry_id != update["entry_id"]:
                    continue

                sources = entry.get("sources", [])
                url_partial = update["url_contains"]

                # Check if we need to add a new source
                if "add_new_source" in update:
                    # Check if source already exists
                    exists = any(url_partial in s.get("url", "") for s in sources)
                    if not exists:
                        sources.append(update["add_new_source"])
                        print(f"  Added new source to {entry_id}: {update['add_new_source']['name']}")
                        update_count += 1
                        continue

                # Update existing source archive path
                for source in sources:
                    if url_partial in source.get("url", ""):
                        old_path = source.get("archive_path", "")
                        new_path = update["new_archive_path"]
                        if old_path != new_path:
                            source["archived"] = True
                            source["archive_path"] = new_path
                            print(f"  Updated {entry_id} {source.get('name', 'unknown')}: {old_path} -> {new_path}")
                            update_count += 1
                        else:
                            print(f"  {entry_id} {source.get('name', 'unknown')} already up to date")

        if update_count > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  Saved {update_count} updates to {filename}")
        else:
            print(f"  No updates needed for {filename}")

if __name__ == "__main__":
    update_json_files()
    print("\nDone!")
