import json
import os
from collections import Counter
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def make_circular_headshot(image_path, size=50):
    """Load image and apply circular mask"""
    img = Image.open(image_path).convert('RGBA')
    # Make square by cropping to center
    min_dim = min(img.size)
    left = (img.size[0] - min_dim) // 2
    top = (img.size[1] - min_dim) // 2
    img = img.crop((left, top, left + min_dim, top + min_dim))
    img = img.resize((size, size), Image.LANCZOS)

    # Create circular mask
    mask = Image.new('L', (size, size), 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    # Apply mask
    output = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    output.paste(img, (0, 0))
    output.putalpha(mask)

    return np.array(output)

# Headshot file mapping to FIPS codes with mayor names
HEADSHOT_DATA = {
    '17031': {'file': 'assets/headshots/brandon_johnson_headshot.jpg', 'mayor': 'Brandon Johnson', 'city': 'Chicago'},
    '06037': {'file': 'assets/headshots/Mayor Karen Bass - Official Headshot_headshot.jpg', 'mayor': 'Karen Bass', 'city': 'Los Angeles'},
    '27053': {'file': 'assets/headshots/Mayor-Jacob-Frey-1_headshot.jpg', 'mayor': 'Jacob Frey', 'city': 'Minneapolis'},
    '36061': {'file': 'assets/headshots/zohran-mamdani_headshot.jpg', 'mayor': 'Zohran Mamdani', 'city': 'New York City'},
    '41051': {'file': 'assets/headshots/Wilson-DSC_7332-2x1a_headshot.jpg', 'mayor': 'Keith Wilson', 'city': 'Portland'},
    '06075': {'file': 'assets/headshots/daniel_lurie_KeVK6TD_headshot.jpg', 'mayor': 'Daniel Lurie', 'city': 'San Francisco'},
    '53033': {'file': 'assets/headshots/katie_wilson_headshot.png', 'mayor': 'Katie Wilson', 'city': 'Seattle'},
    '34013': {'file': 'assets/headshots/Document_headshot.jpg', 'mayor': 'Ras Baraka', 'city': 'Newark'},
    '08031': {'file': 'assets/headshots/mayor_mike_johnston-headshot_ccb_headshot.jpg', 'mayor': 'Mike Johnston', 'city': 'Denver'},
}

# Import the city-to-county mapping from the main script
exec(open('scripts/generate_county_map.py').read().split('# Load incident data')[0])

# Load incident data - non-immigrant only
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

# Filter to counties with MORE than 3 incidents (4+)
MIN_INCIDENTS = 4
filtered_counts = {k: v for k, v in county_counts.items() if v >= MIN_INCIDENTS}

print(f"Total non-immigrant incidents mapped: {total_mapped}")
print(f"Counties with 4+ incidents: {len(filtered_counts)}")
print(f"Incidents in filtered counties: {sum(filtered_counts.values())}")

# Load county boundaries
print("Loading county boundaries...")
county_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
counties = gpd.read_file(county_url)

counties['FIPS'] = counties['id']
counties['incident_count'] = counties['FIPS'].map(lambda x: filtered_counts.get(x, 0))

# Continental US only
continental = counties[~counties['FIPS'].str.startswith(('02', '15', '72'))]

# Create figure with map and legend panel
fig = plt.figure(figsize=(22, 12))
ax = fig.add_axes([0.02, 0.1, 0.68, 0.85])  # Map on left
ax_legend = fig.add_axes([0.72, 0.15, 0.26, 0.7])  # Legend on right
ax_legend.axis('off')

colors = ['#f7f7f7', '#fee5d9', '#fcbba1', '#fc9272', '#fb6a4a', '#de2d26', '#a50f15', '#67000d']
cmap = LinearSegmentedColormap.from_list('incidents', colors, N=256)

max_incidents = max(filtered_counts.values()) if filtered_counts else 1

# Base layer - all counties light gray
continental.plot(ax=ax, color='#f0f0f0', edgecolor='#cccccc', linewidth=0.1)

# Counties with 4+ incidents
counties_with_data = continental[continental['incident_count'] > 0]
if not counties_with_data.empty:
    counties_with_data.plot(
        column='incident_count',
        ax=ax,
        cmap=cmap,
        edgecolor='black',
        linewidth=0.5,
        vmin=MIN_INCIDENTS,
        vmax=max_incidents
    )

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
    '12086': 'Miami',
    '48141': 'El Paso',
    '06071': 'San Bernardino',
    '48201': 'Houston',
    '37119': 'Charlotte',
    '32003': 'Las Vegas',
}

# Counties where label should be on the left (to avoid overlap)
LABEL_ON_LEFT = {'34013'}  # Newark

# Counties with special positioning
NYC_FIPS = '36061'

