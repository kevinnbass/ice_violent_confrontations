"""
Tiered ICE Violence Maps
========================
Creates 4-panel map showing incidents by data tier:
- Panel 1: Tier 1 only (Official government data - deaths)
- Panel 2: Tier 1-2 (+ FOIA/investigative journalism)
- Panel 3: Tier 1-3 (+ systematic news search)
- Panel 4: Tier 1-4 (all data including ad-hoc)

This visualizes how the "picture" changes as we include less reliable data sources.

NOTE: This file now uses the ice_arrests package for data loading.
      Visualization functions will be moved to ice_arrests/visualization/tiered_maps.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable
import matplotlib.patheffects as pe
from pathlib import Path
import warnings

# Import from centralized config
from config import (
    GEOJSON_PATH,
    OUTPUT_DIR,
    COLORS,
    STATE_ABBREV,
)

# Extract colors from config
BLUE_LOW = COLORS['blue_low']
RED_HIGH = COLORS['red_high']
WHITE_MID = COLORS['white_mid']
NO_INCIDENTS_COLOR = COLORS['no_incidents']
NO_DATA_COLOR = COLORS['no_data']

# For backward compatibility
ABBREV_TO_STATE = {v: k for k, v in STATE_ABBREV.items()}

# Try to use ice_arrests package for data loading
try:
    from ice_arrests import load_incidents

    def _load_tier_incidents(tiers):
        """Load incidents using ice_arrests package."""
        return load_incidents(tiers=tiers)

    _USE_PACKAGE = True
except ImportError:
    _USE_PACKAGE = False

# Fall back to legacy imports if package not available
if not _USE_PACKAGE:
    # Legacy imports with deprecation warning suppressed for internal use
    import warnings as _warnings
    with _warnings.catch_warnings():
        _warnings.simplefilter("ignore", DeprecationWarning)
        from TIERED_INCIDENT_DATABASE import (
            TIER_1_DEATHS_IN_CUSTODY,
            TIER_2_SHOOTINGS_BY_AGENTS,
            TIER_2_SHOOTINGS_AT_AGENTS,
            TIER_2_LESS_LETHAL,
            TIER_2_WRONGFUL_DETENTIONS,
            TIER_3_INCIDENTS,
            TIER_4_INCIDENTS,
        )
else:
    # Load data from package and assign to legacy variable names for compatibility
    _all_incidents = load_incidents()
    TIER_1_DEATHS_IN_CUSTODY = [i for i in _all_incidents if i.get('source_tier') == 1]
    TIER_2_SHOOTINGS_BY_AGENTS = [i for i in _all_incidents if i.get('source_tier') == 2 and 'shooting' in i.get('incident_type', '')]
    TIER_2_SHOOTINGS_AT_AGENTS = [i for i in _all_incidents if i.get('source_tier') == 2 and i.get('incident_type') == 'shooting_at_agent']
    TIER_2_LESS_LETHAL = [i for i in _all_incidents if i.get('source_tier') == 2 and i.get('incident_type') in ('less_lethal', 'wrongful_detention')]
    TIER_2_WRONGFUL_DETENTIONS = [i for i in _all_incidents if i.get('source_tier') == 2 and 'wrongful' in i.get('incident_type', '')]
    TIER_3_INCIDENTS = [i for i in _all_incidents if i.get('source_tier') == 3]
    TIER_4_INCIDENTS = [i for i in _all_incidents if i.get('source_tier') == 4]

# Script directory for local outputs
SCRIPT_DIR = Path(__file__).parent


def set_style():
    """Set consistent plot style."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 10,
        'axes.titlesize': 12,
        'axes.labelsize': 10,
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
    })


def load_state_geodata():
    """Load state boundaries from GeoJSON."""
    gdf = gpd.read_file(GEOJSON_PATH)
    if 'STUSPS' in gdf.columns:
        gdf = gdf.rename(columns={'STUSPS': 'state_po'})
    if 'STATEFP' in gdf.columns:
        gdf = gdf[gdf['STATEFP'].astype(int) <= 56]
    return gdf


def load_arrests_data():
    """Load arrest data by state."""
    try:
        csv_path = SCRIPT_DIR / 'FINAL_MERGED_DATASET.csv'
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            df['state_po'] = df['state'].map(STATE_ABBREV)
            return df[['state', 'state_po', 'arrests', 'enforcement_classification']].copy()
    except Exception as e:
        print(f"Warning: Could not load arrests data: {e}")

    # Fallback: return empty with all states
    return pd.DataFrame({
        'state': list(STATE_ABBREV.keys()),
        'state_po': list(STATE_ABBREV.values()),
        'arrests': [0] * len(STATE_ABBREV),
        'enforcement_classification': ['unknown'] * len(STATE_ABBREV)
    })


def aggregate_incidents_by_tier(max_tier=4):
    """
    Aggregate incidents by state up to specified tier.

    Args:
        max_tier: Include tiers 1 through max_tier (1, 2, 3, or 4)

    Returns:
        DataFrame with state, incident_count, deaths, injuries
    """
    all_incidents = []

    # Always include Tier 1
    all_incidents.extend(TIER_1_DEATHS_IN_CUSTODY)

    if max_tier >= 2:
        all_incidents.extend(TIER_2_SHOOTINGS_BY_AGENTS)
        all_incidents.extend(TIER_2_SHOOTINGS_AT_AGENTS)
        all_incidents.extend(TIER_2_LESS_LETHAL)
        all_incidents.extend(TIER_2_WRONGFUL_DETENTIONS)

    if max_tier >= 3:
        all_incidents.extend(TIER_3_INCIDENTS)

    if max_tier >= 4:
        all_incidents.extend(TIER_4_INCIDENTS)

    # Aggregate by state
    state_data = {}
    for incident in all_incidents:
        state = incident.get('state', 'Unknown')
        if state == 'Unknown' or not state:
            continue

        if state not in state_data:
            state_data[state] = {
                'incident_count': 0,
                'deaths': 0,
                'injuries': 0,
            }

        state_data[state]['incident_count'] += 1

        # Count deaths
        outcome = str(incident.get('outcome', '')).lower()
        incident_type = incident.get('incident_type', '')
        if incident_type == 'death_in_custody' or 'death' in outcome or 'fatal' in outcome or 'killed' in outcome:
            state_data[state]['deaths'] += 1

        # Count injuries
        if incident.get('injury') or 'injury' in outcome or 'wounded' in outcome:
            state_data[state]['injuries'] += 1

    # Convert to DataFrame
    rows = []
    for state, data in state_data.items():
        rows.append({
            'state': state,
            'state_po': STATE_ABBREV.get(state, ''),
            'incident_count': data['incident_count'],
            'deaths': data['deaths'],
            'injuries': data['injuries'],
        })

    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=['state', 'state_po', 'incident_count', 'deaths', 'injuries'])


