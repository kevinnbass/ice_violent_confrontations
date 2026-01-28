"""
ICE Violent Incidents Data Collection Framework
================================================
This script provides tools for:
1. Loading and analyzing existing violent incidents data
2. Merging with ICE arrest data to calculate violence ratios by state
3. Adding new incidents from news sources

Data Sources:
- The Trace: https://www.thetrace.org/2025/12/immigration-ice-shootings-guns-tracker/
- House Oversight: https://oversightdemocrats.house.gov/immigration-dashboard
- NBC News: https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202
- Deportation Data Project: https://deportationdata.org/data/ice.html
"""

import pandas as pd
from datetime import datetime
from pathlib import Path

# Incident type categories
INCIDENT_TYPES = [
    'shooting',           # Firearm discharged
    'less_lethal',        # Rubber bullets, pepper balls, tasers
    'gunpoint',           # Held at gunpoint without shooting
    'physical_force',     # Physical altercation, pushing, tackling
    'vehicle_ramming',    # Vehicle used as weapon (by either party)
    'death_in_custody',   # Death while in ICE detention
    'protest_violence',   # Violence during protests
    'other'
]

# Outcome categories
OUTCOMES = ['death', 'injury', 'no_injury', 'unknown']

# Agency categories
AGENCIES = ['ICE', 'CBP', 'Border Patrol', 'DHS', 'Unknown']


def load_incidents(filepath='ice_violent_incidents_schema.csv'):
    """Load existing incidents data."""
    return pd.read_csv(filepath, parse_dates=['date'])


def add_incident(df, incident_dict):
    """
    Add a new incident to the dataframe.

    Required fields:
    - date: YYYY-MM-DD format
    - state: Full state name
    - city: City name
    - agency: ICE, CBP, etc.
    - incident_type: From INCIDENT_TYPES
    - outcome: death, injury, no_injury
    - source_url: News article URL
    """
    new_id = df['incident_id'].max() + 1 if len(df) > 0 else 1
    incident_dict['incident_id'] = new_id
    return pd.concat([df, pd.DataFrame([incident_dict])], ignore_index=True)


def calculate_violence_by_state(incidents_df):
    """
    Calculate violence metrics by state.
    Returns counts of incidents, deaths, and injuries per state.
    """
    state_stats = incidents_df.groupby('state').agg({
        'incident_id': 'count',
        'outcome': lambda x: (x == 'death').sum()
    }).rename(columns={
        'incident_id': 'total_incidents',
        'outcome': 'deaths'
    })

    # Calculate injuries separately
    state_stats['injuries'] = incidents_df[
        incidents_df['outcome'] == 'injury'
    ].groupby('state').size()
    state_stats['injuries'] = state_stats['injuries'].fillna(0).astype(int)

    return state_stats.reset_index()


def merge_with_arrests(violence_df, arrests_df, state_col='state', arrests_col='arrests'):
    """
    Merge violence data with arrests data to calculate:
    - Incidents per 1000 arrests
    - Deaths per 10000 arrests

    arrests_df should have columns: state, arrests (or specify column names)
    """
    merged = violence_df.merge(arrests_df, on='state', how='outer')
    merged = merged.fillna(0)

    # Calculate ratios (per 1000 arrests)
    merged['incidents_per_1000_arrests'] = (
        merged['total_incidents'] / merged[arrests_col] * 1000
    ).replace([float('inf')], 0)

    merged['deaths_per_10000_arrests'] = (
        merged['deaths'] / merged[arrests_col] * 10000
    ).replace([float('inf')], 0)

    return merged


# Example ICE arrests data by state (Feb-Oct 2025)
# You should replace this with actual data from enforcementdashboard.com
SAMPLE_ARRESTS_DATA = {
    'state': [
        'California', 'Texas', 'Florida', 'New York', 'Illinois',
        'Arizona', 'Georgia', 'North Carolina', 'New Jersey', 'Colorado',
        'Minnesota', 'Maryland', 'Oregon', 'Pennsylvania', 'Virginia'
    ],
    'arrests': [
        15000, 25000, 12000, 8000, 6000,
        7000, 5000, 4500, 4000, 3500,
        2000, 2500, 1500, 3000, 3500
    ]
}


def generate_report():
    """Generate a summary report of violence metrics by state."""
    # Load data
    incidents = load_incidents()
    arrests = pd.DataFrame(SAMPLE_ARRESTS_DATA)

    # Calculate state-level violence
    violence_by_state = calculate_violence_by_state(incidents)

    # Merge with arrests
    merged = merge_with_arrests(violence_by_state, arrests)

    # Sort by incidents per arrest
    merged = merged.sort_values('incidents_per_1000_arrests', ascending=False)

    print("\n" + "="*60)
    print("ICE VIOLENT INCIDENTS ANALYSIS BY STATE")
    print("="*60)
    print(f"\nData period: {incidents['date'].min()} to {incidents['date'].max()}")
    print(f"Total incidents: {len(incidents)}")
    print(f"Total deaths: {(incidents['outcome'] == 'death').sum()}")
    print(f"Total injuries: {(incidents['outcome'] == 'injury').sum()}")

    print("\n" + "-"*60)
    print("INCIDENTS PER 1000 ARRESTS BY STATE")
    print("-"*60)
    print(merged[['state', 'total_incidents', 'arrests',
                  'incidents_per_1000_arrests']].to_string(index=False))

    return merged


if __name__ == '__main__':
    report = generate_report()

    # Save to CSV
    report.to_csv('violence_arrest_ratio_by_state.csv', index=False)
    print("\nReport saved to: violence_arrest_ratio_by_state.csv")