# Labels for all filtered counties
for idx, row in counties_with_data.iterrows():
    centroid = row.geometry.centroid
    count = row['incident_count']
    fips = row['FIPS']
    city_name = FIPS_TO_CITY.get(fips, '')

    # Draw city name and count separately (count is bold and larger)
    SEATTLE_FIPS = '53033'
    PORTLAND_FIPS = '41051'
    LA_FIPS = '06037'

    if city_name:
        # Determine base x position
        if fips in LABEL_ON_LEFT:
            # Newark - number on LEFT, then label on right of number
            # Move further left to avoid NYC overlap
            num_x = centroid.x - 4.5
            # Draw count first (leftmost)
            ax.annotate(
                str(count),
                xy=(num_x, centroid.y),
                fontsize=22,
                ha='right',
                va='center',
                fontweight='bold',
                color='black'
            )
            # Draw city name to the right of count
            ax.annotate(
                city_name,
                xy=(num_x + 0.2, centroid.y),
                fontsize=18,
                ha='left',
                va='center',
                fontweight='normal',
                color='#333333',
                style='italic'
            )
        else:
            # All others - label then number to the right
            DENVER_FIPS = '08031'
            if fips == NYC_FIPS:
                base_x = centroid.x + 0.5
            elif fips in [SEATTLE_FIPS, PORTLAND_FIPS, LA_FIPS]:
                base_x = centroid.x + 0.7
            else:
                base_x = centroid.x + 0.5

            # Draw city name
            ax.annotate(
                city_name,
                xy=(base_x, centroid.y),
                fontsize=18,
                ha='left',
                va='center',
                fontweight='normal',
                color='#333333',
                style='italic'
            )
            # Draw count further to the right (increased char_width for larger font)
            char_width = 0.62
            # Denver needs extra offset, NYC needs less offset
            if fips == DENVER_FIPS:
                extra_offset = 0.65
            elif fips == NYC_FIPS:
                extra_offset = -0.3  # Move NYC number closer
            else:
                extra_offset = 0.42
            count_x = base_x + len(city_name) * char_width + extra_offset
            ax.annotate(
                str(count),
                xy=(count_x, centroid.y),
                fontsize=22,
                ha='left',
                va='center',
                fontweight='bold',
                color='black'
            )

# Draw legend with headshots on the right panel
# Sort by incident count descending
sorted_fips = sorted(filtered_counts.keys(), key=lambda x: -filtered_counts[x])

legend_y_start = 0.92
legend_y_spacing = 0.115

for i, fips in enumerate(sorted_fips):
    data = HEADSHOT_DATA.get(fips)
    if not data:
        continue

    y_pos = legend_y_start - (i * legend_y_spacing)
    count = filtered_counts[fips]

    # Draw headshot
    if data['file'] and os.path.exists(data['file']):
        headshot_img = make_circular_headshot(data['file'], size=80)
        imagebox = OffsetImage(headshot_img, zoom=0.85)
        ab = AnnotationBbox(imagebox, (0.08, y_pos), xycoords='axes fraction',
                           frameon=False, box_alignment=(0.5, 0.5))
        ax_legend.add_artist(ab)

    # Draw mayor name (bold) - 2x font size
    ax_legend.text(0.22, y_pos + 0.02, data['mayor'], transform=ax_legend.transAxes,
                  fontsize=22, fontweight='bold', va='center', ha='left')

    # Draw city name and count below - 2x font size, new format
    ax_legend.text(0.22, y_pos - 0.03, f"{data['city']}: {count}", transform=ax_legend.transAxes,
                  fontsize=20, va='center', ha='left', color='#555555')

# Add legend title - 2x font size
ax_legend.text(0.5, 1.02, 'Sanctuary City Mayors', transform=ax_legend.transAxes,
              fontsize=26, fontweight='bold', va='bottom', ha='center')

counties_shown = len(filtered_counts)
incidents_shown = sum(filtered_counts.values())
ax.set_title(
    f'Number of Violent Confrontations With ICE Per County\n'
    f'(Protesters, Journalists, Bystanders, Officers, US Citizens)\n'
    f'All counties with four or more violent confrontations',
    fontsize=21, fontweight='bold'
)

ax.set_axis_off()

sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=MIN_INCIDENTS, vmax=max_incidents))
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.03, pad=0.12, aspect=40)
cbar.set_label('Number of Incidents', fontsize=11)

# Add bottom caption between map and colorbar
fig.text(0.35, 0.20, '63% of all violent confrontations\nwith ICE happen in these 9 counties',
         fontsize=48, fontweight='bold', ha='center', va='center', color='black')

plt.tight_layout()
plt.savefig('non_immigrant_incident_map_county_filtered.png', dpi=150, bbox_inches='tight', facecolor='white')
print(f"\nMap saved to: non_immigrant_incident_map_county_filtered.png")

print("\nCounties with 4+ incidents:")
for fips, count in sorted(filtered_counts.items(), key=lambda x: -x[1]):
    matching = counties[counties['FIPS'] == fips]
    if not matching.empty:
        name = matching.iloc[0].get('NAME', fips)
        print(f"  {name}: {count}")

plt.close()
