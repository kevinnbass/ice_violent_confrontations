import json
import os
from collections import Counter
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import warnings
warnings.filterwarnings('ignore')

# City to County mapping (FIPS codes and county names)
CITY_TO_COUNTY = {
    # Illinois
    "Broadview, Illinois": ("Cook County", "17", "031"),
    "Chicago, Illinois": ("Cook County", "17", "031"),
    "Cicero, Illinois": ("Cook County", "17", "031"),
    "Evanston, Illinois": ("Cook County", "17", "031"),
    "Elgin, Illinois": ("Kane County", "17", "089"),
    "Chicago and surrounding area, Illinois": ("Cook County", "17", "031"),

    # Minnesota
    "Minneapolis, Minnesota": ("Hennepin County", "27", "053"),
    "Minneapolis (Federal Building), Minnesota": ("Hennepin County", "27", "053"),
    "St. Paul, Minnesota": ("Ramsey County", "27", "123"),
    "Minneapolis-St. Paul Airport, Minnesota": ("Hennepin County", "27", "053"),
    "Statewide, Minnesota": ("Hennepin County", "27", "053"),

    # California
    "Los Angeles, California": ("Los Angeles County", "06", "037"),
    "Los Angeles (Grand Park), California": ("Los Angeles County", "06", "037"),
    "Northridge, Los Angeles, California": ("Los Angeles County", "06", "037"),
    "Van Nuys, California": ("Los Angeles County", "06", "037"),
    "Paramount, California": ("Los Angeles County", "06", "037"),
    "San Francisco, California": ("San Francisco County", "06", "075"),
    "Oakland, California": ("Alameda County", "06", "001"),
    "Santa Ana, California": ("Orange County", "06", "059"),
    "Anaheim, California": ("Orange County", "06", "059"),
    "San Diego, California": ("San Diego County", "06", "073"),
    "Sacramento, California": ("Sacramento County", "06", "067"),
    "San Jose, California": ("Santa Clara County", "06", "085"),
    "Fresno, California": ("Fresno County", "06", "019"),
    "Bakersfield, California": ("Kern County", "06", "029"),
    "Riverside, California": ("Riverside County", "06", "065"),
    "Long Beach, California": ("Los Angeles County", "06", "037"),
    "Pasadena, California": ("Los Angeles County", "06", "037"),
    "Glendale, California": ("Los Angeles County", "06", "037"),
    "Santa Monica, California": ("Los Angeles County", "06", "037"),
    "Pomona, California": ("Los Angeles County", "06", "037"),
    "Torrance, California": ("Los Angeles County", "06", "037"),
    "Santa Clarita, California": ("Los Angeles County", "06", "037"),
    "Irvine, California": ("Orange County", "06", "059"),
    "Ontario, California": ("San Bernardino County", "06", "071"),
    "Dublin, California": ("Alameda County", "06", "001"),
    "Los Angeles area, California": ("Los Angeles County", "06", "037"),
    "McCain Valley (near Mexico border), California": ("San Diego County", "06", "073"),
    "Camarillo/Oxnard Plain, Ventura County, California": ("Ventura County", "06", "111"),
    "Camarillo area, California": ("Ventura County", "06", "111"),
    "Adelanto, California": ("San Bernardino County", "06", "071"),
    "Indio, California": ("Riverside County", "06", "065"),
    "Stockton, California": ("San Joaquin County", "06", "077"),
    "Modesto, California": ("Stanislaus County", "06", "099"),
    "Salinas, California": ("Monterey County", "06", "053"),
    "Santa Cruz, California": ("Santa Cruz County", "06", "087"),
    "Santa Barbara, California": ("Santa Barbara County", "06", "083"),
    "Ventura, California": ("Ventura County", "06", "111"),
    "Oxnard, California": ("Ventura County", "06", "111"),
    "El Centro, California": ("Imperial County", "06", "025"),
    "Redding, California": ("Shasta County", "06", "089"),
    "Chico, California": ("Butte County", "06", "007"),
    "Merced, California": ("Merced County", "06", "047"),
    "Visalia, California": ("Tulare County", "06", "107"),
    "Hanford, California": ("Kings County", "06", "031"),
    "San Bernardino, California": ("San Bernardino County", "06", "071"),
    "Fontana, California": ("San Bernardino County", "06", "071"),
    "Moreno Valley, California": ("Riverside County", "06", "065"),
    "Corona, California": ("Riverside County", "06", "065"),
    "Escondido, California": ("San Diego County", "06", "073"),
    "Oceanside, California": ("San Diego County", "06", "073"),
    "Carlsbad, California": ("San Diego County", "06", "073"),
    "Chula Vista, California": ("San Diego County", "06", "073"),
    "National City, California": ("San Diego County", "06", "073"),
    "El Cajon, California": ("San Diego County", "06", "073"),
    "Garden Grove, California": ("Orange County", "06", "059"),
    "Huntington Beach, California": ("Orange County", "06", "059"),
    "Costa Mesa, California": ("Orange County", "06", "059"),
    "Newport Beach, California": ("Orange County", "06", "059"),
    "Fullerton, California": ("Orange County", "06", "059"),
    "Orange, California": ("Orange County", "06", "059"),
    "Compton, California": ("Los Angeles County", "06", "037"),
    "Inglewood, California": ("Los Angeles County", "06", "037"),
    "Downey, California": ("Los Angeles County", "06", "037"),
    "Norwalk, California": ("Los Angeles County", "06", "037"),
    "West Covina, California": ("Los Angeles County", "06", "037"),
    "El Monte, California": ("Los Angeles County", "06", "037"),
    "Carson, California": ("Los Angeles County", "06", "037"),
    "Lakewood, California": ("Los Angeles County", "06", "037"),
    "Hawthorne, California": ("Los Angeles County", "06", "037"),
    "Bellflower, California": ("Los Angeles County", "06", "037"),
    "Baldwin Park, California": ("Los Angeles County", "06", "037"),
    "Lynwood, California": ("Los Angeles County", "06", "037"),
    "South Gate, California": ("Los Angeles County", "06", "037"),
    "Alhambra, California": ("Los Angeles County", "06", "037"),
    "Burbank, California": ("Los Angeles County", "06", "037"),
    "Lancaster, California": ("Los Angeles County", "06", "037"),
    "Palmdale, California": ("Los Angeles County", "06", "037"),
    "Pomona, California": ("Los Angeles County", "06", "037"),
    "Whittier, California": ("Los Angeles County", "06", "037"),
    "Monterey Park, California": ("Los Angeles County", "06", "037"),
    "Arcadia, California": ("Los Angeles County", "06", "037"),
    "Redondo Beach, California": ("Los Angeles County", "06", "037"),
    "Berkeley, California": ("Alameda County", "06", "001"),
    "Fremont, California": ("Alameda County", "06", "001"),
    "Hayward, California": ("Alameda County", "06", "001"),
    "Richmond, California": ("Contra Costa County", "06", "013"),
    "Concord, California": ("Contra Costa County", "06", "013"),
    "Antioch, California": ("Contra Costa County", "06", "013"),
    "Vallejo, California": ("Solano County", "06", "095"),
    "Fairfield, California": ("Solano County", "06", "095"),
    "Daly City, California": ("San Mateo County", "06", "081"),
    "San Mateo, California": ("San Mateo County", "06", "081"),
    "Redwood City, California": ("San Mateo County", "06", "081"),
    "South San Francisco, California": ("San Mateo County", "06", "081"),
    "Sunnyvale, California": ("Santa Clara County", "06", "085"),
    "Santa Clara, California": ("Santa Clara County", "06", "085"),
    "Mountain View, California": ("Santa Clara County", "06", "085"),
    "Palo Alto, California": ("Santa Clara County", "06", "085"),
    "Milpitas, California": ("Santa Clara County", "06", "085"),
    "Gilroy, California": ("Santa Clara County", "06", "085"),
    "Watsonville, California": ("Santa Cruz County", "06", "087"),
    "Napa, California": ("Napa County", "06", "055"),
    "Santa Rosa, California": ("Sonoma County", "06", "097"),
    "Petaluma, California": ("Sonoma County", "06", "097"),
    "San Rafael, California": ("Marin County", "06", "041"),
    "Novato, California": ("Marin County", "06", "041"),
    "Lodi, California": ("San Joaquin County", "06", "077"),
    "Tracy, California": ("San Joaquin County", "06", "077"),
    "Manteca, California": ("San Joaquin County", "06", "077"),

    # Oregon
    "Portland, Oregon": ("Multnomah County", "41", "051"),
    "Eugene, Oregon": ("Lane County", "41", "039"),
    "Salem, Oregon": ("Marion County", "41", "047"),
    "Medford, Oregon": ("Jackson County", "41", "029"),
    "Bend, Oregon": ("Deschutes County", "41", "017"),

    # Texas
    "Houston, Texas": ("Harris County", "48", "201"),
    "Austin, Texas": ("Travis County", "48", "453"),
    "Dallas, Texas": ("Dallas County", "48", "113"),
    "San Antonio, Texas": ("Bexar County", "48", "029"),
    "Fort Worth, Texas": ("Tarrant County", "48", "439"),
    "El Paso, Texas": ("El Paso County", "48", "141"),
    "Alvarado, Texas": ("Johnson County", "48", "251"),
    "Plano, Texas": ("Collin County", "48", "085"),
    "Arlington, Texas": ("Tarrant County", "48", "439"),
    "McAllen, Texas": ("Hidalgo County", "48", "215"),
    "Rio Grande / CBP Checkpoint, Texas": ("Hidalgo County", "48", "215"),
    "Brownsville, Texas": ("Cameron County", "48", "061"),
    "Laredo, Texas": ("Webb County", "48", "479"),
    "Corpus Christi, Texas": ("Nueces County", "48", "355"),
    "Lubbock, Texas": ("Lubbock County", "48", "303"),
    "Amarillo, Texas": ("Potter County", "48", "375"),
    "Irving, Texas": ("Dallas County", "48", "113"),
    "Garland, Texas": ("Dallas County", "48", "113"),
    "Grand Prairie, Texas": ("Dallas County", "48", "113"),
    "Mesquite, Texas": ("Dallas County", "48", "113"),
    "Carrollton, Texas": ("Dallas County", "48", "113"),
    "Denton, Texas": ("Denton County", "48", "121"),
    "Lewisville, Texas": ("Denton County", "48", "121"),
    "McKinney, Texas": ("Collin County", "48", "085"),
    "Frisco, Texas": ("Collin County", "48", "085"),
    "Pasadena, Texas": ("Harris County", "48", "201"),
    "Baytown, Texas": ("Harris County", "48", "201"),
    "Sugar Land, Texas": ("Fort Bend County", "48", "157"),
    "The Woodlands, Texas": ("Montgomery County", "48", "339"),
    "Conroe, Texas": ("Montgomery County", "48", "339"),
    "Beaumont, Texas": ("Jefferson County", "48", "245"),
    "Waco, Texas": ("McLennan County", "48", "309"),
    "Midland, Texas": ("Midland County", "48", "329"),
    "Odessa, Texas": ("Ector County", "48", "135"),
    "Tyler, Texas": ("Smith County", "48", "423"),
    "Abilene, Texas": ("Taylor County", "48", "441"),
    "Wichita Falls, Texas": ("Wichita County", "48", "485"),
    "Pharr, Texas": ("Hidalgo County", "48", "215"),
    "Mission, Texas": ("Hidalgo County", "48", "215"),
    "Edinburg, Texas": ("Hidalgo County", "48", "215"),
    "Harlingen, Texas": ("Cameron County", "48", "061"),

    # New York
    "New York, New York": ("New York County", "36", "061"),
    "New York (Downtown Manhattan), New York": ("New York County", "36", "061"),
    "New York City, New York": ("New York County", "36", "061"),
    "Brooklyn, New York": ("Kings County", "36", "047"),
    "Queens, New York": ("Queens County", "36", "081"),
    "Bronx, New York": ("Bronx County", "36", "005"),
    "Staten Island, New York": ("Richmond County", "36", "085"),
    "Buffalo, New York": ("Erie County", "36", "029"),
    "Manhattan (SoHo/Canal St), New York": ("New York County", "36", "061"),
    "Manhattan (Canal Street), New York": ("New York County", "36", "061"),
    "Manhattan (26 Federal Plaza), New York": ("New York County", "36", "061"),
    "Rochester, New York": ("Monroe County", "36", "055"),
    "Syracuse, New York": ("Onondaga County", "36", "067"),
    "Albany, New York": ("Albany County", "36", "001"),
    "Yonkers, New York": ("Westchester County", "36", "119"),
    "White Plains, New York": ("Westchester County", "36", "119"),
    "New Rochelle, New York": ("Westchester County", "36", "119"),
    "Long Island, New York": ("Nassau County", "36", "059"),
    "Hempstead, New York": ("Nassau County", "36", "059"),
    "Freeport, New York": ("Nassau County", "36", "059"),
    "Brentwood, New York": ("Suffolk County", "36", "103"),

    # Washington
    "Seattle, Washington": ("King County", "53", "033"),
    "Tacoma, Washington": ("Pierce County", "53", "053"),
    "Spokane, Washington": ("Spokane County", "53", "063"),
    "SeaTac/Tacoma, Washington": ("King County", "53", "033"),
    "Vancouver, Washington": ("Clark County", "53", "011"),
    "Bellevue, Washington": ("King County", "53", "033"),
    "Kent, Washington": ("King County", "53", "033"),
    "Everett, Washington": ("Snohomish County", "53", "061"),
    "Olympia, Washington": ("Thurston County", "53", "067"),
    "Yakima, Washington": ("Yakima County", "53", "077"),

    # New Jersey
    "Newark, New Jersey": ("Essex County", "34", "013"),
    "Jersey City, New Jersey": ("Hudson County", "34", "017"),
    "Elizabeth, New Jersey": ("Union County", "34", "039"),
    "Paterson, New Jersey": ("Passaic County", "34", "031"),
    "Trenton, New Jersey": ("Mercer County", "34", "021"),
    "Camden, New Jersey": ("Camden County", "34", "007"),
    "Atlantic City, New Jersey": ("Atlantic County", "34", "001"),
    "New Brunswick, New Jersey": ("Middlesex County", "34", "023"),
    "Edison, New Jersey": ("Middlesex County", "34", "023"),
    "Woodbridge, New Jersey": ("Middlesex County", "34", "023"),

    # Colorado
    "Denver, Colorado": ("Denver County", "08", "031"),
    "Aurora, Colorado": ("Arapahoe County", "08", "005"),
    "Colorado Springs, Colorado": ("El Paso County", "08", "041"),
    "Durango, Colorado": ("La Plata County", "08", "067"),
    "Durango (ICE field office), Colorado": ("La Plata County", "08", "067"),
    "Aurora/Denver, Colorado": ("Denver County", "08", "031"),
    "Boulder, Colorado": ("Boulder County", "08", "013"),
    "Fort Collins, Colorado": ("Larimer County", "08", "069"),
    "Lakewood, Colorado": ("Jefferson County", "08", "059"),
    "Thornton, Colorado": ("Adams County", "08", "001"),
    "Greeley, Colorado": ("Weld County", "08", "123"),
    "Pueblo, Colorado": ("Pueblo County", "08", "101"),

    # Georgia
    "Atlanta, Georgia": ("Fulton County", "13", "121"),
    "Savannah, Georgia": ("Chatham County", "13", "051"),
    "DeKalb County (Atlanta area), Georgia": ("DeKalb County", "13", "089"),
    "Brookhaven, Georgia": ("DeKalb County", "13", "089"),
    "Augusta, Georgia": ("Richmond County", "13", "245"),
    "Columbus, Georgia": ("Muscogee County", "13", "215"),
    "Macon, Georgia": ("Bibb County", "13", "021"),
    "Athens, Georgia": ("Clarke County", "13", "059"),
    "Marietta, Georgia": ("Cobb County", "13", "067"),
    "Sandy Springs, Georgia": ("Fulton County", "13", "121"),
    "Roswell, Georgia": ("Fulton County", "13", "121"),
    "Alpharetta, Georgia": ("Fulton County", "13", "121"),

    # Florida
    "Miami, Florida": ("Miami-Dade County", "12", "086"),
    "Orlando, Florida": ("Orange County", "12", "095"),
    "Tampa, Florida": ("Hillsborough County", "12", "057"),
    "Jacksonville, Florida": ("Duval County", "12", "031"),
    "Riviera Beach, Florida": ("Palm Beach County", "12", "099"),
    "Fort Lauderdale, Florida": ("Broward County", "12", "011"),
    "Hollywood, Florida": ("Broward County", "12", "011"),
    "Pembroke Pines, Florida": ("Broward County", "12", "011"),
    "Hialeah, Florida": ("Miami-Dade County", "12", "086"),
    "Miami Beach, Florida": ("Miami-Dade County", "12", "086"),
    "Homestead, Florida": ("Miami-Dade County", "12", "086"),
    "Kendall, Florida": ("Miami-Dade County", "12", "086"),
    "West Palm Beach, Florida": ("Palm Beach County", "12", "099"),
    "Boca Raton, Florida": ("Palm Beach County", "12", "099"),
    "Delray Beach, Florida": ("Palm Beach County", "12", "099"),
    "St. Petersburg, Florida": ("Pinellas County", "12", "103"),
    "Clearwater, Florida": ("Pinellas County", "12", "103"),
    "Fort Myers, Florida": ("Lee County", "12", "071"),
    "Cape Coral, Florida": ("Lee County", "12", "071"),
    "Naples, Florida": ("Collier County", "12", "021"),
    "Gainesville, Florida": ("Alachua County", "12", "001"),
    "Tallahassee, Florida": ("Leon County", "12", "073"),
    "Pensacola, Florida": ("Escambia County", "12", "033"),
    "Sarasota, Florida": ("Sarasota County", "12", "115"),
    "Bradenton, Florida": ("Manatee County", "12", "081"),
    "Lakeland, Florida": ("Polk County", "12", "105"),
    "Kissimmee, Florida": ("Osceola County", "12", "097"),
    "Melbourne, Florida": ("Brevard County", "12", "009"),
    "Daytona Beach, Florida": ("Volusia County", "12", "127"),
    "Ocala, Florida": ("Marion County", "12", "083"),

    # Massachusetts
    "Boston, Massachusetts": ("Suffolk County", "25", "025"),
    "Cambridge, Massachusetts": ("Middlesex County", "25", "017"),
    "Medford, Massachusetts": ("Middlesex County", "25", "017"),
    "Worcester, Massachusetts": ("Worcester County", "25", "027"),
    "Springfield, Massachusetts": ("Hampden County", "25", "013"),
    "Lowell, Massachusetts": ("Middlesex County", "25", "017"),
    "Brockton, Massachusetts": ("Plymouth County", "25", "023"),
    "New Bedford, Massachusetts": ("Bristol County", "25", "005"),
    "Fall River, Massachusetts": ("Bristol County", "25", "005"),
    "Lynn, Massachusetts": ("Essex County", "25", "009"),
    "Lawrence, Massachusetts": ("Essex County", "25", "009"),

    # Louisiana
    "New Orleans, Louisiana": ("Orleans Parish", "22", "071"),
    "Baton Rouge, Louisiana": ("East Baton Rouge Parish", "22", "033"),
    "Baton Rouge / Honduras, Louisiana": ("East Baton Rouge Parish", "22", "033"),
    "New Orleans area, Louisiana": ("Orleans Parish", "22", "071"),
    "Angola (Camp 57), Louisiana": ("West Feliciana Parish", "22", "125"),
    "Shreveport, Louisiana": ("Caddo Parish", "22", "017"),
    "Lafayette, Louisiana": ("Lafayette Parish", "22", "055"),
    "Lake Charles, Louisiana": ("Calcasieu Parish", "22", "019"),
    "Monroe, Louisiana": ("Ouachita Parish", "22", "073"),
    "Alexandria, Louisiana": ("Rapides Parish", "22", "079"),

    # Oklahoma
    "Oklahoma City, Oklahoma": ("Oklahoma County", "40", "109"),
    "Tulsa, Oklahoma": ("Tulsa County", "40", "143"),
    "Norman, Oklahoma": ("Cleveland County", "40", "027"),
    "Lawton, Oklahoma": ("Comanche County", "40", "031"),
    "Broken Arrow, Oklahoma": ("Tulsa County", "40", "143"),
    "Edmond, Oklahoma": ("Oklahoma County", "40", "109"),

    # North Carolina
    "Charlotte, North Carolina": ("Mecklenburg County", "37", "119"),
    "Raleigh, North Carolina": ("Wake County", "37", "183"),
    "Salisbury, North Carolina": ("Rowan County", "37", "159"),
    "Greensboro, North Carolina": ("Guilford County", "37", "081"),
    "Durham, North Carolina": ("Durham County", "37", "063"),
    "Winston-Salem, North Carolina": ("Forsyth County", "37", "067"),
    "Fayetteville, North Carolina": ("Cumberland County", "37", "051"),
    "Wilmington, North Carolina": ("New Hanover County", "37", "129"),
    "Asheville, North Carolina": ("Buncombe County", "37", "021"),

    # Maryland
    "Baltimore, Maryland": ("Baltimore City", "24", "510"),
    "Laurel, Maryland": ("Prince George's County", "24", "033"),
    "Silver Spring, Maryland": ("Montgomery County", "24", "031"),
    "Bethesda, Maryland": ("Montgomery County", "24", "031"),
    "Rockville, Maryland": ("Montgomery County", "24", "031"),
    "Frederick, Maryland": ("Frederick County", "24", "021"),
    "Annapolis, Maryland": ("Anne Arundel County", "24", "003"),

    # Wisconsin
    "Milwaukee, Wisconsin": ("Milwaukee County", "55", "079"),
    "Madison, Wisconsin": ("Dane County", "55", "025"),
    "Green Bay, Wisconsin": ("Brown County", "55", "009"),
    "Kenosha, Wisconsin": ("Kenosha County", "55", "059"),
    "Racine, Wisconsin": ("Racine County", "55", "101"),
    "Appleton, Wisconsin": ("Outagamie County", "55", "087"),

    # Alabama
    "Birmingham, Alabama": ("Jefferson County", "01", "073"),
    "Foley, Alabama": ("Baldwin County", "01", "003"),
    "Montgomery, Alabama": ("Montgomery County", "01", "101"),
    "Mobile, Alabama": ("Mobile County", "01", "097"),
    "Huntsville, Alabama": ("Madison County", "01", "089"),
    "Tuscaloosa, Alabama": ("Tuscaloosa County", "01", "125"),

    # Nevada
    "Las Vegas, Nevada": ("Clark County", "32", "003"),
    "Reno, Nevada": ("Washoe County", "32", "031"),
    "Henderson, Nevada": ("Clark County", "32", "003"),
    "North Las Vegas, Nevada": ("Clark County", "32", "003"),

    # Arizona
    "Phoenix, Arizona": ("Maricopa County", "04", "013"),
    "Tucson, Arizona": ("Pima County", "04", "019"),
    "Phoenix/Peoria, Arizona": ("Maricopa County", "04", "013"),
    "Mesa, Arizona": ("Maricopa County", "04", "013"),
    "Chandler, Arizona": ("Maricopa County", "04", "013"),
    "Scottsdale, Arizona": ("Maricopa County", "04", "013"),
    "Gilbert, Arizona": ("Maricopa County", "04", "013"),
    "Glendale, Arizona": ("Maricopa County", "04", "013"),
    "Tempe, Arizona": ("Maricopa County", "04", "013"),
    "Peoria, Arizona": ("Maricopa County", "04", "013"),
    "Surprise, Arizona": ("Maricopa County", "04", "013"),
    "Yuma, Arizona": ("Yuma County", "04", "027"),
    "Flagstaff, Arizona": ("Coconino County", "04", "005"),

    # Pennsylvania
    "Philadelphia, Pennsylvania": ("Philadelphia County", "42", "101"),
    "Pittsburgh, Pennsylvania": ("Allegheny County", "42", "003"),
    "Allentown, Pennsylvania": ("Lehigh County", "42", "077"),
    "Reading, Pennsylvania": ("Berks County", "42", "011"),
    "Erie, Pennsylvania": ("Erie County", "42", "049"),
    "Scranton, Pennsylvania": ("Lackawanna County", "42", "069"),
    "Harrisburg, Pennsylvania": ("Dauphin County", "42", "043"),
    "Lancaster, Pennsylvania": ("Lancaster County", "42", "071"),
    "Bethlehem, Pennsylvania": ("Northampton County", "42", "095"),
    "York, Pennsylvania": ("York County", "42", "133"),

    # District of Columbia
    "Washington, District of Columbia": ("District of Columbia", "11", "001"),
    "Washington, D.C.": ("District of Columbia", "11", "001"),
    "Washington DC, District of Columbia": ("District of Columbia", "11", "001"),

    # Rhode Island
    "Providence, Rhode Island": ("Providence County", "44", "007"),
    "Warwick, Rhode Island": ("Kent County", "44", "003"),
    "Cranston, Rhode Island": ("Providence County", "44", "007"),
    "Pawtucket, Rhode Island": ("Providence County", "44", "007"),

    # Iowa
    "Des Moines, Iowa": ("Polk County", "19", "153"),
    "Cedar Rapids, Iowa": ("Linn County", "19", "113"),
    "Davenport, Iowa": ("Scott County", "19", "163"),
    "Sioux City, Iowa": ("Woodbury County", "19", "193"),
    "Iowa City, Iowa": ("Johnson County", "19", "103"),
    "Waterloo, Iowa": ("Black Hawk County", "19", "013"),

    # Michigan
    "Detroit, Michigan": ("Wayne County", "26", "163"),
    "Ann Arbor, Michigan": ("Washtenaw County", "26", "161"),
    "Grand Rapids, Michigan": ("Kent County", "26", "081"),
    "Lansing, Michigan": ("Ingham County", "26", "065"),
    "Flint, Michigan": ("Genesee County", "26", "049"),
    "Dearborn, Michigan": ("Wayne County", "26", "163"),
    "Sterling Heights, Michigan": ("Macomb County", "26", "099"),
    "Warren, Michigan": ("Macomb County", "26", "099"),
    "Kalamazoo, Michigan": ("Kalamazoo County", "26", "077"),

    # South Carolina
    "Charleston, South Carolina": ("Charleston County", "45", "019"),
    "Columbia, South Carolina": ("Richland County", "45", "079"),
    "Greenville, South Carolina": ("Greenville County", "45", "045"),
    "Myrtle Beach, South Carolina": ("Horry County", "45", "051"),
    "North Charleston, South Carolina": ("Charleston County", "45", "019"),

    # Utah
    "Salt Lake City, Utah": ("Salt Lake County", "49", "035"),
    "West Valley City, Utah": ("Salt Lake County", "49", "035"),
    "Provo, Utah": ("Utah County", "49", "049"),
    "West Jordan, Utah": ("Salt Lake County", "49", "035"),
    "Orem, Utah": ("Utah County", "49", "049"),
    "Sandy, Utah": ("Salt Lake County", "49", "035"),
    "Ogden, Utah": ("Weber County", "49", "057"),
    "St. George, Utah": ("Washington County", "49", "053"),

    # Tennessee
    "Nashville, Tennessee": ("Davidson County", "47", "037"),
    "Memphis, Tennessee": ("Shelby County", "47", "157"),
    "Knoxville, Tennessee": ("Knox County", "47", "093"),
    "Chattanooga, Tennessee": ("Hamilton County", "47", "065"),
    "Clarksville, Tennessee": ("Montgomery County", "47", "125"),
    "Murfreesboro, Tennessee": ("Rutherford County", "47", "149"),
    "Franklin, Tennessee": ("Williamson County", "47", "187"),

    # Missouri
    "Kansas City, Missouri": ("Jackson County", "29", "095"),
    "St. Louis, Missouri": ("St. Louis City", "29", "510"),
    "Springfield, Missouri": ("Greene County", "29", "077"),
    "Columbia, Missouri": ("Boone County", "29", "019"),
    "Independence, Missouri": ("Jackson County", "29", "095"),

    # Indiana
    "Indianapolis, Indiana": ("Marion County", "18", "097"),
    "Fort Wayne, Indiana": ("Allen County", "18", "003"),
    "Evansville, Indiana": ("Vanderburgh County", "18", "163"),
    "South Bend, Indiana": ("St. Joseph County", "18", "141"),
    "Carmel, Indiana": ("Hamilton County", "18", "057"),
    "Hammond, Indiana": ("Lake County", "18", "089"),
    "Gary, Indiana": ("Lake County", "18", "089"),

    # Ohio
    "Columbus, Ohio": ("Franklin County", "39", "049"),
    "Cleveland, Ohio": ("Cuyahoga County", "39", "035"),
    "Cincinnati, Ohio": ("Hamilton County", "39", "061"),
    "Toledo, Ohio": ("Lucas County", "39", "095"),
    "Akron, Ohio": ("Summit County", "39", "153"),
    "Dayton, Ohio": ("Montgomery County", "39", "113"),
    "Canton, Ohio": ("Stark County", "39", "151"),
    "Youngstown, Ohio": ("Mahoning County", "39", "099"),

    # Virginia
    "Virginia Beach, Virginia": ("Virginia Beach City", "51", "810"),
    "Norfolk, Virginia": ("Norfolk City", "51", "710"),
    "Chesapeake, Virginia": ("Chesapeake City", "51", "550"),
    "Richmond, Virginia": ("Richmond City", "51", "760"),
    "Newport News, Virginia": ("Newport News City", "51", "700"),
    "Arlington, Virginia": ("Arlington County", "51", "013"),
    "Alexandria, Virginia": ("Alexandria City", "51", "510"),
    "Hampton, Virginia": ("Hampton City", "51", "650"),
    "Roanoke, Virginia": ("Roanoke City", "51", "770"),

    # Connecticut
    "Hartford, Connecticut": ("Hartford County", "09", "003"),
    "New Haven, Connecticut": ("New Haven County", "09", "009"),
    "Bridgeport, Connecticut": ("Fairfield County", "09", "001"),
    "Stamford, Connecticut": ("Fairfield County", "09", "001"),
    "Waterbury, Connecticut": ("New Haven County", "09", "009"),
    "Norwalk, Connecticut": ("Fairfield County", "09", "001"),

    # Kentucky
    "Louisville, Kentucky": ("Jefferson County", "21", "111"),
    "Lexington, Kentucky": ("Fayette County", "21", "067"),
    "Bowling Green, Kentucky": ("Warren County", "21", "227"),
    "Owensboro, Kentucky": ("Daviess County", "21", "059"),
    "Covington, Kentucky": ("Kenton County", "21", "117"),

    # Kansas
    "Wichita, Kansas": ("Sedgwick County", "20", "173"),
    "Kansas City, Kansas": ("Wyandotte County", "20", "209"),
    "Overland Park, Kansas": ("Johnson County", "20", "091"),
    "Olathe, Kansas": ("Johnson County", "20", "091"),
    "Topeka, Kansas": ("Shawnee County", "20", "177"),
    "Lawrence, Kansas": ("Douglas County", "20", "045"),

    # Nebraska
    "Omaha, Nebraska": ("Douglas County", "31", "055"),
    "Lincoln, Nebraska": ("Lancaster County", "31", "109"),
    "Grand Island, Nebraska": ("Hall County", "31", "079"),

    # New Mexico
    "Albuquerque, New Mexico": ("Bernalillo County", "35", "001"),
    "Las Cruces, New Mexico": ("Dona Ana County", "35", "013"),
    "Santa Fe, New Mexico": ("Santa Fe County", "35", "049"),
    "Rio Rancho, New Mexico": ("Sandoval County", "35", "043"),

    # West Virginia
    "Charleston, West Virginia": ("Kanawha County", "54", "039"),
    "Huntington, West Virginia": ("Cabell County", "54", "011"),
    "Morgantown, West Virginia": ("Monongalia County", "54", "061"),

    # Arkansas
    "Little Rock, Arkansas": ("Pulaski County", "05", "119"),
    "Fort Smith, Arkansas": ("Sebastian County", "05", "131"),
    "Fayetteville, Arkansas": ("Washington County", "05", "143"),
    "Springdale, Arkansas": ("Washington County", "05", "143"),
    "Bentonville, Arkansas": ("Benton County", "05", "007"),

    # Mississippi
    "Jackson, Mississippi": ("Hinds County", "28", "049"),
    "Gulfport, Mississippi": ("Harrison County", "28", "047"),
    "Biloxi, Mississippi": ("Harrison County", "28", "047"),
    "Hattiesburg, Mississippi": ("Forrest County", "28", "035"),
    "Southaven, Mississippi": ("DeSoto County", "28", "033"),
    "Jackson area, Mississippi": ("Hinds County", "28", "049"),
    "Pass Christian (Gulf Coast), Mississippi": ("Harrison County", "28", "047"),

    # Additional mappings for unmapped cities
    "Fort Bliss, Texas": ("El Paso County", "48", "141"),
    "Newark (Delaney Hall), New Jersey": ("Essex County", "34", "013"),
    "Franklin Park, Illinois": ("Cook County", "17", "031"),
    "Fitchburg, Massachusetts": ("Worcester County", "25", "027"),
    "Baltimore (Highlandtown), Maryland": ("Baltimore City", "24", "510"),
    "Montclair, California": ("San Bernardino County", "06", "071"),
    "Starr County (near Rio Grande City), Texas": ("Starr County", "48", "427"),
    "Rio Grande City (Starr County), Texas": ("Starr County", "48", "427"),
    "Camarillo, California": ("Ventura County", "06", "111"),
    "Chicago (Brighton Park), Illinois": ("Cook County", "17", "031"),
    "Phoenix (I-17), Arizona": ("Maricopa County", "04", "013"),
    "Glen Burnie, Maryland": ("Anne Arundel County", "24", "003"),
    "Los Angeles (Home Depot protest), California": ("Los Angeles County", "06", "037"),
    "Chicago (Little Village), Illinois": ("Cook County", "17", "031"),
    "Los Angeles (downtown), California": ("Los Angeles County", "06", "037"),
    "Minneapolis (Near North), Minnesota": ("Hennepin County", "27", "053"),
    "Minneapolis (Linden Hills), Minnesota": ("Hennepin County", "27", "053"),
    "Minneapolis (26th & Nicollet), Minnesota": ("Hennepin County", "27", "053"),
    "Chicago (Lincoln Square), Illinois": ("Cook County", "17", "031"),
    "Los Angeles (Encino), California": ("Los Angeles County", "06", "037"),
    "Miami (Port of Miami), Florida": ("Miami-Dade County", "12", "086"),
    "New Orleans (deported to Honduras), Louisiana": ("Orleans Parish", "22", "071"),
    "Austin (deported to Honduras), Texas": ("Travis County", "48", "453"),
    "Los Angeles (Paramount), California": ("Los Angeles County", "06", "037"),
    "Manhattan (SoHo/Chinatown), New York": ("New York County", "36", "061"),
    "Portland (North), Oregon": ("Multnomah County", "41", "051"),
    "Ellabell (Hyundai plant), Georgia": ("Bryan County", "13", "029"),
    "Ellabell, Bryan County, Georgia": ("Bryan County", "13", "029"),
    "Ellabell (Hyundai Metaplant), Georgia": ("Bryan County", "13", "029"),
    "Charlottesville (Albemarle Courthouse), Virginia": ("Albemarle County", "51", "003"),
    "Calcasieu Parish, Louisiana": ("Calcasieu Parish", "22", "019"),
    "Nashville (South Nashville), Tennessee": ("Davidson County", "47", "037"),
    "Memphis area, Tennessee": ("Shelby County", "47", "157"),
    "Iowa City, Iowa": ("Johnson County", "19", "103"),
    "Northwest Indiana (I-94/I-80), Indiana": ("Lake County", "18", "089"),
    "Evansville/Bloomington, Indiana": ("Vanderburgh County", "18", "163"),
    "Seymour, Indiana": ("Jackson County", "18", "079"),
    "SeaTac, Washington": ("King County", "53", "033"),
    "I-40 (Beckham County), Oklahoma": ("Beckham County", "40", "009"),
    "Las Vegas (Downtown), Nevada": ("Clark County", "32", "003"),
    "Dallas-Fort Worth, Texas": ("Dallas County", "48", "113"),
    "Brevard County, Florida": ("Brevard County", "12", "009"),
    "Chicago (metro), Illinois": ("Cook County", "17", "031"),
    "Ambridge (Beaver County), Pennsylvania": ("Beaver County", "42", "007"),
    "Mars (Pittsburgh area), Pennsylvania": ("Butler County", "42", "019"),
    "Huntsville, Alabama": ("Madison County", "01", "089"),
    "Loxley (Baldwin County), Alabama": ("Baldwin County", "01", "003"),
    "New York (Trump Tower), New York": ("New York County", "36", "061"),
    "New York (Foley Square), New York": ("New York County", "36", "061"),
    "New York (Lower Manhattan), New York": ("New York County", "36", "061"),
    "Atlanta (Buford Highway), Georgia": ("DeKalb County", "13", "089"),
    "Denver (State Capitol), Colorado": ("Denver County", "08", "031"),
    "Omaha (Glenn Valley Foods), Nebraska": ("Douglas County", "31", "055"),
    "New York (Manhattan), New York": ("New York County", "36", "061"),
    "Washington (Capitol), District of Columbia": ("District of Columbia", "11", "001"),
    "New York (Times Square), New York": ("New York County", "36", "061"),
    "Los Angeles (Federal Building), California": ("Los Angeles County", "06", "037"),
    "Omaha (South), Nebraska": ("Douglas County", "31", "055"),
    "Tallahassee (FSU College Town), Florida": ("Leon County", "12", "073"),
    "Bellingham, Washington": ("Whatcom County", "53", "073"),
    "Gibsonia / Cranberry Township, Pennsylvania": ("Butler County", "42", "019"),
    "New Haven, Connecticut": ("New Haven County", "09", "009"),
    "Tucker, Georgia": ("DeKalb County", "13", "089"),
    "Minneapolis (Hennepin County Medical Center), Minnesota": ("Hennepin County", "27", "053"),
    "Boston (Logan Airport), Massachusetts": ("Suffolk County", "25", "025"),
    "Carpinteria/Camarillo, California": ("Ventura County", "06", "111"),
    "Chicago (Millennium Park), Illinois": ("Cook County", "17", "031"),
    "Chicago (South Shore), Illinois": ("Cook County", "17", "031"),
    "Crystal (Robbinsdale), Minnesota": ("Hennepin County", "27", "053"),
    "Broadview (ICE Facility), Illinois": ("Cook County", "17", "031"),
    "Hopkins, Minnesota": ("Hennepin County", "27", "053"),
    "Minneapolis, St. Paul, statewide, Minnesota": ("Hennepin County", "27", "053"),
    "Encinitas, California": ("San Diego County", "06", "073"),
    "Highland, California": ("San Bernardino County", "06", "071"),
    "Camarillo/Carpinteria, California": ("Ventura County", "06", "111"),
    "Dallas (Love Field), Texas": ("Dallas County", "48", "113"),
    "Alvarado (Prairieland), Texas": ("Johnson County", "48", "251"),
    "Sedro-Woolley, Washington": ("Skagit County", "53", "057"),
    "Pleasant Valley Farms, Vermont": ("Addison County", "50", "001"),
    "Coventry (Interstate 91), Vermont": ("Orleans County", "50", "019"),
    "Elizabeth, New Jersey": ("Union County", "34", "039"),
    "Minneapolis (MSP Airport), Minnesota": ("Hennepin County", "27", "053"),
    "Los Angeles (Cesar Chavez tunnel), California": ("Los Angeles County", "06", "037"),
    "Los Angeles (Hollywood Home Depot / Dodger Stadium), California": ("Los Angeles County", "06", "037"),
    "Woodburn, Oregon": ("Marion County", "41", "047"),
    "Kent, New York": ("Putnam County", "36", "079"),
    "Monrovia, California": ("Los Angeles County", "06", "037"),
    "New York (26 Federal Plaza), New York": ("New York County", "36", "061"),
    "Lyons, Illinois": ("Cook County", "17", "031"),
    "Lovejoy (Robert A. Deyton Detention Center), Georgia": ("Clayton County", "13", "063"),
    "Lovejoy, Georgia": ("Clayton County", "13", "063"),
    "Tacoma (Northwest Detention Center), Washington": ("Pierce County", "53", "053"),
    "Lakeview, Louisiana": ("Orleans Parish", "22", "071"),
    "San Francisco Bay Area, California": ("San Francisco County", "06", "075"),
    "San Diego (South Park), California": ("San Diego County", "06", "073"),
    "St. Peters, Missouri": ("St. Charles County", "29", "183"),
    "Liberty, Missouri": ("Clay County", "29", "047"),
    "Martha's Vineyard / Nantucket, Massachusetts": ("Dukes County", "25", "007"),

    # New locations from OSINT fill
    "Pompano Beach, Florida": ("Broward County", "12", "011"),
    "San Juan, Puerto Rico": ("San Juan Municipio", "72", "127"),
    "Rolla, Missouri": ("Phelps County", "29", "161"),
    "Valdosta, Georgia": ("Lowndes County", "13", "185"),
    "Lumpkin, Georgia": ("Stewart County", "13", "259"),
    "Karnes City, Texas": ("Karnes County", "48", "255"),
    "Philipsburg, Pennsylvania": ("Centre County", "42", "027"),
    "Florence, Arizona": ("Pinal County", "04", "021"),
    "Eloy, Arizona": ("Pinal County", "04", "021"),
    "Victorville, California": ("San Bernardino County", "06", "071"),
    "Calexico, California": ("Imperial County", "06", "025"),
    "Baldwin, Michigan": ("Lake County", "26", "085"),
    "Gettysburg, Pennsylvania": ("Adams County", "42", "001"),
    "East Meadow, New York": ("Nassau County", "36", "059"),
    "Natchez, Mississippi": ("Adams County", "28", "001"),
    "Conroe, Texas": ("Montgomery County", "48", "339"),
    "Angola, Louisiana": ("West Feliciana Parish", "22", "125"),
    "Jena, Louisiana": ("LaSalle Parish", "22", "059"),
    "Dilley, Texas": ("Frio County", "48", "163"),
    "Estancia, New Mexico": ("Torrance County", "35", "057"),
    "Americus, Georgia": ("Sumter County", "13", "261"),
    "Live Oak, Texas": ("Bexar County", "48", "029"),
    "Hialeah, Florida": ("Miami-Dade County", "12", "086"),
    "Homestead, Florida": ("Miami-Dade County", "12", "086"),
}

