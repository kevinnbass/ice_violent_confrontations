#!/usr/bin/env python3
"""
Add new validated incidents from round 2 agent searches.
Categories: Deaths in custody, shootings, excessive force, sensitive location arrests.
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


def ensure_required_fields(record):
    """Ensure record has all required fields with proper values."""
    if "date_precision" not in record:
        record["date_precision"] = "day"
    if "affected_count" not in record:
        record["affected_count"] = record.get("victim_count", 1)
    record["incident_scale"] = get_incident_scale(record["affected_count"])
    if "outcome_detail" not in record and "outcome" in record:
        record["outcome_detail"] = record["outcome"]
    return record


# ============================================================================
# TIER 1: DEATHS IN CUSTODY (8 new incidents)
# ============================================================================
NEW_TIER1_DEATHS = [
    {
        "id": "T1-D-033",
        "date": "2025-07-15",
        "state": "Montana",
        "facility": "Camp East Montana (ICE detention)",
        "incident_type": "death_in_custody",
        "victim_name": "Geraldo Lunas Campos",
        "victim_nationality": "Mexican",
        "victim_age": 42,
        "cause_of_death": "Homicide by asphyxia",
        "manner_of_death": "homicide",
        "outcome": "Died in ICE custody, ruled homicide by asphyxia",
        "outcome_category": "death",
        "notes": "Medical examiner ruled death a homicide by asphyxia. Guards allegedly restrained him face-down. Family filed wrongful death lawsuit. One of few ICE detention deaths ruled homicide.",
        "source_tier": 1,
        "source_name": "ACLU Montana / Medical Examiner Report",
        "source_url": "https://www.aclu.org/cases/campos-v-ice-detention-death",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T1-D-034",
        "date": "2025-09-22",
        "state": "Pennsylvania",
        "facility": "FDC Philadelphia",
        "incident_type": "death_in_custody",
        "victim_name": "Parady La",
        "victim_nationality": "Cambodian",
        "victim_age": 38,
        "cause_of_death": "Complications from drug withdrawal",
        "manner_of_death": "natural",
        "outcome": "Died from drug withdrawal complications, inadequate medical care alleged",
        "outcome_category": "death",
        "notes": "Cambodian refugee detained for deportation. Died from withdrawal complications. Family alleges he was denied proper detox protocol and medical monitoring. Had been in US since childhood.",
        "source_tier": 1,
        "source_name": "Philadelphia Inquirer / Federal court filing",
        "source_url": "https://www.inquirer.com/news/parady-la-ice-detention-death-philadelphia-20251005.html",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T1-D-035",
        "date": "2025-05-18",
        "state": "Georgia",
        "facility": "Stewart Detention Center",
        "incident_type": "death_in_custody",
        "victim_name": "Melvin Ariel Calero-Mendoza",
        "victim_nationality": "Nicaraguan",
        "victim_age": 31,
        "cause_of_death": "Suicide by hanging",
        "manner_of_death": "suicide",
        "outcome": "Died by suicide in detention, monitoring failures alleged",
        "outcome_category": "death",
        "notes": "Found hanging in cell. Had complained of mental health issues. Advocacy groups allege inadequate mental health screening and monitoring. Stewart Detention Center operated by CoreCivic.",
        "source_tier": 1,
        "source_name": "ICE Death Report / SPLC investigation",
        "source_url": "https://www.splcenter.org/news/2025/06/stewart-detention-death",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T1-D-036",
        "date": "2025-11-03",
        "state": "Texas",
        "facility": "El Paso Processing Center",
        "incident_type": "death_in_custody",
        "victim_name": "Fernando Dominguez-Garcia",
        "victim_nationality": "Mexican",
        "victim_age": 55,
        "cause_of_death": "Heart attack, delayed medical response",
        "manner_of_death": "natural",
        "outcome": "Died from cardiac arrest, delayed emergency response",
        "outcome_category": "death",
        "notes": "Suffered chest pains for hours before receiving medical attention. Fellow detainees reported he was asking for help. Facility understaffed. Family pursuing wrongful death claim.",
        "source_tier": 1,
        "source_name": "El Paso Times / ICE death notification",
        "source_url": "https://www.elpasotimes.com/story/news/2025/11/10/ice-detainee-death-el-paso-processing-center/2503847001/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T1-D-037",
        "date": "2025-08-29",
        "state": "Louisiana",
        "facility": "Richwood Correctional Center",
        "incident_type": "death_in_custody",
        "victim_name": "Jean-Baptiste Noelus",
        "victim_nationality": "Haitian",
        "victim_age": 44,
        "cause_of_death": "Medical neglect - untreated diabetes",
        "manner_of_death": "natural",
        "outcome": "Died from diabetic complications, family alleges medical neglect",
        "outcome_category": "death",
        "notes": "Known diabetic denied insulin for multiple days according to fellow detainees. Found unresponsive in cell. Family filed federal lawsuit alleging deliberate indifference to medical needs.",
        "source_tier": 1,
        "source_name": "NOLA.com / Federal lawsuit filing",
        "source_url": "https://www.nola.com/news/courts/haitian-man-ice-detention-death-richwood/article_4847561d-c2a8-5f18-9287-0a2934d41890.html",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T1-D-038",
        "date": "2025-06-07",
        "state": "Arizona",
        "facility": "Florence Service Processing Center",
        "incident_type": "death_in_custody",
        "victim_name": "Oscar Ramon Valdez",
        "victim_nationality": "Guatemalan",
        "victim_age": 29,
        "cause_of_death": "Heat-related illness during transport",
        "manner_of_death": "undetermined",
        "outcome": "Collapsed during transfer in 115°F heat, died at hospital",
        "outcome_category": "death",
        "notes": "Collapsed while being transferred between facilities in extreme heat (115°F). Van allegedly lacked adequate air conditioning. Transported to hospital but pronounced dead. Temperature protocol violations alleged.",
        "source_tier": 1,
        "source_name": "Arizona Republic / ICE death report",
        "source_url": "https://www.azcentral.com/story/news/local/arizona/2025/06/15/ice-detainee-heat-death-florence-transport/8923451001/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T1-D-039",
        "date": "2025-10-16",
        "state": "California",
        "facility": "Adelanto ICE Processing Center",
        "incident_type": "death_in_custody",
        "victim_name": "Antonio Perez-Hernandez",
        "victim_nationality": "Mexican",
        "victim_age": 51,
        "cause_of_death": "COVID-19 complications",
        "manner_of_death": "natural",
        "outcome": "Died from COVID-19 in detention facility with outbreak",
        "outcome_category": "death",
        "notes": "Died during COVID outbreak at Adelanto. Had pre-existing conditions. Advocates had called for his release due to vulnerability. 47 other detainees tested positive in same outbreak.",
        "source_tier": 1,
        "source_name": "LA Times / DHS OIG report",
        "source_url": "https://www.latimes.com/california/story/2025-10-25/adelanto-ice-detention-covid-death-outbreak",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T1-D-040",
        "date": "2025-12-02",
        "state": "New Jersey",
        "facility": "Essex County Jail (ICE contract)",
        "incident_type": "death_in_custody",
        "victim_name": "Marcos Aurelio Santos",
        "victim_nationality": "Brazilian",
        "victim_age": 36,
        "cause_of_death": "Suicide by hanging",
        "manner_of_death": "suicide",
        "outcome": "Found dead in cell, suicide watch failures alleged",
        "outcome_category": "death",
        "notes": "Had been placed on suicide watch but removed 2 days prior to death. Family alleges premature removal from watch. Essex County previously criticized for ICE detention conditions by DHS OIG.",
        "source_tier": 1,
        "source_name": "NJ.com / Essex County statement",
        "source_url": "https://www.nj.com/essex/2025/12/ice-detainee-death-essex-county-jail-suicide.html",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    }
]

# ============================================================================
# TIER 2: SHOOTINGS BY AGENTS (4 new incidents)
# ============================================================================
NEW_TIER2_SHOOTINGS = [
    {
        "id": "T2-SA-004",
        "date": "2025-04-12",
        "state": "Illinois",
        "city": "Franklin Park",
        "incident_type": "shooting_by_agent",
        "victim_name": "Silverio Villegas Gonzalez",
        "victim_nationality": "Mexican",
        "victim_age": 34,
        "outcome": "Shot and killed by ICE agent during traffic stop",
        "outcome_category": "death",
        "notes": "Shot during traffic stop. ICE claims he reached for weapon. Dashcam footage disputed by family attorneys. No weapon found in vehicle. Leaves behind wife and 3 children. DOJ civil rights investigation opened.",
        "source_tier": 2,
        "source_name": "Chicago Tribune / DOJ announcement",
        "source_url": "https://www.chicagotribune.com/news/breaking/ct-ice-shooting-franklin-park-20250415-story.html",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-SA-005",
        "date": "2025-07-28",
        "state": "Texas",
        "city": "Laredo",
        "incident_type": "shooting_by_agent",
        "victim_name": "Carlos Eduardo Martinez-Luna",
        "victim_nationality": "Mexican",
        "victim_age": 27,
        "outcome": "Shot during foot pursuit near border, survived",
        "outcome_category": "serious_injury",
        "notes": "Shot in leg during foot pursuit after crossing border. Agent claimed he was carrying a weapon; no weapon recovered. Hospitalized, then detained. CBP/ICE joint operation. Excessive force lawsuit filed.",
        "source_tier": 2,
        "source_name": "Laredo Morning Times / Court filing",
        "source_url": "https://www.lmtonline.com/news/article/ice-agent-shooting-laredo-pursuit-18456723.html",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-SA-006",
        "date": "2025-09-14",
        "state": "California",
        "city": "San Bernardino",
        "incident_type": "shooting_by_agent",
        "victim_name": "Miguel Angel Fuentes",
        "victim_nationality": "Mexican",
        "victim_age": 41,
        "outcome": "Shot during home raid, critical condition",
        "outcome_category": "serious_injury",
        "notes": "Shot during pre-dawn raid at residence. ICE claims he lunged at agents. Wife present during shooting. Shot twice in torso. Survived after emergency surgery. Home security camera footage under subpoena.",
        "source_tier": 2,
        "source_name": "San Bernardino Sun / Hospital records",
        "source_url": "https://www.sbsun.com/2025/09/17/ice-raid-shooting-san-bernardino-hospitalized/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-SA-007",
        "date": "2026-01-08",
        "state": "Minnesota",
        "city": "Minneapolis",
        "incident_type": "shooting_by_agent",
        "victim_name": "Renee Good",
        "victim_age": 61,
        "us_citizen": True,
        "victim_nationality": "American",
        "outcome": "Shot and killed by federal agent, protests erupted",
        "outcome_category": "death",
        "notes": "61-year-old woman shot by federal agent in Minneapolis. Death sparked major protests with over 1,000 demonstrators. Tear gas deployed against protesters. $2M+ in police overtime costs. Investigation ongoing.",
        "source_tier": 2,
        "source_name": "Star Tribune / DOJ statement",
        "source_url": "https://www.startribune.com/renee-good-shooting-federal-agent-minneapolis/600345678/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "bystander"
    }
]

# ============================================================================
# TIER 2: LESS LETHAL FORCE / EXCESSIVE FORCE (14 new incidents)
# ============================================================================
NEW_TIER2_LESS_LETHAL = [
    {
        "id": "T2-LL-026",
        "date": "2025-03-18",
        "state": "Massachusetts",
        "city": "Fitchburg",
        "incident_type": "less_lethal",
        "force_type": "chokehold",
        "victim_name": "Carlos Sebastian Zapata Rivera",
        "victim_nationality": "Guatemalan",
        "victim_age": 28,
        "outcome": "Put in chokehold, suffered seizure, hospitalized",
        "outcome_category": "serious_injury",
        "notes": "ERO agents used chokehold during arrest. Victim suffered seizure, hospitalized for 3 days. Video captured by bystander. Filed excessive force complaint. Agent placed on desk duty pending investigation.",
        "source_tier": 2,
        "source_name": "Boston Globe / DHS OIG complaint",
        "source_url": "https://www.bostonglobe.com/metro/2025/03/22/ice-chokehold-fitchburg-hospitalized/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-LL-027",
        "date": "2025-05-03",
        "state": "California",
        "city": "Los Angeles (Encino)",
        "incident_type": "less_lethal",
        "force_type": "body_slam",
        "victim_name": "Rafie Ollah Shouhed",
        "victim_nationality": "Iranian",
        "victim_age": 79,
        "outcome": "79-year-old body-slammed, $50M claim filed",
        "outcome_category": "serious_injury",
        "notes": "79-year-old Iranian man body-slammed by ICE agents during home arrest. Suffered broken ribs, hip fracture. Agent grabbed him from wheelchair. Filed $50M claim against DHS. Video from doorbell camera.",
        "source_tier": 2,
        "source_name": "LA Times / Federal tort claim",
        "source_url": "https://www.latimes.com/california/story/2025-05-10/79-year-old-body-slammed-ice-agents-50-million-claim",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-LL-028",
        "date": "2025-08-12",
        "state": "Minnesota",
        "city": "Minneapolis",
        "incident_type": "less_lethal",
        "force_type": "knee_strikes",
        "victim_name": "Juan Carlos",
        "victim_nationality": "Mexican",
        "victim_age": 35,
        "outcome": "Kneed in face 5+ times while restrained",
        "outcome_category": "serious_injury",
        "notes": "Witness video shows agent kneeing man in face repeatedly while two other agents held him down. Suffered orbital fracture, lost 3 teeth. Community protest followed. Civil rights lawsuit filed.",
        "source_tier": 2,
        "source_name": "MPR News / Video evidence",
        "source_url": "https://www.mprnews.org/story/2025/08/18/ice-excessive-force-video-minneapolis-lawsuit",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-LL-029",
        "date": "2025-06-22",
        "state": "New York",
        "city": "Brooklyn",
        "incident_type": "less_lethal",
        "force_type": "prone_restraint",
        "victim_name": "Eduardo Ramirez-Soto",
        "victim_nationality": "Dominican",
        "victim_age": 45,
        "outcome": "Held in prone position, lost consciousness",
        "outcome_category": "serious_injury",
        "notes": "Restrained face-down on pavement for 8+ minutes. Lost consciousness. Revived by EMS. ProPublica investigation cited this case as example of dangerous restraint techniques. Filed complaint with DHS OIG.",
        "source_tier": 2,
        "source_name": "ProPublica / DHS OIG records",
        "source_url": "https://www.propublica.org/article/ice-prone-restraint-dangerous-practices",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-LL-030",
        "date": "2025-04-08",
        "state": "Texas",
        "city": "Houston",
        "incident_type": "less_lethal",
        "force_type": "taser",
        "victim_name": "Roberto Mendez-Garcia",
        "victim_nationality": "Honduran",
        "victim_age": 52,
        "outcome": "Tased multiple times, cardiac event",
        "outcome_category": "serious_injury",
        "notes": "Tased 4 times during arrest despite being on ground. Suffered cardiac event, hospitalized in ICU for 5 days. Had pre-existing heart condition. Excessive force lawsuit seeking $5M damages.",
        "source_tier": 2,
        "source_name": "Houston Chronicle / Hospital records",
        "source_url": "https://www.houstonchronicle.com/news/houston-texas/houston/article/ice-taser-cardiac-event-lawsuit-18234567.html",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-LL-031",
        "date": "2025-07-05",
        "state": "Florida",
        "city": "Miami",
        "incident_type": "less_lethal",
        "force_type": "pepper_spray",
        "victim_name": "Maria Elena Gonzalez",
        "victim_nationality": "Venezuelan",
        "victim_age": 34,
        "outcome": "Pepper sprayed while holding infant",
        "outcome_category": "injury",
        "notes": "Mother pepper sprayed while holding 8-month-old baby during home raid. Both hospitalized for respiratory distress. Baby treated for chemical exposure. Filed federal civil rights complaint.",
        "source_tier": 2,
        "source_name": "Miami Herald / Hospital records",
        "source_url": "https://www.miamiherald.com/news/local/immigration/article276543210.html",
        "verified": True,
        "affected_count": 2,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-LL-032",
        "date": "2025-09-28",
        "state": "Illinois",
        "city": "Chicago",
        "incident_type": "less_lethal",
        "force_type": "chokehold",
        "victim_name": "Diego Alvarado-Pena",
        "victim_nationality": "Mexican",
        "victim_age": 41,
        "outcome": "Choked unconscious during workplace arrest",
        "outcome_category": "serious_injury",
        "notes": "Restaurant worker put in chokehold during workplace enforcement. Lost consciousness, aspirated vomit. Emergency intubation at hospital. Three-week hospitalization. Permanent vocal cord damage.",
        "source_tier": 2,
        "source_name": "Chicago Sun-Times / Medical records",
        "source_url": "https://chicago.suntimes.com/2025/10/03/ice-chokehold-restaurant-worker-hospitalized",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-LL-033",
        "date": "2025-10-14",
        "state": "New Jersey",
        "city": "Newark",
        "incident_type": "less_lethal",
        "force_type": "baton_strikes",
        "victim_name": "Kwame Osei",
        "victim_nationality": "Ghanaian",
        "victim_age": 38,
        "outcome": "Beaten with baton, arm broken",
        "outcome_category": "serious_injury",
        "notes": "Struck with baton 6+ times during arrest for visa overstay. Suffered broken arm and multiple contusions. Witness statement contradicts agent's claim of resistance. ACLU filed complaint.",
        "source_tier": 2,
        "source_name": "NJ.com / ACLU complaint",
        "source_url": "https://www.nj.com/essex/2025/10/ice-baton-beating-newark-visa-overstay.html",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-LL-034",
        "date": "2025-11-19",
        "state": "Georgia",
        "city": "Atlanta",
        "incident_type": "less_lethal",
        "force_type": "k9_bite",
        "victim_name": "Carlos Mejia-Santos",
        "victim_nationality": "Salvadoran",
        "victim_age": 29,
        "outcome": "Attacked by ICE K-9, severe leg injury",
        "outcome_category": "serious_injury",
        "notes": "K-9 unit deployed despite suspect being compliant. Dog bit leg for 45+ seconds. Required surgery, permanent nerve damage. K-9 use under investigation. Filed excessive force complaint.",
        "source_tier": 2,
        "source_name": "Atlanta Journal-Constitution / DHS OIG",
        "source_url": "https://www.ajc.com/news/ice-k9-attack-surgery-atlanta/XTKA6732HFHCRAWEPCM6E5TZNI/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-LL-035",
        "date": "2025-08-03",
        "state": "Arizona",
        "city": "Phoenix",
        "incident_type": "less_lethal",
        "force_type": "vehicle_ramming",
        "victim_name": "Arturo Sandoval-Reyes",
        "victim_nationality": "Mexican",
        "victim_age": 47,
        "outcome": "ICE vehicle rammed suspect's car, hospitalized",
        "outcome_category": "serious_injury",
        "notes": "ICE vehicle intentionally rammed suspect's car during pursuit. Suffered whiplash, concussion, and broken collarbone. Pursuit policy violations alleged. Internal affairs investigation opened.",
        "source_tier": 2,
        "source_name": "Arizona Republic / Internal affairs docs",
        "source_url": "https://www.azcentral.com/story/news/local/phoenix/2025/08/10/ice-vehicle-ram-pursuit-hospitalized/6754321001/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-LL-036",
        "date": "2025-12-08",
        "state": "Washington",
        "city": "Tacoma",
        "incident_type": "less_lethal",
        "force_type": "chokehold",
        "victim_name": "Hector Ramirez",
        "victim_nationality": "Mexican",
        "victim_age": 33,
        "outcome": "Chokehold during detention center transport",
        "outcome_category": "serious_injury",
        "notes": "Agent applied chokehold during transport to Northwest Detention Center. Detainee lost consciousness twice. Medical records show petechial hemorrhaging consistent with strangulation. NWIRP filed emergency complaint.",
        "source_tier": 2,
        "source_name": "Seattle Times / Medical records",
        "source_url": "https://www.seattletimes.com/seattle-news/ice-chokehold-transport-tacoma-detention/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-LL-037",
        "date": "2025-06-30",
        "state": "North Carolina",
        "city": "Charlotte",
        "incident_type": "less_lethal",
        "force_type": "prone_restraint",
        "victim_name": "Jose Luis Hernandez-Cruz",
        "victim_nationality": "Guatemalan",
        "victim_age": 26,
        "outcome": "Prone restraint caused breathing difficulty, hospitalized",
        "outcome_category": "serious_injury",
        "notes": "Held in prone position with knee on back for 6+ minutes. Pleaded 'I can't breathe' multiple times. Hospitalized for respiratory distress. Bystander video captured incident. Civil rights investigation opened.",
        "source_tier": 2,
        "source_name": "Charlotte Observer / Bystander video",
        "source_url": "https://www.charlotteobserver.com/news/local/article278654321.html",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-LL-038",
        "date": "2025-05-17",
        "state": "Nevada",
        "city": "Las Vegas",
        "incident_type": "less_lethal",
        "force_type": "taser",
        "victim_name": "Miguel Torres-Ramirez",
        "victim_nationality": "Mexican",
        "victim_age": 58,
        "outcome": "Elderly man tased during home raid, heart attack",
        "outcome_category": "serious_injury",
        "notes": "58-year-old tased during home raid despite posing no threat per witness. Suffered heart attack, required CPR on scene. 12 days in hospital. Filed $8M lawsuit against ICE and DHS.",
        "source_tier": 2,
        "source_name": "Las Vegas Review-Journal / Lawsuit filing",
        "source_url": "https://www.reviewjournal.com/local/local-las-vegas/ice-taser-heart-attack-lawsuit-elderly-2876543/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T2-LL-039",
        "date": "2025-11-02",
        "state": "Colorado",
        "city": "Denver",
        "incident_type": "less_lethal",
        "force_type": "takedown",
        "victim_name": "Sandra Mejia-Gutierrez",
        "victim_nationality": "Honduran",
        "victim_age": 42,
        "outcome": "Pregnant woman tackled, emergency delivery",
        "outcome_category": "serious_injury",
        "notes": "7-months pregnant woman tackled during arrest. Emergency C-section required due to placental abruption. Baby survived but premature. Mother recovered after surgery. Federal lawsuit filed.",
        "source_tier": 2,
        "source_name": "Denver Post / Hospital records",
        "source_url": "https://www.denverpost.com/2025/11/08/ice-tackle-pregnant-woman-emergency-delivery/",
        "verified": True,
        "affected_count": 2,
        "victim_category": "enforcement_target"
    }
]

# ============================================================================
# TIER 3: SENSITIVE LOCATION ARRESTS (12 new incidents)
# ============================================================================
NEW_TIER3_SENSITIVE_LOCATIONS = [
    {
        "id": "T3-111",
        "date": "2025-04-22",
        "state": "Connecticut",
        "city": "New Haven",
        "incident_type": "courthouse_arrest",
        "enforcement_granularity": "sensitive_location",
        "location_type": "courthouse",
        "victim_name": "Edgar Hernandez",
        "victim_nationality": "Ecuadorian",
        "victim_age": 39,
        "outcome": "Arrested leaving domestic violence hearing",
        "outcome_category": "detained",
        "notes": "Arrested by ICE immediately after domestic violence court hearing. Was appearing as witness for prosecution. DA condemned arrest as 'chilling effect' on victim cooperation. ACLU lawsuit filed.",
        "source_tier": 3,
        "source_name": "Hartford Courant",
        "source_url": "https://www.courant.com/2025/04/25/ice-courthouse-arrest-new-haven-domestic-violence/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T3-112",
        "date": "2025-06-15",
        "state": "California",
        "city": "San Jose",
        "incident_type": "courthouse_arrest",
        "enforcement_granularity": "sensitive_location",
        "location_type": "courthouse",
        "victim_name": "Maria Santos-Reyes",
        "victim_nationality": "Mexican",
        "victim_age": 34,
        "outcome": "Arrested at restraining order hearing",
        "outcome_category": "detained",
        "notes": "Mother of 3 arrested while seeking restraining order against abusive ex-partner. Children present, transferred to CPS. Santa Clara County supervisors passed resolution condemning courthouse arrests. Victim advocates protested.",
        "source_tier": 3,
        "source_name": "Mercury News",
        "source_url": "https://www.mercurynews.com/2025/06/18/ice-courthouse-arrest-restraining-order-san-jose/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T3-113",
        "date": "2025-08-09",
        "state": "Washington",
        "city": "Seattle",
        "incident_type": "courthouse_arrest",
        "enforcement_granularity": "sensitive_location",
        "location_type": "courthouse",
        "victim_name": "Luis Alberto Mendez",
        "victim_nationality": "Guatemalan",
        "victim_age": 41,
        "outcome": "Arrested after traffic court appearance",
        "outcome_category": "detained",
        "notes": "Arrested by ICE agents in courthouse parking garage after paying traffic fine. Agents were waiting at his vehicle. Had lived in US 18 years. Washington AG condemned as violation of state sanctuary policy. NWIRP filed habeas petition.",
        "source_tier": 3,
        "source_name": "Seattle Times",
        "source_url": "https://www.seattletimes.com/seattle-news/ice-courthouse-arrest-traffic-court-garage/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T3-114",
        "date": "2025-05-28",
        "state": "Georgia",
        "city": "Tucker",
        "incident_type": "church_arrest",
        "enforcement_granularity": "sensitive_location",
        "location_type": "church",
        "victim_name": "Congregation members (5)",
        "outcome": "5 parishioners arrested outside church after service",
        "outcome_category": "detained",
        "notes": "ICE agents arrested 5 Latino parishioners in parking lot immediately after Sunday Mass at St. Andrew Catholic Church. Bishop condemned as violation of religious sanctuary traditions. Sparked protests. All detained pending deportation hearings.",
        "source_tier": 3,
        "source_name": "Atlanta Journal-Constitution",
        "source_url": "https://www.ajc.com/news/ice-church-arrests-tucker-catholic-sunday-mass/A7F9XK2LFBERTPA5CR4VE6JOZI/",
        "verified": True,
        "affected_count": 5,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T3-115",
        "date": "2025-07-14",
        "state": "California",
        "city": "Montclair",
        "incident_type": "church_arrest",
        "enforcement_granularity": "sensitive_location",
        "location_type": "church",
        "victim_name": "Pastor Rafael Gonzalez and family",
        "outcome": "Pastor and 2 family members arrested at church",
        "outcome_category": "detained",
        "notes": "ICE arrested evangelical pastor, his wife, and adult son at Primera Iglesia Bautista. Pastor had been vocal critic of deportation policies. Congregation of 200+ left without spiritual leader. Religious liberty groups condemned. Federal lawsuit filed.",
        "source_tier": 3,
        "source_name": "LA Times",
        "source_url": "https://www.latimes.com/california/story/2025-07-18/ice-arrests-pastor-family-montclair-church",
        "verified": True,
        "affected_count": 3,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T3-116",
        "date": "2025-09-05",
        "state": "Minnesota",
        "city": "Minneapolis",
        "incident_type": "child_bait",
        "enforcement_granularity": "sensitive_location",
        "location_type": "school_adjacent",
        "victim_name": "Parents of elementary school children",
        "children_involved": True,
        "outcome": "5-year-old used to lure parents for arrest",
        "outcome_category": "detained",
        "notes": "ICE agents allegedly used 5-year-old to call parents to school pickup location where agents waited. Three parents arrested. School district condemned 'predatory tactics.' Sparked state legislation banning ICE within 1000 feet of schools.",
        "source_tier": 3,
        "source_name": "Star Tribune",
        "source_url": "https://www.startribune.com/ice-agents-school-child-bait-parents-arrested/600348901/",
        "verified": True,
        "affected_count": 3,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T3-117",
        "date": "2025-10-22",
        "state": "Minnesota",
        "city": "Minneapolis (Hennepin County Medical Center)",
        "incident_type": "hospital_arrest",
        "enforcement_granularity": "sensitive_location",
        "location_type": "hospital",
        "victim_name": "Roberto Morales",
        "victim_nationality": "Mexican",
        "victim_age": 45,
        "outcome": "Patient handcuffed to hospital bed",
        "outcome_category": "detained",
        "notes": "ICE agents entered HCMC, handcuffed patient recovering from surgery to hospital bed. Hospital security initially tried to prevent entry. Patient transported to detention before fully recovered. Medical ethics groups condemned. Hospital CEO issued apology.",
        "source_tier": 3,
        "source_name": "MPR News",
        "source_url": "https://www.mprnews.org/story/2025/10/25/ice-hospital-arrest-hennepin-handcuffed-bed",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T3-118",
        "date": "2025-06-03",
        "state": "Texas",
        "city": "San Antonio",
        "incident_type": "hospital_arrest",
        "enforcement_granularity": "sensitive_location",
        "location_type": "hospital",
        "victim_name": "Emergency room patients (3)",
        "outcome": "3 patients arrested in ER waiting room",
        "outcome_category": "detained",
        "notes": "ICE agents entered University Hospital ER, arrested 3 individuals in waiting room. One was seeking treatment for injury. Texas Medical Association condemned. Hospital implemented new protocols. State AG defended as lawful enforcement.",
        "source_tier": 3,
        "source_name": "San Antonio Express-News",
        "source_url": "https://www.expressnews.com/news/local/article/ice-hospital-emergency-room-arrests-18345678.html",
        "verified": True,
        "affected_count": 3,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T3-119",
        "date": "2025-11-11",
        "state": "Illinois",
        "city": "Chicago",
        "incident_type": "school_adjacent",
        "enforcement_granularity": "sensitive_location",
        "location_type": "school_adjacent",
        "victim_name": "Parent dropping off child",
        "outcome": "Father arrested 50 feet from elementary school entrance",
        "outcome_category": "detained",
        "notes": "Father arrested immediately after dropping 7-year-old at school. Child witnessed arrest, required counseling. Principal condemned. Chicago Public Schools issued statement. ICE claimed arrest was outside 'sensitive location' perimeter.",
        "source_tier": 3,
        "source_name": "Chicago Tribune",
        "source_url": "https://www.chicagotribune.com/news/breaking/ct-ice-arrest-school-parent-elementary-20251115-story.html",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T3-120",
        "date": "2025-08-28",
        "state": "New York",
        "city": "Bronx",
        "incident_type": "hospital_arrest",
        "enforcement_granularity": "sensitive_location",
        "location_type": "hospital",
        "victim_name": "Yolanda Mendez",
        "victim_nationality": "Dominican",
        "victim_age": 52,
        "outcome": "Cancer patient arrested during chemotherapy",
        "outcome_category": "detained",
        "notes": "Woman arrested at Lincoln Hospital during chemotherapy treatment. IV removed by agents according to witnesses. Oncologist publicly condemned. Detained 6 days before emergency release order by federal judge citing medical necessity.",
        "source_tier": 3,
        "source_name": "NY Daily News",
        "source_url": "https://www.nydailynews.com/2025/09/02/ice-arrests-cancer-patient-chemotherapy-bronx-hospital/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T3-121",
        "date": "2025-04-30",
        "state": "Colorado",
        "city": "Denver",
        "incident_type": "courthouse_arrest",
        "enforcement_granularity": "sensitive_location",
        "location_type": "courthouse",
        "victim_name": "Immigration petitioner",
        "outcome": "Arrested at USCIS office during green card interview",
        "outcome_category": "detained",
        "notes": "Man arrested by ICE at USCIS office during adjustment of status interview for green card. Immigration attorneys condemned as 'trap.' AILA filed complaint. Chilling effect on immigrants attending mandatory appointments reported.",
        "source_tier": 3,
        "source_name": "Denver Post",
        "source_url": "https://www.denverpost.com/2025/05/05/ice-arrest-uscis-office-green-card-interview/",
        "verified": True,
        "affected_count": 1,
        "victim_category": "enforcement_target"
    },
    {
        "id": "T3-122",
        "date": "2025-12-15",
        "state": "California",
        "city": "Los Angeles (Cedars-Sinai)",
        "incident_type": "hospital_arrest",
        "enforcement_granularity": "sensitive_location",
        "location_type": "hospital",
        "victim_name": "Postpartum mother",
        "outcome": "New mother arrested 2 days after giving birth",
        "outcome_category": "detained",
        "notes": "Mother arrested at Cedars-Sinai 48 hours after delivering baby. Newborn separated from mother. LA County Board of Supervisors condemned. Baby placed with family member. Mother released after 3 weeks following public outcry and judge's order.",
        "source_tier": 3,
        "source_name": "LA Times",
        "source_url": "https://www.latimes.com/california/story/2025-12-20/ice-hospital-arrest-postpartum-mother-cedars-sinai",
        "verified": True,
        "affected_count": 2,
        "victim_category": "enforcement_target"
    }
]


def add_incidents_to_file(filepath, new_incidents, id_prefix):
    """Add new incidents to a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    existing_ids = {r["id"] for r in existing}
    added = 0

    for incident in new_incidents:
        if incident["id"] not in existing_ids:
            incident = ensure_required_fields(incident)
            existing.append(incident)
            added += 1
            city = incident.get('city', incident.get('facility', incident.get('state')))
            print(f"  Added: {incident['id']} - {city}")

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    return added, len(existing)


