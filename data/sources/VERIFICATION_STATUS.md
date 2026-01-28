# ICE Incidents Database - Verification Status

Generated: 2026-01-27

## Summary

- **Total entries**: 400
- **Passed verification**: 359+ (90%+)
- **Manually verified**: 8 shooting entries (confirmed against NBC comprehensive article)
- **Needs new sources**: 16 entries
- **Parse/API errors**: 4 entries (need re-verification)

## Recently Fixed

### Shooting Entries (T2-S-xxx)
The following entries were incorrectly flagged as "unrelated" by automated verification.
The NBC comprehensive article clearly lists each incident with specific details:
- **T1-S-002**: Alex Pretti (Minneapolis, Jan 24, 2026) - VERIFIED
- **T2-S-001**: Silverio Villegas Gonzalez (Franklin Park, Sep 12, 2025) - VERIFIED
- **T2-S-002**: Marimar Martinez (Chicago, Oct 4, 2025) - VERIFIED
- **T2-S-003**: Carlitos Ricardo Parias (Los Angeles, Oct 21, 2025) - VERIFIED
- **T2-S-006**: Isaias Sanchez Barboza (Rio Grande City, Dec 11, 2025) - VERIFIED
- **T2-S-009**: Luis David Nino Moncada (Portland, Jan 8, 2026) - VERIFIED
- **T2-S-010**: Yorlenys Betzabeth Zambrano-Contreras (Portland, Jan 8, 2026) - VERIFIED
- **T2-S-011**: Julio Cesar Sosa-Celis (Minneapolis, Jan 14, 2026) - VERIFIED

Source: NBC News comprehensive DHS shooting investigation
URL: https://www.nbcnews.com/news/us-news/ice-shootings-list-border-patrol-trump-immigration-rcna192313

### Fixed Archive
- **T3-P040**: Maria Hadden pepper ball incident - Archive replaced with actual Chicago Tribune article

## Entries Needing Review (No Valid Source Found)

These entries have sources that don't directly support the specific incident.
They should NOT be auto-deleted - they may be real incidents that need different sources.

### High Priority (Tier 1)
1. **T1-D-006** - Nhon Ngoc Nguyen death (El Paso, Apr 16, 2025)
   - Current source: Generic ICE policy page
   - Need: ICE death report or news coverage

### Medium Priority (Tier 2)
2. **T2-LL-002** - Ryanne Mena (Paramount, Jun 7, 2025)
   - Current sources describe different incident (Lauren Tomasi)

3. **T2-LL-008** - Brian Rivera (Broadview, Sep 26, 2025)
   - Current source: General explainer, not specific incident

4. **T2-WD-003** - Andrea Velez (Los Angeles, Jun 24, 2025)
   - Current source: ProPublica general report, not specific incident

5. **T2-WD-005** - Rafie Ollah Shouhed (Van Nuys, Sep 9, 2025)
   - Current source: ProPublica general report, not specific incident

### Lower Priority (Tier 3/4)
6. **T3-049** - Child assault (Baltimore, Jun 8, 2025)
   - Sources cover general ICE activity, not specific incident

7. **T3-051** - Newark raid (Jan 23, 2025)
   - Source describes different raid (November 2025)

8. **T3-111** - New Haven courthouse arrest (Jul 7, 2025)
   - Sources cover different arrests

9. **T3-189** - Krome overcrowding (Oct 2025)
   - Source is general report

10. **T3-218** - San Diego raid (Mar 27, 2025)
    - Source doesn't match specific incident

11. **T3-219** - Laredo raid (May 20, 2025)
    - Source doesn't match specific incident

12. **T3-P013** - LAPD friendly fire (Jun 14, 2025)
    - Sources don't mention friendly fire incident

13. **T3-P030** - Denver protest (Jan 24, 2026)
    - Sources describe different dates

14. **T3-P031** - Minneapolis federal building protest (Jan 15, 2026)
    - Sources describe wrong dates

15. **T4-014** - Jeanette Vizguerra arrest (Aurora, Mar 17, 2025)
    - Source describes different event (February vigil)

## Entries Needing Re-verification (Parse Errors)

These entries have valid sources but LLM verification failed due to parsing issues:
- T3-002
- T3-060
- T3-061
- T3-062
- T4-081

## Unrelated Sources (Consider Removing)

66 sources were flagged as not supporting their entries. Most are:
- Generic overview articles attached to specific incidents
- Articles about different incidents/dates

These should be reviewed individually. The entries themselves may still be valid
if they have other supporting sources.

## Recommendations

1. **DO NOT DELETE** entries based solely on verification failure - many are real incidents
2. Search for better sources for entries in "Needs Review" list
3. Re-run verification on parse error entries
4. Review unrelated sources and consider removing or replacing them
5. For entries with no verifiable source after thorough search, move to an "unverified" tier
