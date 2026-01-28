"""
ICE Violent Incidents Analysis Script
=====================================
Analyzes comprehensive violent incidents data and calculates state-level metrics.

Data sources compiled:
- The Trace ICE Shootings Tracker
- House Oversight Democrats Immigration Dashboard
- NBC News / Marshall Project incident lists
- ProPublica US Citizens detained investigation
- ACLU reports and lawsuits
- Local news archives (OPB, Block Club Chicago, etc.)
- Wikipedia incident lists
"""

import pandas as pd
import numpy as np
from collections import defaultdict

def load_data(filepath='ice_violent_incidents_comprehensive.csv'):
    """Load the comprehensive incidents data."""
    df = pd.read_csv(filepath)
    # Convert date column, handling partial dates
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    return df

def summarize_by_state(df):
    """
    Create comprehensive state-level summary of all incidents.
    """
    summary = defaultdict(lambda: {
        'total_incidents': 0,
        'shootings_by_agents': 0,
        'shootings_at_agents': 0,
        'less_lethal_incidents': 0,
        'physical_force_incidents': 0,
        'deaths_in_custody': 0,
        'wrongful_detentions': 0,
        'protest_related': 0,
        'us_citizens_affected': 0,
        'total_deaths': 0,
        'total_injuries': 0,
        'agent_perpetrated': 0,
        'civilian_perpetrated': 0
    })

    for _, row in df.iterrows():
        state = row['state']
        if pd.isna(state):
            continue

        summary[state]['total_incidents'] += 1

        # Categorize by incident type
        incident_type = str(row['incident_type']).lower()
        if incident_type == 'shooting':
            if str(row['perpetrator']).lower() == 'agent':
                summary[state]['shootings_by_agents'] += 1
            else:
                summary[state]['shootings_at_agents'] += 1
        elif incident_type == 'less_lethal':
            summary[state]['less_lethal_incidents'] += 1
        elif incident_type in ['physical_force', 'wrongful_detention', 'courthouse_raid', 'mass_raid']:
            summary[state]['physical_force_incidents'] += 1
        elif incident_type == 'death_in_custody':
            summary[state]['deaths_in_custody'] += 1

        if 'wrongful' in incident_type:
            summary[state]['wrongful_detentions'] += 1

        # Track protest-related
        if str(row['protest_related']).lower() == 'yes':
            summary[state]['protest_related'] += 1

        # Track US citizens
        if str(row['us_citizen_involved']).lower() == 'yes':
            summary[state]['us_citizens_affected'] += 1

        # Track outcomes
        outcome = str(row['outcome']).lower()
        if outcome == 'death':
            summary[state]['total_deaths'] += 1
        elif outcome == 'injury':
            summary[state]['total_injuries'] += 1

        # Track perpetrator
        perpetrator = str(row['perpetrator']).lower()
        if perpetrator == 'agent':
            summary[state]['agent_perpetrated'] += 1
        elif perpetrator == 'civilian':
            summary[state]['civilian_perpetrated'] += 1

    return pd.DataFrame.from_dict(summary, orient='index').reset_index().rename(columns={'index': 'state'})

def calculate_violence_ratios(summary_df, arrests_df):
    """
    Merge violence summary with arrests data to calculate ratios.

    arrests_df should have columns: state, arrests
    """
    merged = summary_df.merge(arrests_df, on='state', how='outer')
    merged = merged.fillna(0)

    # Calculate various ratios per 1000 arrests
    if 'arrests' in merged.columns:
        merged['incidents_per_1000_arrests'] = np.where(
            merged['arrests'] > 0,
            merged['total_incidents'] / merged['arrests'] * 1000,
            0
        )
        merged['agent_violence_per_1000'] = np.where(
            merged['arrests'] > 0,
            merged['agent_perpetrated'] / merged['arrests'] * 1000,
            0
        )
        merged['shootings_per_10000'] = np.where(
            merged['arrests'] > 0,
            merged['shootings_by_agents'] / merged['arrests'] * 10000,
            0
        )

    return merged.sort_values('total_incidents', ascending=False)

