# ICE Violent Incidents Data: Sources and Methodology

## Available Data Sources

### 1. The Trace - ICE Shootings Tracker
- **URL**: https://www.thetrace.org/2025/12/immigration-ice-shootings-guns-tracker/
- **Coverage**: Jan 2025 - Present
- **What it tracks**:
  - 19 incidents where agents opened fire
  - 36 incidents where agents held people at gunpoint
  - 16 incidents involving less-lethal munitions
  - 5 deaths, 8 injuries
- **Data format**: Article with incident details (manual extraction required)
- **Verification**: Uses Gun Violence Archive data + news clips
- **Limitation**: "Likely an undercount as not all shootings are publicly reported"

### 2. House Oversight Committee Democrats - Immigration Dashboard
- **URL**: https://oversightdemocrats.house.gov/immigration-dashboard
- **Coverage**: 2025+
- **Categories tracked**:
  - "Concerning use of force"
  - "Concerning arrest/detention"
  - "Concerning deportation"
  - "Enforcement action at a sensitive location"
  - U.S. citizen involvement flag
- **Data format**: Searchable/filterable table by state, date, category
- **Verification**: "Only incidents verified by reputable media outlets or referenced in litigation"
- **Limitation**: No bulk download option

### 3. NBC News / Marshall Project Incident Lists
- **NBC**: https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202
- **Marshall Project**: https://www.themarshallproject.org/2026/01/07/ice-minneapolis-shooting-renee-good
- **Coverage**: Sept 2025 - Jan 2026
- **Data format**: Article with detailed incident narratives
- **Note**: Frequently updated as new incidents occur

### 4. Deportation Data Project
- **URL**: https://deportationdata.org/data/ice.html
- **Coverage**: Through Oct 2025
- **What it tracks**: Arrests, detentions, deportations (NOT violence)
- **Data format**: CSV downloads available
- **Use**: Provides denominator (arrests) for calculating violence ratios

### 5. DHS Official Statistics
- **URL**: https://www.ice.gov/statistics
- **Note**: Official data, but may not include all incident details
- **2025 stat**: 275 assaults on officers (vs 19 in same period 2024)

## Key Statistics Summary

| Metric | Count | Period |
|--------|-------|--------|
| Shootings by agents | 26 | Jan 2025 - Jan 2026 |
| Deaths from shootings | 6 | Jan 2025 - Jan 2026 |
| Agents opened fire | 19 | Jan 2025 - Jan 2026 |
| Held at gunpoint | 36 | Jan 2025 - Jan 2026 |
| Less-lethal munitions used | 16 | Jan 2025 - Jan 2026 |
| Deaths in ICE custody | 32 | 2025 (deadliest year in 20 yrs) |
| Assaults on officers | 275 | Jan 20 - Dec 31, 2025 |

## Incidents by State (Shootings Only, from compiled data)

| State | Incidents | Deaths | Injuries |
|-------|-----------|--------|----------|
| Minnesota | 3 | 1 | 2 |
| Illinois | 2 | 1 | 1 |
| California | 2 | 0 | 2 |
| Oregon | 1 | 0 | 2 |
| Texas | 1 | 1 | 0 |
| Arizona | 1 | 0 | 1 |
| Maryland | 1 | 0 | 1 |

## Methodology for Violence/Arrest Ratio

```
Violence Ratio = (Violent incidents in state) / (ICE arrests in state) × 1000
```

### Interpretation:
- Higher ratio = more violent incidents relative to arrest volume
- Useful for identifying states where enforcement is more contentious
- Should control for protest activity and local resistance levels

### Caveats:
1. **Underreporting**: Not all incidents make news
2. **Definition variance**: What counts as "violent" varies by source
3. **Temporal mismatch**: Incidents data may not align perfectly with arrest periods
4. **Causality unclear**: High ratios could reflect enforcement tactics OR local resistance

## Data Collection Protocol

For manual news compilation:

1. **Required fields** for each incident:
   - Date (YYYY-MM-DD)
   - State
   - City
   - Agency (ICE/CBP/Border Patrol)
   - Incident type (shooting/less_lethal/gunpoint/physical_force)
   - Victim name (if available)
   - Outcome (death/injury/no_injury)
   - Source URL
   - Verification status

2. **Verification standard**:
   - At least one reputable news outlet OR
   - Referenced in litigation OR
   - Official agency statement

3. **Exclusions**:
   - Unverified social media only
   - Incidents outside U.S.
   - Non-immigration enforcement contexts
