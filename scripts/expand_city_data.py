import json

with open('data/reference/sanctuary_jurisdictions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Comprehensive city/county additions based on research and incident data
new_cities = {
    # DOJ Designated Sanctuary Cities (Aug 2025)
    "Albuquerque, NM": {
        "state": "New Mexico",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "doj_designated": True,
        "notes": "DOJ designated sanctuary jurisdiction Aug 2025."
    },
    "Berkeley, CA": {
        "state": "California",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "doj_designated": True,
        "notes": "DOJ designated. One of oldest sanctuary cities (1971)."
    },
    "East Lansing, MI": {
        "state": "Michigan",
        "local_status": "sanctuary_limited",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "doj_designated": True,
        "notes": "DOJ designated sanctuary jurisdiction Aug 2025."
    },
    "Hoboken, NJ": {
        "state": "New Jersey",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "doj_designated": True,
        "notes": "DOJ designated. Part of NJ AG Directive limiting ICE cooperation."
    },
    "Jersey City, NJ": {
        "state": "New Jersey",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "doj_designated": True,
        "notes": "DOJ designated. Part of NJ AG Directive limiting ICE cooperation."
    },
    "Paterson, NJ": {
        "state": "New Jersey",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "doj_designated": True,
        "notes": "DOJ designated. Large immigrant population."
    },
    "Rochester, NY": {
        "state": "New York",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "doj_designated": True,
        "notes": "DOJ designated sanctuary jurisdiction Aug 2025."
    },
    "New Orleans, LA": {
        "state": "Louisiana",
        "local_status": "policy_conflict",
        "detainer_policy": "state_mandated",
        "policy_conflict": True,
        "doj_designated": True,
        "notes": "DOJ designated but Louisiana is anti-sanctuary state. City has historically limited cooperation but constrained by state law."
    },

    # Major cities from our incidents - Illinois
    "Broadview, IL": {
        "state": "Illinois",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "ICE Detention Center location in sanctuary state. Frequent protest site."
    },
    "Franklin Park, IL": {
        "state": "Illinois",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Chicago suburb under Illinois TRUST Act."
    },
    "Elgin, IL": {
        "state": "Illinois",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Chicago suburb under Illinois TRUST Act."
    },

    # Texas cities
    "Fort Bliss, TX": {
        "state": "Texas",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Military base used for migrant detention. Federal jurisdiction on base."
    },
    "El Paso, TX": {
        "state": "Texas",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Border city. Constrained by SB4 despite historically immigrant-friendly local attitudes."
    },
    "Alvarado, TX": {
        "state": "Texas",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Site of multiple ICE enforcement operations."
    },
    "McAllen, TX": {
        "state": "Texas",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Border city, Rio Grande Valley. Major detention processing area."
    },
    "Laredo, TX": {
        "state": "Texas",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Border city with heavy CBP/ICE presence."
    },

    # California cities
    "Camarillo, CA": {
        "state": "California",
        "local_status": "sanctuary_limited",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Ventura County. Site of ICE detention facility deaths."
    },
    "Paramount, CA": {
        "state": "California",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "LA County suburb under California Values Act."
    },
    "Van Nuys, CA": {
        "state": "California",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "LA neighborhood. Under California Values Act and LAPD Special Order 40."
    },
    "Northridge, CA": {
        "state": "California",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "LA neighborhood. Under California Values Act."
    },
    "Santa Ana, CA": {
        "state": "California",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Orange County. Large immigrant population, under California Values Act."
    },
    "San Bernardino, CA": {
        "state": "California",
        "local_status": "sanctuary_limited",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Inland Empire. Under California Values Act."
    },
    "Ontario, CA": {
        "state": "California",
        "local_status": "sanctuary_limited",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Inland Empire, San Bernardino County. Under California Values Act."
    },
    "Oakland, CA": {
        "state": "California",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Strong sanctuary policy predating state law. Mayor warned residents of ICE raids 2018."
    },
    "Montclair, CA": {
        "state": "California",
        "local_status": "sanctuary_limited",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "San Bernardino County. Under California Values Act."
    },
    "San Jose, CA": {
        "state": "California",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Under California Values Act. Santa Clara County is sanctuary."
    },
    "Sacramento, CA": {
        "state": "California",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "State capital. Under California Values Act."
    },
    "Fresno, CA": {
        "state": "California",
        "local_status": "sanctuary_limited",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Central Valley. Under California Values Act but more conservative area."
    },
    "Long Beach, CA": {
        "state": "California",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "LA County. Under California Values Act."
    },
    "Anaheim, CA": {
        "state": "California",
        "local_status": "sanctuary_limited",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Orange County. Under California Values Act."
    },

    # Colorado cities
    "Aurora, CO": {
        "state": "Colorado",
        "local_status": "sanctuary_limited",
        "detainer_policy": "honor_judicial",
        "policy_conflict": False,
        "notes": "Denver suburb. Under Colorado HB19-1124. Site of Aurora ICE detention facility."
    },

    # New York boroughs/areas
    "Manhattan, NY": {
        "state": "New York",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Part of NYC. Under NYC Executive Order 41."
    },
    "Brooklyn, NY": {
        "state": "New York",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Part of NYC. Under NYC Executive Order 41."
    },
    "Bronx, NY": {
        "state": "New York",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Part of NYC. Under NYC Executive Order 41."
    },
    "Queens, NY": {
        "state": "New York",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Part of NYC. Under NYC Executive Order 41."
    },
    "Staten Island, NY": {
        "state": "New York",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Part of NYC. Under NYC Executive Order 41."
    },

    # Georgia
    "Ellabell, GA": {
        "state": "Georgia",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Site of Hyundai Metaplant raid (475 detained). Bryan County."
    },
    "Lovejoy, GA": {
        "state": "Georgia",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Location of Robert A. Deyton Detention Center (Clayton County)."
    },

    # Washington
    "Tacoma, WA": {
        "state": "Washington",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Site of Northwest Detention Center (now Northwest ICE Processing Center). State has Keep Washington Working Act."
    },
    "SeaTac, WA": {
        "state": "Washington",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Airport area. Under Washington Keep Washington Working Act."
    },

    # Nebraska
    "Omaha, NE": {
        "state": "Nebraska",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Site of Glenn Valley Foods raid (75 detained). Nebraska is anti-sanctuary state (LB 1140)."
    },

    # Tennessee
    "Nashville, TN": {
        "state": "Tennessee",
        "local_status": "policy_conflict",
        "detainer_policy": "state_mandated",
        "policy_conflict": True,
        "notes": "Davidson County had limited cooperation policy but constrained by TN SB6002 (2025) criminalizing sanctuary policies."
    },

    # Iowa
    "Des Moines, IA": {
        "state": "Iowa",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Iowa SF 481 requires cooperation. Polk County has 287(g) agreement."
    },

    # Oklahoma
    "Oklahoma City, OK": {
        "state": "Oklahoma",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Oklahoma HB 4156 grants state police immigration authority. Oklahoma County cooperative."
    },

    # Florida
    "Tallahassee, FL": {
        "state": "Florida",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "State capital. Site of FSU campus enforcement (100 detained). Florida requires full ICE cooperation."
    },
    "Jacksonville, FL": {
        "state": "Florida",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Duval County. Florida requires full ICE cooperation."
    },
    "Tampa, FL": {
        "state": "Florida",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Hillsborough County. Florida requires full ICE cooperation."
    },
    "Orlando, FL": {
        "state": "Florida",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Orange County. Florida requires full ICE cooperation."
    },

    # Virginia
    "Norfolk, VA": {
        "state": "Virginia",
        "local_status": "cooperative",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Virginia has no statewide policy. Norfolk generally cooperative."
    },

    # Massachusetts
    "Fitchburg, MA": {
        "state": "Massachusetts",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Under Massachusetts SJC ruling that detainers are not legally binding."
    },
    "Medford, MA": {
        "state": "Massachusetts",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Under Massachusetts SJC ruling. Boston metro area."
    },

    # District of Columbia
    "Washington DC, DC": {
        "state": "District of Columbia",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "DC Sanctuary Values Act (2019). Does not honor ICE detainers."
    },

    # Missouri
    "Liberty, MO": {
        "state": "Missouri",
        "local_status": "cooperative",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Kansas City suburb. Missouri has no statewide policy."
    },
    "Kansas City, MO": {
        "state": "Missouri",
        "local_status": "sanctuary_partial",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Jackson County. Some limits on ICE cooperation. Missouri has no statewide policy."
    },
    "St. Louis, MO": {
        "state": "Missouri",
        "local_status": "sanctuary_partial",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Independent city. Some limits on ICE cooperation."
    },

    # Maryland
    "Glen Burnie, MD": {
        "state": "Maryland",
        "local_status": "sanctuary_limited",
        "detainer_policy": "honor_judicial",
        "policy_conflict": False,
        "notes": "Anne Arundel County. Under Maryland TRUST Act."
    },
    "Laurel, MD": {
        "state": "Maryland",
        "local_status": "sanctuary_limited",
        "detainer_policy": "honor_judicial",
        "policy_conflict": False,
        "notes": "Prince George's County. Under Maryland TRUST Act."
    },

    # North Carolina
    "Salisbury, NC": {
        "state": "North Carolina",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Rowan County. North Carolina varies by county; Rowan is cooperative."
    },

    # Alabama
    "Foley, AL": {
        "state": "Alabama",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Baldwin County. Alabama is anti-sanctuary (HB 56)."
    },

    # Vermont
    "Coventry, VT": {
        "state": "Vermont",
        "local_status": "sanctuary_limited",
        "detainer_policy": "honor_judicial",
        "policy_conflict": False,
        "notes": "Under Vermont Act 69. Rural area near Canadian border."
    },
    "Burlington, VT": {
        "state": "Vermont",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "Under Vermont Act 69 plus stronger local policy."
    },

    # Mississippi
    "Jackson, MS": {
        "state": "Mississippi",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "State capital. Mississippi HB 1520 is anti-sanctuary."
    },

    # Indiana
    "Indianapolis, IN": {
        "state": "Indiana",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Marion County. Indiana IC 5-2-18.2 is anti-sanctuary."
    },

    # Texas additional
    "Fort Worth, TX": {
        "state": "Texas",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Tarrant County has 287(g) agreement. Texas SB4 mandates cooperation."
    },
    "Arlington, TX": {
        "state": "Texas",
        "local_status": "cooperative",
        "detainer_policy": "state_mandated",
        "policy_conflict": False,
        "notes": "Tarrant County. Under Texas SB4."
    },

    # Pennsylvania
    "Pittsburgh, PA": {
        "state": "Pennsylvania",
        "local_status": "sanctuary_partial",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Allegheny County. Less protective than Philadelphia but some limits on ICE cooperation."
    },

    # Ohio
    "Cincinnati, OH": {
        "state": "Ohio",
        "local_status": "cooperative",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Hamilton County generally cooperative. Ohio has no statewide policy."
    },
    "Cleveland, OH": {
        "state": "Ohio",
        "local_status": "sanctuary_partial",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Cuyahoga County has some limits on ICE cooperation."
    },

    # Arizona
    "Tucson, AZ": {
        "state": "Arizona",
        "local_status": "policy_conflict",
        "detainer_policy": "honor_all",
        "policy_conflict": True,
        "notes": "City attempted sanctuary-like policies but constrained by Arizona SB 1070."
    },
    "Mesa, AZ": {
        "state": "Arizona",
        "local_status": "cooperative",
        "detainer_policy": "honor_all",
        "policy_conflict": False,
        "notes": "Maricopa County. 287(g) county. Arizona is anti-sanctuary."
    },

    # Nevada
    "Reno, NV": {
        "state": "Nevada",
        "local_status": "sanctuary_partial",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Washoe County. Similar to Las Vegas Metro - limited cooperation."
    },

    # Utah
    "Salt Lake City, UT": {
        "state": "Utah",
        "local_status": "sanctuary_partial",
        "detainer_policy": "case_by_case",
        "policy_conflict": False,
        "notes": "Some local limits on ICE cooperation despite no state policy."
    },

    # Rhode Island
    "Providence, RI": {
        "state": "Rhode Island",
        "local_status": "sanctuary_limited",
        "detainer_policy": "honor_judicial",
        "policy_conflict": False,
        "notes": "Under Rhode Island executive order limiting ICE cooperation."
    },

    # Connecticut
    "Hartford, CT": {
        "state": "Connecticut",
        "local_status": "sanctuary_limited",
        "detainer_policy": "honor_judicial",
        "policy_conflict": False,
        "notes": "Under Connecticut TRUST Act."
    },
    "New Haven, CT": {
        "state": "Connecticut",
        "local_status": "sanctuary_strong",
        "detainer_policy": "decline_all",
        "policy_conflict": False,
        "notes": "First city to issue municipal ID cards to undocumented residents (2007). Strong local sanctuary."
    }
}

# Add to reference data
data['cities_with_notable_policies'].update(new_cities)

# Save
with open('data/reference/sanctuary_jurisdictions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Added {len(new_cities)} cities/localities")
print(f"Total cities now: {len(data['cities_with_notable_policies'])}")