# Load ALL incident data (not filtered)
incident_files = [
    'data/incidents/tier1_deaths_in_custody.json',
    'data/incidents/tier2_shootings.json',
    'data/incidents/tier2_less_lethal.json',
    'data/incidents/tier3_incidents.json',
    'data/incidents/tier4_incidents.json'
]

county_counts = Counter()
unmapped = []
total = 0

for filepath in incident_files:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r') as f:
        incidents = json.load(f)

    for inc in incidents:
        total += 1
        city = inc.get('city', '')
        state = inc.get('state', '')
        city_state = f"{city}, {state}"

        # Try exact match
        if city_state in CITY_TO_COUNTY:
            county_info = CITY_TO_COUNTY[city_state]
            fips = county_info[1] + county_info[2]
            county_counts[fips] += 1
        else:
            # Try partial match
            matched = False
            city_lower = city.lower().split(',')[0].split('(')[0].strip()
            for key, value in CITY_TO_COUNTY.items():
                key_city = key.split(',')[0].lower().strip()
                key_state = key.split(',')[1].strip() if ',' in key else ''
                if city_lower == key_city and state == key_state:
                    fips = value[1] + value[2]
                    county_counts[fips] += 1
                    matched = True
                    break
            if not matched:
                unmapped.append(city_state)