def create_tiered_maps(output_path=None):
    """
    Create 4-panel map showing cumulative incidents by tier.
    """
    set_style()
    warnings.filterwarnings('ignore')

    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.flatten()

    # Load base data
    states_gdf = load_state_geodata()
    arrests_df = load_arrests_data()

    # Tier configurations
    tier_configs = [
        {'max_tier': 1, 'title': 'Tier 1 Only\n(Official Government Data: Deaths in Custody)', 'color': '#1a5276'},
        {'max_tier': 2, 'title': 'Tiers 1-2\n(+ FOIA / Investigative Journalism)', 'color': '#1a5276'},
        {'max_tier': 3, 'title': 'Tiers 1-3\n(+ Systematic News Search)', 'color': '#1a5276'},
        {'max_tier': 4, 'title': 'Tiers 1-4\n(All Data Including Ad-Hoc)', 'color': '#1a5276'},
    ]

    # Get max incidents across all tiers for consistent color scale
    all_tier_data = aggregate_incidents_by_tier(max_tier=4)
    if not all_tier_data.empty:
        max_incidents = all_tier_data['incident_count'].max()
    else:
        max_incidents = 10

    # Create colormap
    cmap = LinearSegmentedColormap.from_list('incidents', ['#f7fbff', '#08306b'])
    norm = Normalize(vmin=0, vmax=max(max_incidents, 1))

    for i, config in enumerate(tier_configs):
        ax = axes[i]

        # Get incident data for this tier combination
        tier_incidents = aggregate_incidents_by_tier(max_tier=config['max_tier'])

        # Merge with geometry
        plot_gdf = states_gdf.copy()
        plot_gdf = plot_gdf.merge(
            arrests_df[['state_po', 'arrests', 'enforcement_classification']],
            on='state_po',
            how='left'
        )

        if not tier_incidents.empty:
            plot_gdf = plot_gdf.merge(
                tier_incidents[['state_po', 'incident_count', 'deaths', 'injuries']],
                on='state_po',
                how='left'
            )
        else:
            plot_gdf['incident_count'] = 0
            plot_gdf['deaths'] = 0
            plot_gdf['injuries'] = 0

        plot_gdf['incident_count'] = plot_gdf['incident_count'].fillna(0)
        plot_gdf['deaths'] = plot_gdf['deaths'].fillna(0)
        plot_gdf['arrests'] = plot_gdf['arrests'].fillna(0)

        # Categorize states
        plot_gdf['has_data'] = plot_gdf['arrests'] > 0
        plot_gdf['has_incidents'] = plot_gdf['incident_count'] > 0

        # Project
        plot_gdf = plot_gdf.to_crs('ESRI:102003')
        continental = plot_gdf[~plot_gdf['state_po'].isin(['AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP'])].copy()

        # Plot each state
        for idx, row in continental.iterrows():
            if not row['has_data']:
                color = NO_DATA_COLOR
            elif row['incident_count'] == 0:
                color = NO_INCIDENTS_COLOR
            else:
                color = cmap(norm(row['incident_count']))

            continental[continental.index == idx].plot(
                ax=ax, color=[color], edgecolor='black', linewidth=0.5
            )

            # Hatching for no-data states
            if not row['has_data']:
                continental[continental.index == idx].plot(
                    ax=ax, facecolor='none', edgecolor='gray', linewidth=0.3, hatch='///'
                )

        # Add incident count labels
        for idx, row in continental.iterrows():
            centroid = row.geometry.centroid
            if row['incident_count'] > 0:
                label = f"{int(row['incident_count'])}"
                # Color based on background
                text_color = 'white' if row['incident_count'] > max_incidents * 0.5 else 'black'
            elif row['has_data']:
                label = "0"
                text_color = 'gray'
            else:
                label = "?"
                text_color = 'gray'

            fontsize = 6 if row['state_po'] in ['CT', 'RI', 'DE', 'NJ', 'MD', 'MA', 'NH', 'VT'] else 7

            ax.annotate(
                label, xy=(centroid.x, centroid.y),
                ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color=text_color,
                path_effects=[pe.withStroke(linewidth=1.5, foreground='white' if text_color == 'black' else 'black')]
            )

        ax.axis('off')
        ax.set_title(config['title'], fontsize=12, fontweight='bold', pad=10)

        # Stats annotation
        total_incidents = tier_incidents['incident_count'].sum() if not tier_incidents.empty else 0
        total_deaths = tier_incidents['deaths'].sum() if not tier_incidents.empty else 0
        states_with_incidents = (tier_incidents['incident_count'] > 0).sum() if not tier_incidents.empty else 0

        stats_text = f"Total: {int(total_incidents)} incidents | {int(total_deaths)} deaths | {states_with_incidents} states"
        ax.text(0.5, -0.02, stats_text, transform=ax.transAxes, ha='center', fontsize=9, style='italic')

    # Main title
    fig.suptitle(
        'ICE Incidents by Data Source Tier\nShowing How the Picture Changes with Each Data Quality Level',
        fontsize=16, fontweight='bold', y=0.98
    )

    # Shared colorbar
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes([0.25, 0.02, 0.5, 0.015])
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Number of Incidents (0 = zero documented; ? = no data)', fontsize=10)

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=NO_INCIDENTS_COLOR, edgecolor='black', label='Zero incidents (has arrest data)'),
        mpatches.Patch(facecolor=NO_DATA_COLOR, edgecolor='black', hatch='///', label='No data collected'),
    ]
    fig.legend(handles=legend_elements, loc='lower right', fontsize=9,
               bbox_to_anchor=(0.98, 0.02), framealpha=0.95)

    # Source note
    fig.text(0.02, 0.01,
            'Sources: ICE Detainee Death Reporting (Tier 1); The Trace, ProPublica, ACLU (Tier 2); '
            'NBC, AP, CNN systematic search (Tier 3); Ad-hoc news (Tier 4) | Period: 2025-2026',
            fontsize=8, style='italic', color='gray')

    plt.tight_layout(rect=[0, 0.05, 1, 0.96])

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"Saved: {output_path}")
    else:
        plt.show()

    return fig


