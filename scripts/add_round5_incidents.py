#!/usr/bin/env python3
"""
Add Round 5 incidents: Court rulings and detention resistance.
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
        record["affected_count"] = record.get("participants_count", 1)
    record["incident_scale"] = get_incident_scale(record["affected_count"])
    if "outcome_detail" not in record and "outcome" in record:
        record["outcome_detail"] = record["outcome"]
    if "victim_category" not in record:
        record["victim_category"] = "detainee"
    return record


# ============================================================================
# COURT RULINGS AND LEGAL CHALLENGES
# ============================================================================
NEW_COURT_RULINGS = [
    {
        "id": "T3-148",
        "date": "2025-10-15",
        "state": "Illinois",
        "city": "Chicago",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "court_ruling",
        "case_name": "Castanon Nava v. DHS",
        "judge_name": "Judge Cummings",
        "court": "U.S. District Court Northern District of Illinois",
        "affected_count": 628,
        "outcome": "Consent decree violation found, 13+ ordered released",
        "outcome_detail": "Judge Cummings ruled ICE violated 2022 consent decree by conducting 22+ warrantless arrests. ICE agents carried blank warrant forms (I-200s) and filled them out at arrest scenes. Consent decree extended to February 2026. Ordered release of 13 individuals plus up to 615 more on bond.",
        "outcome_category": "released",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: ICE agents had pattern of carrying blank I-200 forms and completing them at scene rather than obtaining warrants in advance. Represents significant Fourth Amendment violation. Consent decree from 2022 established requirements for warrants. Court found systematic non-compliance. 615 class members eligible for bond hearings. National Immigrant Justice Center represented plaintiffs.",
        "source_tier": 3,
        "source_url": "https://immigrantjustice.org/press-release/federal-judge-extends-consent-decree-prohibiting-ice-from-arresting-people-without-warrants-or-probable-cause/",
        "source_name": "National Immigrant Justice Center",
        "verified": True
    },
    {
        "id": "T3-149",
        "date": "2025-11-01",
        "state": "California",
        "city": "Los Angeles",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "court_ruling",
        "case_name": "Vazquez Perdomo v. Noem",
        "judge_name": "Federal Judge",
        "court": "U.S. District Court Central District of California",
        "affected_count": 500,
        "outcome": "Preliminary injunction granted for Fifth Amendment denial of counsel",
        "outcome_detail": "Court found ICE likely violated Fifth Amendment by denying detained immigrants access to attorneys at B-18 holding facility in Los Angeles. Preliminary injunction granted requiring access to counsel within 24 hours of detention.",
        "outcome_category": "released",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: B-18 facility used for processing detainees after LA raids. Detainees held without access to attorneys for extended periods. Fifth Amendment requires access to counsel. Court found systemic denial of this right. Public Counsel represented plaintiffs.",
        "source_tier": 3,
        "source_url": "https://publiccounsel.org/press-releases/federal-court-grants-preliminary-injunction-against-trump-administration-in-major-los-angeles-immigration-raids-case/",
        "source_name": "Public Counsel",
        "verified": True
    },
    {
        "id": "T3-150",
        "date": "2025-12-01",
        "state": "California",
        "city": "San Francisco",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "court_ruling",
        "case_name": "Maldonado Bautista v. Santacruz",
        "judge_name": "Judge Sykes",
        "court": "U.S. District Court Northern District of California",
        "affected_count": 36000,
        "outcome": "Mandatory detention policy struck down, nationwide class certified",
        "outcome_detail": "Judge Sykes issued final judgment vacating DHS's July 2025 mandatory detention policy. Certified nationwide class of 36,000+ immigrants entitled to bond hearings. Court found policy 'upends decades of practice' and violates due process.",
        "outcome_category": "released",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: DHS July 2025 policy eliminated bond hearings for broad categories of detainees. ACLU challenged as unconstitutional denial of liberty without due process. Court found policy departed from longstanding practice without adequate justification. Nationwide injunction affects all immigration courts. ACLU represented plaintiffs.",
        "source_tier": 3,
        "source_url": "https://www.aclu.org/press-releases/federal-court-affirms-nationwide-class-has-right-to-bond-hearings",
        "source_name": "ACLU",
        "verified": True
    },
    {
        "id": "T3-151",
        "date": "2025-12-15",
        "state": "District of Columbia",
        "city": "Washington DC",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "court_ruling",
        "case_name": "CASA v. DHS",
        "judge_name": "Judge Howell",
        "court": "U.S. District Court District of Columbia",
        "affected_count": 10000,
        "outcome": "Warrantless arrests blocked, documentation required",
        "outcome_detail": "Judge Howell blocked widespread arrests without warrants or flight risk determinations. Required detailed documentation for any warrantless civil immigration arrest. Government must demonstrate probable cause and flight risk before arrest.",
        "outcome_category": "released",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: Fourth Amendment requires warrants or probable cause for arrests. ICE conducting widespread arrests without either. CASA (immigrant advocacy organization) challenged as unconstitutional. Court imposed documentation requirements. ACLU of DC represented plaintiffs.",
        "source_tier": 3,
        "source_url": "https://www.acludc.org/press-releases/federal-judge-blocks-unlawful-immigration-arrests-in-washington-d-c/",
        "source_name": "ACLU of DC",
        "verified": True
    },
    {
        "id": "T3-152",
        "date": "2025-11-25",
        "state": "Colorado",
        "city": "Denver",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "court_ruling",
        "case_name": "Colorado Warrantless Arrests Class Action",
        "judge_name": "Judge Jackson",
        "court": "U.S. District Court District of Colorado",
        "affected_count": 169000,
        "outcome": "66-page ruling found ICE 'policy, pattern, practice' of unconstitutional arrests",
        "outcome_detail": "Judge Jackson ruled in 66-page opinion that ICE had 'policy, pattern, and/or practice' of warrantless arrests without probable cause. Class action preliminarily certified covering 169,000 people. Found systematic Fourth Amendment violations.",
        "outcome_category": "released",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: Comprehensive ruling documenting systematic constitutional violations. ACLU of Colorado brought suit after Operation Aurora and subsequent enforcement. Court found not isolated incidents but intentional policy. Largest class certification in immigration enforcement case. Appeals expected.",
        "source_tier": 3,
        "source_url": "https://coloradosun.com/2025/11/25/federal-court-rules-against-ice-arrests-colorado/",
        "source_name": "Colorado Sun",
        "verified": True
    },
    {
        "id": "T3-153",
        "date": "2025-09-15",
        "state": "New York",
        "city": "New York City",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "court_ruling",
        "case_name": "26 Federal Plaza Conditions Case",
        "judge_name": "Judge Kaplan",
        "court": "U.S. District Court Southern District of New York",
        "affected_count": 200,
        "outcome": "Detention conditions injunction - capacity limits, meals, hygiene required",
        "outcome_detail": "Judge Kaplan extended capacity restrictions (50 sq ft/person), required three meals daily, sleeping mats, hygiene supplies, and confidential attorney calls within 24 hours at 26 Federal Plaza holding facility.",
        "outcome_category": "released",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: 26 Federal Plaza used as processing center for NYC arrests. Overcrowded conditions, lack of food and hygiene. Due process requires humane conditions during detention. Court imposed specific requirements. NYC legal aid organizations represented plaintiffs.",
        "source_tier": 3,
        "source_url": "https://www.nytimes.com/2025/09/15/nyregion/ice-detention-conditions-federal-plaza.html",
        "source_name": "New York Times",
        "verified": True
    },
    {
        "id": "T3-154",
        "date": "2025-12-20",
        "state": "District of Columbia",
        "city": "Washington DC",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "court_ruling",
        "case_name": "Garcia Ramirez v. ICE",
        "judge_name": "Federal Judge",
        "court": "U.S. District Court District of Columbia",
        "affected_count": 5000,
        "outcome": "Unaccompanied minors protected from automatic adult detention transfer",
        "outcome_detail": "Court blocked Trump administration policy to automatically transfer minors turning 18 into adult detention. Enforced 2021 permanent injunction. Required individual assessments before any transfer.",
        "outcome_category": "released",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: Unaccompanied minors have special protections under Flores settlement and TVPRA. Trump policy attempted automatic transfers on 18th birthday without assessment. Court found violation of existing injunction. Affects thousands of minors aging out of UAC system.",
        "source_tier": 3,
        "source_url": "https://www.washingtonpost.com/immigration/2025/12/20/unaccompanied-minors-ice-detention-ruling/",
        "source_name": "Washington Post",
        "verified": True
    },
    {
        "id": "T3-155",
        "date": "2025-12-10",
        "state": "Massachusetts",
        "city": "Boston",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "court_ruling",
        "case_name": "Guerrero Orellana v. Hyde",
        "judge_name": "Federal Judge",
        "court": "U.S. District Court District of Massachusetts",
        "affected_count": 3000,
        "outcome": "Bond hearing denials ruled unlawful through systematic misclassification",
        "outcome_detail": "Court declared it unlawful to deny bond hearings to thousands in New England through systematic misclassification under wrong statutory authority. ICE using inapplicable mandatory detention statutes to deny hearings.",
        "outcome_category": "released",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: ICE systematically classifying detainees under mandatory detention statutes that don't apply to them. Denies due process right to bond hearing. Pattern documented across New England facilities. Court ordered individualized review of classifications.",
        "source_tier": 3,
        "source_url": "https://www.bostonglobe.com/2025/12/10/metro/ice-bond-hearings-massachusetts-ruling/",
        "source_name": "Boston Globe",
        "verified": True
    },
    {
        "id": "T3-156",
        "date": "2026-01-15",
        "state": "Minnesota",
        "city": "Minneapolis",
        "incident_type": "protest",
        "enforcement_granularity": "court_ruling",
        "case_name": "Tincher v. Noem",
        "judge_name": "Judge Menendez",
        "court": "U.S. District Court District of Minnesota",
        "affected_count": 1000,
        "outcome": "First Amendment protections for protesters, chemical agents banned",
        "outcome_detail": "Judge Menendez issued preliminary injunction barring ICE retaliation against peaceful protesters. Prohibited arrests and use of chemical agents against demonstrators. Found First Amendment protections apply to immigration protest.",
        "outcome_category": "released",
        "victim_category": "protester",
        "notes": "EXHAUSTIVE: After Renee Good and Alex Pretti killings, protests erupted across Minneapolis. Federal agents used tear gas and pepper spray on crowds. Court found First Amendment protects right to protest immigration enforcement. ACLU of Minnesota represented plaintiffs.",
        "source_tier": 3,
        "source_url": "https://www.aclu-mn.org/cases/tincher-v-noem/",
        "source_name": "ACLU of Minnesota",
        "verified": True
    },
    {
        "id": "T3-157",
        "date": "2026-01-20",
        "state": "Minnesota",
        "city": "Minneapolis",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "court_ruling",
        "case_name": "Hussen v. Noem",
        "judge_name": "Federal Judge",
        "court": "U.S. District Court District of Minnesota",
        "affected_count": 500,
        "outcome": "Racial profiling class action certified during Operation Metro Surge",
        "outcome_detail": "Challenges warrantless arrests and racial profiling during Operation Metro Surge. Named plaintiff Mubashir Khalif Hussen, 20-year-old US citizen detained despite repeatedly stating citizenship. Class action certified for racial profiling claims.",
        "outcome_category": "detained",
        "victim_category": "us_citizen_collateral",
        "notes": "EXHAUSTIVE: Operation Metro Surge targeted Cedar-Riverside and other immigrant neighborhoods. US citizens detained based on appearance. Mubashir Hussen held in chokehold despite stating citizenship. Class action alleges Fourth and Fourteenth Amendment violations. Related to T3-008 and T4-073.",
        "source_tier": 3,
        "source_url": "https://www.startribune.com/minneapolis-ice-racial-profiling-class-action/600356789/",
        "source_name": "Star Tribune",
        "verified": True,
        "related_incidents": ["T3-008", "T4-073"]
    },
    {
        "id": "T3-158",
        "date": "2025-11-01",
        "state": "Massachusetts",
        "city": "Boston",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "court_ruling",
        "case_name": "Nancy M. v. DHS",
        "judge_name": "Federal Judge",
        "court": "U.S. District Court District of Massachusetts",
        "affected_count": 21500,
        "outcome": "Class action challenging $998/day civil fines totaling $6 billion",
        "outcome_detail": "Class action challenging $998/day civil fines totaling $6 billion issued to 21,500+ immigrants. Alleges Eighth Amendment excessive fines violation. Fines issued for failure to depart despite no practical ability to leave.",
        "outcome_category": "detained",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: DHS imposing $998/day fines on immigrants who don't self-deport. Total fines exceed $6 billion. Many recipients have no ability to leave due to lack of travel documents or home country refusing return. Public Justice and ACLU challenge as unconstitutional excessive fines.",
        "source_tier": 3,
        "source_url": "https://www.publicjustice.net/lawsuit-immigration-civil-fines-ice-homeland-security-department-of-justice/",
        "source_name": "Public Justice",
        "verified": True
    }
]

# ============================================================================
# DETENTION RESISTANCE INCIDENTS
# ============================================================================
NEW_DETENTION_RESISTANCE = [
    {
        "id": "T3-159",
        "date": "2025-06-12",
        "state": "New Jersey",
        "facility": "Delaney Hall Detention Facility",
        "facility_operator": "GEO Group",
        "incident_type": "protest",
        "resistance_type": "protest",
        "victim_name": "Franklin Norberto Bautista Reyes, Joan Sebastian Castaneda Lozada, Andres Felipe Pineda Mogollon, Joel Enrrique Sandoval-Lopez",
        "participants_count": 50,
        "affected_count": 50,
        "outcome": "Facility evacuated, 4 escapees eventually captured",
        "outcome_detail": "Uprising triggered by detainees not receiving food for over 20 hours. Four escaped by breaking through drywall, dropping mattresses to land, using bed sheets to cover barbed wire. All detainees evacuated within 24 hours and transferred to red state facilities. Escapees captured over following weeks with $10,000 reward.",
        "outcome_category": "no_injury",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Delaney Hall first ICE center to open under second Trump administration (February 2025) via $1 billion 15-year GEO Group contract. Uprising caused by: 20+ hours without food, scalding undrinkable tap water, insufficient staff. Newark Mayor Baraka demanded answers. DHS denied revolt. Following escape, ICE transferred detainees to red states for more favorable judges.",
        "source_tier": 3,
        "source_url": "https://peoplesdispatch.org/2025/06/13/ice-detainees-at-delaney-hall-stage-uprising-over-inhumane-conditions/",
        "source_name": "Peoples Dispatch",
        "verified": True
    },
    {
        "id": "T3-160",
        "date": "2025-06-05",
        "state": "Florida",
        "facility": "Krome North Service Processing Center",
        "facility_operator": "ICE",
        "incident_type": "protest",
        "resistance_type": "protest",
        "victim_name": "Cuban detainees (names unknown)",
        "participants_count": 100,
        "affected_count": 100,
        "outcome": "Protest documented, conditions reported internationally",
        "outcome_detail": "Cuban detainees at Krome spelled 'S.O.S' and 'CUBA' with their bodies and towels on facility grounds in south Miami-Dade. Protested being held without release information and feared transfer outside US.",
        "outcome_category": "no_injury",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Detainees reported: worms in food, toilets flooding floors with fecal waste, days without showers or prescription medicine, mosquitoes everywhere, lights on all night, AC shutting off in tropical heat. Amnesty International later released report describing conditions as fitting international definitions of torture. Cubans planning hunger strike to protest transfers.",
        "source_tier": 3,
        "source_url": "https://www.wlrn.org/immigration/2025-06-05/cuban-migrants-at-krome-detention-center-spell-out-sos-in-protest",
        "source_name": "WLRN",
        "verified": True
    },
    {
        "id": "T3-161",
        "date": "2025-08-01",
        "state": "Florida",
        "facility": "Everglades Detention Facility (Alligator Alcatraz)",
        "facility_operator": "State of Florida",
        "incident_type": "less_lethal",
        "resistance_type": "hunger_strike",
        "victim_name": "Pedro Hernandez and others",
        "participants_count": 12,
        "affected_count": 12,
        "duration_days": 14,
        "outcome": "Some strikers hospitalized, DHS denied hunger strike occurred",
        "outcome_detail": "At least dozen detainees refused food for nearly two weeks protesting inhumane conditions at newly opened state facility. Pedro Hernandez hospitalized but continued refusing food. DHS called reports 'hoax spread by criminal illegal aliens.'",
        "outcome_category": "serious_injury",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Alligator Alcatraz opened July 2025 at former training airport in Everglades under Governor DeSantis. Capacity 3,000 expandable to 4,000. Amnesty International 61-page report 'Torture and Enforced Disappearances in the Sunshine State' described 2x2 punishment cages where detainees shackled in Florida sun for hours without food/water. DeSantis press secretary called report 'politically motivated attack.'",
        "source_tier": 3,
        "source_url": "https://www.nbcnews.com/news/latino/alligator-alcatraz-hunger-strike-detainees-protest-conditions-rcna222554",
        "source_name": "NBC News",
        "verified": True
    },
    {
        "id": "T3-162",
        "date": "2025-09-17",
        "state": "Louisiana",
        "facility": "Louisiana State Penitentiary Camp J (Angola)",
        "facility_operator": "State of Louisiana",
        "incident_type": "less_lethal",
        "resistance_type": "hunger_strike",
        "victim_name": "Unknown detainees",
        "participants_count": 19,
        "affected_count": 19,
        "duration_days": 10,
        "outcome": "State denied hunger strike, claimed only 3 refused meals",
        "outcome_detail": "19 detainees launched hunger strike protesting deplorable conditions and lack of medical care at former solitary confinement facility. Many previously held at Alligator Alcatraz before abrupt transfer. State contradicted reports, said detainees didn't refuse meals until after news coverage.",
        "outcome_category": "injury",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Camp J at Angola previously known as 'the Dungeon' for solitary confinement. Closed 2018 due to malfunctioning locks, reopened September 2025 for ICE. Governor Landry announced 208 'criminal illegal aliens' expanding to 400. Demands: medical/mental health care, prescription medications, toilet paper, hygiene products, clean water, ICE officer visits. ACLU filed lawsuit October 2025 alleging inhumane conditions.",
        "source_tier": 3,
        "source_url": "https://www.democracynow.org/2025/9/22/headlines/ice_detainees_in_louisiana_on_hunger_strike_to_protest_conditions_at_angola_prison",
        "source_name": "Democracy Now!",
        "verified": True
    },
    {
        "id": "T3-163",
        "date": "2025-09-01",
        "state": "Louisiana",
        "facility": "LaSalle Detention Facility",
        "facility_operator": "GEO Group",
        "incident_type": "less_lethal",
        "resistance_type": "hunger_strike",
        "victim_name": "Five South Asian men (names withheld)",
        "participants_count": 5,
        "affected_count": 5,
        "duration_days": 75,
        "outcome": "Force-feeding ordered by federal court after 75 days",
        "outcome_detail": "Five South Asian men reached 75 days on hunger strike at GEO Group LaSalle facility. ICE obtained court order to force-feed two men and force-hydrate one. 75 days without nutrition when vital organs begin to fail. Some strikers detained nearly 2 years.",
        "outcome_category": "serious_injury",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Force-feeding involves restraining and forcing fluid through nasal passages. Denounced by UN, Physicians for Human Rights, AMA, World Medical Association. Detainees restrained, tubes in noses, Boost shakes poured twice daily. Freedom for Immigrants filed DHS civil rights complaint. ICE blocked independent physicians. Louisiana holds 7,000+ ICE detainees (second to Texas); 98% in for-profit facilities.",
        "source_tier": 3,
        "source_url": "https://sign.moveon.org/petitions/tell-ice-to-immediately-release-hunger-striking-detainees-in-louisiana",
        "source_name": "MoveOn/Freedom for Immigrants",
        "verified": True
    },
    {
        "id": "T3-164",
        "date": "2025-03-17",
        "state": "Colorado",
        "facility": "Aurora ICE Processing Center",
        "facility_operator": "GEO Group",
        "incident_type": "less_lethal",
        "resistance_type": "escape",
        "victim_name": "Joel Gonzalez-Gonzalez and one other",
        "participants_count": 2,
        "affected_count": 2,
        "outcome": "Both escapees recaptured, ICE delayed notification 4+ hours",
        "outcome_detail": "Two detainees escaped during power outage when doors opened. Joel Gonzalez-Gonzalez captured by Adams County Sheriff ~12 miles from facility. ICE waited 4+ hours to notify local police, drawing criticism.",
        "outcome_category": "no_injury",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: ICE delay in notifying Aurora police drew criticism. Colorado has only one ICE center but Trump planning expansion to Hudson, Walsenburg, Ignacio adding 2,560 beds. ICE arrests in Colorado 4x increase: 734 (Jan-Oct 2024) to 3,230 (Jan-Oct 2025).",
        "source_tier": 3,
        "source_url": "https://www.cnn.com/2025/03/22/us/colorado-ice-escape-arrest-power-outage-hnk/index.html",
        "source_name": "CNN",
        "verified": True
    },
    {
        "id": "T3-165",
        "date": "2025-04-15",
        "state": "Florida",
        "facility": "Florida Detention Center (FDC)",
        "facility_operator": "ICE",
        "incident_type": "less_lethal",
        "resistance_type": "protest",
        "victim_name": "Detainees (names unknown)",
        "participants_count": 50,
        "affected_count": 50,
        "outcome": "Stun grenades and physical force used against detainees",
        "outcome_detail": "Violent incident where FDC staff used stun grenades and physical force against detainees protesting denial of food, water, and medical attention.",
        "outcome_category": "injury",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Human Rights Watch documented as part of 'You Feel Like Your Life Is Over' report on abusive practices at three Florida detention centers since January 2025. 2025 was deadliest year for ICE detainees since 2004 with 31 deaths; December 2025 was deadliest month on record.",
        "source_tier": 3,
        "source_url": "https://www.hrw.org/report/2025/07/21/you-feel-like-your-life-is-over/abusive-practices-at-three-florida-immigration",
        "source_name": "Human Rights Watch",
        "verified": True
    },
    {
        "id": "T3-166",
        "date": "2025-04-02",
        "state": "California",
        "facility": "Adelanto ICE Processing Center",
        "facility_operator": "GEO Group",
        "incident_type": "protest",
        "resistance_type": "hunger_strike",
        "victim_name": "Detainees (names unknown)",
        "participants_count": 50,
        "affected_count": 50,
        "duration_days": 14,
        "outcome": "Rally held outside ICE LA field office to amplify demands",
        "outcome_detail": "Over 50 detainees at Adelanto launched combined hunger and labor strike. Part of Detention Watch Network's 'Communities Not Cages' National Day of Action with 17 demonstrations nationwide.",
        "outcome_category": "no_injury",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Adelanto is largest ICE center in California (GEO Group). At least 8 deaths since 2011. History of hunger strikes, work stoppages, sit-ins. ACLU documented retaliation including solitary confinement. 'Communities Not Cages' campaign co-hosted by AFSC and Immigrant Justice Network.",
        "source_tier": 3,
        "source_url": "https://www.detentionwatchnetwork.org/pressroom/releases/2025/national-day-action-across-country-denounce-ice-detention-raids-abductions",
        "source_name": "Detention Watch Network",
        "verified": True
    },
    {
        "id": "T3-167",
        "date": "2026-01-25",
        "state": "Texas",
        "facility": "South Texas Family Residential Center (Dilley)",
        "facility_operator": "ICE",
        "incident_type": "protest",
        "resistance_type": "protest",
        "victim_name": "Maria Alejandra Montoya Sanchez and others",
        "participants_count": 1500,
        "affected_count": 1500,
        "children_affected": True,
        "outcome": "80% of facility protested, ICE/CBP police rushed to scene",
        "outcome_detail": "~1,500 people (80% of facility) protested after guards abruptly ordered attorneys to leave. Detainees including many children poured into open areas chanting 'Libertad.' Triggered by news of 5-year-old Liam Ramos and Minneapolis events. Dozens of ICE/CBP police cars raced to area.",
        "outcome_category": "no_injury",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Dilley closed 2024, reopened as family detention expanded. Attorney Eric Lee: 'horrible place' with 'putrid' undrinkable water and meals with bugs, dirt, debris. Maria Montoya Sanchez, 31, held with 9-year-old daughter since October: 'We're immigrants, with children, not criminals.' National Center for Youth Law: conditions 'fundamentally unsafe for anyone, let alone young children.'",
        "source_tier": 3,
        "source_url": "https://www.texastribune.org/2026/01/24/immigration-facility-protest-texas-liam-conejo-ramos/",
        "source_name": "Texas Tribune",
        "verified": True
    },
    {
        "id": "T3-168",
        "date": "2025-11-01",
        "state": "New Mexico",
        "facility": "Torrance County Detention Facility",
        "facility_operator": "CoreCivic",
        "incident_type": "protest",
        "resistance_type": "hunger_strike",
        "victim_name": "Eugenio Castaneda Ferrer and four others",
        "participants_count": 5,
        "affected_count": 5,
        "duration_days": 7,
        "outcome": "Ongoing protest over prolonged detention and abuse",
        "outcome_detail": "Five men including Eugenio Castaneda Ferrer refused entry to cells during count. Three commenced hunger strike demanding freedom. May 2025 advocates reported sewage again flooding cells.",
        "outcome_category": "no_injury",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: CoreCivic facility has extensive history of hunger strikes and abuse. DHS OIG previously recommended removing detainees. Sued for 2020 chemical attack on peaceful COVID-19 hunger strikers. Kesley Vial died by suicide August 2022 after meeting officials. Strikers faced: solitary, force-feeding threats, fabricated misconduct reports, expedited deportations.",
        "source_tier": 3,
        "source_url": "https://innovationlawlab.org/torrance-county-detention-facility-timeline",
        "source_name": "Innovation Law Lab",
        "verified": True
    }
]


def add_incidents_to_file(filepath, new_incidents, label):
    """Add new incidents to a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    existing_ids = {r["id"] for r in existing}
    added = 0
    skipped = 0

    for incident in new_incidents:
        if incident["id"] in existing_ids:
            skipped += 1
            continue

        incident = ensure_required_fields(incident)
        existing.append(incident)
        added += 1
        loc = incident.get('city', incident.get('facility', incident.get('state')))
        print(f"  Added: {incident['id']} - {loc}")

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    return added, skipped, len(existing)


def main():
    print("=" * 70)
    print("Adding Round 5 Incidents: Court Rulings & Detention Resistance")
    print("=" * 70)

    print("\n[TIER 3: COURT RULINGS]")
    added, skipped, total = add_incidents_to_file(
        DATA_DIR / "tier3_incidents.json",
        NEW_COURT_RULINGS,
        "T3"
    )
    print(f"Added {added} court rulings (skipped {skipped}), total now: {total}")

    print("\n[TIER 3: DETENTION RESISTANCE]")
    added, skipped, total = add_incidents_to_file(
        DATA_DIR / "tier3_incidents.json",
        NEW_DETENTION_RESISTANCE,
        "T3"
    )
    print(f"Added {added} resistance incidents (skipped {skipped}), total now: {total}")

    print("\n" + "=" * 70)
    print("COMPLETE: Round 5 incidents added")
    print("=" * 70)


if __name__ == "__main__":
    main()
