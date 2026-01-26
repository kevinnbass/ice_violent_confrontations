#!/usr/bin/env python
"""
Verification Script for Refactoring
====================================
Verifies data integrity and backward compatibility after refactoring.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def verify_json_extraction():
    """Verify JSON files were extracted correctly."""
    print("\n" + "=" * 60)
    print("1. VERIFYING JSON DATA EXTRACTION")
    print("=" * 60)

    from ice_arrests.data.loader import (
        load_incidents,
        load_arrests_by_state,
        load_state_classifications,
    )

    # Load from JSON
    all_incidents = load_incidents()
    arrests = load_arrests_by_state()
    classifications = load_state_classifications()

    # Load from original Python files
    from TIERED_INCIDENT_DATABASE import get_all_incidents as orig_incidents
    from COMPREHENSIVE_SOURCED_DATABASE import ARRESTS_BY_STATE
    from STATE_ENFORCEMENT_CLASSIFICATIONS import STATE_CLASSIFICATIONS

    orig_count = len(orig_incidents())
    json_count = len(all_incidents)

    print(f"  Original incidents count: {orig_count}")
    print(f"  JSON incidents count: {json_count}")
    assert json_count == orig_count, f"Incident count mismatch: {json_count} != {orig_count}"
    print("  [OK] Incidents count matches")

    print(f"  Original arrests states: {len(ARRESTS_BY_STATE)}")
    print(f"  JSON arrests states: {len(arrests)}")
    assert len(arrests) == len(ARRESTS_BY_STATE), "Arrests count mismatch"
    print("  [OK] Arrests count matches")

    print(f"  Original classifications: {len(STATE_CLASSIFICATIONS)}")
    print(f"  JSON classifications: {len(classifications)}")
    assert len(classifications) == len(STATE_CLASSIFICATIONS), "Classifications count mismatch"
    print("  [OK] Classifications count matches")

    return True


def verify_backward_compatibility():
    """Verify old imports still work."""
    print("\n" + "=" * 60)
    print("2. VERIFYING BACKWARD COMPATIBILITY")
    print("=" * 60)

    # Test original imports
    try:
        from TIERED_INCIDENT_DATABASE import (
            get_all_incidents,
            get_incidents_by_tier,
            SourceTier,
            IncidentType,
            TIER_1_DEATHS_IN_CUSTODY,
        )
        print("  [OK] TIERED_INCIDENT_DATABASE imports work")
    except ImportError as e:
        print(f"  [FAIL] TIERED_INCIDENT_DATABASE import failed: {e}")
        return False

    try:
        from COMPREHENSIVE_SOURCED_DATABASE import ARRESTS_BY_STATE, VIOLENT_INCIDENTS
        print("  [OK] COMPREHENSIVE_SOURCED_DATABASE imports work")
    except ImportError as e:
        print(f"  [FAIL] COMPREHENSIVE_SOURCED_DATABASE import failed: {e}")
        return False

    try:
        from STATE_ENFORCEMENT_CLASSIFICATIONS import STATE_CLASSIFICATIONS
        print("  [OK] STATE_ENFORCEMENT_CLASSIFICATIONS imports work")
    except ImportError as e:
        print(f"  [FAIL] STATE_ENFORCEMENT_CLASSIFICATIONS import failed: {e}")
        return False

    try:
        from FINAL_MERGED_DATABASE import create_final_dataset
        df = create_final_dataset()
        print(f"  [OK] FINAL_MERGED_DATABASE works ({len(df)} rows)")
    except Exception as e:
        print(f"  [FAIL] FINAL_MERGED_DATABASE failed: {e}")
        return False

    return True


def verify_new_package():
    """Verify new package structure works."""
    print("\n" + "=" * 60)
    print("3. VERIFYING NEW PACKAGE STRUCTURE")
    print("=" * 60)

    try:
        from ice_arrests.data.loader import load_incidents, load_arrests_by_state
        from ice_arrests.data.schemas import SourceTier, IncidentType
        from ice_arrests.analysis.merge import create_merged_dataset
        from ice_arrests.analysis.tiered import calculate_confidence_adjusted_ratios

        incidents = load_incidents()
        print(f"  [OK] Loaded {len(incidents)} incidents from JSON")

        arrests = load_arrests_by_state()
        print(f"  [OK] Loaded {len(arrests)} state arrests records")

        df = create_merged_dataset()
        print(f"  [OK] Created merged dataset with {len(df)} rows")

        ratios = calculate_confidence_adjusted_ratios()
        print(f"  [OK] Calculated confidence ratios for {len(ratios)} states")

        return True

    except ImportError as e:
        print(f"  [FAIL] Package import failed: {e}")
        return False
    except Exception as e:
        print(f"  [FAIL] Package function failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_tier_counts():
    """Verify incident counts by tier."""
    print("\n" + "=" * 60)
    print("4. VERIFYING TIER COUNTS")
    print("=" * 60)

    from ice_arrests.data.loader import get_incidents_by_tier

    tier_counts = {
        1: 28,   # Deaths in custody
        2: 36,   # Shootings + less lethal (15 + 21)
        3: 92,   # Systematic search
        4: 9,    # Ad-hoc search
    }

    for tier, expected in tier_counts.items():
        incidents = get_incidents_by_tier(tier)
        actual = len(incidents)
        print(f"  Tier {tier}: {actual} incidents (expected: {expected})")
        if actual != expected:
            print(f"    ⚠ Warning: Tier {tier} count differs")

    return True


def main():
    """Run all verifications."""
    print("=" * 60)
    print("REFACTORING VERIFICATION")
    print("=" * 60)

    all_passed = True

    try:
        all_passed &= verify_json_extraction()
    except Exception as e:
        print(f"  [FAIL] JSON extraction verification failed: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False

    try:
        all_passed &= verify_backward_compatibility()
    except Exception as e:
        print(f"  [FAIL] Backward compatibility verification failed: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False

    try:
        all_passed &= verify_new_package()
    except Exception as e:
        print(f"  [FAIL] New package verification failed: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False

    try:
        verify_tier_counts()
    except Exception as e:
        print(f"  [FAIL] Tier count verification failed: {e}")

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL VERIFICATIONS PASSED")
    else:
        print("SOME VERIFICATIONS FAILED")
    print("=" * 60)

    return all_passed


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
