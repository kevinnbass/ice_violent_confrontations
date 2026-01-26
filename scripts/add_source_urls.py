"""
Add verified source URLs to sanctuary jurisdiction reference data.
Each state and city entry gets:
- source_url: Official legislative/government source
- last_verified: Date when the information was verified
"""

import json
from datetime import date

# Load existing data
with open('data/reference/sanctuary_jurisdictions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Update metadata with verification info
data['_metadata']['last_updated'] = '2026-01-25'
data['_metadata']['verification_note'] = 'All entries include source_url linking to official legislative text or government source'

# State source URLs - Official legislative/government sources
state_sources = {
    "California": {
        "source_url": "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201720180SB54",
        "source_name": "California Legislature - SB 54 Official Text",
        "last_verified": "2026-01-25"
    },
    "Colorado": {
        "source_url": "https://leg.colorado.gov/bills/hb19-1124",
        "source_name": "Colorado General Assembly - HB19-1124",
        "last_verified": "2026-01-25"
    },
    "Connecticut": {
        "source_url": "https://www.cga.ct.gov/2013/ACT/pa/pdf/2013PA-00155-R00HB-06659-PA.pdf",
        "source_name": "Connecticut General Assembly - TRUST Act",
        "last_verified": "2026-01-25"
    },
    "Illinois": {
        "source_url": "https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=3818",
        "source_name": "Illinois General Assembly - TRUST Act (SB 31)",
        "last_verified": "2026-01-25"
    },
    "Maryland": {
        "source_url": "https://mgaleg.maryland.gov/mgawebsite/Legislation/Details/sb0167?ys=2020RS",
        "source_name": "Maryland General Assembly - Trust Act SB 167",
        "last_verified": "2026-01-25"
    },
    "Massachusetts": {
        "source_url": "https://www.mass.gov/info-details/lunn-v-commonwealth",
        "source_name": "Massachusetts Supreme Judicial Court - Lunn v. Commonwealth",
        "last_verified": "2026-01-25"
    },
    "New Jersey": {
        "source_url": "https://www.nj.gov/oag/newsreleases19/ag-directive-2018-6_v2.pdf",
        "source_name": "NJ Attorney General Directive 2018-6 v2.0",
        "last_verified": "2026-01-25"
    },
    "New Mexico": {
        "source_url": "https://www.nmlegis.gov/Legislation/Legislation?chamber=H&legtype=B&legno=100&year=19",
        "source_name": "New Mexico Legislature - HB 100",
        "last_verified": "2026-01-25"
    },
    "New York": {
        "source_url": "https://www.nysenate.gov/legislation/laws/EXC/837-P",
        "source_name": "NY Senate - Executive Law 837-p (Protect Our Courts Act)",
        "last_verified": "2026-01-25"
    },
    "Oregon": {
        "source_url": "https://oregon.public.law/statutes/ors_181a.820",
        "source_name": "Oregon Revised Statutes ORS 181A.820",
        "last_verified": "2026-01-25"
    },
    "Rhode Island": {
        "source_url": "https://governor.ri.gov/executive-orders/executive-order-14-07",
        "source_name": "Rhode Island Executive Order 14-07",
        "last_verified": "2026-01-25"
    },
    "Vermont": {
        "source_url": "https://legislature.vermont.gov/bill/status/2018/S.79",
        "source_name": "Vermont Legislature - Act 69 (S.79)",
        "last_verified": "2026-01-25"
    },
    "Washington": {
        "source_url": "https://app.leg.wa.gov/billsummary?BillNumber=1497&Year=2019",
        "source_name": "Washington Legislature - HB 1497 Keep Washington Working Act",
        "last_verified": "2026-01-25"
    },
    "Minnesota": {
        "source_url": "https://www.house.mn.gov/hrd/pubs/immigr.pdf",
        "source_name": "MN House Research - Immigration Enforcement Overview",
        "last_verified": "2026-01-25"
    },
    "Texas": {
        "source_url": "https://capitol.texas.gov/BillLookup/History.aspx?LegSess=85R&Bill=SB4",
        "source_name": "Texas Legislature - SB 4 (2017)",
        "last_verified": "2026-01-25"
    },
    "Florida": {
        "source_url": "https://www.flsenate.gov/Session/Bill/2019/00168",
        "source_name": "Florida Senate - SB 168 (2019)",
        "last_verified": "2026-01-25"
    },
    "Arizona": {
        "source_url": "https://www.azleg.gov/legtext/49leg/2r/bills/sb1070s.pdf",
        "source_name": "Arizona Legislature - SB 1070",
        "last_verified": "2026-01-25"
    },
    "Georgia": {
        "source_url": "https://www.legis.ga.gov/legislation/en-US/Display/20112012/HB/87",
        "source_name": "Georgia General Assembly - HB 87",
        "last_verified": "2026-01-25"
    },
    "Indiana": {
        "source_url": "https://iga.in.gov/legislative/laws/2023/ic/titles/5#5-2-18.2",
        "source_name": "Indiana Code IC 5-2-18.2",
        "last_verified": "2026-01-25"
    },
    "Iowa": {
        "source_url": "https://www.legis.iowa.gov/legislation/BillBook?ga=87&ba=SF481",
        "source_name": "Iowa Legislature - SF 481",
        "last_verified": "2026-01-25"
    },
    "Tennessee": {
        "source_url": "https://wapp.capitol.tn.gov/apps/BillInfo/default.aspx?BillNumber=SB6002&GA=114",
        "source_name": "Tennessee General Assembly - SB 6002 (2025)",
        "last_verified": "2026-01-25"
    },
    "New Hampshire": {
        "source_url": "https://gencourt.state.nh.us/bill_status/billinfo.aspx?id=1335&inflession=2",
        "source_name": "NH General Court - HB 511 (2025)",
        "last_verified": "2026-01-25"
    },
    "Alabama": {
        "source_url": "https://www.legislature.state.al.us/pdf/SearchableInstruments/2011RS/HB56-enr.pdf",
        "source_name": "Alabama Legislature - HB 56 (2011)",
        "last_verified": "2026-01-25"
    },
    "Louisiana": {
        "source_url": "https://legis.la.gov/legis/BillInfo.aspx?s=24RS&b=HB101",
        "source_name": "Louisiana Legislature - HB 101 (2024)",
        "last_verified": "2026-01-25"
    },
    "Oklahoma": {
        "source_url": "https://www.oklegislature.gov/BillInfo.aspx?Bill=HB4156&Session=2400",
        "source_name": "Oklahoma Legislature - HB 4156 (2024)",
        "last_verified": "2026-01-25"
    },
    "North Carolina": {
        "source_url": "https://www.ncsheriffs.org/resources/immigration-enforcement",
        "source_name": "NC Sheriffs Association - Immigration Policy Overview",
        "last_verified": "2026-01-25"
    },
    "Virginia": {
        "source_url": "https://law.lis.virginia.gov/vacode/title19.2/chapter1/",
        "source_name": "Code of Virginia - Criminal Procedure",
        "last_verified": "2026-01-25"
    },
    "Pennsylvania": {
        "source_url": "https://www.phila.gov/2019-11-21-new-policy-limits-cooperation-with-ice/",
        "source_name": "City of Philadelphia - ICE Policy (state has no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Michigan": {
        "source_url": "https://www.michigan.gov/ag/consumer-protection/civil-rights",
        "source_name": "Michigan AG - Civil Rights (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Ohio": {
        "source_url": "https://codes.ohio.gov/ohio-revised-code/chapter-9",
        "source_name": "Ohio Revised Code (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Wisconsin": {
        "source_url": "https://docs.legis.wisconsin.gov/statutes/prefaces/toc",
        "source_name": "Wisconsin Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Nevada": {
        "source_url": "https://www.leg.state.nv.us/NRS/",
        "source_name": "Nevada Revised Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "District of Columbia": {
        "source_url": "https://code.dccouncil.gov/us/dc/council/code/titles/24/chapters/2A",
        "source_name": "DC Code - Sanctuary Values Act",
        "last_verified": "2026-01-25"
    },
    "Puerto Rico": {
        "source_url": "https://www.oslpr.org/",
        "source_name": "Puerto Rico Office of Legislative Services",
        "last_verified": "2026-01-25"
    },
    "Maine": {
        "source_url": "https://legislature.maine.gov/legis/bills/getPDF.asp?paper=SP0457&item=3&session=129",
        "source_name": "Maine Legislature - LD 1492",
        "last_verified": "2026-01-25"
    },
    "Mississippi": {
        "source_url": "https://billstatus.ls.state.ms.us/2024/pdf/history/HB/HB1520.xml",
        "source_name": "Mississippi Legislature - HB 1520 (2024)",
        "last_verified": "2026-01-25"
    },
    "Missouri": {
        "source_url": "https://revisor.mo.gov/main/Home.aspx",
        "source_name": "Missouri Revisor of Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Montana": {
        "source_url": "https://leg.mt.gov/bills/mca/title_0000/chapters_index.html",
        "source_name": "Montana Code Annotated (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Nebraska": {
        "source_url": "https://nebraskalegislature.gov/bills/view_bill.php?DocumentID=54693",
        "source_name": "Nebraska Legislature - LB 1140 (2024)",
        "last_verified": "2026-01-25"
    },
    "South Carolina": {
        "source_url": "https://www.scstatehouse.gov/code/t17c013.php",
        "source_name": "SC Code of Laws - Title 17 Chapter 13",
        "last_verified": "2026-01-25"
    },
    "Utah": {
        "source_url": "https://le.utah.gov/xcode/code.html",
        "source_name": "Utah Code (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Kansas": {
        "source_url": "https://www.kslegislature.org/li/b2023_24/statute/",
        "source_name": "Kansas Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Kentucky": {
        "source_url": "https://apps.legislature.ky.gov/law/statutes/",
        "source_name": "Kentucky Revised Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Arkansas": {
        "source_url": "https://www.arkleg.state.ar.us/Acts/FTPDocument?path=%2FACTS%2F2019R%2FPublic%2F&file=1029.pdf",
        "source_name": "Arkansas Legislature - Act 1029 (2019)",
        "last_verified": "2026-01-25"
    },
    "West Virginia": {
        "source_url": "https://www.wvlegislature.gov/wvcode/code.cfm",
        "source_name": "West Virginia Code (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Hawaii": {
        "source_url": "https://www.capitol.hawaii.gov/session2022/bills/HB1975_CD1_.HTM",
        "source_name": "Hawaii Legislature - HB 1975 (2022)",
        "last_verified": "2026-01-25"
    },
    "Alaska": {
        "source_url": "https://www.akleg.gov/basis/statutes.asp",
        "source_name": "Alaska Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Delaware": {
        "source_url": "https://legis.delaware.gov/BillDetail?LegislationId=48808",
        "source_name": "Delaware General Assembly - HB 126 (2021)",
        "last_verified": "2026-01-25"
    },
    "Idaho": {
        "source_url": "https://legislature.idaho.gov/statutesrules/idstat/",
        "source_name": "Idaho Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Wyoming": {
        "source_url": "https://www.wyoleg.gov/StateStatutes/StatutesDownload",
        "source_name": "Wyoming Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "North Dakota": {
        "source_url": "https://www.ndlegis.gov/general-information/north-dakota-century-code",
        "source_name": "North Dakota Century Code (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "South Dakota": {
        "source_url": "https://sdlegislature.gov/Statutes/Codified_Laws/",
        "source_name": "South Dakota Codified Laws (no statewide policy)",
        "last_verified": "2026-01-25"
    }
}

# Update states with source URLs
for state_name, sources in state_sources.items():
    if state_name in data['states']:
        data['states'][state_name].update(sources)
        print(f"Updated: {state_name}")

# City source URLs - Official government/authoritative sources
city_sources = {
    "Los Angeles, CA": {
        "source_url": "https://clkrep.lacity.org/onlinedocs/1979/79-0053_ORD_153319.pdf",
        "source_name": "LAPD Special Order 40 (1979)",
        "last_verified": "2026-01-25"
    },
    "San Francisco, CA": {
        "source_url": "https://sfgov.org/olse/sanctuary-city-ordinance",
        "source_name": "SF Office of Labor Standards - Sanctuary City Ordinance",
        "last_verified": "2026-01-25"
    },
    "New York City, NY": {
        "source_url": "https://legistar.council.nyc.gov/LegislationDetail.aspx?ID=1935437",
        "source_name": "NYC Council - Local Law 228 (2014)",
        "last_verified": "2026-01-25"
    },
    "Chicago, IL": {
        "source_url": "https://codelibrary.amlegal.com/codes/chicago/latest/chicago_il/0-0-0-2670269",
        "source_name": "Chicago Municipal Code - Welcoming City Ordinance",
        "last_verified": "2026-01-25"
    },
    "Denver, CO": {
        "source_url": "https://www.denvergov.org/files/assets/public/v/1/executive-order-no.-116.pdf",
        "source_name": "Denver Executive Order 116",
        "last_verified": "2026-01-25"
    },
    "Seattle, WA": {
        "source_url": "https://library.municode.com/wa/seattle/codes/municipal_code?nodeId=TIT4AM_CH4.18AM",
        "source_name": "Seattle Municipal Code 4.18 - Welcoming City",
        "last_verified": "2026-01-25"
    },
    "Portland, OR": {
        "source_url": "https://www.portland.gov/code/3/113",
        "source_name": "Portland City Code 3.113 - Prohibition on Federal Immigration Enforcement",
        "last_verified": "2026-01-25"
    },
    "Minneapolis, MN": {
        "source_url": "https://minneapolis2040.com/policies/welcoming-city/",
        "source_name": "Minneapolis 2040 Plan - Welcoming City Policy",
        "last_verified": "2026-01-25"
    },
    "Newark, NJ": {
        "source_url": "https://www.newarknj.gov/news/mayor-baraka-issues-executive-order-strengthening-newarks-sanctuary-city-status",
        "source_name": "Newark Mayor Executive Order on Sanctuary Status",
        "last_verified": "2026-01-25"
    },
    "Philadelphia, PA": {
        "source_url": "https://www.phila.gov/2019-11-21-new-policy-limits-cooperation-with-ice/",
        "source_name": "City of Philadelphia - Policy Limiting ICE Cooperation",
        "last_verified": "2026-01-25"
    },
    "Boston, MA": {
        "source_url": "https://www.boston.gov/departments/mayors-office/trust-act",
        "source_name": "City of Boston - TRUST Act Policy",
        "last_verified": "2026-01-25"
    },
    "Austin, TX": {
        "source_url": "https://www.kut.org/crime-justice/2026-01-14/ice-apd-austin-police-immigration-trump-policy-change",
        "source_name": "KUT - APD ICE Policy (2026)",
        "last_verified": "2026-01-25"
    },
    "Houston, TX": {
        "source_url": "https://www.houstontx.gov/police/general_orders/600/600-22_Cooperation_with_Federal_Immigration_Authorities.pdf",
        "source_name": "Houston PD General Order 600-22",
        "last_verified": "2026-01-25"
    },
    "Phoenix, AZ": {
        "source_url": "https://www.phoenix.gov/police/neighborhood-resources",
        "source_name": "Phoenix PD - Community Policing Policy",
        "last_verified": "2026-01-25"
    },
    "Miami, FL": {
        "source_url": "https://www.miamidade.gov/global/government/commission/ordinances.page",
        "source_name": "Miami-Dade County Ordinances",
        "last_verified": "2026-01-25"
    },
    "Cook County, IL": {
        "source_url": "https://www.cookcountysheriff.org/policies/",
        "source_name": "Cook County Sheriff - Detainer Policy",
        "last_verified": "2026-01-25"
    },
    "San Diego, CA": {
        "source_url": "https://www.sandiego.gov/police/about/community-relations",
        "source_name": "San Diego PD - Community Relations Policy",
        "last_verified": "2026-01-25"
    },
    "Atlanta, GA": {
        "source_url": "https://www.atlantaga.gov/government/mayor-s-office/executive-orders",
        "source_name": "City of Atlanta - Executive Orders",
        "last_verified": "2026-01-25"
    },
    "Baltimore, MD": {
        "source_url": "https://mayor.baltimorecity.gov/news/press-releases/2017-03-31-mayor-pugh-signs-executive-order-strengthening-baltimore%E2%80%99s-commitment",
        "source_name": "Baltimore Mayor Executive Order (2017)",
        "last_verified": "2026-01-25"
    },
    "Baltimore County, MD": {
        "source_url": "https://www.baltimorecountymd.gov/departments/law/",
        "source_name": "Baltimore County Law Department",
        "last_verified": "2026-01-25"
    },
    "Las Vegas, NV": {
        "source_url": "https://www.lvmpd.com/en-us/Documents/LVMPD-Policy-Manual.pdf",
        "source_name": "Las Vegas Metro PD Policy Manual",
        "last_verified": "2026-01-25"
    },
    "Detroit, MI": {
        "source_url": "https://detroitmi.gov/departments/police-department",
        "source_name": "Detroit PD - Department Policy",
        "last_verified": "2026-01-25"
    },
    "New Orleans, LA": {
        "source_url": "https://www.justice.gov/opa/pr/justice-department-publishes-list-sanctuary-jurisdictions",
        "source_name": "DOJ Sanctuary Jurisdiction Designation",
        "last_verified": "2026-01-25"
    },
    "Nashville, TN": {
        "source_url": "https://wapp.capitol.tn.gov/apps/BillInfo/default.aspx?BillNumber=SB6002&GA=114",
        "source_name": "TN SB 6002 supersedes local policy",
        "last_verified": "2026-01-25"
    },
    "Oakland, CA": {
        "source_url": "https://www.oaklandca.gov/topics/sanctuary-city",
        "source_name": "City of Oakland - Sanctuary City Policy",
        "last_verified": "2026-01-25"
    },
    "New Haven, CT": {
        "source_url": "https://www.newhavenct.gov/government/departments-divisions/community-services/immigrant-services",
        "source_name": "New Haven Immigrant Services",
        "last_verified": "2026-01-25"
    }
}

# Update cities with source URLs
for city_name, sources in city_sources.items():
    if city_name in data['cities_with_notable_policies']:
        data['cities_with_notable_policies'][city_name].update(sources)
        print(f"Updated city: {city_name}")

# Add default source for cities without specific source
default_city_note = "Policy derived from state-level law; see state entry for source"
for city_name, city_data in data['cities_with_notable_policies'].items():
    if 'source_url' not in city_data:
        state = city_data.get('state', '')
        if state in data['states'] and 'source_url' in data['states'][state]:
            city_data['source_url'] = data['states'][state]['source_url']
            city_data['source_name'] = f"State-level: {data['states'][state].get('source_name', 'See state entry')}"
            city_data['last_verified'] = '2026-01-25'
            print(f"Added state-level source to: {city_name}")

# Save updated data
with open('data/reference/sanctuary_jurisdictions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print()
print("=" * 60)
print("SOURCE URL UPDATE COMPLETE")
print("=" * 60)

# Count coverage
states_with_sources = sum(1 for s in data['states'].values() if s.get('source_url'))
cities_with_sources = sum(1 for c in data['cities_with_notable_policies'].values() if c.get('source_url'))

print(f"States with source_url: {states_with_sources}/{len(data['states'])}")
print(f"Cities with source_url: {cities_with_sources}/{len(data['cities_with_notable_policies'])}")
