#!/usr/bin/env python3
"""Add Round 7 incidents: Military/National Guard cooperation from agent search."""

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

# New military/National Guard incidents
military_incidents = [
    {
        "date": "2025-08-01",
        "date_precision": "month",
        "state": "Texas",
        "city": "Fort Bliss",
        "location": "Camp East Montana (Fort Bliss Army Base)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "military_detention_facility",
        "victim_category": "detainee",
        "victim_name": "Fort Bliss detainees",
        "affected_count": 1000,
        "outcome": "mass detention at military facility",
        "outcome_detail": "Tent camp at Fort Bliss opened; violated 60+ federal detention standards in first 50 days per leaked inspection. Reports of beatings, sexual abuse, medical neglect.",
        "outcome_category": "detained",
        "source_url": "https://www.hrw.org/news/2025/12/08/us-close-fort-bliss-immigration-detention-site",
        "source_name": "Human Rights Watch",
        "notes": "August 2025: Camp East Montana opened at Fort Bliss Army base as largest ICE detention center in the country. Initially 1,000 detainees, expanded to 2,700+. $1.2 billion facility expected to reach 5,000 capacity. Leaked ICE inspection found 60+ federal detention standard violations.",
    },
    {
        "date": "2025-01-24",
        "state": "Washington",
        "city": "Joint Base Lewis-McChord",
        "location": "JBLM Air Base",
        "incident_type": "mass_raid",
        "enforcement_granularity": "military_deportation_flights",
        "victim_category": "detainee",
        "victim_name": "Deportees on military flights",
        "affected_count": 200,
        "outcome": "military deportation flights initiated",
        "outcome_detail": "88 military removal flights conducted using C-17 Globemaster cargo planes; ~80 people per flight; cost $4,675/migrant (5x commercial rates)",
        "outcome_category": "deported",
        "source_url": "https://jsis.washington.edu/humanrights/2025/02/19/research-shows-jblm-based-planes-used-in-military-deportation-flights-and-flights-to-guantanamo/",
        "source_name": "UW Center for Human Rights",
        "notes": "January 24-February 13, 2025: Boeing C-17 Globemaster III military cargo planes from Joint Base Lewis-McChord conducted 88 deportation flights to Guatemala, Ecuador, Colombia. Cost was $4,675 per migrant - five times higher than commercial flights.",
    },
    {
        "date": "2025-02-04",
        "state": "Cuba",
        "city": "Guantanamo Bay",
        "location": "Migrant Operations Center, Naval Station Guantanamo Bay",
        "incident_type": "mass_raid",
        "enforcement_granularity": "military_detention_facility",
        "victim_category": "detainee",
        "victim_name": "Guantanamo immigration detainees",
        "affected_count": 700,
        "outcome": "offshore military detention",
        "outcome_detail": "First deportation flight arrived with 12 detainees from Fort Bliss on C-17 ($142,500 cost). 700+ immigrants detained, 127 in high-security Camp 6. Later ruled illegal by US court.",
        "outcome_category": "detained",
        "source_url": "https://www.niskanencenter.org/the-offshore-detention-gamble-a-billion-dollar-shift-to-gitmo/",
        "source_name": "Niskanen Center",
        "notes": "February 4, 2025: First deportation flight arrived at Guantanamo's Migrant Operations Center carrying 12 detainees from Fort Bliss on a C-17 military jet. Over 700 immigrants detained, including 127 in high-security Camp 6. Nearly 200 Venezuelan migrants held. U.S. court later ruled use of Guantanamo for immigration detention illegal.",
    },
    {
        "date": "2025-09-22",
        "state": "Florida",
        "city": "Central Florida",
        "location": "Multiple Central Florida locations",
        "incident_type": "mass_raid",
        "enforcement_granularity": "military_287g_operation",
        "victim_category": "enforcement_target",
        "victim_name": "Central Florida detainees",
        "affected_count": 400,
        "outcome": "arrests with National Guard support",
        "outcome_detail": "ICE Miami partnered with Florida Highway Patrol, multiple sheriff's offices, and Florida National Guard under 287(g) agreements for weeklong operation",
        "outcome_category": "detained",
        "source_url": "https://www.ice.gov/news/releases/ice-miami-287g-partners-arrest-400-criminal-aliens-during-central-florida-operations",
        "source_name": "ICE News Release",
        "notes": "September 22-26, 2025: ICE Miami partnered with Florida Highway Patrol, multiple county sheriff's offices, and Florida National Guard under 287(g) agreements to arrest over 400 individuals during weeklong operation. Marked unprecedented National Guard involvement in 287(g) immigration enforcement.",
    },
    {
        "date": "2025-10-04",
        "state": "Illinois",
        "city": "Chicago",
        "location": "Statewide Illinois",
        "incident_type": "mass_raid",
        "enforcement_granularity": "state_federal_conflict",
        "victim_category": "multiple",
        "victim_name": "Illinois residents",
        "affected_count": 50,
        "outcome": "National Guard federalization blocked by Supreme Court",
        "outcome_detail": "Trump federalized Illinois National Guard over Gov. Pritzker's objections ('Operation Midway Blitz'); also deployed Texas Guard to Illinois. Supreme Court rejected on Dec 23, 2025.",
        "outcome_category": "multiple",
        "source_url": "https://www.supremecourt.gov/opinions/25pdf/25a443_new_b07d.pdf",
        "source_name": "Supreme Court Opinion",
        "notes": "October 4, 2025: President Trump federalized 300 Illinois National Guard troops over Governor Pritzker's objections as part of 'Operation Midway Blitz.' Also deployed Texas National Guard to Illinois. December 23, 2025: Supreme Court rejected Trump's request, ruling government 'failed to identify a source of authority' for military law enforcement.",
    },
    {
        "date": "2025-01-20",
        "date_precision": "month",
        "state": "Texas",
        "city": "El Paso",
        "location": "US-Mexico border",
        "incident_type": "mass_raid",
        "enforcement_granularity": "military_deputization",
        "victim_category": "enforcement_target",
        "victim_name": "Border crossers",
        "affected_count": 300,
        "outcome": "National Guard granted arrest authority",
        "outcome_detail": "Border Patrol Chief deputized 300+ Texas National Guard soldiers, granting limited law enforcement authority to make immigration arrests - unprecedented for Guard",
        "outcome_category": "detained",
        "source_url": "https://www.cbp.gov/newsroom/local-media-release/texas-national-guard-sworn-support-border-patrol-efforts-el-paso",
        "source_name": "CBP",
        "notes": "January 2025: US Border Patrol Chief Mike Banks deputized over 300 Texas National Guard soldiers, granting them limited law enforcement authority to make immigration arrests. This was unprecedented - immigration arrest authority had previously been reserved for federal agencies. Nearly 5,000 Guard members under Operation Lone Star.",
    },
    {
        "date": "2025-01-27",
        "state": "Colorado",
        "city": "Aurora",
        "location": "Buckley Space Force Base",
        "incident_type": "mass_raid",
        "enforcement_granularity": "military_processing_center",
        "victim_category": "enforcement_target",
        "victim_name": "Adams County detainees",
        "affected_count": 50,
        "outcome": "military base used for ICE processing",
        "outcome_detail": "First military installation used for ICE processing/temporary detention as part of 'Operation Aurora'; served as staging area and operations center",
        "outcome_category": "detained",
        "source_url": "https://www.denverpost.com/2025/01/29/buckley-space-force-base-ice-detained-immigrants/",
        "source_name": "Denver Post",
        "notes": "January 27-29, 2025: Buckley Space Force Base in Aurora became the first military installation used for ICE processing and temporary detention as part of 'Operation Aurora.' The facility served as a staging area and operations center. Plans for extended detention were later reversed.",
    },
    {
        "date": "2025-07-15",
        "state": "New Jersey",
        "city": "Joint Base McGuire-Dix-Lakehurst",
        "location": "Joint Base McGuire-Dix-Lakehurst",
        "incident_type": "mass_raid",
        "enforcement_granularity": "military_detention_facility",
        "victim_category": "detainee",
        "victim_name": "Planned detainees (3,000 capacity)",
        "affected_count": 3000,
        "outcome": "military base certified for detention",
        "outcome_detail": "Defense Secretary certified base for immigrant detention as 'central hub' for deportations; Gov. Murphy opposed as 'gross misuse of military resources'",
        "outcome_category": "detained",
        "source_url": "https://www.inquirer.com/news/new-jersey/joint-base-mcguire-dix-lakehurst-immigration-detention-trump-administration-20250718.html",
        "source_name": "Philadelphia Inquirer",
        "notes": "July 15, 2025: Defense Secretary Pete Hegseth certified Joint Base McGuire-Dix-Lakehurst for immigrant detention as a 'central hub' for deportation efforts. Planned capacity of 3,000 detainees. Governor Phil Murphy opposed, calling it 'a gross misuse of U.S. military resources.' As of October 2025, no construction had begun.",
    },
    {
        "date": "2025-10-01",
        "date_precision": "month",
        "state": "Multiple",
        "city": "Nationwide",
        "location": "Nationwide detention center construction",
        "incident_type": "mass_raid",
        "enforcement_granularity": "military_construction_contract",
        "victim_category": "detainee",
        "victim_name": "Planned detainees (100,000 capacity target)",
        "affected_count": 100000,
        "outcome": "$10B funneled through Navy for detention construction",
        "outcome_detail": "DHS funneled $10 billion through Navy to expedite construction of nationwide detention center network; target 100,000 detention beds",
        "outcome_category": "detained",
        "source_url": "https://www.cnn.com/2025/10/24/politics/navy-building-ice-detention-facilities",
        "source_name": "CNN Politics",
        "notes": "October 2025: DHS funneled $10 billion through the Navy to facilitate construction of a network of migrant detention centers nationwide. The arrangement was designed to expedite construction compared to standard procurement processes. Target capacity: 100,000 detention beds.",
    },
    {
        "date": "2025-09-08",
        "state": "Iowa",
        "city": "Statewide",
        "location": "Iowa ICE facilities",
        "incident_type": "mass_raid",
        "enforcement_granularity": "military_involvement",
        "victim_category": "enforcement_target",
        "victim_name": "Iowa detainees",
        "affected_count": 20,
        "outcome": "National Guard administrative support for ICE",
        "outcome_detail": "Governor Reynolds directed 20 Iowa National Guard soldiers to provide administrative and logistical support to ICE under Title 32 federal funding",
        "outcome_category": "detained",
        "source_url": "https://governor.iowa.gov/press-release/2025-08-12/gov-reynolds-directs-iowa-national-guard-support-federal-immigration-enforcement-mission",
        "source_name": "Governor Kim Reynolds",
        "notes": "September 8, 2025: Governor Kim Reynolds directed 20 Iowa National Guard soldiers to provide administrative and logistical support to Iowa-based ICE officials under Title 32 federal funding.",
    },
    {
        "date": "2025-11-17",
        "state": "Tennessee",
        "city": "Memphis",
        "location": "Memphis area",
        "incident_type": "mass_raid",
        "enforcement_granularity": "state_federal_conflict",
        "victim_category": "enforcement_target",
        "victim_name": "Memphis area residents",
        "affected_count": 50,
        "outcome": "National Guard deployment blocked by court injunction",
        "outcome_detail": "Gov. Lee activated Tennessee National Guard under Title 32 for Memphis task force; Davidson County court issued temporary injunction finding no emergency justification",
        "outcome_category": "multiple",
        "source_url": "https://www.justsecurity.org/114395/the-mounting-crisis-of-militarizing-immigration-enforcement/",
        "source_name": "Just Security",
        "notes": "November 17, 2025: Governor Bill Lee activated Tennessee National Guard under Title 32 to support multi-agency public safety task force in Memphis. Davidson County Chancery Court issued temporary injunction, finding no evidence of rebellion, invasion, or emergency conditions to justify the activation.",
    },
]

