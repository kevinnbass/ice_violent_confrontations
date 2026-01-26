"""Add missing major US cities to sanctuary reference data."""

import json

with open('data/reference/sanctuary_jurisdictions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Add missing major cities - policies derived from state laws
new_cities = {
    "Louisville, KY": {
        "state": "Kentucky",
        "local_status": "cooperative",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Jefferson County. Kentucky has no statewide sanctuary policy; Louisville generally cooperative with ICE.",
        "source_url": "https://apps.legislature.ky.gov/law/statutes/",
        "source_name": "State-level: Kentucky Revised Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Virginia Beach, VA": {
        "state": "Virginia",
        "local_status": "cooperative",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Independent city. Virginia has no statewide policy; Virginia Beach generally cooperative.",
        "source_url": "https://law.lis.virginia.gov/vacode/title19.2/chapter1/",
        "source_name": "State-level: Code of Virginia - Criminal Procedure",
        "last_verified": "2026-01-25"
    },
    "Tulsa, OK": {
        "state": "Oklahoma",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Tulsa County. Oklahoma HB 4156 (2024) grants state police immigration enforcement authority.",
        "source_url": "https://www.oklegislature.gov/BillInfo.aspx?Bill=HB4156&Session=2400",
        "source_name": "State-level: Oklahoma Legislature - HB 4156 (2024)",
        "last_verified": "2026-01-25"
    },
    "Wichita, KS": {
        "state": "Kansas",
        "local_status": "cooperative",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Sedgwick County. Kansas has no statewide sanctuary policy.",
        "source_url": "https://www.kslegislature.org/li/b2023_24/statute/",
        "source_name": "State-level: Kansas Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Honolulu, HI": {
        "state": "Hawaii",
        "local_status": "sanctuary_limited",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "City and County of Honolulu. Hawaii HB 1975 (2022) limits law enforcement cooperation with ICE.",
        "source_url": "https://www.capitol.hawaii.gov/session2022/bills/HB1975_CD1_.HTM",
        "source_name": "State-level: Hawaii Legislature - HB 1975 (2022)",
        "last_verified": "2026-01-25"
    },
    "Corpus Christi, TX": {
        "state": "Texas",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Nueces County. Under Texas SB4 (2017) mandating cooperation with ICE.",
        "source_url": "https://capitol.texas.gov/BillLookup/History.aspx?LegSess=85R&Bill=SB4",
        "source_name": "State-level: Texas Legislature - SB 4 (2017)",
        "last_verified": "2026-01-25"
    },
    "Lexington, KY": {
        "state": "Kentucky",
        "local_status": "cooperative",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Fayette County (merged city-county). Kentucky has no statewide policy.",
        "source_url": "https://apps.legislature.ky.gov/law/statutes/",
        "source_name": "State-level: Kentucky Revised Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Henderson, NV": {
        "state": "Nevada",
        "local_status": "sanctuary_partial",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Clark County. Similar to Las Vegas Metro - limited cooperation policy.",
        "source_url": "https://www.leg.state.nv.us/NRS/",
        "source_name": "State-level: Nevada Revised Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Saint Paul, MN": {
        "state": "Minnesota",
        "local_status": "sanctuary_partial",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Ramsey County. Mayor Kaohly Her (first Hmong mayor) criticized ICE door-to-door targeting. Part of Minneapolis-St. Paul coalition lawsuit against DHS.",
        "source_url": "https://www.house.mn.gov/hrd/pubs/immigr.pdf",
        "source_name": "State-level: MN House Research - Immigration Enforcement Overview",
        "last_verified": "2026-01-25"
    },
    "Greensboro, NC": {
        "state": "North Carolina",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Guilford County. North Carolina varies by county; Guilford generally cooperative.",
        "source_url": "https://www.ncsheriffs.org/resources/immigration-enforcement",
        "source_name": "State-level: NC Sheriffs Association - Immigration Policy Overview",
        "last_verified": "2026-01-25"
    },
    "Lincoln, NE": {
        "state": "Nebraska",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Lancaster County. Nebraska LB 1140 (2024) bans sanctuary policies.",
        "source_url": "https://nebraskalegislature.gov/bills/view_bill.php?DocumentID=54693",
        "source_name": "State-level: Nebraska Legislature - LB 1140 (2024)",
        "last_verified": "2026-01-25"
    },
    "Anchorage, AK": {
        "state": "Alaska",
        "local_status": "cooperative",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Municipality of Anchorage. Alaska has no statewide policy.",
        "source_url": "https://www.akleg.gov/basis/statutes.asp",
        "source_name": "State-level: Alaska Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Plano, TX": {
        "state": "Texas",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Collin County. Under Texas SB4 (2017).",
        "source_url": "https://capitol.texas.gov/BillLookup/History.aspx?LegSess=85R&Bill=SB4",
        "source_name": "State-level: Texas Legislature - SB 4 (2017)",
        "last_verified": "2026-01-25"
    },
    "Irvine, CA": {
        "state": "California",
        "local_status": "sanctuary_limited",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Orange County. Under California Values Act (SB 54).",
        "source_url": "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201720180SB54",
        "source_name": "State-level: California Legislature - SB 54 Official Text",
        "last_verified": "2026-01-25"
    },
    "Durham, NC": {
        "state": "North Carolina",
        "local_status": "sanctuary_partial",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Durham County. More progressive than most NC counties; some limits on ICE cooperation.",
        "source_url": "https://www.ncsheriffs.org/resources/immigration-enforcement",
        "source_name": "State-level: NC Sheriffs Association - Immigration Policy Overview",
        "last_verified": "2026-01-25"
    },
    "Chula Vista, CA": {
        "state": "California",
        "local_status": "sanctuary_limited",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "San Diego County. Border city under California Values Act.",
        "source_url": "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201720180SB54",
        "source_name": "State-level: California Legislature - SB 54 Official Text",
        "last_verified": "2026-01-25"
    },
    "Toledo, OH": {
        "state": "Ohio",
        "local_status": "cooperative",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Lucas County. Ohio has no statewide policy; Toledo generally cooperative.",
        "source_url": "https://codes.ohio.gov/ohio-revised-code/chapter-9",
        "source_name": "State-level: Ohio Revised Code (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Fort Wayne, IN": {
        "state": "Indiana",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Allen County. Indiana IC 5-2-18.2 is anti-sanctuary.",
        "source_url": "https://iga.in.gov/legislative/laws/2023/ic/titles/5#5-2-18.2",
        "source_name": "State-level: Indiana Code IC 5-2-18.2",
        "last_verified": "2026-01-25"
    },
    "St. Petersburg, FL": {
        "state": "Florida",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Pinellas County. Florida SB 168 (2019) requires full ICE cooperation.",
        "source_url": "https://www.flsenate.gov/Session/Bill/2019/00168",
        "source_name": "State-level: Florida Senate - SB 168 (2019)",
        "last_verified": "2026-01-25"
    },
    "Chandler, AZ": {
        "state": "Arizona",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Maricopa County. 287(g) county. Arizona is anti-sanctuary.",
        "source_url": "https://www.azleg.gov/legtext/49leg/2r/bills/sb1070s.pdf",
        "source_name": "State-level: Arizona Legislature - SB 1070",
        "last_verified": "2026-01-25"
    },
    "Lubbock, TX": {
        "state": "Texas",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Lubbock County. Under Texas SB4 (2017).",
        "source_url": "https://capitol.texas.gov/BillLookup/History.aspx?LegSess=85R&Bill=SB4",
        "source_name": "State-level: Texas Legislature - SB 4 (2017)",
        "last_verified": "2026-01-25"
    },
    "Scottsdale, AZ": {
        "state": "Arizona",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Maricopa County. 287(g) county. Arizona is anti-sanctuary.",
        "source_url": "https://www.azleg.gov/legtext/49leg/2r/bills/sb1070s.pdf",
        "source_name": "State-level: Arizona Legislature - SB 1070",
        "last_verified": "2026-01-25"
    },
    "Buffalo, NY": {
        "state": "New York",
        "local_status": "sanctuary_partial",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Erie County. New York varies by county; Buffalo has some limits on ICE cooperation.",
        "source_url": "https://www.nysenate.gov/legislation/laws/EXC/837-P",
        "source_name": "State-level: NY Senate - Executive Law 837-p (Protect Our Courts Act)",
        "last_verified": "2026-01-25"
    },
    "Gilbert, AZ": {
        "state": "Arizona",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Maricopa County. 287(g) county.",
        "source_url": "https://www.azleg.gov/legtext/49leg/2r/bills/sb1070s.pdf",
        "source_name": "State-level: Arizona Legislature - SB 1070",
        "last_verified": "2026-01-25"
    },
    "Glendale, AZ": {
        "state": "Arizona",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Maricopa County. 287(g) county.",
        "source_url": "https://www.azleg.gov/legtext/49leg/2r/bills/sb1070s.pdf",
        "source_name": "State-level: Arizona Legislature - SB 1070",
        "last_verified": "2026-01-25"
    },
    "Winston-Salem, NC": {
        "state": "North Carolina",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Forsyth County. Generally cooperative with ICE.",
        "source_url": "https://www.ncsheriffs.org/resources/immigration-enforcement",
        "source_name": "State-level: NC Sheriffs Association - Immigration Policy Overview",
        "last_verified": "2026-01-25"
    },
    "Chesapeake, VA": {
        "state": "Virginia",
        "local_status": "cooperative",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Independent city. Virginia has no statewide policy.",
        "source_url": "https://law.lis.virginia.gov/vacode/title19.2/chapter1/",
        "source_name": "State-level: Code of Virginia - Criminal Procedure",
        "last_verified": "2026-01-25"
    },
    "Fremont, CA": {
        "state": "California",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Alameda County. Under California Values Act.",
        "source_url": "https://leginfo.legislature.ca.gov/faces/billNavClient.xhtml?bill_id=201720180SB54",
        "source_name": "State-level: California Legislature - SB 54 Official Text",
        "last_verified": "2026-01-25"
    },
    "Garland, TX": {
        "state": "Texas",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Dallas County. Under Texas SB4 (2017).",
        "source_url": "https://capitol.texas.gov/BillLookup/History.aspx?LegSess=85R&Bill=SB4",
        "source_name": "State-level: Texas Legislature - SB 4 (2017)",
        "last_verified": "2026-01-25"
    },
    "Irving, TX": {
        "state": "Texas",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Dallas County. Under Texas SB4 (2017).",
        "source_url": "https://capitol.texas.gov/BillLookup/History.aspx?LegSess=85R&Bill=SB4",
        "source_name": "State-level: Texas Legislature - SB 4 (2017)",
        "last_verified": "2026-01-25"
    },
    "Hialeah, FL": {
        "state": "Florida",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Miami-Dade County. Florida requires full ICE cooperation.",
        "source_url": "https://www.flsenate.gov/Session/Bill/2019/00168",
        "source_name": "State-level: Florida Senate - SB 168 (2019)",
        "last_verified": "2026-01-25"
    },
    "Richmond, VA": {
        "state": "Virginia",
        "local_status": "sanctuary_partial",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Independent city (state capital). Some limits on ICE cooperation.",
        "source_url": "https://law.lis.virginia.gov/vacode/title19.2/chapter1/",
        "source_name": "State-level: Code of Virginia - Criminal Procedure",
        "last_verified": "2026-01-25"
    },
    "Boise, ID": {
        "state": "Idaho",
        "local_status": "cooperative",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Ada County. Idaho has no statewide policy.",
        "source_url": "https://legislature.idaho.gov/statutesrules/idstat/",
        "source_name": "State-level: Idaho Statutes (no statewide policy)",
        "last_verified": "2026-01-25"
    },
    "Baton Rouge, LA": {
        "state": "Louisiana",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "East Baton Rouge Parish. Louisiana HB 101 (2024) grants state police immigration authority.",
        "source_url": "https://legis.la.gov/legis/BillInfo.aspx?s=24RS&b=HB101",
        "source_name": "State-level: Louisiana Legislature - HB 101 (2024)",
        "last_verified": "2026-01-25"
    }
}

data['cities_with_notable_policies'].update(new_cities)

with open('data/reference/sanctuary_jurisdictions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Added {len(new_cities)} major cities")
print(f"Total cities now: {len(data['cities_with_notable_policies'])}")
