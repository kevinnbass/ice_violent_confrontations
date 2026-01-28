"""
Generate bar chart of ICE violent confrontations adjusted by unauthorized immigrant population.
Shows rates per 100,000 unauthorized immigrants for top counties.
"""
import json
import os
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# County FIPS to city name mapping
FIPS_TO_CITY = {
    '17031': 'Chicago',
    '06037': 'Los Angeles',
    '27053': 'Minneapolis',
    '36061': 'New York City',
    '41051': 'Portland',
    '06075': 'San Francisco',
    '53033': 'Seattle',
    '34013': 'Newark',
    '08031': 'Denver',
}

# Unauthorized immigrant population estimates by county (thousands)
# Sources: Migration Policy Institute, Pew Research Center, Census Bureau estimates
# These are estimates for metro areas containing these counties
UNAUTHORIZED_POP = {
    '17031': 380000,   # Cook County (Chicago metro) - ~380k
    '06037': 1000000,  # Los Angeles County - ~1M
    '27053': 34000,    # Hennepin County (Minneapolis) - ~34k
    '36061': 575000,   # New York County (Manhattan) - part of NYC ~575k for Manhattan's share
    '41051': 33000,    # Multnomah County (Portland) - ~33k
    '06075': 42000,    # San Francisco County - ~42k
    '53033': 125000,   # King County (Seattle) - ~125k
    '34013': 68000,    # Essex County (Newark) - ~68k
    '08031': 50000,    # Denver County - ~50k
}

# Total US unauthorized immigrant population estimate: ~11 million
# Total counties: 3,143
TOTAL_US_UNAUTHORIZED = 11000000

# Import city-to-county mapping
exec(open('scripts/generate_county_map.py').read().split('# Load incident data')[0])

# Load incident data
incident_files = [
    'data/incidents/tier1_deaths_in_custody.json',
    'data/incidents/tier2_shootings.json',
    'data/incidents/tier2_less_lethal.json',
    'data/incidents/tier3_incidents.json',
    'data/incidents/tier4_incidents.json'
]

non_immigrant_categories = ['us_citizen', 'bystander', 'officer', 'protester', 'journalist', 'legal_resident']

county_counts = Counter()
total_mapped = 0

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
            city = inc.get('city', '')
            state = inc.get('state', '')
            city_state = f"{city}, {state}"

            if city_state in CITY_TO_COUNTY:
                county_info = CITY_TO_COUNTY[city_state]
                fips = county_info[1] + county_info[2]
                county_counts[fips] += 1
                total_mapped += 1
            else:
                # Try partial match
                matched = False
                city_lower = city.lower().split(',')[0].split('(')[0].strip()
                for key, value in CITY_TO_COUNTY.items():
                    key_city = key.split(',')[0].lower().strip()
                    key_state = key.split(',')[1].strip() if ',' in key else ''
                    if city_lower == key_city and state == key_state:
                        fips = value[1] + value[2]
                        county_counts[fips] += 1
                        total_mapped += 1
                        matched = True
                        break

print(f"Total non-immigrant incidents mapped: {total_mapped}")

# Calculate rates per 100,000 unauthorized immigrants
# Only for counties with 4+ incidents (matching the filtered map)
MIN_INCIDENTS = 4
filtered_fips = [fips for fips, count in county_counts.items() if count >= MIN_INCIDENTS and fips in UNAUTHORIZED_POP]

# Calculate rates
rates = {}
for fips in filtered_fips:
    count = county_counts[fips]
    pop = UNAUTHORIZED_POP[fips]
    rate = (count / pop) * 100000
    rates[fips] = {
        'city': FIPS_TO_CITY.get(fips, fips),
        'incidents': count,
        'population': pop,
        'rate': rate
    }

# Calculate "All Other Counties" rate
top_fips_set = set(filtered_fips)
other_incidents = sum(count for fips, count in county_counts.items() if fips not in top_fips_set)
other_pop = TOTAL_US_UNAUTHORIZED - sum(UNAUTHORIZED_POP.get(fips, 0) for fips in filtered_fips)
other_rate = (other_incidents / other_pop) * 100000 if other_pop > 0 else 0

