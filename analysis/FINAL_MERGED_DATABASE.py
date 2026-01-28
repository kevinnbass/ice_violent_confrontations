"""
FINAL MERGED DATABASE: ICE Arrests, Violence, and State Classifications
=======================================================================
Combines all data sources with rigorous citations for every data point.

OUTPUT: Final analysis-ready dataset with violence/arrest ratios by state,
        classified by sanctuary/cooperation status.

NOTE: This file now uses the ice_arrests package for data loading and analysis.
      Legacy imports are preserved for backward compatibility.
"""

import pandas as pd
import numpy as np
import warnings as _warnings

# Try to import from new package first
try:
    from ice_arrests import load_arrests_by_state, load_state_classifications
    from ice_arrests.data.loader import load_violent_incidents_legacy
    from ice_arrests.analysis.merge import (
        create_merged_dataset as _create_merged,
        aggregate_by_classification as _aggregate_by_class,
    )
    _NEW_PACKAGE_AVAILABLE = True

    # Load from JSON via package
    ARRESTS_BY_STATE = load_arrests_by_state()
    STATE_CLASSIFICATIONS = load_state_classifications()
    VIOLENT_INCIDENTS = load_violent_incidents_legacy()
except ImportError:
    _NEW_PACKAGE_AVAILABLE = False

    # Fall back to legacy imports (suppress deprecation warnings)
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore", DeprecationWarning)
        from STATE_ENFORCEMENT_CLASSIFICATIONS import STATE_CLASSIFICATIONS
        from COMPREHENSIVE_SOURCED_DATABASE import ARRESTS_BY_STATE, VIOLENT_INCIDENTS

# =============================================================================
# MERGE ALL DATA
# =============================================================================

def create_final_dataset():
    """Create the final merged dataset with all sources documented."""

    # Convert incidents to DataFrame and aggregate by state
    incidents_df = pd.DataFrame(VIOLENT_INCIDENTS)

    state_violence = incidents_df.groupby('state').agg({
        'id': 'count',
    }).rename(columns={'id': 'total_violent_incidents'})

    # Count by outcome
    state_violence['deaths'] = incidents_df[incidents_df['outcome'] == 'death'].groupby('state').size()
    state_violence['injuries'] = incidents_df[incidents_df['outcome'] == 'injury'].groupby('state').size()

    # Count by type
    state_violence['shootings_by_agents'] = incidents_df[
        (incidents_df['type'] == 'shooting') & (incidents_df['perpetrator'] == 'agent')
    ].groupby('state').size()

    state_violence['less_lethal_incidents'] = incidents_df[
        incidents_df['type'] == 'less_lethal'
    ].groupby('state').size()

    state_violence['deaths_in_custody'] = incidents_df[
        incidents_df['type'] == 'death_in_custody'
    ].groupby('state').size()

    state_violence['us_citizens_affected'] = incidents_df[
        incidents_df['us_citizen'] == True
    ].groupby('state').size()

    state_violence['protest_related'] = incidents_df[
        incidents_df['protest_related'] == True
    ].groupby('state').size()

    state_violence = state_violence.fillna(0).astype(int).reset_index()

    # Add arrests data
    arrests_rows = []
    for state, data in ARRESTS_BY_STATE.items():
        arrests_rows.append({
            'state': state,
            'arrests': data['arrests'],
            'arrest_rate_per_100k': data['rate_per_100k'],
            'arrests_date_range': data['date_range'],
            'arrests_source_url': data['source_url'],
            'arrests_source_name': data['source_name'],
            'arrests_notes': data['notes']
        })
    arrests_df = pd.DataFrame(arrests_rows)

    # Add classification data
    class_rows = []
    for state, data in STATE_CLASSIFICATIONS.items():
        class_rows.append({
            'state': state,
            'enforcement_classification': data['classification'],
            'classification_tier': data['tier'],
            'primary_law': data['primary_law'],
            'law_effective_date': data.get('effective_date'),
            'doj_designated_sanctuary': data['doj_designated'],
            'classification_source_url': data['source_url'],
            'classification_source_name': data['source_name'],
            'ilrc_rating': data.get('ilrc_rating')
        })
    class_df = pd.DataFrame(class_rows)

    # Merge all
    merged = arrests_df.merge(class_df, on='state', how='outer')
    merged = merged.merge(state_violence, on='state', how='outer')
    merged = merged.fillna(0)

    # Fix dtypes after fillna
    int_cols = ['arrests', 'total_violent_incidents', 'deaths', 'injuries',
                'shootings_by_agents', 'less_lethal_incidents', 'deaths_in_custody',
                'us_citizens_affected', 'protest_related']
    for col in int_cols:
        if col in merged.columns:
            merged[col] = merged[col].astype(int)

    # Calculate ratios
    merged['violence_per_1000_arrests'] = np.where(
        merged['arrests'] > 0,
        merged['total_violent_incidents'] / merged['arrests'] * 1000,
        0
    ).round(3)

    merged['shootings_per_10000_arrests'] = np.where(
        merged['arrests'] > 0,
        merged['shootings_by_agents'] / merged['arrests'] * 10000,
        0
    ).round(3)

    merged['deaths_per_10000_arrests'] = np.where(
        merged['arrests'] > 0,
        merged['deaths'] / merged['arrests'] * 10000,
        0
    ).round(3)

    return merged.sort_values('total_violent_incidents', ascending=False)