def create_tiered_ratio_maps(output_path=None):
    """
    Create 4-panel map showing violence RATIO (per 1000 arrests) by tier.
    Each panel has its own color scale normalized to that tier's data.
    """
    set_style()
    warnings.filterwarnings('ignore')

    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.flatten()

    # Load base data
    states_gdf = load_state_geodata()
    arrests_df = load_arrests_data()

    # Create colormap: Blue (low) -> White (mid) -> Red (high)
    cmap = LinearSegmentedColormap.from_list('violence_ratio', [BLUE_LOW, WHITE_MID, RED_HIGH])

    tier_configs = [
        {'max_tier': 1, 'title': 'Tier 1 Only\n(Official Deaths in Custody)'},
        {'max_tier': 2, 'title': 'Tiers 1-2\n(+ Shootings, Force, Wrongful Detentions)'},
        {'max_tier': 3, 'title': 'Tiers 1-3\n(+ Systematic News: Raids, Protests)'},
        {'max_tier': 4, 'title': 'Tiers 1-4\n(All Available Data)'},
    ]

    for i, config in enumerate(tier_configs):
        ax = axes[i]

        # Get incident data
        tier_incidents = aggregate_incidents_by_tier(max_tier=config['max_tier'])

        # Merge with geometry and arrests
        plot_gdf = states_gdf.copy()
        plot_gdf = plot_gdf.merge(
            arrests_df[['state_po', 'arrests', 'enforcement_classification']],
            on='state_po', how='left'
        )

        if not tier_incidents.empty:
            plot_gdf = plot_gdf.merge(
                tier_incidents[['state_po', 'incident_count', 'deaths']],
                on='state_po', how='left'
            )
        else:
            plot_gdf['incident_count'] = 0
            plot_gdf['deaths'] = 0

        plot_gdf['incident_count'] = plot_gdf['incident_count'].fillna(0)
        plot_gdf['arrests'] = plot_gdf['arrests'].fillna(0)

        # Calculate ratio
        plot_gdf['ratio'] = np.where(
            plot_gdf['arrests'] > 0,
            plot_gdf['incident_count'] / plot_gdf['arrests'] * 1000,
            0
        )

        plot_gdf['has_data'] = plot_gdf['arrests'] > 0
        plot_gdf['has_incidents'] = plot_gdf['incident_count'] > 0

        # Calculate per-panel normalization (only for states with incidents)
        states_with_incidents = plot_gdf[plot_gdf['has_incidents']]
        if not states_with_incidents.empty:
            panel_min = states_with_incidents['ratio'].min()
            panel_max = states_with_incidents['ratio'].max()
        else:
            panel_min, panel_max = 0, 1

        # Ensure we have a valid range
        if panel_max <= panel_min:
            panel_max = panel_min + 0.1

        norm = Normalize(vmin=panel_min, vmax=panel_max)

        # Project
        plot_gdf = plot_gdf.to_crs('ESRI:102003')
        continental = plot_gdf[~plot_gdf['state_po'].isin(['AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP'])].copy()

        # Plot
        for idx, row in continental.iterrows():
            if not row['has_data']:
                color = NO_DATA_COLOR
            elif row['incident_count'] == 0:
                color = NO_INCIDENTS_COLOR
            else:
                color = cmap(norm(row['ratio']))

            continental[continental.index == idx].plot(
                ax=ax, color=[color], edgecolor='black', linewidth=0.5
            )

            if not row['has_data']:
                continental[continental.index == idx].plot(
                    ax=ax, facecolor='none', edgecolor='gray', linewidth=0.3, hatch='///'
                )

        # Labels - S for sanctuary states with incidents, blank otherwise
        for idx, row in continental.iterrows():
            centroid = row.geometry.centroid
            is_sanctuary = row.get('enforcement_classification') == 'sanctuary'

            if row['has_incidents'] and is_sanctuary:
                label = "S"
                fontsize = 9
            else:
                label = ""
                fontsize = 7

            if label:
                ax.annotate(label, xy=(centroid.x, centroid.y), ha='center', va='center',
                           fontsize=fontsize, fontweight='bold', color='black')

        ax.axis('off')

        # Title with scale info
        ax.set_title(f"{config['title']}\n(Scale: {panel_min:.2f} - {panel_max:.2f})",
                    fontsize=11, fontweight='bold', pad=10)

        # Stats
        total_incidents = tier_incidents['incident_count'].sum() if not tier_incidents.empty else 0
        states_with = (tier_incidents['incident_count'] > 0).sum() if not tier_incidents.empty else 0
        stats_text = f"{int(total_incidents)} incidents across {states_with} states"
        ax.text(0.5, -0.02, stats_text, transform=ax.transAxes, ha='center', fontsize=9, style='italic')

        # Per-panel colorbar
        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        # Position colorbars below each panel
        if i == 0:
            cbar_ax = fig.add_axes([0.08, 0.48, 0.38, 0.012])
        elif i == 1:
            cbar_ax = fig.add_axes([0.54, 0.48, 0.38, 0.012])
        elif i == 2:
            cbar_ax = fig.add_axes([0.08, 0.02, 0.38, 0.012])
        else:
            cbar_ax = fig.add_axes([0.54, 0.02, 0.38, 0.012])

        cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
        cbar.set_ticks([panel_min, (panel_min + panel_max) / 2, panel_max])
        cbar.set_ticklabels([f'{panel_min:.2f}', f'{(panel_min + panel_max) / 2:.2f}', f'{panel_max:.2f}'])
        cbar.ax.tick_params(labelsize=7)

    # Title
    fig.suptitle(
        'ICE Violence Ratio by Data Source Tier\n("S" = Sanctuary State - Per 1,000 Arrests)',
        fontsize=16, fontweight='bold', y=0.99
    )

    # Legend
    legend_elements = [
        mpatches.Patch(facecolor=BLUE_LOW, edgecolor='black', label='Low (for this tier)'),
        mpatches.Patch(facecolor=RED_HIGH, edgecolor='black', label='High (for this tier)'),
        mpatches.Patch(facecolor=NO_INCIDENTS_COLOR, edgecolor='black', label='Zero incidents'),
        mpatches.Patch(facecolor=NO_DATA_COLOR, edgecolor='black', hatch='///', label='No data'),
    ]
    fig.legend(handles=legend_elements, loc='center right', fontsize=9,
               bbox_to_anchor=(0.99, 0.5), framealpha=0.95)

    plt.tight_layout(rect=[0, 0.06, 0.92, 0.96])

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"Saved: {output_path}")
    else:
        plt.show()

    return fig


