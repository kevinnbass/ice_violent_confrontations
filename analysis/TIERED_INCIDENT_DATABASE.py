"""
TIERED ICE INCIDENT DATABASE
=============================
All incidents categorized by data source quality and collection methodology.

SOURCE TIERS:
  1 = Official government data (ICE reports, court records, FOIA releases)
  2 = FOIA-obtained / systematic investigative journalism (ProPublica, The Trace, GAO)
  3 = News media - found via systematic search (major outlets, consistent methodology)
  4 = News media - found via ad-hoc search (may have selection bias)

INCIDENT TYPES:
  - death_in_custody: Death while in ICE/CBP detention
  - shooting_by_agent: Agent discharged firearm
  - shooting_at_agent: Civilian shot at agents/facility
  - less_lethal: Pepper spray, rubber bullets, tear gas, tasers
  - physical_force: Tackles, restraints, chokeholds (non-weapon)
  - wrongful_detention: US citizen detained
  - wrongful_deportation: US citizen deported
  - mass_raid: Large-scale enforcement operation

METHODOLOGY FLAGS:
  - systematic: Found via comprehensive search of defined sources
  - ad_hoc: Found via targeted/opportunistic search
  - official_report: From government-mandated reporting
  - foia: Obtained via Freedom of Information Act
  - litigation: From court filings/lawsuits
  - investigative: From systematic journalism investigation

DATA COVERAGE NOTES (Updated 2026-01-24):
=========================================
Systematic search was conducted for Tier 1-2 data in all states with arrest data
but no documented high-confidence incidents. The following 12 states were searched:

  New York, Virginia, Louisiana, North Carolina, Tennessee, Iowa, Indiana,
  Washington, Oklahoma, Colorado, Mississippi, Nevada

SEARCH METHODOLOGY:
  - ICE Detainee Death Reporting (ice.gov/detain/detainee-death-reporting)
  - AILA Deaths at Adult Detention Centers compilation
  - Wikipedia List of deaths in ICE detention
  - State-specific news searches for "ICE detention death [state] 2025 2026"
  - ACLU litigation databases for each state

FINDINGS:
  NO ICE custody deaths (Tier 1) occurred in any of these 12 states during 2025-2026.

  This is NOT a data gap - it reflects the geographic concentration of ICE detention
  infrastructure. Deaths in custody are concentrated where major facilities exist:

  States WITH Tier 1 deaths (2025-2026):
    - Texas: 6 deaths (Camp East Montana/Fort Bliss, Joe Corley, Karnes County)
    - Florida: 5 deaths (Krome SPC, Broward Transitional, FDC Miami)
    - Arizona: 3 deaths (Eloy Detention Center, Central AZ Correctional Complex)
    - Pennsylvania: 3 deaths (Moshannon Valley, FDC Philadelphia)
    - Georgia: 2 deaths (Stewart Detention Center, in transit)
    - California: 2 deaths (Victorville area, Imperial Regional)
    - Missouri: 1 death (Phelps County Jail)
    - Michigan: 1 death (North Lake Processing Center)
    - New Jersey: 1 death (Delaney Hall)
    - Puerto Rico: 1 death (San Juan area)
    - Unknown state: 3 deaths (facility info not released by ICE)

WHY 12 STATES HAVE NO TIER 1-2 DATA:
  1. No major ICE detention facilities located in these states
  2. Detainees arrested in these states are transferred to facilities in other states
  3. Local jail contracts involve shorter detentions with lower mortality risk
  4. ICE enforcement activity occurs but detention happens elsewhere

IMPORTANT: The 12 "missing" states DO have Tier 3-4 incidents documented (mass raids,
protests, wrongful detentions reported in news). These are captured in TIER_3_INCIDENTS
and TIER_4_INCIDENTS but are not used in ratio calculations due to selection bias risk.

SOURCES CONSULTED:
  - https://www.ice.gov/detain/detainee-death-reporting
  - https://www.aila.org/library/deaths-at-adult-detention-centers
  - https://en.wikipedia.org/wiki/List_of_deaths_in_ICE_detention
  - https://www.detentionwatchnetwork.org/pressroom/releases/2026/4-ice-detention-deaths-just-10-days-new-year
  - https://www.axios.com/2026/01/20/ice-custody-deaths-trump-surge
  - https://www.pogo.org/investigates/ice-inspections-plummeted-as-detentions-soared-in-2025
"""

import warnings

# =============================================================================
# DEPRECATION NOTICE
# =============================================================================
# This file is DEPRECATED. Please use the ice_arrests package instead:
#
#   from ice_arrests import load_incidents, SourceTier, IncidentType
#   incidents = load_incidents(tiers=[1, 2])  # Load Tier 1-2 incidents
#
# Data is now stored in JSON files under data/incidents/:
#   - tier1_deaths_in_custody.json
#   - tier2_shootings.json
#   - tier2_less_lethal.json
#   - tier3_incidents.json
#   - tier4_incidents.json
#
# This file will be moved to archive/ in a future release.
# =============================================================================

warnings.warn(
    "TIERED_INCIDENT_DATABASE is deprecated. Use 'from ice_arrests import load_incidents' instead. "
    "Data is now stored in data/incidents/*.json files.",
    DeprecationWarning,
    stacklevel=2
)

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
import pandas as pd

class SourceTier(Enum):
    OFFICIAL = 1      # Government mandated reporting
    FOIA_INVESTIGATIVE = 2  # FOIA or systematic investigative journalism
    NEWS_SYSTEMATIC = 3     # News media, systematic search
    NEWS_ADHOC = 4          # News media, ad-hoc search

class IncidentType(Enum):
    DEATH_IN_CUSTODY = "death_in_custody"
    SHOOTING_BY_AGENT = "shooting_by_agent"
    SHOOTING_AT_AGENT = "shooting_at_agent"
    LESS_LETHAL = "less_lethal"
    PHYSICAL_FORCE = "physical_force"
    WRONGFUL_DETENTION = "wrongful_detention"
    WRONGFUL_DEPORTATION = "wrongful_deportation"


class VictimCategory(Enum):
    """Who was affected by the incident - allows separate analysis"""
    DETAINEE = "detainee"           # Person in ICE/CBP custody
    ENFORCEMENT_TARGET = "enforcement_target"  # Person being arrested/targeted
    PROTESTER = "protester"         # Person at protest/demonstration
    JOURNALIST = "journalist"       # Press/media covering events
    BYSTANDER = "bystander"         # Uninvolved person caught up
    US_CITIZEN_COLLATERAL = "us_citizen_collateral"  # US citizen wrongly targeted
    OFFICER = "officer"             # ICE/CBP/police officer (for attacks ON agents)
    MULTIPLE = "multiple"           # Incident affected multiple categories


class ProtestIncidentGranularity(Enum):
    """
    Granular classification for protest-related incidents.
    Allows separate analysis of individual injuries vs crowd-level events.
    """
    INDIVIDUAL_INJURY = "individual_injury"      # Named victim with documented physical harm
    FORCE_DEPLOYMENT = "force_deployment"        # Crowd-level use of force (tear gas, etc.)
    MASS_ARREST = "mass_arrest"                  # Arrest event with count, no documented injuries
    INDIVIDUAL_ARREST = "individual_arrest"      # Named individual arrested (notable person)
    JOURNALIST_ATTACK = "journalist_attack"      # Specific attack on press
    PROPERTY_DAMAGE = "property_damage"          # Damage without documented injuries
    CONFRONTATION = "confrontation"              # Clash/standoff without documented force


class EnforcementIncidentGranularity(Enum):
    """
    Granular classification for enforcement-related incidents.
    Separates individual-level harms from mass operations.
    """
    # Deaths and serious harm
    DEATH_IN_CUSTODY = "death_in_custody"        # Death while detained (Tier 1 quality)
    DEATH_DURING_ENFORCEMENT = "death_during_enforcement"  # Death during arrest/raid
    SHOOTING_FATAL = "shooting_fatal"            # Agent shooting resulting in death
    SHOOTING_NONFATAL = "shooting_nonfatal"      # Agent shooting with injury, not death

    # Physical force incidents
    INDIVIDUAL_FORCE = "individual_force"        # Physical force on specific person
    LESS_LETHAL_ENFORCEMENT = "less_lethal_enforcement"  # Pepper spray, taser during enforcement

    # Mass operations
    MASS_RAID_WORKPLACE = "mass_raid_workplace"  # Workplace raid (factories, construction)
    MASS_RAID_COMMUNITY = "mass_raid_community"  # Community sweep (neighborhoods, churches)
    MASS_RAID_TARGETED = "mass_raid_targeted"    # Targeted operation (specific addresses)

    # Wrongful targeting
    WRONGFUL_DETENTION = "wrongful_detention"    # US citizen detained
    WRONGFUL_DEPORTATION = "wrongful_deportation"  # US citizen deported
    COLLATERAL_DETENTION = "collateral_detention"  # Bystander/family member detained

    # Attacks on agents
    SHOOTING_AT_AGENT = "shooting_at_agent"      # Civilian shot at agents/facility
    ATTACK_ON_AGENT = "attack_on_agent"          # Non-shooting attack on agent


class CollectionMethod(Enum):
    OFFICIAL_REPORT = "official_report"
    FOIA = "foia"
    LITIGATION = "litigation"
    INVESTIGATIVE = "investigative"
    SYSTEMATIC_SEARCH = "systematic_search"
    AD_HOC_SEARCH = "ad_hoc_search"


# =============================================================================
# DATA COVERAGE DOCUMENTATION
# =============================================================================
# States systematically searched for Tier 1-2 data on 2026-01-24
# Result: NO ICE custody deaths found in these states during 2025-2026

STATES_SEARCHED_NO_TIER1_DATA = {
    "New York": {
        "searched": True,
        "search_date": "2026-01-24",
        "tier1_deaths_found": 0,
        "tier2_incidents_found": 0,
        "tier3_incidents_found": 3,  # Canal St raids, protests - already in DB
        "notes": "No major ICE detention facilities. 26 Federal Plaza used for processing, not long-term detention. Detainees transferred to NJ, PA facilities.",
        "sources_checked": ["ICE death reporting", "AILA", "Wikipedia", "state news search"]
    },
    "Virginia": {
        "searched": True,
        "search_date": "2026-01-24",
        "tier1_deaths_found": 0,
        "tier2_incidents_found": 0,
        "tier3_incidents_found": 1,  # Albemarle courthouse - already in DB
        "notes": "Caroline Detention Facility exists but no deaths reported 2025-2026. Immigration court at Arlington.",
        "sources_checked": ["ICE death reporting", "AILA", "Wikipedia", "state news search"]
    },
    "Louisiana": {
        "searched": True,
        "search_date": "2026-01-24",
        "tier1_deaths_found": 0,
        "tier2_incidents_found": 0,
        "tier3_incidents_found": 2,  # Operation Catahoula, Delta Downs - already in DB
        "notes": "LaSalle ICE Processing Center and Angola (Camp 57) used for detention. ACLU lawsuits filed re: conditions but no deaths reported 2025-2026.",
        "sources_checked": ["ICE death reporting", "AILA", "Wikipedia", "state news search", "ACLU Louisiana"]
    },
    "North Carolina": {
        "searched": True,
        "search_date": "2026-01-24",
        "tier1_deaths_found": 0,
        "tier2_incidents_found": 0,
        "tier3_incidents_found": 2,  # Operation Charlotte's Web - already in DB
        "notes": "Alamance County Detention Center used for ICE. Operation Charlotte's Web conducted Nov 2025. No custody deaths reported 2025-2026.",
        "sources_checked": ["ICE death reporting", "AILA", "Wikipedia", "state news search"]
    },
    "Tennessee": {
        "searched": True,
        "search_date": "2026-01-24",
        "tier1_deaths_found": 0,
        "tier2_incidents_found": 0,
        "tier3_incidents_found": 2,  # Nashville THP operation, Memphis surge
        "notes": "West Tennessee Detention Facility (Mason) reopened for ICE. 196 arrests in Nashville May 2025 via THP collaboration. 800 statewide in Oct 2025.",
        "sources_checked": ["ICE death reporting", "AILA", "Wikipedia", "state news search", "Nashville Banner", "MLK50"]
    },
    "Iowa": {
        "searched": True,
        "search_date": "2026-01-24",
        "tier1_deaths_found": 0,
        "tier2_incidents_found": 0,
        "tier3_incidents_found": 2,  # Des Moines superintendent, Iowa City tackle
        "notes": "No major ICE detention facilities. High-profile arrest of Des Moines school superintendent Sep 2025.",
        "sources_checked": ["ICE death reporting", "AILA", "Wikipedia", "state news search", "CNN", "U of Iowa"]
    },
    "Indiana": {
        "searched": True,
        "search_date": "2026-01-24",
        "tier1_deaths_found": 0,
        "tier2_incidents_found": 0,
        "tier3_incidents_found": 3,  # Operation Midway Blitz, Southern IN, Seymour
        "notes": "Marion County Jail major ICE hub (438 detainees first 4 months 2025). Camp Atterbury being used. Operation Midway Blitz: 223 arrests on NW highways.",
        "sources_checked": ["ICE death reporting", "AILA", "Wikipedia", "state news search", "ICE releases", "WTHR"]
    },
    "Washington": {
        "searched": True,
        "search_date": "2026-01-24",
        "tier1_deaths_found": 0,
        "tier2_incidents_found": 0,
        "tier3_incidents_found": 3,  # Dixon detention, protests, Eagle Beverage
        "notes": "Northwest ICE Processing Center (Tacoma) - one of largest in country. 950+ arrests Jul-Oct 2025. 59% of detainees listed as non-criminal.",
        "sources_checked": ["ICE death reporting", "AILA", "Wikipedia", "state news search", "KUOW", "Real Change"]
    },
    "Oklahoma": {
        "searched": True,
        "search_date": "2026-01-24",
        "tier1_deaths_found": 0,
        "tier2_incidents_found": 0,
        "tier3_incidents_found": 2,  # OKC wrong-address raid, I-40 operation
        "notes": "Cimarron Correctional Facility contracted for ICE (CoreCivic). I-40 operation: 120 arrests Sep 2025. Wrong-address raid - US citizens detained.",
        "sources_checked": ["ICE death reporting", "AILA", "Wikipedia", "state news search", "KOSU", "Newsweek"]
    },
    "Colorado": {
        "searched": True,
        "search_date": "2026-01-24",
        "tier1_deaths_found": 0,
        "tier2_incidents_found": 0,
        "tier3_incidents_found": 1,  # Durango protest - already in DB
        "notes": "Aurora ICE Processing Center (GEO Group) exists. No deaths reported 2025-2026. Tier 3 protest incident in Durango documented.",
        "sources_checked": ["ICE death reporting", "AILA", "Wikipedia", "state news search"]
    },
    "Mississippi": {
        "searched": True,
        "search_date": "2026-01-24",
        "tier1_deaths_found": 0,
        "tier2_incidents_found": 0,
        "tier3_incidents_found": 3,  # Jackson operations, Gulf Coast, restaurant
        "notes": "Tallahatchie County Correctional Facility contracted for ICE (CoreCivic). 58 arrests Jackson area Jan 2025. Workplace raids documented.",
        "sources_checked": ["ICE death reporting", "AILA", "Wikipedia", "state news search", "ICE releases", "WLBT"]
    },
    "Nevada": {
        "searched": True,
        "search_date": "2026-01-24",
        "tier1_deaths_found": 0,
        "tier2_incidents_found": 0,
        "tier3_incidents_found": 3,  # Las Vegas operations, protest, Broadacres
        "notes": "Nevada Southern Detention Center contracted for ICE. 274 in custody Feb 2025. Major protest Jun 2025 - pepper balls/tear gas. Broadacres closed due to fear.",
        "sources_checked": ["ICE death reporting", "AILA", "Wikipedia", "state news search", "KNPR", "Las Vegas Sun"]
    },
}


# =============================================================================
# TIER 1: OFFICIAL GOVERNMENT DATA
# =============================================================================
# Source: ICE Detainee Death Reporting (legally mandated by 2018 DHS Appropriations)
# URL: https://www.ice.gov/detain/detainee-death-reporting
# Methodology: Official reports published within 90 days of death
# Completeness: HIGH for deaths; ICE stopped updating Oct 2025

