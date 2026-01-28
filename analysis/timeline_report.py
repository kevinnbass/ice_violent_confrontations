"""Generate detailed timeline of non-immigrant incidents."""
from TIERED_INCIDENT_DATABASE import *
from collections import Counter

non_imm_cats = ['protester', 'journalist', 'bystander', 'officer', 'us_citizen_collateral']

all_incidents = (list(TIER_1_DEATHS_IN_CUSTODY) + list(TIER_2_SHOOTINGS_BY_AGENTS) +
                list(TIER_2_SHOOTINGS_AT_AGENTS) + list(TIER_2_LESS_LETHAL) +
                list(TIER_2_WRONGFUL_DETENTIONS) + list(TIER_3_INCIDENTS) + list(TIER_4_INCIDENTS))

non_imm = [i for i in all_incidents if i.get('victim_category') in non_imm_cats]

state_counts = Counter([i.get('state') for i in non_imm])
states_n2 = {s for s, c in state_counts.items() if c >= 2}
incidents_n2 = [i for i in non_imm if i.get('state') in states_n2]

incidents_n2.sort(key=lambda x: (x.get('date', '9999'), x.get('state', '')))

print('=' * 90)
print('TIMELINE: NON-IMMIGRANT ICE-RELATED INCIDENTS (Jan 2025 - Jan 2026)')
print('States with 2+ incidents | 61 total incidents')
print('=' * 90)

current_month = ''
for inc in incidents_n2:
    date = inc.get('date', 'Unknown')
    month = date[:7] if date else 'Unknown'

    if month != current_month:
        current_month = month
        print(f'\n{"="*90}')
        print(f'### {month} ###')
        print('='*90 + '\n')

    state = inc.get('state', '?')
    city = inc.get('city', inc.get('location', ''))
    cat = inc.get('victim_category', '?')
    inc_type = inc.get('incident_type', '?')
    outcome = inc.get('outcome', '')
    weapon = inc.get('weapon_used', '')
    notes = inc.get('notes', '')
    victim_name = inc.get('victim_name', '')
    source_name = inc.get('source_name', '')
    arrest_count = inc.get('arrest_count', '')

    loc_str = f"{state}, {city}" if city else state
    print(f'[{date}] {loc_str}')
    print(f'  Victim: {cat.upper()}' + (f' - {victim_name}' if victim_name else ''))
    print(f'  Type: {inc_type}')
    if weapon:
        print(f'  Weapons: {weapon}')
    if outcome:
        print(f'  Outcome: {outcome}')
    if notes:
        print(f'  Details: {notes}')
    if source_name:
        print(f'  Source: {source_name}')
    print()
