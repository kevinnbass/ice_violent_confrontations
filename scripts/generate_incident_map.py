import json
import os
from collections import Counter
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

# Load incident data
incident_files = [
    'data/incidents/tier1_deaths_in_custody.json',
    'data/incidents/tier2_shootings.json',
    'data/incidents/tier2_less_lethal.json',
    'data/incidents/tier3_incidents.json',
    'data/incidents/tier4_incidents.json'
]

# Non-immigrant categories
non_immigrant_categories = ['us_citizen', 'bystander', 'officer', 'protester', 'journalist', 'legal_resident']

state_counts = Counter()
total_non_immigrant = 0

for filepath in incident_files:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r') as f:
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
            'protest' in victim_cat or
            'bystander' in victim_cat or
            'journalist' in victim_cat
        )

        if is_non_immigrant:
            state = inc.get('state', 'Unknown')
            if state not in ['Unknown', 'Multiple']:
                state_counts[state] += 1
                total_non_immigrant += 1

# Load sanctuary reference data
with open('data/reference/sanctuary_jurisdictions.json', 'r') as f:
    ref = json.load(f)
sanctuary_states = set()
for state, data in ref.get('states', {}).items():
    if data.get('classification') == 'sanctuary':
        sanctuary_states.add(state)

print(f"Sanctuary states: {sanctuary_states}")
print(f"Total non-immigrant incidents: {total_non_immigrant}")
print(f"States with incidents: {len(state_counts)}")

# Load US states shapefile
url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
try:
    us_states = gpd.read_file(url)
except:
    # Fallback to local or alternative
    us_states = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    us_states = us_states[us_states['continent'] == 'North America']

# State name mapping for matching
state_name_map = {
    'District of Columbia': 'District of Columbia',
}

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(15, 10))

# Filter to continental US + add state counts
us_states['incident_count'] = us_states['name'].map(lambda x: state_counts.get(x, 0))
us_states['is_sanctuary'] = us_states['name'].map(lambda x: x in sanctuary_states)

# Exclude Alaska, Hawaii, Puerto Rico for cleaner continental view
continental = us_states[~us_states['name'].isin(['Alaska', 'Hawaii', 'Puerto Rico'])]

# Custom colormap (white to dark red)
colors = ['#ffffff', '#fee5d9', '#fcbba1', '#fc9272', '#fb6a4a', '#de2d26', '#a50f15', '#67000d']
cmap = LinearSegmentedColormap.from_list('incidents', colors, N=256)

# Get max for normalization
max_incidents = max(state_counts.values()) if state_counts else 1

# Plot states
continental.plot(
    column='incident_count',
    ax=ax,
    legend=False,
    cmap=cmap,
    edgecolor='black',
    linewidth=0.5,
    vmin=0,
    vmax=max_incidents
)

# Add state labels with counts
for idx, row in continental.iterrows():
    centroid = row.geometry.centroid
    state_name = row['name']
    count = state_counts.get(state_name, 0)
    is_sanctuary = state_name in sanctuary_states

    # Adjust label positions for certain states
    x_offset = 0
    y_offset = 0
    if state_name == 'Florida':
        x_offset = 0.5
    elif state_name == 'Michigan':
        y_offset = -0.5
    elif state_name == 'Louisiana':
        y_offset = -0.3

    label_x = centroid.x + x_offset
    label_y = centroid.y + y_offset

    if count > 0:
        if is_sanctuary:
            # Sanctuary state with incidents
            ax.annotate(f'S\n{count}', xy=(label_x, label_y),
                       fontsize=9, ha='center', va='center', fontweight='bold',
                       color='black')
        else:
            # Non-sanctuary with incidents
            ax.annotate(f'{count}', xy=(label_x, label_y),
                       fontsize=9, ha='center', va='center', fontweight='bold',
                       color='black')
    elif is_sanctuary:
        # Sanctuary state with no incidents
        ax.annotate('S', xy=(label_x, label_y),
                   fontsize=8, ha='center', va='center', fontweight='bold',
                   color='gray')

# Title
states_with_incidents = len([s for s, c in state_counts.items() if c > 0])
ax.set_title(
    f'Non-Immigrant Incidents\n'
    f'(Protesters, Journalists, Bystanders, Officers, US Citizens)\n'
    f'All Tiers Combined (Raw Incident Count)\n'
    f'{total_non_immigrant} total incidents across {states_with_incidents} states\n'
    f'"S" = Sanctuary State',
    fontsize=12, fontweight='bold'
)

# Remove axes
ax.set_axis_off()

# Legend
legend_elements = [
    mpatches.Patch(facecolor='#67000d', edgecolor='black', label=f'High incidents ({max_incidents})'),
    mpatches.Patch(facecolor='white', edgecolor='black', label='Zero incidents'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=max_incidents))
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.03, pad=0.05, aspect=30)
cbar.set_label('Number of Incidents', fontsize=10)

plt.tight_layout()
plt.savefig('non_immigrant_incident_map_single.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"\nMap saved to: non_immigrant_incident_map_single.png")
plt.close()
