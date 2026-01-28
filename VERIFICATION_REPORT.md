# ICE Incidents Database Verification Report

Generated: 2026-01-27

## Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total entries | 377 | 100% |
| Verified (passed) | 303 | 80.4% |
| Unverified (needs attention) | 74 | 19.6% |

## Verification Method

Used DeepSeek LLM-based verification that:
1. Fetches all source articles for each entry
2. Concatenates sources into a single prompt
3. Evaluates each source individually (relevant/unrelated)
4. Scores verification 0-100 based on source support
5. Provides corrections and flags unrelated sources

## Unverified Entries by File

- `tier1_deaths_in_custody.json`: 8 entries (mostly AILA general resource page) - **FIXED**
- `tier2_shootings.json`: 2 entries (unrelated sources)
- `tier2_less_lethal.json`: 6 entries (ProPublica article doesn't mention specific incidents)
- `tier3_incidents.json`: 51 entries (mix of no sources, date mismatches, partial matches)
- `tier4_incidents.json`: 7 entries (unrelated sources)

## Common Issues Found

1. **Generic sources** - AILA deaths database page used as source but doesn't contain specific incident details
2. **Date mismatches** - Source article from different date than claimed incident
3. **No sources available** - Some entries have broken URLs or unfetchable content
4. **Partial matches** - Source confirms general event but not specific victim/details
5. **Unrelated sources** - Source flagged as describing completely different incidents

## Tier 1 Fixes (Deaths in Custody)

All 8 unverified tier 1 entries have been fixed:

| Entry | Name | Issue | Fix |
|-------|------|-------|-----|
| T1-D-004 | Juan Alexis Tineo-Martinez | AILA generic page | Added ICE press release |
| T1-D-005 | Brayan Rayo-Garzon | AILA generic page | Added ICE press release + FOX 2 |
| T1-D-010 | Johnny Noviello | AILA generic page | Added ICE press release + CNN |
| T1-D-015 | Oscar Rascon Duarte | AILA generic page | Added ICE press release |
| T1-D-025 | Huabing Xie | Wrong source | Added ICE press release + KPBS |
| T1-D-054 | Hasan Ali Moh'D Saleh | AILA generic page | Added WUSF article |
| T1-D-056 | Geraldo Lunas Campos | No name, Wikipedia | Added NPR + PBS, ruled homicide |
| T1-D-059 | Francisco Gaspar-Andres | Wrong source | Added El Paso Matters |

**Result: 49/49 tier 1 entries verified (100%)**

## Tier 2 Fixes (Shootings & Less Lethal)

All 8 unverified tier 2 entries have been fixed:

### Shootings (tier2_shootings.json) - **FIXED**
| Entry | Name | Issue | Fix |
|-------|------|-------|-----|
| T2-S-004 | Jose Garcia-Sorto | Unrelated source | Added FOX News, AZ Family, Phoenix New Times |
| T2-S-007 | Tiago Sousa-Martins | Unrelated source | Added Washington Post, CNN, ABC News |

### Less Lethal (tier2_less_lethal.json) - **FIXED**
| Entry | Name | Issue | Fix |
|-------|------|-------|-----|
| T2-LL-002 | Ryanne Mena | Unnamed journalist | Identified as Ryanne Mena, added ABC7, NPR sources |
| T2-LL-004 | Raven Geary | Generic source | Added US Press Freedom Tracker, Block Club Chicago |
| T2-LL-005 | Leigh Kunkel | Generic source | Added US Press Freedom Tracker |
| T2-LL-006 | Autumn Reidy-Hamer | Wrong name/source | Updated name, added court complaint, ABC7 |
| T2-LL-007 | Enrique Bahena | Generic source | Added Block Club Chicago, corrected date to Oct 23 |
| T2-WD-004 | Daniel Montenegro | Generic source | Added ProPublica article |

**Result: 55/55 tier 2 entries verified (100%)**

## Tier 3 Fixes (tier3_incidents.json) - IN PROGRESS

21 entries fixed so far. Original 51 unverified entries being processed in batches of 5.

### Batch 1 - General/Protest Incidents - **FIXED**
| Entry | Original | Issue | Fix |
|-------|----------|-------|-----|
| T3-002 | Australian journalist | Generic source | Updated to ABC Australia crew, added Latin Times, CBS, Wikipedia |
| T3-010 | Latino US citizen (unnamed) | Generic source | Identified as Willy Aceituno (46), added Al Jazeera, ABC News |
| T3-026 | Eagle Beverage (June 15) | Wrong date, generic source | Corrected to May 20, 2025, Kent WA, added King 5, KUOW |
| T3-049 | Child struck | Unrelated source | Verified via WBAL-TV, WYPR, Maryland Matters |
| T3-054 | Operation Patriot | Generic source | Added ICE.gov, DHS.gov official sources |

### Batch 2 - Replaced Fabricated Entries - **FIXED**
| Entry | Original | Issue | Fix |
|-------|----------|-------|-----|
| T3-062 | Bakersfield farmworkers (Oct) | Broken URL, wrong operation name | Replaced with Operation Return to Sender (Jan 28, 2025), CalMatters, ACLU |
| T3-063 | Homestead tomato (64 detained) | Broken URL, fabricated | Replaced with Immokalee bus raid (Nov 12, 2025, 35 detained), WGCU |
| T3-064 | Miguel Santos-Hernandez (Houston) | Person doesn't exist | Replaced with Dallas ICE facility shooting (Sept 24, 2025), Texas Tribune |
| T3-107 | Minneapolis protest (Jan 10) | Wrong date | Corrected to Jan 11, verified via Al Jazeera, CBS Minnesota |
| T3-108 | Jackson family tear gas | Unrelated source | Verified - Destiny Jackson family, CNN, Fox 10 |

### Batch 3 - Courthouse & Church Arrests - **FIXED**
| Entry | Original | Issue | Fix |
|-------|----------|-------|-----|
| T3-111 | Edgar Hernandez (New Haven) | Broken URL, fabricated | Replaced with Gladys Tentes-Pitiur (July 7, 2025), New Haven Independent |
| T3-112 | Maria Santos-Reyes (San Jose) | Broken URL, fabricated | Replaced with Guillermo Medina Reyes (July 15, 2025), Mercury News |
| T3-113 | Luis Alberto Mendez (Seattle) | Broken URL, fabricated | Replaced with Seattle immigration court arrests (May 21-22, 2025), Axios |
| T3-114 | 5 parishioners (Tucker GA) | Broken URL, fabricated | Replaced with Fuente de Vida Church (June 8, 2025), Decaturish |
| T3-115 | Pastor Rafael Gonzalez | Broken URL, fabricated | Replaced with San Bernardino Diocese parishes (June 20, 2025), NCR |

### Batch 4 - Hospital & Sensitive Location Arrests - **FIXED**
| Entry | Original | Issue | Fix |
|-------|----------|-------|-----|
| T3-117 | Roberto Morales (Minneapolis hospital) | Broken URL, fabricated | Replaced with HCMC incident (Dec 31, 2025), CBS Minnesota |
| T3-118 | ER patients (San Antonio) | Broken URL, fabricated | Replaced with Milagro Solis Portillo (July 3, Glendale), LA Public Press |
| T3-119 | Parent near school (Chicago) | Broken URL, fabricated | Replaced with Diana Santillana Galeano daycare (Nov 5, 2025), WashPost |
| T3-120 | Yolanda Mendez (Bronx cancer) | Broken URL, fabricated | Replaced with Ruben Torres Maldonado (Oct 22, 2025), Block Club Chicago |
| T3-121 | Immigration petitioner (Denver) | Broken URL, fabricated | Replaced with Jair Celis (Dec 2, Salt Lake City), KUER |
| T3-122 | Postpartum mother (Cedars-Sinai) | Broken URL, fabricated | Replaced with Nayra Guzmán (Nov 2025, Chicago), 19th News |

### Batch 5 - Detention & Protest Injuries - **FIXED**
| Entry | Original | Issue | Fix |
|-------|----------|-------|-----|
| T3-162 | Angola hunger strike | Source mismatch | Added NOLA.com, Big Easy Magazine sources |
| T3-163 | Camp J hunger strike | Source mismatch | Added WBRZ, The Advocate sources |
| T3-P003 | Marshall Woodruff | Source doesn't name victim | Added ABC7, KTLA, PetaPixel with victim details |
| T3-P010 | Nick Stern | Wrong source | Added US Press Freedom Tracker, CPJ, LBC |

**Current Status: 192/218 tier 3 entries verified (88.1%)**
- Fixed: 25 entries (5 batches)
- Remaining: ~26 entries

## Summary of Corrections

### Fabricated Entries Replaced
Several entries had fabricated URLs or details that didn't match any real events. These were replaced with verified real incidents:
- T3-063: "Homestead tomato facility" → Immokalee tomato bus raid
- T3-064: "Miguel Santos-Hernandez" → Dallas ICE facility shooting
- T3-111-115: Fabricated courthouse/church arrests → Real documented incidents
- T3-117-122: Fabricated hospital/school arrests → Real documented incidents

### Dates Corrected
- T3-026: June 15 → May 20, 2025 (Eagle Beverage)
- T3-062: Oct 15 → Jan 28, 2025 (Bakersfield farmworkers)
- T3-107: Jan 10 → Jan 11, 2026 (Minneapolis protest)

### Names/Victims Identified
- T3-010: "Latino US citizen (unnamed)" → Willy Aceituno (46)
- T3-119: "Parent dropping off child" → Diana Patricia Santillana Galeano
- T3-P003: Added Marshall Woodruff's age (28) and occupation (filmmaker)
- T3-P010: Added Nick Stern's injury details and legal history

## Tier 4 Status (tier4_incidents.json)
- Total: 55 entries
- Unverified: 7 entries (pending)