mapped = total - len(unmapped)
print(f"Total incidents: {total}")
print(f"Mapped to counties: {mapped} ({100*mapped/total:.1f}%)")
print(f"Unmapped: {len(unmapped)}")
if unmapped:
    unique_unmapped = list(set(unmapped))[:20]
    print(f"Sample unmapped: {unique_unmapped}")

# Load county boundaries
print("Loading county boundaries...")
county_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
counties = gpd.read_file(county_url)

counties['FIPS'] = counties['id']
counties['incident_count'] = counties['FIPS'].map(lambda x: county_counts.get(x, 0))

# Continental US only
continental = counties[~counties['FIPS'].str.startswith(('02', '15', '72'))]

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(18, 12))

colors = ['#f7f7f7', '#fee5d9', '#fcbba1', '#fc9272', '#fb6a4a', '#de2d26', '#a50f15', '#67000d']
cmap = LinearSegmentedColormap.from_list('incidents', colors, N=256)

max_incidents = max(county_counts.values()) if county_counts else 1

# Base layer
continental.plot(ax=ax, color='#f0f0f0', edgecolor='#cccccc', linewidth=0.1)

# Counties with data
counties_with_data = continental[continental['incident_count'] > 0]
if not counties_with_data.empty:
    counties_with_data.plot(
        column='incident_count',
        ax=ax,
        cmap=cmap,
        edgecolor='black',
        linewidth=0.3,
        vmin=0,
        vmax=max_incidents
    )

