"""
STATE IMMIGRATION ENFORCEMENT CLASSIFICATIONS
=============================================
Rigorous documentation of sanctuary vs. cooperation states with legal citations.

CLASSIFICATION METHODOLOGY:
- "sanctuary": State has laws limiting cooperation with ICE (detainer non-compliance,
  information sharing restrictions, etc.)
- "anti_sanctuary": State has laws mandating cooperation with ICE or banning sanctuary
  policies
- "aggressive_anti_sanctuary": State has particularly comprehensive laws forcing local
  agencies to participate in deportation
- "neutral": No statewide policy mandating or restricting cooperation

PRIMARY SOURCES:
1. DOJ Sanctuary Jurisdiction List (Executive Order 14287) - Oct 31, 2025
   https://www.justice.gov/ag/us-sanctuary-jurisdiction-list
2. ILRC State Map on Immigration Enforcement (Nov 8, 2024)
   https://www.ilrc.org/state-map-immigration-enforcement-2024
3. Ballotpedia Sanctuary Jurisdiction Policies
   https://ballotpedia.org/Sanctuary_jurisdiction_policies_by_state
4. American Immigration Council
   https://www.americanimmigrationcouncil.org/fact-sheet/sanctuary-policies-overview/
"""

import warnings

# =============================================================================
# DEPRECATION NOTICE
# =============================================================================
# This file is DEPRECATED. Please use the ice_arrests package instead:
#
#   from ice_arrests import load_state_classifications
#   classifications = load_state_classifications()
#
# Data is now stored in JSON files:
#   - data/state_classifications.json
#
# This file will be moved to archive/ in a future release.
# =============================================================================

warnings.warn(
    "STATE_ENFORCEMENT_CLASSIFICATIONS is deprecated. Use 'from ice_arrests import load_state_classifications' instead. "
    "Data is now stored in data/state_classifications.json.",
    DeprecationWarning,
    stacklevel=2
)

# =============================================================================
# STATE CLASSIFICATIONS WITH FULL LEGAL CITATIONS
# =============================================================================