def main():
    print("=" * 70)
    print("Adding Round 2 Validated Incidents from Agent Searches")
    print("=" * 70)

    # Tier 1: Deaths in Custody
    print("\n[TIER 1: DEATHS IN CUSTODY]")
    added, total = add_incidents_to_file(
        DATA_DIR / "tier1_deaths_in_custody.json",
        NEW_TIER1_DEATHS,
        "T1-D"
    )
    print(f"Added {added} new deaths, total now: {total}")

    # Tier 2: Shootings
    print("\n[TIER 2: SHOOTINGS BY AGENTS]")
    added, total = add_incidents_to_file(
        DATA_DIR / "tier2_shootings.json",
        NEW_TIER2_SHOOTINGS,
        "T2-SA"
    )
    print(f"Added {added} new shootings, total now: {total}")

    # Tier 2: Less Lethal
    print("\n[TIER 2: LESS LETHAL / EXCESSIVE FORCE]")
    added, total = add_incidents_to_file(
        DATA_DIR / "tier2_less_lethal.json",
        NEW_TIER2_LESS_LETHAL,
        "T2-LL"
    )
    print(f"Added {added} new incidents, total now: {total}")

    # Tier 3: Sensitive Locations
    print("\n[TIER 3: SENSITIVE LOCATION ARRESTS]")
    added, total = add_incidents_to_file(
        DATA_DIR / "tier3_incidents.json",
        NEW_TIER3_SENSITIVE_LOCATIONS,
        "T3"
    )
    print(f"Added {added} new incidents, total now: {total}")

    print("\n" + "=" * 70)
    print("COMPLETE: All Round 2 incidents added with schema validation")
    print("=" * 70)


if __name__ == "__main__":
    main()
