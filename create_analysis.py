"""
ICE Violent Incidents Analysis - Direct Data Entry
===================================================
Hardcoded data from comprehensive research to avoid CSV parsing issues.
"""

import pandas as pd
from collections import defaultdict

# Comprehensive incident data compiled from all sources
incidents_data = [
    # Shootings by agents (lethal force)
    {"id": 1, "date": "2025-09-12", "state": "Illinois", "city": "Franklin Park", "type": "shooting", "outcome": "death", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "Silverio Villegas González"},
    {"id": 2, "date": "2025-10-04", "state": "Illinois", "city": "Chicago", "type": "shooting", "outcome": "injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Marimar Martinez"},
    {"id": 3, "date": "2025-10-21", "state": "California", "city": "Los Angeles", "type": "shooting", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "Carlitos Ricardo Parias"},
    {"id": 4, "date": "2025-10-29", "state": "Arizona", "city": "Phoenix", "type": "shooting", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "Jose Garcia-Sorto"},
    {"id": 5, "date": "2025-10-30", "state": "California", "city": "Ontario", "type": "shooting", "outcome": "injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Carlos Jimenez"},
    {"id": 6, "date": "2025-12-11", "state": "Texas", "city": "Starr County", "type": "shooting", "outcome": "death", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "Isaias Sanchez Barboza"},
    {"id": 7, "date": "2025-12-24", "state": "Maryland", "city": "Glen Burnie", "type": "shooting", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "Tiago Alexandre Sousa-Martins"},
    {"id": 8, "date": "2026-01-07", "state": "Minnesota", "city": "Minneapolis", "type": "shooting", "outcome": "death", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Renee Good"},
    {"id": 9, "date": "2026-01-08", "state": "Oregon", "city": "Portland", "type": "shooting", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "Luis David Nino Moncada"},
    {"id": 10, "date": "2026-01-08", "state": "Oregon", "city": "Portland", "type": "shooting", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "Yorlenys Betzabeth Zambrano-Contreras"},
    {"id": 11, "date": "2026-01-14", "state": "Minnesota", "city": "Minneapolis", "type": "shooting", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "Julio Cesar Sosa-Celis"},
    {"id": 12, "date": "2026-01-25", "state": "Minnesota", "city": "Minneapolis", "type": "shooting", "outcome": "injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Alex Jeffrey Pretti"},
    {"id": 23, "date": "2025-06-10", "state": "California", "city": "Los Angeles", "type": "shooting", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "Australian cameraman"},

    # Less lethal incidents - Illinois (Broadview)
    {"id": 13, "date": "2025-09-19", "state": "Illinois", "city": "Broadview", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": True, "protest": True, "victim": "Curtis Evans"},
    {"id": 14, "date": "2025-09-21", "state": "Illinois", "city": "Broadview", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "multiple"},
    {"id": 15, "date": "2025-09-26", "state": "Illinois", "city": "Broadview", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "Brian Rivera"},
    {"id": 16, "date": "2025-09-26", "state": "Illinois", "city": "Broadview", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "Joselyn Walsh"},
    {"id": 17, "date": "2025-09-26", "state": "Illinois", "city": "Broadview", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "Levi Rolles"},
    {"id": 18, "date": "2025-09-26", "state": "Illinois", "city": "Broadview", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": True, "protest": True, "victim": "Bushra Amiwala"},
    {"id": 25, "date": "2025-07-08", "state": "Illinois", "city": "Broadview", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "multiple"},

    # Less lethal incidents - Colorado
    {"id": 19, "date": "2025-10-27", "state": "Colorado", "city": "Durango", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "multiple"},
    {"id": 20, "date": "2025-10-27", "state": "Colorado", "city": "Durango", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "unnamed"},

    # Less lethal incidents - California
    {"id": 21, "date": "2025-06-07", "state": "California", "city": "Los Angeles", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "multiple"},
    {"id": 22, "date": "2025-06-10", "state": "California", "city": "Los Angeles", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "Australian journalist"},
    {"id": 24, "date": "2025-06-15", "state": "California", "city": "Los Angeles", "type": "less_lethal", "outcome": "no_injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Christian Damian Cerno-Camacho"},

    # Less lethal incidents - Oregon
    {"id": 26, "date": "2025-10-02", "state": "Oregon", "city": "Portland", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "Leilani Payne"},
    {"id": 27, "date": "2025-12-11", "state": "Oregon", "city": "Portland", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "bystanders"},
    {"id": 28, "date": "2025-09-24", "state": "Oregon", "city": "Eugene", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "multiple"},

    # Less lethal incidents - New York
    {"id": 29, "date": "2025-10-15", "state": "New York", "city": "Manhattan", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "multiple"},
    {"id": 30, "date": "2025-11-29", "state": "New York", "city": "Manhattan", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "multiple"},

    # Physical force / wrongful detention incidents
    {"id": 31, "date": "2025-09-15", "state": "New York", "city": "Manhattan", "type": "physical_force", "outcome": "no_injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "Monica Moreta-Galarza"},
    {"id": 32, "date": "2025-06-10", "state": "Georgia", "city": "Brookhaven", "type": "less_lethal", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": True, "victim": "multiple"},
    {"id": 33, "date": "2025-09-04", "state": "Georgia", "city": "Ellabell", "type": "mass_raid", "outcome": "no_injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "475 workers"},
    {"id": 34, "date": "2025-05-15", "state": "Florida", "city": "Tallahassee", "type": "mass_raid", "outcome": "no_injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "100+ workers"},
    {"id": 35, "date": "2025-05-10", "state": "Massachusetts", "city": "Worcester", "type": "physical_force", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "multiple"},
    {"id": 36, "date": "2025-11-06", "state": "Massachusetts", "city": "Fitchburg", "type": "physical_force", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "family with toddler"},
    {"id": 37, "date": "2025-05-20", "state": "Massachusetts", "city": "Nantucket", "type": "mass_raid", "outcome": "no_injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "40 immigrants"},
    {"id": 38, "date": "2025-08-15", "state": "Massachusetts", "city": "Saugus", "type": "physical_force", "outcome": "no_injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "3 landscapers"},

    # Wrongful US citizen detentions
    {"id": 39, "date": "2025-12-10", "state": "Minnesota", "city": "Minneapolis", "type": "wrongful_detention", "outcome": "no_injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Mubashir Khalif Hussen"},
    {"id": 47, "date": "2025-06-01", "state": "Alabama", "city": "coastal", "type": "wrongful_detention", "outcome": "no_injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Leonardo Garcia Venegas"},
    {"id": 48, "date": "2025-07-15", "state": "California", "city": "Camarillo", "type": "wrongful_detention", "outcome": "injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "George Retes"},
    {"id": 49, "date": "2025-07-01", "state": "California", "city": "Van Nuys", "type": "physical_force", "outcome": "injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Daniel Montenegro"},
    {"id": 50, "date": "2025-06-20", "state": "California", "city": "Los Angeles", "type": "wrongful_detention", "outcome": "no_injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Andrea Velez"},
    {"id": 51, "date": "2025-08-01", "state": "California", "city": "unknown", "type": "physical_force", "outcome": "injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Rafie Ollah Shouhed"},
    {"id": 52, "date": "2025-10-10", "state": "Illinois", "city": "Chicago", "type": "wrongful_detention", "outcome": "injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Debbie Brockman"},
    {"id": 53, "date": "2025-05-15", "state": "Florida", "city": "unknown", "type": "wrongful_detention", "outcome": "no_injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Juan Carlos Lopez Gomez"},
    {"id": 54, "date": "2025-06-15", "state": "California", "city": "unknown", "type": "wrongful_detention", "outcome": "injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Adrian Andrew Martinez"},
    {"id": 55, "date": "2025-06-18", "state": "Louisiana", "city": "Angola", "type": "wrongful_deportation", "outcome": "no_injury", "perpetrator": "agent", "us_citizen": True, "protest": False, "victim": "Chanthila Souvannarath"},

    # Virginia and North Carolina
    {"id": 40, "date": "2025-11-15", "state": "North Carolina", "city": "Charlotte", "type": "physical_force", "outcome": "no_injury", "perpetrator": "civilian", "us_citizen": False, "protest": False, "victim": "agents (vehicle assault)"},
    {"id": 41, "date": "2025-04-20", "state": "Virginia", "city": "Charlottesville", "type": "courthouse_raid", "outcome": "no_injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "2 men"},

    # Attacks on agents/facilities
    {"id": 42, "date": "2025-07-04", "state": "Texas", "city": "Alvarado", "type": "facility_attack", "outcome": "injury", "perpetrator": "civilian", "us_citizen": True, "protest": False, "victim": "1 police officer"},
    {"id": 43, "date": "2025-09-24", "state": "Texas", "city": "Dallas", "type": "facility_attack", "outcome": "death", "perpetrator": "civilian", "us_citizen": False, "protest": False, "victim": "2 detainees killed"},
    {"id": 44, "date": "2025-07-07", "state": "Texas", "city": "McAllen", "type": "facility_attack", "outcome": "injury", "perpetrator": "civilian", "us_citizen": True, "protest": False, "victim": "3 Border Patrol agents"},
    {"id": 45, "date": "2025-07-20", "state": "California", "city": "Camarillo", "type": "shooting_at_agents", "outcome": "no_injury", "perpetrator": "civilian", "us_citizen": False, "protest": True, "victim": "none"},
    {"id": 46, "date": "2025-11-10", "state": "Illinois", "city": "Chicago", "type": "shooting_at_agents", "outcome": "no_injury", "perpetrator": "civilian", "us_citizen": False, "protest": False, "victim": "none"},

    # Oregon raids
    {"id": 56, "date": "2025-10-15", "state": "Oregon", "city": "Gresham", "type": "physical_force", "outcome": "injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "mother and baby"},
    {"id": 57, "date": "2025-10-28", "state": "Oregon", "city": "Woodburn", "type": "mass_raid", "outcome": "no_injury", "perpetrator": "agent", "us_citizen": False, "protest": False, "victim": "30+ farm workers"},

    # Deaths in custody (2025)
    {"id": 58, "date": "2025-01-29", "state": "Arizona", "city": "Phoenix", "type": "death_in_custody", "outcome": "death", "perpetrator": "detention", "us_citizen": False, "protest": False, "victim": "Serawit Gezahegn Dejene"},
    {"id": 59, "date": "2025-08-31", "state": "Arizona", "city": "Mesa", "type": "death_in_custody", "outcome": "death", "perpetrator": "detention", "us_citizen": False, "protest": False, "victim": "Lorenzo Antonio Batrez Vargas"},
    {"id": 60, "date": "2025-01-23", "state": "Florida", "city": "Hialeah", "type": "death_in_custody", "outcome": "death", "perpetrator": "detention", "us_citizen": False, "protest": False, "victim": "Genry Donaldo Ruiz-Guillen"},
    {"id": 61, "date": "2025-06-07", "state": "Georgia", "city": "Americus", "type": "death_in_custody", "outcome": "death", "perpetrator": "detention", "us_citizen": False, "protest": False, "victim": "Jesus Molina-Veya"},
    {"id": 62, "date": "2025-08-05", "state": "Pennsylvania", "city": "Philipsburg", "type": "death_in_custody", "outcome": "death", "perpetrator": "detention", "us_citizen": False, "protest": False, "victim": "Chaofeng Ge"},
    {"id": 63, "date": "2025-01-05", "state": "Texas", "city": "Conroe", "type": "death_in_custody", "outcome": "death", "perpetrator": "detention", "us_citizen": False, "protest": False, "victim": "Luis Gustavo Nunez Caceres"},
    {"id": 64, "date": "2025-01-06", "state": "California", "city": "Calexico", "type": "death_in_custody", "outcome": "death", "perpetrator": "detention", "us_citizen": False, "protest": False, "victim": "Luis Beltran Yanez-Cruz"},
]

# Convert to DataFrame
df = pd.DataFrame(incidents_data)

# Summary by state
def summarize_by_state(df):
    summary = []
    for state in df['state'].unique():
        state_df = df[df['state'] == state]
        summary.append({
            'state': state,
            'total_incidents': len(state_df),
            'shootings_by_agents': len(state_df[(state_df['type'] == 'shooting') & (state_df['perpetrator'] == 'agent')]),
            'shootings_at_agents': len(state_df[(state_df['type'].isin(['shooting_at_agents', 'facility_attack'])) & (state_df['perpetrator'] == 'civilian')]),
            'less_lethal': len(state_df[state_df['type'] == 'less_lethal']),
            'physical_force': len(state_df[state_df['type'].isin(['physical_force', 'mass_raid', 'courthouse_raid', 'wrongful_detention', 'wrongful_deportation'])]),
            'deaths_in_custody': len(state_df[state_df['type'] == 'death_in_custody']),
            'total_deaths': len(state_df[state_df['outcome'] == 'death']),
            'total_injuries': len(state_df[state_df['outcome'] == 'injury']),
            'us_citizens_affected': len(state_df[state_df['us_citizen'] == True]),
            'protest_related': len(state_df[state_df['protest'] == True]),
        })
    return pd.DataFrame(summary).sort_values('total_incidents', ascending=False)

# Run analysis
print("=" * 80)
print("ICE VIOLENT INCIDENTS COMPREHENSIVE ANALYSIS")
print("=" * 80)

print(f"\nTotal incidents documented: {len(df)}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")

# Overall stats
print("\n" + "-" * 50)
print("OVERALL STATISTICS")
print("-" * 50)
print(f"Total deaths: {len(df[df['outcome'] == 'death'])}")
print(f"Total injuries: {len(df[df['outcome'] == 'injury'])}")
print(f"Agent-perpetrated incidents: {len(df[df['perpetrator'] == 'agent'])}")
print(f"Civilian-perpetrated incidents: {len(df[df['perpetrator'] == 'civilian'])}")
print(f"US citizens affected: {len(df[df['us_citizen'] == True])}")
print(f"Protest-related incidents: {len(df[df['protest'] == True])}")

# By incident type
print("\n" + "-" * 50)
print("INCIDENTS BY TYPE")
print("-" * 50)
type_counts = df.groupby('type').size().sort_values(ascending=False)
for t, count in type_counts.items():
    deaths = len(df[(df['type'] == t) & (df['outcome'] == 'death')])
    print(f"  {t}: {count} incidents ({deaths} deaths)")

# By state
print("\n" + "-" * 50)
print("INCIDENTS BY STATE")
print("-" * 50)
state_summary = summarize_by_state(df)
print(state_summary.to_string(index=False))

# Save outputs
state_summary.to_csv('violence_summary_by_state.csv', index=False)
df.to_csv('all_incidents_clean.csv', index=False)

print("\n\nSaved: violence_summary_by_state.csv, all_incidents_clean.csv")

# Print for quick reference
print("\n" + "=" * 80)
print("STATE RANKINGS BY TOTAL INCIDENTS")
print("=" * 80)
for i, row in state_summary.head(15).iterrows():
    print(f"{row['state']:20s} | Total: {row['total_incidents']:3d} | Shootings: {row['shootings_by_agents']:2d} | Deaths: {row['total_deaths']:2d} | US Citizens: {row['us_citizens_affected']:2d}")
