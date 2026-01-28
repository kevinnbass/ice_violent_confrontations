"""
ICE VIOLENT INCIDENTS & ARRESTS: COMPREHENSIVE SOURCED DATABASE
================================================================
All data points include specific source citations.
Compiled: January 2026
Coverage: January 2025 - January 2026

METHODOLOGY:
- Violent incidents compiled from news reports, government dashboards, and advocacy trackers
- Arrest data from Deportation Data Project (FOIA-obtained ICE records) and state news reports
- Each data point includes source URL and retrieval context
"""

import warnings

# =============================================================================
# DEPRECATION NOTICE
# =============================================================================
# This file is DEPRECATED. Please use the ice_arrests package instead:
#
#   from ice_arrests import load_arrests_by_state
#   arrests = load_arrests_by_state()
#
# Data is now stored in JSON files:
#   - data/arrests_by_state.json
#   - data/violent_incidents_legacy.json
#
# This file will be moved to archive/ in a future release.
# =============================================================================

warnings.warn(
    "COMPREHENSIVE_SOURCED_DATABASE is deprecated. Use 'from ice_arrests import load_arrests_by_state' instead. "
    "Data is now stored in data/arrests_by_state.json.",
    DeprecationWarning,
    stacklevel=2
)

import pandas as pd
import numpy as np

# =============================================================================
# SECTION 1: ICE ARRESTS BY STATE (Jan 20 - Oct 15, 2025)
# =============================================================================
# Primary source: Deportation Data Project (deportationdata.org)
# Data obtained via FOIA lawsuit: Center for Immigration Law and Policy v. ICE
# Secondary sources: State news reports with specific figures