def aggregate_incidents_by_tier_and_category(max_tier=4, victim_categories=None):
    """
    Aggregate incidents by state up to specified tier, filtered by victim category.

    Args:
        max_tier: Include tiers 1 through max_tier (1, 2, 3, or 4)
        victim_categories: List of victim_category values to include, or None for all

    Returns:
        DataFrame with state, incident_count, deaths, injuries
    """
    all_incidents = []

    # Always include Tier 1
    all_incidents.extend(TIER_1_DEATHS_IN_CUSTODY)

    if max_tier >= 2:
        all_incidents.extend(TIER_2_SHOOTINGS_BY_AGENTS)
        all_incidents.extend(TIER_2_SHOOTINGS_AT_AGENTS)
        all_incidents.extend(TIER_2_LESS_LETHAL)
        all_incidents.extend(TIER_2_WRONGFUL_DETENTIONS)

    if max_tier >= 3:
        all_incidents.extend(TIER_3_INCIDENTS)

    if max_tier >= 4:
        all_incidents.extend(TIER_4_INCIDENTS)

    # Filter by victim category if specified
    if victim_categories:
        all_incidents = [i for i in all_incidents if i.get('victim_category') in victim_categories]

    # Aggregate by state
    state_data = {}
    for incident in all_incidents:
        state = incident.get('state', 'Unknown')
        if state == 'Unknown' or not state:
            continue

        if state not in state_data:
            state_data[state] = {'incident_count': 0, 'deaths': 0, 'injuries': 0}

        state_data[state]['incident_count'] += 1

        outcome = str(incident.get('outcome', '')).lower()
        incident_type = incident.get('incident_type', '')
        if incident_type == 'death_in_custody' or 'death' in outcome or 'fatal' in outcome or 'killed' in outcome:
            state_data[state]['deaths'] += 1

        if incident.get('injury') or 'injury' in outcome or 'wounded' in outcome:
            state_data[state]['injuries'] += 1

    rows = []
    for state, data in state_data.items():
        rows.append({
            'state': state,
            'state_po': STATE_ABBREV.get(state, ''),
            'incident_count': data['incident_count'],
            'deaths': data['deaths'],
            'injuries': data['injuries'],
        })

    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=['state', 'state_po', 'incident_count', 'deaths', 'injuries'])


def create_category_tiered_ratio_map(victim_categories, category_name, output_path=None):
    """
    Create 4-panel tiered ratio map for specific victim category.
    Each panel has its own color scale normalized to that tier's data.
    """
    set_style()
    warnings.filterwarnings('ignore')

    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.flatten()

    states_gdf = load_state_geodata()
    arrests_df = load_arrests_data()

    cmap = LinearSegmentedColormap.from_list('violence_ratio', [BLUE_LOW, WHITE_MID, RED_HIGH])

    tier_configs = [
        {'max_tier': 1, 'title': 'Tier 1 Only\n(Official Government Data)'},
        {'max_tier': 2, 'title': 'Tiers 1-2\n(+ FOIA / Investigative)'},
        {'max_tier': 3, 'title': 'Tiers 1-3\n(+ Systematic News)'},
        {'max_tier': 4, 'title': 'Tiers 1-4\n(All Data)'},
    ]

    for i, config in enumerate(tier_configs):
        ax = axes[i]

        tier_incidents = aggregate_incidents_by_tier_and_category(
            max_tier=config['max_tier'], victim_categories=victim_categories
        )

        plot_gdf = states_gdf.copy()
        plot_gdf = plot_gdf.merge(
            arrests_df[['state_po', 'arrests']], on='state_po', how='left'
        )

        if not tier_incidents.empty:
            plot_gdf = plot_gdf.merge(
                tier_incidents[['state_po', 'incident_count', 'deaths']],
                on='state_po', how='left'
            )
        else:
            plot_gdf['incident_count'] = 0
            plot_gdf['deaths'] = 0

        plot_gdf['incident_count'] = plot_gdf['incident_count'].fillna(0)
        plot_gdf['arrests'] = plot_gdf['arrests'].fillna(0)

        plot_gdf['ratio'] = np.where(
            plot_gdf['arrests'] > 0,
            plot_gdf['incident_count'] / plot_gdf['arrests'] * 1000, 0
        )

        plot_gdf['has_data'] = plot_gdf['arrests'] > 0
        plot_gdf['has_incidents'] = plot_gdf['incident_count'] > 0

        # Calculate per-panel normalization (only for states with incidents)
        states_with_incidents = plot_gdf[plot_gdf['has_incidents']]
        if not states_with_incidents.empty:
            panel_min = states_with_incidents['ratio'].min()
            panel_max = states_with_incidents['ratio'].max()
        else:
            panel_min, panel_max = 0, 1

        # Ensure we have a valid range
        if panel_max <= panel_min:
            panel_max = panel_min + 0.1

        norm = Normalize(vmin=panel_min, vmax=panel_max)

        plot_gdf = plot_gdf.to_crs('ESRI:102003')
        continental = plot_gdf[~plot_gdf['state_po'].isin(['AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP'])].copy()

        for idx, row in continental.iterrows():
            if not row['has_data']:
                color = NO_DATA_COLOR
            elif row['incident_count'] == 0:
                color = NO_INCIDENTS_COLOR
            else:
                color = cmap(norm(row['ratio']))

            continental[continental.index == idx].plot(
                ax=ax, color=[color], edgecolor='black', linewidth=0.5
            )

            if not row['has_data']:
                continental[continental.index == idx].plot(
                    ax=ax, facecolor='none', edgecolor='gray', linewidth=0.3, hatch='///'
                )

        # Labels - S for sanctuary states with incidents, blank otherwise
        for idx, row in continental.iterrows():
            centroid = row.geometry.centroid
            is_sanctuary = row.get('enforcement_classification') == 'sanctuary'

            if row['has_incidents'] and is_sanctuary:
                label = "S"
                fontsize = 9
            else:
                label = ""
                fontsize = 7

            if label:
                ax.annotate(label, xy=(centroid.x, centroid.y), ha='center', va='center',
                           fontsize=fontsize, fontweight='bold', color='black')

        ax.axis('off')

        # Title with scale info
        ax.set_title(f"{config['title']}\n(Scale: {panel_min:.2f} - {panel_max:.2f})",
                    fontsize=11, fontweight='bold', pad=10)

        total_incidents = tier_incidents['incident_count'].sum() if not tier_incidents.empty else 0
        states_with = (tier_incidents['incident_count'] > 0).sum() if not tier_incidents.empty else 0
        stats_text = f"{int(total_incidents)} incidents across {states_with} states"
        ax.text(0.5, -0.02, stats_text, transform=ax.transAxes, ha='center', fontsize=9, style='italic')

        # Per-panel colorbar
        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        # Position colorbars below each panel
        if i == 0:
            cbar_ax = fig.add_axes([0.08, 0.48, 0.38, 0.012])
        elif i == 1:
            cbar_ax = fig.add_axes([0.54, 0.48, 0.38, 0.012])
        elif i == 2:
            cbar_ax = fig.add_axes([0.08, 0.02, 0.38, 0.012])
        else:
            cbar_ax = fig.add_axes([0.54, 0.02, 0.38, 0.012])

        cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
        cbar.set_ticks([panel_min, (panel_min + panel_max) / 2, panel_max])
        cbar.set_ticklabels([f'{panel_min:.2f}', f'{(panel_min + panel_max) / 2:.2f}', f'{panel_max:.2f}'])
        cbar.ax.tick_params(labelsize=7)

    fig.suptitle(
        f'{category_name} Incidents by Data Tier\n(Per 1,000 ICE Arrests - "S" = Sanctuary State)',
        fontsize=16, fontweight='bold', y=0.99
    )

    legend_elements = [
        mpatches.Patch(facecolor=BLUE_LOW, edgecolor='black', label='Low (for this tier)'),
        mpatches.Patch(facecolor=RED_HIGH, edgecolor='black', label='High (for this tier)'),
        mpatches.Patch(facecolor=NO_INCIDENTS_COLOR, edgecolor='black', label='Zero incidents'),
        mpatches.Patch(facecolor=NO_DATA_COLOR, edgecolor='black', hatch='///', label='No data'),
    ]
    fig.legend(handles=legend_elements, loc='center right', fontsize=9,
               bbox_to_anchor=(0.99, 0.5), framealpha=0.95)

    plt.tight_layout(rect=[0, 0.06, 0.92, 0.96])

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"Saved: {output_path}")
    else:
        plt.show()

    return fig