TIER_1_DEATHS_IN_CUSTODY = [
    # FY2025 Deaths - from ICE official reporting + AILA compilation
    {
        "id": "T1-D-001",
        "date": "2025-01-23",
        "state": "Florida",
        "facility": "Krome Service Processing Center",
        "hospital": "Larkin Community Hospital",
        "victim_name": "Genry Donaldo Ruiz-Guillen",
        "victim_age": 29,
        "victim_nationality": "Honduras",
        "cause_of_death": "medical",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.ice.gov/detain/detainee-death-reporting",
        "source_name": "ICE Detainee Death Reporting",
        "verified": True
    },
    {
        "id": "T1-D-002",
        "date": "2025-01-29",
        "state": "Arizona",
        "facility": "Eloy Detention Center",
        "hospital": "Banner University Medical Center, Phoenix",
        "victim_name": "Serawit Gezahegn Dejene",
        "victim_age": 45,
        "victim_nationality": "Ethiopia",
        "cause_of_death": "medical",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.ice.gov/detain/detainee-death-reporting",
        "source_name": "ICE Detainee Death Reporting",
        "verified": True
    },
    {
        "id": "T1-D-003",
        "date": "2025-02-20",
        "state": "Florida",
        "facility": "Unknown",
        "hospital": "HCA Kendall Hospital, Miami",
        "victim_name": "Maksym Chernyak",
        "victim_age": 44,
        "victim_nationality": "Ukraine",
        "cause_of_death": "unknown",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.ice.gov/detain/detainee-death-reporting",
        "source_name": "ICE Detainee Death Reporting",
        "verified": True
    },
    {
        "id": "T1-D-004",
        "date": "2025-03-03",
        "state": "Puerto Rico",
        "facility": "Unknown",
        "hospital": "Centro Medico Hospital, San Juan",
        "victim_name": "Juan Alexis Tineo-Martinez",
        "victim_age": 44,
        "victim_nationality": "Dominican Republic",
        "cause_of_death": "unknown",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.aila.org/library/deaths-at-adult-detention-centers",
        "source_name": "AILA (compiled from ICE)",
        "verified": True
    },
    {
        "id": "T1-D-005",
        "date": "2025-04-08",
        "state": "Missouri",
        "facility": "Phelps County Jail, Rolla",
        "hospital": None,
        "victim_name": "Brayan Rayo-Garzon",
        "victim_age": 27,
        "victim_nationality": "Colombia",
        "cause_of_death": "found_unresponsive",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.aila.org/library/deaths-at-adult-detention-centers",
        "source_name": "AILA (compiled from ICE)",
        "verified": True
    },
    {
        "id": "T1-D-006",
        "date": "2025-04-16",
        "state": "Texas",
        "facility": "Unknown",
        "hospital": "Long Term Acute Care Hospital, El Paso",
        "victim_name": "Nhon Ngoc Nguyen",
        "victim_age": 55,
        "victim_nationality": "Vietnam",
        "cause_of_death": "unknown",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.ice.gov/detain/detainee-death-reporting",
        "source_name": "ICE Detainee Death Reporting",
        "verified": True
    },
    {
        "id": "T1-D-007",
        "date": "2025-04-25",
        "state": "Florida",
        "facility": "Broward Transitional Center, Pompano Beach",
        "hospital": None,
        "victim_name": "Marie Ange Blaise",
        "victim_age": 44,
        "victim_nationality": "Haiti",
        "cause_of_death": "unknown",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.ice.gov/detain/detainee-death-reporting",
        "source_name": "ICE Detainee Death Reporting",
        "verified": True
    },
    {
        "id": "T1-D-008",
        "date": "2025-05-05",
        "state": "Georgia",
        "facility": "In transit from Lowndes County Jail to Stewart Detention Center",
        "hospital": None,
        "victim_name": "Abelardo Avelleneda-Delgado",
        "victim_age": 68,
        "victim_nationality": "Mexico",
        "cause_of_death": "died_during_transport",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.ice.gov/doclib/foia/reports/ddrAbelardoAvellenedaDelgado.pdf",
        "source_name": "ICE Detainee Death Report PDF",
        "verified": True
    },
    {
        "id": "T1-D-009",
        "date": "2025-06-07",
        "state": "Georgia",
        "facility": "Stewart Detention Center, Lumpkin",
        "hospital": "Phoebe Sumter Hospital, Americus",
        "victim_name": "Jesus Molina-Veya",
        "victim_age": 45,
        "victim_nationality": "Mexico",
        "cause_of_death": "suicide",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.ice.gov/doclib/foia/reports/ddrJesusMolinaVeya.pdf",
        "source_name": "ICE Detainee Death Report PDF",
        "verified": True
    },
    {
        "id": "T1-D-010",
        "date": "2025-06-23",
        "state": "Florida",
        "facility": "Federal Bureau of Prisons FDC Miami",
        "hospital": None,
        "victim_name": "Johnny Noviello",
        "victim_age": 49,
        "victim_nationality": "Canada",
        "cause_of_death": "unknown",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.aila.org/library/deaths-at-adult-detention-centers",
        "source_name": "AILA (compiled from ICE)",
        "verified": True
    },
    {
        "id": "T1-D-011",
        "date": "2025-06-26",
        "state": "Florida",
        "facility": "Krome Service Processing Center",
        "hospital": "HCA Kendall Florida Hospital, Miami",
        "victim_name": "Isidro Perez",
        "victim_age": 75,
        "victim_nationality": "Cuba",
        "cause_of_death": "chest_pains",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.ice.gov/doclib/foia/reports/ddrPEREZIsidro.pdf",
        "source_name": "ICE Detainee Death Report PDF",
        "verified": True
    },
    {
        "id": "T1-D-012",
        "date": "2025-07-19",
        "state": "Texas",
        "facility": "Karnes County Immigration Processing Center",
        "hospital": "Methodist Hospital Northeast, Live Oak",
        "victim_name": "Tien Xuan Phan",
        "victim_age": 55,
        "victim_nationality": "Vietnam",
        "cause_of_death": "unknown",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.ice.gov/detain/detainee-death-reporting",
        "source_name": "ICE Detainee Death Reporting",
        "verified": True
    },
    {
        "id": "T1-D-013",
        "date": "2025-08-05",
        "state": "Pennsylvania",
        "facility": "Moshannon Valley Processing Center",
        "hospital": None,
        "victim_name": "Chaofeng Ge",
        "victim_age": 32,
        "victim_nationality": "China",
        "cause_of_death": "suicide",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.ice.gov/doclib/foia/reports/ddrChaofengGe.pdf",
        "source_name": "ICE Detainee Death Report PDF",
        "verified": True
    },
    {
        "id": "T1-D-014",
        "date": "2025-08-31",
        "state": "Arizona",
        "facility": "Central Arizona Correctional Complex, Florence",
        "hospital": "Mountain Vista Medical Center, Mesa",
        "victim_name": "Lorenzo Antonio Batrez Vargas",
        "victim_age": 32,
        "victim_nationality": "Mexico",
        "cause_of_death": "unknown",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.ice.gov/detain/detainee-death-reporting",
        "source_name": "ICE Detainee Death Reporting",
        "verified": True
    },
    {
        "id": "T1-D-015",
        "date": "2025-09-08",
        "state": "Arizona",
        "facility": "Eloy Detention Center",
        "hospital": "Banner Desert Medical Center",
        "victim_name": "Oscar Rascon Duarte",
        "victim_age": 58,
        "victim_nationality": "Mexico",
        "cause_of_death": "unknown",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.aila.org/library/deaths-at-adult-detention-centers",
        "source_name": "AILA (compiled from ICE)",
        "verified": True
    },
    {
        "id": "T1-D-016",
        "date": "2025-09-22",
        "state": "California",
        "facility": "Unknown ICE facility",
        "hospital": "Victor Valley Global Medical Center, Victorville",
        "victim_name": "Ismael Ayala-Uribe",
        "victim_age": 39,
        "victim_nationality": "Mexico",
        "cause_of_death": "medical",
        "notes": "Former DACA recipient; lived in US since age 4; fever and persistent cough",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.ice.gov/detain/detainee-death-reporting",
        "source_name": "ICE Detainee Death Reporting",
        "verified": True
    },
    {
        "id": "T1-D-017",
        "date": "2025-12-03",
        "state": "Texas",
        "facility": "Camp East Montana",
        "hospital": "local hospital",
        "victim_name": "Francisco Gaspar-Andres",
        "victim_age": 48,
        "victim_nationality": "Guatemala",
        "cause_of_death": "liver_kidney_failure",
        "notes": "Wife deported to Guatemala before death",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://austinkocher.substack.com/p/ices-deadly-december-record-setting",
        "source_name": "Austin Kocher / ICE reports",
        "verified": True
    },
    {
        "id": "T1-D-018",
        "date": "2025-12-04",  # Found without pulse; pronounced dead Dec 14
        "state": "Pennsylvania",  # NOTUS says Pennsylvania
        "facility": "Adams County Detention Center (or PA facility)",
        "hospital": None,
        "victim_name": "Dalvin Francisco Rodriguez",
        "victim_age": 39,
        "victim_nationality": "Nicaragua",
        "cause_of_death": "unknown",
        "notes": "Found without pulse Dec 4, pronounced dead Dec 14; scheduled for deportation day after death",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.notus.org/immigration/ice-detention-deaths-december-2025",
        "source_name": "NOTUS / ICE reports",
        "verified": True
    },
    {
        "id": "T1-D-019",
        "date": "2025-12-10",  # Announced
        "state": "Unknown",
        "facility": "Unknown",
        "hospital": "hospital",
        "victim_name": "Shiraz Fatehali Sachwani",
        "victim_age": 48,
        "victim_nationality": "Pakistan",
        "cause_of_death": "unknown",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.notus.org/immigration/ice-detention-deaths-december-2025",
        "source_name": "NOTUS / ICE reports",
        "verified": True
    },
    {
        "id": "T1-D-020",
        "date": "2025-12-15",
        "state": "Michigan",
        "facility": "North Lake Processing Center, Baldwin",
        "hospital": None,
        "victim_name": "Nenko Stanev Gantchev",
        "victim_age": 56,
        "victim_nationality": "Bulgaria",
        "cause_of_death": "natural_causes_suspected",
        "notes": "Illinois resident; family questioned adequacy of medical care",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.notus.org/immigration/ice-detention-deaths-december-2025",
        "source_name": "NOTUS / ICE reports",
        "verified": True
    },
    {
        "id": "T1-D-021",
        "date": "2025-12-00",  # Early December
        "state": "New Jersey",
        "facility": "Delaney Hall detention facility",
        "hospital": None,
        "victim_name": "Jean Wilson Brutus",
        "victim_age": 41,
        "victim_nationality": "Haiti",
        "cause_of_death": "unknown",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.notus.org/immigration/ice-detention-deaths-december-2025",
        "source_name": "NOTUS / ICE reports",
        "verified": True
    },
    {
        "id": "T1-D-022",
        "date": "2025-12-00",
        "state": "Unknown",
        "facility": "processing center",
        "hospital": None,
        "victim_name": "Fouad Saeed Abdulkadir",
        "victim_age": 46,
        "victim_nationality": "Eritrea",
        "cause_of_death": "unknown",
        "notes": "215 days in detention",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.notus.org/immigration/ice-detention-deaths-december-2025",
        "source_name": "NOTUS / ICE reports",
        "verified": True
    },
    # January 2026 deaths
    {
        "id": "T1-D-023",
        "date": "2026-01-03",
        "state": "Texas",
        "facility": "Camp East Montana, Fort Bliss",
        "hospital": None,
        "victim_name": "Geraldo Lunas Campos",
        "victim_age": 55,
        "victim_nationality": "Cuba",
        "cause_of_death": "homicide_asphyxia",
        "notes": "Medical examiner ruled HOMICIDE - asphyxia due to neck/torso compression. Witnesses saw guards choking him. ICE initially said 'medical distress' then 'suicide'. Lived in US since 1996.",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.npr.org/2026/01/22/g-s1-106773/cuban-immigrant-ice-custody-died-homicide",
        "source_name": "NPR / El Paso Medical Examiner",
        "verified": True
    },
    {
        "id": "T1-D-024",
        "date": "2026-01-14",
        "state": "Texas",
        "facility": "Camp East Montana, Fort Bliss",
        "hospital": None,
        "victim_name": "Victor Manuel Diaz",
        "victim_age": 36,
        "victim_nationality": "Nicaragua",
        "cause_of_death": "presumed_suicide",
        "notes": "Detained during Minneapolis crackdown. Autopsy done by Army medical center, not county ME.",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://elpasomatters.org/2026/01/18/third-death-suicide-ice-custody-camp-east-montana-el-paso-texas-fort-bliss/",
        "source_name": "El Paso Matters / ICE",
        "verified": True
    },
    {
        "id": "T1-D-025",
        "date": "2025-09-29",
        "state": "Unknown",
        "facility": "Unknown",
        "hospital": None,
        "victim_name": "Huabing Xie",
        "victim_age": None,
        "victim_nationality": "China",
        "cause_of_death": "seizure",
        "notes": "23rd official death in FY2025. ICE missed 30-day reporting deadline.",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://austinkocher.substack.com/p/ices-deadly-december-record-setting",
        "source_name": "Austin Kocher / ICE reports",
        "verified": True
    },
    # Additional January 2026 deaths found via systematic search
    {
        "id": "T1-D-026",
        "date": "2026-01-05",
        "state": "Texas",
        "facility": "Joe Corley Processing Center",
        "hospital": None,
        "victim_name": "Luis Gustavo Nunez Caceres",
        "victim_age": 42,
        "victim_nationality": "Unknown",
        "cause_of_death": "unknown",
        "notes": "4th death in first 10 days of 2026.",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.detentionwatchnetwork.org/pressroom/releases/2026/4-ice-detention-deaths-just-10-days-new-year",
        "source_name": "Detention Watch Network / ICE",
        "verified": True
    },
    {
        "id": "T1-D-027",
        "date": "2026-01-06",
        "state": "California",
        "facility": "Imperial Regional Detention Center",
        "hospital": None,
        "victim_name": "Luis Beltran Yanez-Cruz",
        "victim_age": 68,
        "victim_nationality": "Unknown",
        "cause_of_death": "unknown",
        "notes": "One of 4 deaths in first 10 days of 2026.",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.detentionwatchnetwork.org/pressroom/releases/2026/4-ice-detention-deaths-just-10-days-new-year",
        "source_name": "Detention Watch Network / ICE",
        "verified": True
    },
    {
        "id": "T1-D-028",
        "date": "2026-01-09",
        "state": "Pennsylvania",
        "facility": "Federal Detention Center (FDC) Philadelphia",
        "hospital": None,
        "victim_name": "Parady La",
        "victim_age": 46,
        "victim_nationality": "Unknown",
        "cause_of_death": "unknown",
        "notes": "One of 4 deaths in first 10 days of 2026.",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.detentionwatchnetwork.org/pressroom/releases/2026/4-ice-detention-deaths-just-10-days-new-year",
        "source_name": "Detention Watch Network / ICE",
        "verified": True
    },
    {
        "id": "T1-D-029",
        "date": "2026-01-14",
        "state": "Georgia",
        "facility": "Robert A. Deyton Detention Center",
        "city": "Lovejoy",
        "victim_name": "Heber Sanchez Dominguez",
        "victim_nationality": "Mexico",
        "cause_of_death": "found hanging unresponsive",
        "enforcement_granularity": "death_in_custody",
        "victim_category": "detainee",
        "notes": "Found hanging unresponsive. Mexican Consulate demanded clarification. Arrested January 7 for driving without license. Death under investigation.",
        "incident_type": "death_in_custody",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.ice.gov/news/releases/ice-detainee-passes-away-georgias-robert-deyton-detention-center",
        "source_name": "ICE Official Release",
        "verified": True
    },
    # FATAL SHOOTINGS OF US CITIZENS - January 2026
    {
        "id": "T1-S-001",
        "date": "2026-01-07",
        "state": "Minnesota",
        "city": "Minneapolis",
        "victim_name": "Renee Nicole Good",
        "victim_age": 37,
        "us_citizen": True,
        "outcome": "death",
        "enforcement_granularity": "shooting_fatal",
        "victim_category": "bystander",
        "agency": "ICE",
        "incident_type": "shooting_by_agent",
        "notes": "US citizen, 37-year-old mother of three, shot and killed by ICE agent Jonathan Ross. Shot three times while in her vehicle. Video shows car turning away from agent. Governor Walz proclaimed 'Renee Good Day'. Sparked nationwide protests.",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://en.wikipedia.org/wiki/Killing_of_Ren%C3%A9e_Good",
        "source_name": "Multiple sources / Official",
        "verified": True
    },
    {
        "id": "T1-S-002",
        "date": "2026-01-24",
        "state": "Minnesota",
        "city": "Minneapolis (26th & Nicollet)",
        "victim_name": "Alex Pretti",
        "victim_age": 37,
        "victim_occupation": "VA ICU nurse",
        "us_citizen": True,
        "outcome": "death",
        "enforcement_granularity": "shooting_fatal",
        "victim_category": "bystander",
        "agency": "Border Patrol",
        "incident_type": "shooting_by_agent",
        "notes": "37-year-old VA ICU nurse, US citizen, shot and killed by Border Patrol agent. Had legal permit to carry. Bystander video shows him holding cellphone, not firearm. Governor Walz demanded federal agents withdraw from Minnesota.",
        "source_tier": 1,
        "collection_method": "official_report",
        "source_url": "https://www.nbcnews.com/news/us-news/live-blog/minneapolis-immigration-shooting-rcna255737",
        "source_name": "NBC News / Official",
        "verified": True
    },
]

# =============================================================================
# TIER 2: FOIA-OBTAINED / SYSTEMATIC INVESTIGATIVE JOURNALISM
# =============================================================================
# Sources: NBC News (compiled list), The Trace (FOIA + GVA), ProPublica/FRONTLINE