# New deaths to add to Tier 1
new_deaths = [
    {
        "date": "2026-01-03",
        "state": "Texas",
        "city": "Fort Bliss",
        "facility": "Camp East Montana (Fort Bliss)",
        "name": "Geraldo Lunas Campos",
        "age": 55,
        "nationality": "Cuban",
        "cause_of_death": "Asphyxia due to neck and chest compression (homicide)",
        "incident_type": "death_in_custody",
        "outcome": "death",
        "outcome_detail": "Preliminary cause: asphyxia due to neck and chest compression, suggesting homicide. Occurred at military base detention facility.",
        "outcome_category": "death",
        "source_url": "https://thenationaldesk.com/news/americas-news-now/report-migrants-death-at-fort-bliss-detention-center-likely-ruled-homicide",
        "source_name": "The National Desk",
        "notes": "January 3, 2026: Geraldo Lunas Campos, 55-year-old Cuban migrant, died at Camp East Montana on Fort Bliss military base. Preliminary cause of death reported as 'asphyxia due to neck and chest compression,' suggesting homicide ruling pending toxicology results.",
    },
    {
        "date": "2026-01-14",
        "state": "Texas",
        "city": "Fort Bliss",
        "facility": "Camp East Montana (Fort Bliss)",
        "name": "Victor Manuel Diaz",
        "age": 36,
        "nationality": "Nicaraguan",
        "cause_of_death": "Presumed suicide",
        "incident_type": "death_in_custody",
        "outcome": "death",
        "outcome_detail": "Died of 'presumed suicide' at Camp East Montana tent complex. At least third death at the facility.",
        "outcome_category": "death",
        "source_url": "https://abcnews.go.com/US/ice-detainee-dies-presumed-suicide-texas-detention-facility/story?id=129364093",
        "source_name": "ABC News",
        "notes": "January 14, 2026: Victor Manuel Diaz, 36-year-old Nicaraguan national, died of 'presumed suicide' at Camp East Montana tent complex at Fort Bliss. This was at least the third death reported at the facility.",
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
        # Check for duplicate
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
    print("[TIER 3: MILITARY/NATIONAL GUARD INCIDENTS]")
    tier3_path = data_dir / 'tier3_incidents.json'
    incidents = load_json(tier3_path)

    t3_ids = [int(i['id'].split('-')[-1]) for i in incidents
              if i['id'].startswith('T3-') and not i['id'].startswith('T3-P')]
    next_t3_id = max(t3_ids) + 1 if t3_ids else 1

    added_t3 = 0
    skipped_t3 = 0

    for inc in military_incidents:
        # Check for duplicate by location/date/type
        is_dupe = False
        for existing in incidents:
            # Check for same date and state and similar type
            if (existing.get('date') == inc.get('date') and
                existing.get('state') == inc.get('state') and
                existing.get('incident_type') == inc.get('incident_type')):
                is_dupe = True
                print(f"  Skipping duplicate: {inc.get('date')} {inc.get('state')} {inc.get('location', '')[:30]}")
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
                inc['victim_category'] = 'enforcement_target'

            incidents.append(inc)
            next_t3_id += 1
            added_t3 += 1
            print(f"  Added: {new_id} - {inc.get('date')} {inc.get('state', 'Unknown')} - {inc.get('location', '')[:40]}")

    save_json(tier3_path, incidents)
    print(f"Added {added_t3} incidents (skipped {skipped_t3}), total now: {len(incidents)}\n")

    print("COMPLETE: Round 7 military/National Guard incidents added")

if __name__ == "__main__":
    main()
