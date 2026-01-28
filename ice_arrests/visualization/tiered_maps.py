"""
Tiered Map Visualizations for ice_arrests
==========================================
Functions for creating tier-based incident visualizations.

Tiers:
- Tier 1: Official government data (deaths in custody)
- Tier 2: FOIA/investigative journalism (shootings, force, wrongful detentions)
- Tier 3: Systematic news search (raids, protests)
- Tier 4: Ad-hoc news (may have selection bias)
"""

import warnings
from typing import Optional, List, Dict, Any
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable

try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

from .styles import (
    set_style,
    BLUE_LOW, WHITE_MID, RED_HIGH,
    NO_INCIDENTS_COLOR, NO_DATA_COLOR,
)

# Import from parent package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import GEOJSON_PATH, STATE_ABBREV, OUTPUT_DIR
from ice_arrests import load_incidents


# =============================================================================
# DATA AGGREGATION FUNCTIONS
# =============================================================================

def aggregate_incidents_by_tier(max_tier: int = 4, incidents: Optional[List[Dict]] = None) -> pd.DataFrame:
    """
    Aggregate incidents by state up to specified tier (cumulative).

    Args:
        max_tier: Include tiers 1 through max_tier (1, 2, 3, or 4)
        incidents: Optional pre-loaded incidents. If None, loads from package.

    Returns:
        DataFrame with state, state_po, incident_count, deaths, injuries
    """
    if incidents is None:
        tiers_to_load = list(range(1, max_tier + 1))
        incidents = load_incidents(tiers=tiers_to_load)

    # Filter to max tier
    all_incidents = [i for i in incidents if i.get('source_tier', 4) <= max_tier]

    # Aggregate by state
    state_data = {}
    for incident in all_incidents:
        state = incident.get('state', 'Unknown')
        if state == 'Unknown' or not state:
            continue

        if state not in state_data:
            state_data[state] = {'incident_count': 0, 'deaths': 0, 'injuries': 0}

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

    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=['state', 'state_po', 'incident_count', 'deaths', 'injuries']
    )


