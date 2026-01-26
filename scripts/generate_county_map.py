import json
import os
from collections import Counter
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# City to County mapping (FIPS codes and county names)
# Format: "City, State": ("County Name", "State FIPS", "County FIPS")
CITY_TO_COUNTY = {
    # Illinois
    "Broadview, Illinois": ("Cook County", "17", "031"),
    "Chicago, Illinois": ("Cook County", "17", "031"),
    "Cicero, Illinois": ("Cook County", "17", "031"),
    "Evanston, Illinois": ("Cook County", "17", "031"),

    # Minnesota
    "Minneapolis, Minnesota": ("Hennepin County", "27", "053"),
    "Minneapolis (Federal Building), Minnesota": ("Hennepin County", "27", "053"),
    "St. Paul, Minnesota": ("Ramsey County", "27", "123"),

    # California
    "Los Angeles, California": ("Los Angeles County", "06", "037"),
    "Los Angeles (Grand Park), California": ("Los Angeles County", "06", "037"),
    "Northridge, Los Angeles, California": ("Los Angeles County", "06", "037"),
    "Van Nuys, California": ("Los Angeles County", "06", "037"),
    "Paramount, California": ("Los Angeles County", "06", "037"),
    "San Francisco, California": ("San Francisco County", "06", "075"),
    "Oakland, California": ("Alameda County", "06", "001"),
    "Santa Ana, California": ("Orange County", "06", "059"),
    "Anaheim, California": ("Orange County", "06", "059"),
    "San Diego, California": ("San Diego County", "06", "073"),
    "Sacramento, California": ("Sacramento County", "06", "067"),
    "San Jose, California": ("Santa Clara County", "06", "085"),
    "Fresno, California": ("Fresno County", "06", "019"),
    "Bakersfield, California": ("Kern County", "06", "029"),
    "Riverside, California": ("Riverside County", "06", "065"),
    "Long Beach, California": ("Los Angeles County", "06", "037"),
    "Pasadena, California": ("Los Angeles County", "06", "037"),
    "Glendale, California": ("Los Angeles County", "06", "037"),
    "Santa Monica, California": ("Los Angeles County", "06", "037"),
    "Pomona, California": ("Los Angeles County", "06", "037"),
    "Torrance, California": ("Los Angeles County", "06", "037"),
    "Santa Clarita, California": ("Los Angeles County", "06", "037"),
    "Irvine, California": ("Orange County", "06", "059"),

    # Oregon
    "Portland, Oregon": ("Multnomah County", "41", "051"),
    "Eugene, Oregon": ("Lane County", "41", "039"),

    # Texas
    "Houston, Texas": ("Harris County", "48", "201"),
    "Austin, Texas": ("Travis County", "48", "453"),
    "Dallas, Texas": ("Dallas County", "48", "113"),
    "San Antonio, Texas": ("Bexar County", "48", "029"),
    "Fort Worth, Texas": ("Tarrant County", "48", "439"),
    "El Paso, Texas": ("El Paso County", "48", "141"),
    "Alvarado, Texas": ("Johnson County", "48", "251"),
    "Plano, Texas": ("Collin County", "48", "085"),
    "Arlington, Texas": ("Tarrant County", "48", "439"),
    "Sarita, Texas": ("Kenedy County", "48", "261"),
    "Rio Grande City, Texas": ("Starr County", "48", "427"),

    # New York
    "New York, New York": ("New York County", "36", "061"),
    "New York (Downtown Manhattan), New York": ("New York County", "36", "061"),
    "New York City, New York": ("New York County", "36", "061"),
    "Brooklyn, New York": ("Kings County", "36", "047"),
    "Queens, New York": ("Queens County", "36", "081"),
    "Bronx, New York": ("Bronx County", "36", "005"),
    "Staten Island, New York": ("Richmond County", "36", "085"),
    "Buffalo, New York": ("Erie County", "36", "029"),

    # Washington
    "Seattle, Washington": ("King County", "53", "033"),
    "Tacoma, Washington": ("Pierce County", "53", "053"),

    # New Jersey
    "Newark, New Jersey": ("Essex County", "34", "013"),
    "Jersey City, New Jersey": ("Hudson County", "34", "017"),
    "Elizabeth, New Jersey": ("Union County", "34", "039"),
    "Paterson, New Jersey": ("Passaic County", "34", "031"),

    # Colorado
    "Denver, Colorado": ("Denver County", "08", "031"),
    "Aurora, Colorado": ("Arapahoe County", "08", "005"),
    "Colorado Springs, Colorado": ("El Paso County", "08", "041"),

    # Georgia
    "Atlanta, Georgia": ("Fulton County", "13", "121"),
    "Savannah, Georgia": ("Chatham County", "13", "051"),

    # Florida
    "Miami, Florida": ("Miami-Dade County", "12", "086"),
    "Orlando, Florida": ("Orange County", "12", "095"),
    "Tampa, Florida": ("Hillsborough County", "12", "057"),
    "Jacksonville, Florida": ("Duval County", "12", "031"),

    # Massachusetts
    "Boston, Massachusetts": ("Suffolk County", "25", "025"),
    "Cambridge, Massachusetts": ("Middlesex County", "25", "017"),

    # Louisiana
    "New Orleans, Louisiana": ("Orleans Parish", "22", "071"),
    "Baton Rouge, Louisiana": ("East Baton Rouge Parish", "22", "033"),

    # Oklahoma
    "Oklahoma City, Oklahoma": ("Oklahoma County", "40", "109"),
    "Tulsa, Oklahoma": ("Tulsa County", "40", "143"),

    # North Carolina
    "Charlotte, North Carolina": ("Mecklenburg County", "37", "119"),
    "Raleigh, North Carolina": ("Wake County", "37", "183"),

    # Maryland
    "Baltimore, Maryland": ("Baltimore City", "24", "510"),

    # Wisconsin
    "Milwaukee, Wisconsin": ("Milwaukee County", "55", "079"),
    "Madison, Wisconsin": ("Dane County", "55", "025"),

    # Alabama
    "Birmingham, Alabama": ("Jefferson County", "01", "073"),

    # Nevada
    "Las Vegas, Nevada": ("Clark County", "32", "003"),
    "Reno, Nevada": ("Washoe County", "32", "031"),

    # Arizona
    "Phoenix, Arizona": ("Maricopa County", "04", "013"),
    "Tucson, Arizona": ("Pima County", "04", "019"),

    # Pennsylvania
    "Philadelphia, Pennsylvania": ("Philadelphia County", "42", "101"),
    "Pittsburgh, Pennsylvania": ("Allegheny County", "42", "003"),

    # District of Columbia
    "Washington, District of Columbia": ("District of Columbia", "11", "001"),

    # Rhode Island
    "Providence, Rhode Island": ("Providence County", "44", "007"),

    # Iowa
    "Des Moines, Iowa": ("Polk County", "19", "153"),

    # Michigan
    "Detroit, Michigan": ("Wayne County", "26", "163"),
    "Ann Arbor, Michigan": ("Washtenaw County", "26", "161"),

    # South Carolina
    "Charleston, South Carolina": ("Charleston County", "45", "019"),
    "Columbia, South Carolina": ("Richland County", "45", "079"),

    # Utah
    "Salt Lake City, Utah": ("Salt Lake County", "49", "035"),

    # Additional mappings for unmapped cities
    # Illinois
    "Elgin, Illinois": ("Kane County", "17", "089"),
    "Chicago and surrounding area, Illinois": ("Cook County", "17", "031"),

    # Minnesota
    "Minneapolis-St. Paul Airport, Minnesota": ("Hennepin County", "27", "053"),
    "Statewide, Minnesota": ("Hennepin County", "27", "053"),  # Default to largest metro

    # New York
    "Manhattan (SoHo/Canal St), New York": ("New York County", "36", "061"),
    "Manhattan (Canal Street), New York": ("New York County", "36", "061"),
    "Manhattan (26 Federal Plaza), New York": ("New York County", "36", "061"),

    # California
    "Ontario, California": ("San Bernardino County", "06", "071"),
    "Dublin, California": ("Alameda County", "06", "001"),
    "Los Angeles area, California": ("Los Angeles County", "06", "037"),
    "McCain Valley (near Mexico border), California": ("San Diego County", "06", "073"),
    "Camarillo/Oxnard Plain, Ventura County, California": ("Ventura County", "06", "111"),
    "Camarillo area, California": ("Ventura County", "06", "111"),

    # Colorado
    "Durango, Colorado": ("La Plata County", "08", "067"),
    "Durango (ICE field office), Colorado": ("La Plata County", "08", "067"),
    "Aurora/Denver, Colorado": ("Denver County", "08", "031"),

    # Georgia
    "DeKalb County (Atlanta area), Georgia": ("DeKalb County", "13", "089"),
    "Brookhaven, Georgia": ("DeKalb County", "13", "089"),

    # Louisiana
    "Baton Rouge / Honduras, Louisiana": ("East Baton Rouge Parish", "22", "033"),
    "New Orleans area, Louisiana": ("Orleans Parish", "22", "071"),
    "Angola (Camp 57), Louisiana": ("West Feliciana Parish", "22", "125"),

    # Maryland
    "Laurel, Maryland": ("Prince George's County", "24", "033"),

    # Massachusetts
    "Medford, Massachusetts": ("Middlesex County", "25", "017"),

    # North Carolina
    "Salisbury, North Carolina": ("Rowan County", "37", "159"),

    # South Carolina
    "Greenville, South Carolina": ("Greenville County", "45", "045"),

    # Florida
    "Riviera Beach, Florida": ("Palm Beach County", "12", "099"),

    # Alabama
    "Foley, Alabama": ("Baldwin County", "01", "003"),

    # Arizona
    "Phoenix/Peoria, Arizona": ("Maricopa County", "04", "013"),

    # Texas
    "McAllen, Texas": ("Hidalgo County", "48", "215"),
    "Rio Grande / CBP Checkpoint, Texas": ("Hidalgo County", "48", "215"),

    # Washington
    "Spokane, Washington": ("Spokane County", "53", "063"),
    "SeaTac/Tacoma, Washington": ("King County", "53", "033"),
}

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
unmapped_cities = []
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

            # Try exact match first
            if city_state in CITY_TO_COUNTY:
                county_info = CITY_TO_COUNTY[city_state]
                fips = county_info[1] + county_info[2]
                county_counts[fips] += 1
                total_mapped += 1
            else:
                # Try partial match (city name only)
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
                if not matched:
                    unmapped_cities.append(city_state)