def aggregate_incidents_single_tier(tier, victim_categories=None):
    """
    Aggregate incidents by state for a SINGLE tier only (not cumulative).

    Args:
        tier: Which tier to include (1, 2, 3, 4, or "3-4" for combined)
        victim_categories: List of victim_category values to include, or None for all

    Returns:
        DataFrame with state, incident_count, deaths, injuries
    """
    if tier == 1:
        all_incidents = list(TIER_1_DEATHS_IN_CUSTODY)
    elif tier == 2:
        all_incidents = (list(TIER_2_SHOOTINGS_BY_AGENTS) +
                        list(TIER_2_SHOOTINGS_AT_AGENTS) +
                        list(TIER_2_LESS_LETHAL) +
                        list(TIER_2_WRONGFUL_DETENTIONS))
    elif tier == 3:
        all_incidents = list(TIER_3_INCIDENTS)
    elif tier == 4:
        all_incidents = list(TIER_4_INCIDENTS)
    elif tier == "3-4":
        all_incidents = list(TIER_3_INCIDENTS) + list(TIER_4_INCIDENTS)
    elif tier == "all":
        all_incidents = (list(TIER_1_DEATHS_IN_CUSTODY) +
                        list(TIER_2_SHOOTINGS_BY_AGENTS) +
                        list(TIER_2_SHOOTINGS_AT_AGENTS) +
                        list(TIER_2_LESS_LETHAL) +
                        list(TIER_2_WRONGFUL_DETENTIONS) +
                        list(TIER_3_INCIDENTS) +
                        list(TIER_4_INCIDENTS))
    else:
        all_incidents = []

    # Filter by victim category if specified
    if victim_categories:
        all_incidents = [i for i in all_incidents if i.get('victim_category') in victim_categories]

    # Aggregate by state
    state_data = {}
    for incident in all_incidents:
        state = incident.get('state', 'Unknown')
        if state == 'Unknown' or not state:
            continue

        if state not in state_data:
            state_data[state] = {'incident_count': 0, 'deaths': 0, 'injuries': 0}

        state_data[state]['incident_count'] += 1

        outcome = str(incident.get('outcome', '')).lower()
        incident_type = incident.get('incident_type', '')
        if incident_type == 'death_in_custody' or 'death' in outcome or 'fatal' in outcome or 'killed' in outcome:
            state_data[state]['deaths'] += 1

        if incident.get('injury') or 'injury' in outcome or 'wounded' in outcome:
            state_data[state]['injuries'] += 1

    rows = []
    for state, data in state_data.items():
        rows.append({
            'state': state,
            'state_po': STATE_ABBREV.get(state, ''),
            'incident_count': data['incident_count'],
            'deaths': data['deaths'],
            'injuries': data['injuries'],
        })

    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=['state', 'state_po', 'incident_count', 'deaths', 'injuries'])