def aggregate_incidents_single_tier(
    tier: int,
    incidents: Optional[List[Dict]] = None,
    victim_categories: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Aggregate incidents by state for a SINGLE tier only (not cumulative).

    Args:
        tier: Which tier to include (1, 2, 3, 4)
        incidents: Optional pre-loaded incidents
        victim_categories: Optional filter by victim category

    Returns:
        DataFrame with state, state_po, incident_count, deaths, injuries
    """
    if incidents is None:
        if tier == "3-4":
            incidents = load_incidents(tiers=[3, 4])
        elif tier == "all":
            incidents = load_incidents()
        else:
            incidents = load_incidents(tiers=[tier])

    # Filter by tier
    if tier == "3-4":
        filtered = [i for i in incidents if i.get('source_tier') in (3, 4)]
    elif tier == "all":
        filtered = incidents
    else:
        filtered = [i for i in incidents if i.get('source_tier') == tier]

    # Filter by victim category if specified
    if victim_categories:
        filtered = [i for i in filtered if i.get('victim_category') in victim_categories]

    # Aggregate by state
    state_data = {}
    for incident in filtered:
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

    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=['state', 'state_po', 'incident_count', 'deaths', 'injuries']
    )


def aggregate_incidents_by_tier_and_category(
    max_tier: int = 4,
    victim_categories: Optional[List[str]] = None,
    incidents: Optional[List[Dict]] = None
) -> pd.DataFrame:
    """
    Aggregate incidents by state up to specified tier, filtered by victim category.

    Args:
        max_tier: Include tiers 1 through max_tier
        victim_categories: List of victim_category values to include, or None for all
        incidents: Optional pre-loaded incidents

    Returns:
        DataFrame with state, state_po, incident_count, deaths, injuries
    """
    if incidents is None:
        tiers_to_load = list(range(1, max_tier + 1))
        incidents = load_incidents(tiers=tiers_to_load)

    # Filter to max tier
    filtered = [i for i in incidents if i.get('source_tier', 4) <= max_tier]

    # Filter by victim category if specified
    if victim_categories:
        filtered = [i for i in filtered if i.get('victim_category') in victim_categories]

    # Aggregate by state
    state_data = {}
    for incident in filtered:
        state = incident.get('state', 'Unknown')
        if state == 'Unknown' or not state:
            continue

        if state not in state_data:
            state_data[state] = {'incident_count': 0, 'deaths': 0, 'injuries': 0}

        state_data[state]['incident_count'] += 1

        outcome = str(incident.get('outcome', '')).lower()
        incident_type = incident.get('incident_type', '')
        if incident_type == 'death_in_custody' or 'death' in outcome or 'fatal' in outcome:
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

    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=['state', 'state_po', 'incident_count', 'deaths', 'injuries']
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_state_geodata() -> 'gpd.GeoDataFrame':
    """Load state boundaries from GeoJSON."""
    if not HAS_GEOPANDAS:
        raise ImportError("geopandas is required for map generation")

    gdf = gpd.read_file(GEOJSON_PATH)
    if 'STUSPS' in gdf.columns:
        gdf = gdf.rename(columns={'STUSPS': 'state_po'})
    if 'STATEFP' in gdf.columns:
        gdf = gdf[gdf['STATEFP'].astype(int) <= 56]
    return gdf


def load_arrests_data() -> pd.DataFrame:
    """Load arrest data by state."""
    try:
        csv_path = OUTPUT_DIR.parent / 'FINAL_MERGED_DATASET.csv'
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            df['state_po'] = df['state'].map(STATE_ABBREV)
            return df[['state', 'state_po', 'arrests', 'enforcement_classification']].copy()
    except Exception:
        pass

    # Fallback: return empty with all states
    return pd.DataFrame({
        'state': list(STATE_ABBREV.keys()),
        'state_po': list(STATE_ABBREV.values()),
        'arrests': [0] * len(STATE_ABBREV),
        'enforcement_classification': ['unknown'] * len(STATE_ABBREV)
    })


# =============================================================================
# MAP CREATION FUNCTIONS
# =============================================================================

def create_tiered_ratio_maps(output_path: Optional[Path] = None) -> plt.Figure:
    """
    Create 4-panel map showing violence RATIO (per 1000 arrests) by tier.
    Each panel has its own color scale normalized to that tier's data.

    Args:
        output_path: Optional path to save the figure

    Returns:
        matplotlib Figure object
    """
    set_style()
    warnings.filterwarnings('ignore')

    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.flatten()

    states_gdf = load_state_geodata()
    arrests_df = load_arrests_data()

    cmap = LinearSegmentedColormap.from_list('violence_ratio', [BLUE_LOW, WHITE_MID, RED_HIGH])

    tier_configs = [
        {'max_tier': 1, 'title': 'Tier 1 Only\n(Official Deaths in Custody)'},
        {'max_tier': 2, 'title': 'Tiers 1-2\n(+ Shootings, Force, Wrongful Detentions)'},
        {'max_tier': 3, 'title': 'Tiers 1-3\n(+ Systematic News: Raids, Protests)'},
        {'max_tier': 4, 'title': 'Tiers 1-4\n(All Available Data)'},
    ]

    for i, config in enumerate(tier_configs):
        ax = axes[i]

        tier_incidents = aggregate_incidents_by_tier(max_tier=config['max_tier'])

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

        for idx, row in continental.iterrows():
            centroid = row.geometry.centroid
            is_sanctuary = row.get('enforcement_classification') == 'sanctuary'

            if row['has_incidents'] and is_sanctuary:
                label = "S"
                ax.annotate(label, xy=(centroid.x, centroid.y), ha='center', va='center',
                           fontsize=9, fontweight='bold', color='black')

        ax.axis('off')
        ax.set_title(f"{config['title']}\n(Scale: {panel_min:.2f} - {panel_max:.2f})",
                    fontsize=11, fontweight='bold', pad=10)

        total_incidents = tier_incidents['incident_count'].sum() if not tier_incidents.empty else 0
        states_with = (tier_incidents['incident_count'] > 0).sum() if not tier_incidents.empty else 0
        stats_text = f"{int(total_incidents)} incidents across {states_with} states"
        ax.text(0.5, -0.02, stats_text, transform=ax.transAxes, ha='center', fontsize=9, style='italic')

        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar_positions = [
            [0.08, 0.48, 0.38, 0.012],
            [0.54, 0.48, 0.38, 0.012],
            [0.08, 0.02, 0.38, 0.012],
            [0.54, 0.02, 0.38, 0.012]
        ]
        cbar_ax = fig.add_axes(cbar_positions[i])
        cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
        cbar.set_ticks([panel_min, (panel_min + panel_max) / 2, panel_max])
        cbar.set_ticklabels([f'{panel_min:.2f}', f'{(panel_min + panel_max) / 2:.2f}', f'{panel_max:.2f}'])
        cbar.ax.tick_params(labelsize=7)

    fig.suptitle(
        'ICE Violence Ratio by Data Source Tier\n("S" = Sanctuary State - Per 1,000 Arrests)',
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


def create_isolated_tier_ratio_maps(output_path: Optional[Path] = None) -> plt.Figure:
    """
    Create 4-panel map showing violence RATIO for each tier IN ISOLATION.
    Tier 1 only, Tier 2 only, Tiers 3-4, All combined.

    Args:
        output_path: Optional path to save the figure

    Returns:
        matplotlib Figure object
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

        for idx, row in continental.iterrows():
            centroid = row.geometry.centroid
            is_sanctuary = row.get('enforcement_classification') == 'sanctuary'

            if row['has_incidents'] and is_sanctuary:
                ax.annotate("S", xy=(centroid.x, centroid.y), ha='center', va='center',
                           fontsize=9, fontweight='bold', color='black')

        ax.axis('off')
        ax.set_title(f"{config['title']}\n(Scale: {panel_min:.2f} - {panel_max:.2f})",
                    fontsize=10, fontweight='bold', pad=10)

        total_incidents = tier_incidents['incident_count'].sum() if not tier_incidents.empty else 0
        states_with = (tier_incidents['incident_count'] > 0).sum() if not tier_incidents.empty else 0
        stats_text = f"{int(total_incidents)} incidents across {states_with} states"
        ax.text(0.5, -0.02, stats_text, transform=ax.transAxes, ha='center', fontsize=9, style='italic')

        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar_positions = [
            [0.08, 0.48, 0.38, 0.012],
            [0.54, 0.48, 0.38, 0.012],
            [0.08, 0.02, 0.38, 0.012],
            [0.54, 0.02, 0.38, 0.012]
        ]
        cbar_ax = fig.add_axes(cbar_positions[i])
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
