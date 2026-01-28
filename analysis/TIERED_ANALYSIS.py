"""
TIERED ANALYSIS: ICE Incidents with Confidence Levels
======================================================
Analyzes incidents by source tier and provides confidence assessments
for different types of analysis.

NOTE: This file now uses the ice_arrests package for data loading and analysis.
      Legacy imports are preserved for backward compatibility.
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import warnings as _warnings

# Try to import from new package first
try:
    from ice_arrests import load_incidents, load_arrests_by_state, load_state_classifications
    from ice_arrests.data.loader import get_incidents_by_tier as _get_incidents_by_tier
    from ice_arrests.analysis.tiered import (
        calculate_confidence_adjusted_ratios as _calc_ratios,
        analyze_by_classification_with_confidence as _analyze_by_class,
        analyze_by_state_and_tier as _analyze_by_tier,
    )
    _NEW_PACKAGE_AVAILABLE = True

    # Load from JSON via package
    ARRESTS_BY_STATE = load_arrests_by_state()
    STATE_CLASSIFICATIONS = load_state_classifications()

    # Package-based functions
    def get_all_incidents():
        return load_incidents()

    def get_incidents_by_tier(tier):
        return load_incidents(tiers=[tier])

    def get_incidents_by_type(incident_type):
        all_incidents = load_incidents()
        return [i for i in all_incidents if i.get('incident_type') == incident_type]

    # Load tier-specific data for backward compatibility
    _all = load_incidents()
    TIER_1_DEATHS_IN_CUSTODY = [i for i in _all if i.get('source_tier') == 1]
    TIER_2_SHOOTINGS_BY_AGENTS = [i for i in _all if i.get('source_tier') == 2 and 'shooting' in i.get('incident_type', '') and i.get('incident_type') != 'shooting_at_agent']
    TIER_2_LESS_LETHAL = [i for i in _all if i.get('source_tier') == 2 and i.get('incident_type') == 'less_lethal']
    TIER_2_WRONGFUL_DETENTIONS = [i for i in _all if i.get('source_tier') == 2 and 'wrongful' in i.get('incident_type', '')]

except ImportError:
    _NEW_PACKAGE_AVAILABLE = False

    # Fall back to legacy imports (suppress deprecation warnings)
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore", DeprecationWarning)
        from TIERED_INCIDENT_DATABASE import (
            get_all_incidents,
            get_incidents_by_tier,
            get_incidents_by_type,
            TIER_1_DEATHS_IN_CUSTODY,
            TIER_2_SHOOTINGS_BY_AGENTS,
            TIER_2_LESS_LETHAL,
            TIER_2_WRONGFUL_DETENTIONS,
        )
        from COMPREHENSIVE_SOURCED_DATABASE import ARRESTS_BY_STATE
        from STATE_ENFORCEMENT_CLASSIFICATIONS import STATE_CLASSIFICATIONS


# =============================================================================
# CONFIDENCE LEVELS
# =============================================================================

CONFIDENCE_LEVELS = {
    "HIGH": "Data from official government sources with mandated reporting",
    "MEDIUM_HIGH": "Data from FOIA releases or systematic investigative journalism",
    "MEDIUM": "Data from systematic news search with known coverage biases",
    "LOW_MEDIUM": "Data available but significant gaps acknowledged",
    "LOW": "Ad-hoc data collection with high selection bias risk",
}


# =============================================================================
# ANALYSIS BY TIER
# =============================================================================

def analyze_by_state_and_tier():
    """Analyze incidents by state, broken down by source tier."""
    all_incidents = get_all_incidents()

    # Build state-level aggregations
    state_data = defaultdict(lambda: {
        'tier_1_count': 0,
        'tier_2_count': 0,
        'tier_3_count': 0,
        'tier_4_count': 0,
        'total_deaths': 0,
        'total_injuries': 0,
        'us_citizens': 0,
        'incidents_by_type': defaultdict(int),
    })

    for incident in all_incidents:
        state = incident.get('state', 'Unknown')
        tier = incident.get('source_tier', 4)

        state_data[state][f'tier_{tier}_count'] += 1

        # Count deaths
        if incident.get('outcome') == 'death' or 'death' in incident.get('incident_type', ''):
            state_data[state]['total_deaths'] += 1

        # Count injuries
        if incident.get('outcome') == 'injury' or incident.get('injury'):
            state_data[state]['total_injuries'] += 1

        # Count US citizens
        if incident.get('us_citizen') == True:
            state_data[state]['us_citizens'] += 1

        # Count by type
        incident_type = incident.get('incident_type', 'unknown')
        state_data[state]['incidents_by_type'][incident_type] += 1

    return dict(state_data)


def calculate_confidence_adjusted_ratios():
    """
    Calculate violence/arrest ratios with confidence levels.

    Only uses Tier 1 + Tier 2 data for ratio calculations.
    Returns confidence assessment for each state.
    """
    results = []

    # Get high-confidence incidents (Tier 1 + 2 only)
    tier_1 = get_incidents_by_tier(1)
    tier_2 = get_incidents_by_tier(2)
    high_confidence_incidents = tier_1 + tier_2

    # Count by state
    state_counts = defaultdict(lambda: {
        'deaths_tier1': 0,
        'shootings_tier2': 0,
        'less_lethal_tier2': 0,
        'wrongful_detention_tier2': 0,
        'total_high_confidence': 0,
    })

    for incident in high_confidence_incidents:
        state = incident.get('state', 'Unknown')
        tier = incident.get('source_tier')
        incident_type = incident.get('incident_type', '')

        state_counts[state]['total_high_confidence'] += 1

        if tier == 1:
            state_counts[state]['deaths_tier1'] += 1
        elif tier == 2:
            if 'shooting' in incident_type and 'agent' not in incident.get('perpetrator', 'agent'):
                state_counts[state]['shootings_tier2'] += 1
            elif incident_type == 'less_lethal':
                state_counts[state]['less_lethal_tier2'] += 1
            elif 'wrongful' in incident_type:
                state_counts[state]['wrongful_detention_tier2'] += 1

    # Calculate ratios for states with arrest data
    for state, arrests_data in ARRESTS_BY_STATE.items():
        arrests = arrests_data['arrests']
        counts = state_counts.get(state, {})

        total_incidents = counts.get('total_high_confidence', 0)
        deaths = counts.get('deaths_tier1', 0)

        # Determine confidence level
        if deaths > 0 and total_incidents > 3:
            confidence = "MEDIUM_HIGH"
        elif deaths > 0 or total_incidents > 0:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"  # No incidents found doesn't mean none occurred

        # Calculate ratio (only if we have incidents)
        if arrests > 0:
            ratio = total_incidents / arrests * 1000
            death_ratio = deaths / arrests * 10000
        else:
            ratio = None
            death_ratio = None

        # Get classification
        classification = STATE_CLASSIFICATIONS.get(state, {}).get('classification', 'unknown')

        results.append({
            'state': state,
            'arrests': arrests,
            'total_high_confidence_incidents': total_incidents,
            'deaths_tier1': deaths,
            'violence_ratio_per_1000': round(ratio, 3) if ratio else None,
            'death_ratio_per_10000': round(death_ratio, 3) if death_ratio else None,
            'confidence_level': confidence,
            'enforcement_classification': classification,
        })

    return pd.DataFrame(results).sort_values('total_high_confidence_incidents', ascending=False)


def analyze_by_classification_with_confidence():
    """
    Aggregate analysis by sanctuary classification.
    Uses only Tier 1 + 2 data and reports confidence levels.
    """
    df = calculate_confidence_adjusted_ratios()

    results = []
    for classification in ['sanctuary', 'aggressive_anti_sanctuary', 'anti_sanctuary', 'neutral']:
        subset = df[df['enforcement_classification'] == classification]

        if len(subset) == 0:
            continue

        total_arrests = subset['arrests'].sum()
        total_incidents = subset['total_high_confidence_incidents'].sum()
        total_deaths = subset['deaths_tier1'].sum()
        states_with_data = len(subset[subset['total_high_confidence_incidents'] > 0])
        states_total = len(subset)

        # Calculate aggregate ratio
        if total_arrests > 0:
            agg_ratio = total_incidents / total_arrests * 1000
            death_ratio = total_deaths / total_arrests * 10000
        else:
            agg_ratio = None
            death_ratio = None

        # Confidence assessment
        coverage_pct = states_with_data / states_total * 100 if states_total > 0 else 0
        if coverage_pct >= 50 and total_incidents >= 10:
            confidence = "MEDIUM"
        elif coverage_pct >= 25 or total_incidents >= 5:
            confidence = "LOW_MEDIUM"
        else:
            confidence = "LOW"

        results.append({
            'classification': classification,
            'states_count': states_total,
            'states_with_incidents': states_with_data,
            'coverage_pct': round(coverage_pct, 1),
            'total_arrests': total_arrests,
            'total_incidents_tier1_2': total_incidents,
            'total_deaths_tier1': total_deaths,
            'ratio_per_1000': round(agg_ratio, 3) if agg_ratio else None,
            'death_ratio_per_10000': round(death_ratio, 3) if death_ratio else None,
            'confidence': confidence,
        })

    return pd.DataFrame(results)


def print_tiered_analysis():
    """Print comprehensive tiered analysis."""

    print("=" * 100)
    print("TIERED ANALYSIS: ICE Incidents with Confidence Levels")
    print("=" * 100)
    print("\nMETHODOLOGY:")
    print("  - Tier 1: Official government data (deaths in custody)")
    print("  - Tier 2: FOIA/investigative journalism (shootings, less-lethal, wrongful detentions)")
    print("  - Tier 3-4: News media (included for completeness, not used in ratios)")
    print("\n" + "=" * 100)

    # Summary by tier
    all_incidents = get_all_incidents()
    print("\nINCIDENT COUNTS BY TIER:")
    print("-" * 50)
    for tier in [1, 2, 3, 4]:
        tier_data = get_incidents_by_tier(tier)
        print(f"  Tier {tier}: {len(tier_data)} incidents")
    print(f"  TOTAL: {len(all_incidents)} incidents")

    # State-level analysis
    print("\n" + "=" * 100)
    print("STATE-LEVEL ANALYSIS (Tier 1 + 2 Data Only)")
    print("=" * 100)

    df = calculate_confidence_adjusted_ratios()

    # Show states with data
    states_with_data = df[df['total_high_confidence_incidents'] > 0].copy()
    print(f"\nStates with documented incidents: {len(states_with_data)}")
    print(f"States with arrest data but no documented incidents: {len(df) - len(states_with_data)}")

    print("\n" + "-" * 80)
    print(f"{'State':<20} {'Arrests':>10} {'Incidents':>10} {'Deaths':>8} {'Ratio/1k':>10} {'Confidence':<15}")
    print("-" * 80)

    for _, row in states_with_data.iterrows():
        ratio_str = f"{row['violence_ratio_per_1000']:.3f}" if row['violence_ratio_per_1000'] else "N/A"
        print(f"{row['state']:<20} {row['arrests']:>10,} {row['total_high_confidence_incidents']:>10} "
              f"{row['deaths_tier1']:>8} {ratio_str:>10} {row['confidence_level']:<15}")

    # Classification analysis
    print("\n" + "=" * 100)
    print("ANALYSIS BY SANCTUARY CLASSIFICATION")
    print("=" * 100)
    print("\n*** IMPORTANT: These comparisons have LOW confidence due to:")
    print("    - Uneven geographic coverage of incident data")
    print("    - Media coverage bias (sanctuary states may get more coverage)")
    print("    - Small sample sizes in most categories")
    print("")

    class_df = analyze_by_classification_with_confidence()

    print("-" * 100)
    print(f"{'Classification':<25} {'States':>8} {'w/Data':>8} {'Coverage':>10} {'Arrests':>12} "
          f"{'Incidents':>10} {'Deaths':>8} {'Ratio':>8} {'Conf':<12}")
    print("-" * 100)

    for _, row in class_df.iterrows():
        ratio_str = f"{row['ratio_per_1000']:.3f}" if row['ratio_per_1000'] else "N/A"
        print(f"{row['classification']:<25} {row['states_count']:>8} {row['states_with_incidents']:>8} "
              f"{row['coverage_pct']:>9.1f}% {row['total_arrests']:>12,} "
              f"{row['total_incidents_tier1_2']:>10} {row['total_deaths_tier1']:>8} {ratio_str:>8} {row['confidence']:<12}")

    # Data gaps
    print("\n" + "=" * 100)
    print("DATA GAPS AND LIMITATIONS")
    print("=" * 100)

    states_no_incidents = df[df['total_high_confidence_incidents'] == 0]['state'].tolist()
    print(f"\nStates with arrest data but NO documented incidents ({len(states_no_incidents)}):")
    print(f"  {', '.join(states_no_incidents)}")
    print("\n  NOTE: This does NOT mean no incidents occurred - only that none were")
    print("        documented in Tier 1-2 sources. Selection bias is likely.")

    # Known undercounts
    print("\n" + "-" * 50)
    print("KNOWN UNDERCOUNTS:")
    print("  - ProPublica found 170+ US citizen detentions; only ~30 fully documented")
    print("  - The Trace identified 26 shootings; our Tier 2 has 12 with full details")
    print("  - ICE stopped publishing death reports after Oct 2025")
    print("  - GAO found ICE couldn't provide 5 years of use-of-force data")

    return df, class_df


if __name__ == '__main__':
    state_df, class_df = print_tiered_analysis()

    # Save outputs
    state_df.to_csv('STATE_ANALYSIS_WITH_CONFIDENCE.csv', index=False)
    class_df.to_csv('CLASSIFICATION_ANALYSIS_WITH_CONFIDENCE.csv', index=False)

    print("\n\nSaved:")
    print("  - STATE_ANALYSIS_WITH_CONFIDENCE.csv")
    print("  - CLASSIFICATION_ANALYSIS_WITH_CONFIDENCE.csv")
