import json
import os
import re

# Location extraction rules based on facility/hospital names
FACILITY_LOCATIONS = {
    # Florida
    "HCA Kendall Hospital, Miami": ("Miami", "Florida"),
    "Broward Transitional Center, Pompano Beach": ("Pompano Beach", "Florida"),
    "Federal Bureau of Prisons FDC Miami": ("Miami", "Florida"),
    "Krome Service Processing Center": ("Miami", "Florida"),
    "HCA Kendall Florida Hospital, Miami": ("Miami", "Florida"),
    "Larkin Community Hospital Palm Springs": ("Hialeah", "Florida"),
    "South Florida Detention Facility": ("Pompano Beach", "Florida"),
    "Krome North Service Processing Center": ("Miami", "Florida"),
    "Everglades Detention Facility": ("Miami", "Florida"),
    "Florida Detention Center": ("Miami", "Florida"),

    # Texas
    "Long Term Acute Care Hospital, El Paso": ("El Paso", "Texas"),
    "Karnes County Immigration Processing Center": ("Karnes City", "Texas"),
    "Methodist Hospital Northeast, Live Oak": ("Live Oak", "Texas"),
    "Camp East Montana": ("El Paso", "Texas"),
    "Camp East Montana, Fort Bliss": ("El Paso", "Texas"),
    "Joe Corley Processing Center": ("Conroe", "Texas"),
    "South Texas Family Residential Center (Dilley)": ("Dilley", "Texas"),
    "South Texas Family Residential Center": ("Dilley", "Texas"),

    # Georgia
    "Stewart Detention Center, Lumpkin": ("Lumpkin", "Georgia"),
    "Phoebe Sumter Hospital, Americus": ("Americus", "Georgia"),
    "In transit from Lowndes County Jail to Stewart Detention Center": ("Valdosta", "Georgia"),
    "Stewart Detention Center (died during transport)": ("Lumpkin", "Georgia"),
    "Stewart Detention Center": ("Lumpkin", "Georgia"),

    # Pennsylvania
    "Moshannon Valley Processing Center": ("Philipsburg", "Pennsylvania"),
    "Adams County Detention Center": ("Gettysburg", "Pennsylvania"),
    "Federal Detention Center (FDC) Philadelphia": ("Philadelphia", "Pennsylvania"),

    # Arizona
    "Central Arizona Correctional Complex, Florence": ("Florence", "Arizona"),
    "Mountain Vista Medical Center, Mesa": ("Mesa", "Arizona"),
    "Eloy Detention Center": ("Eloy", "Arizona"),
    "Banner Desert Medical Center": ("Mesa", "Arizona"),
    "Banner University Medical Center Phoenix": ("Phoenix", "Arizona"),

    # California
    "Victor Valley Global Medical Center, Victorville": ("Victorville", "California"),
    "Imperial Regional Detention Center": ("Calexico", "California"),
    "Adelanto ICE Processing Center": ("Adelanto", "California"),

    # Missouri
    "Phelps County Jail, Rolla": ("Rolla", "Missouri"),

    # Michigan
    "North Lake Processing Center, Baldwin": ("Baldwin", "Michigan"),

    # New Jersey
    "Delaney Hall detention facility": ("Newark", "New Jersey"),
    "Delaney Hall Detention Facility": ("Newark", "New Jersey"),

    # Puerto Rico
    "Centro Medico Hospital, San Juan": ("San Juan", "Puerto Rico"),

    # Mississippi
    "Adams County Detention Center, Natchez": ("Natchez", "Mississippi"),
    "Merit Health Natchez": ("Natchez", "Mississippi"),

    # New York
    "Nassau County Correctional Center, East Meadow": ("East Meadow", "New York"),

    # Louisiana
    "Louisiana State Penitentiary Camp J (Angola)": ("Angola", "Louisiana"),
    "LaSalle Detention Facility": ("Jena", "Louisiana"),

    # Colorado
    "Aurora ICE Processing Center": ("Aurora", "Colorado"),

    # New Mexico
    "Torrance County Detention Facility": ("Estancia", "New Mexico"),
}

# State-specific default locations for "Statewide" entries
STATEWIDE_DEFAULTS = {
    "Florida": ("Miami", "Florida"),  # Largest city, most ICE activity
    "Massachusetts": ("Boston", "Massachusetts"),
    "Alabama": ("Montgomery", "Alabama"),
    "Iowa": ("Des Moines", "Iowa"),
    "Minnesota": ("Minneapolis", "Minnesota"),
}

incident_files = [
    'data/incidents/tier1_deaths_in_custody.json',
    'data/incidents/tier2_shootings.json',
    'data/incidents/tier2_less_lethal.json',
    'data/incidents/tier3_incidents.json',
    'data/incidents/tier4_incidents.json'
]

updated_count = 0
total_missing = 0

for filepath in incident_files:
    if not os.path.exists(filepath):
        continue

    with open(filepath, 'r') as f:
        incidents = json.load(f)

    modified = False
    for inc in incidents:
        city = inc.get('city', '')
        state = inc.get('state', '')

        # Skip if already has city
        if city and not city.startswith('Statewide') and city not in ['Unknown', '', 'Multiple', 'Nationwide', 'Border region']:
            continue

        total_missing += 1
        new_city = None
        new_state = state

        # Try facility name
        facility = inc.get('facility', '')
        if facility:
            for fac_key, (fac_city, fac_state) in FACILITY_LOCATIONS.items():
                if fac_key.lower() in facility.lower():
                    new_city = fac_city
                    if not state or state == 'Unknown':
                        new_state = fac_state
                    break

        # Try hospital name
        if not new_city:
            hospital = inc.get('hospital', '')
            if hospital:
                for fac_key, (fac_city, fac_state) in FACILITY_LOCATIONS.items():
                    if fac_key.lower() in hospital.lower():
                        new_city = fac_city
                        if not state or state == 'Unknown':
                            new_state = fac_state
                        break

        # Try statewide default
        if not new_city and city.startswith('Statewide') and state in STATEWIDE_DEFAULTS:
            new_city, new_state = STATEWIDE_DEFAULTS[state]

        # Extract from notes for specific patterns
        if not new_city:
            notes = inc.get('notes', '')
            # Look for "at [Facility], [City]" pattern
            match = re.search(r'at ([^,]+),\s*(\w+(?:\s+\w+)?)\s*(?:County|Parish)?', notes)
            if match:
                potential_city = match.group(2).strip()
                if potential_city and len(potential_city) > 2:
                    new_city = potential_city

        if new_city:
            inc['city'] = new_city
            if new_state and new_state != state:
                inc['state'] = new_state
            updated_count += 1
            modified = True
            print(f"Updated {inc['id']}: {city} -> {new_city}, {state} -> {new_state}")

    if modified:
        with open(filepath, 'w') as f:
            json.dump(incidents, f, indent=2)

print(f"\n{'='*60}")
print(f"Total incidents with missing city: {total_missing}")
print(f"Successfully updated: {updated_count}")
print(f"Still missing: {total_missing - updated_count}")
