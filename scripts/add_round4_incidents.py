#!/usr/bin/env python3
"""
Add Round 4 incidents: State enforcement conflicts, legal challenges, detention resistance.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "incidents"


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


def ensure_required_fields(record):
    if "date_precision" not in record:
        record["date_precision"] = "day"
    if "affected_count" not in record:
        record["affected_count"] = record.get("victim_count", 1)
    record["incident_scale"] = get_incident_scale(record["affected_count"])
    if "outcome_detail" not in record and "outcome" in record:
        record["outcome_detail"] = record["outcome"]
    if "victim_category" not in record:
        record["victim_category"] = "enforcement_target"
    return record


# ============================================================================
# STATE-FEDERAL CONFLICTS AND SANCTUARY CITY INCIDENTS
# ============================================================================
NEW_STATE_CONFLICTS = [
    {
        "id": "T3-137",
        "date": "2025-06-07",
        "state": "California",
        "city": "Los Angeles",
        "incident_type": "protest",
        "enforcement_granularity": "state_federal_conflict",
        "elected_official": True,
        "official_title": "Governor Gavin Newsom",
        "affected_count": 4800,
        "outcome": "National Guard deployment challenged, eventually withdrawn",
        "outcome_detail": "Governor Newsom sued Trump administration after 4,100 National Guard troops and 700 Marines deployed to LA against his objections. September 2, U.S. District Judge Charles Breyer ruled deployment violated Posse Comitatus Act. By December 2025, troops reduced to 250 pending litigation. Court ruled federalization of Cal Guard was illegal.",
        "outcome_category": "released",
        "victim_category": "protester",
        "notes": "EXHAUSTIVE: June 2025 LA protests became largest confrontation over National Guard deployment. Trump federalized California National Guard under Joint Task Force 51, overriding Newsom who stated 'no need' for deployment. First presidential deployment without governor's request since 1965. Trump cited Title 10 authority; Newsom argued unconstitutional breach of state sovereignty. Border Czar Tom Homan threatened Newsom and Mayor Karen Bass could face federal charges. VP Vance called protesters 'insurrectionists.' Newsom gave televised speech calling deployment 'purposefully inflammatory.' Court found Trump's Title 10 authority used unlawfully.",
        "source_tier": 3,
        "source_url": "https://en.wikipedia.org/wiki/June_2025_Los_Angeles_protests_against_mass_deportation",
        "source_name": "Wikipedia/CalMatters/Washington Post",
        "verified": True
    },
    {
        "id": "T3-138",
        "date": "2025-10-06",
        "state": "Illinois",
        "city": "Chicago",
        "incident_type": "protest",
        "enforcement_granularity": "state_federal_conflict",
        "elected_official": True,
        "official_title": "Mayor Brandon Johnson, Governor JB Pritzker",
        "affected_count": 4000,
        "outcome": "Supreme Court blocked National Guard deployment 6-3",
        "outcome_detail": "Mayor Johnson signed executive order creating 'ICE-free zones' October 6, 2025, prohibiting city property for ICE staging. Governor Pritzker filed lawsuit calling deployment 'invasion.' December 23, 2025, Supreme Court ruled 6-3 Trump failed to identify legal authority under Posse Comitatus Act and Tenth Amendment. Operation Midway Blitz arrested 4,000+, but only 15% had criminal records.",
        "outcome_category": "released",
        "victim_category": "elected_official",
        "notes": "EXHAUSTIVE: Operation Midway Blitz began September 2025. Trump ordered 300 Illinois National Guard + 400 Texas National Guard to Chicago. October 9, US District Judge April Perry temporarily blocked deployment as unconstitutional. Pritzker called it 'absolutely outrageous and un-American.' DOJ sued Pritzker over state immigrant protection laws. Illinois AG Kwame Raoul: 'Defendants' deployment of federalized troops to Illinois is patently unlawful.' Lawsuit alleged federal agents used 'unprecedented brute force tactics' and 'shot chemical munitions at media and legal observers.' Justice Kavanaugh wrote concurrent opinion; Alito, Thomas, Gorsuch dissented. Cost to cities: $340 million per Senator Duckworth.",
        "source_tier": 3,
        "source_url": "https://www.cnn.com/2025/12/23/politics/supreme-court-blocks-trump-national-guard-chicago",
        "source_name": "CNN/Texas Tribune/Block Club Chicago",
        "verified": True
    },
    {
        "id": "T3-139",
        "date": "2025-05-09",
        "state": "New Jersey",
        "city": "Newark",
        "incident_type": "physical_force",
        "enforcement_granularity": "sanctuary_conflict",
        "victim_name": "Rep. LaMonica McIver",
        "elected_official": True,
        "official_title": "U.S. Representative (D-NJ)",
        "affected_count": 4,
        "outcome": "Congresswoman indicted on federal charges",
        "outcome_detail": "Rep. McIver indicted on three counts of assaulting, resisting, impeding federal officials following May 9 incident at Delaney Hall ICE facility. Two counts carry maximum 8-year prison sentences. Pleaded not guilty. November 2025, U.S. District Judge Jamel Semper rejected immunity defense under Speech or Debate Clause.",
        "outcome_category": "arrested",
        "victim_category": "elected_official",
        "notes": "EXHAUSTIVE: Delaney Hall is largest ICE detention center on East Coast, GEO Group operated under $1 billion 15-year contract. McIver was there with Reps. Watson Coleman and Menendez for congressional oversight. DOJ alleged McIver 'slammed forearm into one officer' and 'forcibly grabbed' another. Defense argued conduct covered by Speech or Debate Clause. McIver: charges are 'purely political' and 'meant to criminalize and deter legislative oversight.' US Attorney Alina Habba announced indictment. Newark sued GEO Group - facility lacked valid certificate of occupancy. Four detainees later escaped through drywall.",
        "source_tier": 3,
        "source_url": "https://www.cnn.com/2025/06/10/politics/lamonica-mciver-indicted-ice-detention-center",
        "source_name": "CNN/ABC News/NPR",
        "verified": True,
        "related_incidents": ["T3-052", "T4-080"]
    },
    {
        "id": "T3-140",
        "date": "2025-10-04",
        "state": "Oregon",
        "city": "Portland",
        "incident_type": "protest",
        "enforcement_granularity": "sanctuary_conflict",
        "affected_count": 128,
        "outcome": "National Guard deployment blocked, 128 arrested in protests",
        "outcome_detail": "October 4, 2025, Judge Karin Immergut granted TRO blocking federalization of Oregon National Guard. Trump attempted to deploy 200 Oregon Guard + 400 Texas + 300 California Guard. December 31, 2025, Trump officially abandoned Portland deployment. 128 arrested in protests as of October 2.",
        "outcome_category": "arrested",
        "victim_category": "protester",
        "notes": "EXHAUSTIVE: Portland codified sanctuary city status October 15, 2025, unanimously approving Protect Portland Initiative. Oregon was first sanctuary law state (1987). ICE Director Wamsley: facility faced violence 100+ consecutive nights with Portland police 'largely absent under guidance from mayor.' PPB Assistant Chief Dobson: federal police appeared to be 'instigating clashes' and 'not following best practice.' Oregon AG Dan Rayfield and Governor Newsom filed suit against cross-state Guard deployments. Trump signed Executive Order 14159 directing agencies to withhold sanctuary city funding.",
        "source_tier": 3,
        "source_url": "https://en.wikipedia.org/wiki/2025_Portland,_Oregon_protests",
        "source_name": "Wikipedia/OPB/Portland Mercury",
        "verified": True
    },
    {
        "id": "T3-141",
        "date": "2025-02-05",
        "state": "Colorado",
        "city": "Aurora/Denver",
        "incident_type": "mass_raid",
        "enforcement_granularity": "local_resistance",
        "affected_count": 30,
        "outcome": "30 detained, only 1 Tren de Aragua member found",
        "outcome_detail": "Part of 'Operation Aurora' targeting Tren de Aragua gang. Raids began 6 AM at Edge at Lowry apartments and Cedar Run Apartments. Despite targeting gang members, Fox News reported only 1 of 30 detained was actually TdA member. Border czar Homan blamed leak. Federal judge later sided with ACLU, granting preliminary injunction against warrantless apprehensions.",
        "outcome_category": "detained",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: ICE Acting Director Vitello: 'looking for Tren de Aragua.' Mayor Johnston: 'Denver Police and city authorities were not involved, nor given prior notice.' Aurora police also not involved. ACLU of Colorado challenged warrantless apprehensions as constitutional violations. Triggered 'No Kings' demonstrations and mass protests at state Capitol. Immigration arrests quintupled vs pre-Trump averages. Petition for 2026 ballot measure allowing police to cooperate with ICE received 200,000+ signatures.",
        "source_tier": 3,
        "source_url": "https://coloradosun.com/2025/02/05/ice-raids-aurora-denver/",
        "source_name": "Colorado Sun/Denver Post/CPR",
        "verified": True
    },
    {
        "id": "T3-142",
        "date": "2025-04-27",
        "state": "Colorado",
        "city": "Colorado Springs",
        "incident_type": "mass_raid",
        "enforcement_granularity": "multi_agency",
        "affected_count": 104,
        "outcome": "104 detained, 18 with final removal orders, 12 active-duty military caught",
        "outcome_detail": "Overnight raid on underground nightclub. Of 104 arrested: 18 had final deportation orders, 86 pending proceedings, 14 prior criminal records, 2 suspected Sinaloa Cartel ties. 12 active-duty military personnel detained as patrons or armed security. Army Staff Sgt. Juan Gabriel Orona-Rodriguez arrested April 30 on cocaine distribution charges.",
        "outcome_category": "detained",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: 300+ federal officers: DEA, ICE, HSI, FBI, US Marshals, Army CID, ATF, Colorado Springs police, El Paso and Douglas County sheriffs. Nightclub under DEA surveillance for months. Documented drug trafficking, prostitution, alleged Tren de Aragua, MS-13, Hells Angels presence. Seized 12 guns, cocaine, pink cocaine, meth. No federal/local charges except Army soldier. One of largest multi-agency raids in Colorado history.",
        "source_tier": 3,
        "source_url": "https://www.cnn.com/2025/04/27/us/colorado-springs-ice-raid-club",
        "source_name": "CNN/Colorado Sun/Denver Post",
        "verified": True
    },
    {
        "id": "T3-143",
        "date": "2025-04-21",
        "state": "Florida",
        "city": "Statewide",
        "incident_type": "mass_raid",
        "enforcement_granularity": "state_federal_cooperation",
        "elected_official": True,
        "official_title": "Governor Ron DeSantis",
        "affected_count": 1120,
        "outcome": "Largest single-state weekly arrest operation in ICE history",
        "outcome_detail": "Operation Tidal Wave April 21-26, 2025 arrested 1,120 people - largest in single state in one week in ICE history. 63% had existing criminal arrests/convictions. 378 had final removal orders. By January 2026, operation reached 10,000+ total. Florida has 325 287(g) agreements - 577% increase since January 20, 2025.",
        "outcome_category": "detained",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: Florida model = opposite of sanctuary states. DeSantis issued agreements with all 67 sheriffs. State agencies under 287(g): FDLE, FWC, Florida State Guard. FHP can enforce federal immigration laws without warrant. DeSantis: 'I have power to remove local officials from office and administer fines... It has teeth.' Federal funding: $10M to local agencies, $28.5M to state-level including $27.5M equipment for 3,676 officers. ACLU: ICE 'rushing training and lowering standards' with 'racial profiling' risks.",
        "source_tier": 3,
        "source_url": "https://www.flgov.com/eog/news/press/2025/largest-joint-immigration-operation-florida-history-leads-1120-criminal-alien",
        "source_name": "Florida Governor's Office/NPR/US News",
        "verified": True
    },
    {
        "id": "T3-144",
        "date": "2026-01-12",
        "state": "New York",
        "city": "New York City",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "sanctuary_conflict",
        "victim_name": "Rafael Andres Rubio Bohorquez",
        "elected_official": False,
        "victim_occupation": "NYC Council data analyst",
        "affected_count": 1,
        "outcome": "NYC Council employee detained at immigration appointment",
        "outcome_detail": "Rafael Andres Rubio Bohorquez, 53-year-old Venezuelan national working as NYC Council data analyst, detained during 'routine' immigration appointment on Long Island. Council Speaker Julie Menin claimed he was cleared to remain until October 2026. DHS said he has 'no authorization' and prior assault arrest. Mayor Mamdani called it 'egregious government overreach.'",
        "outcome_category": "detained",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: First major ICE confrontation for Mayor Zohran Mamdani, NYC's first socialist mayor (sworn in January 1, 2026). Mamdani: 'I am in support of abolishing ICE... an entity that has no interest in fulfilling its stated reason to exist.' DHS Assistant Secretary McLaughlin: 'shocking' that 'criminal illegal alien with no authorization' employed by City Council. Governor Hochul: 'This is exactly what happens when immigration enforcement is weaponized.'",
        "source_tier": 3,
        "source_url": "https://abcnews.go.com/US/mamdani-outraged-after-new-york-city-council-employee/story?id=129149275",
        "source_name": "ABC News/Fox News/City & State NY",
        "verified": True
    },
    {
        "id": "T3-145",
        "date": "2026-01-19",
        "state": "Minnesota",
        "city": "Minneapolis",
        "incident_type": "protest",
        "enforcement_granularity": "state_federal_conflict",
        "elected_official": True,
        "official_title": "Governor Tim Walz, Mayor Jacob Frey",
        "affected_count": 1360,
        "outcome": "DOJ investigation opened into governor and mayor",
        "outcome_detail": "DHS called on Governor Walz and Mayor Frey to honor ICE detainers for 1,360+ individuals in state custody. DOJ opened investigations into both for alleged conspiracy to impede immigration enforcement. Minnesota, Minneapolis, St. Paul filed lawsuit alleging Tenth Amendment violations and agents 'commandeered police resources.'",
        "outcome_category": "arrested",
        "victim_category": "elected_official",
        "notes": "EXHAUSTIVE: DHS deployed 2,000+ officers - largest immigration enforcement operation ever. St. Paul Mayor Kaohly Her (first woman and first Hmong mayor): agents 'going door to door targeting you by the way you look and sound.' DHS January 14, 2026 attacked Frey's 'sanctuary policies' for releasing 'criminal illegal aliens.' Coalition lawsuit alleges Tenth Amendment violation - reserve of policing powers to states. Most direct federal investigation of state/local officials for immigration non-cooperation.",
        "source_tier": 3,
        "source_url": "https://www.minneapolismn.gov/news/2026/january/ag-lawsuit/",
        "source_name": "City of Minneapolis/DHS/CBS Minnesota",
        "verified": True
    },
    {
        "id": "T3-146",
        "date": "2025-02-12",
        "state": "Colorado",
        "city": "Denver",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "school_protection",
        "victim_name": "Denver Public Schools",
        "children_affected": True,
        "affected_count": 90000,
        "outcome": "Lawsuit filed then dismissed after judge found policies similar",
        "outcome_detail": "Denver Public Schools (first school district to sue) filed lawsuit against Trump's rescission of sensitive locations policy. Student attendance dropped 3% in February 2025 (up to 4.7% at schools with many immigrant students). U.S. District Judge Daniel Domenico rejected attempt to reinstate policy, finding 'little practical difference.' DPS dismissed lawsuit without prejudice.",
        "outcome_category": "released",
        "victim_category": "bystander",
        "notes": "EXHAUSTIVE: DPS serves 90,000 students, 52% Latino. ~4,000 new immigrant students (mostly Venezuelan) by end of 2022. Lawsuit argued rescission violated APA, constitutional rights to religious freedom and due process, would deter access to essential services. January 20, 2025, Trump rescinded Biden-era sensitive locations policy (in place since 2011). New policy emphasized 'common sense' discretion with no hard limits. 1,400+ churches obtained federal injunction protection in Maryland. California passed laws limiting arrests at schools/universities/hospitals.",
        "source_tier": 3,
        "source_url": "https://www.chalkbeat.org/colorado/2025/02/13/denver-district-sues-ice-to-stop-immigration-enforcement-at-schools/",
        "source_name": "Chalkbeat/Denver Post/K-12 Dive",
        "verified": True
    },
    {
        "id": "T3-147",
        "date": "2025-12-09",
        "state": "Illinois",
        "city": "Springfield",
        "incident_type": "protest",
        "enforcement_granularity": "state_federal_conflict",
        "elected_official": True,
        "official_title": "Governor JB Pritzker",
        "affected_count": 1,
        "outcome": "Package of immigrant protection laws signed, DOJ countersued",
        "outcome_detail": "Governor Pritzker signed package of bills protecting immigrants as rebuke to Operation Midway Blitz. Laws stop courthouse arrests, require hospitals to prepare for ICE visits, protect daycares/colleges/universities, allow lawsuits against federal agents for constitutional violations. DOJ sued Pritzker and AG Raoul December 23, arguing laws 'threaten safety of federal officers.'",
        "outcome_category": "released",
        "victim_category": "elected_official",
        "notes": "EXHAUSTIVE: Represents escalating legal warfare between states and federal government. Illinois laws mirror California (limiting arrests at schools/hospitals, banning facial coverings, requiring officer identification). DOJ names both Pritzker and AG Raoul as defendants. One law enables individuals to sue federal agents for state or federal constitutional violations - potential chilling effect on enforcement.",
        "source_tier": 3,
        "source_url": "https://blockclubchicago.org/2025/12/09/gov-pritzker-signs-laws-to-better-protect-immigrants-sue-federal-agents-after-midway-blitz/",
        "source_name": "Block Club Chicago/CBS Chicago/Capitol News Illinois",
        "verified": True
    }
]

# Shootings to add to Tier 2
NEW_SHOOTINGS = [
    {
        "id": "T2-SA-008",
        "date": "2026-01-07",
        "state": "Minnesota",
        "city": "Minneapolis",
        "incident_type": "shooting_by_agent",
        "victim_name": "Renee Good",
        "victim_age": 37,
        "us_citizen": True,
        "victim_nationality": "American",
        "outcome": "US citizen killed by ICE agent, ruled homicide",
        "outcome_detail": "Renee Good, 37-year-old American citizen, fatally shot by ICE agent Jonathan Ross during Operation Metro Surge. Hennepin County Medical Examiner ruled death homicide. Video showed Good briefly reversed then moved forward/right; Ross fired three shots from front-left. Federal officials claimed self-defense. Mayor Frey: DHS claim she was weaponizing SUV was 'bullshit' and told ICE to 'get the fuck out of Minneapolis.' Governor Walz proclaimed January 9 'Renee Good Day.'",
        "outcome_category": "death",
        "victim_category": "bystander",
        "notes": "EXHAUSTIVE: Operation Metro Surge began December 2025 as largest ICE operation ever - 2,000+ agents in Twin Cities. DOJ opened investigations into Mayor Frey and Governor Walz for alleged conspiracy to impede enforcement. Minnesota AG Keith Ellison, Minneapolis and St. Paul filed lawsuit alleging Tenth Amendment violations. Rep. Robin Kelly (IL) introduced impeachment articles for DHS Secretary Noem January 14, 2026. AP-NORC poll: Trump immigration approval dropped from 50-49% in March 2025 to 61% disapproval by mid-January 2026.",
        "source_tier": 2,
        "source_url": "https://en.wikipedia.org/wiki/Killing_of_Ren%C3%A9e_Good",
        "source_name": "Wikipedia/MPR News/CBS Minnesota",
        "verified": True,
        "affected_count": 1,
        "related_incidents": ["T1-S-001"]
    },
    {
        "id": "T2-SA-009",
        "date": "2026-01-24",
        "state": "Minnesota",
        "city": "Minneapolis",
        "incident_type": "shooting_by_agent",
        "victim_name": "Alex Pretti",
        "victim_age": 37,
        "us_citizen": True,
        "victim_nationality": "American",
        "victim_occupation": "ICU nurse at Minneapolis VA hospital",
        "outcome": "US citizen ICU nurse killed by Border Patrol agent",
        "outcome_detail": "Alex Pretti, 37-year-old American ICU nurse at Minneapolis VA hospital, shot and killed by Border Patrol agents. Video showed Pretti filming agents with phone and directing traffic. Stood between agent and woman pushed to ground. Pepper-sprayed, wrestled to ground by several agents, then shot 10 times over 5 seconds. Agents yelled about gun ~8 seconds after Pretti pinned. Video reviewed by Reuters and WSJ appeared to show agent removing gun and moving away <1 second before another agent fired.",
        "outcome_category": "death",
        "victim_category": "bystander",
        "notes": "EXHAUSTIVE: Second US citizen killed during Operation Metro Surge. Pretti was AFGE member, had active nursing license, Minnesota permit to carry, no serious criminal history (only traffic tickets). DHS alleged Pretti approached with 9mm and 'violently resisted'; local officials disputed. Two witnesses gave sworn testimony Pretti did not brandish gun. Video showed phone in right hand, nothing in left. Mayor Frey: only 3 homicides in Minneapolis in 2026 so far, 2 were by federal agents. Minnesota National Guard activated. Judge granted restraining order against DHS. Third federal agent shooting in <3 weeks.",
        "source_tier": 2,
        "source_url": "https://en.wikipedia.org/wiki/Killing_of_Alex_Pretti",
        "source_name": "Wikipedia/PBS/ABC News",
        "verified": True,
        "affected_count": 1,
        "related_incidents": ["T1-S-002"]
    }
]


def add_incidents_to_file(filepath, new_incidents, label):
    """Add new incidents to a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    existing_ids = {r["id"] for r in existing}

    existing_keys = set()
    for r in existing:
        name = r.get('victim_name', '').lower() if r.get('victim_name') else ''
        date = r.get('date', '')
        if name and date:
            existing_keys.add((name, date))

    added = 0
    skipped = 0

    for incident in new_incidents:
        if incident["id"] in existing_ids:
            skipped += 1
            continue

        name = incident.get('victim_name', '').lower() if incident.get('victim_name') else ''
        date = incident.get('date', '')
        if name and date and (name, date) in existing_keys:
            print(f"  SKIPPED (dupe): {incident['id']} - {name} on {date}")
            skipped += 1
            continue

        incident = ensure_required_fields(incident)
        existing.append(incident)
        added += 1
        city = incident.get('city', incident.get('facility', incident.get('state')))
        print(f"  Added: {incident['id']} - {city}")

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    return added, skipped, len(existing)


def main():
    print("=" * 70)
    print("Adding Round 4 Incidents: State-Federal Conflicts")
    print("=" * 70)

    # Tier 2: Shootings
    print("\n[TIER 2: SHOOTINGS BY AGENTS]")
    added, skipped, total = add_incidents_to_file(
        DATA_DIR / "tier2_shootings.json",
        NEW_SHOOTINGS,
        "T2-SA"
    )
    print(f"Added {added} new shootings (skipped {skipped}), total now: {total}")

    # Tier 3: State-Federal Conflicts
    print("\n[TIER 3: STATE-FEDERAL CONFLICTS]")
    added, skipped, total = add_incidents_to_file(
        DATA_DIR / "tier3_incidents.json",
        NEW_STATE_CONFLICTS,
        "T3"
    )
    print(f"Added {added} new incidents (skipped {skipped}), total now: {total}")

    print("\n" + "=" * 70)
    print("COMPLETE: Round 4 incidents added")
    print("=" * 70)


if __name__ == "__main__":
    main()