def incident_type_breakdown(df):
    """Breakdown of incidents by type across all states."""
    type_counts = df.groupby('incident_type').agg({
        'incident_id': 'count',
        'outcome': lambda x: (x == 'death').sum()
    }).rename(columns={'incident_id': 'count', 'outcome': 'deaths'})

    return type_counts.sort_values('count', ascending=False)

def generate_full_report(df):
    """Generate comprehensive report."""
    print("=" * 80)
    print("ICE VIOLENT INCIDENTS COMPREHENSIVE ANALYSIS")
    print("=" * 80)

    print(f"\nData coverage: {df['date'].min()} to {df['date'].max()}")
    print(f"Total incidents documented: {len(df)}")

    # Overall statistics
    print("\n" + "-" * 40)
    print("OVERALL STATISTICS")
    print("-" * 40)

    deaths = (df['outcome'] == 'death').sum()
    injuries = (df['outcome'] == 'injury').sum()
    agent_perp = (df['perpetrator'] == 'agent').sum()
    civilian_perp = (df['perpetrator'] == 'civilian').sum()
    us_citizens = (df['us_citizen_involved'] == 'yes').sum()
    protest = (df['protest_related'] == 'yes').sum()

    print(f"Total deaths: {deaths}")
    print(f"Total injuries: {injuries}")
    print(f"Agent-perpetrated incidents: {agent_perp}")
    print(f"Civilian-perpetrated incidents: {civilian_perp}")
    print(f"US citizens affected: {us_citizens}")
    print(f"Protest-related incidents: {protest}")

    # Incident type breakdown
    print("\n" + "-" * 40)
    print("INCIDENTS BY TYPE")
    print("-" * 40)
    type_breakdown = incident_type_breakdown(df)
    print(type_breakdown.to_string())

    # State summary
    print("\n" + "-" * 40)
    print("INCIDENTS BY STATE (Top 15)")
    print("-" * 40)
    state_summary = summarize_by_state(df)
    top_states = state_summary.nlargest(15, 'total_incidents')[
        ['state', 'total_incidents', 'shootings_by_agents', 'less_lethal_incidents',
         'total_deaths', 'total_injuries', 'us_citizens_affected']
    ]
    print(top_states.to_string(index=False))

    return state_summary

# Sample arrests data - REPLACE WITH YOUR ACTUAL DATA from enforcementdashboard.com
SAMPLE_ARRESTS = pd.DataFrame({
    'state': [
        'California', 'Texas', 'Florida', 'New York', 'Illinois', 'Arizona',
        'Georgia', 'North Carolina', 'New Jersey', 'Colorado', 'Virginia',
        'Massachusetts', 'Minnesota', 'Maryland', 'Oregon', 'Pennsylvania',
        'Louisiana', 'Washington', 'Connecticut', 'Nevada'
    ],
    'arrests': [
        45000, 65000, 35000, 25000, 18000, 22000,
        15000, 12000, 12000, 8000, 10000,
        6000, 4000, 7000, 3500, 9000,
        8000, 5000, 4000, 6000
    ]
})


if __name__ == '__main__':
    # Load data
    df = load_data()

    # Generate report
    state_summary = generate_full_report(df)

    # Calculate ratios with arrests data
    print("\n" + "=" * 80)
    print("VIOLENCE RATIOS (using sample arrests data - replace with actual)")
    print("=" * 80)

    ratios = calculate_violence_ratios(state_summary, SAMPLE_ARRESTS)
    ratio_cols = ['state', 'total_incidents', 'arrests', 'incidents_per_1000_arrests',
                  'shootings_by_agents', 'shootings_per_10000']
    print(ratios[ratio_cols].head(20).to_string(index=False))

    # Save outputs
    state_summary.to_csv('violence_summary_by_state.csv', index=False)
    ratios.to_csv('violence_arrest_ratios.csv', index=False)

    print("\n\nOutputs saved:")
    print("  - violence_summary_by_state.csv")
    print("  - violence_arrest_ratios.csv")
