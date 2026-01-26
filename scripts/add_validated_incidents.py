#!/usr/bin/env python3
"""
Add new validated incidents from agent searches and fix schema issues.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "incidents"


def get_incident_scale(count):
    """Determine incident_scale based on affected_count."""
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


def fix_incident_scales(records):
    """Fix incident_scale mismatches in records."""
    fixed = 0
    for record in records:
        count = record.get("affected_count", 1)
        expected = get_incident_scale(count)
        if record.get("incident_scale") != expected:
            record["incident_scale"] = expected
            fixed += 1
    return fixed


def ensure_required_fields(record):
    """Ensure record has all required fields with proper values."""
    # Ensure date_precision
    if "date_precision" not in record:
        record["date_precision"] = "day"

    # Ensure affected_count
    if "affected_count" not in record:
        record["affected_count"] = record.get("victim_count", 1)

    # Ensure incident_scale matches affected_count
    record["incident_scale"] = get_incident_scale(record["affected_count"])

    # Ensure outcome_detail
    if "outcome_detail" not in record and "outcome" in record:
        record["outcome_detail"] = record["outcome"]

    return record


# New Tier 3 incidents from agent searches
NEW_TIER3_INCIDENTS = [
    {
        "id": "T3-101",
        "date": "2025-09-04",
        "state": "Georgia",
        "city": "Ellabell (Hyundai Metaplant)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_category": "enforcement_target",
        "victim_count": 475,
        "outcome": "475 workers detained, largest single-site raid in DHS history",
        "notes": "Largest single-site worksite enforcement in DHS history. Workers hid in air ducts, some fled into sewage pond where agents used boats. Majority South Korean nationals (~300), plus Mexican, Japanese, Chinese workers. Major diplomatic dispute with South Korea. $7.6B EV battery plant opening delayed 2-3 months.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cnn.com/2025/09/05/us/georgia-plant-ice-raid-hundreds-arrested-hnk",
        "source_name": "CNN",
        "verified": True,
        "affected_count": 475,
        "outcome_category": "detained"
    },
    {
        "id": "T3-102",
        "date": "2025-06-10",
        "state": "Nebraska",
        "city": "Omaha (South)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_category": "enforcement_target",
        "victim_count": 76,
        "outcome": "76 workers detained at meatpacking plant",
        "notes": "Glenn Valley Foods meatpacking plant. Largest Nebraska workplace raid. Workers ordered 'Manos arriba!' Four-hour operation. Workers accused of using 100+ stolen identities. Purged ~half of staff. Sparked protests, some threw rocks at vehicles.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.npr.org/2025/06/11/nx-s1-5429790/immigration-raid-at-omaha-meatpacking-plant-spurs-protests-stokes-fear-in-the-city",
        "source_name": "NPR",
        "verified": True,
        "affected_count": 76,
        "outcome_category": "detained"
    },
    {
        "id": "T3-103",
        "date": "2025-05-29",
        "state": "Florida",
        "city": "Tallahassee (FSU College Town)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_category": "enforcement_target",
        "victim_count": 100,
        "outcome": "100+ workers detained at construction site",
        "notes": "Student housing construction site near FSU. One of largest FL immigration raids. Joint operation with FBI, DEA, ATF, US Marshals, FDLE, IRS. Workers from Mexico, Guatemala, Nicaragua, El Salvador, Colombia, Honduras.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.ice.gov/news/releases/ice-arrests-100-illegal-aliens-during-targeted-enforcement-operation-tallahassee",
        "source_name": "ICE Official Release",
        "verified": True,
        "affected_count": 100,
        "outcome_category": "detained"
    },
    {
        "id": "T3-104",
        "date": "2025-05-27",
        "state": "Massachusetts",
        "city": "Martha's Vineyard / Nantucket",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_category": "enforcement_target",
        "victim_count": 40,
        "outcome": "40 detained across island vacation resorts",
        "notes": "Joint operation with FBI, DEA, ATF. Coast Guard provided boats. Workers disappeared from farms, lumberyards, ferryboats. Governor Healey got 'zero information' about arrests.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cbsnews.com/boston/news/ice-arrests-marthas-vineyard-nantucket-massachusetts/",
        "source_name": "CBS Boston",
        "verified": True,
        "affected_count": 40,
        "outcome_category": "detained"
    },
    {
        "id": "T3-105",
        "date": "2025-04-02",
        "state": "Washington",
        "city": "Bellingham",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_category": "enforcement_target",
        "victim_count": 37,
        "outcome": "37 workers detained at roofing company",
        "notes": "Mt. Baker Roofing Company. 56 falsified green cards found in 84 I-9 forms. Agents arrived with guns drawn at 7:30am. All 37 taken to Tacoma NWDC. Community raised funds for affected families.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.kuow.org/stories/ice-arrests-37-in-workplace-raid-at-bellingham-roofing-company",
        "source_name": "KUOW",
        "verified": True,
        "affected_count": 37,
        "outcome_category": "detained"
    },
    {
        "id": "T3-106",
        "date": "2025-06-11",
        "state": "Washington",
        "city": "Seattle",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "victim_category": "protester",
        "weapon_used": "pepper_spray",
        "arrest_count": 8,
        "outcome": "8 arrested, pepper spray deployed",
        "protest_related": True,
        "notes": "Protest from Cal Anderson Park to downtown, blocked 6th Ave/Seneca St. Dumpster fire set ~10 PM. Firework thrown at officers. 8 arrested for assault and obstruction.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.king5.com/article/news/local/protest-blocks-intersections-downtown-seattle-ice/281-5eb88df3-e1cf-4d92-811d-82a901b3cdab",
        "source_name": "King5",
        "verified": True,
        "affected_count": 8,
        "outcome_category": "arrested"
    },
    {
        "id": "T3-107",
        "date": "2026-01-10",
        "state": "Minnesota",
        "city": "Minneapolis",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "victim_category": "protester",
        "weapon_used": "tear_gas, pepper_spray",
        "arrest_count": 29,
        "outcome": "29 arrested, 1 officer injured by ice chunk",
        "protest_related": True,
        "notes": "~1,000 protesters after Renee Good shooting. Federal agents used tear gas and pepper spray. Officer struck by hurled ice chunk. $2M+ overtime costs for Minneapolis PD (Jan 8-11).",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-out-rally-minneapolis-immigration-protest-rcna255631",
        "source_name": "NBC News",
        "verified": True,
        "affected_count": 29,
        "outcome_category": "arrested"
    },
    {
        "id": "T3-108",
        "date": "2026-01-14",
        "state": "Minnesota",
        "city": "Minneapolis",
        "incident_type": "less_lethal",
        "protest_granularity": "bystander_injury",
        "victim_category": "bystander",
        "weapon_used": "tear_gas_canister",
        "victim_name": "Jackson family (6 children including 6-month-old)",
        "outcome": "6 family members hospitalized including infant",
        "notes": "Shawn and Destiny Jackson with 6 children tried to leave during protest. Tear gas canister rolled under car, set off airbags, filled vehicle with fumes. Mother performed CPR on 6-month-old who stopped breathing. 3 children + parents hospitalized.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cnn.com/us/live-news/ice-minnesota-minneapolis-maine-immigration-01-23-26",
        "source_name": "CNN",
        "verified": True,
        "affected_count": 8,
        "outcome_category": "serious_injury"
    },
    {
        "id": "T3-109",
        "date": "2025-08-07",
        "state": "Pennsylvania",
        "city": "Gibsonia / Cranberry Township",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_category": "enforcement_target",
        "victim_count": 16,
        "outcome": "16 workers detained at Mexican restaurant",
        "notes": "Emiliano's Mexican Restaurant (2 locations). Agents used assault rifles and battering ram. Restaurant accused agents of leaving 'trail of destruction': burned kitchen, torn ceiling tiles, broken doors, safe cut open. Prior June raid aborted when TV crews arrived. Community donated $133k+ for workers.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.nbcnews.com/news/latino/ice-raids-pittsburgh-mexican-restaurant-emilianos-pennsylvania-rcna224726",
        "source_name": "NBC News",
        "verified": True,
        "affected_count": 16,
        "outcome_category": "detained"
    },
    {
        "id": "T3-110",
        "date": "2025-02-07",
        "state": "Missouri",
        "city": "Liberty",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_category": "enforcement_target",
        "victim_count": 12,
        "outcome": "12 detained, 11 arrests later ruled unlawful",
        "notes": "El Potro Mexican Restaurant. Agents claimed searching for child sex offender. Workers held in booths 3 hours. Federal judge ruled 11 of 12 arrests unlawful (lacked probable cause). DHS ordered to pay attorney fees. Restaurant closed August citing labor challenges.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.kcur.org/news/2025-10-10/ice-kansas-city-el-potro-mexican-cafe-arrests-warrant",
        "source_name": "KCUR",
        "verified": True,
        "affected_count": 12,
        "outcome_category": "detained"
    }
]

# New Tier 4 incidents from agent searches
NEW_TIER4_INCIDENTS = [
    {
        "id": "T4-069",
        "date": "2025-06-17",
        "state": "California",
        "city": "Pico Rivera (Walmart)",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_category": "us_citizen_collateral",
        "victim_name": "Adrian Andrew Martinez",
        "victim_age": 20,
        "us_citizen": True,
        "outcome": "US citizen detained 3 days, fired by Walmart",
        "notes": "20-year-old US citizen Walmart employee detained during lunch break after questioning ICE agents. Video shows agents tackled him. Held at Metropolitan Detention Center. Fired by Walmart while in custody. Cuts and bruises from arrest. Charged with felony conspiracy.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://abc7.com/post/ice-raids-los-angeles-20-year-old-speaks-being-detained-federal-agents-pico-rivera/16902646/",
        "source_name": "ABC7 Los Angeles",
        "verified": True,
        "affected_count": 1,
        "outcome_category": "detained"
    },
    {
        "id": "T4-070",
        "date": "2026-01-13",
        "state": "Minnesota",
        "city": "Minneapolis",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_category": "us_citizen_collateral",
        "victim_name": "William Vermie",
        "victim_age": 39,
        "us_citizen": True,
        "outcome": "Army veteran detained 8 hours, no charges",
        "notes": "39-year-old US citizen, Army veteran (2004-2009, Iraq 2006-2007), Purple Heart recipient. Tackled while standing on sidewalk observing ICE detention. Denied phone call or attorney. DHS claimed 'assault' but no charges filed. Incident blocks from where Renee Good was shot.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://abcnews.go.com/US/army-vet-detained-ice-8-hours-allowed-call/story?id=129379081",
        "source_name": "ABC News",
        "verified": True,
        "affected_count": 1,
        "outcome_category": "released"
    },
    {
        "id": "T4-071",
        "date": "2026-01-05",
        "state": "North Carolina",
        "city": "Salisbury",
        "incident_type": "physical_force",
        "enforcement_granularity": "excessive_force",
        "victim_category": "us_citizen_collateral",
        "victim_name": "Edwin Godinez and Yair Napoles",
        "us_citizen": True,
        "outcome": "US citizen stepbrothers punched by agents",
        "notes": "Edwin Godinez (29, born California) and Yair Napoles (22, born NC). Stopped by ICE in unmarked vehicle. Officers demanded they stop recording, punched them in abdomen. Video went viral (millions of views). Filing complaint. Godinez reported nightmares, panic attacks.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.wunc.org/race-class-communities/2026-01-09/ice-officers-detained-assaulted-citizens-salisbury-nc",
        "source_name": "WUNC News",
        "verified": True,
        "affected_count": 2,
        "outcome_category": "injury"
    },
    {
        "id": "T4-072",
        "date": "2025-01-25",
        "state": "Wisconsin",
        "city": "Milwaukee",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_category": "us_citizen_collateral",
        "victim_name": "Puerto Rican family (toddler, mother, grandmother)",
        "us_citizen": True,
        "outcome": "US citizen family detained for speaking Spanish",
        "notes": "3-year-old toddler, mother, grandmother - all US citizens born in Puerto Rico. Detained while shopping after being overheard speaking Spanish. Not allowed to present ID until at detention center. ICE apologized but refused to drive them back.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://truthout.org/articles/family-us-citizens-shopping-in-milwaukee-was-detained-for-speaking-spanish/",
        "source_name": "Truthout",
        "verified": True,
        "affected_count": 3,
        "outcome_category": "released"
    },
    {
        "id": "T4-073",
        "date": "2025-12-10",
        "state": "Minnesota",
        "city": "Minneapolis (Cedar-Riverside)",
        "incident_type": "physical_force",
        "enforcement_granularity": "excessive_force",
        "victim_category": "us_citizen_collateral",
        "victim_name": "Mubashir Khalif Hussen",
        "victim_age": 20,
        "us_citizen": True,
        "outcome": "US citizen put in chokehold",
        "notes": "20-year-old US citizen. Told agents 'I'm a US citizen'; agent put him in chokehold. Minneapolis leaders condemned wrongful arrest.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.cbsnews.com/minnesota/news/minneapolis-leaders-say-us-citizen-was-wrongfully-arrested-by-ice-agents/",
        "source_name": "CBS Minnesota",
        "verified": True,
        "affected_count": 1,
        "outcome_category": "injury"
    },
    {
        "id": "T4-074",
        "date": "2025-08-21",
        "state": "Washington",
        "city": "Tacoma (Northwest Detention Center)",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_category": "enforcement_target",
        "victim_name": "Muhammad Zahid Chaudhry",
        "us_citizen": False,
        "outcome": "disabled Army veteran detained 4 months, ruled unlawful",
        "notes": "Disabled Army veteran, LPR since 2001, National Guard 2001-2005. Uses wheelchair. Detained at citizenship interview. Judge ruled detention unlawful, US Attorney apologized. Went 4 months without ophthalmologist despite thyroid eye disease. President of Veterans for Peace chapter.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.military.com/daily-news/2025/12/23/federal-judge-releases-disabled-veteran-ice-custody.html",
        "source_name": "Military.com",
        "verified": True,
        "affected_count": 1,
        "outcome_category": "released"
    },
    {
        "id": "T4-075",
        "date": "2025-04-15",
        "state": "Louisiana",
        "city": "New Orleans area",
        "incident_type": "wrongful_deportation",
        "enforcement_granularity": "wrongful_deportation",
        "victim_category": "us_citizen_collateral",
        "victim_name": "Romeo and siblings (3 US citizen children)",
        "us_citizen": True,
        "children_affected": True,
        "outcome": "3 US citizen children deported to Honduras",
        "notes": "Romeo (4-5yo with Stage 4 kidney cancer), 7yo sister, 2yo girl - all US citizens. Swept up with mothers, detained in hotel rooms incommunicado, deported within 1-2 days. Romeo deported without cancer medication. Lawsuit filed (J.L.V. v. Acuna).",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-deport-us-citizen-kids-stage-4-cancer-honduras-rcna224501",
        "source_name": "NBC News",
        "verified": True,
        "affected_count": 3,
        "outcome_category": "deported"
    },
    {
        "id": "T4-076",
        "date": "2025-06-15",
        "state": "Louisiana",
        "city": "Lakeview",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_category": "enforcement_target",
        "victim_name": "Mandonna Kashanian",
        "outcome": "Iranian grandmother detained while gardening",
        "notes": "Iranian grandmother, lived in US nearly 50 years, no criminal record. Detained by ICE while gardening outside home. Released after nearly 3 weeks when House Majority Leader Scalise and State Rep. Hilferty intervened.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://thehill.com/homenews/state-watch/5392114-iranian-grandmother-detained-by-ice-louisiana-scalise/",
        "source_name": "The Hill",
        "verified": True,
        "affected_count": 1,
        "outcome_category": "released"
    },
    {
        "id": "T4-077",
        "date": "2025-09-08",
        "state": "California",
        "city": "San Francisco Bay Area",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_category": "enforcement_target",
        "victim_name": "Harjit Kaur",
        "victim_age": 73,
        "outcome": "73-year-old grandmother detained at routine check-in",
        "notes": "73-year-old grandmother with legal status. Faithfully reported to ICE every 6 months for 13+ years. Detained at routine check-in in SF, transferred to Fresno then Bakersfield in handcuffs (arrived 3am). No criminal record. 10,000+ signed petition for release.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.nbcnews.com/news/us-news/california-grandmother-detained-ice-check-ins-immigration-rcna231685",
        "source_name": "NBC News",
        "verified": True,
        "affected_count": 1,
        "outcome_category": "detained"
    },
    {
        "id": "T4-078",
        "date": "2025-05-30",
        "state": "California",
        "city": "San Diego (South Park)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_category": "enforcement_target",
        "outcome": "12+ detained at Italian restaurant, flash bangs used",
        "notes": "Buona Forchetta restaurant. 20+ masked agents in military gear. Investigation began after 2020/2025 tips. 47.5% of workforce had fraudulent green cards. Flash bangs used to disperse crowd. Mayor Gloria called it 'deeply upsetting.' All 7 locations closed temporarily.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.kpbs.org/news/border-immigration/2025/05/30/ice-arrests-several-workers-from-south-park-restaurant",
        "source_name": "KPBS",
        "verified": True,
        "affected_count": 12,
        "outcome_category": "detained"
    },
    {
        "id": "T4-079",
        "date": "2025-09-02",
        "state": "Missouri",
        "city": "St. Peters",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_category": "enforcement_target",
        "victim_count": 12,
        "outcome": "12+ workers detained at Chinese buffet",
        "notes": "Golden Apple Buffet. Workers from China, Mexico, Indonesia. Agents used battering rams to enter employee housing. Two workers showering when agents pointed guns at them. Owners charged with 'bringing in and harboring aliens.' Restaurant reopened Sep 23.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.stlpr.org/show/st-louis-on-the-air/2025-11-03/immigration-raid-st-louis-targeted-food-workers-attorney-larger-crackdown",
        "source_name": "St. Louis Public Radio",
        "verified": True,
        "affected_count": 12,
        "outcome_category": "detained"
    },
    {
        "id": "T4-080",
        "date": "2025-05-09",
        "state": "New Jersey",
        "city": "Newark (Delaney Hall)",
        "incident_type": "physical_force",
        "protest_granularity": "individual_arrest",
        "victim_category": "protester",
        "victim_name": "Mayor Ras Baraka",
        "victim_occupation": "Newark Mayor",
        "us_citizen": True,
        "outcome": "Mayor arrested, charges later dropped",
        "protest_related": True,
        "notes": "Mayor Ras Baraka arrested by 12-20 ICE/HSI officers outside newly opened Delaney Hall. Three members of Congress present (Reps. Menendez, McIver, Watson Coleman). Protesters formed human shield. Rep. McIver later charged with assaulting federal officer. Baraka charges dropped.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.cnn.com/2025/05/09/us/new-jersey-mayor-arrested-at-ice-detention-center",
        "source_name": "CNN",
        "verified": True,
        "affected_count": 2,
        "outcome_category": "arrested"
    }
]


def main():
    print("=" * 60)
    print("Adding Validated Incidents and Fixing Schema Issues")
    print("=" * 60)

    # Fix tier3_incidents.json
    tier3_path = DATA_DIR / "tier3_incidents.json"
    with open(tier3_path, 'r', encoding='utf-8') as f:
        tier3 = json.load(f)

    # Get existing IDs
    existing_t3_ids = {r["id"] for r in tier3}

    # Fix scale mismatches
    fixed_t3 = fix_incident_scales(tier3)
    print(f"\nTier 3: Fixed {fixed_t3} incident_scale mismatches")

    # Add new incidents
    added_t3 = 0
    for incident in NEW_TIER3_INCIDENTS:
        if incident["id"] not in existing_t3_ids:
            incident = ensure_required_fields(incident)
            tier3.append(incident)
            added_t3 += 1
            print(f"  Added: {incident['id']} - {incident.get('city', incident.get('state'))}")

    print(f"Tier 3: Added {added_t3} new incidents")

    # Write tier3
    with open(tier3_path, 'w', encoding='utf-8') as f:
        json.dump(tier3, f, indent=2, ensure_ascii=False)

    # Fix tier4_incidents.json
    tier4_path = DATA_DIR / "tier4_incidents.json"
    with open(tier4_path, 'r', encoding='utf-8') as f:
        tier4 = json.load(f)

    # Get existing IDs
    existing_t4_ids = {r["id"] for r in tier4}

    # Fix scale mismatches
    fixed_t4 = fix_incident_scales(tier4)
    print(f"\nTier 4: Fixed {fixed_t4} incident_scale mismatches")

    # Add new incidents
    added_t4 = 0
    for incident in NEW_TIER4_INCIDENTS:
        if incident["id"] not in existing_t4_ids:
            incident = ensure_required_fields(incident)
            tier4.append(incident)
            added_t4 += 1
            print(f"  Added: {incident['id']} - {incident.get('city', incident.get('state'))}")

    print(f"Tier 4: Added {added_t4} new incidents")

    # Write tier4
    with open(tier4_path, 'w', encoding='utf-8') as f:
        json.dump(tier4, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"COMPLETE: Fixed {fixed_t3 + fixed_t4} scale issues, added {added_t3 + added_t4} new incidents")
    print("=" * 60)


if __name__ == "__main__":
    main()