print(f"\nCounties with {MIN_INCIDENTS}+ incidents:")
for fips in sorted(rates.keys(), key=lambda x: -rates[x]['rate']):
    r = rates[fips]
    print(f"  {r['city']}: {r['incidents']} incidents, {r['rate']:.1f} per 100k")

print(f"\nAll Other Counties: {other_incidents} incidents, {other_rate:.2f} per 100k")

# Sort by rate descending
sorted_data = sorted(rates.values(), key=lambda x: -x['rate'])

# Add "All Other Counties"
sorted_data.append({
    'city': 'All Other\nCounties',
    'incidents': other_incidents,
    'population': other_pop,
    'rate': other_rate
})

# Create figure
fig, ax = plt.subplots(figsize=(14, 10))

# Bar colors - gradient from dark red (high) to light red (low)
base_color = '#c0392b'  # Dark red
colors = [base_color] * (len(sorted_data) - 1) + ['#7f8c8d']  # Gray for "Other"

# Create bars
cities = [d['city'] for d in sorted_data]
rates_list = [d['rate'] for d in sorted_data]
incidents_list = [d['incidents'] for d in sorted_data]

y_pos = np.arange(len(cities))
bars = ax.barh(y_pos, rates_list, color=colors, edgecolor='black', linewidth=0.5, height=0.7)

# Add rate labels inside bars
for i, (bar, rate) in enumerate(zip(bars, rates_list)):
    # Position text inside bar
    if rate > 5:
        ax.text(rate - 0.5, bar.get_y() + bar.get_height()/2,
                f'{rate:.1f}', va='center', ha='right', fontsize=14,
                fontweight='bold', color='white')
    else:
        ax.text(rate + 0.5, bar.get_y() + bar.get_height()/2,
                f'{rate:.2f}' if rate < 1 else f'{rate:.1f}',
                va='center', ha='left', fontsize=14, fontweight='bold', color='black')

# Add incident count labels on right
for i, (bar, incidents) in enumerate(zip(bars, incidents_list)):
    ax.text(max(rates_list) * 1.02, bar.get_y() + bar.get_height()/2,
            f'({incidents} incidents)', va='center', ha='left', fontsize=11, color='#666666')

# Add national baseline line
baseline = other_rate
ax.axvline(x=baseline, color='#333333', linestyle='--', linewidth=1.5, zorder=0)
ax.text(baseline + 0.3, len(cities) - 0.5, 'National baseline\n(excl. top 9)',
        fontsize=10, color='#333333', va='top', ha='left')

# Add callout for Minneapolis comparison
if len(sorted_data) > 1 and sorted_data[0]['city'] == 'Minneapolis':
    minneapolis_rate = sorted_data[0]['rate']
    multiplier = int(round(minneapolis_rate / other_rate))

    # Draw callout box
    callout_x = minneapolis_rate * 0.75
    callout_y = 2.5

    num_other_counties = 3143 - len(filtered_fips)  # Total US counties minus top counties
    ax.annotate(
        f'Minneapolis rate is\n{multiplier}x higher than\nany of the other {num_other_counties:,}\ncounties outside the top {len(filtered_fips)}',
        xy=(minneapolis_rate - 2, 0),
        xytext=(callout_x, callout_y),
        fontsize=12,
        fontweight='bold',
        color='#8b0000',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#fff5f5', edgecolor='#8b0000', linewidth=2),
        arrowprops=dict(arrowstyle='->', color='#8b0000', lw=2),
        ha='center'
    )

# Styling
ax.set_yticks(y_pos)
ax.set_yticklabels(cities, fontsize=12)
ax.invert_yaxis()  # Highest at top
ax.set_xlabel('Violent Confrontations per 100,000 Unauthorized Immigrants', fontsize=13, fontweight='bold')
ax.set_xlim(0, max(rates_list) * 1.15)

# Title
ax.set_title(
    'ICE Violent Confrontations Adjusted by Unauthorized Immigrant Population\n'
    '(Protesters, Journalists, Bystanders, Officers, US Citizens)',
    fontsize=16, fontweight='bold', pad=20
)

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
plt.savefig('ice_confrontations_adjusted_by_population.png', dpi=150, bbox_inches='tight', facecolor='white')
print(f"\nChart saved to: ice_confrontations_adjusted_by_population.png")
plt.close()
