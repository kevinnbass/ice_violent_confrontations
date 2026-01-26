#!/usr/bin/env python3
"""Add Round 6 incidents: deportation flights, sensitive locations, military involvement."""

import json
from pathlib import Path
from datetime import datetime

def get_incident_scale(count):
    """Calculate incident scale from affected count."""
    if count is None or count <= 1:
        return "single"
    elif count <= 5:
        return "small"
    elif count <= 50:
        return "medium"
    elif count <= 200:
        return "large"
    else:
        return "mass"

def load_json(filepath):
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    """Save JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_existing_ids(data_dir):
    """Get all existing incident IDs."""
    ids = set()
    for filepath in data_dir.glob('tier*.json'):
        data = load_json(filepath)
        if isinstance(data, list):
            incidents = data
        elif 'incidents' in data:
            incidents = data['incidents']
        elif 'deaths' in data:
            incidents = data['deaths']
        elif 'shootings' in data:
            incidents = data['shootings']
        elif 'less_lethal_incidents' in data:
            incidents = data['less_lethal_incidents']
        else:
            continue
        for inc in incidents:
            ids.add(inc['id'])
    return ids

# New incidents from web searches

# Deportation flight incidents
flight_incidents = [
    {
        "date": "2025-11-13",
        "state": "Unknown",
        "location": "ICE Air flight (airborne)",
        "incident_type": "physical_force",
        "enforcement_granularity": "transport_incident",
        "victim_category": "deportee",
        "victim_name": "6 deportees injured",
        "affected_count": 6,
        "outcome": "injuries from cabin pressure loss",
        "outcome_detail": "Avelo ICE flight declared emergency when cabin lost pressure; plane made rapid descent; 6 of 88 passengers injured with nosebleeds",
        "outcome_category": "injury",
        "source_url": "https://prospect.org/2025/11/17/ice-airs-sloppy-dangerous-deportation-flights/",
        "source_name": "American Prospect",
        "notes": "November 13, 2025: Avelo ICE deportation flight experienced cabin pressure loss mid-flight. The plane made a rapid descent and landed safely. Of 88 people on board, six were injured, primarily experiencing nosebleeds. Flight attendants have raised concerns about deportees being shackled and unable to reach oxygen masks during emergencies.",
    },
    {
        "date": "2025-01-01",
        "date_precision": "month",
        "state": "Unknown",
        "location": "ICE Air flight over Mexico",
        "incident_type": "physical_force",
        "enforcement_granularity": "medical_emergency",
        "victim_category": "child",
        "victim_name": "Unknown child (little girl)",
        "affected_count": 1,
        "outcome": "medical emergency",
        "outcome_detail": "Child collapsed with high fever and ragged breathing during deportation flight over Mexico",
        "outcome_category": "medical_emergency",
        "source_url": "https://www.propublica.org/article/inside-ice-air-deportation-flights",
        "source_name": "ProPublica",
        "notes": "Flight attendants recounted incident where a deportation flight was over Mexico when a little girl collapsed with a high fever and was taking ragged, frantic breaths. Exact date unknown (2025). Highlights concerns about medical care on shackled deportation flights.",
    },
    {
        "date": "2025-01-01",
        "date_precision": "month",
        "state": "Unknown",
        "location": "World Atlantic deportation flight",
        "incident_type": "physical_force",
        "enforcement_granularity": "transport_incident",
        "victim_category": "deportee",
        "victim_name": "Deportees on flight (count unknown)",
        "affected_count": 50,
        "outcome": "emergency landing, evacuation",
        "outcome_detail": "Landing gear broke, wing caught fire, smell of burning rubber. ICE employee noted no emergency training for staff or instructions for evacuating restrained passengers.",
        "outcome_category": "injury",
        "source_url": "https://www.propublica.org/article/inside-ice-air-deportation-flights",
        "source_name": "ProPublica/UW Center for Human Rights",
        "notes": "World Atlantic deportation flight incident: landing gear broke, wing caught fire. ICE employee aboard noted flight attendants made no emergency announcements and simply evacuated themselves. Staff had no training on evacuating restrained passengers. Some flight attendants informally told to save themselves while abandoning deportees.",
    },
]

# Sensitive location incidents
sensitive_location_incidents = [
    {
        "date": "2025-01-26",
        "state": "Unknown",
        "location": "Church (first post-policy raid)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "sensitive_location",
        "victim_category": "undocumented",
        "victim_name": "Wilson (detained at church)",
        "affected_count": 1,
        "outcome": "arrest",
        "outcome_detail": "First reported ICE raid at a church in Trump's second term, occurring 5 days after sensitive locations policy was revoked",
        "outcome_category": "detained",
        "source_url": "https://www.lawfirm4immigrants.com/trump-ice-arrests-churches-schools-courthouse-hospital-protection-removed/",
        "source_name": "LG Law Firm",
        "notes": "Wilson's arrest appears to be the first reported ICE raid at a church in President Trump's second term, coming five days after the administration revoked the sensitive locations protection policy on January 21, 2025.",
    },
    {
        "date": "2025-12-04",
        "state": "Minnesota",
        "city": "Hopkins",
        "location": "St. Gabriel the Archangel Catholic Church",
        "incident_type": "wrongful_deportation",
        "enforcement_granularity": "sensitive_location",
        "victim_category": "undocumented",
        "victim_name": "Francisco Paredes",
        "victim_age": 46,
        "affected_count": 1,
        "outcome": "deported",
        "outcome_detail": "Church maintenance worker deported to Mexico; subsequent ICE surveillance of parish during Mass caused attendance at Spanish Mass to drop by half",
        "outcome_category": "deported",
        "source_url": "https://catholicnewsagency.com/news/268977/minnesota-ice-catholic-church",
        "source_name": "Catholic News Agency",
        "notes": "Francisco Paredes (46), maintenance worker at St. Gabriel the Archangel Catholic Church in Hopkins, Minnesota, was deported to Mexico on December 4, 2025. ICE agents subsequently surveilled the parish during Epiphany Mass. Attendance at the Spanish Mass has dropped by half since the Immaculate Conception, with parishioners expressing fear of churchgoing.",
    },
    {
        "date": "2026-01-15",
        "date_precision": "month",
        "state": "Minnesota",
        "city": "St. Paul",
        "location": "Cities Church",
        "incident_type": "physical_force",
        "enforcement_granularity": "protest_response",
        "victim_category": "protester",
        "victim_name": "Nekima Levy Armstrong and Chauntyll Louisa Allen",
        "affected_count": 3,
        "outcome": "arrests",
        "outcome_detail": "AG Pam Bondi announced arrests of Nekima Levy Armstrong and Chauntyll Louisa Allen (St. Paul School Board member) for allegedly organizing protest at Cities Church under federal FACE Act",
        "outcome_category": "detained",
        "source_url": "https://www.cbsnews.com/minnesota/news/church-protesters-minneapolis-charges-federal-face-act/",
        "source_name": "CBS Minnesota",
        "notes": "Attorney General Pam Bondi announced the arrest of Nekima Levy Armstrong, who allegedly played a key role in organizing a coordinated attack on Cities Church in St. Paul, Minnesota. Also arrested was Chauntyll Louisa Allen, an elected member of the St. Paul School Board. Three total arrested for alleged disruption of church services under federal FACE Act.",
    },
]

# National Guard/military incidents
military_incidents = [
    {
        "date": "2025-06-06",
        "state": "California",
        "city": "Los Angeles",
        "location": "Multiple locations citywide",
        "incident_type": "mass_raid",
        "enforcement_granularity": "military_involvement",
        "victim_category": "multiple",
        "victim_name": "Multiple detained in LA raids",
        "affected_count": 100,
        "outcome": "mass protests, federal intervention",
        "outcome_detail": "ICE raids in LA triggered protests; Trump federalized California National Guard against Gov. Newsom's wishes and deployed Marines to quell protests",
        "outcome_category": "detained",
        "source_url": "https://en.wikipedia.org/wiki/June_2025_Los_Angeles_protests_against_mass_deportation",
        "source_name": "Wikipedia",
        "notes": "June 6, 2025: Protests began in Los Angeles after ICE raided multiple city locations. Trump federalized California's National Guard against Gov. Gavin Newsom's wishes and sent Marines to quell protests. A federal judge later ruled the Guard use violated Posse Comitatus Act. Deployment ended December 31, 2025 after court losses.",
    },
    {
        "date": "2025-09-05",
        "state": "Illinois",
        "city": "Chicago",
        "location": "Chicago metropolitan area",
        "incident_type": "mass_raid",
        "enforcement_granularity": "military_involvement",
        "victim_category": "multiple",
        "victim_name": "Chicago area detainees",
        "affected_count": 50,
        "outcome": "National Guard deployment, lawsuits",
        "outcome_detail": "Trump activated Illinois and Texas National Guards to deploy to Chicago; Governor and Mayor denounced as 'invasion' and sued to block",
        "outcome_category": "detained",
        "source_url": "https://www.wbez.org/public-safety/2025/09/05/faq-national-guard-chicago-donald-trump-ice-deportation-campaign",
        "source_name": "WBEZ Chicago",
        "notes": "September 2025: President Trump activated the Illinois and Texas National Guards to deploy to the Chicago area. The administration said troops would protect federal property and immigration agents. Illinois' governor and Chicago's mayor denounced the deployments as an 'invasion' and filed lawsuits to block them.",
    },
    {
        "date": "2025-08-01",
        "date_precision": "month",
        "state": "Florida",
        "city": "Multiple cities",
        "location": "Miami, Orlando, and 7 other cities",
        "incident_type": "mass_raid",
        "enforcement_granularity": "military_involvement",
        "victim_category": "multiple",
        "victim_name": "Florida detainees",
        "affected_count": 100,
        "outcome": "National Guard support for ICE",
        "outcome_detail": "Florida National Guard troops activated to support ICE officers in nine cities including Miami and Orlando",
        "outcome_category": "detained",
        "source_url": "https://www.csmonitor.com/USA/2025/0805/national-guard-trump-immigration-deportation-states",
        "source_name": "Christian Science Monitor",
        "notes": "August 2025: Florida activated National Guard troops to support ICE officers in nine cities including Miami and Orlando. Part of 20 GOP-led states authorized to support ICE with Title 32 troops. 26 GOP governors had signaled support for using 'every tool at our disposal.'",
    },
    {
        "date": "2025-07-01",
        "date_precision": "month",
        "state": "Texas",
        "city": "Border region",
        "location": "US-Mexico border zone",
        "incident_type": "mass_raid",
        "enforcement_granularity": "military_involvement",
        "victim_category": "multiple",
        "victim_name": "Border crossers",
        "affected_count": 200,
        "outcome": "military patrol with arrest authority",
        "outcome_detail": "At least 7,600 Armed Forces members patrolling border with authority to arrest and detain; over 10,000 troops total (up from 2,500 under Biden)",
        "outcome_category": "detained",
        "source_url": "https://www.ilrc.org/sites/default/files/2025-12/Escalating%20Immigration%20Enforcement%20Practices_1.pdf",
        "source_name": "ILRC",
        "notes": "As of July 2025, border zones were patrolled by at least 7,600 Armed Forces members with authority to arrest and detain immigrants entering without authorization. Over 10,000 troops total along the border, a sharp increase from ~2,500 during Biden administration.",
    },
]

# Deaths to add to Tier 1
new_deaths = [
    {
        "date": "2026-01-15",
        "date_precision": "month",
        "state": "Pennsylvania",
        "city": "Philadelphia",
        "facility": "ICE detention facility",
        "name": "Parady La",
        "age": 46,
        "nationality": "Cambodian",
        "cause_of_death": "Drug withdrawal",
        "incident_type": "death_in_custody",
        "outcome": "death",
        "outcome_detail": "Died from drug withdrawal in ICE detention; family accused ICE of medical neglect, saying he was begging for help in final hours",
        "outcome_category": "death",
        "source_url": "https://en.wikipedia.org/wiki/Deportation_in_the_second_Trump_administration",
        "source_name": "Wikipedia/News reports",
        "notes": "January 2026: Parady La, 46-year-old Cambodian refugee, died from drug withdrawal in ICE detention in Philadelphia. La's family accused ICE of medical neglect, saying they were told he was begging for help in the final hours of his life.",
    },
    {
        "date": "2026-01-03",
        "state": "Montana",
        "city": "Camp East Montana",
        "facility": "Camp East Montana ICE detention",
        "name": "Cuban man (unnamed)",
        "age": 55,
        "nationality": "Cuban",
        "cause_of_death": "Homicide (ruled by medical examiner)",
        "incident_type": "death_in_custody",
        "outcome": "death",
        "outcome_detail": "ICE initially reported suicide; witness said he was choked by guard; medical examiner ruled homicide",
        "outcome_category": "death",
        "source_url": "https://en.wikipedia.org/wiki/Deportation_in_the_second_Trump_administration",
        "source_name": "Wikipedia/News reports",
        "notes": "January 3, 2026: 55-year-old Cuban man died in ICE detention at Camp East Montana. ICE initially said his death was a suicide, but a witness stated he was choked by a guard. Subsequently, the medical examiner ruled the death a homicide.",
    },
]


def main():
    data_dir = Path(__file__).parent.parent / 'data' / 'incidents'
    existing_ids = get_existing_ids(data_dir)

    # Add Tier 1 deaths
    print("[TIER 1: DEATHS IN CUSTODY]")
    tier1_path = data_dir / 'tier1_deaths_in_custody.json'
    tier1_data = load_json(tier1_path)
    # Handle both list and dict formats
    if isinstance(tier1_data, list):
        deaths = tier1_data
        tier1_is_list = True
    else:
        deaths = tier1_data.get('deaths', tier1_data.get('incidents', []))
        tier1_is_list = False

    # Find next ID
    death_ids = [int(d['id'].split('-')[-1]) for d in deaths if d['id'].startswith('T1-D-')]
    next_death_id = max(death_ids) + 1 if death_ids else 1

    added_deaths = 0
    for inc in new_deaths:
        # Check for duplicate by name/date
        is_dupe = False
        for existing in deaths:
            if (existing.get('name', '').lower() == inc.get('name', '').lower() and
                existing.get('date') == inc.get('date')):
                is_dupe = True
                print(f"  Skipping duplicate: {inc.get('name')}")
                break

        if not is_dupe:
            new_id = f"T1-D-{next_death_id:03d}"
            inc['id'] = new_id
            inc['source_tier'] = 1
            inc['collection_method'] = 'web_search'
            inc['verified'] = True
            inc['victim_category'] = 'detainee'
            inc['affected_count'] = 1
            inc['incident_scale'] = 'single'
            if 'date_precision' not in inc:
                inc['date_precision'] = 'day'

            deaths.append(inc)
            next_death_id += 1
            added_deaths += 1
            print(f"  Added: {new_id} - {inc.get('name')}")

    if tier1_is_list:
        save_json(tier1_path, deaths)
    else:
        tier1_data['deaths'] = deaths
        save_json(tier1_path, tier1_data)
    print(f"Added {added_deaths} deaths, total now: {len(deaths)}\n")

    # Add Tier 3 incidents
    print("[TIER 3: FLIGHT, SENSITIVE LOCATION, MILITARY INCIDENTS]")
    tier3_path = data_dir / 'tier3_incidents.json'
    tier3_data = load_json(tier3_path)
    # Handle both list and dict formats
    if isinstance(tier3_data, list):
        incidents = tier3_data
        tier3_is_list = True
    else:
        incidents = tier3_data.get('incidents', [])
        tier3_is_list = False

    # Find next T3 ID
    t3_ids = [int(i['id'].split('-')[-1]) for i in incidents
              if i['id'].startswith('T3-') and not i['id'].startswith('T3-P')]
    next_t3_id = max(t3_ids) + 1 if t3_ids else 1

    all_new = flight_incidents + sensitive_location_incidents + military_incidents
    added_t3 = 0
    skipped_t3 = 0

    for inc in all_new:
        # Check for duplicate by location/date
        is_dupe = False
        for existing in incidents:
            if (existing.get('date') == inc.get('date') and
                existing.get('state') == inc.get('state') and
                existing.get('incident_type') == inc.get('incident_type')):
                is_dupe = True
                print(f"  Skipping duplicate: {inc.get('date')} {inc.get('state')} {inc.get('incident_type')}")
                skipped_t3 += 1
                break

        if not is_dupe:
            new_id = f"T3-{next_t3_id:03d}"
            inc['id'] = new_id
            inc['source_tier'] = 3
            inc['collection_method'] = 'web_search'
            inc['verified'] = True
            inc['incident_scale'] = get_incident_scale(inc.get('affected_count'))
            if 'date_precision' not in inc:
                inc['date_precision'] = 'day'
            if 'victim_category' not in inc:
                inc['victim_category'] = 'undocumented'

            incidents.append(inc)
            next_t3_id += 1
            added_t3 += 1
            print(f"  Added: {new_id} - {inc.get('date')} {inc.get('state', 'Unknown')} - {inc.get('incident_type')}")

    if tier3_is_list:
        save_json(tier3_path, incidents)
    else:
        tier3_data['incidents'] = incidents
        save_json(tier3_path, tier3_data)
    print(f"Added {added_t3} incidents (skipped {skipped_t3}), total now: {len(incidents)}\n")

    print("COMPLETE: Round 6 incidents added")

if __name__ == "__main__":
    main()