print(f"Mapped incidents: {total_mapped}")
print(f"Unmapped cities: {len(unmapped_cities)}")
if unmapped_cities:
    print("Unmapped:", set(unmapped_cities))

# Load sanctuary reference for state classification
with open('data/reference/sanctuary_jurisdictions.json', 'r') as f:
    ref = json.load(f)
sanctuary_states = set()
for state, data in ref.get('states', {}).items():
    if data.get('classification') == 'sanctuary':
        sanctuary_states.add(state)

# Load US counties GeoJSON
county_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
print("Loading county boundaries...")
counties = gpd.read_file(county_url)

# Add FIPS column and incident counts
counties['FIPS'] = counties['id']
counties['incident_count'] = counties['FIPS'].map(lambda x: county_counts.get(x, 0))

# Filter to continental US (exclude Alaska and Hawaii by FIPS prefix)
continental = counties[~counties['FIPS'].str.startswith(('02', '15', '72'))]

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(18, 12))

# Custom colormap
colors = ['#f7f7f7', '#fee5d9', '#fcbba1', '#fc9272', '#fb6a4a', '#de2d26', '#a50f15', '#67000d']
cmap = LinearSegmentedColormap.from_list('incidents', colors, N=256)

max_incidents = max(county_counts.values()) if county_counts else 1