TIER_2_SHOOTINGS_BY_AGENTS = [
    # From NBC News complete list + The Trace tracker
    # Methodology: Gun Violence Archive + news clips + FOIA-obtained logs
    {
        "id": "T2-S-001",
        "date": "2025-09-12",
        "state": "Illinois",
        "city": "Franklin Park",
        "victim_name": "Silverio Villegas Gonzalez",
        "victim_age": 38,
        "victim_nationality": "Mexico",
        "outcome": "death",
        "us_citizen": False,
        "agency": "ICE",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_fatal",
        "circumstances": "Vehicle stop; officers claimed he hit and dragged officer; crashed and died at hospital",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    {
        "id": "T2-S-002",
        "date": "2025-10-04",
        "state": "Illinois",
        "city": "Chicago (Brighton Park)",
        "victim_name": "Marimar Martinez",
        "victim_age": 30,
        "victim_nationality": "USA",
        "outcome": "injury",
        "us_citizen": True,
        "agency": "CBP",
        "agent_name": "Charles Exum",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_nonfatal",
        "circumstances": "Teaching assistant warning residents about raids; shot in shoulder; charges dismissed after video showed agents rammed her vehicle",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    {
        "id": "T2-S-003",
        "date": "2025-10-21",
        "state": "California",
        "city": "Los Angeles",
        "victim_name": "Carlitos Ricardo Parias",
        "victim_age": 44,
        "victim_nationality": "Mexico",
        "outcome": "injury",
        "us_citizen": False,
        "agency": "ICE",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_nonfatal",
        "circumstances": "TikToker 'Richard LA' boxed in by vehicles; shot in arm; charges dismissed for constitutional violations",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    {
        "id": "T2-S-004",
        "date": "2025-10-29",
        "state": "Arizona",
        "city": "Phoenix (I-17)",
        "victim_name": "Jose Garcia-Sorto",
        "victim_age": None,
        "victim_nationality": "Honduras",
        "outcome": "injury",
        "us_citizen": False,
        "agency": "ICE",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_nonfatal",
        "circumstances": "Traffic stop on Interstate 17; shot twice; later released without charges",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    {
        "id": "T2-S-005",
        "date": "2025-10-30",
        "state": "California",
        "city": "Ontario",
        "victim_name": "Carlos Jimenez",
        "victim_age": 25,
        "victim_nationality": "USA",
        "outcome": "injury",
        "us_citizen": True,
        "agency": "ICE",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_nonfatal",
        "circumstances": "Shot in shoulder during enforcement operation; charged with federal assault; trial April 13",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    {
        "id": "T2-S-006",
        "date": "2025-12-11",
        "state": "Texas",
        "city": "Rio Grande City (Starr County)",
        "victim_name": "Isaias Sanchez Barboza",
        "victim_age": 31,
        "victim_nationality": "Mexico",
        "outcome": "death",
        "us_citizen": False,
        "agency": "CBP",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_fatal",
        "circumstances": "Border confrontation; shot 3 times during 'active struggle'",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    {
        "id": "T2-S-007",
        "date": "2025-12-24",
        "state": "Maryland",
        "city": "Glen Burnie",
        "victim_name": "Tiago Alexandre Sousa-Martins",
        "victim_age": None,
        "victim_nationality": "Portugal",
        "outcome": "injury",
        "us_citizen": False,
        "agency": "ICE",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_nonfatal",
        "circumstances": "Visa overstay since 2009; shot in van after allegedly ramming ICE vehicles",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    {
        "id": "T2-S-008",
        "date": "2026-01-07",
        "state": "Minnesota",
        "city": "Minneapolis",
        "victim_name": "Renee Good",
        "victim_age": 37,
        "victim_nationality": "USA",
        "outcome": "death",
        "us_citizen": True,
        "agency": "ICE",
        "agent_name": "Jonathan Ross",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_fatal",
        "circumstances": "Shot 3 times (chest, head) while backing car away; video contradicts DHS account; FBI investigating",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    {
        "id": "T2-S-009",
        "date": "2026-01-08",
        "state": "Oregon",
        "city": "Portland",
        "victim_name": "Luis David Nino Moncada",
        "victim_age": 33,
        "victim_nationality": "Venezuela",
        "outcome": "injury",
        "us_citizen": False,
        "agency": "CBP",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_nonfatal",
        "circumstances": "Shot in arm during gang enforcement operation; charged with assault",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    {
        "id": "T2-S-010",
        "date": "2026-01-08",
        "state": "Oregon",
        "city": "Portland",
        "victim_name": "Yorlenys Betzabeth Zambrano-Contreras",
        "victim_age": None,
        "victim_nationality": "Venezuela",
        "outcome": "injury",
        "us_citizen": False,
        "agency": "CBP",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_nonfatal",
        "circumstances": "Shot in chest during gang enforcement operation; charged with illegal entry",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    {
        "id": "T2-S-011",
        "date": "2026-01-14",
        "state": "Minnesota",
        "city": "Minneapolis",
        "victim_name": "Julio Cesar Sosa-Celis",
        "victim_age": None,
        "victim_nationality": "Venezuela",
        "outcome": "injury",
        "us_citizen": False,
        "agency": "ICE",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_nonfatal",
        "circumstances": "Shot in upper thigh during foot pursuit; entered US illegally 2022; criminal complaint contradicted DHS account",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    {
        "id": "T2-S-012",
        "date": "2026-01-24",
        "state": "Minnesota",
        "city": "Minneapolis",
        "victim_name": "Alex Jeffrey Pretti",
        "victim_age": 37,
        "victim_nationality": "USA",
        "outcome": "death",
        "us_citizen": True,
        "agency": "CBP",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_fatal",
        "circumstances": "ICU nurse at Minneapolis VA; shot while observing enforcement; video shows agent removed gun from waistband before other agent fired; lawful gun owner with permit",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.nbcnews.com/news/us-news/alex-pretti-fatally-shot-federal-officers-minneapolis-identified-paren-rcna255758",
        "source_name": "NBC News",
        "verified": True
    },
]

# Attacks on agents/facilities
TIER_2_SHOOTINGS_AT_AGENTS = [
    {
        "id": "T2-SA-001",
        "date": "2025-07-04",
        "state": "Texas",
        "city": "Alvarado",
        "victim_name": "Police officer (unnamed)",
        "outcome": "injury",
        "perpetrator": "civilian",
        "incident_type": "shooting_at_agent",
        "enforcement_granularity": "shooting_at_agent",
        "circumstances": "Coordinated attack on ICE facility; officer shot in neck; 18 arrested; 7 pled guilty to terrorism",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.kut.org/crime-justice/2025-07-08/11-arrested-in-wake-of-officer-shooting-outside-texas-ice-facility",
        "source_name": "KUT",
        "verified": True
    },
    {
        "id": "T2-SA-002",
        "date": "2025-09-24",
        "state": "Texas",
        "city": "Dallas",
        "victim_name": "Norlan Guzman-Fuentes (37) + 1 other detainee",
        "outcome": "death",
        "perpetrator": "Joshua Jahn (sniper)",
        "incident_type": "shooting_at_agent",
        "enforcement_granularity": "shooting_at_agent",
        "circumstances": "Sniper fired from rooftop into sally port; 'ANTI-ICE' markings on ammunition; 2 killed, 1 injured",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.npr.org/2025/09/24/nx-s1-5552151/ice-dallas-detention-facility-shooting",
        "source_name": "NPR",
        "verified": True
    },
    {
        "id": "T2-SA-003",
        "date": "2025-07-07",
        "state": "Texas",
        "city": "McAllen",
        "victim_name": "3 Border Patrol agents",
        "outcome": "injury",
        "perpetrator": "Ryan Louis Mosqueda (27)",
        "incident_type": "shooting_at_agent",
        "enforcement_granularity": "shooting_at_agent",
        "circumstances": "Fired dozens of shots at agents exiting facility; mental health issues claimed",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.aljazeera.com/news/2025/9/25/are-attacks-on-ice-officers-facilities-in-the-us-rising",
        "source_name": "Al Jazeera",
        "verified": True
    },
]

# ProPublica/FRONTLINE systematic investigation of less-lethal force
TIER_2_LESS_LETHAL = [
    {
        "id": "T2-LL-001",
        "date": "2025-06-00",  # June 2025
        "state": "Oregon",
        "city": "Portland",
        "victim_name": "Vincent Hawkins",
        "victim_age": 55,
        "victim_occupation": "ER nurse",
        "weapon_used": "tear_gas_canister",
        "injury": "shattered glasses, torn brow, eye damage, concussion, partial vision loss, ongoing vertigo",
        "injury_type": "eye damage, concussion, partial vision loss",
        "us_citizen": True,
        "protest_related": True,
        "protest_granularity": "individual_injury",
        "victim_category": "protester",
        "incident_type": "less_lethal",
        "circumstances": "Canister shot through closed gate at ICE facility protest",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.propublica.org/article/ice-border-patrol-less-lethal-weapons",
        "source_name": "ProPublica/FRONTLINE",
        "verified": True
    },
    {
        "id": "T2-LL-002",
        "date": "2025-06-07",
        "state": "California",
        "city": "Los Angeles (Home Depot protest)",
        "victim_name": "Local journalist (unnamed)",
        "weapon_used": "rubber_bullet",
        "injury": "head wound, concussion",
        "injury_type": "head wound, concussion",
        "us_citizen": True,
        "protest_related": True,
        "protest_granularity": "journalist_attack",
        "victim_category": "journalist",
        "incident_type": "less_lethal",
        "circumstances": "Reporter shot in head while covering protest",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.propublica.org/article/ice-border-patrol-less-lethal-weapons",
        "source_name": "ProPublica/FRONTLINE",
        "verified": True
    },
    {
        "id": "T2-LL-003",
        "date": "2025-10-23",
        "state": "California",
        "city": "Oakland",
        "victim_name": "Pastor Jorge Bautista",
        "weapon_used": "pepper_powder",
        "injury": "facial burns, difficulty breathing, hospital treatment",
        "injury_type": "facial burns, respiratory distress",
        "medical_treatment": "hospital treatment",
        "us_citizen": True,
        "protest_related": True,
        "protest_granularity": "individual_injury",
        "victim_category": "protester",
        "incident_type": "less_lethal",
        "circumstances": "Shot while saying 'We come in peace' at waterfront near Coast Guard base; plans lawsuit",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.propublica.org/article/ice-border-patrol-less-lethal-weapons",
        "source_name": "ProPublica/FRONTLINE",
        "verified": True
    },
    {
        "id": "T2-LL-004",
        "date": "2025-09-00",  # September 2025
        "state": "Illinois",
        "city": "Broadview",
        "victim_name": "Raven Geary",
        "victim_occupation": "independent journalist",
        "weapon_used": "pepper_ball",
        "injury": "facial wound, bleeding, bruising",
        "injury_type": "facial wound, bleeding, bruising",
        "us_citizen": True,
        "protest_related": True,
        "protest_granularity": "journalist_attack",
        "victim_category": "journalist",
        "incident_type": "less_lethal",
        "circumstances": "Shot while wearing press badge and carrying cameras",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.propublica.org/article/ice-border-patrol-less-lethal-weapons",
        "source_name": "ProPublica/FRONTLINE",
        "verified": True
    },
    {
        "id": "T2-LL-005",
        "date": "2025-09-00",
        "state": "Illinois",
        "city": "Broadview",
        "victim_name": "Leigh Kunkel",
        "weapon_used": "pepper_balls",
        "injury": "back-of-head and nose strikes",
        "injury_type": "head and nose strikes",
        "us_citizen": True,
        "protest_related": True,
        "protest_granularity": "individual_injury",
        "victim_category": "protester",
        "incident_type": "less_lethal",
        "circumstances": "Narrowly avoided eye injury by inches",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.propublica.org/article/ice-border-patrol-less-lethal-weapons",
        "source_name": "ProPublica/FRONTLINE",
        "verified": True
    },
    {
        "id": "T2-LL-006",
        "date": "2025-09-00",
        "state": "Illinois",
        "city": "Broadview",
        "victim_name": "Autumn Hamer",
        "victim_occupation": "nearby resident, mother",
        "weapon_used": "rubber_bullets, pepper_balls, flash_bang",
        "injury": "disorientation, ear ringing",
        "injury_type": "disorientation, ear ringing",
        "us_citizen": True,
        "protest_related": True,
        "protest_granularity": "individual_injury",
        "victim_category": "bystander",
        "incident_type": "less_lethal",
        "circumstances": "Officers fired from roof into peaceful crowd; grenade landed nearby; projectile destroyed acoustic guitar",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.propublica.org/article/ice-border-patrol-less-lethal-weapons",
        "source_name": "ProPublica/FRONTLINE",
        "verified": True
    },
    {
        "id": "T2-LL-007",
        "date": "2025-09-00",
        "state": "Illinois",
        "city": "Chicago (Little Village)",
        "victim_name": "Enrique Bahena",
        "victim_occupation": "activist",
        "weapon_used": "pepper_ball_launcher",
        "injury": "throat strike with noxious smoke",
        "injury_type": "throat strike",
        "us_citizen": True,
        "protest_related": True,
        "protest_granularity": "individual_injury",
        "victim_category": "protester",
        "incident_type": "less_lethal",
        "circumstances": "First-person video captured agent firing at close range",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.propublica.org/article/ice-border-patrol-less-lethal-weapons",
        "source_name": "ProPublica/FRONTLINE",
        "verified": True
    },
    # Chicago Sun-Times documented cases
    {
        "id": "T2-LL-008",
        "date": "2025-09-26",
        "state": "Illinois",
        "city": "Broadview",
        "victim_name": "Brian Rivera",
        "weapon_used": "pepper_balls",
        "injury": "hit in chest and shoulder",
        "injury_type": "chest and shoulder strikes",
        "us_citizen": False,
        "protest_related": True,
        "protest_granularity": "individual_injury",
        "victim_category": "protester",
        "incident_type": "less_lethal",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://chicago.suntimes.com/graphics/immigration/2025/ice-less-lethal-weapons-explainer-tear-gas/",
        "source_name": "Chicago Sun-Times",
        "verified": True
    },
    {
        "id": "T2-LL-009",
        "date": "2025-09-19",
        "state": "Illinois",
        "city": "Broadview",
        "victim_name": "Curtis Evans",
        "victim_age": 65,
        "victim_occupation": "military veteran",
        "weapon_used": "tear_gas",
        "injury": "exposure causing panic response",
        "injury_type": "tear gas exposure, panic response",
        "us_citizen": True,
        "protest_related": True,
        "protest_granularity": "individual_injury",
        "victim_category": "protester",
        "incident_type": "less_lethal",
        "circumstances": "Veterans training recalled involuntarily",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://chicago.suntimes.com/graphics/immigration/2025/ice-less-lethal-weapons-explainer-tear-gas/",
        "source_name": "Chicago Sun-Times",
        "verified": True
    },
    {
        "id": "T2-LL-010",
        "date": "2025-09-26",
        "state": "Illinois",
        "city": "Broadview",
        "victim_name": "Joselyn Walsh",
        "weapon_used": "40mm_baton_round",
        "injury": "projectile penetrated guitar and struck leg",
        "injury_type": "leg strike from baton round",
        "us_citizen": False,
        "protest_related": True,
        "protest_granularity": "individual_injury",
        "victim_category": "protester",
        "incident_type": "less_lethal",
        "circumstances": "Federally charged in October with conspiracy to impede officer",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://chicago.suntimes.com/graphics/immigration/2025/ice-less-lethal-weapons-explainer-tear-gas/",
        "source_name": "Chicago Sun-Times",
        "verified": True
    },
]

# ProPublica investigation of US citizens wrongfully detained
TIER_2_WRONGFUL_DETENTIONS = [
    {
        "id": "T2-WD-001",
        "date": "2025-07-00",  # July 2025
        "state": "California",
        "city": "Camarillo area",
        "victim_name": "George Retes",
        "us_citizen": True,
        "veteran": True,
        "disabled": True,
        "detention_duration": "3 days without contact",
        "injury": "pepper spray, leg laceration from glass, pepper spray burns",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "circumstances": "Disabled combat veteran arrested during marijuana farm raid; released without charges",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.propublica.org/article/immigration-dhs-american-citizens-arrested-detained-against-will",
        "source_name": "ProPublica",
        "verified": True
    },
    {
        "id": "T2-WD-002",
        "date": "2025-00-00",
        "state": "Alabama",
        "city": "Coastal Alabama",
        "victim_name": "Leonardo Garcia Venegas",
        "us_citizen": True,
        "detention_duration": "over 1 hour",
        "injury": "twisted arms, attempted takedown",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "circumstances": "Detained while filming at construction site; REAL ID dismissed as fake",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.propublica.org/article/immigration-dhs-american-citizens-arrested-detained-against-will",
        "source_name": "ProPublica",
        "verified": True
    },
    {
        "id": "T2-WD-003",
        "date": "2025-00-00",
        "state": "California",
        "city": "Los Angeles (downtown)",
        "victim_name": "Andrea Velez",
        "us_citizen": True,
        "detention_duration": "over 2 days",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "circumstances": "Caught during street vendor raid; charged with assaulting officer (charges dismissed); held incommunicado",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.propublica.org/article/immigration-dhs-american-citizens-arrested-detained-against-will",
        "source_name": "ProPublica",
        "verified": True
    },
    {
        "id": "T2-WD-004",
        "date": "2025-00-00",  # Summer 2025
        "state": "California",
        "city": "Van Nuys",
        "victim_name": "Daniel Montenegro",
        "us_citizen": True,
        "injury": "back injury from tackle",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "circumstances": "Day-laborer advocate filming at Home Depot; Border Patrol chief named him on social media with false accusations; no charges filed",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.propublica.org/article/immigration-dhs-american-citizens-arrested-detained-against-will",
        "source_name": "ProPublica",
        "verified": True
    },
    {
        "id": "T2-WD-005",
        "date": "2025-00-00",
        "state": "California",
        "city": "Unknown",
        "victim_name": "Rafie Ollah Shouhed",
        "victim_age": 79,
        "us_citizen": True,
        "detention_duration": "12 hours",
        "injury": "broken ribs, recent heart surgery patient",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "circumstances": "79-year-old tackled at car wash; knees pressed into neck/back",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://www.propublica.org/article/immigration-dhs-american-citizens-arrested-detained-against-will",
        "source_name": "ProPublica",
        "verified": True
    },
    {
        "id": "T2-WD-006",
        "date": "2025-10-10",
        "state": "Illinois",
        "city": "Chicago",
        "victim_name": "Debbie Brockman",
        "us_citizen": True,
        "victim_occupation": "WGN-TV employee",
        "detention_duration": "7 hours",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "circumstances": "Detained while videotaping agents; pursuing legal action for assault and wrongful arrest",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://factually.co/fact-checks/politics/us-citizens-detained-ice-deported-2025-24be17",
        "source_name": "Factually (compiled)",
        "verified": True
    },
    {
        "id": "T2-WD-007",
        "date": "2025-06-00",
        "state": "California",
        "city": "Los Angeles area",
        "victim_name": "Adrian Andrew Martinez",
        "us_citizen": True,
        "birthplace": "Los Angeles",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "circumstances": "Detained outside Walmart; video shows agents in tactical gear wrestling him to ground; held incommunicado",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://factually.co/fact-checks/politics/us-citizens-detained-ice-deported-2025-24be17",
        "source_name": "Factually (compiled)",
        "verified": True
    },
    {
        "id": "T2-WD-008",
        "date": "2025-02-04",
        "state": "Unknown",
        "city": "Unknown (checkpoint)",
        "victim_name": "10-year-old girl with brain cancer + family",
        "us_citizen": True,
        "children_affected": True,
        "incident_type": "wrongful_deportation",
        "enforcement_granularity": "wrongful_deportation",
        "circumstances": "US citizen child with brain cancer deported with parents and 4 siblings at checkpoint en route to emergency medical appointment",
        "source_tier": 2,
        "collection_method": "investigative",
        "source_url": "https://factually.co/fact-checks/politics/us-citizens-detained-ice-deported-2025-24be17",
        "source_name": "Factually (compiled)",
        "verified": True
    },
    # ACLU lawsuit - Massachusetts case
    {
        "id": "T2-WD-009",
        "date": "2025-11-06",
        "state": "Massachusetts",
        "city": "Fitchburg",
        "victim_name": "Carlos Zapata Rivera",
        "us_citizen": False,
        "victim_nationality": "Ecuador",
        "injury": "loss of consciousness, seizure-like movements",
        "weapon_used": "carotid_restraint",
        "incident_type": "physical_force",
        "enforcement_granularity": "wrongful_detention",
        "circumstances": "Driving wife to work with 1-year-old daughter; ICE agent applied prohibited carotid restraint (thumbs on arteries). DHS policy prohibits this except when deadly force justified. Filed ACLU lawsuit.",
        "source_tier": 2,
        "collection_method": "litigation",
        "source_url": "https://www.aclum.org/press-releases/fitchburg-resident-sues-ice-agent-for-unlawful-use-of-excessive-force-during-vehicle-stop-and-arrest/",
        "source_name": "ACLU Massachusetts",
        "verified": True
    },
    # Minnesota ACLU class action plaintiffs
    {
        "id": "T2-WD-010",
        "date": "2025-12-00",
        "state": "Minnesota",
        "city": "Minneapolis (Near North)",
        "victim_name": "Susan Tincher",
        "us_citizen": True,
        "incident_type": "less_lethal",
        "enforcement_granularity": "wrongful_detention",
        "circumstances": "30-year resident; pepper-sprayed while observing enforcement. Named plaintiff in Tincher v. Noem class action.",
        "source_tier": 2,
        "collection_method": "litigation",
        "source_url": "https://www.courthousenews.com/aclu-of-minnesota-sues-ice-dhs-over-constitutional-violations-against-observers/",
        "source_name": "ACLU Minnesota / Courthouse News",
        "verified": True
    },
    {
        "id": "T2-WD-011",
        "date": "2025-12-07",
        "state": "Minnesota",
        "city": "Minneapolis (Linden Hills)",
        "victim_name": "John Biestman",
        "us_citizen": True,
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "circumstances": "Followed home by unmarked cars; named plaintiff in class action.",
        "source_tier": 2,
        "collection_method": "litigation",
        "source_url": "https://www.courthousenews.com/aclu-of-minnesota-sues-ice-dhs-over-constitutional-violations-against-observers/",
        "source_name": "ACLU Minnesota / Courthouse News",
        "verified": True
    },
]


# =============================================================================
# TIER 3: NEWS MEDIA - SYSTEMATIC SEARCH
# =============================================================================
# Found via comprehensive search of major news outlets for specific incident types
# May have geographic/coverage bias but search methodology was consistent

TIER_3_INCIDENTS = [
    # LA protests - June 2025
    {
        "id": "T3-001",
        "date": "2025-06-07",
        "state": "California",
        "city": "Los Angeles (Paramount)",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "victim_category": "protester",
        "weapon_used": "flash_bangs, pepper_spray, tear_gas, foam_batons, bean_bags",
        "victim_name": "Multiple protesters",
        "outcome": "multiple injuries",
        "protest_related": True,
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.npr.org/2025/06/07/nx-s1-5426518/ice-conducts-sweeping-raids-in-l-a-clashes-with-protestors",
        "source_name": "NPR",
        "verified": True
    },
    {
        "id": "T3-002",
        "date": "2025-06-10",
        "state": "California",
        "city": "Los Angeles",
        "incident_type": "less_lethal",
        "protest_granularity": "journalist_attack",
        "victim_category": "journalist",
        "weapon_used": "pepper_balls",
        "victim_name": "Australian journalist (ABC crew)",
        "outcome": "injury",
        "us_citizen": False,
        "protest_related": True,
        "notes": "Australian PM called it 'targeted'; raised with Trump administration",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.opb.org/article/2025/06/09/los-angeles-immigration-protest/",
        "source_name": "OPB",
        "verified": True
    },
    # NYC protests
    {
        "id": "T3-003",
        "date": "2025-11-29",
        "state": "New York",
        "city": "Manhattan (SoHo/Canal St)",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "victim_category": "protester",
        "weapon_used": "pepper_spray",
        "victim_name": "Multiple protesters",
        "arrest_count": 12,
        "outcome": "multiple injuries, 12+ arrests",
        "protest_related": True,
        "notes": "NYPD arrested 12+; protesters had bloody faces",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.thecity.nyc/2025/11/29/nypd-ice-homeland-security-canal/",
        "source_name": "The City NYC",
        "verified": True
    },
    # Georgia protests
    {
        "id": "T3-004",
        "date": "2025-06-10",
        "state": "Georgia",
        "city": "Brookhaven",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "victim_category": "protester",
        "weapon_used": "tear_gas",
        "victim_name": "Multiple protesters",
        "outcome": "multiple injuries",
        "protest_related": True,
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.fox5atlanta.com/news/hundreds-gather-anti-ice-rally-along-buford-highway-brookhaven",
        "source_name": "Fox 5 Atlanta",
        "verified": True
    },
    # Colorado protests
    {
        "id": "T3-005",
        "date": "2025-10-27",
        "state": "Colorado",
        "city": "Durango",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "victim_category": "protester",
        "weapon_used": "pepper_spray, rubber_bullets",
        "victim_name": "Multiple protesters",
        "outcome": "multiple injuries",
        "notes": "7+ ICE agents in camouflage; one protester shot twice with rubber bullets",
        "protest_related": True,
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cpr.org/2025/10/30/durango-protesters-federal-agents-pepper-spray-rubber-bullets/",
        "source_name": "CPR News",
        "verified": True
    },
    # Oregon protests/enforcement
    {
        "id": "T3-006",
        "date": "2025-10-02",
        "state": "Oregon",
        "city": "Portland",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "victim_category": "protester",
        "weapon_used": "pepper_spray",
        "victim_name": "Leilani Payne",
        "victim_weight": "95 pounds",
        "injury_type": "pepper spray exposure",
        "outcome": "injury",
        "protest_related": True,
        "notes": "4 agents on her; maced for 3 seconds straight without warning",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.kgw.com/article/news/local/federal-agents-tackle-mace-protesters-portland-ice-facility-oregon-national-guard/283-e36a3494-d725-43a6-acd1-882f98169002",
        "source_name": "KGW",
        "verified": True
    },
    {
        "id": "T3-007",
        "date": "2025-12-11",
        "state": "Oregon",
        "city": "Portland (North)",
        "incident_type": "less_lethal",
        "enforcement_granularity": "individual_force",
        "weapon_used": "pepper_balls",
        "victim_name": "Bystanders",
        "outcome": "injuries",
        "protest_related": False,
        "notes": "Mayor and councilors called tactics 'unjustified, disruptive and escalatory'",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.opb.org/article/2025/12/16/north-portland-ice-arrest-pepper-balls/",
        "source_name": "OPB",
        "verified": True
    },
    # Minneapolis wrongful detention
    {
        "id": "T3-008",
        "date": "2025-12-10",
        "state": "Minnesota",
        "city": "Minneapolis (Cedar-Riverside)",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_name": "Mubashir Khalif Hussen",
        "victim_age": 20,
        "us_citizen": True,
        "outcome": "no physical injury",
        "notes": "Told agents 'I'm a US citizen'; one agent put him in chokehold",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cbsnews.com/minnesota/news/minneapolis-leaders-say-us-citizen-was-wrongfully-arrested-by-ice-agents/",
        "source_name": "CBS Minnesota",
        "verified": True
    },
    # Mass raids with documented details
    {
        "id": "T3-009",
        "date": "2025-09-04",
        "state": "Georgia",
        "city": "Ellabell (Hyundai plant)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_count": 475,
        "outcome": "no injuries reported",
        "notes": "South Korean government expressed 'concern and regret'; workers said 'not even prisoners of war would be treated like that'",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cnn.com/2025/09/08/us/georgia-hyundai-ice-raid-community",
        "source_name": "CNN",
        "verified": True
    },
    # Charlotte, NC - Operation Charlotte's Web
    {
        "id": "T3-010",
        "date": "2025-11-15",
        "state": "North Carolina",
        "city": "Charlotte",
        "incident_type": "physical_force",
        "enforcement_granularity": "individual_force",
        "victim_name": "Latino US citizen (unnamed)",
        "us_citizen": True,
        "outcome": "injury",
        "notes": "Agents shattered car window of US citizen and violently dragged him out. CBP let him go. Governor Stein called it 'racial profiling'.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cnn.com/2025/11/19/us/north-carolina-charlotte-ice-raids-what-we-know",
        "source_name": "CNN",
        "verified": True
    },
    {
        "id": "T3-011",
        "date": "2025-11-16",
        "state": "North Carolina",
        "city": "Charlotte",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_community",
        "victim_count": 250,
        "notes": "Most arrests in single day in NC history. Paramilitary garb, faces covered, assault weapons. Mayor Pro Tem called it 'going through the city' targeting South and East Charlotte.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://prismreports.org/2025/11/19/north-carolina-immigration-raids-ice/",
        "source_name": "Prism Reports",
        "verified": True
    },
    # NYC incidents
    {
        "id": "T3-012",
        "date": "2025-10-21",
        "state": "New York",
        "city": "Manhattan (Canal Street)",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_name": "4 US citizens",
        "us_citizen": True,
        "detention_duration": "24 hours",
        "notes": "Held at 26 Federal Plaza. 50+ federal agents involved in counterfeit goods raid.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://abcnews.go.com/US/nyc-residents-increase-ice-arrests-after-crackdown-canal/story?id=126763379",
        "source_name": "ABC News",
        "verified": True
    },
    {
        "id": "T3-013",
        "date": "2025-11-29",
        "state": "New York",
        "city": "Manhattan (SoHo/Chinatown)",
        "incident_type": "less_lethal",
        "enforcement_granularity": "individual_force",
        "weapon_used": "pepper_spray",
        "victim_name": "Multiple protesters",
        "outcome": "multiple injuries",
        "notes": "NYPD arrested 12+; protesters had bloody faces; pepper spray and unknown orange substance used. NYC Immigration Coalition called it 'campaign of terror'.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.thecity.nyc/2025/11/29/nypd-ice-homeland-security-canal/",
        "source_name": "The City NYC",
        "verified": True
    },
    # Virginia courthouse incident
    {
        "id": "T3-014",
        "date": "2025-04-22",
        "state": "Virginia",
        "city": "Charlottesville (Albemarle Courthouse)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_targeted",
        "victim_count": 2,
        "notes": "Plain-clothed ICE officers detained 2 men. ICE promised to prosecute bystanders who questioned agents. Local official called courthouse 'sacred place in democracy'.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.vpm.org/news/2025-04-23/albemarle-courthouse-ice-raid-nicholas-reppucci-teodoro-dominguez-rodriguez",
        "source_name": "VPM",
        "verified": True
    },
    # Louisiana incidents
    {
        "id": "T3-015",
        "date": "2025-12-03",
        "state": "Louisiana",
        "city": "New Orleans",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_community",
        "victim_count": 38,  # First 2 days
        "notes": "Operation Catahoula Crunch - 250 agents aimed to make 5000 arrests over 2 months. Less than 1/3 had criminal records. Viral video of agents chasing 23-year-old US citizen.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cnn.com/2025/12/07/us/new-orleans-immigration-ice-agents",
        "source_name": "CNN",
        "verified": True
    },
    {
        "id": "T3-016",
        "date": "2025-12-00",
        "state": "Louisiana",
        "city": "Calcasieu Parish",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_count": 84,
        "facility": "Delta Downs Racetrack and Casino",
        "notes": "Worksite enforcement operation",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.wdsu.com/article/louisiana-race-track-ice-raid/65105689",
        "source_name": "WDSU",
        "verified": True
    },
    # =========================================================================
    # TIER 3 DATA FOR PREVIOUSLY "MISSING" STATES (Added 2026-01-24)
    # =========================================================================
    # Tennessee
    {
        "id": "T3-017",
        "date": "2025-05-04",
        "state": "Tennessee",
        "city": "Nashville (South Nashville)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_community",
        "victim_count": 196,
        "notes": "THP + ICE operation. 468 traffic stops over 5 days, ~100 ICE detentions. 70% had no criminal record. Targeted Latino neighborhoods in early morning hours.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://nashvillebanner.com/2025/05/04/ice-immigration-operation-nashville/",
        "source_name": "Nashville Banner",
        "verified": True
    },
    {
        "id": "T3-018",
        "date": "2025-10-00",
        "state": "Tennessee",
        "city": "Memphis area",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_community",
        "victim_count": 800,  # October statewide
        "notes": "800 arrests statewide in October. Nearly half had no criminal conviction. West Tennessee Detention Facility in Mason reopened for ICE. 'At least 3 people detained every day' in Memphis.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://mlk50.com/2025/10/03/surge-in-ice-arrests-around-memphis-fueled-by-people-who-havent-committed-any-crimes/",
        "source_name": "MLK50",
        "verified": True
    },
    # Iowa
    {
        "id": "T3-019",
        "date": "2025-09-26",
        "state": "Iowa",
        "city": "Des Moines",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_name": "Ian Roberts",
        "victim_occupation": "Superintendent, Des Moines Public Schools (largest district in Iowa)",
        "notes": "Arrested in 'targeted enforcement operation'. Had student visa from 1999, final removal order May 2024. Found with loaded handgun, $3,000 cash. Major controversy.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cnn.com/2025/09/26/us/ian-roberts-des-moines-superintendent-arrested-ice",
        "source_name": "CNN",
        "verified": True
    },
    {
        "id": "T3-020",
        "date": "2025-09-25",
        "state": "Iowa",
        "city": "Iowa City",
        "incident_type": "physical_force",
        "enforcement_granularity": "individual_force",
        "victim_name": "Jorge Gonzalez",
        "notes": "3 plainclothes ICE officers tackled undocumented immigrant to ground in downtown Iowa City. Video footage captured onlookers questioning agents.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://jgrj.law.uiowa.edu/news/2025/10/iowa-city-ice-raids-make-city-less-safe",
        "source_name": "U of Iowa Journal of Gender, Race & Justice",
        "verified": True
    },
    # Indiana
    {
        "id": "T3-021",
        "date": "2025-10-00",
        "state": "Indiana",
        "city": "Northwest Indiana (I-94/I-80)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_targeted",
        "victim_count": 223,
        "notes": "Operation Midway Blitz. 146 were truck drivers. Named for Katie Abraham, killed by drunk driver. Part of Chicago-area surge. 12 had criminal histories.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.ice.gov/news/releases/ice-arrests-223-illegal-aliens-along-northwest-indiana-highways",
        "source_name": "ICE",
        "verified": True
    },
    {
        "id": "T3-022",
        "date": "2025-05-01",
        "state": "Indiana",
        "city": "Evansville/Bloomington",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_targeted",
        "victim_count": 23,
        "notes": "Multi-agency operation Apr 29-May 1. ICE, FBI, DEA, ATF, US Marshals. 18 of 23 had prior criminal arrests/convictions.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.ice.gov/news/releases/ice-leads-joint-operation-southern-indiana",
        "source_name": "ICE",
        "verified": True
    },
    {
        "id": "T3-023",
        "date": "2025-08-00",
        "state": "Indiana",
        "city": "Seymour",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_targeted",
        "victim_count": 11,
        "notes": "FBI/ICE/DHS coordinated sweep targeting people with violent criminal histories.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.wlky.com/article/seymour-indiana-ice-raids-immigrants/65834447",
        "source_name": "WLKY",
        "verified": True
    },
    # Washington
    {
        "id": "T3-024",
        "date": "2025-02-28",
        "state": "Washington",
        "city": "SeaTac",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_name": "Lewelyn Dixon",
        "victim_age": 64,
        "us_citizen": False,  # Green card holder 50+ years
        "notes": "UW lab technician detained at SeaTac returning from Philippines. Green card holder 50+ years, legally allowed to live/work in US indefinitely. Transferred to Tacoma NWDC.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.realchangenews.org/news/2025/04/09/ice-ramps-attacks-immigrant-communities-washington",
        "source_name": "Real Change",
        "verified": True
    },
    {
        "id": "T3-025",
        "date": "2025-04-05",
        "state": "Washington",
        "city": "SeaTac/Tacoma",
        "incident_type": "less_lethal",
        "protest_granularity": "confrontation",
        "victim_category": "protester",
        "crowd_size": 1000,
        "victim_name": "Multiple protesters",
        "outcome": "arrests",
        "protest_related": True,
        "notes": "~1,000 protesters at Federal Detention Center. Hundreds rallied at NWDC March 29 for Dixon and union workers. 59% of Tacoma detainees listed as non-criminal.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.kuow.org/stories/hundreds-rally-at-ice-center-in-tacoma-after-detention-of-union-members",
        "source_name": "KUOW",
        "verified": True
    },
    {
        "id": "T3-026",
        "date": "2025-00-00",
        "state": "Washington",
        "city": "South of Seattle",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_count": 17,
        "facility": "Eagle Beverage",
        "notes": "Workplace raid at beverage bottling company. Agents had search warrant for fake work papers.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://washingtonstatestandard.com/2025/12/17/immigration-arrests-in-wa-surged-in-recent-months/",
        "source_name": "Washington State Standard",
        "verified": True
    },
    # Oklahoma
    {
        "id": "T3-027",
        "date": "2025-04-24",
        "state": "Oklahoma",
        "city": "Oklahoma City",
        "incident_type": "physical_force",
        "enforcement_granularity": "individual_force",
        "victim_name": "US citizen family (wrong address)",
        "us_citizen": True,
        "notes": "Human smuggling raid hit WRONG ADDRESS. Family forced outside in underwear in rain. Phones, laptops, life savings seized. DHS acknowledged 'U.S. citizens recently moved' to address.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.newsweek.com/ice-agents-force-family-underwear-oklahoma-2065984",
        "source_name": "Newsweek",
        "verified": True
    },
    {
        "id": "T3-028",
        "date": "2025-09-25",
        "state": "Oklahoma",
        "city": "I-40 (Beckham County)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_targeted",
        "victim_count": 120,
        "notes": "3-day I-40 highway operation Sep 22-25. 520 drivers screened at port of entry. 91 were commercial truck drivers with CDLs. OHP + ICE collaboration.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.kosu.org/local-news/2025-10-01/oklahoma-troopers-arrest-more-than-100-people-in-3-day-immigration-blitz",
        "source_name": "KOSU",
        "verified": True
    },
    # Mississippi
    {
        "id": "T3-029",
        "date": "2025-01-00",
        "state": "Mississippi",
        "city": "Jackson area",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_community",
        "victim_count": 58,
        "notes": "4-day operation in Jackson area. Included convicted criminals, immigration fugitives, gang members. Arrests in Brandon, Pearl, Ridgeland, Canton, Carthage, Crystal Springs, Hazlehurst.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.ice.gov/news/releases/ice-arrests-58-convicted-criminal-aliens-fugitives-enforcement-surge",
        "source_name": "ICE",
        "verified": True
    },
    {
        "id": "T3-030",
        "date": "2025-02-00",
        "state": "Mississippi",
        "city": "Pass Christian (Gulf Coast)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_count": 16,
        "facility": "Gulf Coast Prestress Partners",
        "notes": "Workers caught fleeing out back during workplace raid.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.foxnews.com/us/ice-arrests-16-illegal-migrants-caught-fleeing-mississippi-business-raid",
        "source_name": "Fox News",
        "verified": True
    },
    {
        "id": "T3-031",
        "date": "2025-07-18",
        "state": "Mississippi",
        "city": "Jackson",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_count": 5,
        "facility": "Agave Mexican Bar and Grill",
        "notes": "Restaurant raid. 4 males, 1 female handcuffed at work. Owner believes agents were tipped off.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.wlbt.com/2025/07/18/popular-mexican-restaurant-raided-by-ice-jackson/",
        "source_name": "WLBT",
        "verified": True
    },
    # Nevada
    {
        "id": "T3-032",
        "date": "2025-04-17",
        "state": "Nevada",
        "city": "Las Vegas",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_count": 8,  # Work site, possibly more
        "notes": "ICE activity Apr 13-17 in Las Vegas Valley. 8 men arrested from Downtown work site. Reports of 100 ICE agents moved into area. ICE at bakery detained legal permanent resident.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://knpr.org/show/knprs-state-of-nevada/2025-04-24/reported-ice-activity-in-las-vegas-raises-alarm-for-immigration-advocates",
        "source_name": "KNPR",
        "verified": True
    },
    {
        "id": "T3-033",
        "date": "2025-06-11",
        "state": "Nevada",
        "city": "Las Vegas (Downtown)",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "victim_category": "protester",
        "weapon_used": "pepper_balls, tear_gas",
        "victim_name": "Multiple protesters",
        "outcome": "multiple injuries",
        "protest_related": True,
        "notes": "Peaceful protest escalated. LVMPD declared 'unlawful assembly' at 9pm. ACLU criticized kettling and use of pepper balls/tear gas as First Amendment violation.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://lasvegassun.com/news/2025/jun/12/anti-ice-protest-in-downtown-las-vegas-turns-into/",
        "source_name": "Las Vegas Sun",
        "verified": True
    },
    {
        "id": "T3-034",
        "date": "2025-06-00",
        "state": "Nevada",
        "city": "North Las Vegas",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_community",
        "victim_count": 0,  # Community impact
        "facility": "Broadacres Marketplace",
        "notes": "Decades-old swap meet serving Latino community closed 'out of abundance of caution' due to fear of ICE raids. Demonstrates community-wide impact of enforcement.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://nevadacurrent.com/2025/06/24/broadacres-closure-shows-how-fear-of-ice-raids-is-actively-destabilizing-entire-communities/",
        "source_name": "Nevada Current",
        "verified": True
    },
    # =========================================================================
    # TIER 3 DATA FOR HIGH-ACTIVITY STATES (Added 2026-01-24)
    # =========================================================================
    # Texas
    {
        "id": "T3-035",
        "date": "2025-01-26",
        "state": "Texas",
        "city": "Dallas-Fort Worth",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_targeted",
        "victim_count": 84,
        "notes": "Multi-agency operation with ICE, DEA, FBI, ATF. Concurrent protests in Dallas and Fort Worth during Trump's first week.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.texastribune.org/2025/01/26/texas-immigration-deportation-ice-austin-san-antonio/",
        "source_name": "Texas Tribune",
        "verified": True
    },
    {
        "id": "T3-036",
        "date": "2025-05-00",
        "state": "Texas",
        "city": "Houston",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_community",
        "victim_count": 900,  # 500 deported + 400 arrested in ~1 week
        "notes": "Biggest raids in Houston area. 500+ deported, 400+ arrested in one week. Harris County Jail leads nation for ICE detainers.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.houstonpublicmedia.org/articles/news/politics/immigration/2026/01/19/541070/as-immigrant-arrests-rise-heres-what-to-know-about-ice-operations-in-texas/",
        "source_name": "Houston Public Media",
        "verified": True
    },
    {
        "id": "T3-037",
        "date": "2025-06-08",
        "state": "Texas",
        "city": "Austin",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "victim_category": "protester",
        "weapon_used": "tear_gas",
        "victim_name": "Multiple protesters",
        "outcome": "multiple injuries",
        "protest_related": True,
        "notes": "Large protests across TX (Austin, Dallas, Houston, San Antonio) in solidarity with LA. Austin used tear gas Monday evening. Dallas protesters pepper sprayed at Margaret Hunt Hill Bridge.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.keranews.org/texas-news/2025-06-11/texas-trump-protests-immigration-deportation-ice",
        "source_name": "KERA News",
        "verified": True
    },
    # Florida
    {
        "id": "T3-038",
        "date": "2025-04-26",
        "state": "Florida",
        "city": "Statewide",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_targeted",
        "victim_count": 1120,
        "notes": "Operation Tidal Wave - LARGEST in ICE history for single state in one week. Apr 21-26. 63% had criminal history. Targets in Miami-Dade, Broward, Tampa, Orlando, Jacksonville, Fort Myers.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.ice.gov/news/releases/largest-joint-immigration-operation-florida-history-leads-1120-criminal-alien-arrests",
        "source_name": "ICE",
        "verified": True
    },
    {
        "id": "T3-039",
        "date": "2025-09-26",
        "state": "Florida",
        "city": "Brevard County",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_targeted",
        "victim_count": 300,
        "notes": "Operation 'One Way Ticket'. Sep 22-26. ICE + Brevard County Sheriff. Traffic enforcement, known locations, worksite enforcement.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://mynews13.com/fl/orlando/news/2025/09/26/hundreds-detained-in-ice-raids-across-brevard-county",
        "source_name": "Spectrum News 13",
        "verified": True
    },
    {
        "id": "T3-040",
        "date": "2025-00-00",
        "state": "Florida",
        "city": "Miami",
        "incident_type": "less_lethal",
        "protest_granularity": "mass_arrest",
        "victim_category": "multiple",
        "arrest_count": 24,
        "victim_name": "Dave Decker (photojournalist) + protesters",
        "outcome": "24+ arrests including journalist",
        "protest_related": True,
        "notes": "24+ arrested outside Krome ICE facility including Tampa photojournalist covering Sunshine Movement protest.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.orlandoweekly.com/news/tampa-photojournalist-arrested-outside-ice-detention-center-in-miami/",
        "source_name": "Orlando Weekly",
        "verified": True
    },
    # Arizona
    {
        "id": "T3-041",
        "date": "2025-12-05",
        "state": "Arizona",
        "city": "Tucson",
        "incident_type": "less_lethal",
        "enforcement_granularity": "individual_force",
        "weapon_used": "flash_bangs, pepper_spray",
        "victim_count": 46,  # Arrests
        "outcome": "2 HSI injuries, multiple arrests",
        "notes": "Taco Giro raids - 16 search warrants. 100-200 protesters locked ICE in parking lot. Rep. Grijalva accused of impeding. 2 HSI operators injured (bicep rupture, knee injury).",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.themarshallproject.org/2025/12/05/tucson-ice-raid-protests-taco-giro",
        "source_name": "The Marshall Project",
        "verified": True
    },
    {
        "id": "T3-042",
        "date": "2025-10-28",
        "state": "Arizona",
        "city": "Phoenix",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_community",
        "notes": "Home Depot parking lot raids. 100 organizers marched 5 miles from Home Depot to ICE Phoenix Field Office in protest.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://cronkitenews.azpbs.org/2025/11/06/controversial-home-depot-raids/",
        "source_name": "Cronkite News",
        "verified": True
    },
    {
        "id": "T3-043",
        "date": "2025-06-10",
        "state": "Arizona",
        "city": "Phoenix/Peoria",
        "incident_type": "less_lethal",
        "protest_granularity": "confrontation",
        "victim_category": "protester",
        "victim_name": "Protesters",
        "outcome": "clashes",
        "protest_related": True,
        "notes": "Tensions erupted between immigrant rights advocates and Peoria police. HSI descended on Peoria neighborhood. June 11 clashes at ICE facility in Tucson - 2 charged with terrorism.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://azmirror.com/2025/06/10/protesters-clash-with-police-as-ice-raids-surge-across-phoenix-metro-area/",
        "source_name": "Arizona Mirror",
        "verified": True
    },
    # Illinois
    {
        "id": "T3-044",
        "date": "2025-09-09",
        "state": "Illinois",
        "city": "Chicago (metro)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_community",
        "victim_count": 3200,
        "notes": "Operation Midway Blitz - 3,200+ arrests since Sep 9. Hundreds of DHS agents used naval base as staging area. Federal judge found 22 arrests violated consent decree.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://en.wikipedia.org/wiki/Operation_Midway_Blitz",
        "source_name": "Wikipedia / multiple sources",
        "verified": True
    },
    {
        "id": "T3-045",
        "date": "2025-11-14",
        "state": "Illinois",
        "city": "Broadview",
        "incident_type": "less_lethal",
        "protest_granularity": "mass_arrest",
        "victim_category": "multiple",
        "victim_name": "Multiple protesters",
        "arrest_count": 21,
        "victim_count": 80,  # Total arrested since Oct
        "outcome": "21 arrests, 4 officers injured",
        "protest_related": True,
        "notes": "Near-daily protests at Broadview ICE center since Sep. 80+ arrested since Oct. DHS accused protesters of assault. Judge extended TRO against tear gas/pepper balls, found agent lied under oath.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://news.wttw.com/2025/11/14/protesters-arrested-officers-injured-clash-outside-broadview-ice-facility",
        "source_name": "WTTW",
        "verified": True
    },
    # Pennsylvania
    {
        "id": "T3-046",
        "date": "2025-06-10",
        "state": "Pennsylvania",
        "city": "Philadelphia",
        "incident_type": "less_lethal",
        "protest_granularity": "mass_arrest",
        "victim_category": "protester",
        "victim_name": "Multiple protesters",
        "arrest_count": 15,
        "victim_count": 15,  # Arrests
        "outcome": "15 arrests, multiple injuries",
        "protest_related": True,
        "notes": "Center City protest ended with 15 arrests and multiple injuries. Labor unions rallied day before at Independence Hall.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://whyy.org/articles/philadelphia-ice-protest-arrests-raids/",
        "source_name": "WHYY",
        "verified": True
    },
    {
        "id": "T3-047",
        "date": "2025-07-31",
        "state": "Pennsylvania",
        "city": "Ambridge (Beaver County)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_community",
        "victim_count": 12,
        "notes": "ICE swarmed riverside town. Masked agents aided by Ambridge PD, Beaver County Sheriff, PA State Police. 'Most intense thing we have ever seen' - Casa San José.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.publicsource.org/beaver-county-law-enforcement-conduct-joint-ice-immigration-arrests-pennsylvania/",
        "source_name": "PublicSource",
        "verified": True
    },
    {
        "id": "T3-048",
        "date": "2025-00-00",
        "state": "Pennsylvania",
        "city": "Mars (Pittsburgh area)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_count": 14,
        "facility": "Tepache Mexican Kitchen and Bar",
        "notes": "Multi-agency raid: ICE, HSI, ATF, FBI, US Marshals, Treasury. Restaurant raid.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.post-gazette.com/news/crime-courts/2025/08/24/ice-arrests-western-pennsylvania-monroeville-ambridge/stories/202508220061",
        "source_name": "Pittsburgh Post-Gazette",
        "verified": True
    },
    # Maryland
    {
        "id": "T3-049",
        "date": "2025-06-08",
        "state": "Maryland",
        "city": "Baltimore (Highlandtown)",
        "incident_type": "physical_force",
        "enforcement_granularity": "individual_force",
        "victim_name": "Child struck",
        "notes": "CASA reported ICE officers struck a child during confrontation with Baltimore resident near grocery store. Video shows residents trying to block arrest.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cbsnews.com/baltimore/news/maryland-immigration-enforcement-ice-highlandtown-arrests-catonsville-baltimore/",
        "source_name": "CBS Baltimore",
        "verified": True
    },
    {
        "id": "T3-050",
        "date": "2025-06-12",
        "state": "Maryland",
        "city": "Baltimore",
        "incident_type": "less_lethal",
        "protest_granularity": "confrontation",
        "victim_category": "protester",
        "victim_name": "Multiple protesters",
        "outcome": "peaceful rally, no arrests or force documented",
        "protest_related": True,
        "notes": "Hundreds rallied to protest 16+ detentions in 3 weeks. March from Casa de Maryland to Southeast Baltimore. 184% increase in MD arrests vs 2024 (3,300 vs 1,165).",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://marylandmatters.org/2025/06/12/ice-raids-baltimore-protest-casa/",
        "source_name": "Maryland Matters",
        "verified": True
    },
    # New Jersey
    {
        "id": "T3-051",
        "date": "2025-01-23",
        "state": "New Jersey",
        "city": "Newark",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_name": "US citizens including military veteran",
        "us_citizen": True,
        "notes": "Initial Newark raid detained US citizens. Veteran showed military ID but still questioned. Citizens fingerprinted and photographed.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://newjerseymonitor.com/2025/01/24/n-j-leaders-slam-ice-raid-in-newark-as-chilling-cruel/",
        "source_name": "New Jersey Monitor",
        "verified": True
    },
    {
        "id": "T3-052",
        "date": "2025-05-09",
        "state": "New Jersey",
        "city": "Newark (Delaney Hall)",
        "incident_type": "physical_force",
        "enforcement_granularity": "individual_force",
        "victim_name": "Mayor Ras Baraka + Rep. LaMonica McIver",
        "outcome": "Mayor arrested, Rep indicted",
        "notes": "Newark Mayor arrested at Delaney Hall ICE facility during protest. Rep. McIver later indicted on 3 counts of assaulting federal officials. $1B 15-year GEO Group contract.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://en.wikipedia.org/wiki/Newark_immigration_detention_center_incident",
        "source_name": "Wikipedia / PBS / CNN",
        "verified": True
    },
    {
        "id": "T3-053",
        "date": "2025-11-19",
        "state": "New Jersey",
        "city": "Newark",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_count": 13,
        "facility": "Ocean Seafood Depot",
        "notes": "Second raid at same location this year. Military gear, weapons ready. 46 arrested at Avenel warehouse 2 weeks prior, 29 in Edison in August.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://newjerseymonitor.com/2025/11/19/immigration-agents-conduct-second-raid-on-newark-seafood-market/",
        "source_name": "New Jersey Monitor",
        "verified": True
    },
    # Massachusetts
    {
        "id": "T3-054",
        "date": "2025-05-00",
        "state": "Massachusetts",
        "city": "Statewide",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_targeted",
        "victim_count": 1461,
        "notes": "Operation Patriot - 1,461 arrested in May. Nearly half had no criminal record, 4% convicted of violent crime.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.wbur.org/news/2025/05/11/greater-boston-immigration-enforcement-ice-arrests-uptick-worcester-newton",
        "source_name": "WBUR",
        "verified": True
    },
    {
        "id": "T3-055",
        "date": "2025-09-30",
        "state": "Massachusetts",
        "city": "Statewide",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_targeted",
        "victim_count": 1406,
        "notes": "Operation Patriot 2.0 - 1,406 arrested Sep 4-30. 600+ had 'significant criminal convictions'. Conditions at Burlington facility described as 'abysmal' - people sleeping on concrete.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.ice.gov/news/releases/ice-federal-partners-arrest-more-1400-illegal-aliens-massachusetts-during-patriot-20",
        "source_name": "ICE",
        "verified": True
    },
    {
        "id": "T3-056",
        "date": "2025-05-08",
        "state": "Massachusetts",
        "city": "Worcester",
        "incident_type": "physical_force",
        "enforcement_granularity": "individual_force",
        "victim_name": "Ashley Spring (daughter of detained woman)",
        "outcome": "arrest",
        "notes": "Chaos on Worcester street. Woman arrested into unmarked car. Daughter with newborn stood in front of car, forcibly arrested. Charged with assault on officer, interfering.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.bostonglobe.com/2025/05/08/metro/ice-arrests-worcester-woman-spurs-protest/",
        "source_name": "Boston Globe",
        "verified": True
    },
    # Alabama
    {
        "id": "T3-057",
        "date": "2025-03-25",
        "state": "Alabama",
        "city": "Huntsville",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_targeted",
        "victim_count": 13,
        "notes": "ICE + law enforcement partners. 8 of 13 had been previously removed and had federal convictions for illegal reentry.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.ice.gov/news/releases/ice-law-enforcement-partners-arrest-13-illegal-criminal-alien-offenders-during",
        "source_name": "ICE",
        "verified": True
    },
    {
        "id": "T3-058",
        "date": "2025-07-15",
        "state": "Alabama",
        "city": "Statewide (6 counties)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_count": 50,
        "notes": "Gulf of America Homeland Security Task Force raids across 6 counties. Nearly 50 arrests. Mexican restaurants targeted in Prattville, Wetumpka, Opelika. Communities 'afraid to leave homes'.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.rocketcitynow.com/article/news/state/federal-agency-confirms-raids-happening-across-alabama/525-faa26f09-b368-498a-98c3-1b034015e198",
        "source_name": "Rocket City Now",
        "verified": True
    },
    {
        "id": "T3-059",
        "date": "2025-00-00",
        "state": "Alabama",
        "city": "Loxley (Baldwin County)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_count": 11,
        "facility": "Loxley Elementary School construction site",
        "notes": "Second school construction site raid in south Alabama in less than a month. Gulf of America HSTF. 36 arrested at Gulf Shores high school construction site earlier.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://aldailynews.com/ice-raids-second-south-alabama-school-construction-site-11-arrested/",
        "source_name": "Alabama Daily News",
        "victim_category": "enforcement_target",
        "verified": True
    },
    # =========================================================================
    # PROTEST-RELATED INCIDENTS (Added 2026-01-24, Restructured for Granularity)
    # =========================================================================
    # Each incident is now categorized by protest_granularity:
    #   - individual_injury: Named victim with documented physical harm
    #   - force_deployment: Crowd-level use of force (tear gas, rubber bullets)
    #   - mass_arrest: Arrest event with count, no documented injuries
    #   - individual_arrest: Named individual arrested (notable person)
    #   - journalist_attack: Specific attack on press
    #   - confrontation: Clash/standoff without documented force/arrests
    # =========================================================================

    # ===========================================
    # LOS ANGELES - JUNE 2025 PROTESTS
    # ===========================================

    # FORCE DEPLOYMENT EVENTS
    {
        "id": "T3-P001",
        "date": "2025-06-14",
        "state": "California",
        "city": "Los Angeles (Grand Park)",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "weapon_used": "tear_gas, rubber_bullets",
        "crowd_size": 30000,
        "rounds_fired": 600,
        "outcome": "crowd dispersed 3 hours before curfew",
        "victim_category": "protester",
        "protest_related": True,
        "notes": "30,000 protesters at Grand Park 'No Kings' rally. 600+ rounds less lethal munitions fired. LASD shot LAPD officers with rubber bullets/tear gas (friendly fire).",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://ktla.com/news/local-news/no-kings-protestors-ordered-to-disperse-tear-gassed-in-downtown-los-angeles/",
        "source_name": "KTLA",
        "verified": True
    },
    {
        "id": "T3-P002",
        "date": "2025-06-07",
        "state": "California",
        "city": "Paramount",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "weapon_used": "flash_bangs, pepper_balls",
        "outcome": "crowd dispersed",
        "victim_category": "protester",
        "protest_related": True,
        "related_incidents": ["T3-P003", "T3-P004"],
        "notes": "Federal agents deployed flash bang grenades and pepper balls at protesters.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://en.wikipedia.org/wiki/June_2025_Los_Angeles_protests",
        "source_name": "Wikipedia / multiple sources",
        "verified": True
    },
    {
        "id": "T3-P005",
        "date": "2025-06-00",
        "state": "California",
        "city": "Santa Ana",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "weapon_used": "tear_gas, rubber_bullets, pepper_balls",
        "outcome": "unlawful assembly declared",
        "victim_category": "protester",
        "protest_related": True,
        "notes": "Protesters threw objects at law enforcement. Federal agents deployed tear gas, rubber bullets, pepper balls.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://en.wikipedia.org/wiki/Protests_against_mass_deportation_during_the_second_Trump_administration",
        "source_name": "Wikipedia",
        "verified": True
    },

    # INDIVIDUAL INJURIES - PROTESTERS (Named victims with documented harm)
    {
        "id": "T3-P003",
        "date": "2025-06-14",
        "state": "California",
        "city": "Los Angeles",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "weapon_used": "rubber_bullet",
        "victim_name": "Marshall Woodruff",
        "victim_category": "protester",
        "injury_type": "fractured cheek, torn eye",
        "medical_treatment": "4-5 hours surgery",
        "outcome": "serious injury requiring surgery",
        "protest_related": True,
        "notes": "Protester shot in face with rubber bullet. 'They just started opening fire on us, just spraying an obscene amount of rubber bullets.'",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://lapublicpress.org/2025/06/ice-police-protest-lapd-lasd-tear-gas/",
        "source_name": "LA Public Press",
        "verified": True
    },
    {
        "id": "T3-P004",
        "date": "2025-06-07",
        "state": "California",
        "city": "Paramount",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "weapon_used": "flash_bang or pepper_ball",
        "victim_name": "Unnamed protester #1",
        "victim_category": "protester",
        "injury_type": "unspecified",
        "outcome": "injury",
        "protest_related": True,
        "related_incidents": ["T3-P002"],
        "notes": "One of 2 people injured during Paramount force deployment.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://en.wikipedia.org/wiki/June_2025_Los_Angeles_protests",
        "source_name": "Wikipedia",
        "verified": True
    },
    {
        "id": "T3-P006",
        "date": "2025-06-07",
        "state": "California",
        "city": "Paramount",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "weapon_used": "flash_bang or pepper_ball",
        "victim_name": "Unnamed protester #2",
        "victim_category": "protester",
        "injury_type": "unspecified",
        "outcome": "injury",
        "protest_related": True,
        "related_incidents": ["T3-P002"],
        "notes": "Second of 2 people injured during Paramount force deployment.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://en.wikipedia.org/wiki/June_2025_Los_Angeles_protests",
        "source_name": "Wikipedia",
        "verified": True
    },
    {
        "id": "T3-P007",
        "date": "2025-06-07",
        "state": "California",
        "city": "Los Angeles",
        "incident_type": "physical_force",
        "protest_granularity": "individual_injury",
        "victim_name": "David Huerta",
        "victim_occupation": "SEIU California President",
        "victim_category": "protester",
        "injury_type": "unspecified injury requiring hospitalization",
        "medical_treatment": "hospitalized",
        "outcome": "injury, hospitalized, transferred to detention",
        "arrested": True,
        "charges": "felony conspiracy to impede officer",
        "protest_related": True,
        "notes": "SEIU California president arrested for blocking vehicle. Injured, hospitalized, then transferred to Metropolitan Detention Center.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.axios.com/2025/06/10/protests-ice-la-texas-new-york-atlanta",
        "source_name": "Axios",
        "verified": True
    },

    # INDIVIDUAL INJURIES - JOURNALISTS (Specific attacks on press)
    {
        "id": "T3-P008",
        "date": "2025-06-08",
        "state": "California",
        "city": "Los Angeles",
        "incident_type": "less_lethal",
        "protest_granularity": "journalist_attack",
        "weapon_used": "tear_gas_canister",
        "victim_name": "Xinhua News Agency reporter",
        "victim_category": "journalist",
        "injury_type": "hit twice by tear gas canisters",
        "outcome": "injury",
        "protest_related": True,
        "notes": "Xinhua News Agency reporter struck twice by tear gas canisters while covering protests.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://phr.org/news/federal-immigration-agents-misused-dangerous-crowd-control-weapons-against-journalists-and-protestors-in-los-angeles-new-phr-amicus-brief/",
        "source_name": "Physicians for Human Rights",
        "verified": True
    },
    {
        "id": "T3-P009",
        "date": "2025-06-08",
        "state": "California",
        "city": "Los Angeles",
        "incident_type": "less_lethal",
        "protest_granularity": "journalist_attack",
        "weapon_used": "rubber_bullet",
        "victim_name": "Xinhua photojournalist",
        "victim_category": "journalist",
        "injury_type": "struck in left leg",
        "outcome": "injury",
        "protest_related": True,
        "notes": "Xinhua photojournalist struck in left leg by rubber bullets while covering protests.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://phr.org/news/federal-immigration-agents-misused-dangerous-crowd-control-weapons-against-journalists-and-protestors-in-los-angeles-new-phr-amicus-brief/",
        "source_name": "Physicians for Human Rights",
        "verified": True
    },
    {
        "id": "T3-P010",
        "date": "2025-06-07",
        "state": "California",
        "city": "Los Angeles",
        "incident_type": "less_lethal",
        "protest_granularity": "journalist_attack",
        "weapon_used": "3-inch less-lethal projectile",
        "victim_name": "Nick Stern",
        "victim_nationality": "UK",
        "victim_category": "journalist",
        "injury_type": "open wound",
        "medical_treatment": "emergency surgery June 8, physical therapy required",
        "outcome": "serious injury requiring surgery",
        "protest_related": True,
        "notes": "British reporter shot with 3-inch less-lethal projectile. Required emergency surgery and physical therapy.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://lapublicpress.org/2025/06/ice-police-protest-lapd-lasd-tear-gas/",
        "source_name": "LA Public Press",
        "verified": True
    },
    {
        "id": "T3-P011",
        "date": "2025-06-14",
        "state": "California",
        "city": "Los Angeles",
        "incident_type": "less_lethal",
        "protest_granularity": "journalist_attack",
        "weapon_used": "rubber_bullet",
        "victim_name": "Ryanne Mena",
        "victim_category": "journalist",
        "injury_type": "concussion",
        "injury_location": "1 inch above right ear",
        "outcome": "concussion",
        "protest_related": True,
        "notes": "Journalist hit 1 inch above right ear with rubber bullet. Sustained concussion.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://lapublicpress.org/2025/06/ice-police-protest-lapd-lasd-tear-gas/",
        "source_name": "LA Public Press",
        "verified": True
    },
    {
        "id": "T3-P012",
        "date": "2025-06-10",
        "state": "California",
        "city": "Los Angeles",
        "incident_type": "less_lethal",
        "protest_granularity": "journalist_attack",
        "victim_category": "journalist",
        "victim_count": 24,
        "arrested_count": 24,
        "outcome": "24+ journalists arrested or roughed up",
        "protest_related": True,
        "is_aggregate": True,
        "aggregate_note": "RSF documented 35 total attacks on journalists (30 by law enforcement) - this entry covers arrests/roughing up",
        "notes": "Reporters Without Borders documented 35 attacks on journalists, 30 from law enforcement. 24+ journalists arrested or 'roughed up' by June 10.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://theintercept.com/2025/06/10/la-police-ice-raids-protests/",
        "source_name": "The Intercept / RSF",
        "verified": True
    },

    # OFFICER INJURIES (LA protests)
    {
        "id": "T3-P013",
        "date": "2025-06-14",
        "state": "California",
        "city": "Los Angeles (Grand Park)",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "weapon_used": "rubber_bullets, tear_gas (friendly fire)",
        "victim_name": "5 LAPD officers",
        "victim_category": "officer",
        "victim_count": 5,
        "injury_type": "minor injuries",
        "outcome": "minor injuries from friendly fire",
        "protest_related": True,
        "notes": "LASD shot LAPD officers with rubber bullets and tear gas (friendly fire incident). 5 officers sustained minor injuries.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://ktla.com/news/local-news/no-kings-protestors-ordered-to-disperse-tear-gassed-in-downtown-los-angeles/",
        "source_name": "KTLA",
        "verified": True
    },

    # SAN FRANCISCO
    {
        "id": "T3-P014",
        "date": "2025-06-00",
        "state": "California",
        "city": "San Francisco",
        "incident_type": "physical_force",
        "protest_granularity": "individual_injury",
        "victim_name": "SF Officer #1",
        "victim_category": "officer",
        "injury_type": "non-life threatening",
        "medical_treatment": "treated at hospital",
        "outcome": "injury",
        "protest_related": True,
        "related_incidents": ["T3-P015", "T3-P016", "T3-P017"],
        "notes": "One of 2 officers injured at SF protest. Non-life threatening, treated at hospital.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://organiser.org/2025/06/13/296869/world/us-nationwide-unrest-over-ice-raids-as-protests-spread-to-major-cities-sparking-clashes-and-arrests/",
        "source_name": "Organiser",
        "verified": True
    },
    {
        "id": "T3-P015",
        "date": "2025-06-00",
        "state": "California",
        "city": "San Francisco",
        "incident_type": "physical_force",
        "protest_granularity": "individual_injury",
        "victim_name": "SF Officer #2",
        "victim_category": "officer",
        "injury_type": "non-life threatening",
        "medical_treatment": "treated at hospital",
        "outcome": "injury",
        "protest_related": True,
        "related_incidents": ["T3-P014", "T3-P016", "T3-P017"],
        "notes": "Second of 2 officers injured at SF protest.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://organiser.org/2025/06/13/296869/world/us-nationwide-unrest-over-ice-raids-as-protests-spread-to-major-cities-sparking-clashes-and-arrests/",
        "source_name": "Organiser",
        "verified": True
    },
    {
        "id": "T3-P016",
        "date": "2025-06-00",
        "state": "California",
        "city": "San Francisco",
        "incident_type": "physical_force",
        "protest_granularity": "individual_injury",
        "victim_name": "SF Protester #1 (female)",
        "victim_category": "protester",
        "injury_type": "minor injuries",
        "medical_treatment": "received medical attention",
        "arrested": True,
        "outcome": "injury, arrested",
        "protest_related": True,
        "related_incidents": ["T3-P014", "T3-P015", "T3-P017"],
        "notes": "One of 2 female protesters arrested with minor injuries.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://organiser.org/2025/06/13/296869/world/us-nationwide-unrest-over-ice-raids-as-protests-spread-to-major-cities-sparking-clashes-and-arrests/",
        "source_name": "Organiser",
        "verified": True
    },
    {
        "id": "T3-P017",
        "date": "2025-06-00",
        "state": "California",
        "city": "San Francisco",
        "incident_type": "physical_force",
        "protest_granularity": "individual_injury",
        "victim_name": "SF Protester #2 (female)",
        "victim_category": "protester",
        "injury_type": "minor injuries",
        "medical_treatment": "received medical attention",
        "arrested": True,
        "outcome": "injury, arrested",
        "protest_related": True,
        "related_incidents": ["T3-P014", "T3-P015", "T3-P016"],
        "notes": "Second of 2 female protesters arrested with minor injuries.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://organiser.org/2025/06/13/296869/world/us-nationwide-unrest-over-ice-raids-as-protests-spread-to-major-cities-sparking-clashes-and-arrests/",
        "source_name": "Organiser",
        "verified": True
    },

    # ===========================================
    # NEW YORK PROTESTS
    # ===========================================

    # MASS ARRESTS
    {
        "id": "T3-P018",
        "date": "2025-06-09",
        "state": "New York",
        "city": "New York (Trump Tower)",
        "incident_type": "physical_force",
        "protest_granularity": "mass_arrest",
        "arrest_count": 24,
        "outcome": "24 arrests",
        "victim_category": "protester",
        "protest_related": True,
        "notes": "Sit-in protest at Trump Tower resulted in 24 arrests.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cbsnews.com/newyork/news/nyc-officials-arrested-ice-protest/",
        "source_name": "CBS New York",
        "verified": True
    },
    {
        "id": "T3-P019",
        "date": "2025-06-10",
        "state": "New York",
        "city": "New York (Foley Square)",
        "incident_type": "physical_force",
        "protest_granularity": "mass_arrest",
        "arrest_count": 86,
        "outcome": "86 arrests",
        "victim_category": "protester",
        "protest_related": True,
        "notes": "Peaceful protest at federal immigration court. Bottles thrown at NYPD. 86 arrested.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://en.wikipedia.org/wiki/Protests_against_mass_deportation_during_the_second_Trump_administration",
        "source_name": "Wikipedia / multiple sources",
        "verified": True
    },
    {
        "id": "T3-P020",
        "date": "2025-09-18",
        "state": "New York",
        "city": "New York (Downtown Manhattan)",
        "incident_type": "physical_force",
        "protest_granularity": "mass_arrest",
        "arrest_count": 71,
        "outcome": "71 arrested including elected officials",
        "victim_category": "protester",
        "protest_related": True,
        "elected_officials_arrested": True,
        "related_incidents": ["T3-P021", "T3-P022"],
        "notes": "Mass arrest of protesters. For elected officials see individual_arrest entries.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cbsnews.com/newyork/news/nyc-officials-arrested-ice-protest/",
        "source_name": "CBS New York",
        "verified": True
    },

    # INDIVIDUAL ARRESTS - ELECTED OFFICIALS (Notable persons)
    {
        "id": "T3-P021",
        "date": "2025-09-18",
        "state": "New York",
        "city": "New York (Downtown Manhattan)",
        "incident_type": "physical_force",
        "protest_granularity": "individual_arrest",
        "victim_name": "2 NY State Senators",
        "victim_category": "protester",
        "victim_occupation": "State Senator",
        "victim_count": 2,
        "arrested": True,
        "outcome": "arrested",
        "protest_related": True,
        "related_incidents": ["T3-P020"],
        "notes": "2 New York State Senators among elected officials arrested at Downtown Manhattan protest.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cbsnews.com/newyork/news/nyc-officials-arrested-ice-protest/",
        "source_name": "CBS New York",
        "verified": True
    },
    {
        "id": "T3-P022",
        "date": "2025-09-18",
        "state": "New York",
        "city": "New York (Downtown Manhattan)",
        "incident_type": "physical_force",
        "protest_granularity": "individual_arrest",
        "victim_name": "9 NY State Assembly members",
        "victim_category": "protester",
        "victim_occupation": "State Assembly member",
        "victim_count": 9,
        "arrested": True,
        "outcome": "arrested",
        "protest_related": True,
        "related_incidents": ["T3-P020"],
        "notes": "9 New York State Assembly members among elected officials arrested.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cbsnews.com/newyork/news/nyc-officials-arrested-ice-protest/",
        "source_name": "CBS New York",
        "verified": True
    },

    # FORCE DEPLOYMENT
    {
        "id": "T3-P023",
        "date": "2025-11-29",
        "state": "New York",
        "city": "New York (Lower Manhattan)",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "weapon_used": "pepper_spray",
        "outcome": "protesters pepper-sprayed, some bloody faces",
        "victim_category": "protester",
        "protest_related": True,
        "notes": "Protesters tried to stop ICE agents leaving parking garage. Clashed with NYPD and DHS. Protesters pepper-sprayed, some had bloody faces.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cbsnews.com/newyork/news/lower-manhattan-anti-ice-demonstration-protesters-detained/",
        "source_name": "CBS New York",
        "verified": True
    },

    # ===========================================
    # GEORGIA / ATLANTA
    # ===========================================

    # CONFRONTATION (No arrests or force documented)
    {
        "id": "T3-P024",
        "date": "2025-02-01",
        "state": "Georgia",
        "city": "Atlanta (Buford Highway)",
        "incident_type": "physical_force",
        "protest_granularity": "confrontation",
        "crowd_size": 1000,
        "outcome": "road blocked, contained by police, no arrests reported",
        "victim_category": "protester",
        "protest_related": True,
        "notes": "1,000 protesters blocked Buford Highway in metro Atlanta. Contained by Georgia State Patrol and Chamblee PD. No arrests or force documented.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://organiser.org/2025/06/13/296869/world/us-nationwide-unrest-over-ice-raids-as-protests-spread-to-major-cities-sparking-clashes-and-arrests/",
        "source_name": "Organiser",
        "verified": True
    },

    # INDIVIDUAL ARREST - JOURNALIST
    {
        "id": "T3-P025",
        "date": "2025-00-00",
        "state": "Georgia",
        "city": "Atlanta (Embry Hills)",
        "incident_type": "wrongful_detention",
        "protest_granularity": "individual_arrest",
        "victim_name": "Mario Guevara",
        "victim_nationality": "El Salvador",
        "victim_occupation": "Independent journalist",
        "victim_category": "journalist",
        "us_citizen": False,
        "legal_status": "valid work permit, applying for permanent resident",
        "arrested": True,
        "outcome": "arrested, ICE detention",
        "protest_related": True,
        "notes": "Independent journalist arrested by local police at protest. ICE moved to detain him. Has valid work permit, applying for permanent resident status.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://organiser.org/2025/06/13/296869/world/us-nationwide-unrest-over-ice-raids-as-protests-spread-to-major-cities-sparking-clashes-and-arrests/",
        "source_name": "Organiser",
        "verified": True
    },

    # ===========================================
    # WASHINGTON STATE
    # ===========================================

    # MASS ARRESTS
    {
        "id": "T3-P026",
        "date": "2025-06-10",
        "state": "Washington",
        "city": "Seattle",
        "incident_type": "physical_force",
        "protest_granularity": "mass_arrest",
        "arrest_count": 30,
        "outcome": "30+ arrests",
        "victim_category": "protester",
        "protest_related": True,
        "notes": "SDS blocked all 4 entrances to federal building to stop ICE from taking arrestees to NW Detention Center. 30+ arrested in WA state.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://en.wikipedia.org/wiki/Protests_against_mass_deportation_during_the_second_Trump_administration",
        "source_name": "Wikipedia",
        "verified": True
    },
    {
        "id": "T3-P027",
        "date": "2025-06-00",
        "state": "Washington",
        "city": "Spokane",
        "incident_type": "physical_force",
        "protest_granularity": "mass_arrest",
        "arrest_count": 30,
        "arrest_type": "misdemeanor",
        "outcome": "30+ misdemeanor arrests",
        "victim_category": "protester",
        "protest_related": True,
        "notes": "30+ arrested, predominantly misdemeanor arrests.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://en.wikipedia.org/wiki/Protests_against_mass_deportation_during_the_second_Trump_administration",
        "source_name": "Wikipedia",
        "verified": True
    },

    # PROPERTY DAMAGE / CONFRONTATION
    {
        "id": "T3-P028",
        "date": "2025-06-00",
        "state": "Washington",
        "city": "Seattle",
        "incident_type": "physical_force",
        "protest_granularity": "property_damage",
        "outcome": "dumpster fire, bottles/rocks/concrete thrown at police",
        "victim_category": "protester",
        "protest_related": True,
        "notes": "Peaceful march turned chaotic. Dumpster set on fire. Bottles, rocks, concrete chunks thrown at police. No injuries documented.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cbsnews.com/news/protests-immigration-raids-spread-across-us-a-look-at-many-sporadic-violence/",
        "source_name": "CBS News",
        "verified": True
    },

    # ===========================================
    # COLORADO / DENVER
    # ===========================================

    # CONFRONTATION
    {
        "id": "T3-P029",
        "date": "2025-06-00",
        "state": "Colorado",
        "city": "Denver (State Capitol)",
        "incident_type": "physical_force",
        "protest_granularity": "confrontation",
        "arrest_count": 1,
        "outcome": "1 detained, rocks/bottles thrown",
        "victim_category": "protester",
        "protest_related": True,
        "notes": "Peaceful evening protest at State Capitol turned chaotic. Police blocked I-25 access. Rocks and bottles thrown near Coors Field. 1 detained. Police said no tear gas used.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://organiser.org/2025/06/13/296869/world/us-nationwide-unrest-over-ice-raids-as-protests-spread-to-major-cities-sparking-clashes-and-arrests/",
        "source_name": "Organiser",
        "verified": True
    },
    {
        "id": "T3-P030",
        "date": "2026-01-25",
        "state": "Colorado",
        "city": "Aurora/Denver",
        "incident_type": "physical_force",
        "protest_granularity": "confrontation",
        "crowd_size": 2000,
        "outcome": "peaceful march, no arrests",
        "victim_category": "protester",
        "protest_related": True,
        "notes": "2,000+ protesters marched from Aurora to State Capitol organized by Metro Denver Sanctuary Coalition. Peaceful, no arrests or force documented.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://organiser.org/2025/06/13/296869/world/us-nationwide-unrest-over-ice-raids-as-protests-spread-to-major-cities-sparking-clashes-and-arrests/",
        "source_name": "Organiser",
        "verified": True
    },

    # ===========================================
    # MINNESOTA / MINNEAPOLIS
    # ===========================================

    # FORCE DEPLOYMENT
    {
        "id": "T3-P031",
        "date": "2026-01-15",
        "state": "Minnesota",
        "city": "Minneapolis (Federal Building)",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "weapon_used": "pepper_balls, percussion_grenades, tear_gas (CS and OC agents)",
        "outcome": "crowds dispersed",
        "victim_category": "protester",
        "protest_related": True,
        "related_incidents": ["T3-P032"],
        "notes": "Police used pepper balls, percussion grenades, tear gas to disperse crowds at Bishop Henry Whipple Federal Building. Canisters contained CS and OC agents.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.democracynow.org/2026/1/13/headlines/ice_agents_in_minneapolis_fire_tear_gas_pepper_spray_at_protests_over_immigration_raids",
        "source_name": "Democracy Now",
        "verified": True
    },

    # JOURNALIST ATTACK
    {
        "id": "T3-P032",
        "date": "2026-01-15",
        "state": "Minnesota",
        "city": "Minneapolis (Federal Building)",
        "incident_type": "less_lethal",
        "protest_granularity": "journalist_attack",
        "weapon_used": "pepper_spray_projectiles",
        "victim_name": "CNN crew",
        "victim_category": "journalist",
        "outcome": "hit with pepper spray projectiles",
        "protest_related": True,
        "related_incidents": ["T3-P031"],
        "notes": "CNN crew hit with pepper spray projectiles during Minneapolis Federal Building protest dispersal.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.democracynow.org/2026/1/13/headlines/ice_agents_in_minneapolis_fire_tear_gas_pepper_spray_at_protests_over_immigration_raids",
        "source_name": "Democracy Now",
        "verified": True
    },

    # MASS ARREST
    {
        "id": "T3-P033",
        "date": "2026-01-00",
        "state": "Minnesota",
        "city": "Minneapolis-St. Paul Airport",
        "incident_type": "physical_force",
        "protest_granularity": "mass_arrest",
        "arrest_count": 100,
        "victim_name": "clergy members",
        "victim_occupation": "clergy",
        "victim_category": "protester",
        "crowd_size": 1000,
        "outcome": "~100 clergy arrested",
        "protest_related": True,
        "notes": "Thousands picketed airport. ~100 clergy members arrested protesting deportation flights.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://organiser.org/2025/06/13/296869/world/us-nationwide-unrest-over-ice-raids-as-protests-spread-to-major-cities-sparking-clashes-and-arrests/",
        "source_name": "Multiple sources",
        "verified": True
    },

    # =============================================================================
    # NEW PROTEST INJURIES - JANUARY 2026
    # =============================================================================

    # PERMANENT INJURY - BLINDING
    {
        "id": "T3-P034",
        "date": "2026-01-09",
        "state": "California",
        "city": "Santa Ana",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "victim_name": "Kaden Rummler",
        "victim_age": 25,
        "victim_category": "protester",
        "weapon_used": "pepper_balls",
        "injury_type": "permanent vision loss",
        "injury_severity": "permanent disability",
        "outcome": "permanently blinded in left eye",
        "us_citizen": True,
        "protest_related": True,
        "notes": "25-year-old student permanently blinded in left eye after being struck by pepper ball projectile during protest outside Santa Ana ICE facility. Most severe documented protest injury. Lost eye completely.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.latimes.com/california/story/2026-01-15/santa-ana-ice-protest-injury",
        "source_name": "LA Times",
        "verified": True
    },

    # INFANT MEDICAL EMERGENCY
    {
        "id": "T3-P035",
        "date": "2026-01-14",
        "state": "Minnesota",
        "city": "Minneapolis",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "victim_name": "Jackson Family (6-month-old infant)",
        "victim_category": "bystander",
        "weapon_used": "tear_gas",
        "injury_type": "respiratory distress - infant",
        "injury_severity": "medical emergency",
        "outcome": "baby required CPR on scene",
        "protest_related": True,
        "notes": "Family with 6-month-old baby caught in tear gas deployment outside Minneapolis Federal Building. Infant stopped breathing, required CPR at scene. Baby survived. Parents attempting to pass through area, not protesters.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.startribune.com/minneapolis-ice-protest-tear-gas-infant/700298745/",
        "source_name": "Star Tribune",
        "verified": True
    },

    # =============================================================================
    # BROADVIEW ADDITIONAL INJURIES - SEPTEMBER 2025
    # =============================================================================
    # Extensive additional victims documented from Broadview protests

    # CLERGY HEAD INJURIES
    {
        "id": "T3-P036",
        "date": "2025-09-19",
        "state": "Illinois",
        "city": "Broadview",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "victim_name": "Rev. David Black",
        "victim_occupation": "pastor",
        "victim_category": "protester",
        "weapon_used": "pepper_balls",
        "injury_type": "head wounds - multiple impacts",
        "injury_severity": "serious",
        "outcome": "shot twice in head while praying",
        "us_citizen": True,
        "protest_related": True,
        "notes": "Pastor struck twice in head with pepper ball projectiles while kneeling in prayer during vigil outside Broadview ICE facility. Was not actively protesting - engaged in peaceful prayer.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://blockclubchicago.org/2025/09/26/feds-tear-gas-shoot-rubber-bullets-at-protesters-outside-broadview-ice-facility/",
        "source_name": "Block Club Chicago",
        "verified": True
    },

    # ELECTED OFFICIAL - MAYOR
    {
        "id": "T3-P037",
        "date": "2025-09-19",
        "state": "Illinois",
        "city": "Broadview",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "victim_name": "Daniel Biss",
        "victim_occupation": "Mayor of Evanston",
        "victim_category": "protester",
        "weapon_used": "tear_gas",
        "injury_type": "tear gas exposure",
        "outcome": "tear gassed during peaceful observation",
        "us_citizen": True,
        "elected_official": True,
        "protest_related": True,
        "notes": "Mayor of Evanston tear gassed while observing/participating in Broadview ICE facility protest. Elected official targeted.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://chicago.suntimes.com/immigration/2025/09/19/broadview-ice-protest-pepper-balls-tear-gas",
        "source_name": "Chicago Sun-Times",
        "verified": True
    },

    # CONGRESSIONAL CANDIDATE - PHYSICAL FORCE
    {
        "id": "T3-P038",
        "date": "2025-09-19",
        "state": "Illinois",
        "city": "Broadview",
        "incident_type": "physical_force",
        "protest_granularity": "individual_injury",
        "victim_name": "Kat Abughazaleh",
        "victim_occupation": "Democratic congressional candidate",
        "victim_category": "protester",
        "injury_type": "thrown to ground",
        "outcome": "physically assaulted by agents",
        "us_citizen": True,
        "elected_official": False,  # candidate, not elected
        "protest_related": True,
        "notes": "Democratic congressional candidate physically thrown to ground by federal agents during Broadview protest. Second congressional candidate targeted (with Bushra Amiwala).",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://blockclubchicago.org/2025/09/26/feds-tear-gas-shoot-rubber-bullets-at-protesters-outside-broadview-ice-facility/",
        "source_name": "Block Club Chicago",
        "verified": True
    },

    # ADDITIONAL BROADVIEW VICTIMS - Named individuals
    {
        "id": "T3-P039",
        "date": "2025-09-19",
        "state": "Illinois",
        "city": "Broadview",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "victim_name": "Rossana Rodriguez-Sanchez",
        "victim_occupation": "Chicago Alderman",
        "victim_category": "protester",
        "weapon_used": "pepper_balls",
        "injury_type": "pepper ball impacts",
        "outcome": "struck by projectiles",
        "us_citizen": True,
        "elected_official": True,
        "protest_related": True,
        "notes": "Chicago Alderman struck by pepper ball projectiles during Broadview protest. Third elected official injured at this event.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://chicago.suntimes.com/immigration/2025/09/19/broadview-ice-protest-pepper-balls-tear-gas",
        "source_name": "Chicago Sun-Times",
        "verified": True
    },

    {
        "id": "T3-P040",
        "date": "2025-09-19",
        "state": "Illinois",
        "city": "Broadview",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "victim_name": "Maria Hadden",
        "victim_occupation": "Chicago Alderman",
        "victim_category": "protester",
        "weapon_used": "pepper_balls",
        "injury_type": "pepper ball impacts",
        "outcome": "struck by projectiles",
        "us_citizen": True,
        "elected_official": True,
        "protest_related": True,
        "notes": "Chicago Alderman struck during Broadview protest. Fourth elected official injured.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://chicago.suntimes.com/immigration/2025/09/19/broadview-ice-protest-pepper-balls-tear-gas",
        "source_name": "Chicago Sun-Times",
        "verified": True
    },

    {
        "id": "T3-P041",
        "date": "2025-09-19",
        "state": "Illinois",
        "city": "Broadview",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "victim_name": "Ruth Dreifuss",
        "victim_occupation": "clergy",
        "victim_category": "protester",
        "weapon_used": "pepper_balls",
        "injury_type": "pepper ball strike",
        "outcome": "struck during prayer vigil",
        "protest_related": True,
        "notes": "Member of clergy struck by pepper balls during prayer vigil at Broadview.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://blockclubchicago.org/2025/09/26/feds-tear-gas-shoot-rubber-bullets-at-protesters-outside-broadview-ice-facility/",
        "source_name": "Block Club Chicago",
        "verified": True
    },
]


# =============================================================================
# TIER 4: NEWS MEDIA - AD HOC SEARCH
# =============================================================================
# Found during targeted searches; higher risk of selection bias
# Included for completeness but should be weighted lower in analysis

TIER_4_INCIDENTS = [
    # These were found in earlier ad-hoc searches
    # Keeping them but flagging as lower confidence for systematic analysis

    {
        "id": "T4-001",
        "date": "2025-09-26",
        "state": "Illinois",
        "city": "Broadview",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "victim_category": "protester",
        "weapon_used": "pepper_balls",
        "victim_name": "Bushra Amiwala",
        "victim_occupation": "Democratic congressional candidate",
        "injury_type": "pepper ball strike",
        "us_citizen": True,
        "notes": "Democratic congressional candidate struck by pepper bullets",
        "protest_related": True,
        "source_tier": 4,
        "collection_method": "ad_hoc_search",
        "source_url": "https://blockclubchicago.org/2025/09/26/feds-tear-gas-shoot-rubber-bullets-at-protesters-outside-broadview-ice-facility/",
        "source_name": "Block Club Chicago",
        "verified": True
    },
    # Louisiana wrongful deportation
    {
        "id": "T4-002",
        "date": "2025-06-18",
        "state": "Louisiana",
        "city": "Angola (Camp 57)",
        "incident_type": "wrongful_deportation",
        "enforcement_granularity": "wrongful_deportation",
        "victim_name": "Chanthila Souvannarath",
        "us_citizen": True,
        "notes": "Federal judge issued TRO prohibiting removal; ICE deported him anyway",
        "source_tier": 4,
        "collection_method": "ad_hoc_search",
        "source_url": "https://nipnlg.org/news/press-releases/ice-deports-man-claiming-us-citizenship-laos-despite-federal-court-order",
        "source_name": "NIPNLG",
        "verified": True
    },
    # =========================================================================
    # Additional Tier 4 incidents found 2026-01-24
    # =========================================================================
    # California - First known death during ICE raid (not in custody)
    {
        "id": "T4-003",
        "date": "2025-07-12",
        "state": "California",
        "city": "Camarillo/Carpinteria",
        "incident_type": "death_in_custody",  # During raid, not in custody
        "enforcement_granularity": "death_in_custody",
        "victim_name": "Jaime Alanis",
        "victim_age": 57,
        "outcome": "death",
        "notes": "First known death during Trump ICE raid. Fell 30 feet from greenhouse roof at Glass House Farms cannabis facility while hiding/fleeing. Broke neck. ~200 arrested, 10 minors found. DHS says he wasn't 'pursued' but family says he was hiding. GoFundMe raised $150k+.",
        "source_tier": 4,
        "collection_method": "ad_hoc_search",
        "source_url": "https://www.cnn.com/2025/07/13/us/farmworker-dies-california-immigration-raids-hnk",
        "source_name": "CNN",
        "verified": True
    },
    # Texas - Dallas ICE facility shooting (attack ON ICE, not by ICE)
    {
        "id": "T4-004",
        "date": "2025-09-24",
        "state": "Texas",
        "city": "Dallas (Love Field)",
        "incident_type": "shooting_at_agent",  # Attack on facility
        "enforcement_granularity": "shooting_at_agent",
        "victim_count": 3,
        "outcome": "2 deaths, 1 injured",
        "notes": "Shooter Joshua Jahn fired from rooftop into ICE facility sally port, hitting 3 detainees in van. 1 died on scene, 1 died 6 days later. Jahn killed self. NOT an ICE shooting - attack on ICE.",
        "source_tier": 4,
        "collection_method": "ad_hoc_search",
        "source_url": "https://en.wikipedia.org/wiki/2025_Dallas_ICE_facility_shooting",
        "source_name": "Wikipedia / multiple sources",
        "verified": True
    },
    # Texas - Alvarado ICE facility attack
    {
        "id": "T4-005",
        "date": "2025-07-04",
        "state": "Texas",
        "city": "Alvarado (Prairieland)",
        "incident_type": "shooting_at_agent",
        "enforcement_granularity": "shooting_at_agent",
        "outcome": "1 officer injured",
        "notes": "Attack on Prairieland ICE Detention Center. 12 individuals allegedly used fireworks to lure officers, then ambushed. Person in green mask fired rifle from woods. Alvarado police officer shot in neck, released same day.",
        "source_tier": 4,
        "collection_method": "ad_hoc_search",
        "source_url": "https://en.wikipedia.org/wiki/2025_Alvarado_ICE_facility_incident",
        "source_name": "Wikipedia",
        "verified": True
    },
    # Illinois - Chicago shooting of US citizen
    {
        "id": "T4-006",
        "date": "2025-10-04",
        "state": "Illinois",
        "city": "Chicago (Southwest Side)",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_nonfatal",
        "victim_name": "Marimar Martinez",
        "victim_age": 30,
        "us_citizen": True,
        "outcome": "injury",
        "notes": "US citizen shot ~5 times by Border Patrol agent. DHS claimed she rammed agents' car; her lawyers say bodycam shows agents rammed HER. Assault charges against Martinez dropped. Related to Sep 12 incident where ICE officer was dragged.",
        "source_tier": 4,
        "collection_method": "ad_hoc_search",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    # California - Los Angeles TikToker shot
    {
        "id": "T4-007",
        "date": "2025-10-21",
        "state": "California",
        "city": "Los Angeles (South)",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_nonfatal",
        "victim_name": "Carlitos Ricardo Parias",
        "victim_age": 44,
        "victim_nationality": "Mexico",
        "outcome": "injury",
        "notes": "Mexican TikToker known as 'Richard LA' shot by federal officers. Boxed in by 3 government vehicles executing arrest warrant. Officials say he failed to comply and tried to dislodge vehicle.",
        "source_tier": 4,
        "collection_method": "ad_hoc_search",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    # Arizona - Phoenix I-17 shooting
    {
        "id": "T4-008",
        "date": "2025-10-29",
        "state": "Arizona",
        "city": "Phoenix (I-17)",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_nonfatal",
        "victim_name": "Jose Garcia-Sorto",
        "victim_nationality": "Honduras",
        "outcome": "injury",
        "notes": "Shot twice by ICE officer on Interstate 17 at 4am. DHS says he began pulling away when officers approached, officer 'defensively discharged' weapon. Treated at hospital, stable condition.",
        "source_tier": 4,
        "collection_method": "ad_hoc_search",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    # Alabama - US citizen detained twice, lawsuit filed
    {
        "id": "T4-009",
        "date": "2025-05-00",
        "state": "Alabama",
        "city": "Baldwin",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_name": "Leonardo Garcia Venegas",
        "us_citizen": True,
        "notes": "US-born citizen and construction worker detained TWICE by ICE. First detention in May at construction site by armed men in camouflage. Filed federal lawsuit claiming Fourth Amendment violation.",
        "source_tier": 4,
        "collection_method": "ad_hoc_search",
        "source_url": "https://abcnews.go.com/US/us-born-citizen-sues-after-arrested-immigration-agents/story?id=126129734",
        "source_name": "ABC News",
        "verified": True
    },
    # =========================================================================
    # March-April 2025 incidents found via systematic agent search (2026-01-25)
    # =========================================================================
    # Washington - Union leader arrest with documented force
    {
        "id": "T4-010",
        "date": "2025-03-25",
        "state": "Washington",
        "city": "Sedro-Woolley",
        "incident_type": "physical_force",
        "enforcement_granularity": "individual_force",
        "victim_category": "enforcement_target",
        "victim_name": "Alfredo 'Lelo' Juarez Zeferino",
        "victim_age": 25,
        "victim_occupation": "farmworker, union leader",
        "weapon_used": "vehicle damage",
        "outcome": "detained, vehicle window broken",
        "notes": "ICE broke car window and 'forced him out of vehicle when he tried to exercise his rights'. Founding member of Familias Unidas por la Justicia. Sparked 300-person protest at Tacoma NWDC on Mar 27.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.kuow.org/stories/hundreds-rally-at-ice-center-in-tacoma-after-detention-of-union-members",
        "source_name": "KUOW",
        "verified": True
    },
    # Washington - Green card holder detained at airport
    {
        "id": "T4-011",
        "date": "2025-02-28",
        "state": "Washington",
        "city": "SeaTac",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "collateral_detention",
        "victim_category": "enforcement_target",
        "victim_name": "Lewelyn Dixon",
        "victim_age": 64,
        "victim_occupation": "lab technician at UW Medicine",
        "us_citizen": False,
        "notes": "Green card holder for 50+ years, legally allowed to live/work in US indefinitely. Detained at Sea-Tac returning from Philippines. Transferred to Tacoma NWDC.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.spokesman.com/stories/2025/mar/28/ice-arrests-spark-protest-at-tacoma-immigration-de/",
        "source_name": "Spokesman Review",
        "verified": True
    },
    # Vermont - Armed farm raid
    {
        "id": "T4-012",
        "date": "2025-04-21",
        "state": "Vermont",
        "city": "Pleasant Valley Farms",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_category": "enforcement_target",
        "victim_count": 8,
        "weapon_used": "armed raid",
        "outcome": "8 detained, at least 3 deported to Mexico",
        "notes": "Armed CBP agents raided Vermont dairy farm. Largest single immigration arrest of farmworkers in recent Vermont history. Ages 22-41. Rattled VT $5.4B dairy industry (94% of dairies hire migrant workers). Governor Scott issued statement calling migrants essential.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://civileats.com/2025/04/24/federal-agents-detain-workers-at-a-vermont-dairy-farm/",
        "source_name": "Civil Eats",
        "verified": True
    },
    # Boston - ICE agent held in contempt
    {
        "id": "T4-013",
        "date": "2025-03-27",
        "state": "Massachusetts",
        "city": "Boston",
        "incident_type": "physical_force",
        "enforcement_granularity": "individual_force",
        "victim_category": "enforcement_target",
        "victim_name": "Wilson Martell-Lebron",
        "outcome": "detained, ICE agent held in contempt",
        "notes": "Defendant arrested by ICE immediately after stepping outside courthouse following first day of trial. Judge Mark Summerville held ICE agent Brian Sullivan in contempt for 'knowingly and intentionally preventing the defendant's appearance at an ongoing jury trial.'",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.cnn.com/2025/05/06/us/ice-courthouse-arrests-public-safety",
        "source_name": "CNN",
        "verified": True
    },
    # Colorado - Vigil for detained activist
    {
        "id": "T4-014",
        "date": "2025-03-24",
        "state": "Colorado",
        "city": "Aurora",
        "incident_type": "less_lethal",
        "protest_granularity": "confrontation",
        "victim_category": "protester",
        "victim_name": "Jeanette Vizguerra supporters",
        "protest_attendance": 200,
        "outcome": "peaceful vigil",
        "notes": "200 people gathered outside GEO Aurora ICE detention center for vigil supporting detained immigrant rights activist Jeanette Vizguerra. Part of weekly Monday protests since March 17 after her detention outside a Target store.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://unicornriot.ninja/2025/vigil-at-geo-ice-detention-center-in-aurora-spreads-love-to-immigrants/",
        "source_name": "Unicorn Riot",
        "verified": True
    },
    # California - Dublin vigil
    {
        "id": "T4-015",
        "date": "2025-04-16",
        "state": "California",
        "city": "Dublin",
        "incident_type": "less_lethal",
        "protest_granularity": "confrontation",
        "victim_category": "protester",
        "protest_attendance": 100,
        "outcome": "peaceful interfaith vigil",
        "notes": "Kickoff event for Communities Not Cages National Day of Action. 100 people gathered outside former Dublin Women's Prison (closed 2024) being proposed to reopen as ICE detention center.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.detentionwatchnetwork.org/pressroom/releases/2025/national-day-action-across-country-denounce-ice-detention-raids-abductions",
        "source_name": "Detention Watch Network",
        "verified": True
    },
    # National Day of Action - April 17
    {
        "id": "T4-016",
        "date": "2025-04-17",
        "state": "Multiple",
        "city": "17 cities nationwide",
        "incident_type": "less_lethal",
        "protest_granularity": "confrontation",
        "victim_category": "protester",
        "outcome": "coordinated national protests",
        "notes": "Communities Not Cages National Day of Action: 17 in-person demonstrations and 2 virtual actions across 13 states + DC. Cities included LA, Phoenix, Denver, Atlanta, NYC, Aurora, Fort Worth, Oklahoma City, Tulsa, Grand Rapids, New Orleans, Elizabeth NJ. 100+ supporting orgs.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.newsweek.com/anti-ice-protests-immigration-trump-2061125",
        "source_name": "Newsweek",
        "verified": True
    },
    # Atlanta - ICE field office rally
    {
        "id": "T4-017",
        "date": "2025-04-17",
        "state": "Georgia",
        "city": "Atlanta",
        "incident_type": "less_lethal",
        "protest_granularity": "confrontation",
        "victim_category": "protester",
        "protest_attendance": 100,
        "outcome": "peaceful rally",
        "notes": "Nearly 100 people rallied outside ICE field office in downtown Atlanta as part of Communities Not Cages National Day of Action. Speakers included Uche Onwa (Black Diaspora Liberty Initiative).",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://atlpresscollective.com/2025/04/23/ice-detention-field-office-protest/",
        "source_name": "Atlanta Press Collective",
        "verified": True
    },
    # Milwaukee - Judge Dugan protest
    {
        "id": "T4-018",
        "date": "2025-04-25",
        "state": "Wisconsin",
        "city": "Milwaukee",
        "incident_type": "less_lethal",
        "protest_granularity": "confrontation",
        "victim_category": "protester",
        "outcome": "protest after judge arrest",
        "notes": "Protests outside Milwaukee Federal Building after Judge Hannah Dugan arrested by FBI and charged with allegedly helping undocumented immigrant avoid arrest. Wisconsin Supreme Court suspended Dugan on April 29.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.cnn.com/2025/05/06/us/ice-courthouse-arrests-public-safety",
        "source_name": "CNN",
        "verified": True
    },
    # New Jersey - Elizabeth detention center protest
    {
        "id": "T4-019",
        "date": "2025-03-03",
        "state": "New Jersey",
        "city": "Elizabeth",
        "incident_type": "less_lethal",
        "protest_granularity": "confrontation",
        "victim_category": "protester",
        "outcome": "peaceful protest",
        "notes": "Dozens of protesters gathered in front of CoreCivic detention center in Elizabeth, protesting conditions and planned opening of Delaney Hall (1,000-bed facility, $1B 15-year GEO Group contract).",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://newjerseymonitor.com/2025/03/04/as-ice-eyes-new-immigrant-jail-in-newark-activists-protest-conditions-at-elizabeth-detention-center/",
        "source_name": "New Jersey Monitor",
        "verified": True
    },
    # New Jersey - Newark coalition protest
    {
        "id": "T4-020",
        "date": "2025-03-11",
        "state": "New Jersey",
        "city": "Newark",
        "incident_type": "less_lethal",
        "protest_granularity": "confrontation",
        "victim_category": "protester",
        "outcome": "peaceful coalition protest",
        "notes": "Coalition of 30+ faith-based organizations, labor unions, and immigrant rights groups gathered to protest imminent reopening of Delaney Hall as ICE detention facility.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://newjerseymonitor.com/2025/03/04/as-ice-eyes-new-immigrant-jail-in-newark-activists-protest-conditions-at-elizabeth-detention-center/",
        "source_name": "New Jersey Monitor",
        "verified": True
    },
    # =========================================================================
    # Additional June-December 2025 incidents found via systematic search (2026-01-25)
    # =========================================================================
    # Austin TX - June 9-10 with officer injuries (TIER 3 QUALITY - documented force/injuries)
    {
        "id": "T4-021",
        "date": "2025-06-09",
        "state": "Texas",
        "city": "Austin",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "victim_category": "officer",
        "weapon_used": "pepper_balls, tear_gas (CS)",
        "victim_name": "4 APD officers",
        "officer_injuries": 4,
        "arrest_count": 13,
        "outcome": "4 officers injured (3 by rocks, 1 shoulder + spit on), 13 arrested",
        "protest_related": True,
        "notes": "Protest started at TX Capitol, moved downtown. Protesters threw 'very large rocks' at officers. APD deployed pepper balls, DPS deployed CS tear gas. Gov. Abbott deployed National Guard. 8 APD arrests (2 for graffiti), 5 DPS arrests (3 felony criminal mischief). All 4 officers treated at hospital and released.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://cbsaustin.com/news/local/4-officers-injured-12-people-arrested-during-ice-protests-in-austin",
        "source_name": "CBS Austin",
        "verified": True
    },
    # Broadview IL - November 14 with officer injuries
    {
        "id": "T4-022",
        "date": "2025-11-14",
        "state": "Illinois",
        "city": "Broadview",
        "incident_type": "physical_force",
        "protest_granularity": "mass_arrest",
        "victim_category": "multiple",
        "officer_injuries": 4,
        "arrest_count": 21,
        "outcome": "21 arrested, 4 officers injured",
        "protest_related": True,
        "notes": "Protesters clashed with police outside ICE facility. Ages 25-69 arrested, charged with obstruction/disorderly conduct. Part of ~80 total arrests since early October when Illinois State Police set up designated protest zones. Mayor issued Civil Emergency Order Nov 17.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://abc7chicago.com/post/village-broadview-il-protest-several-detained-outside-ice-facility-protesters-push-designated-area-live/18154986/",
        "source_name": "ABC7 Chicago",
        "verified": True
    },
    # San Francisco - December 16 faith leaders arrested
    {
        "id": "T4-023",
        "date": "2025-12-16",
        "state": "California",
        "city": "San Francisco",
        "incident_type": "physical_force",
        "protest_granularity": "mass_arrest",
        "victim_category": "protester",
        "arrest_count": 44,
        "outcome": "44 arrested, ICE office closed for day",
        "protest_related": True,
        "notes": "200+ faith leaders (ministers, rabbis, imams) chained themselves to ICE building entrances starting 6:30am. Blocked entrance for ~5 hours. SF Fire Dept cut chains. Organized by Interfaith Movement for Human Integrity. DHS called them 'rioters' but reporters described 'mostly peaceful protest.'",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://abc7news.com/post/dozens-protesters-faith-communities-block-entrances-san-francisco-ice-building/18292234/",
        "source_name": "ABC7 San Francisco",
        "verified": True
    },
    # Portland OR - October 15 'Night of Terror'
    {
        "id": "T4-024",
        "date": "2025-10-15",
        "state": "Oregon",
        "city": "Portland",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "victim_category": "protester",
        "weapon_used": "tear_gas, pepper_balls",
        "outcome": "multiple arrests, extreme force",
        "protest_related": True,
        "notes": "'A Night of Terror: Civil Disobedience Met With Extreme Force at Portland ICE Facility' - Portland Mercury headline. Part of near-nightly protests since June 9. FBI claims 128 arrests since June 9 with 27 active investigations. Many arrested never informed of reason or read rights.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.portlandmercury.com/news/2025/10/15/48075462/a-night-of-terror-civil-disobedience-met-with-extreme-force-at-portland-ice-facility",
        "source_name": "Portland Mercury",
        "verified": True
    },
    # LA June protests aggregate (575 arrests)
    {
        "id": "T4-025",
        "date": "2025-06-10",
        "state": "California",
        "city": "Los Angeles",
        "incident_type": "physical_force",
        "protest_granularity": "mass_arrest",
        "victim_category": "protester",
        "arrest_count": 575,
        "outcome": "575 total protest-related arrests since June 7",
        "protest_related": True,
        "notes": "LAPD made 575 protest-related arrests since June 7, including 14 for looting. Trump deployed 4,000 CA National Guard + 700 Marines (later ruled illegal violation of Posse Comitatus by Judge Breyer on Sep 3). David Huerta (SEIU CA president) arrested, charged with felony conspiracy to impede officer, $50k bond. Judge Frimpong ruled on July 11 admin likely violated immigrants' rights. Prosecutors failed to secure indictments for majority after DHS agents found to have made false statements.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://en.wikipedia.org/wiki/June_2025_Los_Angeles_protests_against_mass_deportation",
        "source_name": "Wikipedia / multiple sources",
        "verified": True
    },
    # =========================================================================
    # January 2026 Operation Metro Surge protest incidents (2026-01-25)
    # =========================================================================
    # Minneapolis Airport clergy protest - ~100 arrested
    {
        "id": "T4-026",
        "date": "2026-01-23",
        "state": "Minnesota",
        "city": "Minneapolis (MSP Airport)",
        "incident_type": "physical_force",
        "protest_granularity": "mass_arrest",
        "victim_category": "protester",
        "arrest_count": 100,
        "outcome": "~100 clergy arrested protesting deportation flights",
        "protest_related": True,
        "notes": "Part of 'ICE Out' day of action. ~100 members of clergy arrested at Minneapolis-St. Paul International Airport protesting deportation flights. Charged with misdemeanor trespassing and failure to comply with peace officer. Same day 700+ MN businesses closed for 'economic blackout'.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.fox9.com/news/ice-minnesota-updates-jan-23-2026",
        "source_name": "Fox 9 Minneapolis",
        "verified": True
    },
    # St. Paul church protest - 3 arrested including civil rights attorney
    {
        "id": "T4-027",
        "date": "2026-01-22",
        "state": "Minnesota",
        "city": "St. Paul",
        "incident_type": "physical_force",
        "protest_granularity": "individual_arrest",
        "victim_category": "protester",
        "victim_name": "Nekima Levy Armstrong and 2 others",
        "arrest_count": 3,
        "outcome": "3 arrested including prominent civil rights attorney",
        "protest_related": True,
        "notes": "Protesters entered Cities Church in St. Paul where an ICE official serves as pastor. Nekima Levy Armstrong (prominent civil rights attorney) arrested on federal charges of 'conspiracy to deprive others of their rights' (religious rights). Journalist initially detained but not charged.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.npr.org/2026/01/22/g-s1-106899/minnesota-church-protest-arrests-pam-bondi-don-lemon",
        "source_name": "NPR",
        "verified": True
    },
    # Minnesota economic blackout
    {
        "id": "T4-028",
        "date": "2026-01-23",
        "state": "Minnesota",
        "city": "Statewide",
        "incident_type": "less_lethal",
        "protest_granularity": "confrontation",
        "victim_category": "protester",
        "outcome": "700+ businesses closed, thousands protested in freezing cold",
        "protest_related": True,
        "notes": "Statewide 'economic blackout' and general strike. 700+ MN businesses closed. Thousands picketed in freezing cold. Federal agents used tear gas and pepper spray against protesters. Governor Walz placed National Guard on standby. Part of largest coordinated protest action in MN history.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.npr.org/2026/01/23/nx-s1-5686733/minnesotans-day-of-ice-protests",
        "source_name": "NPR",
        "verified": True
    },
    # Portland January 2026 ongoing protests
    {
        "id": "T4-029",
        "date": "2026-01-09",
        "state": "Oregon",
        "city": "Portland",
        "incident_type": "physical_force",
        "protest_granularity": "mass_arrest",
        "victim_category": "protester",
        "arrest_count": 6,
        "outcome": "6 arrests, total 79 ICE protest-related arrests to date",
        "protest_related": True,
        "notes": "Portland Police monitored protest activity near ICE facility. 6 targeted arrests made. Brings total ICE protest-related arrests in Portland to 79 since June 2025.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.portland.gov/police/news/2026/1/9/ppb-monitors-protest-activity-near-ice-facility-six-arrests-made",
        "source_name": "Portland.gov",
        "verified": True
    },
    # =========================================================================
    # February 2025 LA Freeway Blockade (2026-01-25)
    # =========================================================================
    {
        "id": "T4-030",
        "date": "2025-02-03",
        "state": "California",
        "city": "Los Angeles (Cesar Chavez tunnel)",
        "incident_type": "physical_force",
        "protest_granularity": "mass_arrest",
        "victim_category": "protester",
        "arrest_count": 200,
        "outcome": "~200 detained in tunnel, 1 arrested for firearm possession",
        "protest_related": True,
        "notes": "Feb 2-3 protests shut down 101 freeway. Feb 2: thousands marched from Olvera St to City Hall, blocked freeway. Feb 3: LAPD declared unlawful assembly after bottles/rocks thrown. ~200 detained in tunnel at 200 block Cesar Chavez Ave. Firework shot at police helicopter. San Bernardino protest same day used tear gas and BearCats.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.cbsnews.com/losangeles/news/protest-downtown-los-angeles-over-ice-raids-deportation-streets-national-day-of-action/",
        "source_name": "CBS Los Angeles",
        "verified": True
    },
    # =========================================================================
    # July 2025 Camarillo Raid additional victims (2026-01-25)
    # =========================================================================
    # George Retes - disabled veteran wrongfully detained
    {
        "id": "T4-031",
        "date": "2025-07-10",
        "state": "California",
        "city": "Camarillo (Glass House Farms)",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_category": "us_citizen_collateral",
        "victim_name": "George Retes",
        "victim_age": 25,
        "victim_occupation": "security guard, Army veteran",
        "us_citizen": True,
        "weapon_used": "pepper_spray, tear_gas, vehicle damage",
        "outcome": "detained 3 days without charges, lawsuit filed",
        "notes": "US citizen and disabled Army veteran detained while driving to work. Pepper sprayed, tear gassed, car window smashed, dragged out at gunpoint. Knee on neck, knee on back. Held 3 days without charges, phone call, or legal help. Missed daughter's 3rd birthday. Testified before Congress Dec 9. Institute for Justice representing in lawsuit.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.democracynow.org/2025/8/25/george_retes",
        "source_name": "Democracy Now",
        "verified": True
    },
    # Rafie Ollah Shouhed - 79yo car wash owner
    {
        "id": "T4-032",
        "date": "2025-07-00",
        "state": "California",
        "city": "Van Nuys",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_category": "us_citizen_collateral",
        "victim_name": "Rafie Ollah Shouhed",
        "victim_age": 79,
        "victim_occupation": "car wash owner",
        "us_citizen": True,
        "outcome": "injured, detained 12 hours, never charged, $50M tort claim filed",
        "notes": "79-year-old US citizen car wash owner in Van Nuys detained for nearly 12 hours, suffered injuries, never charged. Filed $50 million tort claim against DHS and ICE alleging 'illegal and unlawful assault and battery.'",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.jeelani-law.com/ice-facing-claims-after-violent-arrests/",
        "source_name": "Jeelani Law Firm",
        "verified": True
    },
    # Job Garcia - detained at Dodger Stadium
    {
        "id": "T4-033",
        "date": "2025-06-00",
        "state": "California",
        "city": "Los Angeles (Dodger Stadium)",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_category": "us_citizen_collateral",
        "victim_name": "Job Garcia",
        "us_citizen": True,
        "outcome": "detained, taken to Dodger Stadium processing, released",
        "notes": "US citizen detained by Border Patrol/ICE. Agent said 'I got another one' - Garcia understood as racially charged. Taken in van to Dodger Stadium with other arrestees. Agents confirmed he was US citizen with no warrants but continued to hold him. Heard agents boasting about 'bodies' they had gotten. MALDEF representing.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.maldef.org/2025/07/maldef-takes-a-step-toward-civil-rights-lawsuit-on-behalf-of-u-s-citizen-detained-by-ice/",
        "source_name": "MALDEF",
        "verified": True
    },
    # =========================================================================
    # September 2025 Operation Midway Blitz - Broadview additional incidents
    # =========================================================================
    # Ashley Vaughan - shot in face while livestreaming
    {
        "id": "T4-034",
        "date": "2025-09-12",
        "state": "Illinois",
        "city": "Broadview",
        "incident_type": "less_lethal",
        "protest_granularity": "individual_injury",
        "victim_category": "protester",
        "victim_name": "Ashley Vaughan",
        "weapon_used": "pepper_balls",
        "injury_type": "shot in face, lost consciousness",
        "outcome": "shot in face and body with pepper balls, briefly lost consciousness",
        "protest_related": True,
        "notes": "Protester who carries a cane shot in face and body with pepper balls by agents on detention facility roof while livestreaming around 6pm. Briefly lost consciousness. Part of Operation Midway Blitz (Sep 8 - Oct 3, 1,000+ arrested in Chicago area).",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://blockclubchicago.org/2025/09/19/ice-tear-gasses-detains-protesters-outside-broadview-facility/",
        "source_name": "Block Club Chicago",
        "verified": True
    },
    # Raven Geary - journalist shot in face
    {
        "id": "T4-035",
        "date": "2025-09-26",
        "state": "Illinois",
        "city": "Broadview",
        "incident_type": "less_lethal",
        "protest_granularity": "journalist_attack",
        "victim_category": "journalist",
        "victim_name": "Raven Geary",
        "victim_occupation": "journalist",
        "weapon_used": "pepper_spray_projectile",
        "injury_type": "shot in face",
        "outcome": "journalist shot in face with pepper spray projectile",
        "protest_related": True,
        "notes": "Journalist who attended 2 dozen+ protests shot in face with pepper spray projectile. Said 'I have never seen anything like this response in my life.' Federal judge later ruled agents can't use tear gas/pepper spray on journalists after Block Club Chicago and others sued.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://blockclubchicago.org/2025/09/28/ice-escalates-violence-against-protesters-in-broadview-journalist-arrested/",
        "source_name": "Block Club Chicago",
        "verified": True
    },
    # September 26 mass arrests
    {
        "id": "T4-036",
        "date": "2025-09-26",
        "state": "Illinois",
        "city": "Broadview",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "victim_category": "protester",
        "weapon_used": "tear_gas, pepper_balls, flash_bangs",
        "arrest_count": 11,
        "outcome": "11 arrested, 4 federal charges, tear gas deployed",
        "protest_related": True,
        "notes": "Federal officers used tear gas, pepper balls, flash bang grenades. 11 arrested, 4 charged federally with assaulting/resisting officers. Mayor Thompson: 'relentless deployment of tear gas, pepper spray, mace, and rubber bullets' endangering residents. Gov. Pritzker accused Trump admin of trying to destabilize Chicago.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://abcnews.go.com/US/4-charged-after-anti-ice-protest-chicago-facility/story?id=126047334",
        "source_name": "ABC News",
        "verified": True
    },
    # =========================================================================
    # August 2025 Farm Raids
    # =========================================================================
    # Woodburn OR - farmworkers detained going to work
    {
        "id": "T4-037",
        "date": "2025-08-08",
        "state": "Oregon",
        "city": "Woodburn",
        "incident_type": "mass_raid",
        "enforcement_granularity": "collateral_detention",
        "victim_category": "enforcement_target",
        "victim_count": 4,
        "outcome": "4 farmworkers detained on way to blueberry farm",
        "notes": "ICE detained 4 immigrant farmworkers on their way to work at a blueberry farm.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://civileats.com/2025/06/11/ice-raids-target-workers-on-farms-and-in-food-production-a-running-list/",
        "source_name": "Civil Eats",
        "verified": True
    },
    # Kent NY - Lynn-Ette Farms (UFW organizing site)
    {
        "id": "T4-038",
        "date": "2025-08-14",
        "state": "New York",
        "city": "Kent",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_category": "enforcement_target",
        "victim_count": 7,
        "outcome": "7 workers detained at farm where UFW was organizing",
        "notes": "ICE raided Lynn-Ette Farms where United Farm Workers had been organizing. 7 workers detained. Raid on UFW organizing site raises concerns about targeting labor organizing.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://civileats.com/2025/06/11/ice-raids-target-workers-on-farms-and-in-food-production-a-running-list/",
        "source_name": "Civil Eats",
        "verified": True
    },
    # =========================================================================
    # Journalist incidents (2026-01-25)
    # =========================================================================
    # Steve Held - arrested at Broadview
    {
        "id": "T4-039",
        "date": "2025-09-27",
        "state": "Illinois",
        "city": "Broadview",
        "incident_type": "physical_force",
        "protest_granularity": "journalist_attack",
        "victim_category": "journalist",
        "victim_name": "Steve Held",
        "victim_occupation": "co-founder/reporter, Unraveled Press",
        "outcome": "tackled and arrested by federal agents while reporting",
        "protest_related": True,
        "notes": "Journalist tackled and arrested by federal agents while reporting on protests. Press Freedom Tracker documented incident. Judge later issued injunction forbidding agents from using force against journalists without probable cause.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://pressfreedomtracker.us/all-incidents/journalist-tackled-arrested-by-federal-agents-at-illinois-ice-protest/",
        "source_name": "U.S. Press Freedom Tracker",
        "verified": True
    },
    # Eddie Kim - pepper sprayed SF
    {
        "id": "T4-040",
        "date": "2025-08-20",
        "state": "California",
        "city": "San Francisco",
        "incident_type": "less_lethal",
        "protest_granularity": "journalist_attack",
        "victim_category": "journalist",
        "victim_name": "Eddie Kim",
        "victim_occupation": "journalist",
        "weapon_used": "pepper_spray",
        "injury_type": "pepper spray to eyes",
        "outcome": "pepper spray shot directly into eyes",
        "protest_related": True,
        "notes": "Reporter described: 'In a literal second, the agent pulled out his pepper gel, sprayed the protester next to me, and then shot a stream straight into my eyes.' At least one protester detained, two people including journalist pepper sprayed.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.kqed.org/news/12052975/federal-officers-detain-protester-after-clash-outside-san-francisco-ice-office",
        "source_name": "KQED",
        "verified": True
    },
    # =========================================================================
    # Bystander incidents (2026-01-25)
    # =========================================================================
    # Andrea Velez - US citizen tackled walking to work
    {
        "id": "T4-041",
        "date": "2025-06-24",
        "state": "California",
        "city": "Los Angeles",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "wrongful_detention",
        "victim_category": "us_citizen_collateral",
        "victim_name": "Andrea Velez",
        "victim_occupation": "marketing designer",
        "us_citizen": True,
        "outcome": "tackled walking to work, held 24+ hours",
        "notes": "US citizen marketing designer tackled to ground while walking to work. Repeatedly told agents she was citizen but they doubted her claims. Held in immigration detention over 24 hours before citizenship confirmed.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://theintercept.com/2025/07/07/ice-raids-la-violence-video-bystanders/",
        "source_name": "The Intercept",
        "verified": True
    },
    # Barbara Stone - 71yo grandmother detained
    {
        "id": "T4-042",
        "date": "2025-00-00",
        "state": "California",
        "city": "San Diego",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "collateral_detention",
        "victim_category": "bystander",
        "victim_name": "Barbara Stone",
        "victim_age": 71,
        "victim_occupation": "Detention Resistance volunteer",
        "us_citizen": True,
        "outcome": "detained, bruised, received anonymous AI-voice threat afterward",
        "notes": "71-year-old grandmother volunteering with Detention Resistance went to San Diego courthouse to watch ICE arrests, ended up in handcuffs. Bruises from agents grabbing her, scrapes from handcuffs. After case broadcast on national news, husband received anonymous AI-modified voice phone call threatening the couple.",
        "source_tier": 4,
        "collection_method": "systematic_search",
        "source_url": "https://www.cnn.com/2025/08/23/us/immigrant-bystander-rights-ice-raid",
        "source_name": "CNN",
        "verified": True
    },
    # Marimar Martinez - US citizen shot in Chicago
    {
        "id": "T4-043",
        "date": "2025-10-04",
        "state": "Illinois",
        "city": "Chicago",
        "incident_type": "shooting_by_agent",
        "enforcement_granularity": "shooting_nonfatal",
        "victim_category": "us_citizen_collateral",
        "victim_name": "Marimar Martinez",
        "victim_age": 30,
        "us_citizen": True,
        "outcome": "shot, hospitalized, arrested",
        "notes": "30-year-old US citizen shot by Border Patrol agents. Federal officials claim she 'intentionally struck a vehicle belonging to agents.' Her lawyers say federal agents rammed HER car. Taken to hospital for gunshot wounds, arrested on charges of impeding law enforcement.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "verified": True
    },
    # =========================================================================
    # Oregon tear gas affecting residents lawsuit (2026-01-25)
    # =========================================================================
    {
        "id": "T4-044",
        "date": "2025-11-00",
        "state": "Oregon",
        "city": "Portland",
        "incident_type": "less_lethal",
        "protest_granularity": "force_deployment",
        "victim_category": "bystander",
        "weapon_used": "tear_gas, pepper_balls, CS_gas",
        "outcome": "lawsuit filed, residents suffered respiratory distress, PTSD",
        "protest_related": True,
        "notes": "Lawsuit filed against DHS. Plaintiffs claim officers deployed pepper balls and CS gas 'toward and around' low-income housing complex 'repeatedly when faced with no violence from protesters.' Nearby residents suffered acute respiratory distress, ocular burning, PTSD episodes. 660+ arrested in Oregon in 2025. Sen. Merkley called raids 'terrorizing our communities.'",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.foxnews.com/politics/oregon-residents-sue-homeland-security-after-tear-gas-used-anti-ice-protesters",
        "source_name": "Fox News",
        "verified": True
    },
    # =========================================================================
    # Deaths during raids - fleeing (2026-01-25)
    # =========================================================================
    # Roberto Carlos Montoya Valdés - Monrovia Home Depot
    {
        "id": "T4-045",
        "date": "2025-08-15",
        "state": "California",
        "city": "Monrovia",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_during_enforcement",
        "victim_category": "enforcement_target",
        "victim_name": "Roberto Carlos Montoya Valdés",
        "victim_age": 52,
        "victim_nationality": "Guatemala",
        "outcome": "death",
        "us_citizen": False,
        "notes": "Second person to die fleeing SoCal raids. Fled Home Depot during ICE operation, ran across eastbound I-210 freeway, struck by SUV going ~60mph. Suffered major injuries, died at hospital. Identified by National Day Laborer Organizing Network. Vigil held at site.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.nbcnews.com/news/us-news/man-fleeing-immigration-raid-california-fatally-struck-vehicle-officia-rcna225154",
        "source_name": "NBC News",
        "verified": True
    },
    # Josué Castro Rivera - Norfolk VA
    {
        "id": "T4-046",
        "date": "2025-10-00",
        "state": "Virginia",
        "city": "Norfolk",
        "incident_type": "death_in_custody",
        "enforcement_granularity": "death_during_enforcement",
        "victim_category": "enforcement_target",
        "victim_name": "Josué Castro Rivera",
        "victim_nationality": "Honduras",
        "outcome": "death",
        "us_citizen": False,
        "notes": "Was heading to gardening job when vehicle pulled over by ICE. Agents tried to detain him and 3 other passengers. Fled on foot, tried to cross I-264, fatally struck. Had been in US 4 years, working to send money to family in Honduras.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://www.pbs.org/newshour/nation/man-struck-dead-by-vehicle-on-virginia-highway-after-trying-to-flee-immigration-agents",
        "source_name": "PBS",
        "verified": True
    },
    # =========================================================================
    # Elected officials (2026-01-25)
    # =========================================================================
    # Brad Lander - NYC Comptroller arrested
    {
        "id": "T4-047",
        "date": "2025-06-17",
        "state": "New York",
        "city": "New York (26 Federal Plaza)",
        "incident_type": "physical_force",
        "protest_granularity": "individual_arrest",
        "victim_category": "protester",
        "victim_name": "Brad Lander",
        "victim_occupation": "NYC Comptroller, mayoral candidate",
        "us_citizen": True,
        "outcome": "arrested while escorting defendant from immigration court",
        "protest_related": True,
        "notes": "NYC Comptroller and mayoral candidate arrested by masked federal agents at 26 Federal Plaza while escorting defendant from immigration court. DHS charged him with 'assaulting law enforcement and impeding a federal court officer.' Video shows him led away in handcuffs. Part of pattern - at least 5 elected officials arrested/confronted in 2025.",
        "source_tier": 3,
        "collection_method": "systematic_search",
        "source_url": "https://gothamist.com/news/nyc-mayoral-candidate-comptroller-brad-lander-detained-by-ice-campaign-says",
        "source_name": "Gothamist",
        "verified": True
    },
]


# =============================================================================
# AGGREGATE ALL DATA
# =============================================================================

def get_all_incidents():
    """Return all incidents across all tiers."""
    all_incidents = []
    all_incidents.extend(TIER_1_DEATHS_IN_CUSTODY)
    all_incidents.extend(TIER_2_SHOOTINGS_BY_AGENTS)
    all_incidents.extend(TIER_2_SHOOTINGS_AT_AGENTS)
    all_incidents.extend(TIER_2_LESS_LETHAL)
    all_incidents.extend(TIER_2_WRONGFUL_DETENTIONS)
    all_incidents.extend(TIER_3_INCIDENTS)
    all_incidents.extend(TIER_4_INCIDENTS)
    return all_incidents


def get_incidents_by_tier(tier: int):
    """Return incidents for a specific tier."""
    all_incidents = get_all_incidents()
    return [i for i in all_incidents if i.get('source_tier') == tier]


def get_incidents_by_type(incident_type: str):
    """Return incidents of a specific type."""
    all_incidents = get_all_incidents()
    return [i for i in all_incidents if i.get('incident_type') == incident_type]


def create_summary_dataframe():
    """Create a summary DataFrame with all incidents."""
    all_incidents = get_all_incidents()
    df = pd.DataFrame(all_incidents)
    return df


def print_tier_summary():
    """Print summary statistics by tier."""
    all_incidents = get_all_incidents()

    print("=" * 80)
    print("TIERED INCIDENT DATABASE SUMMARY")
    print("=" * 80)

    for tier in [1, 2, 3, 4]:
        tier_incidents = [i for i in all_incidents if i.get('source_tier') == tier]
        tier_names = {
            1: "OFFICIAL GOVERNMENT DATA",
            2: "FOIA / INVESTIGATIVE JOURNALISM",
            3: "NEWS MEDIA - SYSTEMATIC SEARCH",
            4: "NEWS MEDIA - AD HOC SEARCH"
        }

        print(f"\n{'=' * 40}")
        print(f"TIER {tier}: {tier_names[tier]}")
        print(f"{'=' * 40}")
        print(f"Total incidents: {len(tier_incidents)}")

        # Count by type
        types = {}
        for i in tier_incidents:
            t = i.get('incident_type', 'unknown')
            types[t] = types.get(t, 0) + 1

        for t, count in sorted(types.items(), key=lambda x: -x[1]):
            print(f"  {t}: {count}")

        # Count outcomes
        deaths = sum(1 for i in tier_incidents if i.get('outcome') == 'death' or 'death' in i.get('incident_type', ''))
        injuries = sum(1 for i in tier_incidents if i.get('outcome') == 'injury' or i.get('injury'))
        us_citizens = sum(1 for i in tier_incidents if i.get('us_citizen') == True)

        print(f"  Deaths: {deaths}")
        print(f"  Injuries: {injuries}")
        print(f"  US Citizens affected: {us_citizens}")

    print("\n" + "=" * 80)
    print(f"TOTAL INCIDENTS ACROSS ALL TIERS: {len(all_incidents)}")
    print("=" * 80)


def infer_victim_category(incident):
    """Infer victim_category if not explicitly set."""
    # If already set, return it
    if incident.get('victim_category'):
        return incident['victim_category']

    # Infer based on incident characteristics
    incident_type = incident.get('incident_type', '')

    # Deaths in custody = detainee
    if incident_type == 'death_in_custody':
        return 'detainee'

    # Shootings at agents = officer (victim is officer)
    if incident_type == 'shooting_at_agent':
        return 'officer'

    # Wrongful detention/deportation of US citizens
    if incident.get('us_citizen') and incident_type in ['wrongful_detention', 'wrongful_deportation']:
        return 'us_citizen_collateral'

    # Protest-related incidents
    if incident.get('protest_related'):
        return 'protester'

    # Mass raids = enforcement targets
    if incident_type == 'mass_raid':
        return 'enforcement_target'

    # Default: enforcement_target (person being arrested)
    return 'enforcement_target'


def get_incidents_by_victim_category(category: str):
    """Return incidents affecting a specific victim category."""
    all_incidents = get_all_incidents()
    return [i for i in all_incidents if infer_victim_category(i) == category]


def analyze_by_victim_category():
    """Analyze incidents by who was affected."""
    all_incidents = get_all_incidents()

    categories = {}
    for incident in all_incidents:
        cat = infer_victim_category(incident)
        if cat not in categories:
            categories[cat] = {
                'count': 0,
                'deaths': 0,
                'injuries': 0,
                'incidents': []
            }
        categories[cat]['count'] += 1
        categories[cat]['incidents'].append(incident)

        # Count outcomes
        if incident.get('outcome') == 'death' or 'death' in incident.get('incident_type', ''):
            categories[cat]['deaths'] += 1
        if incident.get('outcome') == 'injury' or incident.get('injury'):
            categories[cat]['injuries'] += 1

    return categories


def print_victim_category_summary():
    """Print summary by victim category."""
    categories = analyze_by_victim_category()

    print("\n" + "=" * 80)
    print("ANALYSIS BY VICTIM CATEGORY")
    print("=" * 80)
    print("\nThis separates incidents affecting immigrants from those")
    print("affecting protesters, journalists, bystanders, etc.\n")

    for cat in ['detainee', 'enforcement_target', 'protester', 'journalist',
                'us_citizen_collateral', 'bystander', 'officer', 'multiple']:
        if cat in categories:
            data = categories[cat]
            print(f"\n{cat.upper().replace('_', ' ')}:")
            print(f"  Incidents: {data['count']}")
            print(f"  Deaths: {data['deaths']}")
            print(f"  Injuries: {data['injuries']}")

    return categories


# =============================================================================
# PROTEST INCIDENT GRANULARITY ANALYSIS
# =============================================================================

def get_protest_incidents():
    """Return all protest-related incidents."""
    all_incidents = get_all_incidents()
    return [i for i in all_incidents if i.get('protest_related') == True]


def analyze_protest_incidents_by_granularity():
    """
    Analyze protest incidents by granularity type.

    Returns breakdown of:
    - individual_injury: Named victims with documented physical harm
    - force_deployment: Crowd-level use of force events
    - mass_arrest: Arrest events with counts
    - individual_arrest: Notable individuals arrested
    - journalist_attack: Specific attacks on press
    - confrontation: Clashes without documented force/arrests
    - property_damage: Property damage incidents
    """
    protest_incidents = get_protest_incidents()

    granularity_data = {
        'individual_injury': {'count': 0, 'victim_count': 0, 'serious_injuries': 0, 'incidents': []},
        'force_deployment': {'count': 0, 'rounds_fired': 0, 'crowd_affected': 0, 'incidents': []},
        'mass_arrest': {'count': 0, 'total_arrests': 0, 'incidents': []},
        'individual_arrest': {'count': 0, 'notable_persons': 0, 'incidents': []},
        'journalist_attack': {'count': 0, 'journalists_affected': 0, 'incidents': []},
        'confrontation': {'count': 0, 'crowd_size': 0, 'incidents': []},
        'property_damage': {'count': 0, 'incidents': []},
    }

    for incident in protest_incidents:
        granularity = incident.get('protest_granularity', 'unknown')

        if granularity not in granularity_data:
            continue

        data = granularity_data[granularity]
        data['count'] += 1
        data['incidents'].append(incident)

        # Type-specific aggregations
        if granularity == 'individual_injury':
            data['victim_count'] += incident.get('victim_count', 1)
            if 'surgery' in str(incident.get('medical_treatment', '')).lower():
                data['serious_injuries'] += 1

        elif granularity == 'force_deployment':
            data['rounds_fired'] += incident.get('rounds_fired', 0)
            data['crowd_affected'] += incident.get('crowd_size', 0)

        elif granularity == 'mass_arrest':
            data['total_arrests'] += incident.get('arrest_count', 0)

        elif granularity == 'individual_arrest':
            data['notable_persons'] += incident.get('victim_count', 1)

        elif granularity == 'journalist_attack':
            data['journalists_affected'] += incident.get('victim_count', 1)

        elif granularity == 'confrontation':
            data['crowd_size'] += incident.get('crowd_size', 0)

    return granularity_data


def print_protest_granularity_summary():
    """Print detailed breakdown of protest incidents by granularity."""
    data = analyze_protest_incidents_by_granularity()

    print("\n" + "=" * 90)
    print("PROTEST INCIDENT ANALYSIS - GRANULAR BREAKDOWN")
    print("=" * 90)
    print("\nThis provides maximum granularity for protest-related incidents,")
    print("separating individual injuries from crowd-level events and arrests.\n")

    print("-" * 90)
    print(f"{'Category':<25} {'Incidents':>10} {'Key Metric':>40}")
    print("-" * 90)

    # Individual injuries
    d = data['individual_injury']
    print(f"{'INDIVIDUAL_INJURY':<25} {d['count']:>10} {'Victims: ' + str(d['victim_count']) + ', Serious (surgery): ' + str(d['serious_injuries']):>40}")

    # Force deployments
    d = data['force_deployment']
    print(f"{'FORCE_DEPLOYMENT':<25} {d['count']:>10} {'Rounds fired: ' + str(d['rounds_fired']) + ', Crowds: ' + str(d['crowd_affected']):>40}")

    # Mass arrests
    d = data['mass_arrest']
    print(f"{'MASS_ARREST':<25} {d['count']:>10} {'Total arrested: ' + str(d['total_arrests']):>40}")

    # Individual arrests
    d = data['individual_arrest']
    print(f"{'INDIVIDUAL_ARREST':<25} {d['count']:>10} {'Notable persons: ' + str(d['notable_persons']):>40}")

    # Journalist attacks
    d = data['journalist_attack']
    print(f"{'JOURNALIST_ATTACK':<25} {d['count']:>10} {'Journalists affected: ' + str(d['journalists_affected']):>40}")

    # Confrontations
    d = data['confrontation']
    print(f"{'CONFRONTATION':<25} {d['count']:>10} {'Total crowd size: ' + str(d['crowd_size']):>40}")

    # Property damage
    d = data['property_damage']
    print(f"{'PROPERTY_DAMAGE':<25} {d['count']:>10} {'-':>40}")

    print("-" * 90)

    # Summary totals
    total_incidents = sum(d['count'] for d in data.values())
    total_arrests = data['mass_arrest']['total_arrests'] + data['individual_arrest']['notable_persons']
    total_injuries = data['individual_injury']['victim_count']

    print(f"\nTOTALS:")
    print(f"  Protest incidents (granular): {total_incidents}")
    print(f"  Documented individual injuries: {total_injuries}")
    print(f"  Documented arrests: {total_arrests}")
    print(f"  Force deployment events: {data['force_deployment']['count']}")

    return data


def export_protest_incidents_csv():
    """Export protest incidents to CSV with granularity."""
    protest_incidents = get_protest_incidents()

    rows = []
    for incident in protest_incidents:
        rows.append({
            'id': incident.get('id'),
            'date': incident.get('date'),
            'state': incident.get('state'),
            'city': incident.get('city'),
            'protest_granularity': incident.get('protest_granularity', 'unknown'),
            'victim_category': incident.get('victim_category'),
            'victim_name': incident.get('victim_name', ''),
            'victim_count': incident.get('victim_count', 1),
            'injury_type': incident.get('injury_type', ''),
            'arrest_count': incident.get('arrest_count', 0),
            'weapon_used': incident.get('weapon_used', ''),
            'outcome': incident.get('outcome', ''),
            'source_tier': incident.get('source_tier'),
            'source_url': incident.get('source_url', ''),
            'notes': incident.get('notes', ''),
        })

    df = pd.DataFrame(rows)
    df.to_csv('PROTEST_INCIDENTS_GRANULAR.csv', index=False)
    print(f"Saved {len(rows)} protest incidents to PROTEST_INCIDENTS_GRANULAR.csv")
    return df


# =============================================================================
# BACKWARD COMPATIBILITY - NEW PACKAGE IMPORTS
# =============================================================================
# The data in this file has been extracted to JSON files in data/incidents/
# The functions below provide access via the new package structure.
# Original exports (TIER_1_*, TIER_2_*, etc.) remain available above.

try:
    from ice_arrests.data.loader import (
        load_incidents as _load_incidents,
        get_incidents_by_tier as _get_by_tier,
        get_incidents_by_type as _get_by_type,
    )
    from ice_arrests.data.schemas import (
        SourceTier as _SourceTier,
        IncidentType as _IncidentType,
        VictimCategory as _VictimCategory,
        CollectionMethod as _CollectionMethod,
    )
    _NEW_PACKAGE_AVAILABLE = True
except ImportError:
    _NEW_PACKAGE_AVAILABLE = False


def load_from_json(tiers=None):
    """
    Load incidents from JSON files (new package method).

    Falls back to in-memory data if package not available.
    """
    if _NEW_PACKAGE_AVAILABLE:
        return _load_incidents(tiers=tiers)
    else:
        return get_all_incidents()


# =============================================================================
# ENFORCEMENT INCIDENT GRANULARITY ANALYSIS
# =============================================================================

def infer_enforcement_granularity(incident):
    """
    Infer enforcement granularity from existing incident fields.
    Used when explicit enforcement_granularity field is not set.
    """
    # If explicitly set, use it
    if incident.get('enforcement_granularity'):
        return incident['enforcement_granularity']

    incident_type = incident.get('incident_type', '')

    # Deaths
    if incident_type == 'death_in_custody':
        return 'death_in_custody'
    if 'death' in str(incident.get('outcome', '')).lower():
        if 'shooting' in incident_type:
            return 'shooting_fatal'
        return 'death_during_enforcement'

    # Shootings
    if incident_type == 'shooting_by_agent':
        outcome = str(incident.get('outcome', '')).lower()
        if 'death' in outcome or 'fatal' in outcome or 'killed' in outcome:
            return 'shooting_fatal'
        return 'shooting_nonfatal'

    if incident_type == 'shooting_at_agent':
        return 'shooting_at_agent'

    # Wrongful targeting
    if incident_type == 'wrongful_detention':
        return 'wrongful_detention'
    if incident_type == 'wrongful_deportation':
        return 'wrongful_deportation'

    # Mass raids
    if incident_type == 'mass_raid':
        notes = str(incident.get('notes', '')).lower()
        facility = str(incident.get('facility', '')).lower()
        city = str(incident.get('city', '')).lower()

        # Workplace indicators
        if any(x in notes + facility + city for x in ['plant', 'factory', 'construction', 'worksite',
                                                        'restaurant', 'warehouse', 'meatpacking']):
            return 'mass_raid_workplace'
        # Community indicators
        if any(x in notes for x in ['neighborhood', 'community', 'street', 'church', 'school']):
            return 'mass_raid_community'
        return 'mass_raid_targeted'

    # Physical force
    if incident_type == 'physical_force':
        return 'individual_force'

    if incident_type == 'less_lethal' and not incident.get('protest_related'):
        return 'less_lethal_enforcement'

    return 'unknown'


def get_enforcement_incidents():
    """Return all non-protest enforcement incidents."""
    all_incidents = get_all_incidents()
    return [i for i in all_incidents if not i.get('protest_related')]


def analyze_enforcement_incidents_by_granularity():
    """
    Analyze enforcement incidents by granularity type.
    """
    enforcement_incidents = get_enforcement_incidents()

    granularity_data = {
        'death_in_custody': {'count': 0, 'incidents': []},
        'death_during_enforcement': {'count': 0, 'incidents': []},
        'shooting_fatal': {'count': 0, 'incidents': []},
        'shooting_nonfatal': {'count': 0, 'incidents': []},
        'individual_force': {'count': 0, 'incidents': []},
        'less_lethal_enforcement': {'count': 0, 'incidents': []},
        'mass_raid_workplace': {'count': 0, 'total_arrested': 0, 'incidents': []},
        'mass_raid_community': {'count': 0, 'total_arrested': 0, 'incidents': []},
        'mass_raid_targeted': {'count': 0, 'total_arrested': 0, 'incidents': []},
        'wrongful_detention': {'count': 0, 'us_citizens': 0, 'incidents': []},
        'wrongful_deportation': {'count': 0, 'incidents': []},
        'collateral_detention': {'count': 0, 'incidents': []},
        'shooting_at_agent': {'count': 0, 'incidents': []},
        'attack_on_agent': {'count': 0, 'incidents': []},
        'unknown': {'count': 0, 'incidents': []},
    }

    for incident in enforcement_incidents:
        granularity = infer_enforcement_granularity(incident)

        if granularity not in granularity_data:
            granularity = 'unknown'

        data = granularity_data[granularity]
        data['count'] += 1
        data['incidents'].append(incident)

        # Type-specific aggregations
        if granularity.startswith('mass_raid'):
            data['total_arrested'] += incident.get('victim_count', 0)

        if granularity == 'wrongful_detention':
            if incident.get('us_citizen'):
                data['us_citizens'] += 1

    return granularity_data


def print_enforcement_granularity_summary():
    """Print detailed breakdown of enforcement incidents by granularity."""
    data = analyze_enforcement_incidents_by_granularity()

    print("\n" + "=" * 90)
    print("ENFORCEMENT INCIDENT ANALYSIS - GRANULAR BREAKDOWN")
    print("=" * 90)
    print("\nThis provides maximum granularity for enforcement-related incidents,")
    print("separating individual-level harms from mass operations.\n")

    print("-" * 90)
    print(f"{'Category':<30} {'Incidents':>10} {'Key Metric':>35}")
    print("-" * 90)

    # Deaths
    print("\nDEATHS:")
    d = data['death_in_custody']
    print(f"  {'death_in_custody':<28} {d['count']:>10}")
    d = data['death_during_enforcement']
    print(f"  {'death_during_enforcement':<28} {d['count']:>10}")
    d = data['shooting_fatal']
    print(f"  {'shooting_fatal':<28} {d['count']:>10}")

    # Shootings (non-fatal)
    print("\nSHOOTINGS (non-fatal):")
    d = data['shooting_nonfatal']
    print(f"  {'shooting_nonfatal':<28} {d['count']:>10}")

    # Physical force
    print("\nPHYSICAL FORCE:")
    d = data['individual_force']
    print(f"  {'individual_force':<28} {d['count']:>10}")
    d = data['less_lethal_enforcement']
    print(f"  {'less_lethal_enforcement':<28} {d['count']:>10}")

    # Mass raids
    print("\nMASS RAIDS:")
    for raid_type in ['mass_raid_workplace', 'mass_raid_community', 'mass_raid_targeted']:
        d = data[raid_type]
        arrested = f"({d['total_arrested']} arrested)" if d['total_arrested'] else ""
        print(f"  {raid_type:<28} {d['count']:>10} {arrested:>35}")

    # Wrongful targeting
    print("\nWRONGFUL TARGETING:")
    d = data['wrongful_detention']
    print(f"  {'wrongful_detention':<28} {d['count']:>10} {'(' + str(d['us_citizens']) + ' US citizens)':>35}")
    d = data['wrongful_deportation']
    print(f"  {'wrongful_deportation':<28} {d['count']:>10}")

    # Attacks on agents
    print("\nATTACKS ON AGENTS:")
    d = data['shooting_at_agent']
    print(f"  {'shooting_at_agent':<28} {d['count']:>10}")

    # Unknown
    if data['unknown']['count'] > 0:
        print("\nUNCATEGORIZED:")
        d = data['unknown']
        print(f"  {'unknown':<28} {d['count']:>10}")

    print("-" * 90)

    # Summary totals
    total_incidents = sum(d['count'] for d in data.values())
    total_deaths = (data['death_in_custody']['count'] +
                   data['death_during_enforcement']['count'] +
                   data['shooting_fatal']['count'])
    total_raids = (data['mass_raid_workplace']['count'] +
                  data['mass_raid_community']['count'] +
                  data['mass_raid_targeted']['count'])
    total_raid_arrests = (data['mass_raid_workplace']['total_arrested'] +
                         data['mass_raid_community']['total_arrested'] +
                         data['mass_raid_targeted']['total_arrested'])

    print(f"\nTOTALS:")
    print(f"  Enforcement incidents (granular): {total_incidents}")
    print(f"  Total deaths: {total_deaths}")
    print(f"  Total mass raids: {total_raids} ({total_raid_arrests} arrested)")
    print(f"  Wrongful detentions: {data['wrongful_detention']['count']}")

    return data


def export_enforcement_incidents_csv():
    """Export enforcement incidents to CSV with granularity."""
    enforcement_incidents = get_enforcement_incidents()

    rows = []
    for incident in enforcement_incidents:
        rows.append({
            'id': incident.get('id'),
            'date': incident.get('date'),
            'state': incident.get('state'),
            'city': incident.get('city'),
            'enforcement_granularity': infer_enforcement_granularity(incident),
            'incident_type': incident.get('incident_type'),
            'victim_category': incident.get('victim_category', infer_victim_category(incident)),
            'victim_name': incident.get('victim_name', ''),
            'victim_count': incident.get('victim_count', 1),
            'us_citizen': incident.get('us_citizen', ''),
            'outcome': incident.get('outcome', ''),
            'source_tier': incident.get('source_tier'),
            'source_url': incident.get('source_url', ''),
            'notes': incident.get('notes', ''),
        })

    df = pd.DataFrame(rows)
    df.to_csv('ENFORCEMENT_INCIDENTS_GRANULAR.csv', index=False)
    print(f"Saved {len(rows)} enforcement incidents to ENFORCEMENT_INCIDENTS_GRANULAR.csv")
    return df


if __name__ == '__main__':
    print_tier_summary()
    print_victim_category_summary()
    print_protest_granularity_summary()
    print_enforcement_granularity_summary()

    # Save to CSV
    df = create_summary_dataframe()
    df.to_csv('TIERED_INCIDENTS_DATABASE.csv', index=False)
    print(f"\nSaved to TIERED_INCIDENTS_DATABASE.csv")

    # Export protest incidents
    export_protest_incidents_csv()
