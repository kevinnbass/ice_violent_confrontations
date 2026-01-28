# ICE Incidents Database - Data Dictionary

**Last Updated**: 2026-01-25
**Total Incidents**: 400
**Total Reference Entries**: 52 states/territories, 159 cities

---

## Data Structure Overview

```
ice_arrests/
├── data/
│   ├── incidents/
│   │   ├── tier1_deaths_in_custody.json    (49 incidents)
│   │   ├── tier2_shootings.json            (19 incidents)
│   │   ├── tier2_less_lethal.json          (50 incidents)
│   │   ├── tier3_incidents.json            (218 incidents)
│   │   └── tier4_incidents.json            (64 incidents)
│   └── reference/
│       └── sanctuary_jurisdictions.json     (52 states, 159 cities)
└── ice_arrests/data/schemas.py             (Schema definitions)
```

---

## Tier Classification System

| Tier | Source Type | Description | Count |
|------|-------------|-------------|-------|
| 1 | Official | ICE/DHS official reports, government records | 49 |
| 2 | FOIA/Investigative | FOIA releases, investigative journalism (The Trace, NBC) | 69 |
| 3 | Systematic Search | Systematic news searches, verified reports | 218 |
| 4 | Ad-hoc | Individual news reports, social media with verification | 64 |

---

## Incident Schema

### Core Required Fields (100% coverage)

| Field | Type | Format | Description |
|-------|------|--------|-------------|
| `id` | string | `T{tier}-{type}-{num}` | Unique identifier (e.g., "T1-D-003") |
| `date` | string | `YYYY-MM-DD` | Incident date |
| `state` | string | Full name | U.S. state/territory |
| `incident_type` | enum | See below | Type of incident |
| `source_tier` | integer | 1-4 | Data source quality tier |
| `source_url` | string | URL | Primary source link |
| `source_name` | string | Text | Source publication/agency |
| `verified` | boolean | true/false | Verification status |
| `victim_category` | enum | See below | Category of affected person |
| `outcome` | string | Text | Brief outcome description |
| `notes` | string | Text | Detailed incident notes |
| `affected_count` | integer | >= 1 | Number of people affected |
| `incident_scale` | enum | single/multiple/mass | Scale of incident |
| `outcome_detail` | string | Text | Detailed outcome |
| `outcome_category` | enum | See below | Standardized outcome category |
| `date_precision` | enum | day/month/year | How precise the date is |

### Incident Type Values
```
death_in_custody        - Death while in ICE/CBP custody
shooting_by_agent       - Agent fired weapon at person
shooting_at_agent       - Person fired at agent
less_lethal             - Tasers, pepper spray, rubber bullets
physical_force          - Strikes, takedowns, restraints
mass_raid               - Large-scale enforcement operation
wrongful_detention      - Detention of citizen or visa holder
wrongful_deportation    - Deportation of citizen or legal resident
```

### Outcome Category Values
```
death           - Fatal outcome
serious_injury  - Hospitalization required
injury          - Non-hospitalized injury
no_injury       - No physical injury
detained        - Person detained
arrested        - Person arrested
released        - Person released
deported        - Person deported
multiple        - Multiple different outcomes
none            - No outcome recorded
```

### Victim Category Values
```
detainee            - Person in ICE custody
suspect             - Person being pursued/arrested
bystander           - Uninvolved third party
us_citizen          - Confirmed U.S. citizen
legal_resident      - Legal resident (visa/green card)
undocumented        - Undocumented immigrant
unknown             - Status unknown
```

---

## Sanctuary Policy Fields (Cross-Referenced)

| Field | Type | Coverage | Description |
|-------|------|----------|-------------|
| `state_sanctuary_status` | enum | 96.2% | State-level sanctuary classification |
| `local_sanctuary_status` | enum | 73.2% | City/county-level policy |
| `detainer_policy` | enum | 96.2% | ICE detainer handling |
| `policy_conflict` | boolean | 54.8% | State vs local policy conflict |
| `jurisdiction_notes` | string | 65.2% | Jurisdiction-specific notes |

### State Sanctuary Status Values
```
sanctuary               - Statewide sanctuary law (CA SB54, IL TRUST Act)
anti_sanctuary          - Law mandating ICE cooperation (TX SB4, FL SB168)
aggressive_anti_sanctuary - Active enforcement partnerships
neutral                 - No specific state policy
```

### Local Sanctuary Status Values (ILRC-based)
```
sanctuary_strong    - ILRC "green" - strong protections
sanctuary_limited   - ILRC "light green" - some protections
sanctuary_partial   - ILRC "yellow" - partial cooperation
cooperative         - ILRC "orange" - general cooperation
policy_conflict     - Local differs from state policy
unknown             - Status not determined
```

