#!/usr/bin/env python3
"""Add Round 8 incidents: Additional deportation flight and detention incidents."""

import json
from pathlib import Path

def get_incident_scale(count):
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
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# New deaths to add
new_deaths = [
    {
        "date": "2025-12-03",
        "state": "Texas",
        "city": "Fort Bliss",
        "facility": "Camp East Montana (Fort Bliss)",
        "name": "Francisco Gaspar-Andres",
        "age": 48,
        "nationality": "Guatemalan",
        "cause_of_death": "Liver and kidney failure",
        "incident_type": "death_in_custody",
        "outcome": "death",
        "outcome_detail": "First death at Camp East Montana. Died from liver and kidney failure. Facility documented to have violated 60+ federal standards in first 50 days.",
        "outcome_category": "death",
        "source_url": "https://elpasomatters.org/2026/01/16/migrant-death-homicide-ice-el-paso-texas-fort-bliss-east-montana-detention-center/",
        "source_name": "El Paso Matters",
        "notes": "December 3, 2025: Francisco Gaspar-Andres, 48-year-old Guatemalan man, was the first death at Camp East Montana (opened August 2025). ICE reported cause as liver and kidney failure. Facility violated at least 60 federal standards during its first 50 days of operation.",
    },
    {
        "date": "2025-12-12",
        "state": "New Jersey",
        "city": "Newark",
        "facility": "Delaney Hall Detention Facility",
        "name": "Jean Wilson Brutus",
        "age": 41,
        "nationality": "Haitian",
        "cause_of_death": "Medical emergency",
        "incident_type": "death_in_custody",
        "outcome": "death",
        "outcome_detail": "Died at University Hospital Newark following medical emergency at detention facility. Had entered ICE custody only the day before after arrest for criminal mischief.",
        "outcome_category": "death",
        "source_url": "https://stevens.house.gov/sites/evo-subsites/stevens.house.gov/files/evo-media-document/2025-1223-ltr-to-dhs-and-ice-re-north-lake-detainee-death-signed.pdf",
        "source_name": "Congressional Letter to DHS",
        "notes": "December 12, 2025: Jean Wilson Brutus, 41-year-old Haitian man, died at University Hospital Newark following medical emergency at Delaney Hall Detention Facility. He had entered ICE custody only the day before, on December 11, 2025, after being arrested for criminal mischief.",
    },
    {
        "date": "2025-10-11",
        "state": "Florida",
        "city": "Miami",
        "facility": "Krome Detention Center",
        "name": "Hasan Ali Moh'D Saleh",
        "age": None,
        "nationality": "Unknown",
        "legal_status": "Lawful permanent resident",
        "cause_of_death": "Medical emergency following fever",
        "incident_type": "death_in_custody",
        "outcome": "death",
        "outcome_detail": "Lawful permanent resident transferred to Krome September 14. Transported to Larkin Community Hospital due to fever on October 10; died the next day.",
        "outcome_category": "death",
        "source_url": "https://www.aclu.org/news/immigrants-rights/inside-an-ice-detention-center-detained-people-describe-severe-medical-neglect-harrowing-conditions",
        "source_name": "ACLU",
        "notes": "October 11, 2025: Hasan Ali Moh'D Saleh, a lawful permanent resident, died after being transferred to Krome on September 14, 2025. On October 10, he was transported to Larkin Community Hospital due to fever; the next day he was dead.",
    },
]