# Labels for counties with 3+ incidents
for idx, row in counties_with_data.iterrows():
    centroid = row.geometry.centroid
    count = row['incident_count']
    if count >= 3:
        ax.annotate(
            str(count),
            xy=(centroid.x, centroid.y),
            fontsize=7,
            ha='center',
            va='center',
            fontweight='bold',
            color='black'
        )

counties_with_incidents = len(county_counts)
ax.set_title(
    f'ALL ICE-Related Incidents by County\n'
    f'(Deaths, Shootings, Force, Raids, Detentions, Protests)\n'
    f'{mapped} incidents mapped across {counties_with_incidents} counties\n'
    f'Labels shown for counties with 3+ incidents',
    fontsize=14, fontweight='bold'
)

ax.set_axis_off()

legend_elements = [
    mpatches.Patch(facecolor='#67000d', edgecolor='black', label=f'High incidents ({max_incidents})'),
    mpatches.Patch(facecolor='#f0f0f0', edgecolor='#cccccc', label='Zero incidents'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=max_incidents))
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.03, pad=0.02, aspect=40)
cbar.set_label('Number of Incidents', fontsize=11)

plt.tight_layout()
plt.savefig('all_incidents_map_county.png', dpi=150, bbox_inches='tight', facecolor='white')
print(f"\nMap saved to: all_incidents_map_county.png")

print("\nTop 20 counties:")
for fips, count in sorted(county_counts.items(), key=lambda x: -x[1])[:20]:
    matching = counties[counties['FIPS'] == fips]
    if not matching.empty:
        name = matching.iloc[0].get('NAME', fips)
        print(f"  {name}: {count}")

plt.close()