### Detainer Policy Values
```
decline_all         - Decline all ICE detainers
honor_judicial      - Honor only judicial warrants
honor_felony        - Honor only for felony charges
honor_all           - Honor all ICE requests
case_by_case        - Case-by-case determination
state_mandated      - Required by state law
```

---

## Sanctuary Reference Data

### State Entry Schema (`data/reference/sanctuary_jurisdictions.json`)

```json
{
  "California": {
    "classification": "sanctuary",
    "primary_law": "SB 54 California Values Act (2017)",
    "detainer_policy": "decline_all",
    "doj_designated": false,
    "effective_date": "2018-01-01",
    "notes": "Statewide sanctuary law...",
    "source_url": "https://leginfo.legislature.ca.gov/...",
    "source_name": "California Legislature - SB 54 Official Text",
    "last_verified": "2026-01-25"
  }
}
```

### City Entry Schema

```json
{
  "Austin, TX": {
    "state": "Texas",
    "local_status": "policy_conflict",
    "detainer_policy": "state_mandated",
    "policy_conflict": true,
    "notes": "Historically immigrant-friendly but constrained by TX SB4...",
    "source_url": "https://www.kut.org/...",
    "source_name": "KUT - APD ICE Policy (2026)",
    "last_verified": "2026-01-25"
  }
}
```

---

## Key Legislation References

| State | Law | Effect | Effective Date |
|-------|-----|--------|----------------|
| California | SB 54 (Values Act) | Sanctuary | 2018-01-01 |
| Illinois | TRUST Act | Sanctuary | 2019-08-25 |
| New Jersey | AG Directive 2018-6 | Limited sanctuary | 2018-11-29 |
| Texas | SB 4 | Anti-sanctuary | 2017-09-01 |
| Florida | SB 168 | Anti-sanctuary | 2019-07-01 |
| Tennessee | SB 6002 | Anti-sanctuary | 2025-07-01 |
| Arizona | SB 1070 (partial) | Mandate cooperation | 2010-07-29 |

---

## Data Quality Metrics

### Coverage Statistics

| Metric | Value |
|--------|-------|
| Total incidents | 400 |
| 100% complete fields | 16 core fields |
| State sanctuary cross-ref | 96.2% (385/400) |
| City sanctuary cross-ref | 53.2% (213/400) |
| Date precision: day | 88.8% (355/400) |
| Date precision: month | 9.8% (39/400) |
| Date precision: year | 1.5% (6/400) |

### Source Diversity

| Source Type | Count | Examples |
|-------------|-------|----------|
| ICE Official | 49 | ICE Death Reporting, DHS Statistics |
| Investigative | 69 | The Trace, Marshall Project |
| News (systematic) | 218 | AP, Reuters, Local affiliates |
| News (ad-hoc) | 64 | Individual reports |

---

## Update History

| Date | Update |
|------|--------|
| 2026-01-25 | Added 159 cities to reference data |
| 2026-01-25 | Cross-referenced all incidents with sanctuary status |
| 2026-01-25 | Added source URLs to all reference entries |
| 2026-01-25 | Created data dictionary documentation |

---

## Usage Notes

### Parsing Incidents
```python
import json

with open('data/incidents/tier1_deaths_in_custody.json') as f:
    incidents = json.load(f)  # Returns list of incident dicts

for incident in incidents:
    print(f"{incident['date']}: {incident['incident_type']} in {incident['state']}")
```

### Filtering by Sanctuary Status
```python
# Get all incidents in sanctuary states
sanctuary_incidents = [i for i in incidents
                       if i.get('state_sanctuary_status') == 'sanctuary']

# Get policy conflict incidents
conflict_incidents = [i for i in incidents
                      if i.get('policy_conflict') == True]
```

### Joining with Reference Data
```python
with open('data/reference/sanctuary_jurisdictions.json') as f:
    ref = json.load(f)

states = ref['states']
cities = ref['cities_with_notable_policies']

# Get full state policy details
for incident in incidents:
    state_policy = states.get(incident['state'], {})
    print(f"Primary law: {state_policy.get('primary_law')}")
```

---

## Schema Validation

The schema is defined in `ice_arrests/data/schemas.py` and can be validated:

```python
from ice_arrests.data.schemas import Incident, validate_incident
# See schemas.py for enum definitions and dataclass structure
```

All 400 incidents pass schema validation as of 2026-01-25.
