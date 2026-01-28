"""
Merge Logic for ice_arrests
===========================
Consolidated logic for creating merged datasets.
"""

import pandas as pd
import numpy as np
from typing import Optional

from ..data.loader import (
    load_incidents,
    load_incidents_deduplicated,
    load_arrests_by_state,
    load_state_classifications,
    load_violent_incidents_legacy,
)


def create_merged_dataset(
    use_legacy_incidents: bool = True,
    deduplicate: bool = True
) -> pd.DataFrame:
    """
    Create the final merged dataset with all sources documented.

    Combines:
    - Arrest data by state
    - State enforcement classifications
    - Violence incident aggregations

    Args:
        use_legacy_incidents: If True, use VIOLENT_INCIDENTS from
            COMPREHENSIVE_SOURCED_DATABASE for backward compatibility.
            If False, use tiered incidents database.
        deduplicate: If True (default), use canonical_incident_id for
            deduplication to avoid double-counting cross-tier duplicates.
            If False, count all records (legacy behavior).

    Returns:
        DataFrame with merged data including violence ratios.
    """
    # Load incident data
    if use_legacy_incidents:
        incidents = load_violent_incidents_legacy()
    else:
        if deduplicate:
            incidents = load_incidents_deduplicated(dedupe_strategy="primary_only")
        else:
            incidents = load_incidents()

    incidents_df = pd.DataFrame(incidents)

    # Aggregate incidents by state
    if len(incidents_df) > 0:
        # Use canonical_incident_id for counting if available, otherwise fall back to id
        incidents_df['count_key'] = incidents_df.apply(
            lambda r: r.get('canonical_incident_id') or r['id'],
            axis=1
        )

        state_violence = incidents_df.groupby('state').agg({
            'count_key': 'nunique',  # Count UNIQUE incidents
        }).rename(columns={'count_key': 'total_violent_incidents'})

        # Count by outcome
        state_violence['deaths'] = incidents_df[
            incidents_df['outcome'] == 'death'
        ].groupby('state').size()

        state_violence['injuries'] = incidents_df[
            incidents_df['outcome'] == 'injury'
        ].groupby('state').size()

        # Count by type
        state_violence['shootings_by_agents'] = incidents_df[
            (incidents_df['type'] == 'shooting') &
            (incidents_df['perpetrator'] == 'agent')
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
    else:
        state_violence = pd.DataFrame(columns=[
            'state', 'total_violent_incidents', 'deaths', 'injuries',
            'shootings_by_agents', 'less_lethal_incidents', 'deaths_in_custody',
            'us_citizens_affected', 'protest_related'
        ])

    # Load and transform arrests data
    arrests_data = load_arrests_by_state()
    arrests_rows = []
    for state, data in arrests_data.items():
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

    # Load and transform classification data
    classifications = load_state_classifications()
    class_rows = []
    for state, data in classifications.items():
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


def aggregate_by_classification(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Aggregate data by sanctuary classification type.

    Args:
        df: Optional pre-computed merged dataset.
            If None, creates it using create_merged_dataset().

    Returns:
        DataFrame with aggregated statistics by classification.
    """
    if df is None:
        df = create_merged_dataset()

    results = []
    for classification in ['sanctuary', 'aggressive_anti_sanctuary', 'anti_sanctuary', 'neutral']:
        subset = df[df['enforcement_classification'] == classification]
        if len(subset) == 0:
            continue

        total_arrests = subset['arrests'].sum()
        total_incidents = subset['total_violent_incidents'].sum()
        total_deaths = subset['deaths'].sum()
        avg_ratio = total_incidents / total_arrests * 1000 if total_arrests > 0 else 0

        results.append({
            'classification': classification,
            'states_count': len(subset),
            'total_arrests': total_arrests,
            'total_incidents': total_incidents,
            'total_deaths': total_deaths,
            'avg_violence_ratio': round(avg_ratio, 3),
        })

    return pd.DataFrame(results)


def create_state_summary() -> pd.DataFrame:
    """
    Create a state-level summary combining arrests and violence data.

    Returns:
        DataFrame with state-level summary statistics.
    """
    return create_merged_dataset(use_legacy_incidents=True)
