import json
import os
from collections import Counter
import matplotlib.pyplot as plt

# Load incident data - non-immigrant only
incident_files = [
    'data/incidents/tier1_deaths_in_custody.json',
    'data/incidents/tier2_shootings.json',
    'data/incidents/tier2_less_lethal.json',
    'data/incidents/tier3_incidents.json',
    'data/incidents/tier4_incidents.json'
]

non_immigrant_categories = ['us_citizen', 'bystander', 'officer', 'protester', 'journalist', 'legal_resident']

# Load sanctuary reference
with open('data/reference/sanctuary_jurisdictions.json', 'r') as f:
    ref = json.load(f)

sanctuary_states = set()
for state, data in ref.get('states', {}).items():
    if data.get('classification') == 'sanctuary':
        sanctuary_states.add(state)

# Count incidents
total_non_immigrant = 0
# Top 8 counties with 4+ incidents (Denver dropped below threshold)
top_counties = {'17031', '06037', '27053', '36061', '41051', '06075', '53033', '34013'}
NUM_TOP_COUNTIES = len(top_counties)
TOTAL_US_COUNTIES = 3143
NUM_OTHER_COUNTIES = TOTAL_US_COUNTIES - NUM_TOP_COUNTIES
top_count = 0
other_count = 0

sanctuary_count = 0
non_sanctuary_count = 0

# City to county FIPS mapping (simplified)
exec(open('scripts/generate_county_map.py').read().split('# Load incident data')[0])

for filepath in incident_files:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        incidents = json.load(f)

    for inc in incidents:
        victim_cat = inc.get('victim_category', '').lower()
        is_us_citizen = inc.get('us_citizen', False)
        protest_related = inc.get('protest_related', False)

        is_non_immigrant = (
            victim_cat in non_immigrant_categories or
            is_us_citizen or
            protest_related or
            'citizen' in victim_cat or
            'protest' in victim_cat
        )

        if is_non_immigrant:
            total_non_immigrant += 1
            state = inc.get('state', '')
            city = inc.get('city', '')
            city_state = f"{city}, {state}"

            # Check if in top counties
            fips = None
            if city_state in CITY_TO_COUNTY:
                fips = CITY_TO_COUNTY[city_state][1] + CITY_TO_COUNTY[city_state][2]
            else:
                # Try partial match
                city_lower = city.lower().split(',')[0].split('(')[0].strip()
                for key, value in CITY_TO_COUNTY.items():
                    key_city = key.split(',')[0].lower().strip()
                    key_state = key.split(',')[1].strip() if ',' in key else ''
                    if city_lower == key_city and state == key_state:
                        fips = value[1] + value[2]
                        break

            if fips and fips in top_counties:
                top_count += 1
            else:
                other_count += 1

            # Check sanctuary status
            if state in sanctuary_states:
                sanctuary_count += 1
            else:
                non_sanctuary_count += 1

print(f"Total non-immigrant incidents: {total_non_immigrant}")
print(f"Top {NUM_TOP_COUNTIES} counties: {top_count}")
print(f"Other {NUM_OTHER_COUNTIES:,} counties: {other_count}")
print(f"Sanctuary states: {sanctuary_count}")
print(f"Non-sanctuary states: {non_sanctuary_count}")

# Create visualization: pie chart + stats panel
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Pie chart: Top counties vs rest (show counts, not percentages)
colors1 = ['#1a5276', '#c0392b']  # Blue for non-cooperating, red for others
wedges, texts = ax1.pie([top_count, other_count],
        labels=[f'Top {NUM_TOP_COUNTIES}\nNon-Cooperating\nCounties', f'All Other\nCounties\n({NUM_OTHER_COUNTIES:,})'],
        colors=colors1,
        explode=(0.05, 0),
        startangle=90,
        textprops={'fontsize': 18})

# Add count labels inside wedges
ax1.text(-0.3, -0.2, str(top_count), fontsize=24, fontweight='bold', color='white', ha='center', va='center')
ax1.text(0.4, 0.3, str(other_count), fontsize=24, fontweight='bold', color='white', ha='center', va='center')

# Title
ax1.set_title('Violent Confrontations in\nNon-Cooperating Jurisdictions', fontsize=26, fontweight='bold')

# Stats panel instead of second pie chart
ax2.axis('off')

# Calculate the multiplier
incidents_per_top = top_count / NUM_TOP_COUNTIES
incidents_per_other = other_count / NUM_OTHER_COUNTIES
multiplier = int(round(incidents_per_top / incidents_per_other)) if incidents_per_other > 0 else 0

# Add stats text with dynamic values
ax2.text(0.5, 0.7, f'{multiplier}x', fontsize=108, fontweight='bold', color='#1a5276',
         ha='center', va='center', transform=ax2.transAxes)
ax2.text(0.5, 0.45, 'more likely', fontsize=36, fontweight='bold', color='#333333',
         ha='center', va='center', transform=ax2.transAxes)
ax2.text(0.5, 0.20, f'A county among the top {NUM_TOP_COUNTIES} non-cooperating\njurisdictions is {multiplier}x more likely to have a\nviolent confrontation with ICE\nthan any of the other {NUM_OTHER_COUNTIES:,} counties.',
         fontsize=24, color='#333333', ha='center', va='center', transform=ax2.transAxes)

plt.tight_layout()
plt.savefig('non_immigrant_pie_charts.png', dpi=150, bbox_inches='tight', facecolor='white')
print(f"\nVisualization saved to: non_immigrant_pie_charts.png")
plt.close()
