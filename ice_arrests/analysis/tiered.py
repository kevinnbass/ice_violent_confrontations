"""
Tiered Analysis for ice_arrests
===============================
Confidence-adjusted analysis using data source tiers.
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple

from ..data.loader import (
    load_incidents,
    load_incidents_deduplicated,
    get_incidents_by_tier,
    load_arrests_by_state,
    load_state_classifications,
    infer_victim_category,
)


def analyze_by_state_and_tier(deduplicate: bool = True) -> Dict:
    """
    Analyze incidents by state, broken down by source tier.

    Args:
        deduplicate: If True (default), only count primary records to avoid
            double-counting cross-tier duplicates.

    Returns:
        Dictionary with state-level aggregations by tier.
    """
    if deduplicate:
        all_incidents = load_incidents_deduplicated(dedupe_strategy="primary_only")
    else:
        all_incidents = load_incidents()

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

        if incident.get('outcome') == 'death' or 'death' in incident.get('incident_type', ''):
            state_data[state]['total_deaths'] += 1

        if incident.get('outcome') == 'injury' or incident.get('injury'):
            state_data[state]['total_injuries'] += 1

        if incident.get('us_citizen') == True:
            state_data[state]['us_citizens'] += 1

        incident_type = incident.get('incident_type', 'unknown')
        state_data[state]['incidents_by_type'][incident_type] += 1

    return dict(state_data)


def calculate_confidence_adjusted_ratios() -> pd.DataFrame:
    """
    Calculate violence/arrest ratios with confidence levels.

    Only uses Tier 1 + Tier 2 data for ratio calculations.

    Returns:
        DataFrame with confidence-adjusted ratios per state.
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

    # Load arrests and classifications
    arrests_data = load_arrests_by_state()
    classifications = load_state_classifications()

    # Calculate ratios for states with arrest data
    for state, arrest_info in arrests_data.items():
        arrests = arrest_info['arrests']
        counts = state_counts.get(state, {})

        total_incidents = counts.get('total_high_confidence', 0)
        deaths = counts.get('deaths_tier1', 0)

        # Determine confidence level
        if deaths > 0 and total_incidents > 3:
            confidence = "MEDIUM_HIGH"
        elif deaths > 0 or total_incidents > 0:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        # Calculate ratio
        if arrests > 0:
            ratio = total_incidents / arrests * 1000
            death_ratio = deaths / arrests * 10000
        else:
            ratio = None
            death_ratio = None

        # Get classification
        classification = classifications.get(state, {}).get('classification', 'unknown')

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


def analyze_by_classification_with_confidence() -> pd.DataFrame:
    """
    Aggregate analysis by sanctuary classification.

    Uses only Tier 1 + 2 data and reports confidence levels.

    Returns:
        DataFrame with classification-level aggregations.
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


def analyze_by_victim_category(deduplicate: bool = True) -> Dict:
    """
    Analyze incidents by who was affected.

    Args:
        deduplicate: If True (default), only count primary records to avoid
            double-counting cross-tier duplicates.

    Returns:
        Dictionary with category-level aggregations.
    """
    if deduplicate:
        all_incidents = load_incidents_deduplicated(dedupe_strategy="primary_only")
    else:
        all_incidents = load_incidents()

    categories = {}
    for incident in all_incidents:
        cat = infer_victim_category(incident)
        if cat not in categories:
            categories[cat] = {
                'count': 0,
                'deaths': 0,
                'injuries': 0,
                'incidents': []
            }
        categories[cat]['count'] += 1
        categories[cat]['incidents'].append(incident)

        if incident.get('outcome') == 'death' or 'death' in incident.get('incident_type', ''):
            categories[cat]['deaths'] += 1
        if incident.get('outcome') == 'injury' or incident.get('injury'):
            categories[cat]['injuries'] += 1

    return categories


def get_tier_summary(deduplicate: bool = True) -> Dict:
    """
    Get summary statistics by tier.

    Args:
        deduplicate: If True (default), only count primary records to avoid
            double-counting cross-tier duplicates.

    Returns:
        Dictionary with tier-level summary.
    """
    if deduplicate:
        all_incidents = load_incidents_deduplicated(dedupe_strategy="primary_only")
    else:
        all_incidents = load_incidents()

    summary = {}
    for tier in [1, 2, 3, 4]:
        tier_incidents = [i for i in all_incidents if i.get('source_tier') == tier]

        types = defaultdict(int)
        for i in tier_incidents:
            t = i.get('incident_type', 'unknown')
            types[t] += 1

        deaths = sum(1 for i in tier_incidents
                    if i.get('outcome') == 'death' or 'death' in i.get('incident_type', ''))
        injuries = sum(1 for i in tier_incidents
                      if i.get('outcome') == 'injury' or i.get('injury'))
        us_citizens = sum(1 for i in tier_incidents if i.get('us_citizen') == True)

        summary[tier] = {
            'total': len(tier_incidents),
            'by_type': dict(types),
            'deaths': deaths,
            'injuries': injuries,
            'us_citizens': us_citizens,
        }

    return summary
