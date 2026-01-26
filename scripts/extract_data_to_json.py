"""
Script to extract data from Python files to JSON format.
Run this once to create the JSON data files.

NOTE: This script suppresses deprecation warnings to load from the
original Python data files, not from JSON.
"""

import json
import sys
import warnings
from pathlib import Path

# Suppress deprecation warnings to load from original Python data
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from TIERED_INCIDENT_DATABASE import (
    TIER_1_DEATHS_IN_CUSTODY,
    TIER_2_SHOOTINGS_BY_AGENTS,
    TIER_2_SHOOTINGS_AT_AGENTS,
    TIER_2_LESS_LETHAL,
    TIER_2_WRONGFUL_DETENTIONS,
    TIER_3_INCIDENTS,
    TIER_4_INCIDENTS,
    STATES_SEARCHED_NO_TIER1_DATA,
)

from COMPREHENSIVE_SOURCED_DATABASE import ARRESTS_BY_STATE, VIOLENT_INCIDENTS
from STATE_ENFORCEMENT_CLASSIFICATIONS import STATE_CLASSIFICATIONS


def write_json(data, filepath):
    """Write data to JSON file with pretty formatting."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  Saved: {filepath} ({len(data)} records)")


def main():
    """Extract all data to JSON files."""
    print("=" * 60)
    print("Extracting data to JSON files...")
    print("=" * 60)

    # Base paths
    data_dir = Path(__file__).parent.parent / "data"
    incidents_dir = data_dir / "incidents"

    # Create directories
    incidents_dir.mkdir(parents=True, exist_ok=True)

    # ==========================================================================
    # TIERED INCIDENT DATA
    # ==========================================================================
    print("\nTiered Incident Data:")

    # Tier 1 - Deaths in Custody
    write_json(TIER_1_DEATHS_IN_CUSTODY, incidents_dir / "tier1_deaths_in_custody.json")

    # Tier 2 - Shootings (combine by and at agents)
    tier2_shootings = TIER_2_SHOOTINGS_BY_AGENTS + TIER_2_SHOOTINGS_AT_AGENTS
    write_json(tier2_shootings, incidents_dir / "tier2_shootings.json")

    # Tier 2 - Less Lethal (combine with wrongful detentions as originally structured)
    tier2_less_lethal = TIER_2_LESS_LETHAL + TIER_2_WRONGFUL_DETENTIONS
    write_json(tier2_less_lethal, incidents_dir / "tier2_less_lethal.json")

    # Tier 3 - Systematic news search
    write_json(TIER_3_INCIDENTS, incidents_dir / "tier3_incidents.json")

    # Tier 4 - Ad-hoc search
    write_json(TIER_4_INCIDENTS, incidents_dir / "tier4_incidents.json")

    # States searched documentation
    write_json(STATES_SEARCHED_NO_TIER1_DATA, incidents_dir / "states_searched_metadata.json")

    # ==========================================================================
    # ARRESTS DATA
    # ==========================================================================
    print("\nArrests Data:")
    write_json(ARRESTS_BY_STATE, data_dir / "arrests_by_state.json")

    # Also save the VIOLENT_INCIDENTS from COMPREHENSIVE_SOURCED_DATABASE
    # (This is the simplified version used for backward compatibility)
    write_json(VIOLENT_INCIDENTS, data_dir / "violent_incidents_legacy.json")

    # ==========================================================================
    # STATE CLASSIFICATIONS
    # ==========================================================================
    print("\nState Classifications:")
    write_json(STATE_CLASSIFICATIONS, data_dir / "state_classifications.json")

    # ==========================================================================
    # SUMMARY
    # ==========================================================================
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)

    # Count totals
    total_incidents = (
        len(TIER_1_DEATHS_IN_CUSTODY) +
        len(TIER_2_SHOOTINGS_BY_AGENTS) +
        len(TIER_2_SHOOTINGS_AT_AGENTS) +
        len(TIER_2_LESS_LETHAL) +
        len(TIER_2_WRONGFUL_DETENTIONS) +
        len(TIER_3_INCIDENTS) +
        len(TIER_4_INCIDENTS)
    )

    print(f"\nTotal tiered incidents extracted: {total_incidents}")
    print(f"  Tier 1 (Deaths): {len(TIER_1_DEATHS_IN_CUSTODY)}")
    print(f"  Tier 2 (Shootings): {len(tier2_shootings)}")
    print(f"  Tier 2 (Less Lethal + Wrongful): {len(tier2_less_lethal)}")
    print(f"  Tier 3 (Systematic): {len(TIER_3_INCIDENTS)}")
    print(f"  Tier 4 (Ad-hoc): {len(TIER_4_INCIDENTS)}")
    print(f"\nArrests by state: {len(ARRESTS_BY_STATE)} states")
    print(f"State classifications: {len(STATE_CLASSIFICATIONS)} states")
    print(f"Legacy violent incidents: {len(VIOLENT_INCIDENTS)} records")


if __name__ == "__main__":
    main()