def create_isolated_tier_ratio_maps(output_path=None):
    """
    Create 4-panel map showing violence RATIO for each tier IN ISOLATION.
    Tier 1 only, Tier 2 only, Tier 3 only, Tier 4 only.
    """
    set_style()
    warnings.filterwarnings('ignore')

    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.flatten()

    states_gdf = load_state_geodata()
    arrests_df = load_arrests_data()

    cmap = LinearSegmentedColormap.from_list('violence_ratio', [BLUE_LOW, WHITE_MID, RED_HIGH])

    tier_configs = [
        {'tier': 1, 'title': 'Tier 1 Only\n(Official Government Data: Deaths in Custody)'},
        {'tier': 2, 'title': 'Tier 2 Only\n(FOIA/Investigative: Shootings, Force, Wrongful Detentions)'},
        {'tier': "3-4", 'title': 'Tiers 3-4 Combined\n(News Media: Raids, Protests, Less-Lethal)'},
        {'tier': "all", 'title': 'All Tiers Combined\n(Complete Dataset)'},
    ]

    for i, config in enumerate(tier_configs):
        ax = axes[i]

        tier_incidents = aggregate_incidents_single_tier(tier=config['tier'])

        plot_gdf = states_gdf.copy()
        plot_gdf = plot_gdf.merge(
            arrests_df[['state_po', 'arrests', 'enforcement_classification']],
            on='state_po', how='left'
        )

        if not tier_incidents.empty:
            plot_gdf = plot_gdf.merge(
                tier_incidents[['state_po', 'incident_count', 'deaths']],
                on='state_po', how='left'
            )
        else:
            plot_gdf['incident_count'] = 0
            plot_gdf['deaths'] = 0

        plot_gdf['incident_count'] = plot_gdf['incident_count'].fillna(0)
        plot_gdf['arrests'] = plot_gdf['arrests'].fillna(0)

        plot_gdf['ratio'] = np.where(
            plot_gdf['arrests'] > 0,
            plot_gdf['incident_count'] / plot_gdf['arrests'] * 1000,
            0
        )

        plot_gdf['has_data'] = plot_gdf['arrests'] > 0
        plot_gdf['has_incidents'] = plot_gdf['incident_count'] > 0

        # Per-panel normalization
        states_with_incidents = plot_gdf[plot_gdf['has_incidents']]
        if not states_with_incidents.empty:
            panel_min = states_with_incidents['ratio'].min()
            panel_max = states_with_incidents['ratio'].max()
        else:
            panel_min, panel_max = 0, 1

        if panel_max <= panel_min:
            panel_max = panel_min + 0.1

        norm = Normalize(vmin=panel_min, vmax=panel_max)

        plot_gdf = plot_gdf.to_crs('ESRI:102003')
        continental = plot_gdf[~plot_gdf['state_po'].isin(['AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP'])].copy()

        for idx, row in continental.iterrows():
            if not row['has_data']:
                color = NO_DATA_COLOR
            elif row['incident_count'] == 0:
                color = NO_INCIDENTS_COLOR
            else:
                color = cmap(norm(row['ratio']))

            continental[continental.index == idx].plot(
                ax=ax, color=[color], edgecolor='black', linewidth=0.5
            )

            if not row['has_data']:
                continental[continental.index == idx].plot(
                    ax=ax, facecolor='none', edgecolor='gray', linewidth=0.3, hatch='///'
                )

        # Labels - S for sanctuary states with incidents, blank otherwise
        for idx, row in continental.iterrows():
            centroid = row.geometry.centroid
            is_sanctuary = row.get('enforcement_classification') == 'sanctuary'

            if row['has_incidents'] and is_sanctuary:
                label = "S"
                fontsize = 9
            else:
                label = ""
                fontsize = 7

            if label:
                ax.annotate(label, xy=(centroid.x, centroid.y), ha='center', va='center',
                           fontsize=fontsize, fontweight='bold', color='black')

        ax.axis('off')
        ax.set_title(f"{config['title']}\n(Scale: {panel_min:.2f} - {panel_max:.2f})",
                    fontsize=10, fontweight='bold', pad=10)

        total_incidents = tier_incidents['incident_count'].sum() if not tier_incidents.empty else 0
        states_with = (tier_incidents['incident_count'] > 0).sum() if not tier_incidents.empty else 0
        stats_text = f"{int(total_incidents)} incidents across {states_with} states"
        ax.text(0.5, -0.02, stats_text, transform=ax.transAxes, ha='center', fontsize=9, style='italic')

        # Per-panel colorbar
        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        if i == 0:
            cbar_ax = fig.add_axes([0.08, 0.48, 0.38, 0.012])
        elif i == 1:
            cbar_ax = fig.add_axes([0.54, 0.48, 0.38, 0.012])
        elif i == 2:
            cbar_ax = fig.add_axes([0.08, 0.02, 0.38, 0.012])
        else:
            cbar_ax = fig.add_axes([0.54, 0.02, 0.38, 0.012])

        cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
        cbar.set_ticks([panel_min, (panel_min + panel_max) / 2, panel_max])
        cbar.set_ticklabels([f'{panel_min:.2f}', f'{(panel_min + panel_max) / 2:.2f}', f'{panel_max:.2f}'])
        cbar.ax.tick_params(labelsize=7)

    fig.suptitle(
        'ICE Violence Ratio by ISOLATED Data Tier\n("S" = Sanctuary State - Per 1,000 Arrests)',
        fontsize=16, fontweight='bold', y=0.99
    )

    legend_elements = [
        mpatches.Patch(facecolor=BLUE_LOW, edgecolor='black', label='Low (for this tier)'),
        mpatches.Patch(facecolor=RED_HIGH, edgecolor='black', label='High (for this tier)'),
        mpatches.Patch(facecolor=NO_INCIDENTS_COLOR, edgecolor='black', label='Zero incidents'),
        mpatches.Patch(facecolor=NO_DATA_COLOR, edgecolor='black', hatch='///', label='No data'),
    ]
    fig.legend(handles=legend_elements, loc='center right', fontsize=9,
               bbox_to_anchor=(0.99, 0.5), framealpha=0.95)

    plt.tight_layout(rect=[0, 0.06, 0.92, 0.96])

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"Saved: {output_path}")
    else:
        plt.show()

    return fig


