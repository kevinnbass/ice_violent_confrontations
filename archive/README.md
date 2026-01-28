# Archive Directory

This directory contains archived copies of legacy Python data files that have been superseded by the JSON-based data storage in `data/` and the `ice_arrests` package.

## Archived Files

| File | Lines | Original Purpose |
|------|-------|------------------|
| `TIERED_INCIDENT_DATABASE.py` | ~4,700 | Hardcoded incident data by source tier + enums + documentation |
| `COMPREHENSIVE_SOURCED_DATABASE.py` | ~1,500 | Hardcoded arrests and legacy violent incidents data |
| `STATE_ENFORCEMENT_CLASSIFICATIONS.py` | ~650 | Hardcoded state sanctuary/enforcement classifications |

## Why Archived?

These files embedded data directly in Python code, which caused several problems:
- **Large file sizes** - Difficult to review in code editors
- **Mixed concerns** - Data, enums, and functions all in one file
- **Version control noise** - Data changes created large diffs
- **Not portable** - Can't easily share data with other tools

## Current Approach

Data is now stored in JSON files under `data/`:
- `data/incidents/tier1_deaths_in_custody.json`
- `data/incidents/tier2_shootings.json`
- `data/incidents/tier2_less_lethal.json`
- `data/incidents/tier3_incidents.json`
- `data/incidents/tier4_incidents.json`
- `data/arrests_by_state.json`
- `data/state_classifications.json`
- `data/methodology.json`

Load data using the `ice_arrests` package:

```python
from ice_arrests import load_incidents, load_arrests_by_state, load_state_classifications

# Load all incidents
incidents = load_incidents()

# Load specific tiers only
tier_1_2 = load_incidents(tiers=[1, 2])

# Load arrest data
arrests = load_arrests_by_state()

# Load classifications
classifications = load_state_classifications()
```

## Backward Compatibility

The original files in the project root still exist with deprecation warnings. They will import the data from JSON files when possible, falling back to hardcoded data if needed.

Importing from these files will trigger a `DeprecationWarning`:

```python
# Deprecated - will show warning
from TIERED_INCIDENT_DATABASE import TIER_1_DEATHS_IN_CUSTODY

# Recommended approach
from ice_arrests import load_incidents
tier_1 = load_incidents(tiers=[1])
```

## Future Plans

The root-level legacy files (`TIERED_INCIDENT_DATABASE.py`, etc.) will be removed in a future version once all code has been migrated to use the `ice_arrests` package.

---

*Archived: January 2026*
