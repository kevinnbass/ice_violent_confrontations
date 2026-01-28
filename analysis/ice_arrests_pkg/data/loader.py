"""
Data Loader for ice_arrests
===========================
Unified data loading from JSON files.
"""

import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from difflib import SequenceMatcher

# Get package data directory
_PACKAGE_ROOT = Path(__file__).parent.parent.parent
_DATA_DIR = _PACKAGE_ROOT / "data"
_INCIDENTS_DIR = _DATA_DIR / "incidents"


def _load_json(filepath: Path) -> Any:
    """Load a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_incidents(tiers: Optional[List[int]] = None) -> List[Dict]:
    """
    Load incidents from JSON files.

    Args:
        tiers: Optional list of tiers to load (1, 2, 3, 4).
               If None, loads all tiers.

    Returns:
        List of incident dictionaries.
    """
    all_incidents = []

    # Define tier mappings
    tier_files = {
        1: "tier1_deaths_in_custody.json",
        2: ["tier2_shootings.json", "tier2_less_lethal.json"],
        3: "tier3_incidents.json",
        4: "tier4_incidents.json",
    }

    # Default to all tiers if none specified
    if tiers is None:
        tiers = [1, 2, 3, 4]

    for tier in tiers:
        if tier not in tier_files:
            continue

        files = tier_files[tier]
        if isinstance(files, str):
            files = [files]

        for filename in files:
            filepath = _INCIDENTS_DIR / filename
            if filepath.exists():
                incidents = _load_json(filepath)
                all_incidents.extend(incidents)

    return all_incidents


def get_incidents_by_tier(tier: int) -> List[Dict]:
    """
    Get incidents for a specific tier only.

    Args:
        tier: The tier number (1-4).

    Returns:
        List of incidents for that tier.
    """
    return load_incidents(tiers=[tier])


def get_incidents_by_type(incident_type: str) -> List[Dict]:
    """
    Get incidents of a specific type.

    Args:
        incident_type: The incident type to filter by.

    Returns:
        List of matching incidents.
    """
    all_incidents = load_incidents()
    return [i for i in all_incidents if i.get('incident_type') == incident_type]


def load_arrests_by_state() -> Dict[str, Dict]:
    """
    Load arrests by state data.

    Returns:
        Dictionary mapping state names to arrest data.
    """
    filepath = _DATA_DIR / "arrests_by_state.json"
    if filepath.exists():
        return _load_json(filepath)
    return {}


def load_state_classifications() -> Dict[str, Dict]:
    """
    Load state enforcement classifications.

    Returns:
        Dictionary mapping state names to classification data.
    """
    filepath = _DATA_DIR / "state_classifications.json"
    if filepath.exists():
        return _load_json(filepath)
    return {}


def load_violent_incidents_legacy() -> List[Dict]:
    """
    Load the legacy violent incidents data.

    This is from COMPREHENSIVE_SOURCED_DATABASE for backward compatibility.

    Returns:
        List of incident dictionaries.
    """
    filepath = _DATA_DIR / "violent_incidents_legacy.json"
    if filepath.exists():
        return _load_json(filepath)
    return []


def load_states_searched_metadata() -> Dict[str, Dict]:
    """
    Load metadata about states that were searched for Tier 1-2 data.

    Returns:
        Dictionary with search metadata for each state.
    """
    filepath = _INCIDENTS_DIR / "states_searched_metadata.json"
    if filepath.exists():
        return _load_json(filepath)
    return {}


def get_all_incidents() -> List[Dict]:
    """
    Get all incidents across all tiers.

    Convenience function for backward compatibility.

    Returns:
        List of all incidents.
    """
    return load_incidents()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def infer_victim_category(incident: Dict) -> str:
    """
    Infer victim_category if not explicitly set.

    Args:
        incident: The incident dictionary.

    Returns:
        The inferred victim category.
    """
    if incident.get('victim_category'):
        return incident['victim_category']

    incident_type = incident.get('incident_type', '')

    if incident_type == 'death_in_custody':
        return 'detainee'

    if incident_type == 'shooting_at_agent':
        return 'officer'

    if incident.get('us_citizen') and incident_type in ['wrongful_detention', 'wrongful_deportation']:
        return 'us_citizen_collateral'

    if incident.get('protest_related'):
        return 'protester'

    if incident_type == 'mass_raid':
        return 'enforcement_target'

    return 'enforcement_target'


def get_incidents_by_victim_category(category: str) -> List[Dict]:
    """
    Get incidents affecting a specific victim category.

    Args:
        category: The victim category to filter by.

    Returns:
        List of matching incidents.
    """
    all_incidents = get_all_incidents()
    return [i for i in all_incidents if infer_victim_category(i) == category]


# =============================================================================
# DEDUPLICATION FUNCTIONS
# =============================================================================

def load_incidents_deduplicated(
    tiers: Optional[List[int]] = None,
    dedupe_strategy: str = "primary_only"
) -> List[Dict]:
    """
    Load incidents with deduplication applied.

    Args:
        tiers: Optional list of tiers to load (1, 2, 3, 4).
               If None, loads all tiers.
        dedupe_strategy: Deduplication strategy to use:
            - "primary_only": Only return records where is_primary_record=True
            - "highest_tier": Return highest tier version per canonical_incident_id
            - "all_with_flag": Return all records, adding 'is_duplicate' flag

    Returns:
        List of deduplicated incident dictionaries.
    """
    all_incidents = load_incidents(tiers=tiers)

    if dedupe_strategy == "primary_only":
        return _dedupe_primary_only(all_incidents)
    elif dedupe_strategy == "highest_tier":
        return _dedupe_highest_tier(all_incidents)
    elif dedupe_strategy == "all_with_flag":
        return _dedupe_all_with_flag(all_incidents)
    else:
        raise ValueError(f"Unknown dedupe_strategy: {dedupe_strategy}")


def _dedupe_primary_only(incidents: List[Dict]) -> List[Dict]:
    """Return only primary records (is_primary_record=True)."""
    return [i for i in incidents if i.get('is_primary_record', True)]


def _dedupe_highest_tier(incidents: List[Dict]) -> List[Dict]:
    """Return the highest tier version for each canonical_incident_id."""
    # Group by canonical_incident_id
    canonical_groups: Dict[str, List[Dict]] = {}

    for incident in incidents:
        canonical_id = incident.get('canonical_incident_id')
        if canonical_id:
            if canonical_id not in canonical_groups:
                canonical_groups[canonical_id] = []
            canonical_groups[canonical_id].append(incident)
        else:
            # No canonical_id means it's unique - use incident id as key
            canonical_groups[incident['id']] = [incident]

    # Select highest tier (lowest number) from each group
    result = []
    for canonical_id, group in canonical_groups.items():
        # Sort by source_tier (ascending) - tier 1 is highest quality
        group.sort(key=lambda x: x.get('source_tier', 4))
        result.append(group[0])

    return result


def _dedupe_all_with_flag(incidents: List[Dict]) -> List[Dict]:
    """Return all records with 'is_duplicate' flag added."""
    # Build set of IDs that are duplicates (non-primary)
    result = []
    for incident in incidents:
        incident_copy = incident.copy()
        incident_copy['is_duplicate'] = not incident.get('is_primary_record', True)
        result.append(incident_copy)
    return result


def validate_related_incidents() -> List[Dict]:
    """
    Validate all related_incidents links exist and are bidirectional.

    Returns:
        List of validation error dictionaries with keys:
        - incident_id: The incident with the issue
        - error_type: Type of error ('missing_target', 'not_bidirectional', 'self_reference')
        - details: Description of the issue
    """
    all_incidents = load_incidents()
    errors = []

    # Build lookup of all incident IDs
    incident_ids = {i['id'] for i in all_incidents}

    # Build lookup of incident -> related_incidents
    related_map: Dict[str, List[str]] = {}
    for incident in all_incidents:
        related_map[incident['id']] = incident.get('related_incidents', [])

    for incident in all_incidents:
        incident_id = incident['id']
        related = incident.get('related_incidents', [])

        for related_id in related:
            # Check for self-reference
            if related_id == incident_id:
                errors.append({
                    'incident_id': incident_id,
                    'error_type': 'self_reference',
                    'details': f"Incident references itself in related_incidents"
                })
                continue

            # Check target exists
            if related_id not in incident_ids:
                errors.append({
                    'incident_id': incident_id,
                    'error_type': 'missing_target',
                    'details': f"Related incident '{related_id}' does not exist"
                })
                continue

            # Check bidirectional link
            target_related = related_map.get(related_id, [])
            if incident_id not in target_related:
                errors.append({
                    'incident_id': incident_id,
                    'error_type': 'not_bidirectional',
                    'details': f"Link to '{related_id}' is not bidirectional"
                })

    return errors


def find_potential_duplicates(
    similarity_threshold: float = 0.8
) -> List[Tuple[Dict, Dict, float]]:
    """
    Find potential duplicate incidents via fuzzy matching.

    Matches on: victim_name + date + state

    Args:
        similarity_threshold: Minimum similarity score (0-1) to consider a match.

    Returns:
        List of tuples: (incident1, incident2, similarity_score)
    """
    all_incidents = load_incidents()
    potential_duplicates = []

    # Only compare incidents that don't already have related_incidents links
    for i, inc1 in enumerate(all_incidents):
        for inc2 in all_incidents[i + 1:]:
            # Skip if already linked
            if inc2['id'] in inc1.get('related_incidents', []):
                continue
            if inc1['id'] in inc2.get('related_incidents', []):
                continue

            # Must be same date to be potential duplicate
            if inc1.get('date') != inc2.get('date'):
                continue

            # Must be same state
            if inc1.get('state') != inc2.get('state'):
                continue

            # Compare victim names if both have them
            name1 = inc1.get('victim_name', '')
            name2 = inc2.get('victim_name', '')

            if not name1 or not name2:
                continue

            # Calculate similarity
            similarity = SequenceMatcher(
                None,
                _normalize_name(name1),
                _normalize_name(name2)
            ).ratio()

            if similarity >= similarity_threshold:
                potential_duplicates.append((inc1, inc2, similarity))

    # Sort by similarity descending
    potential_duplicates.sort(key=lambda x: x[2], reverse=True)
    return potential_duplicates


def _normalize_name(name: str) -> str:
    """Normalize a name for comparison."""
    if not name:
        return ""
    # Lowercase, remove extra whitespace, remove punctuation
    name = name.lower().strip()
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name)
    return name


def generate_canonical_id(incident: Dict) -> str:
    """
    Generate a canonical incident ID for a given incident.

    Format: INC-{YYYY-MM-DD}-{STATE_ABBREV}-{VICTIM_NAME_OR_TYPE}

    Args:
        incident: The incident dictionary.

    Returns:
        Generated canonical incident ID.
    """
    date = incident.get('date', 'UNKNOWN')

    # Get state abbreviation
    state = incident.get('state', 'XX')
    state_abbrev = _get_state_abbrev(state)

    # Get victim identifier
    victim_name = incident.get('victim_name', '')
    if victim_name:
        # Use last name, uppercase
        parts = victim_name.split()
        # Handle names like "Villegas Gonzalez" - use first last name
        victim_id = parts[-1].upper() if parts else 'UNKNOWN'
        # Clean up special characters
        victim_id = re.sub(r'[^A-Z]', '', victim_id)
    else:
        # Use incident type as fallback
        incident_type = incident.get('incident_type', 'incident')
        victim_id = incident_type.upper().replace('_', '-')

    return f"INC-{date}-{state_abbrev}-{victim_id}"


def _get_state_abbrev(state_name: str) -> str:
    """Convert state name to abbreviation."""
    STATE_ABBREVS = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
        'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
        'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
        'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
        'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
        'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
        'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
        'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
        'Oregon': 'OR', 'Pennsylvania': 'PA', 'Puerto Rico': 'PR', 'Rhode Island': 'RI',
        'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX',
        'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
        'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
        'Unknown': 'XX'
    }
    return STATE_ABBREVS.get(state_name, 'XX')


def get_canonical_groups() -> Dict[str, List[Dict]]:
    """
    Group all incidents by their canonical_incident_id.

    Returns:
        Dictionary mapping canonical_incident_id to list of incidents.
        Incidents without canonical_incident_id are grouped by their id.
    """
    all_incidents = load_incidents()
    groups: Dict[str, List[Dict]] = {}

    for incident in all_incidents:
        canonical_id = incident.get('canonical_incident_id', incident['id'])
        if canonical_id not in groups:
            groups[canonical_id] = []
        groups[canonical_id].append(incident)

    return groups


def count_unique_incidents(tiers: Optional[List[int]] = None) -> int:
    """
    Count unique real-world incidents (using canonical IDs for deduplication).

    Args:
        tiers: Optional list of tiers to include.

    Returns:
        Count of unique incidents.
    """
    incidents = load_incidents_deduplicated(tiers=tiers, dedupe_strategy="primary_only")
    return len(incidents)
