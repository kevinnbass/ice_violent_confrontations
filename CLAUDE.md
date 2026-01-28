# Claude Code Project Guidelines

## Project Overview
This repository contains a database of ICE (Immigration and Customs Enforcement) incidents from 2025-2026, with associated source verification and analysis tools.

## Data Schema

### Incident Files
Located in `data/incidents/`:
- `tier1_deaths_in_custody.json` - Deaths in ICE custody
- `tier2_less_lethal.json` - Less-lethal force incidents (tasers, pepper spray, wrongful detention)
- `tier2_shootings.json` - Shooting incidents
- `tier3_incidents.json` - General incidents (raids, protests, policy)
- `tier4_incidents.json` - Miscellaneous incidents

### Sources Schema (NEW)
Each entry uses a `sources` array instead of flat fields:

```json
{
  "id": "T3-056",
  "date": "2025-05-08",
  "state": "Massachusetts",
  "city": "Worcester",
  ...
  "sources": [
    {
      "url": "https://www.boston25news.com/...",
      "name": "Boston 25 News",
      "tier": 2,
      "primary": true,
      "archived": true,
      "archive_path": "data/sources/T3-056/article.txt"
    },
    {
      "url": "https://secondary-source.com/...",
      "name": "Secondary Source",
      "tier": 3,
      "primary": false
    }
  ]
}
```

### Source Tiers
- **Tier 1**: Official government sources (ICE press releases, court documents)
- **Tier 2**: Major national news (CNN, NBC, NPR, AP)
- **Tier 3**: Local news and advocacy organizations
- **Tier 4**: Aggregators, blogs, secondary sources

## Verification Workflow

### IMPORTANT: Always Use Local Archives First

When verifying or reviewing an entry:

1. **Check for local article first**:
   ```
   data/sources/{entry_id}/article.txt
   ```

2. **Read the local article** to verify details match the entry

3. **Only fetch from web** if:
   - Local archive doesn't exist
   - Local archive is incomplete/wrong article
   - Need additional corroborating sources

### Running Verification

```bash
# Download missing archives first (high concurrency), then verify all
python scripts/robust_verify.py --download-missing --reset

# Full verification (local-first, then web fallback)
python scripts/robust_verify.py --reset

# Local archives only (no web fetching)
python scripts/robust_verify.py --local-only --reset

# Specific entries only
python scripts/robust_verify.py --ids T3-056,T4-042,T1-D-003
```

### Recommended Workflow

For complete verification, use `--download-missing`:
1. **Phase 1**: Downloads all missing articles with high concurrency (unlimited across domains, rate-limited within each domain)
2. **Phase 2**: Verifies all entries against local archives

### Verification Output
- Report: `data/sources/robust_verification_report.json`
- Audit log: `data/sources/robust_audit.jsonl`

### Verdicts
- **verified** (70%+): Strong match between article and entry
- **likely_valid** (50-69%): Reasonable match, may need review
- **weak_match** (35-49%): Partial match, needs manual verification
- **no_match** (<35%): Article doesn't support entry claims
- **url_inaccessible**: Could not fetch article
- **no_local_archive**: No local archive (in --local-only mode)

## Manual Verification Process

When manually reviewing entries:

1. **Read the local article** at `data/sources/{id}/article.txt`

2. **Cross-check these fields**:
   - Date (exact match preferred)
   - Location (city, state)
   - Victim name (if applicable)
   - Key details in `notes` field
   - Agency involved (ICE, CBP, DHS)

3. **Common errors to check for**:
   - Wrong date (off by days/months)
   - Wrong city (e.g., Tucker vs Norcross)
   - Fabricated details not in source
   - Fabricated names/ages
   - Wrong victim count
   - Misattributed quotes

4. **If article doesn't match entry**:
   - Search for correct source URL
   - Add to `sources` array as additional source
   - Update entry details to match verified sources

## Adding Additional Sources

To add a corroborating source to an entry:

```json
"sources": [
  { "url": "https://primary...", "name": "NBC", "tier": 2, "primary": true, "archived": true },
  { "url": "https://secondary...", "name": "Local News", "tier": 3, "primary": false }
]
```

## Schema Migration

If working with old schema (flat `source_url` field), run:
```bash
python scripts/migrate_sources_schema.py
```

Backups are created at: `data/incidents/backups_schema_migration/`

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/robust_verify.py` | Main verification (local-first) |
| `scripts/scrape_sources.py` | Download articles to local archive |
| `scripts/migrate_sources_schema.py` | Migrate to new sources array schema |
| `scripts/audit_urls.py` | Check URL accessibility |

## Notes for Claude

- **Always read local articles first** before web fetching
- **Entries can have multiple sources** - use the `sources` array
- **Check `archive_path`** to see if article is already downloaded
- **Verify details match exactly** - don't assume entry is correct
- **Common fabrication patterns**: wrong dates, invented ages, wrong cities, misattributed quotes