def create_category_isolated_tier_ratio_map(victim_categories, category_name, output_path=None):
    """
    Create 4-panel map for specific victim category with each tier IN ISOLATION.
    """
    set_style()
    warnings.filterwarnings('ignore')

    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.flatten()

    states_gdf = load_state_geodata()
    arrests_df = load_arrests_data()

    cmap = LinearSegmentedColormap.from_list('violence_ratio', [BLUE_LOW, WHITE_MID, RED_HIGH])

    tier_configs = [
        {'tier': 1, 'title': 'Tier 1 Only\n(Official Government Data)'},
        {'tier': 2, 'title': 'Tier 2 Only\n(FOIA / Investigative)'},
        {'tier': "3-4", 'title': 'Tiers 3-4 Combined\n(News Media)'},
        {'tier': "all", 'title': 'All Tiers Combined\n(Complete Dataset)'},
    ]

    for i, config in enumerate(tier_configs):
        ax = axes[i]

        tier_incidents = aggregate_incidents_single_tier(
            tier=config['tier'], victim_categories=victim_categories
        )

        plot_gdf = states_gdf.copy()
        plot_gdf = plot_gdf.merge(
            arrests_df[['state_po', 'arrests']], on='state_po', how='left'
        )

        if not tier_incidents.empty:
            plot_gdf = plot_gdf.merge(
                tier_incidents[['state_po', 'incident_count', 'deaths']],
                on='state_po', how='left'
            )
        else:
            plot_gdf['incident_count'] = 0
            plot_gdf['deaths'] = 0

        plot_gdf['incident_count'] = plot_gdf['incident_count'].fillna(0)
        plot_gdf['arrests'] = plot_gdf['arrests'].fillna(0)

        plot_gdf['ratio'] = np.where(
            plot_gdf['arrests'] > 0,
            plot_gdf['incident_count'] / plot_gdf['arrests'] * 1000, 0
        )

        plot_gdf['has_data'] = plot_gdf['arrests'] > 0
        plot_gdf['has_incidents'] = plot_gdf['incident_count'] > 0

        states_with_incidents = plot_gdf[plot_gdf['has_incidents']]
        if not states_with_incidents.empty:
            panel_min = states_with_incidents['ratio'].min()
            panel_max = states_with_incidents['ratio'].max()
        else:
            panel_min, panel_max = 0, 1

        if panel_max <= panel_min:
            panel_max = panel_min + 0.1

        norm = Normalize(vmin=panel_min, vmax=panel_max)

        plot_gdf = plot_gdf.to_crs('ESRI:102003')
        continental = plot_gdf[~plot_gdf['state_po'].isin(['AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP'])].copy()

        for idx, row in continental.iterrows():
            if not row['has_data']:
                color = NO_DATA_COLOR
            elif row['incident_count'] == 0:
                color = NO_INCIDENTS_COLOR
            else:
                color = cmap(norm(row['ratio']))

            continental[continental.index == idx].plot(
                ax=ax, color=[color], edgecolor='black', linewidth=0.5
            )

            if not row['has_data']:
                continental[continental.index == idx].plot(
                    ax=ax, facecolor='none', edgecolor='gray', linewidth=0.3, hatch='///'
                )

        # Labels - S for sanctuary states with incidents, blank otherwise
        for idx, row in continental.iterrows():
            centroid = row.geometry.centroid
            is_sanctuary = row.get('enforcement_classification') == 'sanctuary'

            if row['has_incidents'] and is_sanctuary:
                label = "S"
                fontsize = 9
            else:
                label = ""
                fontsize = 7

            if label:
                ax.annotate(label, xy=(centroid.x, centroid.y), ha='center', va='center',
                           fontsize=fontsize, fontweight='bold', color='black')

        ax.axis('off')
        ax.set_title(f"{config['title']}\n(Scale: {panel_min:.2f} - {panel_max:.2f})",
                    fontsize=10, fontweight='bold', pad=10)

        total_incidents = tier_incidents['incident_count'].sum() if not tier_incidents.empty else 0
        states_with = (tier_incidents['incident_count'] > 0).sum() if not tier_incidents.empty else 0
        stats_text = f"{int(total_incidents)} incidents across {states_with} states"
        ax.text(0.5, -0.02, stats_text, transform=ax.transAxes, ha='center', fontsize=9, style='italic')

        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        if i == 0:
            cbar_ax = fig.add_axes([0.08, 0.48, 0.38, 0.012])
        elif i == 1:
            cbar_ax = fig.add_axes([0.54, 0.48, 0.38, 0.012])
        elif i == 2:
            cbar_ax = fig.add_axes([0.08, 0.02, 0.38, 0.012])
        else:
            cbar_ax = fig.add_axes([0.54, 0.02, 0.38, 0.012])

        cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
        cbar.set_ticks([panel_min, (panel_min + panel_max) / 2, panel_max])
        cbar.set_ticklabels([f'{panel_min:.2f}', f'{(panel_min + panel_max) / 2:.2f}', f'{panel_max:.2f}'])
        cbar.ax.tick_params(labelsize=7)

    fig.suptitle(
        f'{category_name} Incidents by ISOLATED Tier\n("S" = Sanctuary State - Per 1,000 Arrests)',
        fontsize=16, fontweight='bold', y=0.99
    )

    legend_elements = [
        mpatches.Patch(facecolor=BLUE_LOW, edgecolor='black', label='Low (for this tier)'),
        mpatches.Patch(facecolor=RED_HIGH, edgecolor='black', label='High (for this tier)'),
        mpatches.Patch(facecolor=NO_INCIDENTS_COLOR, edgecolor='black', label='Zero incidents'),
        mpatches.Patch(facecolor=NO_DATA_COLOR, edgecolor='black', hatch='///', label='No data'),
    ]
    fig.legend(handles=legend_elements, loc='center right', fontsize=9,
               bbox_to_anchor=(0.99, 0.5), framealpha=0.95)

    plt.tight_layout(rect=[0, 0.06, 0.92, 0.96])

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"Saved: {output_path}")
    else:
        plt.show()

    return fig


def create_single_panel_incident_map(victim_categories, category_name, output_path=None, min_incidents=1):
    """
    Create a single-panel map showing raw incident counts (not ratio).
    White = 0, Dark red = maximum.
    S label for sanctuary states with incident count below.

    Args:
        min_incidents: Minimum incidents to display (default 1, set to 2 to exclude n=1 states)
    """
    set_style()
    warnings.filterwarnings('ignore')

    fig, ax = plt.subplots(figsize=(16, 12))

    states_gdf = load_state_geodata()
    arrests_df = load_arrests_data()

    # Get all incidents across all tiers
    all_incidents = aggregate_incidents_single_tier(tier="all", victim_categories=victim_categories)

    # Merge data
    plot_gdf = states_gdf.copy()
    plot_gdf = plot_gdf.merge(
        arrests_df[['state_po', 'arrests', 'enforcement_classification']], on='state_po', how='left'
    )

    if not all_incidents.empty:
        plot_gdf = plot_gdf.merge(
            all_incidents[['state_po', 'incident_count']],
            on='state_po', how='left'
        )
    else:
        plot_gdf['incident_count'] = 0

    plot_gdf['incident_count'] = plot_gdf['incident_count'].fillna(0)

    # For display purposes, treat below-threshold as 0
    plot_gdf['display_count'] = plot_gdf['incident_count'].apply(
        lambda x: x if x >= min_incidents else 0
    )

    # Binary sanctuary classification
    plot_gdf['is_sanctuary'] = plot_gdf['enforcement_classification'] == 'sanctuary'

    # Color scale: white (0) to dark red (max)
    max_incidents = plot_gdf['display_count'].max()
    if max_incidents == 0:
        max_incidents = 1

    # Create white-to-red colormap
    cmap = LinearSegmentedColormap.from_list('white_red', ['#ffffff', '#67000d'])
    norm = Normalize(vmin=0, vmax=max_incidents)

    # Project to ESRI:102003 for continental US
    plot_gdf = plot_gdf.to_crs('ESRI:102003')
    continental = plot_gdf[~plot_gdf['state_po'].isin(['AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP'])].copy()

    # Plot each state
    for idx, row in continental.iterrows():
        incidents = row['display_count']
        color = cmap(norm(incidents))

        continental[continental.index == idx].plot(
            ax=ax, color=[color], edgecolor='black', linewidth=0.5
        )

    # Add labels - S for sanctuary states (always), incident count below (only if >= threshold)
    for idx, row in continental.iterrows():
        centroid = row.geometry.centroid
        is_sanctuary = row.get('is_sanctuary', False)
        incidents = int(row['display_count'])

        # Use white text for dark states (>50% of max)
        text_color = 'white' if incidents > max_incidents * 0.5 else 'black'

        if is_sanctuary:
            # Always show "S" for sanctuary states
            ax.annotate("S", xy=(centroid.x, centroid.y + 40000), ha='center', va='center',
                       fontsize=19, fontweight='bold', color=text_color)
            # Only show count if above threshold
            if incidents > 0:
                ax.annotate(str(incidents), xy=(centroid.x, centroid.y - 40000), ha='center', va='center',
                           fontsize=12, fontweight='bold', color=text_color)
        else:
            # Non-sanctuary: only show count if above threshold
            if incidents > 0:
                ax.annotate(str(incidents), xy=(centroid.x, centroid.y), ha='center', va='center',
                           fontsize=12, fontweight='bold', color=text_color)

    ax.axis('off')

    # Title - calculate displayed stats
    displayed_incidents = int(plot_gdf['display_count'].sum())
    states_displayed = (plot_gdf['display_count'] > 0).sum()
    total_incidents = int(all_incidents['incident_count'].sum()) if not all_incidents.empty else 0

    threshold_note = f'\n(Excluding single-incident states, n<{min_incidents})' if min_incidents > 1 else ''

    ax.set_title(f'{category_name}\nAll Tiers Combined | Jan 2025 - Jan 2026\n'
                f'{displayed_incidents} incidents across {states_displayed} states{threshold_note}\n'
                f'"S" = Sanctuary State',
                fontsize=18, fontweight='bold', pad=20)

    # Colorbar
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes([0.25, 0.08, 0.5, 0.02])
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Number of Incidents', fontsize=12)
    cbar.ax.tick_params(labelsize=10)

    # Legend for sanctuary indicator
    legend_elements = [
        mpatches.Patch(facecolor='#67000d', edgecolor='black', label=f'High incidents ({int(max_incidents)})'),
        mpatches.Patch(facecolor='#ffffff', edgecolor='black', label='Zero incidents'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=11, framealpha=0.95)

    plt.tight_layout(rect=[0, 0.12, 1, 0.95])

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"Saved: {output_path}")
    else:
        plt.show()

    return fig


