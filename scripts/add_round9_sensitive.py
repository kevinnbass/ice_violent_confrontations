#!/usr/bin/env python3
"""Add Round 9 incidents: Sensitive location incidents (schools, hospitals, churches, courthouses)."""

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

# Sensitive location incidents
sensitive_incidents = [
    # SCHOOLS
    {
        "date": "2026-01-07",
        "state": "Minnesota",
        "city": "Minneapolis",
        "location": "Roosevelt High School",
        "incident_type": "less_lethal",
        "enforcement_granularity": "sensitive_location_school",
        "victim_category": "multiple",
        "victim_name": "School staff and students",
        "affected_count": 10,
        "outcome": "staff detained, chemical agents deployed",
        "outcome_detail": "Border Patrol clashed with teachers during dismissal; handcuffed 2 staff members including US citizen; allegedly pepper-sprayed students. Occurred hours after ICE fatally shot Renee Nicole Good nearby. School canceled classes for 2 days.",
        "outcome_category": "detained",
        "source_url": "https://www.startribune.com/what-happened-when-border-patrol-agents-showed-up-at-minneapolis-roosevelt-high-school/601561137",
        "source_name": "Minneapolis Star Tribune",
        "notes": "January 7, 2026: US Border Patrol agents clashed with teachers and protesters at Roosevelt High School during dismissal. Agents handcuffed two staff members (including US citizen special education assistant) and allegedly pepper-sprayed students. Occurred hours after ICE fatally shot Renee Nicole Good nearby. Minneapolis Public Schools canceled classes for two days.",
    },
    {
        "date": "2026-01-15",
        "date_precision": "month",
        "state": "Minnesota",
        "city": "Columbia Heights",
        "location": "Near school/residence",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "sensitive_location_school",
        "victim_category": "enforcement_target",
        "victim_name": "Liam Conejo Ramos (5-year-old) and father",
        "affected_count": 5,
        "outcome": "child used as bait to arrest parent",
        "outcome_detail": "Federal agents took 5-year-old from running car in family driveway after preschool, then told him to knock on door - 'essentially using a 5-year-old as bait.' 4 total students from Columbia Heights schools detained.",
        "outcome_category": "detained",
        "source_url": "https://www.cbsnews.com/minnesota/news/minnesota-school-children-ice-arrests-columbia-heights/",
        "source_name": "CBS Minnesota",
        "notes": "January 2026: Federal agents took 5-year-old Liam Conejo Ramos from running car in family driveway after he arrived home from preschool. Officers then told him to knock on door, 'essentially using a 5-year-old as bait' per school superintendent. 4 total students from Columbia Heights schools detained.",
    },
    {
        "date": "2025-08-20",
        "state": "California",
        "city": "Encinitas",
        "location": "Near Park Dale Lane Elementary School (2 blocks)",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "sensitive_location_school",
        "victim_category": "enforcement_target",
        "victim_name": "Guatemalan parent (2017 removal order)",
        "affected_count": 1,
        "outcome": "parent arrested during school drop-off",
        "outcome_detail": "ICE and ATF arrested father near elementary school at 7:30am during drop-off hours. Video shows agents forcing man into truck as wife and young daughter cry out.",
        "outcome_category": "detained",
        "source_url": "https://www.kpbs.org/news/border-immigration/2025/08/20/ice-arrests-parent-near-elementary-school-in-encinitas",
        "source_name": "KPBS",
        "notes": "August 20, 2025: ICE and ATF agents arrested a father near Park Dale Lane Elementary School (2 blocks from campus) around 7:30 a.m. during drop-off hours. Video shows agents forcing the Guatemalan national (with 2017 removal order) into a truck as his wife and young daughter cry out.",
    },
    {
        "date": "2025-08-01",
        "date_precision": "month",
        "state": "California",
        "city": "Chula Vista",
        "location": "Near elementary school",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "sensitive_location_school",
        "victim_category": "enforcement_target",
        "victim_name": "Kyungjin Yu (South Korean national)",
        "affected_count": 1,
        "outcome": "mother arrested at school arrival",
        "outcome_detail": "Immigration agents arrested mother outside elementary school as students were arriving. City councilmember called arrest 'shameful and disgusting'.",
        "outcome_category": "detained",
        "source_url": "https://www.kpbs.org/news/border-immigration/2025/08/08/what-we-know-about-ice-arrest-of-a-parent-outside-a-chula-vista-elementary-school",
        "source_name": "KPBS",
        "notes": "August 2025: Immigration agents arrested Kyungjin Yu, a South Korean national who overstayed visa, outside a Chula Vista elementary school as students were arriving. City councilmember called the arrest 'shameful and disgusting.'",
    },
    {
        "date": "2025-11-15",
        "state": "North Carolina",
        "city": "Charlotte",
        "location": "Community-wide schools affected",
        "incident_type": "mass_raid",
        "enforcement_granularity": "operation_school_impact",
        "victim_category": "multiple",
        "victim_name": "Charlotte area residents and students",
        "affected_count": 370,
        "outcome": "370+ arrests, 56,000+ school absences",
        "outcome_detail": "Border Patrol 'Operation Charlotte's Web' deployed 200 agents; 370+ arrests. School absences tripled - 30,000+ students absent Monday (20% of district enrollment), 56,000+ over two days.",
        "outcome_category": "detained",
        "source_url": "https://www.axios.com/local/charlotte/2025/11/19/border-patrol-ice-operation-immigration-web",
        "source_name": "Axios Charlotte",
        "notes": "November 15-20, 2025: Border Patrol's 'Operation Charlotte's Web' deployed 200 agents who made 370+ arrests. School absences nearly tripled - over 30,000 students absent on one Monday (20% of district enrollment), 56,000+ over two days total.",
    },
    # HOSPITALS
    {
        "date": "2025-12-15",
        "date_precision": "month",
        "state": "Minnesota",
        "city": "Minneapolis",
        "location": "Hennepin County Medical Center",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "sensitive_location_hospital",
        "victim_category": "detainee",
        "victim_name": "Patient shackled to hospital bed",
        "affected_count": 1,
        "outcome": "patient shackled 28 hours without warrant",
        "outcome_detail": "Six ICE officers entered ER without judicial warrant, stationed in staff-only areas, shackled patient to bed for 28 hours. Doctors reported patients delaying lifesaving care due to fear - pediatrician saw 'rash of appendicitis that should have been treated earlier'.",
        "outcome_category": "detained",
        "source_url": "https://sahanjournal.com/health/ice-agents-hospitals-hennepin-county-medical-center/",
        "source_name": "Sahan Journal",
        "notes": "December 2025-January 2026: Six ICE officers entered Hennepin County Medical Center emergency department without judicial warrant, stationed in staff-only areas, shackled a patient to bed for 28 hours. Doctors reported patients delaying lifesaving care due to fear; one pediatrician said she saw 'a rash of appendicitis that should have been treated earlier.'",
    },
    {
        "date": "2025-07-03",
        "state": "California",
        "city": "Glendale",
        "location": "Glendale Memorial Hospital",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "sensitive_location_hospital",
        "victim_category": "detainee",
        "victim_name": "Milagro Solis Portillo (El Salvador)",
        "affected_count": 1,
        "outcome": "15-day ICE stakeout at hospital",
        "outcome_detail": "After detaining woman who needed emergency care, ICE agents camped out at hospital for 15 days waiting to re-apprehend her. Agents sat in lobby, slept on couches, described by nurses as 'intimidating and hostile'.",
        "outcome_category": "detained",
        "source_url": "https://lapublicpress.org/2025/07/ice-agents-glendale-hospital-waiting-to-arrest-a-patient/",
        "source_name": "LA Public Press",
        "notes": "July 3-18, 2025: After detaining Milagro Solis Portillo who then needed emergency medical care, ICE agents camped out at Glendale Memorial Hospital for 15 days waiting to re-apprehend her. Agents sat in the lobby, slept on couches, and were described by nurses as 'intimidating and hostile.'",
    },
    # CHURCHES (additional to ones already in database)
    {
        "date": "2025-06-20",
        "state": "California",
        "city": "Montclair",
        "location": "Our Lady of Lourdes Church",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "sensitive_location_church",
        "victim_category": "enforcement_target",
        "victim_name": "Longtime parishioner (landscaping)",
        "affected_count": 1,
        "outcome": "parishioner detained on church property",
        "outcome_detail": "ICE agents took longtime parishioner into custody on church grounds while doing landscaping work. His family involved in ministry. ICE claimed man pulled into parking lot during traffic stop.",
        "outcome_category": "detained",
        "source_url": "https://calmatters.org/california-divide/2025/07/ice-targets-immigrants-church-grounds/",
        "source_name": "CalMatters",
        "notes": "June 20, 2025: ICE agents took a longtime parishioner into custody on Our Lady of Lourdes Church grounds in Montclair while he was doing landscaping work. His family is involved in the ministry. ICE claimed the man pulled into the church parking lot during a traffic stop.",
    },
    {
        "date": "2025-06-20",
        "state": "California",
        "city": "Highland",
        "location": "St. Adelaide Parish",
        "incident_type": "mass_raid",
        "enforcement_granularity": "sensitive_location_church",
        "victim_category": "enforcement_target",
        "victim_name": "Multiple individuals detained",
        "affected_count": 5,
        "outcome": "agents chased individuals onto church property",
        "outcome_detail": "Same day as Montclair incident, ICE agents chased several men onto St. Adelaide Parish parking lot and detained multiple people who were neither employees nor parishioners.",
        "outcome_category": "detained",
        "source_url": "https://calmatters.org/california-divide/2025/07/ice-targets-immigrants-church-grounds/",
        "source_name": "CalMatters",
        "notes": "June 20, 2025: Same day as Montclair incident, ICE agents chased several men onto the parking lot of St. Adelaide parish in Highland and detained multiple people who were neither employees nor parishioners.",
    },
    # COURTHOUSES
    {
        "date": "2025-05-20",
        "state": "California",
        "city": "San Francisco",
        "location": "SF and Concord Immigration Courts",
        "incident_type": "mass_raid",
        "enforcement_granularity": "sensitive_location_courthouse",
        "victim_category": "enforcement_target",
        "victim_name": "Immigration court respondents",
        "affected_count": 130,
        "outcome": "systematic arrests at court appearances",
        "outcome_detail": "Following May 20 ICE memo, agents systematically arrested individuals at immigration court appearances. Trial attorneys would dismiss cases, then deportation officers would arrest for expedited removal. ~130 arrests documented. Federal judge ordered halt on Christmas Eve.",
        "outcome_category": "detained",
        "source_url": "https://www.americanimmigrationcouncil.org/blog/ice-arrests-immigration-courts-expedited-removal/",
        "source_name": "American Immigration Council",
        "notes": "May 2025-present: Following May 20, 2025 internal ICE memo, agents began systematically arresting individuals at San Francisco and Concord immigration court appearances. ICE trial attorneys would move to dismiss cases, then deportation officers would arrest respondents for expedited removal. Approximately 130 arrests documented. Federal judge ordered halt on Christmas Eve.",
    },
    {
        "date": "2025-01-01",
        "date_precision": "year",
        "state": "Multiple",
        "location": "Immigration courts nationwide",
        "incident_type": "mass_raid",
        "enforcement_granularity": "systemic_courthouse_fear",
        "victim_category": "enforcement_target",
        "victim_name": "Immigration court respondents",
        "affected_count": 50000,
        "outcome": "50,000+ in absentia removal orders due to fear",
        "outcome_detail": "Following increased courthouse arrests, immigrants not appearing for hearings nearly tripled. Over 50,000 in absentia removal orders in FY 2025. Lawyers report clients saying 'if you go to court, you could get picked up from ICE'.",
        "outcome_category": "deported",
        "source_url": "https://www.npr.org/2025/12/22/nx-s1-5583971/trump-ice-immigration-arrests-deportation-no-shows",
        "source_name": "NPR",
        "notes": "FY 2025: Following increased courthouse arrests, number of immigrants not appearing for court hearings nearly tripled. Over 50,000 in absentia removal orders (nearly triple previous year). Immigration lawyers report clients saying 'if you go to court, you could get picked up from ICE.'",
    },
    # DOMESTIC VIOLENCE IMPACT
    {
        "date": "2025-06-01",
        "date_precision": "month",
        "state": "Texas",
        "city": "Houston",
        "location": "Houston police/social services",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "dv_victim_deterrence",
        "victim_category": "bystander",
        "victim_name": "Domestic violence victims deterred",
        "affected_count": 100,
        "outcome": "DV victims deterred from reporting",
        "outcome_detail": "Houston police calls to ICE increased over 1,000% in 2025. In June, officer warned woman reporting her abuser that police had contacted ICE and advised her not to file in person or risk deportation.",
        "outcome_category": "none",
        "source_url": "https://www.themarshallproject.org/2025/11/22/women-police-ice-domestic-violence",
        "source_name": "The Marshall Project",
        "notes": "2025: Houston police calls to ICE increased over 1,000%. In June, a Houston officer warned a woman reporting her abuser that police had contacted ICE and advised her not to file a report in person or risk deportation. Deterring domestic violence victims from seeking help.",
    },
]