# Plot all counties (base layer - light gray)
continental.plot(
    ax=ax,
    color='#f0f0f0',
    edgecolor='#cccccc',
    linewidth=0.1
)

# Plot counties with incidents
counties_with_data = continental[continental['incident_count'] > 0]
if not counties_with_data.empty:
    counties_with_data.plot(
        column='incident_count',
        ax=ax,
        cmap=cmap,
        edgecolor='black',
        linewidth=0.3,
        vmin=0,
        vmax=max_incidents
    )

# Add labels for counties with incidents
for idx, row in counties_with_data.iterrows():
    centroid = row.geometry.centroid
    count = row['incident_count']
    ax.annotate(
        str(count),
        xy=(centroid.x, centroid.y),
        fontsize=7,
        ha='center',
        va='center',
        fontweight='bold',
        color='black'
    )

# Title
counties_with_incidents = len(county_counts)
ax.set_title(
    f'Non-Immigrant Incidents by County\n'
    f'(Protesters, Journalists, Bystanders, Officers, US Citizens)\n'
    f'{total_mapped} incidents across {counties_with_incidents} counties',
    fontsize=14, fontweight='bold'
)

ax.set_axis_off()

# Legend
legend_elements = [
    mpatches.Patch(facecolor='#67000d', edgecolor='black', label=f'High incidents ({max_incidents})'),
    mpatches.Patch(facecolor='#f0f0f0', edgecolor='#cccccc', label='Zero incidents'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=max_incidents))
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.03, pad=0.02, aspect=40)
cbar.set_label('Number of Incidents', fontsize=11)

plt.tight_layout()
plt.savefig('non_immigrant_incident_map_county.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"\nMap saved to: non_immigrant_incident_map_county.png")

# Print county breakdown
print("\nTop counties by incident count:")
# Get county names from data
county_name_map = {}
for idx, row in counties.iterrows():
    county_name_map[row['FIPS']] = row.get('NAME', row['FIPS'])

for fips, count in sorted(county_counts.items(), key=lambda x: -x[1])[:15]:
    matching = counties[counties['FIPS'] == fips]
    if not matching.empty:
        name = matching.iloc[0].get('NAME', fips)
        print(f"  {name}: {count}")
    else:
        print(f"  FIPS {fips}: {count}")

plt.close()