if __name__ == '__main__':
    print("Generating Tiered ICE Violence Maps...")
    print("=" * 60)

    # =========================================================================
    # CUMULATIVE TIER MAPS (1, 1-2, 1-3, 1-4)
    # =========================================================================
    print("\n--- CUMULATIVE TIER MAPS ---")

    # All incidents ratio by tier (cumulative)
    create_tiered_ratio_maps(output_path=OUTPUT_DIR / 'ice_ratio_by_tier_ALL.png')

    # Category-specific maps
    category_configs = [
        {
            'categories': ['protester'],
            'name': 'Protester',
            'filename': 'ice_ratio_by_tier_PROTESTERS.png'
        },
        {
            'categories': ['journalist'],
            'name': 'Journalist',
            'filename': 'ice_ratio_by_tier_JOURNALISTS.png'
        },
        {
            'categories': ['bystander'],
            'name': 'Bystander',
            'filename': 'ice_ratio_by_tier_BYSTANDERS.png'
        },
        {
            'categories': ['officer'],
            'name': 'Officer/Agent',
            'filename': 'ice_ratio_by_tier_OFFICERS.png'
        },
        {
            'categories': ['us_citizen_collateral'],
            'name': 'US Citizen (Wrongly Targeted)',
            'filename': 'ice_ratio_by_tier_US_CITIZENS.png'
        },
        {
            'categories': ['detainee'],
            'name': 'Detainee (In Custody)',
            'filename': 'ice_ratio_by_tier_DETAINEES.png'
        },
        {
            'categories': ['enforcement_target'],
            'name': 'Enforcement Target',
            'filename': 'ice_ratio_by_tier_ENFORCEMENT_TARGETS.png'
        },
        {
            # Non-immigrant combined: protesters + journalists + bystanders + officers + us_citizen_collateral
            'categories': ['protester', 'journalist', 'bystander', 'officer', 'us_citizen_collateral'],
            'name': 'Non-Immigrant Combined\n(Protesters, Journalists, Bystanders, Officers, US Citizens)',
            'filename': 'ice_ratio_by_tier_NON_IMMIGRANT.png'
        },
    ]

    for config in category_configs:
        print(f"\nGenerating {config['name']} map...")
        create_category_tiered_ratio_map(
            victim_categories=config['categories'],
            category_name=config['name'],
            output_path=OUTPUT_DIR / config['filename']
        )

    # =========================================================================
    # ISOLATED TIER MAPS (1, 2, 3, 4 separately)
    # =========================================================================
    print("\n--- ISOLATED TIER MAPS ---")

    # All incidents - isolated tiers
    create_isolated_tier_ratio_maps(output_path=OUTPUT_DIR / 'ice_ratio_ISOLATED_ALL.png')

    # Category-specific isolated tier maps
    isolated_category_configs = [
        {
            'categories': ['protester'],
            'name': 'Protester',
            'filename': 'ice_ratio_ISOLATED_PROTESTERS.png'
        },
        {
            'categories': ['journalist'],
            'name': 'Journalist',
            'filename': 'ice_ratio_ISOLATED_JOURNALISTS.png'
        },
        {
            'categories': ['bystander'],
            'name': 'Bystander',
            'filename': 'ice_ratio_ISOLATED_BYSTANDERS.png'
        },
        {
            'categories': ['officer'],
            'name': 'Officer/Agent',
            'filename': 'ice_ratio_ISOLATED_OFFICERS.png'
        },
        {
            'categories': ['us_citizen_collateral'],
            'name': 'US Citizen (Wrongly Targeted)',
            'filename': 'ice_ratio_ISOLATED_US_CITIZENS.png'
        },
        {
            'categories': ['detainee'],
            'name': 'Detainee (In Custody)',
            'filename': 'ice_ratio_ISOLATED_DETAINEES.png'
        },
        {
            'categories': ['enforcement_target'],
            'name': 'Enforcement Target',
            'filename': 'ice_ratio_ISOLATED_ENFORCEMENT_TARGETS.png'
        },
        {
            'categories': ['protester', 'journalist', 'bystander', 'officer', 'us_citizen_collateral'],
            'name': 'Non-Immigrant Combined\n(Protesters, Journalists, Bystanders, Officers, US Citizens)',
            'filename': 'ice_ratio_ISOLATED_NON_IMMIGRANT.png'
        },
    ]

    for config in isolated_category_configs:
        print(f"\nGenerating ISOLATED {config['name']} map...")
        create_category_isolated_tier_ratio_map(
            victim_categories=config['categories'],
            category_name=config['name'],
            output_path=OUTPUT_DIR / config['filename']
        )

    print("\n" + "=" * 60)
    print("Done! All maps saved.")
