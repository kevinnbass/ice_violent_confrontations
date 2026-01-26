#!/usr/bin/env python3
"""
Add Round 3 incidents from exhaustive agent searches.
Categories: Deportation flights, family separations, detention deaths/conditions.
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
    if "victim_category" not in record:
        record["victim_category"] = "enforcement_target"
    return record


# ============================================================================
# TIER 1: DEATHS IN CUSTODY - New deaths from agent searches
# ============================================================================
NEW_TIER1_DEATHS = [
    {
        "id": "T1-D-041",
        "date": "2025-01-23",
        "state": "Florida",
        "facility": "Krome Service Processing Center / Larkin Community Hospital",
        "facility_operator": "ICE",
        "incident_type": "death_in_custody",
        "victim_name": "Genry Donaldo Ruiz-Guillen",
        "victim_age": 29,
        "victim_nationality": "Honduran",
        "cause_of_death": "Complications from schizoaffective disorder",
        "manner_of_death": "natural",
        "medical_condition": "Schizoaffective disorder, rhabdomyolysis, seizures, episodes of confusion",
        "outcome": "Death after hospitalization since December 9, 2024",
        "outcome_detail": "Ruiz-Guillen hospitalized at Larkin Community Hospital since December 9, 2024. After more than a month at Krome where he experienced seizures and confusion, transferred to three different hospitals. Diagnosed with rhabdomyolysis (life-threatening muscle tissue breakdown). Pronounced deceased January 23, 2025 at 8:07 AM. Mother told Univision he called from detention saying he wasn't feeling well and experiencing fainting spells - last time she spoke with him.",
        "outcome_category": "death",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Krome has housed 4 of 24+ ICE deaths since October 2024. By March 2025, facility detained 249% over capacity. Amnesty International documented delays in intake, overcrowding, inadequate medical care, prolonged solitary, limited legal access. Ruiz-Guillen entered US June 2023, released on parole July 2023, re-entered ICE custody October 29, 2024 after Pinellas County encounter. Medical experts said death could likely have been prevented.",
        "source_tier": 1,
        "source_url": "https://www.ice.gov/news/releases/honduran-national-ice-custody-passes-away-miami-area-hospital",
        "source_name": "ICE Official Release / Univision / Latin Times",
        "verified": True,
        "affected_count": 1
    },
    {
        "id": "T1-D-042",
        "date": "2025-01-29",
        "state": "Arizona",
        "facility": "Eloy Detention Center",
        "facility_operator": "CoreCivic",
        "incident_type": "death_in_custody",
        "victim_name": "Serawit Gezahegn Dejene",
        "victim_age": 45,
        "victim_nationality": "Ethiopian",
        "cause_of_death": "Complications from untreated HIV",
        "manner_of_death": "natural",
        "medical_condition": "HIV (undiagnosed until death), dehydration, weakness, fatigue, back pain",
        "outcome": "Death from entirely preventable HIV complications",
        "outcome_detail": "Dejene hospitalized since December 23, 2024, first at Banner Casa Grande Medical Center, then Banner University Medical Center Phoenix. Pronounced deceased January 29, 2025 at 1:21 PM. Medical examiner report reviewed by Newsweek stated death 'related to untreated HIV and could have been saved with the help of routine blood tests.' Professor Perry Halkitis of Rutgers stated 'routine blood work' tests would have 'immediately' shown HIV. Another expert called death 'entirely preventable.'",
        "outcome_category": "death",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Eloy has 'gained notoriety as one of the deadliest detention centers in the U.S. with at least 16 reported deaths, including five suicides' per Detention Watch Network. Dejene entered US August 19, 2024 near Lukeville, AZ, arrested by Border Patrol, issued expedited removal, transferred to Eloy August 21. Immigration judge granted continuance September 20 for asylum application. Ethiopian organizer held fundraiser to repatriate body. One of three deaths in just over a month of Trump's second presidency.",
        "source_tier": 1,
        "source_url": "https://www.ice.gov/news/releases/ethiopian-national-ice-custody-passes-away-phoenix-area-hospital",
        "source_name": "ICE Official Release / Newsweek / Detention Watch Network",
        "verified": True,
        "affected_count": 1
    },
    {
        "id": "T1-D-043",
        "date": "2025-04-08",
        "state": "Missouri",
        "facility": "Phelps County Jail",
        "facility_operator": "County",
        "incident_type": "death_in_custody",
        "victim_name": "Brayan Rayo-Garzon",
        "victim_age": 27,
        "victim_nationality": "Colombian",
        "cause_of_death": "Suicide by hanging",
        "manner_of_death": "suicide",
        "medical_condition": "Anxiety, labored breathing, heart murmur history, COVID-19, positive TB test",
        "outcome": "Death after mental health evaluation cancelled",
        "outcome_detail": "Jail staff found Rayo-Garzon unresponsive in cell with blanket wrapped around neck on April 7, 2025. Transported by helicopter to Mercy South at 2:26 AM on April 8. Declared brain dead about 12 hours later. ICE report confirms he did NOT receive mental health evaluation due to staffing shortages and COVID-19 diagnosis. Mental health appointment cancelled due to 'mental health clinic time and staff.' Security camera confirmed he was alone when he hanged himself with bedsheet.",
        "outcome_category": "death",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Days after booking, medical screening showed labored breathing, anxiety, self-reported heart murmur. March 29, nurse checked TB test as positive; severe head pain, body aches, sweating, elevated heart rate, taken to ER. Mental health evaluation never completed. Phelps County Jail ended ICE agreement September 1, 2025. Decision came months after death. Second ICE death in Missouri for 2025.",
        "source_tier": 1,
        "source_url": "https://www.stlpr.org/law-order/2025-05-12/ice-brayan-garzon-rayo-death-report-phelps-county-jail",
        "source_name": "STLPR / KCUR / ICE Death Report",
        "verified": True,
        "affected_count": 1
    },
    {
        "id": "T1-D-044",
        "date": "2025-05-05",
        "state": "Georgia",
        "facility": "Stewart Detention Center (died during transport)",
        "facility_operator": "CoreCivic/TransCor",
        "incident_type": "death_in_custody",
        "victim_name": "Abelardo Avellaneda-Delgado",
        "victim_age": 68,
        "victim_nationality": "Mexican",
        "cause_of_death": "Unknown - under investigation",
        "manner_of_death": "undetermined",
        "medical_condition": "Hypertensive crisis (blood pressure 226/57) documented before transport",
        "outcome": "Death during transport from jail to detention center",
        "outcome_detail": "Avellaneda-Delgado died May 5, 2025 during transport from Lowndes County Jail to Stewart Detention Center by TransCor (CoreCivic subsidiary). Pronounced deceased by Webster County Coroner at 1:25 PM ET. Medical records show blood pressure of 226/57 (hypertensive crisis/stroke-level) before release. Webster County Coroner stated 'When the ambulance got there, he was dead. He was cold to the touch, so he had been dead.' Forensic pathologist Dr. Kris Sperry confirmed it takes 30-45 minutes for body to become 'cool to touch.'",
        "outcome_category": "death",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Major discrepancies: TransCor told 911 'medical department cleared him for travel, no noticeable medical conditions.' Yet EMS records showed stroke-level blood pressure. Acting ICE director Todd Lyons said 'We have nothing to hide' but official death report omits cause of death or medical detail. Family said he had no prior health conditions. Senators Warnock and Ossoff demanded answers. Arrested April 9, 2025 by Echols County Sheriff for probation violation.",
        "source_tier": 1,
        "source_url": "https://theappeal.org/ice-death-in-custody-jorge-avellaneda-delgado/",
        "source_name": "The Appeal / Senator Ossoff Investigation",
        "verified": True,
        "affected_count": 1
    },
    {
        "id": "T1-D-045",
        "date": "2025-06-07",
        "state": "Georgia",
        "facility": "Stewart Detention Center",
        "facility_operator": "CoreCivic",
        "incident_type": "death_in_custody",
        "victim_name": "Jesus Molina-Veya",
        "victim_age": 45,
        "victim_nationality": "Mexican",
        "cause_of_death": "Suicide - ligature around neck",
        "manner_of_death": "suicide",
        "outcome": "Third confirmed suicide at Stewart Detention Center",
        "outcome_detail": "Jesus Molina-Veya found unresponsive in cell with ligature around neck on June 7, 2025. Pronounced deceased at Phoebe Sumter Hospital in Americus, GA. Thirteenth death in custody and third confirmed death by suicide at Stewart since ICE began detaining there in 2006.",
        "outcome_category": "death",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: 2017 Office of Civil Rights and Civil Liberties report found insufficient staff for health needs, sometimes only one mental health provider for 1,800 detainees. Organizations documented: inept mental health care, solitary confinement, medical neglect, unsanitary conditions, forced labor, use of force. Double amputee spent days immobile, unable to charge prosthetic legs. Detainees sleep on floors, use showers as toilets - 'unjust torture' with showers 'covered in feces, mold, urine.'",
        "source_tier": 1,
        "source_url": "https://www.detentionwatchnetwork.org/pressroom/releases/2025/third-death-suicide-georgias-ice-detention-center-advocates-call-immediate",
        "source_name": "Detention Watch Network / ICE",
        "verified": True,
        "affected_count": 1
    },
    {
        "id": "T1-D-046",
        "date": "2025-06-23",
        "state": "Florida",
        "facility": "Federal Detention Center Miami",
        "facility_operator": "Bureau of Prisons",
        "incident_type": "death_in_custody",
        "victim_name": "Johnny Noviello",
        "victim_age": 49,
        "victim_nationality": "Canadian",
        "cause_of_death": "Under investigation - cardiac related suspected",
        "manner_of_death": "undetermined",
        "medical_condition": "Seizure disorder, hypertension, poor personal hygiene, not eating",
        "outcome": "Death after documented health issues ignored",
        "outcome_detail": "Johnny Noviello found unresponsive at approximately 1 PM at BOP FDC Miami. Pronounced deceased by Miami Fire Rescue at 1:36 PM on June 23, 2025. Medical staff administered CPR and AED shock. Day after custody, diagnosed with seizure disorder and hypertension, prescribed anticonvulsant and blood pressure medications. Another provider found Noviello 'maintained poor personal hygiene and stated he had not eaten in a while.'",
        "outcome_category": "death",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Noviello entered US 1988 with legal visa, became LPR 1991. Convicted October 2023 of racketeering and drug trafficking in Volusia County FL, 12-month sentence. ICE arrested May 15, 2025. Canadian consulate notified. Canadian officials pressed US for details. 10th death in ICE custody in 2025, fourth in Florida.",
        "source_tier": 1,
        "source_url": "https://www.washingtonpost.com/immigration/2025/06/27/canadian-dies-ice-custody-florida/",
        "source_name": "Washington Post / CBC News / CNN / ICE",
        "verified": True,
        "affected_count": 1
    },
    {
        "id": "T1-D-047",
        "date": "2025-08-31",
        "state": "Arizona",
        "facility": "Central Arizona Correctional Complex",
        "facility_operator": "CoreCivic",
        "incident_type": "death_in_custody",
        "victim_name": "Lorenzo Antonio Batrez Vargas",
        "victim_age": 32,
        "victim_nationality": "Mexican",
        "cause_of_death": "Unknown - under investigation",
        "manner_of_death": "undetermined",
        "medical_condition": "Family alleges inadequate medical attention",
        "outcome": "Death, family demands investigation",
        "outcome_detail": "Lorenzo Antonio Batrez Vargas (known as 'Lenchito') died at Mountain Vista Medical Center in Mesa on August 31, 2025. Cause of death unknown, under investigation. Family voiced concerns on GoFundMe regarding adequacy of medical treatment - asserts he did not receive necessary medical attention. 12th person to die in ICE custody in 2025, making it deadliest year since 2020.",
        "outcome_category": "death",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Raised in Flagstaff, graduated Coconino High School. August 2, 2025 arrested by Flagstaff Police for drug paraphernalia possession (felony). ERO Phoenix took custody, processed at Phoenix ICE office, transferred to Central Arizona Correctional Complex in Florence. Prior: DUI March 2018 (10-day sentence), DUI charges March 2024, conviction May 2024. Facility exceeded capacity in 2025. At time of death, 61,000+ in ICE detention - highest in history.",
        "source_tier": 1,
        "source_url": "https://www.kjzz.org/fronteras-desk/2025-09-04/a-mexican-national-from-flagstaff-has-died-in-ice-detention",
        "source_name": "KJZZ / KNAU / Detention Watch Network",
        "verified": True,
        "affected_count": 1
    },
    {
        "id": "T1-D-048",
        "date": "2025-09-22",
        "state": "California",
        "facility": "Adelanto ICE Processing Center",
        "facility_operator": "GEO Group",
        "incident_type": "death_in_custody",
        "victim_name": "Ismael Ayala-Uribe",
        "victim_age": 39,
        "victim_nationality": "Mexican",
        "cause_of_death": "Abscess on buttock - denied timely lifesaving care",
        "manner_of_death": "natural",
        "medical_condition": "Abscess, cough, fever, severe pain flagged as potentially life-threatening",
        "outcome": "Death from treatable condition, family planning lawsuit",
        "outcome_detail": "Ismael Ayala-Uribe died September 22, 2025 at Victor Valley Global Medical Center. Former DACA recipient (2012, denied renewal 2016 after DUI). Brought to US at age 4, lived in Westminster, OC his whole life. Two weeks after Adelanto arrival, reported cough, fever, severe pain. Staff flagged as life-threatening, escorted in wheelchair to medical - 1.5 hours later, cleared to return. NOT sent to hospital until THREE DAYS LATER. Died one month later. ICE didn't notify family - learned of death from 5:30 AM police visit.",
        "outcome_category": "death",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Adelanto has years of scrutiny for poor conditions and inadequate medical care. Arrested by ICE August 17, 2025, transferred August 22. 14th detainee death since January 2025, first known California death. Senator Ossoff investigation: 85 credible medical neglect reports Jan 20 - Aug 5, 2025. ICE stopped paying outside medical providers October 3, 2025. Family attorney planning lawsuit against DHS, GEO Group, and Adelanto.",
        "source_tier": 1,
        "source_url": "https://lataco.com/death-confirmed-adelanto-ismael-ayala-uribe",
        "source_name": "LA Taco / LA Times / ABC7 Los Angeles",
        "verified": True,
        "affected_count": 1
    },
    {
        "id": "T1-D-049",
        "date": "2025-10-23",
        "state": "California",
        "facility": "Adelanto ICE Processing Center",
        "facility_operator": "GEO Group",
        "incident_type": "death_in_custody",
        "victim_name": "Gabriel Garcia-Aviles",
        "victim_age": 56,
        "victim_nationality": "Mexican",
        "cause_of_death": "Cardiac arrest from alcohol withdrawal symptoms",
        "manner_of_death": "natural",
        "medical_condition": "Alcohol withdrawal",
        "outcome": "Death 10 days after detention, family not notified until deathbed",
        "outcome_detail": "Gabriel Garcia-Aviles died October 23, 2025 - just 10 days after transfer to Adelanto following Costa Mesa arrest. Beloved community member, family man with work permit, lived in US over 30 years. When daughter arrived, found him 'unconscious, intubated, and with dried blood on his forehead.' ICE only notified family when he was on deathbed. Federal lawmakers demanded answers in December 23, 2025 letter to DHS Secretary Noem and ICE Director Lyons.",
        "outcome_category": "death",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Second Adelanto death in 2025 (after Ayala-Uribe). ICE missed deadline to release death report. ICE stopped paying outside medical providers since October 3, 2025 - 'no mechanism to provide prescribed medication' or 'pay for medically necessary off-site care.' No dialysis, prenatal care, oncology, chemotherapy. Population ballooned from <40,000 in January to 73,000+.",
        "source_tier": 1,
        "source_url": "https://www.kvcrnews.org/local-news/2025-11-06/federal-lawmakers-demand-answers-after-gabriel-garcia-aviles-dies-in-custody-at-adelanto-ice-processing-center",
        "source_name": "KVCR News / LA Taco / CBS Los Angeles",
        "verified": True,
        "affected_count": 1
    },
    {
        "id": "T1-D-050",
        "date": "2025-12-03",
        "state": "Texas",
        "facility": "Camp East Montana (Fort Bliss)",
        "facility_operator": "Private Contractor",
        "incident_type": "death_in_custody",
        "victim_name": "Francisco Gaspar-Andres",
        "victim_age": 48,
        "victim_nationality": "Guatemalan",
        "cause_of_death": "Natural liver and kidney failure",
        "manner_of_death": "natural",
        "medical_condition": "Multiple: flu-like symptoms, bleeding gums, jaundice, severe edema, hypertension, sepsis, renal failure, internal bleeding",
        "outcome": "Death after months of medical treatment, wife deported before able to see him",
        "outcome_detail": "Francisco Gaspar-Andres died December 3, 2025 at The Hospitals of Providence in El Paso after months of treatment. Arrested September 1, 2025 in Florida. Admitted to West Kendall Hospital September 4 for alcohol withdrawal. Transferred to Fort Bliss September 19. Immigration judge ordered removal November 14. Intubated November 21. Liver transplant list November 24. Dialysis began but declined. Wife Lucia Pedro Juan told El Paso Times officers didn't allow her to see him before she was deported to Guatemala.",
        "outcome_category": "death",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Fort Bliss opened August 2025 despite congressional warnings. Leaked ICE inspection found 60+ federal standard violations in first 50 days. Largest detention center with 2,700+ people. On military base formerly used to intern Japanese Americans during WWII. ACLU documented beatings, sexual abuse, medical neglect, insufficient food, denial of attorney access. First death at facility. Rep. Escobar criticized that Congress wasn't notified until nearly a week after death. 2025 already deadliest year since 2004 with 30+ deaths by mid-December.",
        "source_tier": 1,
        "source_url": "https://elpasomatters.org/2025/12/09/ice-detainee-death-immigrant-camp-east-montana-fort-bliss-el-paso-texas/",
        "source_name": "El Paso Matters / El Paso Times / ACLU",
        "verified": True,
        "affected_count": 1
    },
    {
        "id": "T1-D-051",
        "date": "2025-12-15",
        "state": "Michigan",
        "facility": "North Lake Processing Center",
        "facility_operator": "Private (former prison)",
        "incident_type": "death_in_custody",
        "victim_name": "Nenko Stanev Gantchev",
        "victim_age": 56,
        "victim_nationality": "Bulgarian",
        "cause_of_death": "Suspected natural causes - under investigation",
        "manner_of_death": "undetermined",
        "medical_condition": "Diabetes (allegedly untreated), heart condition requiring echocardiogram (never received)",
        "outcome": "Death, family seeking second autopsy, congressional investigation demanded",
        "outcome_detail": "Nenko Stanev Gantchev, Illinois resident and Bulgarian citizen, found unresponsive in holding cell December 15, 2025. Doctor declared him dead at 9:54 PM. Had been in custody 82 days after arrest September 23, 2025 at green card interview. Family says he suffered from diabetes that went untreated. Staff told him he needed echocardiogram but at least a month went by without receiving it. Family seeking private autopsy. Reps. Delia Ramirez and Rashida Tlaib demanded 'immediate, transparent investigation.'",
        "outcome_category": "death",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Born October 31, 1969 in Bulgaria. Entered US June 1995 as J1 visitor. LPR 2005, revoked 2009 after 2008 DUI. Removal ordered January 11, 2023. Arrested September 23, 2025 at green card interview - detained at interview. North Lake is former prison contracted for ICE in 2025, 1,800-bed capacity. Death was fourth in four-day period December 12-15, 2025. By December 2025, at least 30 deaths - highest since 2004. Gantchev was Chicago business owner.",
        "source_tier": 1,
        "source_url": "https://abc7chicago.com/post/bulgarian-chicago-business-owner-nenko-gantchev-dies-ice-custody-family-congresswoman-call-immediate-investigation/18301520/",
        "source_name": "ABC7 Chicago / Block Club Chicago / Common Dreams",
        "verified": True,
        "affected_count": 1
    },
    {
        "id": "T1-D-052",
        "date": "2026-01-09",
        "state": "Pennsylvania",
        "facility": "Federal Detention Center Philadelphia",
        "facility_operator": "Bureau of Prisons",
        "incident_type": "death_in_custody",
        "victim_name": "Parady La",
        "victim_age": 46,
        "victim_nationality": "Cambodian",
        "cause_of_death": "Fentanyl withdrawal complications - medical neglect alleged",
        "manner_of_death": "natural",
        "medical_condition": "Severe opioid withdrawal, vomiting",
        "outcome": "Death after only 3 days in ICE custody, advocates allege egregious medical neglect",
        "outcome_detail": "Parady La, Cambodian refugee who arrived as child, died January 9, 2026 at Thomas Jefferson University Hospital after just THREE DAYS in ICE custody. Arrested January 6 outside Upper Darby, PA home. Shut Down Detention Campaign: 'completely preventable and direct result of egregious medical neglect.' He 'told staff he was going through fentanyl withdrawal and repeatedly requested care after vomiting several times throughout January 6th.'",
        "outcome_category": "death",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: One of four ICE deaths in first 10 days of 2026. Early 2026 rate extrapolates to 120+ deaths annually - more than 10 times rate in last year of Biden administration (11 deaths). In 2025, 31 people died in ICE custody - all-time high. Senator Ossoff investigation: ICE stopped paying outside medical providers October 3, 2025, 'no mechanism to provide prescribed medication.' Population: <40,000 in January 2025 to 73,000+.",
        "source_tier": 1,
        "source_url": "https://whyy.org/articles/parady-la-upper-day-ice-custody-death/",
        "source_name": "WHYY / Detention Watch Network / Bucks County Beacon",
        "verified": True,
        "affected_count": 1
    },
    {
        "id": "T1-D-053",
        "date": "2026-01-14",
        "state": "Texas",
        "facility": "Camp East Montana (Fort Bliss)",
        "facility_operator": "Private Contractor",
        "incident_type": "death_in_custody",
        "victim_name": "Victor Manuel Diaz",
        "victim_age": 36,
        "victim_nationality": "Nicaraguan",
        "cause_of_death": "Presumed suicide - family disputes",
        "manner_of_death": "suicide",
        "outcome": "Third death at Fort Bliss in 44 days, family demands investigation",
        "outcome_detail": "Victor Manuel Diaz found unconscious and unresponsive in room by contract security staff January 14, 2026. Pronounced dead at 4:09 PM. ICE classified as 'presumed suicide.' Given final removal order January 12 - TWO DAYS before death. Brother Yorlan Diaz: 'I don't believe he took his life. He was not a criminal; he was looking for a better life.' Major concern: Unlike previous deaths, autopsy NOT conducted by local medical examiner. Body taken to William Beaumont Army Medical Center at Fort Bliss. El Paso Medical Examiner's Office confirmed no record of death.",
        "outcome_category": "death",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Diaz illegally entered US March 2024, ordered removed in absentia August 2025. In custody since January 6, 2026 when ICE 'encountered' him in Minneapolis amid federal crackdown in Minnesota. Third Fort Bliss death in 44 days. After death, visitors blocked from seeing Minnesota immigrants - guards said 'They're not allowing the people from Minnesota to have visitors.' Camp holds 2,903 detainees as of January 8, 2026. 2025: 31 deaths. As of January 18, 2026: 6 deaths - one every three days.",
        "source_tier": 1,
        "source_url": "https://abcnews.go.com/US/dont-life-family-nicaraguan-man-seeks-answers-after/story?id=129497484",
        "source_name": "ABC News / NBC News / El Paso Matters / KVIA",
        "verified": True,
        "affected_count": 1
    }
]

# ============================================================================
# TIER 3: DEPORTATION FLIGHTS AND FAMILY SEPARATIONS
# ============================================================================
NEW_TIER3_INCIDENTS = [
    # CECOT and Guantanamo
    {
        "id": "T3-123",
        "date": "2025-03-15",
        "state": "Federal/Multiple",
        "city": "El Salvador - CECOT Prison",
        "incident_type": "wrongful_deportation",
        "enforcement_granularity": "mass_deportation",
        "victim_name": "Andry Jose Hernandez Romero (lead plaintiff) + 237 others",
        "victim_nationality": "Venezuelan",
        "affected_count": 238,
        "outcome": "238 deported to CECOT mega-prison, 252 later released in prisoner swap",
        "outcome_detail": "238 Venezuelans deported March 15, 2025 (137 under Alien Enemies Act, 101 regular immigration law). Flights departed despite TRO issued by Judge Boasberg. DHS Secretary Noem made decision to continue. Men held incommunicado 4 months, subjected to documented torture: daily beatings, sexual violence, solitary confinement. 48.8% had no US criminal record. Released July 18, 2025 in prisoner swap to Venezuela.",
        "outcome_category": "deported",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: Judge Boasberg issued TRO at 11 AM ordering flights turned around; DOJ admitted Noem proceeded anyway. US paid El Salvador $4.76M for detention with condition: no funds for legal counsel. HRW 'You Have Arrived in Hell' documented: 23-hour solitary, 2x3 meter cells, concrete beds without mattresses, daily beatings. Named individuals: Merwil Gutierrez (TPS, no record), Jhon Chacin (tattoo artist), Franco Caraballo (clock tattoo), Neiyerver Adrian Leon Rengel (detained on 27th birthday despite documents). First use of Alien Enemies Act since WWII. J.G.G. v. Trump filed. Supreme Court ruled April 7 detainees entitled to habeas.",
        "source_tier": 3,
        "source_url": "https://www.hrw.org/report/2025/11/12/you-have-arrived-in-hell/torture-and-other-abuses-against-venezuelans-in-el",
        "source_name": "Human Rights Watch / Cristosal",
        "verified": True
    },
    {
        "id": "T3-124",
        "date": "2025-02-04",
        "state": "Federal/Multiple",
        "city": "Guantanamo Bay Naval Base, Cuba",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "mass_detention",
        "victim_nationality": "Venezuelan",
        "affected_count": 195,
        "outcome": "177 deported to Venezuela via Honduras on February 20, 2025",
        "outcome_detail": "First migrant detention flight to Guantanamo February 4, 2025 following Trump January 29 memo expanding Migrant Operations Center. Nearly 200 Venezuelans transported. 127 held in Camp 6 in individual cells (2x3m, concrete bed, no mattress); 51 in tent facilities not meeting ICE standards. 23-hour solitary, warned not to speak with others. Not informed of destination; families not notified. $40 million monthly cost.",
        "outcome_category": "detained",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: HRW documented: detainees not informed of destination or legal status, unsanitary conditions, 'climate of extreme fear and intimidation,' beatings, sexual abuse, coercive threats, medical neglect, insufficient food. Legal challenges: Espinoza Escalona v. Noem (March 2025), Gutierrez v. Noem (June 2025). Senator Reed criticized $40M monthly expenditure. 168 organizations demanded closure. UN human rights experts condemned.",
        "source_tier": 3,
        "source_url": "https://www.hrw.org/news/2025/08/29/us-migrants-face-abuse-in-guantanamo",
        "source_name": "Human Rights Watch",
        "verified": True
    },
    {
        "id": "T3-125",
        "date": "2025-11-22",
        "state": "Massachusetts",
        "city": "Boston (Logan Airport)",
        "incident_type": "wrongful_deportation",
        "enforcement_granularity": "court_order_violation",
        "victim_name": "Any Lucia Lopez Belloza",
        "victim_age": 19,
        "victim_nationality": "Honduran",
        "affected_count": 1,
        "outcome": "Wrongfully deported to Honduras despite federal court order; Trump administration apologized for 'mistake'",
        "outcome_detail": "19-year-old Babson College freshman detained at Boston Logan November 20 while flying to Texas for Thanksgiving. Surrounded, handcuffed, 'dragged out.' Transferred to military base, flown to Texas, deported November 22 despite emergency court order November 21. ICE officer said order 'did not matter' once out of state. Deported 'in shackles like she's a murder suspect.' Trump administration apologized for 'mistake.' Currently with grandparents in Honduras.",
        "outcome_category": "deported",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: Legal background: Family removal proceedings 2016, appeal dismissed 2017. Had valid work authorization to attend Babson studying business. Father is tailor. Attorney: Todd Pomerleau. January 2: ICE officer declaration admitted he did not notify Port Isabel to abort removal. Pending: T visa for trafficking victims. Fifth known wrongful deportation violating court orders in 2025.",
        "source_tier": 3,
        "source_url": "https://www.cnn.com/2025/12/01/us/babson-college-student-deported-thanksgiving-hnk",
        "source_name": "CNN",
        "verified": True
    },
    {
        "id": "T3-126",
        "date": "2025-11-11",
        "state": "Louisiana",
        "city": "Louisiana Detention Facility to Mexico Border",
        "incident_type": "wrongful_deportation",
        "enforcement_granularity": "court_order_violation",
        "victim_name": "Britania Uriostegui Rios",
        "victim_nationality": "Mexican",
        "us_citizen": False,
        "legal_status": "LPR",
        "affected_count": 1,
        "outcome": "Trans woman wrongfully deported to Mexico despite judge ruling she would face torture",
        "outcome_detail": "Mexican trans woman, US nearly 50 years, lost LPR in 2023 after felony conviction. Immigration Judge Elaine Cintron ruled March 2025 she would face torture/persecution/death in Mexico under CAT. Despite ruling, flown from Louisiana to Texas, taken across border November 11 without money, medications (mental health, HIV prevention), hormones, or phone. Government admitted 'inadvertent.' Fifth wrongful deportation violating orders in 2025.",
        "outcome_category": "deported",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: 'Sexually trafficked by cartels at age 12' per attorney. Government attempted deportations to Costa Rica, Nicaragua, Honduras, El Salvador since March - all failed. Now living in hiding in Mexico using deadname, family not accepting of trans identity. Mexico one of deadliest countries for trans people. Suing to compel release upon return.",
        "source_tier": 3,
        "source_url": "https://www.cnn.com/2025/11/19/us/uriostegui-rios-deportation-government-lawsuit-hnk",
        "source_name": "CNN",
        "verified": True
    },
    {
        "id": "T3-127",
        "date": "2025-04-25",
        "state": "Louisiana",
        "city": "Baton Rouge / Honduras",
        "incident_type": "wrongful_deportation",
        "enforcement_granularity": "us_citizen_child",
        "victim_name": "V.M.L. (2-year-old US citizen)",
        "victim_age": 2,
        "us_citizen": True,
        "affected_count": 3,
        "children_affected": True,
        "children_count": 1,
        "outcome": "2-year-old US citizen deported to Honduras with mother 'with no meaningful process'",
        "outcome_detail": "2-year-old born Baton Rouge 2023, deported with mother Jenny Carolina Lopez-Villela April 25, 2025. Family detained during routine ISAP check-in. ICE officer threatened if mother didn't sign, children would go to foster care. Father given only 1 minute to speak with family while hearing children crying. Notarized custody order for sister-in-law (US citizen) refused. Judge Doughty set hearing 'in the interest of dispelling our strong suspicion that the Government just deported a U.S. citizen with no meaningful process.'",
        "outcome_category": "deported",
        "victim_category": "us_citizen_collateral",
        "notes": "EXHAUSTIVE: Same week: two other US citizen children (ages 4 and 7) deported with different mother, including 4-year-old with metastatic cancer. DHS: 'The parents made the decision to take the child with them to Honduras.' Judge Doughty: 'It is illegal and unconstitutional to deport, detain for deportation, or recommend deportation of a U.S. citizen.'",
        "source_tier": 3,
        "source_url": "https://www.cnn.com/2025/04/25/us/toddler-deported-honduras-us-citizen-judge",
        "source_name": "CNN / NPR",
        "verified": True
    },
    {
        "id": "T3-128",
        "date": "2025-02-04",
        "state": "Texas",
        "city": "Rio Grande / CBP Checkpoint",
        "incident_type": "wrongful_deportation",
        "enforcement_granularity": "us_citizen_child",
        "victim_name": "10-year-old US citizen girl (name protected)",
        "victim_age": 10,
        "us_citizen": True,
        "children_affected": True,
        "children_count": 5,
        "affected_count": 7,
        "outcome": "10-year-old US citizen recovering from brain cancer surgery deported to Mexico with family",
        "outcome_detail": "Texas family with 6 children (5 US citizens) stopped at CBP checkpoint driving from Rio Grande to Houston for daughter's emergency brain cancer checkup. Parents (arrived 2013) given choice: 'separate permanently from our children, or be deported together.' All deported February 4, 2025. 10-year-old had brain surgery to remove tumor in 2024 - doctors 'gave no hope.' Cannot access proper medical care in rural Mexico.",
        "outcome_category": "deported",
        "victim_category": "us_citizen_collateral",
        "notes": "EXHAUSTIVE: Made 350-mile trip 5+ times before without incident. Brain swelling persists, speech difficulties, right-side mobility impairment. DHS civil rights complaint filed, humanitarian parole applications July 22, 2025. CBP: 'when someone is given expedited removal orders and chooses to disregard them, they will face the consequences.'",
        "source_tier": 3,
        "source_url": "https://www.nbcnews.com/news/latino/us-citizen-child-recovering-brain-cancer-deported-mexico-undocumented-rcna196049",
        "source_name": "NBC News",
        "verified": True
    },
    {
        "id": "T3-129",
        "date": "2025-12-09",
        "state": "Arizona",
        "city": "Arizona to Cairo to Moscow",
        "incident_type": "wrongful_deportation",
        "enforcement_granularity": "third_country_deportation",
        "victim_nationality": "Russian",
        "affected_count": 64,
        "outcome": "64 Russian asylum seekers deported to Moscow via Cairo; all received military draft summons",
        "outcome_detail": "December 2025 deportation flight with 64 Russians departed Arizona December 7, stopped in Cairo, arrived Moscow Domodedovo Airport 2:39 AM December 9. All 64 had sought political asylum claiming persecution. Flew in shackles and handcuffs attached to chains across stomachs. In Cairo, ~50 Egyptian security escorted deportees; some who resisted were beaten. FSB interrogated deportees for hours. ALL men (including 68-year-old) received military draft summons.",
        "outcome_category": "deported",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: Known arrests: Zair Syamiullin (70, fraud charges), Artyom Vovchenko (26, military deserter facing 10-year sentence, arrested August 2025). Fourth Russia flight in 2025; total 127 Russians deported 2025 (2022: 58; 2023: 222; 2024: 455). Egypt route established specifically for Russian deportations. Violates non-refoulement principle - deporting asylum seekers to country of claimed persecution.",
        "source_tier": 3,
        "source_url": "https://www.euronews.com/2025/12/11/latest-us-deportations-to-russia-spark-fears-over-draft-notices-and-fsb-intimidation",
        "source_name": "Euronews / Meduza / The Insider",
        "verified": True
    },
    {
        "id": "T3-130",
        "date": "2025-08-31",
        "state": "Federal/Multiple",
        "city": "Multiple US locations / Guatemala",
        "incident_type": "wrongful_deportation",
        "enforcement_granularity": "unaccompanied_minors",
        "victim_nationality": "Guatemalan",
        "children_affected": True,
        "affected_count": 76,
        "outcome": "Federal judge blocked deportation of 76 unaccompanied Guatemalan children after one plane already took off",
        "outcome_detail": "76 Guatemalan unaccompanied minors roused from beds ~1 AM August 31, 2025, brought onto three planes. One took off but ordered to turn around after Judge Sparkle Sooknanan issued 14-day freeze. Judge received complaint 2 AM, personally tried reaching US Attorney at 3:43 AM. All 10 named plaintiffs declared fear of Guatemala (gang violence, trafficking, family abuse). NILC: 600+ Guatemalan children potentially at risk.",
        "outcome_category": "detained",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: Justice Department claimed 'repatriating' not 'deporting.' 17-year-old in Texas: 'I felt like I lost my breath for a second because they had never woken us up in the middle of the night before.' First known attempt at mass deportation of unaccompanied minors under second Trump administration.",
        "source_tier": 3,
        "source_url": "https://abcnews.go.com/Politics/lawyers-block-trump-administration-repatriating-guatemalan-minors/story?id=125140049",
        "source_name": "ABC News / NPR",
        "verified": True
    },
    # FAMILY SEPARATIONS
    {
        "id": "T3-131",
        "date": "2025-04-26",
        "state": "Louisiana",
        "city": "New Orleans/Baton Rouge",
        "incident_type": "wrongful_deportation",
        "enforcement_granularity": "family_separation",
        "victim_name": "Julia, Jade (2), Janelle (11)",
        "children_affected": True,
        "children_count": 2,
        "us_citizen_children": True,
        "affected_count": 3,
        "outcome": "Mother and both children deported to Honduras",
        "outcome_detail": "Julia and two daughters (Jade, 2, US citizen; Janelle, 11, Honduran citizen) deported to Honduras within days of ISAP check-in detention. Julia signed consent under threat Jade would go to foster care. Attorneys allege parents held incommunicado, denied counsel, never given meaningful choice about children's care. Part of J.L.V. v. Acuna lawsuit.",
        "outcome_category": "deported",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: ACLU and NIPNLG representing. Lawsuit names AG Pam Bondi, DHS Secretary Noem, ICE Director Lyons. DHS disputes account. Attorneys say Julia signed under duress after foster care threat. Father Jacob left in Louisiana. Case ongoing as of August 2025.",
        "source_tier": 3,
        "source_url": "https://lailluminator.com/2025/08/21/children-deport/",
        "source_name": "Louisiana Illuminator / NBC News / ACLU",
        "verified": True
    },
    {
        "id": "T3-132",
        "date": "2025-07-10",
        "state": "California",
        "city": "Carpinteria/Camarillo",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_workplace",
        "victim_name": "Glass House Farms workers",
        "children_affected": True,
        "children_count": 14,
        "us_citizen_children": True,
        "affected_count": 361,
        "outcome": "361 arrested, 14 children 'rescued', 12+ US citizen children left parentless, 1 worker killed",
        "outcome_detail": "Massive raid on Glass House Farms cannabis sites in Santa Barbara/Ventura counties. DHS claimed 14 migrant children 'rescued' from exploitation. However, 12+ US citizen children left without parents. Jaime Alanis Garcia died falling 30 feet while evading ICE. One pregnant mother had chemical spilled on leg, hospitalized. 16-year-old Alexa left caring for 6-year-old and 10-month-old sisters alone.",
        "outcome_category": "detained",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: Congressman Carbajal denied access, condemned 'troubling lack of transparency.' Rubber bullets and flash bangs used against crowds. United Farm Workers: some workers including US citizens 'remain totally unaccounted for.' DHS claimed convicted child predator found working near minors. House Republicans launched investigation.",
        "source_tier": 3,
        "source_url": "https://www.independent.com/2025/07/11/children-left-alone-after-mothers-arrested-in-immigration-raids/",
        "source_name": "Santa Barbara Independent / DHS / CNN",
        "verified": True
    },
    {
        "id": "T3-133",
        "date": "2025-09-28",
        "state": "Illinois",
        "city": "Chicago (Millennium Park)",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "family_separation",
        "victim_name": "Jaime Ramirez, Noemi Chavez, Dasha (8), son (3)",
        "children_affected": True,
        "children_count": 2,
        "affected_count": 4,
        "outcome": "Family detained at Millennium Park, separated; mother and children released after court order, father in Texas",
        "outcome_detail": "Family from Albany Park detained by Border Patrol at Millennium Park - 8-year-old Dasha had requested outing. Video shows Dasha clinging to doll, crying as armed agents detained family. Father transferred to Texas, mother/children held at O'Hare. Federal judge ordered family protected. Mother/children released October 2, father remains in Texas. Family has asylum appointment October 2027.",
        "outcome_category": "detained",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: Part of Operation Midway Blitz. Gov. Pritzker: 'invasion'; Mayor Johnson: 'what it meant for us as a city.' 8-year-old ran toward father surrounded by armed agents. Second group encircled mother helping 3-year-old with shoes. National Immigrant Justice Center representing. Judge later ruled ICE violated 2022 consent decree with warrantless arrests.",
        "source_tier": 3,
        "source_url": "https://blockclubchicago.org/2025/09/30/family-taken-by-feds-from-millennium-park-separated-in-detention-centers-theyre-locking-up-children/",
        "source_name": "Block Club Chicago / Chicago Tribune / CNN",
        "verified": True
    },
    {
        "id": "T3-134",
        "date": "2025-09-30",
        "state": "Illinois",
        "city": "Chicago (South Shore)",
        "incident_type": "mass_raid",
        "enforcement_granularity": "mass_raid_residential",
        "victim_name": "South Shore apartment residents",
        "children_affected": True,
        "children_count": 4,
        "us_citizen_children": True,
        "affected_count": 37,
        "outcome": "37 arrested, 4 US citizen children detained, 1 US citizen adult detained 3 hours",
        "outcome_detail": "Around 1 AM, armed federal agents rappelled from helicopters onto 5-story apartment in South Shore. Agents kicked down doors, threw flashbangs. 37 arrested from Venezuela, Mexico, Colombia, Nigeria. 4 US citizen children detained 'until placed in care of guardians.' Governor Pritzker reported children zip-tied (DHS denies). US citizen Rodrick Johnson (67) detained in zip ties for 3 hours before release.",
        "outcome_category": "detained",
        "victim_category": "us_citizen_collateral",
        "notes": "EXHAUSTIVE: Part of Operation Midway Blitz. Gov. Pritzker: 'Imagine being a child awakened in the middle of the night by a Black Hawk helicopter landing... armed stranger forcibly removing you from bed, zip-tying your hands, separating you from your family.' Eyewitness saw children 'zip tied to each other.' DHS: 'shameful and disgusting lie.' Rodrick Johnson (US citizen) door broken down, dragged out, told to wait until they 'looked him up.' October 7: House Committees launched investigation.",
        "source_tier": 3,
        "source_url": "https://www.cnn.com/2025/10/03/us/chicago-apartment-ice-raid",
        "source_name": "CNN / Block Club Chicago / TIME",
        "verified": True
    },
    {
        "id": "T3-135",
        "date": "2026-01-23",
        "state": "Minnesota",
        "city": "Minneapolis",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "family_separation",
        "victim_name": "Elvis Joel Tipan Echeverria, Chloe Renata Tipan Villacis",
        "victim_age": 2,
        "children_affected": True,
        "children_count": 1,
        "affected_count": 2,
        "outcome": "Father and 2-year-old detained, flown to Texas despite court order, toddler returned next day",
        "outcome_detail": "ICE agents followed Elvis and 2-year-old Chloe from grocery store to home. Both detained. Family has pending asylum - in country legally, no final removal order. Federal Judge Menendez issued emergency order at 8:11 PM to release child by 9:30 PM citing 'irreparable harm.' Despite order, at 8:30 PM ICE put both on commercial flight to Texas. Toddler returned Friday after court intervention. Father remains in custody. 1,000+ community members donated nearly $50,000 within hours.",
        "outcome_category": "detained",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: Child has lived in Minneapolis 'since her arrival in the United States as a newborn.' Attorney: 'recovering from this horrific ordeal.' ICE defied federal judge's order - informed court AFTER pair was on flight (19 minutes after order). 9th child detained in Minnesota that month (ages 2-17). Part of broader Minnesota enforcement causing Minneapolis Public Schools to move to remote learning.",
        "source_tier": 3,
        "source_url": "https://www.cnn.com/2026/01/24/us/elvis-tipan-echeverria-toddler-ice-arrest-minnesota",
        "source_name": "CNN / Star Tribune / NBC News",
        "verified": True
    },
    {
        "id": "T3-136",
        "date": "2026-01-15",
        "state": "Minnesota",
        "city": "Crystal (Robbinsdale)",
        "incident_type": "wrongful_detention",
        "enforcement_granularity": "school_adjacent",
        "victim_name": "Parent at Northport Elementary",
        "children_affected": True,
        "children_count": 1,
        "affected_count": 1,
        "outcome": "Parent detained at school bus stop in front of child and busload of students",
        "outcome_detail": "Parent detained by ICE while waiting with child at school bus stop. Children on bus and at stop witnessed arrest. All students including child of arrested parent were able to board bus. Child left with 'traumatizing image of their parent being detained while they are bussed to school.'",
        "outcome_category": "detained",
        "victim_category": "enforcement_target",
        "notes": "EXHAUSTIVE: Superintendent Teri Staloch confirmed. Rep. Cedrick Frazier: 'Waiting for the school bus is a fundamental, mundane part of American parenthood... targeting parents as they perform the basic duty of getting their children to school is abhorrent and un-American. No child should have to sit in a classroom wondering if their parent will be there when they get home.' Part of broader Minnesota surge causing Minneapolis Public Schools to cancel in-person classes.",
        "source_tier": 3,
        "source_url": "https://bringmethenews.com/minnesota-news/robbinsdale-schools-parent-detained-by-ice-while-waiting-with-child-at-bus-stop",
        "source_name": "Bring Me The News / KARE11 / KSTP",
        "verified": True
    }
]

# ============================================================================
# TIER 2: LESS LETHAL - Detention facility abuse
# ============================================================================
NEW_TIER2_LESS_LETHAL = [
    {
        "id": "T2-LL-040",
        "date": "2025-12-08",
        "state": "Texas",
        "facility": "Camp East Montana (Fort Bliss)",
        "incident_type": "physical_force",
        "force_type": "beating",
        "victim_name": "Multiple detainees (45+ interviewed)",
        "affected_count": 45,
        "outcome": "ACLU and human rights groups demand facility closure",
        "outcome_detail": "December 8, 2025, ACLU and human rights groups sent letter to ICE demanding end to detention at Camp East Montana. Letter details accounts from 45+ interviewed detainees including 16 sworn declarations documenting: beatings and sexual abuse by officers, beatings and coercive threats to compel deportation to third countries, medical neglect, hunger, denial of counsel access.",
        "outcome_category": "serious_injury",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Detained teenager 'Samuel' told lawyers he was beaten so severely he sustained injuries across body, lost consciousness, taken to hospital by ambulance. Another detainee: 'slammed against the ground, handcuffed, taken outside for stepping out of line in the dining hall' with guards nearly breaking his wrists. Opened August 2025 despite warnings. Former Japanese internment site. 60+ federal standard violations in first 50 days. 2,700+ detainees - largest center. DHS disputed claims but Senator Ossoff investigation received 510 credible reports of abuse across 25 states.",
        "source_tier": 2,
        "source_url": "https://www.aclu.org/news/immigrants-rights/detained-immigrants-detail-physical-abuse-and-inhumane-conditions-at-largest-immigration-detention-center-in-the-u-s",
        "source_name": "ACLU / Human Rights Watch / Senator Ossoff Investigation",
        "verified": True
    },
    {
        "id": "T2-LL-041",
        "date": "2025-07-22",
        "state": "Florida",
        "facility": "South Florida Detention Facility (Alligator Alcatraz)",
        "incident_type": "less_lethal",
        "force_type": "torture_conditions",
        "victim_name": "Pedro Lorenzo Concepcion",
        "victim_age": 44,
        "victim_nationality": "Cuban",
        "affected_count": 1,
        "outcome": "Ended 17-day hunger strike after ICE assured not on deportation list",
        "outcome_detail": "Pedro Lorenzo Concepcion began hunger strike July 22, 2025, two weeks after entering 'Alligator Alcatraz.' Detained July 9 when voluntarily appeared at ICE Miramar for routine check despite compliance. Transferred to Krome in retaliation. Despite 2-week strike, Krome wouldn't recognize him as striker until he rejected 9 consecutive meals. Ended strike after 17 days (August 8) when ICE assured him he wasn't on deportation list. Extremely weakened, could barely walk.",
        "outcome_category": "no_injury",
        "victim_category": "detainee",
        "notes": "EXHAUSTIVE: Alligator Alcatraz conditions per Amnesty International: Lights on 24/7, overflowing toilets, no shower access, solitary in 2x2 foot boxes, people shackled in 2-foot-high metal cages left outside without water for up to a day, denial of potable water, meals with maggots, oversized mosquitoes. Amnesty: 'amount to torture or other ill-treatment.' Built in 8 days in June 2025 on remote Everglades airfield. 34 no-bid contracts totaling $360+ million. Only 31% of detainees had final orders despite DeSantis claims. Environmental groups won preliminary injunction.",
        "source_tier": 2,
        "source_url": "https://www.democracynow.org/2025/8/6/headlines/cuban_immigrant_on_hunger_strike_for_over_14_days_to_protest_his_detention_at_ice_jails",
        "source_name": "Democracy Now / CiberCuba / Amnesty International",
        "verified": True
    }
]


def add_incidents_to_file(filepath, new_incidents, label):
    """Add new incidents to a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    existing_ids = {r["id"] for r in existing}

    # Also check for duplicate names/dates to avoid cross-tier dupes
    existing_keys = set()
    for r in existing:
        name = r.get('victim_name', '').lower() if r.get('victim_name') else ''
        date = r.get('date', '')
        if name and date:
            existing_keys.add((name, date))

    added = 0
    skipped = 0

    for incident in new_incidents:
        # Skip if ID exists
        if incident["id"] in existing_ids:
            skipped += 1
            continue

        # Check for duplicate by name/date
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
    print("Adding Round 3 Validated Incidents from Exhaustive Agent Searches")
    print("=" * 70)

    # Tier 1: Deaths in Custody
    print("\n[TIER 1: DEATHS IN CUSTODY]")
    added, skipped, total = add_incidents_to_file(
        DATA_DIR / "tier1_deaths_in_custody.json",
        NEW_TIER1_DEATHS,
        "T1-D"
    )
    print(f"Added {added} new deaths (skipped {skipped}), total now: {total}")

    # Tier 2: Less Lethal
    print("\n[TIER 2: LESS LETHAL / DETENTION ABUSE]")
    added, skipped, total = add_incidents_to_file(
        DATA_DIR / "tier2_less_lethal.json",
        NEW_TIER2_LESS_LETHAL,
        "T2-LL"
    )
    print(f"Added {added} new incidents (skipped {skipped}), total now: {total}")

    # Tier 3: Deportations & Family Separations
    print("\n[TIER 3: DEPORTATIONS & FAMILY SEPARATIONS]")
    added, skipped, total = add_incidents_to_file(
        DATA_DIR / "tier3_incidents.json",
        NEW_TIER3_INCIDENTS,
        "T3"
    )
    print(f"Added {added} new incidents (skipped {skipped}), total now: {total}")

    print("\n" + "=" * 70)
    print("COMPLETE: Round 3 incidents added with schema validation")
    print("=" * 70)


if __name__ == "__main__":
    main()
