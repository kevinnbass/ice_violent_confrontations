#!/usr/bin/env python3
"""
Migration script: Convert flat source fields to unified sources array.

Before:
    {
        "source_url": "https://...",
        "source_name": "NBC News",
        "source_tier": 2,
        ...
    }

After:
    {
        "sources": [
            {
                "url": "https://...",
                "name": "NBC News",
                "tier": 2,
                "primary": true,
                "archived": true,
                "archive_path": "data/sources/T4-042/article.txt"
            }
        ],
        ...
    }

Usage:
    python scripts/migrate_sources_schema.py [--dry-run]
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import argparse


# Paths
BASE_DIR = Path(__file__).parent.parent
INCIDENTS_DIR = BASE_DIR / "data" / "incidents"
SOURCES_DIR = BASE_DIR / "data" / "sources"
BACKUP_DIR = INCIDENTS_DIR / "backups_schema_migration"

# Files to migrate
INCIDENT_FILES = [
    "tier1_deaths_in_custody.json",
    "tier2_less_lethal.json",
    "tier3_incidents.json",
    "tier4_incidents.json",
]


def create_backup():
    """Create timestamped backup of all incident files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / timestamp
    backup_path.mkdir(parents=True, exist_ok=True)

    backed_up = []
    for filename in INCIDENT_FILES:
        src = INCIDENTS_DIR / filename
        if src.exists():
            dst = backup_path / filename
            shutil.copy2(src, dst)
            backed_up.append(str(dst))
            print(f"  Backed up: {filename}")

    # Also save a manifest
    manifest = {
        "backup_timestamp": timestamp,
        "files": backed_up,
        "migration": "flat_sources_to_array"
    }
    with open(backup_path / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nBackup created at: {backup_path}")
    return backup_path


def check_archive_exists(entry_id):
    """Check if archived article exists for this entry."""
    archive_dir = SOURCES_DIR / entry_id
    article_txt = archive_dir / "article.txt"
    article_html = archive_dir / "article.html"

    if article_txt.exists():
        return True, f"data/sources/{entry_id}/article.txt"
    elif article_html.exists():
        return True, f"data/sources/{entry_id}/article.html"
    return False, None


def migrate_entry(entry):
    """Migrate a single entry from flat source fields to sources array."""
    # Check if already migrated
    if "sources" in entry:
        return entry, False  # Already has sources array

    # Extract old fields
    old_url = entry.pop("source_url", None)
    old_name = entry.pop("source_name", None)
    old_tier = entry.pop("source_tier", None)

    if not old_url:
        # No source to migrate
        return entry, False

    # Check for archived version
    entry_id = entry.get("id", "")
    archived, archive_path = check_archive_exists(entry_id)

    # Build new source object
    source = {
        "url": old_url,
        "name": old_name,
        "tier": old_tier,
        "primary": True,
    }

    if archived:
        source["archived"] = True
        source["archive_path"] = archive_path
    else:
        source["archived"] = False

    # Add sources array to entry
    entry["sources"] = [source]

    return entry, True


def migrate_file(filepath, dry_run=False):
    """Migrate all entries in a single file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    migrated_count = 0
    skipped_count = 0

    for i, entry in enumerate(data):
        data[i], was_migrated = migrate_entry(entry)
        if was_migrated:
            migrated_count += 1
        else:
            skipped_count += 1

    if not dry_run:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    return migrated_count, skipped_count


def main():
    parser = argparse.ArgumentParser(description="Migrate source fields to unified array schema")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    print("=" * 60)
    print("SOURCE SCHEMA MIGRATION")
    print("=" * 60)
    print(f"\nDry run: {args.dry_run}")

    # Step 1: Create backup (even for dry run, to test)
    if not args.dry_run:
        print("\n[1/3] Creating backup...")
        backup_path = create_backup()
    else:
        print("\n[1/3] Skipping backup (dry run)")

    # Step 2: Migrate each file
    print("\n[2/3] Migrating files...")
    total_migrated = 0
    total_skipped = 0

    for filename in INCIDENT_FILES:
        filepath = INCIDENTS_DIR / filename
        if not filepath.exists():
            print(f"  SKIP: {filename} (not found)")
            continue

        migrated, skipped = migrate_file(filepath, dry_run=args.dry_run)
        total_migrated += migrated
        total_skipped += skipped

        action = "Would migrate" if args.dry_run else "Migrated"
        print(f"  {filename}: {action} {migrated} entries, skipped {skipped}")

    # Step 3: Summary
    print("\n[3/3] Summary")
    print("-" * 40)
    print(f"  Total entries migrated: {total_migrated}")
    print(f"  Total entries skipped:  {total_skipped}")

    if args.dry_run:
        print("\n[DRY RUN] No files were modified.")
        print("Run without --dry-run to apply changes.")
    else:
        print(f"\nMigration complete!")
        print(f"Backup location: {backup_path}")
        print("\nTo restore from backup if needed:")
        print(f"  cp {backup_path}/*.json {INCIDENTS_DIR}/")

    print("=" * 60)


if __name__ == "__main__":
    main()