def print_analysis():
    """Print comprehensive analysis."""
    df = create_final_dataset()

    print("=" * 100)
    print("FINAL MERGED ANALYSIS: ICE Violence Ratios by State Classification")
    print("=" * 100)

    print("\n" + "=" * 100)
    print("VIOLENCE RATIOS BY STATE (with Classification)")
    print("=" * 100)

    cols = ['state', 'enforcement_classification', 'arrests', 'total_violent_incidents',
            'violence_per_1000_arrests', 'shootings_by_agents', 'deaths']

    for _, row in df[df['total_violent_incidents'] > 0][cols].iterrows():
        print(f"\n{row['state']} [{row['enforcement_classification'].upper()}]")
        print(f"  Arrests: {row['arrests']:,} | Incidents: {row['total_violent_incidents']} | Violence Ratio: {row['violence_per_1000_arrests']:.3f}/1k")
        print(f"  Shootings by agents: {row['shootings_by_agents']} | Deaths: {row['deaths']}")

    # Aggregate by classification
    print("\n" + "=" * 100)
    print("AGGREGATE BY CLASSIFICATION TYPE")
    print("=" * 100)

    for classification in ['sanctuary', 'aggressive_anti_sanctuary', 'anti_sanctuary', 'neutral']:
        subset = df[df['enforcement_classification'] == classification]
        if len(subset) == 0:
            continue

        total_arrests = subset['arrests'].sum()
        total_incidents = subset['total_violent_incidents'].sum()
        total_deaths = subset['deaths'].sum()
        avg_ratio = total_incidents / total_arrests * 1000 if total_arrests > 0 else 0

        print(f"\n{classification.upper()} STATES ({len(subset)} states):")
        print(f"  Total arrests: {total_arrests:,}")
        print(f"  Total violent incidents: {total_incidents}")
        print(f"  Total deaths: {total_deaths}")
        print(f"  Average violence ratio: {avg_ratio:.3f} per 1,000 arrests")

    return df


if __name__ == '__main__':
    df = print_analysis()

    # Save final dataset
    df.to_csv('FINAL_MERGED_DATASET.csv', index=False)

    print("\n\n" + "=" * 100)
    print("OUTPUT FILES:")
    print("  - FINAL_MERGED_DATASET.csv (complete analysis-ready dataset)")
    print("=" * 100)

    # Print source summary
    print("\n" + "=" * 100)
    print("DATA SOURCES SUMMARY")
    print("=" * 100)

    print("\nARRESTS DATA SOURCES:")
    for state, data in ARRESTS_BY_STATE.items():
        print(f"  {state}: {data['source_name']} - {data['source_url']}")

    print("\nCLASSIFICATION SOURCES:")
    print("  Primary: DOJ Sanctuary Jurisdiction List (EO 14287)")
    print("    https://www.justice.gov/ag/us-sanctuary-jurisdiction-list")
    print("  Secondary: ILRC State Map on Immigration Enforcement")
    print("    https://www.ilrc.org/state-map-immigration-enforcement-2024")
    print("  Tertiary: Ballotpedia Sanctuary Policies")
    print("    https://ballotpedia.org/Sanctuary_jurisdiction_policies_by_state")

    print("\nINCIDENT DATA SOURCES:")
    print("  - NBC News ICE Shootings List")
    print("    https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202")
    print("  - The Trace ICE Shootings Tracker")
    print("    https://www.thetrace.org/2025/12/immigration-ice-shootings-guns-tracker/")
    print("  - ProPublica US Citizens Investigation")
    print("    https://www.propublica.org/article/immigration-dhs-american-citizens-arrested-detained-against-will")
    print("  - Wikipedia Deaths in ICE Detention")
    print("    https://en.wikipedia.org/wiki/List_of_deaths_in_ICE_detention")
    print("  - Block Club Chicago (Broadview incidents)")
    print("    https://blockclubchicago.org/")
    print("  - OPB (Oregon incidents)")
    print("    https://www.opb.org/")
    print("  - CPR News (Colorado incidents)")
    print("    https://www.cpr.org/")