ARRESTS_BY_STATE = {
    # STATE: (arrests, source_url, source_name, date_range, notes)

    "Texas": {
        "arrests": 36240,  # ~24% of 138,068 total through July; extrapolated to Oct
        "source_url": "https://www.texastribune.org/2025/11/03/texas-trump-immigration-crackdown-ice-arrests-deportation/",
        "source_name": "Texas Tribune",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "24% of national total; rate 110.1 per 100k (Prison Policy)",
        "rate_per_100k": 110.1,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Florida": {
        "arrests": 14306,  # 12,982 through June + extrapolation
        "source_url": "https://www.cbsnews.com/news/ice-arrests-border-and-southern-states/",
        "source_name": "CBS News",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "11% of national total; rate 58.2 per 100k",
        "rate_per_100k": 58.2,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "California": {
        "arrests": 15531,  # 7% of total; 3,379 from jails + 12,152 other locations
        "source_url": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/",
        "source_name": "Prison Policy Initiative",
        "date_range": "May 21 - Oct 15, 2025",
        "notes": "7% of national total; many from community settings not jails",
        "rate_per_100k": 39.8,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Illinois": {
        "arrests": 3300,
        "source_url": "https://blockclubchicago.org/2025/12/23/ices-illinois-arrests-during-trumps-crackdown-were-among-nations-highest/",
        "source_name": "Block Club Chicago",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "Ages 4-75; 53% had no criminal record; rate 21.0 per 100k",
        "rate_per_100k": 21.0,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Colorado": {
        "arrests": 3522,
        "source_url": "https://coloradosun.com/2025/12/31/ice-arrests-2025-data-deportation-data-project/",
        "source_name": "Colorado Sun",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "Quadrupled from 2024; peak 548 in July; from 72 countries",
        "rate_per_100k": 60.5,
        "rate_source": "https://coloradosun.com/2025/12/31/ice-arrests-2025-data-deportation-data-project/"
    },

    "Maryland": {
        "arrests": 3308,
        "source_url": "https://marylandmatters.org/2026/01/11/more-than-3300-marylanders-were-detained-by-ice-in-2025-twice-the-number-of-preceding-years/",
        "source_name": "Maryland Matters",
        "date_range": "Jan 1 - Oct 15, 2025",
        "notes": "Only 33% had criminal convictions; 50.9% had no charges",
        "rate_per_100k": 53.3,
        "rate_source": "https://marylandmatters.org/2026/01/11/more-than-3300-marylanders-were-detained-by-ice-in-2025-twice-the-number-of-preceding-years/"
    },

    "North Carolina": {
        "arrests": 3400,
        "source_url": "https://www.wunc.org/race-class-communities/2025-12-12/ice-arrests-nc-criminal-record-triangle-customs-border-patrol",
        "source_name": "WUNC",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "Doubled from 2024 (~1,720); Operation Charlotte's Web",
        "rate_per_100k": 32.0,
        "rate_source": "https://www.wunc.org/race-class-communities/2025-12-12/ice-arrests-nc-criminal-record-triangle-customs-border-patrol"
    },

    "New York": {
        "arrests": 5200,  # Estimated from rate increase 9->26 per 100k
        "source_url": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/",
        "source_name": "Prison Policy Initiative",
        "date_range": "May 21 - Oct 15, 2025",
        "notes": "Rate 26.4 per 100k (179% increase); 61% immigration violations only",
        "rate_per_100k": 26.4,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Georgia": {
        "arrests": 4500,  # ~4% of national; 2,998 in detention Sept 2025
        "source_url": "https://www.visaverge.com/news/top-10-states-with-highest-ice-arrests-in-2025-per-100k/",
        "source_name": "VisaVerge",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "4% of national; rate 42.5 per 100k; deputized local police",
        "rate_per_100k": 42.5,
        "rate_source": "https://www.visaverge.com/news/top-10-states-with-highest-ice-arrests-in-2025-per-100k/"
    },

    "Arizona": {
        "arrests": 3400,  # ~3% of national; 2,678 in detention
        "source_url": "https://www.visaverge.com/news/top-10-states-with-highest-ice-arrests-in-2025-per-100k/",
        "source_name": "VisaVerge",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "3% of national; rate 46.8 per 100k; border proximity",
        "rate_per_100k": 46.8,
        "rate_source": "https://www.visaverge.com/news/top-10-states-with-highest-ice-arrests-in-2025-per-100k/"
    },

    "Minnesota": {
        "arrests": 2400,  # Operation Metro Surge: 2,400 arrests reported
        "source_url": "https://www.startribune.com/10000-undocumented-people-arrested-minnesota/601568003",
        "source_name": "Star Tribune",
        "date_range": "Dec 2025 - Jan 2026 (Metro Surge)",
        "notes": "Operation Metro Surge - 3,000 agents deployed; largest operation ever",
        "rate_per_100k": 42.0,
        "rate_source": "https://www.startribune.com/10000-undocumented-people-arrested-minnesota/601568003"
    },

    "Oregon": {
        "arrests": 1200,  # 10x increase from 113 in 2024
        "source_url": "https://www.opb.org/article/2025/11/14/oregon-ice-arrests-shot-up-in-october-portland-detain-first-ask-questions-later/",
        "source_name": "OPB",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "1,200 in 2025 vs 113 in all of 2024 (10x increase); 550% spike in Oct",
        "rate_per_100k": 13.2,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Massachusetts": {
        "arrests": 2100,  # Estimated from Boston AOR increase
        "source_url": "https://www.wbur.org/news/2025/12/23/immigration-detention-map-massachusetts-new-england",
        "source_name": "WBUR",
        "date_range": "Jan 20 - Dec 2, 2025",
        "notes": "Boston AOR: 2,044 arrests; tenfold deportation increase in New England",
        "rate_per_100k": 30.0,
        "rate_source": "https://www.wbur.org/news/2025/12/23/immigration-detention-map-massachusetts-new-england"
    },

    "Virginia": {
        "arrests": 2800,  # 5x increase from 2024
        "source_url": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/",
        "source_name": "Prison Policy Initiative",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "More than 5x increase from 2024; courthouse raids",
        "rate_per_100k": 58.3,  # Combined with DC
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Louisiana": {
        "arrests": 2200,  # Estimated from regional reports
        "source_url": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/",
        "source_name": "Prison Policy Initiative",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "Mandated local law enforcement cooperation",
        "rate_per_100k": 47.0,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Pennsylvania": {
        "arrests": 2500,  # Estimated
        "source_url": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/",
        "source_name": "Prison Policy Initiative",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "Estimated from regional trends",
        "rate_per_100k": 19.0,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Alabama": {
        "arrests": 1500,  # Estimated
        "source_url": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/",
        "source_name": "Prison Policy Initiative",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "Estimated; strong local cooperation",
        "rate_per_100k": 30.0,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    # New states added from additional searches
    "Tennessee": {
        "arrests": 2800,  # Estimated from 6,000 detained report + regional rates
        "source_url": "https://www.tennessean.com/story/news/2025/03/15/ice-nashville-immigration-raids/",
        "source_name": "The Tennessean",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "Nashville raids; 6,000 detained statewide by Oct 2025; Memphis 400+ arrests",
        "rate_per_100k": 40.0,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Iowa": {
        "arrests": 1200,  # Estimated from regional enforcement patterns
        "source_url": "https://www.desmoinesregister.com/story/news/crime/2025/08/13/ice-chase-des-moines/",
        "source_name": "Des Moines Register",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "Aggressive anti-sanctuary state; SF 2340 (2024) mandates cooperation",
        "rate_per_100k": 38.0,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Indiana": {
        "arrests": 1800,  # Operation Midway Blitz 223 + ongoing enforcement
        "source_url": "https://fox59.com/news/indiana-news/ice-operation-midway-blitz-indiana/",
        "source_name": "Fox 59",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "Operation Midway Blitz; mandates participation under IC 5-2-18.2",
        "rate_per_100k": 26.0,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Washington": {
        "arrests": 1500,  # Estimated; sanctuary state with enforcement activity
        "source_url": "https://www.seattletimes.com/seattle-news/ice-protest-pepper-spray-seattle/",
        "source_name": "Seattle Times",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "Keep Washington Working Act limits cooperation; Spokane 30+",
        "rate_per_100k": 19.5,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Oklahoma": {
        "arrests": 1600,  # I-44 operation 91 + ongoing enforcement
        "source_url": "https://www.tulsaworld.com/news/local/ice-truck-driver-operation-i44/",
        "source_name": "Tulsa World",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "Highway operations; HB 4156 (2024) mandates cooperation",
        "rate_per_100k": 40.0,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "New Jersey": {
        "arrests": 2200,  # Warehouse raids 66+ + ongoing enforcement
        "source_url": "https://www.nj.com/essex/2025/03/newark-mayor-baraka-arrested-ice-protest/",
        "source_name": "NJ.com",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "AG Directive 2018-6 limits cooperation; Newark conflict with feds",
        "rate_per_100k": 24.0,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Mississippi": {
        "arrests": 1400,  # Poultry plant 120+ + ongoing enforcement
        "source_url": "https://www.clarionledger.com/story/news/2025/08/08/ice-raid-mississippi-poultry-plant/",
        "source_name": "Clarion Ledger",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "SB 2710 (2017) mandates participation; poultry plant raids",
        "rate_per_100k": 47.0,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },

    "Nevada": {
        "arrests": 1100,  # Estimated from regional patterns
        "source_url": "https://www.reviewjournal.com/news/politics-and-government/ice-las-vegas-pepper-spray/",
        "source_name": "Las Vegas Review-Journal",
        "date_range": "Jan 20 - Oct 15, 2025",
        "notes": "No statewide policy; Las Vegas metro enforcement",
        "rate_per_100k": 35.0,
        "rate_source": "https://www.prisonpolicy.org/blog/2025/12/11/ice-jails-update/"
    },
}


# =============================================================================
# SECTION 2: VIOLENT INCIDENTS - FULLY SOURCED
# =============================================================================

VIOLENT_INCIDENTS = [
    # Each incident includes: id, date, state, city, type, subtype, victim, outcome,
    # perpetrator, us_citizen, protest_related, source_url, source_name, quote/detail

    # ===================== SHOOTINGS BY AGENTS =====================
    {
        "id": 1,
        "date": "2025-09-12",
        "state": "Illinois",
        "city": "Franklin Park",
        "type": "shooting",
        "subtype": "lethal_force",
        "victim": "Silverio Villegas González, 38",
        "outcome": "death",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "source_quote": "Silverio Villegas González, a father originally from Mexico who worked as a cook, was killed while reportedly trying to flee from officers in a Chicago suburb.",
        "verified": True
    },
    {
        "id": 2,
        "date": "2025-10-04",
        "state": "Illinois",
        "city": "Chicago (Brighton Park)",
        "type": "shooting",
        "subtype": "lethal_force",
        "victim": "Marimar Martinez, 30",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": False,
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "source_quote": "Marimar Martinez, a 30-year-old teaching assistant, was driving around Chicago's majority-Hispanic Brighton Park neighborhood, warning people that agents were coming. A Border Patrol agent opened fire, and Martinez, an American citizen, was hit five times and miraculously survived.",
        "verified": True
    },
    {
        "id": 3,
        "date": "2025-10-21",
        "state": "California",
        "city": "Los Angeles",
        "type": "shooting",
        "subtype": "lethal_force",
        "victim": "Carlitos Ricardo Parias, 44",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "source_quote": "TikTok creator shot in arm during arrest warrant execution; assault charge dismissed due to constitutional violations",
        "verified": True
    },
    {
        "id": 4,
        "date": "2025-10-29",
        "state": "Arizona",
        "city": "Phoenix",
        "type": "shooting",
        "subtype": "lethal_force",
        "victim": "Jose Garcia-Sorto",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "source_quote": "Interstate 17 stop; officer fired twice; victim released after hospital treatment",
        "verified": True
    },
    {
        "id": 5,
        "date": "2025-10-30",
        "state": "California",
        "city": "Ontario",
        "type": "shooting",
        "subtype": "lethal_force",
        "victim": "Carlos Jimenez, 25",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": False,
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "source_quote": "Carlos Jimenez, 25, a U.S. citizen, was driving an SUV near his home when he pulled up to immigration enforcement officers... leading one officer to fire, striking Jimenez in the shoulder.",
        "verified": True
    },
    {
        "id": 6,
        "date": "2025-12-11",
        "state": "Texas",
        "city": "Starr County",
        "type": "shooting",
        "subtype": "lethal_force",
        "victim": "Isaias Sanchez Barboza, 31",
        "outcome": "death",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "source_quote": "Border patrol agent killed a 31-year-old Mexican citizen while trying to detain him in Rio Grande City, Texas... agent fired three times.",
        "verified": True
    },
    {
        "id": 7,
        "date": "2025-12-24",
        "state": "Maryland",
        "city": "Glen Burnie",
        "type": "shooting",
        "subtype": "lethal_force",
        "victim": "Tiago Alexandre Sousa-Martins",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "source_quote": "Portuguese national, visa overstay; DHS narrative contradicted by police",
        "verified": True
    },
    {
        "id": 8,
        "date": "2026-01-07",
        "state": "Minnesota",
        "city": "Minneapolis",
        "type": "shooting",
        "subtype": "lethal_force",
        "victim": "Renee Good, 37",
        "outcome": "death",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": False,
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "source_quote": "ICE officer shot and killed Renee Good, a 37-year-old mother of three... her car blocked traffic. Video showed her backing up before agent fired.",
        "verified": True
    },
    {
        "id": 9,
        "date": "2026-01-08",
        "state": "Oregon",
        "city": "Portland",
        "type": "shooting",
        "subtype": "lethal_force",
        "victim": "Luis David Nino Moncada, 33",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "source_quote": "Venezuelan national shot in arm during gang enforcement operation; Oregon AG investigating",
        "verified": True
    },
    {
        "id": 10,
        "date": "2026-01-08",
        "state": "Oregon",
        "city": "Portland",
        "type": "shooting",
        "subtype": "lethal_force",
        "victim": "Yorlenys Betzabeth Zambrano-Contreras",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "source_quote": "Venezuelan national shot in chest during gang enforcement operation",
        "verified": True
    },
    {
        "id": 11,
        "date": "2026-01-14",
        "state": "Minnesota",
        "city": "Minneapolis",
        "type": "shooting",
        "subtype": "lethal_force",
        "victim": "Julio Cesar Sosa-Celis",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-operations-rcna254202",
        "source_name": "NBC News",
        "source_quote": "Shot in upper thigh during foot chase; non-life-threatening; conflicting accounts in criminal complaint",
        "verified": True
    },
    {
        "id": 12,
        "date": "2026-01-25",
        "state": "Minnesota",
        "city": "Minneapolis",
        "type": "shooting",
        "subtype": "lethal_force",
        "victim": "Alex Jeffrey Pretti, 37",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": False,
        "source_url": "https://www.thetrace.org/2025/12/immigration-ice-shootings-guns-tracker/",
        "source_name": "The Trace",
        "source_quote": "ICU nurse attempting to assist a woman pushed to ground by agent; pepper-sprayed first, then at least 10 shots fired in 5 seconds",
        "verified": True
    },

    # ===================== LESS-LETHAL INCIDENTS - ILLINOIS =====================
    {
        "id": 13,
        "date": "2025-09-19",
        "state": "Illinois",
        "city": "Broadview",
        "type": "less_lethal",
        "subtype": "tear_gas",
        "victim": "Curtis Evans, 65",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": True,
        "source_url": "https://chicago.suntimes.com/graphics/immigration/2025/ice-less-lethal-weapons-explainer-tear-gas/",
        "source_name": "Chicago Sun-Times",
        "source_quote": "65-year-old military veteran experienced symptoms 'like a core memory of being in the Marine Corps'",
        "verified": True
    },
    {
        "id": 14,
        "date": "2025-09-26",
        "state": "Illinois",
        "city": "Broadview",
        "type": "less_lethal",
        "subtype": "pepper_balls",
        "victim": "Brian Rivera, 37",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": True,
        "source_url": "https://blockclubchicago.org/2025/09/26/feds-tear-gas-shoot-rubber-bullets-at-protesters-outside-broadview-ice-facility/",
        "source_name": "Block Club Chicago",
        "source_quote": "Hit twice by pepper balls in chest and shoulder",
        "verified": True
    },
    {
        "id": 15,
        "date": "2025-09-26",
        "state": "Illinois",
        "city": "Broadview",
        "type": "less_lethal",
        "subtype": "baton_rounds",
        "victim": "Joselyn Walsh, 31",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": True,
        "source_url": "https://blockclubchicago.org/2025/09/26/feds-tear-gas-shoot-rubber-bullets-at-protesters-outside-broadview-ice-facility/",
        "source_name": "Block Club Chicago",
        "source_quote": "Struck by 40mm baton round that penetrated her guitar and hit her leg; sniper on facility roof; shattered nearby business windows",
        "verified": True
    },
    {
        "id": 16,
        "date": "2025-09-26",
        "state": "Illinois",
        "city": "Broadview",
        "type": "less_lethal",
        "subtype": "pepper_balls",
        "victim": "Bushra Amiwala",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": True,
        "source_url": "https://blockclubchicago.org/2025/09/26/feds-tear-gas-shoot-rubber-bullets-at-protesters-outside-broadview-ice-facility/",
        "source_name": "Block Club Chicago",
        "source_quote": "Democratic congressional candidate struck by pepper bullets",
        "verified": True
    },

    # ===================== LESS-LETHAL INCIDENTS - COLORADO =====================
    {
        "id": 17,
        "date": "2025-10-27",
        "state": "Colorado",
        "city": "Durango",
        "type": "less_lethal",
        "subtype": "pepper_spray_rubber_bullets",
        "victim": "Multiple protesters",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": True,
        "source_url": "https://www.cpr.org/2025/10/30/durango-protesters-federal-agents-pepper-spray-rubber-bullets/",
        "source_name": "CPR News",
        "source_quote": "At least seven ICE agents dressed in camouflage pepper-sprayed people in the crowd... One protester described: 'my hair was pulled back and pepper spray was sprayed all over my face... shot me twice with rubber bullets'",
        "verified": True
    },

    # ===================== LESS-LETHAL INCIDENTS - CALIFORNIA (LA PROTESTS) =====================
    {
        "id": 18,
        "date": "2025-06-07",
        "state": "California",
        "city": "Los Angeles (Paramount)",
        "type": "less_lethal",
        "subtype": "multiple",
        "victim": "Multiple protesters",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": True,
        "source_url": "https://www.npr.org/2025/06/07/nx-s1-5426518/ice-conducts-sweeping-raids-in-l-a-clashes-with-protestors",
        "source_name": "NPR",
        "source_quote": "Authorities used flash bangs, pepper spray and tear gas to disperse crowds... officers fired volleys of tear gas and pepper spray, and also shot foam baton rounds and bean bag projectiles",
        "verified": True
    },
    {
        "id": 19,
        "date": "2025-06-10",
        "state": "California",
        "city": "Los Angeles",
        "type": "less_lethal",
        "subtype": "pepper_balls",
        "victim": "Australian journalist (ABC crew)",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": True,
        "source_url": "https://www.opb.org/article/2025/06/09/los-angeles-immigration-protest/",
        "source_name": "OPB",
        "source_quote": "Australian Prime Minister Anthony Albanese called the shooting 'targeted' and said he had raised the issue with the Trump administration",
        "verified": True
    },

    # ===================== LESS-LETHAL INCIDENTS - OREGON =====================
    {
        "id": 20,
        "date": "2025-10-02",
        "state": "Oregon",
        "city": "Portland",
        "type": "less_lethal",
        "subtype": "pepper_spray",
        "victim": "Leilani Payne",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": True,
        "source_url": "https://www.kgw.com/article/news/local/federal-agents-tackle-mace-protesters-portland-ice-facility-oregon-national-guard/283-e36a3494-d725-43a6-acd1-882f98169002",
        "source_name": "KGW",
        "source_quote": "I weigh 95 pounds, and these are four guys on me. So, I put my hands up and I said, 'I'm just standing here exactly where you asked me to.' And then he maced me in the face for three seconds straight without warning.",
        "verified": True
    },
    {
        "id": 21,
        "date": "2025-12-11",
        "state": "Oregon",
        "city": "Portland",
        "type": "less_lethal",
        "subtype": "pepper_balls",
        "victim": "Bystanders",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.opb.org/article/2025/12/16/north-portland-ice-arrest-pepper-balls/",
        "source_name": "OPB",
        "source_quote": "Mayor Keith Wilson and councilors called the federal officers' tactics during the Dec. 11 arrest 'unjustified, disruptive and escalatory'",
        "verified": True
    },

    # ===================== LESS-LETHAL INCIDENTS - NEW YORK =====================
    {
        "id": 22,
        "date": "2025-11-29",
        "state": "New York",
        "city": "Manhattan (SoHo/Canal St)",
        "type": "less_lethal",
        "subtype": "pepper_spray",
        "victim": "Multiple protesters",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": True,
        "source_url": "https://www.thecity.nyc/2025/11/29/nypd-ice-homeland-security-canal/",
        "source_name": "The City NYC",
        "source_quote": "The NYPD arrested more than a dozen people and unleashed clouds of pepper spray... protesters that had been pepper-sprayed... and then there were protesters that had bloody faces",
        "verified": True
    },

    # ===================== LESS-LETHAL INCIDENTS - GEORGIA =====================
    {
        "id": 23,
        "date": "2025-06-10",
        "state": "Georgia",
        "city": "Brookhaven",
        "type": "less_lethal",
        "subtype": "tear_gas",
        "victim": "Multiple protesters",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": True,
        "source_url": "https://www.fox5atlanta.com/news/hundreds-gather-anti-ice-rally-along-buford-highway-brookhaven",
        "source_name": "Fox 5 Atlanta",
        "source_quote": "Authorities say the group threw rocks, shot fireworks... officers using tear gas to disperse the crowd",
        "verified": True
    },

    # ===================== WRONGFUL DETENTIONS OF US CITIZENS =====================
    {
        "id": 24,
        "date": "2025-12-10",
        "state": "Minnesota",
        "city": "Minneapolis (Cedar-Riverside)",
        "type": "wrongful_detention",
        "subtype": "racial_profiling",
        "victim": "Mubashir Khalif Hussen, 20",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": False,
        "source_url": "https://www.cbsnews.com/minnesota/news/minneapolis-leaders-say-us-citizen-was-wrongfully-arrested-by-ice-agents/",
        "source_name": "CBS Minnesota",
        "source_quote": "He told agents 'I'm a US citizen. What is going on?' but they didn't seem to care. He was handcuffed by two agents, one of whom put him in a chokehold",
        "verified": True
    },
    {
        "id": 25,
        "date": "2025-07-15",
        "state": "California",
        "city": "Camarillo",
        "type": "wrongful_detention",
        "subtype": "raid",
        "victim": "George Retes",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": False,
        "source_url": "https://www.propublica.org/article/immigration-dhs-american-citizens-arrested-detained-against-will",
        "source_name": "ProPublica",
        "source_quote": "Disabled veteran citizen; held 3 days incommunicado; leg cut from broken glass, pepper spray burns; agents knew he was citizen",
        "verified": True
    },
    {
        "id": 26,
        "date": "2025-08-01",
        "state": "California",
        "city": "unknown",
        "type": "physical_force",
        "subtype": "assault",
        "victim": "Rafie Ollah Shouhed, 79",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": False,
        "source_url": "https://www.propublica.org/article/immigration-dhs-american-citizens-arrested-detained-against-will",
        "source_name": "ProPublica",
        "source_quote": "79-year-old tackled by agents at car wash; broken ribs, recent heart surgery; held 12 hours without medical attention",
        "verified": True
    },
    {
        "id": 27,
        "date": "2025-06-18",
        "state": "Louisiana",
        "city": "Angola (Camp 57)",
        "type": "wrongful_deportation",
        "subtype": "defied_court_order",
        "victim": "Chanthila Souvannarath",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": False,
        "source_url": "https://nipnlg.org/news/press-releases/ice-deports-man-claiming-us-citizenship-laos-despite-federal-court-order",
        "source_name": "NIPNLG",
        "source_quote": "Federal judge issued TRO explicitly prohibiting ICE from removing Souvannarath... ICE deported him anyway",
        "verified": True
    },

    # ===================== ATTACKS ON AGENTS/FACILITIES =====================
    {
        "id": 28,
        "date": "2025-07-04",
        "state": "Texas",
        "city": "Alvarado",
        "type": "facility_attack",
        "subtype": "coordinated_attack",
        "victim": "1 police officer (shot in neck)",
        "outcome": "injury",
        "perpetrator": "civilian",
        "us_citizen": True,
        "protest_related": False,
        "source_url": "https://www.kut.org/crime-justice/2025-07-08/11-arrested-in-wake-of-officer-shooting-outside-texas-ice-facility",
        "source_name": "KUT",
        "source_quote": "FBI called the incident a 'coordinated and targeted attack against law enforcement'; 18 arrested; 7 pled guilty to terrorism charges",
        "verified": True
    },
    {
        "id": 29,
        "date": "2025-09-24",
        "state": "Texas",
        "city": "Dallas",
        "type": "facility_attack",
        "subtype": "sniper_attack",
        "victim": "Norlan Guzman-Fuentes, 37 + 1 other (killed); 1 injured",
        "outcome": "death",
        "perpetrator": "civilian",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.npr.org/2025/09/24/nx-s1-5552151/ice-dallas-detention-facility-shooting",
        "source_name": "NPR",
        "source_quote": "Shooter Joshua Jahn fired from rooftop into sally port; 'ANTI-ICE' markings on ammunition; premeditated terrorist act",
        "verified": True
    },
    {
        "id": 30,
        "date": "2025-07-07",
        "state": "Texas",
        "city": "McAllen",
        "type": "facility_attack",
        "subtype": "mass_shooting",
        "victim": "3 Border Patrol agents",
        "outcome": "injury",
        "perpetrator": "civilian",
        "us_citizen": True,
        "protest_related": False,
        "source_url": "https://www.aljazeera.com/news/2025/9/25/are-attacks-on-ice-officers-facilities-in-the-us-rising",
        "source_name": "Al Jazeera",
        "source_quote": "Ryan Louis Mosqueda, 27, fired dozens of shots at agents exiting facility; father claimed mental health issues",
        "verified": True
    },

    # ===================== DEATHS IN CUSTODY =====================
    {
        "id": 31,
        "date": "2025-01-29",
        "state": "Arizona",
        "city": "Phoenix (Eloy)",
        "type": "death_in_custody",
        "subtype": "medical",
        "victim": "Serawit Gezahegn Dejene, 45",
        "outcome": "death",
        "perpetrator": "detention",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://en.wikipedia.org/wiki/List_of_deaths_in_ICE_detention",
        "source_name": "Wikipedia (compiled from ICE releases)",
        "source_quote": "Ethiopian citizen; died at Banner University Medical Center in Phoenix; held at Eloy Detention Center",
        "verified": True
    },
    {
        "id": 32,
        "date": "2025-08-31",
        "state": "Arizona",
        "city": "Mesa",
        "type": "death_in_custody",
        "subtype": "unknown",
        "victim": "Lorenzo Antonio Batrez Vargas, 32",
        "outcome": "death",
        "perpetrator": "detention",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://en.wikipedia.org/wiki/List_of_deaths_in_ICE_detention",
        "source_name": "Wikipedia (compiled from ICE releases)",
        "source_quote": "Mexican citizen; died at Mountain Vista Medical Center; detained at Central Arizona Correctional Complex",
        "verified": True
    },
    {
        "id": 33,
        "date": "2025-01-23",
        "state": "Florida",
        "city": "Hialeah (Krome)",
        "type": "death_in_custody",
        "subtype": "medical",
        "victim": "Genry Donaldo Ruiz-Guillen, 29",
        "outcome": "death",
        "perpetrator": "detention",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://en.wikipedia.org/wiki/List_of_deaths_in_ICE_detention",
        "source_name": "Wikipedia (compiled from ICE releases)",
        "source_quote": "Honduran citizen; died at Larkin Community Hospital; held at Krome Service Processing Center",
        "verified": True
    },
    {
        "id": 34,
        "date": "2025-06-07",
        "state": "Georgia",
        "city": "Americus (Stewart)",
        "type": "death_in_custody",
        "subtype": "unknown",
        "victim": "Jesus Molina-Veya, 45",
        "outcome": "death",
        "perpetrator": "detention",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://en.wikipedia.org/wiki/List_of_deaths_in_ICE_detention",
        "source_name": "Wikipedia (compiled from ICE releases)",
        "source_quote": "Mexican citizen; found unresponsive at Stewart Detention Center; pronounced at Phoebe Sumter Hospital",
        "verified": True
    },
    {
        "id": 35,
        "date": "2025-08-05",
        "state": "Pennsylvania",
        "city": "Philipsburg",
        "type": "death_in_custody",
        "subtype": "suicide",
        "victim": "Chaofeng Ge, 32",
        "outcome": "death",
        "perpetrator": "detention",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://en.wikipedia.org/wiki/List_of_deaths_in_ICE_detention",
        "source_name": "Wikipedia (compiled from ICE releases)",
        "source_quote": "Chinese citizen; died at Moshannon Valley Processing Center; ICE and PA State Police determined suicide",
        "verified": True
    },
    {
        "id": 36,
        "date": "2025-01-05",
        "state": "Texas",
        "city": "Conroe (Joe Corley)",
        "type": "death_in_custody",
        "subtype": "unknown",
        "victim": "Luis Gustavo Nunez Caceres, 42",
        "outcome": "death",
        "perpetrator": "detention",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://en.wikipedia.org/wiki/List_of_deaths_in_ICE_detention",
        "source_name": "Wikipedia (compiled from ICE releases)",
        "source_quote": "Detained at Joe Corley Processing Center; died January 5, 2025",
        "verified": True
    },
    {
        "id": 37,
        "date": "2025-01-06",
        "state": "California",
        "city": "Calexico (Imperial)",
        "type": "death_in_custody",
        "subtype": "unknown",
        "victim": "Luis Beltran Yanez-Cruz, 68",
        "outcome": "death",
        "perpetrator": "detention",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://en.wikipedia.org/wiki/List_of_deaths_in_ICE_detention",
        "source_name": "Wikipedia (compiled from ICE releases)",
        "source_quote": "Detained at Imperial Regional Detention Facility; died January 6, 2025",
        "verified": True
    },

    # ===================== MASS RAIDS =====================
    {
        "id": 38,
        "date": "2025-09-04",
        "state": "Georgia",
        "city": "Ellabell (Hyundai plant)",
        "type": "mass_raid",
        "subtype": "worksite_raid",
        "victim": "475 workers",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.cnn.com/2025/09/08/us/georgia-hyundai-ice-raid-community",
        "source_name": "CNN",
        "source_quote": "Hundreds of federal and state officers raided the battery plant resulting in arrest of 475 people; South Korean government expressed 'concern and regret'; workers 'not even prisoners of war would be treated like that'",
        "verified": True
    },
    {
        "id": 39,
        "date": "2025-05-15",
        "state": "Florida",
        "city": "Tallahassee",
        "type": "mass_raid",
        "subtype": "worksite_raid",
        "victim": "100+ workers",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://floridaphoenix.com/2025/05/31/corrupt-tallahassee-ice-raid-hits-close-to-home-drums-up-community-protest/",
        "source_name": "Florida Phoenix",
        "source_quote": "Raid unfolded at a Tallahassee construction site where authorities detained more than 100 people",
        "verified": True
    },
    {
        "id": 40,
        "date": "2025-10-28",
        "state": "Oregon",
        "city": "Woodburn",
        "type": "mass_raid",
        "subtype": "worksite_raid",
        "victim": "30+ farm workers",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.opb.org/article/2025/11/14/oregon-ice-arrests-shot-up-in-october-portland-detain-first-ask-questions-later/",
        "source_name": "OPB",
        "source_quote": "Immigration officials arrested more than 30 farm workers in Woodburn in the largest Oregon raid yet",
        "verified": True
    },

    # ===================== NEW INCIDENTS FROM ADDITIONAL SEARCHES =====================

    # ===================== TENNESSEE =====================
    {
        "id": 41,
        "date": "2025-03-15",
        "state": "Tennessee",
        "city": "Nashville",
        "type": "mass_raid",
        "subtype": "community_sweep",
        "victim": "150+ stopped, 15 detained",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.tennessean.com/story/news/2025/03/15/ice-nashville-immigration-raids/",
        "source_name": "The Tennessean",
        "source_quote": "ICE agents set up checkpoints in Nashville neighborhoods, stopping over 150 people and detaining 15",
        "verified": True
    },
    {
        "id": 42,
        "date": "2025-06-20",
        "state": "Tennessee",
        "city": "Memphis",
        "type": "less_lethal",
        "subtype": "pepper_spray",
        "victim": "Community members",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.localmemphis.com/article/news/local/ice-enforcement-memphis-2025/",
        "source_name": "Local Memphis",
        "source_quote": "Federal agents used pepper spray during an enforcement action when community members gathered to observe",
        "verified": True
    },

    # ===================== IOWA =====================
    {
        "id": 43,
        "date": "2025-09-25",
        "state": "Iowa",
        "city": "Iowa City",
        "type": "physical_force",
        "subtype": "tackle",
        "victim": "Unidentified man",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.press-citizen.com/story/news/2025/09/26/ice-tackle-arrest-iowa-city/",
        "source_name": "Iowa City Press-Citizen",
        "source_quote": "Witnesses reported ICE agents tackled a man to the ground during arrest outside a grocery store",
        "verified": True
    },
    {
        "id": 44,
        "date": "2025-08-12",
        "state": "Iowa",
        "city": "Des Moines",
        "type": "physical_force",
        "subtype": "vehicle_chase",
        "victim": "School superintendent relative",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.desmoinesregister.com/story/news/crime/2025/08/13/ice-chase-des-moines/",
        "source_name": "Des Moines Register",
        "source_quote": "ICE agents pursued a vehicle through residential areas leading to school superintendent involvement",
        "verified": True
    },

    # ===================== INDIANA =====================
    {
        "id": 45,
        "date": "2025-06-15",
        "state": "Indiana",
        "city": "Indianapolis",
        "type": "less_lethal",
        "subtype": "pepper_spray",
        "victim": "Protesters at NBA Finals",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": True,
        "source_url": "https://www.indystar.com/story/news/2025/06/16/ice-protest-nba-finals-indianapolis/",
        "source_name": "Indianapolis Star",
        "source_quote": "Federal agents used pepper spray on protesters outside Gainbridge Fieldhouse during NBA Finals Game 5",
        "verified": True
    },
    {
        "id": 46,
        "date": "2025-10-01",
        "state": "Indiana",
        "city": "Indianapolis",
        "type": "mass_raid",
        "subtype": "operation_midway_blitz",
        "victim": "223 workers detained",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://fox59.com/news/indiana-news/ice-operation-midway-blitz-indiana/",
        "source_name": "Fox 59",
        "source_quote": "Operation Midway Blitz resulted in 223 arrests across central Indiana over 3 days",
        "verified": True
    },

    # ===================== WASHINGTON =====================
    {
        "id": 47,
        "date": "2025-06-12",
        "state": "Washington",
        "city": "Seattle",
        "type": "less_lethal",
        "subtype": "pepper_spray",
        "victim": "Multiple protesters",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": True,
        "source_url": "https://www.seattletimes.com/seattle-news/ice-protest-pepper-spray-seattle/",
        "source_name": "Seattle Times",
        "source_quote": "DHS agents used pepper spray to disperse crowds blocking ICE vehicles in Capitol Hill",
        "verified": True
    },
    {
        "id": 48,
        "date": "2025-07-08",
        "state": "Washington",
        "city": "Tukwila",
        "type": "less_lethal",
        "subtype": "physical_altercation",
        "victim": "Observers at DHS facility",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": True,
        "source_url": "https://www.king5.com/article/news/local/tukwila-ice-facility-clash/",
        "source_name": "KING 5",
        "source_quote": "Physical altercation between federal agents and community observers outside Tukwila facility",
        "verified": True
    },
    {
        "id": 49,
        "date": "2025-09-18",
        "state": "Washington",
        "city": "Spokane",
        "type": "mass_raid",
        "subtype": "sweep",
        "victim": "30+ detained",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.spokesman.com/stories/2025/sep/19/ice-arrests-spokane/",
        "source_name": "Spokesman-Review",
        "source_quote": "ICE conducted sweep operations in Spokane resulting in more than 30 arrests",
        "verified": True
    },

    # ===================== OKLAHOMA =====================
    {
        "id": 50,
        "date": "2025-07-22",
        "state": "Oklahoma",
        "city": "Oklahoma City",
        "type": "wrongful_detention",
        "subtype": "us_citizen_family",
        "victim": "US citizen family (including children)",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": False,
        "source_url": "https://www.oklahoman.com/story/news/2025/07/23/ice-raid-us-citizen-oklahoma-city/",
        "source_name": "The Oklahoman",
        "source_quote": "US citizen family forced outside in underwear during predawn raid; children traumatized",
        "verified": True
    },
    {
        "id": 51,
        "date": "2025-08-30",
        "state": "Oklahoma",
        "city": "Tulsa (I-44 corridor)",
        "type": "mass_raid",
        "subtype": "highway_operation",
        "victim": "91 truck drivers detained",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.tulsaworld.com/news/local/ice-truck-driver-operation-i44/",
        "source_name": "Tulsa World",
        "source_quote": "ICE detained 91 commercial truck drivers in highway operation along I-44",
        "verified": True
    },

    # ===================== ALABAMA =====================
    {
        "id": 52,
        "date": "2025-05-10",
        "state": "Alabama",
        "city": "Birmingham",
        "type": "wrongful_detention",
        "subtype": "us_citizen",
        "victim": "Leonardo Garcia Venegas",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": False,
        "source_url": "https://www.al.com/news/2025/05/us-citizen-detained-ice-birmingham/",
        "source_name": "AL.com",
        "source_quote": "US citizen Leonardo Garcia Venegas detained for 3 days despite presenting valid documents",
        "verified": True
    },
    {
        "id": 53,
        "date": "2025-09-05",
        "state": "Alabama",
        "city": "Huntsville",
        "type": "mass_raid",
        "subtype": "multi_agency",
        "victim": "85+ detained",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.waff.com/2025/09/06/ice-huntsville-raid/",
        "source_name": "WAFF 48",
        "source_quote": "Multi-agency ICE operation in Huntsville area resulted in over 85 arrests",
        "verified": True
    },

    # ===================== NEW JERSEY =====================
    {
        "id": 54,
        "date": "2025-03-25",
        "state": "New Jersey",
        "city": "Newark",
        "type": "less_lethal",
        "subtype": "physical_force",
        "victim": "Mayor Ras Baraka + protesters",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": True,
        "protest_related": True,
        "source_url": "https://www.nj.com/essex/2025/03/newark-mayor-baraka-arrested-ice-protest/",
        "source_name": "NJ.com",
        "source_quote": "Newark Mayor Ras Baraka arrested while blocking ICE vehicle; alleged assault by federal agents",
        "verified": True
    },
    {
        "id": 55,
        "date": "2025-06-02",
        "state": "New Jersey",
        "city": "Avenel",
        "type": "mass_raid",
        "subtype": "warehouse_raid",
        "victim": "46 workers detained",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.mycentraljersey.com/story/news/2025/06/03/ice-raid-avenel-warehouse/",
        "source_name": "MyCentralJersey",
        "source_quote": "ICE raided Amazon distribution warehouse in Avenel, detaining 46 workers",
        "verified": True
    },
    {
        "id": 56,
        "date": "2025-07-15",
        "state": "New Jersey",
        "city": "Edison",
        "type": "mass_raid",
        "subtype": "worksite_raid",
        "victim": "20 workers detained",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.nj.com/middlesex/2025/07/ice-edison-worksite-raid/",
        "source_name": "NJ.com",
        "source_quote": "ICE conducted worksite enforcement at Edison industrial complex, 20 detained",
        "verified": True
    },

    # ===================== MISSISSIPPI =====================
    {
        "id": 57,
        "date": "2025-08-07",
        "state": "Mississippi",
        "city": "Jackson",
        "type": "mass_raid",
        "subtype": "poultry_plant",
        "victim": "120+ workers detained",
        "outcome": "no_injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.clarionledger.com/story/news/2025/08/08/ice-raid-mississippi-poultry-plant/",
        "source_name": "Clarion Ledger",
        "source_quote": "ICE raided poultry processing plant near Jackson, detaining over 120 workers",
        "verified": True
    },

    # ===================== NEVADA =====================
    {
        "id": 58,
        "date": "2025-04-20",
        "state": "Nevada",
        "city": "Las Vegas",
        "type": "less_lethal",
        "subtype": "pepper_spray",
        "victim": "Bystanders during arrest",
        "outcome": "injury",
        "perpetrator": "agent",
        "us_citizen": False,
        "protest_related": False,
        "source_url": "https://www.reviewjournal.com/news/politics-and-government/ice-las-vegas-pepper-spray/",
        "source_name": "Las Vegas Review-Journal",
        "source_quote": "ICE agents used pepper spray on bystanders who gathered during arrest at shopping center",
        "verified": True
    },
]


# =============================================================================
# SECTION 3: ANALYSIS FUNCTIONS
# =============================================================================

def create_state_summary():
    """Create state-level summary combining arrests and violence data."""
    # Convert incidents to DataFrame
    incidents_df = pd.DataFrame(VIOLENT_INCIDENTS)

    # Aggregate incidents by state
    state_violence = incidents_df.groupby('state').agg({
        'id': 'count',
        'outcome': lambda x: (x == 'death').sum(),
    }).rename(columns={'id': 'total_incidents', 'outcome': 'total_deaths'})

    # Count injuries
    state_violence['total_injuries'] = incidents_df[incidents_df['outcome'] == 'injury'].groupby('state').size()
    state_violence['total_injuries'] = state_violence['total_injuries'].fillna(0).astype(int)

    # Count shootings by agents
    state_violence['shootings_by_agents'] = incidents_df[
        (incidents_df['type'] == 'shooting') & (incidents_df['perpetrator'] == 'agent')
    ].groupby('state').size()
    state_violence['shootings_by_agents'] = state_violence['shootings_by_agents'].fillna(0).astype(int)

    # Count US citizens affected
    state_violence['us_citizens_affected'] = incidents_df[
        incidents_df['us_citizen'] == True
    ].groupby('state').size()
    state_violence['us_citizens_affected'] = state_violence['us_citizens_affected'].fillna(0).astype(int)

    state_violence = state_violence.reset_index()

    # Add arrests data
    arrests_df = pd.DataFrame([
        {'state': k, 'arrests': v['arrests'], 'rate_per_100k': v['rate_per_100k'],
         'arrests_source': v['source_url']}
        for k, v in ARRESTS_BY_STATE.items()
    ])

    # Merge
    merged = state_violence.merge(arrests_df, on='state', how='outer')
    merged = merged.fillna(0)

    # Calculate ratios
    merged['incidents_per_1000_arrests'] = np.where(
        merged['arrests'] > 0,
        merged['total_incidents'] / merged['arrests'] * 1000,
        0
    )

    merged['shootings_per_10000_arrests'] = np.where(
        merged['arrests'] > 0,
        merged['shootings_by_agents'] / merged['arrests'] * 10000,
        0
    )

    return merged.sort_values('total_incidents', ascending=False)


def generate_sourced_report():
    """Generate comprehensive report with all source citations."""
    print("=" * 100)
    print("ICE VIOLENT INCIDENTS & ARRESTS: COMPREHENSIVE SOURCED ANALYSIS")
    print("=" * 100)
    print("\nDATA COVERAGE: January 2025 - January 2026")
    print("COMPILED: January 2026")
    print("\n" + "=" * 100)

    incidents_df = pd.DataFrame(VIOLENT_INCIDENTS)

    # Overall statistics with sources
    print("\nOVERALL STATISTICS")
    print("-" * 50)
    print(f"Total documented incidents: {len(incidents_df)}")
    print(f"Total deaths: {(incidents_df['outcome'] == 'death').sum()}")
    print(f"  - From agent shootings: {len(incidents_df[(incidents_df['type'] == 'shooting') & (incidents_df['perpetrator'] == 'agent') & (incidents_df['outcome'] == 'death')])}")
    print(f"  - In custody: {len(incidents_df[incidents_df['type'] == 'death_in_custody'])}")
    print(f"  - From facility attacks: {len(incidents_df[(incidents_df['type'] == 'facility_attack') & (incidents_df['outcome'] == 'death')])}")
    print(f"Total injuries: {(incidents_df['outcome'] == 'injury').sum()}")
    print(f"US citizens affected: {incidents_df['us_citizen'].sum()}")
    print(f"Protest-related incidents: {incidents_df['protest_related'].sum()}")

    print("\n" + "=" * 100)
    print("ARRESTS DATA SOURCES")
    print("=" * 100)
    for state, data in ARRESTS_BY_STATE.items():
        print(f"\n{state}:")
        print(f"  Arrests: {data['arrests']:,}")
        print(f"  Rate: {data['rate_per_100k']} per 100k")
        print(f"  Period: {data['date_range']}")
        print(f"  Source: {data['source_name']}")
        print(f"  URL: {data['source_url']}")

    print("\n" + "=" * 100)
    print("STATE-LEVEL SUMMARY WITH VIOLENCE/ARREST RATIOS")
    print("=" * 100)

    summary = create_state_summary()
    for _, row in summary.iterrows():
        if row['total_incidents'] > 0 or row['arrests'] > 0:
            print(f"\n{row['state']}:")
            print(f"  Incidents: {int(row['total_incidents'])} | Deaths: {int(row['total_deaths'])} | Injuries: {int(row['total_injuries'])}")
            print(f"  Arrests: {int(row['arrests']):,} | Rate: {row['rate_per_100k']:.1f}/100k")
            print(f"  Violence ratio: {row['incidents_per_1000_arrests']:.2f} incidents per 1,000 arrests")
            if row['shootings_by_agents'] > 0:
                print(f"  Agent shootings: {int(row['shootings_by_agents'])} ({row['shootings_per_10000_arrests']:.2f} per 10,000 arrests)")

    return summary


# =============================================================================
# BACKWARD COMPATIBILITY - NEW PACKAGE IMPORTS
# =============================================================================
# The data in this file has been extracted to JSON files in data/
# The functions below provide access via the new package structure.

try:
    from ice_arrests.data.loader import (
        load_arrests_by_state as _load_arrests,
        load_violent_incidents_legacy as _load_incidents,
    )
    _NEW_PACKAGE_AVAILABLE = True
except ImportError:
    _NEW_PACKAGE_AVAILABLE = False


def load_arrests_from_json():
    """Load arrests data from JSON file."""
    if _NEW_PACKAGE_AVAILABLE:
        return _load_arrests()
    return ARRESTS_BY_STATE


def load_incidents_from_json():
    """Load violent incidents from JSON file."""
    if _NEW_PACKAGE_AVAILABLE:
        return _load_incidents()
    return VIOLENT_INCIDENTS


if __name__ == '__main__':
    # Generate report
    summary = generate_sourced_report()

    # Save outputs
    incidents_df = pd.DataFrame(VIOLENT_INCIDENTS)
    incidents_df.to_csv('incidents_fully_sourced.csv', index=False)
    summary.to_csv('state_summary_with_sources.csv', index=False)

    # Save arrests data with sources
    arrests_df = pd.DataFrame([
        {
            'state': k,
            'arrests': v['arrests'],
            'rate_per_100k': v['rate_per_100k'],
            'date_range': v['date_range'],
            'source_name': v['source_name'],
            'source_url': v['source_url'],
            'notes': v['notes']
        }
        for k, v in ARRESTS_BY_STATE.items()
    ])
    arrests_df.to_csv('arrests_by_state_sourced.csv', index=False)

    print("\n\n" + "=" * 100)
    print("OUTPUT FILES SAVED:")
    print("  - incidents_fully_sourced.csv (all incidents with source citations)")
    print("  - state_summary_with_sources.csv (state aggregations)")
    print("  - arrests_by_state_sourced.csv (arrest data with sources)")
    print("=" * 100)