STATE_CLASSIFICATIONS = {
    # =========================================================================
    # SANCTUARY STATES (Laws limiting ICE cooperation)
    # =========================================================================

    "California": {
        "classification": "sanctuary",
        "tier": "comprehensive",
        "primary_law": "SB 54 - California Values Act (2017)",
        "law_details": "Prohibits state/local resources from enforcing federal immigration law; bars cooperation with ICE holds; restricts responses to detainer requests",
        "additional_laws": [
            "AB 32 (2019) - Prohibits private immigration detention facilities",
            "AB 668 (2019) - Prohibits immigration arrests in/around courthouses",
            "TRUST Act (2013) - Original detainer restriction"
        ],
        "effective_date": "2018-01-01",
        "doj_designated": True,
        "source_url": "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201720180SB54",
        "source_name": "California Legislative Information",
        "ilrc_rating": "fairly_broad_sanctuary",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Oregon": {
        "classification": "sanctuary",
        "tier": "comprehensive",
        "primary_law": "ORS § 181a.820 (1987) + Oregon Sanctuary Promise Act (2021)",
        "law_details": "First sanctuary state (1987); prohibits use of public resources to arrest/detain based on immigration status; bans ICE detention centers; prohibits info sharing with federal immigration authorities",
        "additional_laws": [
            "HB 3464 (2017) - Restricts communication with federal immigration authorities",
            "Order No. 19-095 (2019) - Prohibits courthouse arrests without judicial warrant"
        ],
        "effective_date": "1987-07-01",
        "doj_designated": True,
        "source_url": "https://www.oregonlegislature.gov/bills_laws/ors/ors181a.html",
        "source_name": "Oregon Revised Statutes",
        "ilrc_rating": "most_protective",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Illinois": {
        "classification": "sanctuary",
        "tier": "comprehensive",
        "primary_law": "SB 31 - Illinois TRUST Act (2017) + Way Forward Act (2021)",
        "law_details": "Prohibits holding individuals on ICE detainers; bans immigration detention centers; prohibits local cooperation with ICE; limits enforcement at schools, hospitals, courthouses",
        "additional_laws": [
            "Way Forward Act (2021) - Expanded protections",
            "AG Guidance (2025) - Prohibits law enforcement from federal immigration enforcement without judicial warrant"
        ],
        "effective_date": "2017-08-28",
        "doj_designated": True,
        "source_url": "https://www.ilga.gov/legislation/publicacts/100/PDF/100-0463.pdf",
        "source_name": "Illinois General Assembly",
        "ilrc_rating": "most_protective",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Washington": {
        "classification": "sanctuary",
        "tier": "fairly_broad",
        "primary_law": "SB 5497 - Keep Washington Working Act (2019)",
        "law_details": "Bars local jails from holding individuals based solely on ICE detainers; restricts information sharing",
        "additional_laws": [
            "HB 2567 (2020) - Prohibits immigration arrests in/around courthouses"
        ],
        "effective_date": "2019-05-21",
        "doj_designated": True,
        "source_url": "https://lawfilesext.leg.wa.gov/biennium/2019-20/Pdf/Bills/Session%20Laws/Senate/5497-S2.SL.pdf",
        "source_name": "Washington State Legislature",
        "ilrc_rating": "fairly_broad_sanctuary",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "New Jersey": {
        "classification": "sanctuary",
        "tier": "fairly_broad",
        "primary_law": "Immigrant Trust Directive (AG Directive 2018-6)",
        "law_details": "Limits local law enforcement cooperation with ICE; restricts honoring detainers without judicial warrant",
        "additional_laws": [],
        "effective_date": "2018-11-29",
        "doj_designated": False,
        "source_url": "https://www.nj.gov/oag/dcj/agguide/directives/ag-directive-2018-6_v2.pdf",
        "source_name": "NJ Office of Attorney General",
        "ilrc_rating": "fairly_broad_sanctuary",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Colorado": {
        "classification": "sanctuary",
        "tier": "some_protections",
        "primary_law": "HB 19-1124 (2019)",
        "law_details": "Prohibits detainer compliance absent judicial warrant; bans cooperative agreements with federal immigration authorities",
        "additional_laws": [
            "SB 20-083 (2020) - Prohibits immigration arrests in/around courthouses",
            "HB 23-1100 (2024) - Bars use of jails for immigration arrests"
        ],
        "effective_date": "2019-05-28",
        "doj_designated": True,
        "source_url": "https://leg.colorado.gov/bills/hb19-1124",
        "source_name": "Colorado General Assembly",
        "ilrc_rating": "some_protections",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Connecticut": {
        "classification": "sanctuary",
        "tier": "some_protections",
        "primary_law": "TRUST Act (Public Act 13-155) (2013)",
        "law_details": "Limits compliance with ICE detainers; requires judicial warrant for immigration holds",
        "additional_laws": [],
        "effective_date": "2013-10-01",
        "doj_designated": True,
        "source_url": "https://www.cga.ct.gov/2013/ACT/pa/pdf/2013PA-00155-R00SB-00992-PA.pdf",
        "source_name": "Connecticut General Assembly",
        "ilrc_rating": "some_protections",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "New York": {
        "classification": "sanctuary",
        "tier": "limited_steps",
        "primary_law": "Executive Order (2017) + Various local policies",
        "law_details": "Prohibits inquiring about immigration status; limits ICE access to city facilities",
        "additional_laws": [],
        "effective_date": "2017-01-01",
        "doj_designated": True,
        "source_url": "https://www.governor.ny.gov/executiveorders",
        "source_name": "NY Governor's Office",
        "ilrc_rating": "limited_steps",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Vermont": {
        "classification": "sanctuary",
        "tier": "some_protections",
        "primary_law": "Act 69 (2017) - Fair and Impartial Policing Policy",
        "law_details": "Limits state/local law enforcement cooperation with federal immigration authorities",
        "additional_laws": [],
        "effective_date": "2017-06-09",
        "doj_designated": True,
        "source_url": "https://legislature.vermont.gov/bill/status/2018/S.79",
        "source_name": "Vermont General Assembly",
        "ilrc_rating": "some_protections",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Maryland": {
        "classification": "sanctuary",
        "tier": "some_protections",
        "primary_law": "Dignity Not Detention Act (2021)",
        "law_details": "Prohibits local jurisdictions from entering immigration detention agreements with private entities",
        "additional_laws": [
            "TRUST Act (various counties)"
        ],
        "effective_date": "2021-12-01",
        "doj_designated": False,
        "source_url": "https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/sb0565?ys=2021RS",
        "source_name": "Maryland General Assembly",
        "ilrc_rating": "some_protections",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Rhode Island": {
        "classification": "sanctuary",
        "tier": "limited_steps",
        "primary_law": "Executive Order 15-09 (2015)",
        "law_details": "Limits compliance with ICE detainers for non-violent offenses",
        "additional_laws": [],
        "effective_date": "2015-10-22",
        "doj_designated": True,
        "source_url": "https://governor.ri.gov/executive-orders",
        "source_name": "RI Governor's Office",
        "ilrc_rating": "limited_steps",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Minnesota": {
        "classification": "sanctuary",
        "tier": "limited_steps",
        "primary_law": "No statewide law; Governor policy + local policies",
        "law_details": "Governor Walz administration policy limiting state cooperation; various local sanctuary policies",
        "additional_laws": [],
        "effective_date": "2019-01-01",
        "doj_designated": True,
        "source_url": "https://www.justice.gov/ag/us-sanctuary-jurisdiction-list",
        "source_name": "DOJ Sanctuary List",
        "ilrc_rating": "limited_steps",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Delaware": {
        "classification": "sanctuary",
        "tier": "limited_steps",
        "primary_law": "Executive order/administrative policy",
        "law_details": "State policy limiting ICE cooperation",
        "additional_laws": [],
        "effective_date": "2019-01-01",
        "doj_designated": True,
        "source_url": "https://www.justice.gov/ag/us-sanctuary-jurisdiction-list",
        "source_name": "DOJ Sanctuary List",
        "ilrc_rating": "limited_steps",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    # =========================================================================
    # AGGRESSIVE ANTI-SANCTUARY STATES (Comprehensive mandatory cooperation)
    # =========================================================================

    "Texas": {
        "classification": "aggressive_anti_sanctuary",
        "tier": "most_restrictive",
        "primary_law": "SB 4 (2017)",
        "law_details": "Bans sanctuary policies statewide; grants officers authority to ask immigration status during routine encounters; imposes fines on non-compliant jurisdictions; allows removal from office for officials implementing sanctuary policies",
        "additional_laws": [
            "HB 4 (2023) - Creates state deportation mechanism",
            "Operation Lone Star (2021) - State border enforcement"
        ],
        "effective_date": "2017-09-01",
        "doj_designated": False,
        "source_url": "https://capitol.texas.gov/tlodocs/85R/billtext/pdf/SB00004F.pdf",
        "source_name": "Texas Legislature",
        "ilrc_rating": "aggressive_anti_sanctuary",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Florida": {
        "classification": "aggressive_anti_sanctuary",
        "tier": "most_restrictive",
        "primary_law": "SB 168 (2019)",
        "law_details": "Requires local law enforcement to comply with ICE detainers; bans sanctuary policies; requires 287(g) participation",
        "additional_laws": [
            "SB 1718 (2023) - Enhanced enforcement; E-Verify mandate"
        ],
        "effective_date": "2019-06-14",
        "doj_designated": False,
        "source_url": "https://www.flsenate.gov/Session/Bill/2019/168",
        "source_name": "Florida Senate",
        "ilrc_rating": "aggressive_anti_sanctuary",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024",
        "notes": "As of June 2025, 295 active 287(g) MOAs - most in nation"
    },

    "Georgia": {
        "classification": "aggressive_anti_sanctuary",
        "tier": "most_restrictive",
        "primary_law": "HB 87 (2011) + SB 452 (2024)",
        "law_details": "Bans sanctuary policies; requires 287(g) participation; mandates E-Verify; punishes local governments refusing ICE cooperation",
        "additional_laws": [],
        "effective_date": "2011-07-01",
        "doj_designated": False,
        "source_url": "https://www.legis.ga.gov/legislation/20039",
        "source_name": "Georgia General Assembly",
        "ilrc_rating": "aggressive_anti_sanctuary",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Iowa": {
        "classification": "aggressive_anti_sanctuary",
        "tier": "most_restrictive",
        "primary_law": "SF 481 (2018) + SF 2340 (2024)",
        "law_details": "Bans sanctuary policies; requires detainer compliance; 2024 law creates state deportation mechanism and crimes for being undocumented",
        "additional_laws": [],
        "effective_date": "2018-04-10",
        "doj_designated": False,
        "source_url": "https://www.legis.iowa.gov/legislation/BillBook?ga=87&ba=SF481",
        "source_name": "Iowa Legislature",
        "ilrc_rating": "aggressive_anti_sanctuary",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "West Virginia": {
        "classification": "aggressive_anti_sanctuary",
        "tier": "most_restrictive",
        "primary_law": "SB 156 (2024)",
        "law_details": "Comprehensive anti-sanctuary law; forces local agencies to participate in deportation",
        "additional_laws": [],
        "effective_date": "2024-03-01",
        "doj_designated": False,
        "source_url": "https://www.wvlegislature.gov/Bill_Status/bills_history.cfm?input=156&year=2024&sessiontype=RS",
        "source_name": "WV Legislature",
        "ilrc_rating": "aggressive_anti_sanctuary",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    # =========================================================================
    # ANTI-SANCTUARY STATES (Mandatory cooperation, less comprehensive)
    # =========================================================================

    "Alabama": {
        "classification": "anti_sanctuary",
        "tier": "broad_negative",
        "primary_law": "HB 56 (2011)",
        "law_details": "Bans sanctuary cities; fines levied directly against officials; criminal charges possible for failing to report violations",
        "additional_laws": [],
        "effective_date": "2011-09-28",
        "doj_designated": False,
        "source_url": "http://alisondb.legislature.state.al.us/ALISON/SearchableInstruments/2011RS/PrintFiles/HB56-enr.pdf",
        "source_name": "Alabama Legislature",
        "ilrc_rating": "broad_anti_sanctuary",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Tennessee": {
        "classification": "anti_sanctuary",
        "tier": "broad_negative",
        "primary_law": "HB 2315 (2018) + SB 6002 (2025)",
        "law_details": "Requires compliance with ICE detainers; 2025 law creates Class E felony for officials adopting sanctuary policies (1-6 years prison)",
        "additional_laws": [],
        "effective_date": "2018-05-21",
        "doj_designated": False,
        "source_url": "https://wapp.capitol.tn.gov/apps/BillInfo/Default.aspx?BillNumber=HB2315",
        "source_name": "Tennessee General Assembly",
        "ilrc_rating": "broad_anti_sanctuary",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Arizona": {
        "classification": "anti_sanctuary",
        "tier": "mandates_participation",
        "primary_law": "SB 1070 (2010) (partially enjoined) + subsequent laws",
        "law_details": "Requires law enforcement to check immigration status during stops; mandates ICE cooperation",
        "additional_laws": [],
        "effective_date": "2010-04-23",
        "doj_designated": False,
        "source_url": "https://www.azleg.gov/legtext/49leg/2r/bills/sb1070s.pdf",
        "source_name": "Arizona Legislature",
        "ilrc_rating": "mandates_participation",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Louisiana": {
        "classification": "anti_sanctuary",
        "tier": "mandates_participation",
        "primary_law": "Governor Executive Order (2025)",
        "law_details": "Requires State Police, Corrections, Wildlife, Fire Marshal, National Guard to join 287(g) program",
        "additional_laws": [
            "HB 1148 (2024) - Creates state deportation mechanism"
        ],
        "effective_date": "2025-05-01",
        "doj_designated": False,
        "source_url": "https://gov.louisiana.gov/index.cfm/newsroom/detail/4521",
        "source_name": "Louisiana Governor's Office",
        "ilrc_rating": "mandates_participation",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Indiana": {
        "classification": "anti_sanctuary",
        "tier": "mandates_participation",
        "primary_law": "IC 5-2-18.2 (2011)",
        "law_details": "Bans sanctuary cities since 2011; prohibits limiting involvement in immigration enforcement to less than full extent permitted",
        "additional_laws": [],
        "effective_date": "2011-07-01",
        "doj_designated": False,
        "source_url": "https://iga.in.gov/laws/2023/ic/titles/5#5-2-18.2",
        "source_name": "Indiana General Assembly",
        "ilrc_rating": "mandates_participation",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Mississippi": {
        "classification": "anti_sanctuary",
        "tier": "mandates_participation",
        "primary_law": "SB 2710 (2017)",
        "law_details": "Bars sanctuary policies; blocks counties, cities, colleges from creating sanctuary policies; requires immigration status cooperation",
        "additional_laws": [],
        "effective_date": "2017-07-01",
        "doj_designated": False,
        "source_url": "http://billstatus.ls.state.ms.us/2017/pdf/history/SB/SB2710.xml",
        "source_name": "Mississippi Legislature",
        "ilrc_rating": "mandates_participation",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "North Carolina": {
        "classification": "anti_sanctuary",
        "tier": "mandates_participation",
        "primary_law": "HB 318 (2015) + SB 145 (2018)",
        "law_details": "Bans sanctuary cities; strips state revenues from sanctuary jurisdictions",
        "additional_laws": [],
        "effective_date": "2015-10-28",
        "doj_designated": False,
        "source_url": "https://www.ncleg.gov/BillLookUp/2015/h318",
        "source_name": "NC General Assembly",
        "ilrc_rating": "mandates_participation",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Arkansas": {
        "classification": "anti_sanctuary",
        "tier": "mandates_participation",
        "primary_law": "SB 411 (2019)",
        "law_details": "Prohibits municipalities from adopting sanctuary policies",
        "additional_laws": [],
        "effective_date": "2019-03-22",
        "doj_designated": False,
        "source_url": "https://www.arkleg.state.ar.us/Bills/Detail?id=SB411&ddBienniumSession=2019%2F2019R",
        "source_name": "Arkansas Legislature",
        "ilrc_rating": "mandates_participation",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Oklahoma": {
        "classification": "anti_sanctuary",
        "tier": "mandates_participation",
        "primary_law": "HB 4156 (2024)",
        "law_details": "Creates state deportation mechanism; mandates ICE cooperation",
        "additional_laws": [],
        "effective_date": "2024-11-01",
        "doj_designated": False,
        "source_url": "http://webserver1.lsb.state.ok.us/cf_pdf/2023-24%20ENR/hB/HB4156%20ENR.PDF",
        "source_name": "Oklahoma Legislature",
        "ilrc_rating": "mandates_participation",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "South Carolina": {
        "classification": "anti_sanctuary",
        "tier": "mandates_participation",
        "primary_law": "Act 69 (2011)",
        "law_details": "Requires verification of immigration status; prohibits sanctuary policies",
        "additional_laws": [],
        "effective_date": "2012-01-01",
        "doj_designated": False,
        "source_url": "https://www.scstatehouse.gov/sess119_2011-2012/bills/69.htm",
        "source_name": "SC General Assembly",
        "ilrc_rating": "mandates_participation",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    # =========================================================================
    # NEUTRAL STATES (No statewide mandate either direction)
    # =========================================================================

    "Massachusetts": {
        "classification": "neutral",
        "tier": "no_statewide_policy",
        "primary_law": "No statewide law; various local sanctuary policies (Boston, Cambridge, etc.)",
        "law_details": "No statewide sanctuary or anti-sanctuary law; local policies vary significantly",
        "additional_laws": [],
        "effective_date": None,
        "doj_designated": False,
        "source_url": "https://www.ilrc.org/state-map-immigration-enforcement-2024",
        "source_name": "ILRC State Map",
        "ilrc_rating": "neutral",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024",
        "notes": "Boston is sanctuary city (DOJ designated)"
    },

    "Pennsylvania": {
        "classification": "neutral",
        "tier": "no_statewide_policy",
        "primary_law": "No statewide law; Philadelphia has sanctuary policy",
        "law_details": "No statewide mandate; major cities have varying policies",
        "additional_laws": [],
        "effective_date": None,
        "doj_designated": False,
        "source_url": "https://www.ilrc.org/state-map-immigration-enforcement-2024",
        "source_name": "ILRC State Map",
        "ilrc_rating": "neutral",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024",
        "notes": "Philadelphia is sanctuary city (DOJ designated)"
    },

    "Virginia": {
        "classification": "neutral",
        "tier": "no_statewide_policy",
        "primary_law": "No statewide law; Governor vetoed anti-sanctuary bills",
        "law_details": "Gov. Northam vetoed SB 1156 (2019) and HB 1257 (2018); no mandate either direction",
        "additional_laws": [],
        "effective_date": None,
        "doj_designated": False,
        "source_url": "https://ballotpedia.org/Sanctuary_jurisdiction_policies_by_state",
        "source_name": "Ballotpedia",
        "ilrc_rating": "neutral",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Nevada": {
        "classification": "neutral",
        "tier": "no_statewide_policy",
        "primary_law": "No statewide law",
        "law_details": "No statewide sanctuary or anti-sanctuary policy",
        "additional_laws": [],
        "effective_date": None,
        "doj_designated": False,
        "source_url": "https://www.ilrc.org/state-map-immigration-enforcement-2024",
        "source_name": "ILRC State Map",
        "ilrc_rating": "neutral",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Ohio": {
        "classification": "neutral",
        "tier": "no_statewide_policy",
        "primary_law": "No statewide law",
        "law_details": "No statewide sanctuary or anti-sanctuary policy",
        "additional_laws": [],
        "effective_date": None,
        "doj_designated": False,
        "source_url": "https://www.ilrc.org/state-map-immigration-enforcement-2024",
        "source_name": "ILRC State Map",
        "ilrc_rating": "neutral",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },

    "Michigan": {
        "classification": "neutral",
        "tier": "no_statewide_policy",
        "primary_law": "No statewide law",
        "law_details": "No statewide sanctuary or anti-sanctuary policy",
        "additional_laws": [],
        "effective_date": None,
        "doj_designated": False,
        "source_url": "https://www.ilrc.org/state-map-immigration-enforcement-2024",
        "source_name": "ILRC State Map",
        "ilrc_rating": "neutral",
        "ilrc_source": "https://www.ilrc.org/state-map-immigration-enforcement-2024"
    },
}


# =============================================================================
# SUMMARY STATISTICS
# =============================================================================

def summarize_classifications():
    """Summarize state classifications."""
    summary = {
        'sanctuary': [],
        'anti_sanctuary': [],
        'aggressive_anti_sanctuary': [],
        'neutral': []
    }

    for state, data in STATE_CLASSIFICATIONS.items():
        summary[data['classification']].append(state)

    return summary


def print_summary():
    """Print classification summary."""
    summary = summarize_classifications()

    print("=" * 80)
    print("STATE IMMIGRATION ENFORCEMENT CLASSIFICATIONS")
    print("=" * 80)

    print(f"\nSANCTUARY STATES ({len(summary['sanctuary'])}):")
    print("-" * 40)
    for state in sorted(summary['sanctuary']):
        data = STATE_CLASSIFICATIONS[state]
        print(f"  {state}: {data['primary_law']}")

    print(f"\nAGGRESSIVE ANTI-SANCTUARY STATES ({len(summary['aggressive_anti_sanctuary'])}):")
    print("-" * 40)
    for state in sorted(summary['aggressive_anti_sanctuary']):
        data = STATE_CLASSIFICATIONS[state]
        print(f"  {state}: {data['primary_law']}")

    print(f"\nANTI-SANCTUARY STATES ({len(summary['anti_sanctuary'])}):")
    print("-" * 40)
    for state in sorted(summary['anti_sanctuary']):
        data = STATE_CLASSIFICATIONS[state]
        print(f"  {state}: {data['primary_law']}")

    print(f"\nNEUTRAL STATES ({len(summary['neutral'])}):")
    print("-" * 40)
    for state in sorted(summary['neutral']):
        data = STATE_CLASSIFICATIONS[state]
        print(f"  {state}: {data.get('notes', 'No statewide policy')}")


# =============================================================================
# BACKWARD COMPATIBILITY - NEW PACKAGE IMPORTS
# =============================================================================
# The data in this file has been extracted to JSON files in data/
# The functions below provide access via the new package structure.

try:
    from ice_arrests.data.loader import load_state_classifications as _load_classifications
    _NEW_PACKAGE_AVAILABLE = True
except ImportError:
    _NEW_PACKAGE_AVAILABLE = False


def load_classifications_from_json():
    """Load state classifications from JSON file."""
    if _NEW_PACKAGE_AVAILABLE:
        return _load_classifications()
    return STATE_CLASSIFICATIONS


if __name__ == '__main__':
    print_summary()

    # Export to CSV
    import pandas as pd

    rows = []
    for state, data in STATE_CLASSIFICATIONS.items():
        rows.append({
            'state': state,
            'classification': data['classification'],
            'tier': data['tier'],
            'primary_law': data['primary_law'],
            'law_details': data['law_details'],
            'effective_date': data.get('effective_date'),
            'doj_designated_sanctuary': data['doj_designated'],
            'source_url': data['source_url'],
            'source_name': data['source_name'],
            'ilrc_rating': data.get('ilrc_rating'),
            'ilrc_source': data.get('ilrc_source')
        })

    df = pd.DataFrame(rows)
    df.to_csv('state_classifications_sourced.csv', index=False)
    print("\n\nSaved: state_classifications_sourced.csv")
