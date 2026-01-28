"""
Generate bar charts and pie chart with binary sanctuary classification.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from pathlib import Path

from TIERED_INCIDENT_DATABASE import *

STATE_ABBREV = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
}

# Load data
arrests_df = pd.read_csv('FINAL_MERGED_DATASET.csv')
arrests_df['state_po'] = arrests_df['state'].map(STATE_ABBREV)
arrests_df['is_sanctuary'] = arrests_df['enforcement_classification'] == 'sanctuary'

# Get all incidents
all_incidents = (list(TIER_1_DEATHS_IN_CUSTODY) + list(TIER_2_SHOOTINGS_BY_AGENTS) +
                list(TIER_2_SHOOTINGS_AT_AGENTS) + list(TIER_2_LESS_LETHAL) +
                list(TIER_2_WRONGFUL_DETENTIONS) + list(TIER_3_INCIDENTS) + list(TIER_4_INCIDENTS))

non_immigrant_cats = ['protester', 'journalist', 'bystander', 'officer', 'us_citizen_collateral']

# Count incidents by state
non_imm_counts = {}
for inc in all_incidents:
    if inc.get('victim_category') in non_immigrant_cats:
        state = inc.get('state', 'Unknown')
        if state != 'Unknown' and state:
            state_po = STATE_ABBREV.get(state, state)
            non_imm_counts[state_po] = non_imm_counts.get(state_po, 0) + 1

# Colors
SANCTUARY_COLOR = '#2166ac'  # Blue
NON_SANCTUARY_COLOR = '#b2182b'  # Red

# ========== FIGURE 1: ARRESTS BY STATE (Binary) ==========
arrests_plot = arrests_df[['state_po', 'arrests', 'is_sanctuary']].copy()
arrests_plot = arrests_plot[arrests_plot['arrests'] > 0].sort_values('arrests', ascending=True)

fig1, ax1 = plt.subplots(figsize=(12, 14))
colors1 = [SANCTUARY_COLOR if s else NON_SANCTUARY_COLOR for s in arrests_plot['is_sanctuary']]
bars1 = ax1.barh(arrests_plot['state_po'], arrests_plot['arrests'], color=colors1, edgecolor='black', linewidth=0.5)

for bar, val in zip(bars1, arrests_plot['arrests']):
    ax1.text(val + 500, bar.get_y() + bar.get_height()/2, f'{int(val):,}', va='center', fontsize=8)

ax1.set_xlabel('Number of ICE Arrests', fontsize=12)
ax1.set_ylabel('State', fontsize=12)
ax1.set_title('ICE Arrests by State\n(Blue = Sanctuary, Red = Non-Sanctuary)', fontsize=14, fontweight='bold')
ax1.set_xlim(0, arrests_plot['arrests'].max() * 1.15)

legend_elements = [
    Patch(facecolor=SANCTUARY_COLOR, edgecolor='black', label='Sanctuary'),
    Patch(facecolor=NON_SANCTUARY_COLOR, edgecolor='black', label='Non-Sanctuary'),
]
ax1.legend(handles=legend_elements, loc='lower right', fontsize=10)

plt.tight_layout()
fig1.savefig('bar_arrests_by_state_binary.png', dpi=300, bbox_inches='tight', facecolor='white')
print('Saved: bar_arrests_by_state_binary.png')
plt.close()

# ========== FIGURE 2: NON-IMMIGRANT INCIDENTS BY STATE (Binary) ==========
non_imm_df = pd.DataFrame([
    {'state_po': k, 'incidents': v} for k, v in non_imm_counts.items()
])
sanc_map = arrests_df.set_index('state_po')['is_sanctuary'].to_dict()
non_imm_df['is_sanctuary'] = non_imm_df['state_po'].map(sanc_map)
non_imm_df = non_imm_df.sort_values('incidents', ascending=True)

fig2, ax2 = plt.subplots(figsize=(12, 10))
colors2 = [SANCTUARY_COLOR if s else NON_SANCTUARY_COLOR for s in non_imm_df['is_sanctuary']]
bars2 = ax2.barh(non_imm_df['state_po'], non_imm_df['incidents'], color=colors2, edgecolor='black', linewidth=0.5)

for bar, val in zip(bars2, non_imm_df['incidents']):
    ax2.text(val + 0.3, bar.get_y() + bar.get_height()/2, f'{int(val)}', va='center', fontsize=9)

ax2.set_xlabel('Number of Non-Immigrant Incidents', fontsize=12)
ax2.set_ylabel('State', fontsize=12)
ax2.set_title('Non-Immigrant Incidents by State\n(Protesters, Journalists, Bystanders, Officers, US Citizens)\nBlue = Sanctuary, Red = Non-Sanctuary',
              fontsize=14, fontweight='bold')
ax2.set_xlim(0, non_imm_df['incidents'].max() * 1.2)
ax2.legend(handles=legend_elements, loc='lower right', fontsize=10)

plt.tight_layout()
fig2.savefig('bar_non_immigrant_incidents_binary.png', dpi=300, bbox_inches='tight', facecolor='white')
print('Saved: bar_non_immigrant_incidents_binary.png')
plt.close()

# ========== FIGURE 3: PIE CHART - Clustered by Sanctuary Status ==========
# Separate sanctuary and non-sanctuary states
sanc_states = non_imm_df[non_imm_df['is_sanctuary'] == True].sort_values('incidents', ascending=False)
non_sanc_states = non_imm_df[non_imm_df['is_sanctuary'] == False].sort_values('incidents', ascending=False)

# Create labels and values - sanctuary first, then non-sanctuary
labels = []
values = []
colors = []
explode = []

# Sanctuary states (single blue)
for i, (_, row) in enumerate(sanc_states.iterrows()):
    labels.append(row['state_po'])
    values.append(row['incidents'])
    colors.append(SANCTUARY_COLOR)
    explode.append(0.02)

# Non-sanctuary states (single red)
for i, (_, row) in enumerate(non_sanc_states.iterrows()):
    labels.append(row['state_po'])
    values.append(row['incidents'])
    colors.append(NON_SANCTUARY_COLOR)
    explode.append(0.02)

fig3, ax3 = plt.subplots(figsize=(24, 18))

wedges, texts, autotexts = ax3.pie(
    values, labels=labels, colors=colors, explode=explode,
    autopct='',
    labeldistance=1.12,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2},
    textprops={'fontsize': 36, 'fontweight': 'bold'}
)

# Make label text large and bold
for text in texts:
    text.set_fontweight('bold')
    text.set_fontsize(36)

# Calculate totals
sanc_total = sanc_states['incidents'].sum()
non_sanc_total = non_sanc_states['incidents'].sum()
total = sanc_total + non_sanc_total

ax3.set_title(f'Non-Immigrant Incidents by State\nSanctuary (Blue): {int(sanc_total)} | Non-Sanctuary (Red): {int(non_sanc_total)}',
              fontsize=56, fontweight='bold', pad=40)

# Legend
legend_elements = [
    Patch(facecolor='#2166ac', edgecolor='black', label=f'Sanctuary States: {int(sanc_total)} incidents'),
    Patch(facecolor='#b2182b', edgecolor='black', label=f'Non-Sanctuary States: {int(non_sanc_total)} incidents'),
]
ax3.legend(handles=legend_elements, loc='lower center', fontsize=44, bbox_to_anchor=(0.5, -0.12))

plt.tight_layout()
fig3.savefig('pie_non_immigrant_incidents.png', dpi=300, bbox_inches='tight', facecolor='white')
print('Saved: pie_non_immigrant_incidents.png')
plt.close()

print('\nDone!')