def main():
    data_dir = Path(__file__).parent.parent / 'data' / 'incidents'

    print("[TIER 3: SENSITIVE LOCATION INCIDENTS]")
    tier3_path = data_dir / 'tier3_incidents.json'
    incidents = load_json(tier3_path)

    t3_ids = [int(i['id'].split('-')[-1]) for i in incidents
              if i['id'].startswith('T3-') and not i['id'].startswith('T3-P')]
    next_t3_id = max(t3_ids) + 1 if t3_ids else 1

    added = 0
    skipped = 0

    for inc in sensitive_incidents:
        is_dupe = False
        for existing in incidents:
            # Check for similar date/state/type
            if (existing.get('date') == inc.get('date') and
                existing.get('state') == inc.get('state') and
                existing.get('incident_type') == inc.get('incident_type')):
                is_dupe = True
                print(f"  Skipping duplicate: {inc.get('date')} {inc.get('state')} {inc.get('location', '')[:25]}")
                skipped += 1
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
            added += 1
            print(f"  Added: {new_id} - {inc.get('date')} {inc.get('state')} - {inc.get('location', '')[:35]}")

    save_json(tier3_path, incidents)
    print(f"\nAdded {added} incidents (skipped {skipped}), total now: {len(incidents)}")
    print("\nCOMPLETE: Round 9 sensitive location incidents added")

if __name__ == "__main__":
    main()