# New Tier 3 incidents
new_incidents = [
    {
        "date": "2025-01-01",
        "date_precision": "year",
        "state": "Unknown",
        "location": "GlobalX deportation flight",
        "incident_type": "physical_force",
        "enforcement_granularity": "medical_emergency",
        "victim_category": "detainee",
        "victim_name": "11 detainees hospitalized",
        "affected_count": 11,
        "outcome": "heat-related hospitalizations",
        "outcome_detail": "Failed GlobalX air conditioning unit sent 11 detainees to hospital with heat-related injuries",
        "outcome_category": "serious_injury",
        "source_url": "https://www.propublica.org/article/inside-ice-air-deportation-flights",
        "source_name": "ProPublica",
        "notes": "2025: A failed GlobalX air conditioning unit sent 11 detainees to the hospital with 'heat-related injuries.' Highlights ongoing safety concerns about aircraft used for deportation flights.",
    },
    {
        "date": "2025-01-15",
        "date_precision": "month",
        "state": "Unknown",
        "location": "GlobalX flight to Brazil",
        "incident_type": "physical_force",
        "enforcement_granularity": "diplomatic_incident",
        "victim_category": "detainee",
        "victim_name": "Multiple deportees fainted",
        "affected_count": 10,
        "outcome": "heat exhaustion, diplomatic incident",
        "outcome_detail": "Shackled deportees on Brazil-bound flight experienced repeated AC failures; multiple people fainted from heat exhaustion. Brazilian government described treatment as 'unacceptable' and 'degrading'.",
        "outcome_category": "serious_injury",
        "source_url": "https://en.wikipedia.org/wiki/Global_Crossing_Airlines",
        "source_name": "Wikipedia",
        "notes": "January 2025: GlobalX flight to Brazil experienced repeated technical problems including broken AC. Multiple people fainted from heat exhaustion while shackled. Brazilian government ministers described treatment as 'unacceptable' and 'degrading,' creating diplomatic tensions.",
    },
    {
        "date": "2025-10-01",
        "date_precision": "month",
        "state": "Florida",
        "city": "Miami",
        "location": "Krome Detention Center",
        "incident_type": "physical_force",
        "enforcement_granularity": "overcrowding",
        "victim_category": "detainee",
        "victim_name": "Krome detainees (1,806 at 611 capacity)",
        "affected_count": 1806,
        "outcome": "severe overcrowding, inhumane conditions",
        "outcome_detail": "Facility held triple capacity (1,806 vs 611). Detainees slept on floors, held on buses overnight in shackles, received only 'a cup of rice and water a day', no bedding.",
        "outcome_category": "serious_injury",
        "source_url": "https://www.pogo.org/investigates/ice-inspections-plummeted-as-detentions-soared-in-2025",
        "source_name": "POGO",
        "notes": "October 2025: Krome detention center held triple its capacity for at least one night - 1,806 detainees at a facility designed for 611. Detainees reported sleeping on floors, being held on buses overnight in shackles, receiving only 'a cup of rice and a glass of water a day,' and having to sleep without bedding.",
    },
    {
        "date": "2025-10-03",
        "state": "Multiple",
        "location": "Nationwide ICE detention facilities",
        "incident_type": "physical_force",
        "enforcement_granularity": "systemic_medical_failure",
        "victim_category": "detainee",
        "victim_name": "73,000+ detainees affected",
        "affected_count": 73000,
        "outcome": "medical care suspended",
        "outcome_detail": "ICE stopped paying third-party medical providers; 'absolute emergency' with no mechanism to provide medication, dialysis, prenatal care, oncology, or chemotherapy until April 30, 2026.",
        "outcome_category": "serious_injury",
        "source_url": "https://www.cbsnews.com/atlanta/news/ice-stopped-paying-for-detainee-medical-care-as-population-surged/",
        "source_name": "CBS News Atlanta",
        "notes": "October 3, 2025: ICE stopped paying third-party medical providers for detainee care, with payments suspended until at least April 30, 2026. Internal documents describe 'absolute emergency' with 'no mechanism to provide prescribed medication' and no ability to pay for dialysis, prenatal care, oncology, or chemotherapy. Affects 73,000+ detainees.",
    },
    {
        "date": "2025-07-04",
        "state": "Texas",
        "city": "Alvarado",
        "location": "Prairieland Detention Center",
        "incident_type": "shooting_at_agent",
        "enforcement_granularity": "facility_attack",
        "victim_category": "officer",
        "victim_name": "Alvarado police officer (shot in neck)",
        "affected_count": 20,
        "outcome": "coordinated attack on ICE facility",
        "outcome_detail": "12 individuals used fireworks/vandalism to draw out officers; one person fired rifle, shooting officer in neck. Two AR-15s, ballistic vests, helmet found. 19 arrested, 7 pleaded guilty to terrorism charges.",
        "outcome_category": "serious_injury",
        "source_url": "https://en.wikipedia.org/wiki/2025_Alvarado_ICE_facility_incident",
        "source_name": "Wikipedia",
        "notes": "July 4, 2025: Coordinated attack on Prairieland Detention Center in Alvarado, Texas. 12 individuals used fireworks and vandalism to draw out officers; a person opened fire with rifle, shooting Alvarado police officer in neck. Two AR-15 rifles, ballistic vests, helmet found. 19 suspects arrested; 7 pleaded guilty to terrorism-related charges. Trial for 9 defendants set for February 17, 2026.",
    },
    {
        "date": "2025-11-15",
        "date_precision": "month",
        "state": "Rhode Island",
        "city": "Providence",
        "location": "Courthouse",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_category": "us_citizen_collateral",
        "victim_name": "High school courthouse intern",
        "affected_count": 1,
        "outcome": "wrongful detention of student",
        "outcome_detail": "High school intern at courthouse mistakenly detained by ICE. State officials called incident 'outrageous'. Highlights concerns about courthouse enforcement.",
        "outcome_category": "detained",
        "source_url": "https://www.cnn.com/2025/11/22/us/rhode-island-intern-detained-ice",
        "source_name": "CNN",
        "notes": "November 2025: A high school courthouse intern was mistakenly detained by ICE in Rhode Island. State officials called the incident 'outrageous.' Case highlights concerns about ICE enforcement operations at courthouses and potential for wrongful detentions.",
    },
]


def main():
    data_dir = Path(__file__).parent.parent / 'data' / 'incidents'

    # Add Tier 1 deaths
    print("[TIER 1: DEATHS IN CUSTODY]")
    tier1_path = data_dir / 'tier1_deaths_in_custody.json'
    deaths = load_json(tier1_path)

    death_ids = [int(d['id'].split('-')[-1]) for d in deaths if d['id'].startswith('T1-D-')]
    next_death_id = max(death_ids) + 1 if death_ids else 1

    added_deaths = 0
    for inc in new_deaths:
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

    save_json(tier1_path, deaths)
    print(f"Added {added_deaths} deaths, total now: {len(deaths)}\n")

    # Add Tier 3 incidents
    print("[TIER 3: ADDITIONAL FLIGHT/DETENTION INCIDENTS]")
    tier3_path = data_dir / 'tier3_incidents.json'
    incidents = load_json(tier3_path)

    t3_ids = [int(i['id'].split('-')[-1]) for i in incidents
              if i['id'].startswith('T3-') and not i['id'].startswith('T3-P')]
    next_t3_id = max(t3_ids) + 1 if t3_ids else 1

    added_t3 = 0
    skipped_t3 = 0

    for inc in new_incidents:
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

            incidents.append(inc)
            next_t3_id += 1
            added_t3 += 1
            print(f"  Added: {new_id} - {inc.get('date')} {inc.get('state')} - {inc.get('location', '')[:40]}")

    save_json(tier3_path, incidents)
    print(f"Added {added_t3} incidents (skipped {skipped_t3}), total now: {len(incidents)}\n")

    print("COMPLETE: Round 8 incidents added")

if __name__ == "__main__":
    main()
