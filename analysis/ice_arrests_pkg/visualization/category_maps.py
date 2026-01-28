"""
Category-Based Map Visualizations for ice_arrests
==================================================
Functions for creating victim category-specific incident visualizations.

Victim Categories:
- detainee: Person in ICE/CBP custody
- enforcement_target: Person being arrested/targeted
- protester: Person at protest/demonstration
- journalist: Press/media covering events
- bystander: Uninvolved person caught up
- us_citizen_collateral: US citizen wrongly targeted
- officer: ICE/CBP/police officer (for attacks ON agents)
"""

import warnings
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
from .tiered_maps import (
    aggregate_incidents_by_tier_and_category,
    aggregate_incidents_single_tier,
    load_state_geodata,
    load_arrests_data,
)

# Import from parent package
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import STATE_ABBREV, OUTPUT_DIR
from ice_arrests import load_incidents


# =============================================================================
# CATEGORY CONFIGURATIONS
# =============================================================================

VICTIM_CATEGORIES = {
    'protester': 'Protester',
    'journalist': 'Journalist',
    'bystander': 'Bystander',
    'officer': 'Officer/Agent',
    'us_citizen_collateral': 'US Citizen (Wrongly Targeted)',
    'detainee': 'Detainee (In Custody)',
    'enforcement_target': 'Enforcement Target',
}

# Common category groupings
NON_IMMIGRANT_CATEGORIES = [
    'protester', 'journalist', 'bystander', 'officer', 'us_citizen_collateral'
]


# =============================================================================
# CATEGORY-TIERED MAP FUNCTIONS
# =============================================================================

def create_category_tiered_ratio_map(
    victim_categories: List[str],
    category_name: str,
    output_path: Optional[Path] = None
) -> plt.Figure:
    """
    Create 4-panel tiered ratio map for specific victim category.
    Each panel has its own color scale normalized to that tier's data.

    Args:
        victim_categories: List of victim_category values to include
        category_name: Display name for the category
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
        {'max_tier': 1, 'title': 'Tier 1 Only\n(Official Government Data)'},
        {'max_tier': 2, 'title': 'Tiers 1-2\n(+ FOIA / Investigative)'},
        {'max_tier': 3, 'title': 'Tiers 1-3\n(+ Systematic News)'},
        {'max_tier': 4, 'title': 'Tiers 1-4\n(All Data)'},
    ]

    for i, config in enumerate(tier_configs):
        ax = axes[i]

        tier_incidents = aggregate_incidents_by_tier_and_category(
            max_tier=config['max_tier'],
            victim_categories=victim_categories
        )

        plot_gdf = states_gdf.copy()
        plot_gdf = plot_gdf.merge(
            arrests_df[['state_po', 'arrests']],
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
        f'{category_name} Incidents by Data Tier\n(Per 1,000 ICE Arrests)',
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


def create_category_isolated_tier_ratio_map(
    victim_categories: List[str],
    category_name: str,
    output_path: Optional[Path] = None
) -> plt.Figure:
    """
    Create 4-panel map for specific victim category with each tier IN ISOLATION.

    Args:
        victim_categories: List of victim_category values to include
        category_name: Display name for the category
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
        {'tier': 1, 'title': 'Tier 1 Only\n(Official Government Data)'},
        {'tier': 2, 'title': 'Tier 2 Only\n(FOIA / Investigative)'},
        {'tier': "3-4", 'title': 'Tiers 3-4 Combined\n(News Media)'},
        {'tier': "all", 'title': 'All Tiers Combined\n(Complete Dataset)'},
    ]

    for i, config in enumerate(tier_configs):
        ax = axes[i]

        tier_incidents = aggregate_incidents_single_tier(
            tier=config['tier'],
            victim_categories=victim_categories
        )

        plot_gdf = states_gdf.copy()
        plot_gdf = plot_gdf.merge(
            arrests_df[['state_po', 'arrests']],
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
        f'{category_name} Incidents by ISOLATED Tier\n(Per 1,000 Arrests)',
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


def create_single_panel_incident_map(
    victim_categories: List[str],
    category_name: str,
    output_path: Optional[Path] = None,
    min_incidents: int = 1
) -> plt.Figure:
    """
    Create a single-panel map showing raw incident counts (not ratio).
    White = 0, Dark red = maximum.

    Args:
        victim_categories: List of victim_category values to include
        category_name: Display name for the category
        output_path: Optional path to save the figure
        min_incidents: Minimum incidents to display (default 1)

    Returns:
        matplotlib Figure object
    """
    set_style()
    warnings.filterwarnings('ignore')

    fig, ax = plt.subplots(figsize=(16, 12))

    states_gdf = load_state_geodata()
    arrests_df = load_arrests_data()

    all_incidents = aggregate_incidents_single_tier(tier="all", victim_categories=victim_categories)

    plot_gdf = states_gdf.copy()
    plot_gdf = plot_gdf.merge(
        arrests_df[['state_po', 'arrests', 'enforcement_classification']],
        on='state_po', how='left'
    )

    if not all_incidents.empty:
        plot_gdf = plot_gdf.merge(
            all_incidents[['state_po', 'incident_count']],
            on='state_po', how='left'
        )
    else:
        plot_gdf['incident_count'] = 0

    plot_gdf['incident_count'] = plot_gdf['incident_count'].fillna(0)

    plot_gdf['display_count'] = plot_gdf['incident_count'].apply(
        lambda x: x if x >= min_incidents else 0
    )

    plot_gdf['is_sanctuary'] = plot_gdf['enforcement_classification'] == 'sanctuary'

    max_incidents = plot_gdf['display_count'].max()
    if max_incidents == 0:
        max_incidents = 1

    cmap = LinearSegmentedColormap.from_list('white_red', ['#ffffff', '#67000d'])
    norm = Normalize(vmin=0, vmax=max_incidents)

    plot_gdf = plot_gdf.to_crs('ESRI:102003')
    continental = plot_gdf[~plot_gdf['state_po'].isin(['AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP'])].copy()

    for idx, row in continental.iterrows():
        incidents = row['display_count']
        color = cmap(norm(incidents))

        continental[continental.index == idx].plot(
            ax=ax, color=[color], edgecolor='black', linewidth=0.5
        )

    for idx, row in continental.iterrows():
        centroid = row.geometry.centroid
        is_sanctuary = row.get('is_sanctuary', False)
        incidents = int(row['display_count'])

        text_color = 'white' if incidents > max_incidents * 0.5 else 'black'

        if is_sanctuary:
            ax.annotate("S", xy=(centroid.x, centroid.y + 40000), ha='center', va='center',
                       fontsize=19, fontweight='bold', color=text_color)
            if incidents > 0:
                ax.annotate(str(incidents), xy=(centroid.x, centroid.y - 40000), ha='center', va='center',
                           fontsize=12, fontweight='bold', color=text_color)
        else:
            if incidents > 0:
                ax.annotate(str(incidents), xy=(centroid.x, centroid.y), ha='center', va='center',
                           fontsize=12, fontweight='bold', color=text_color)

    ax.axis('off')

    displayed_incidents = int(plot_gdf['display_count'].sum())
    states_displayed = (plot_gdf['display_count'] > 0).sum()
    total_incidents = int(all_incidents['incident_count'].sum()) if not all_incidents.empty else 0

    threshold_note = f'\n(Excluding single-incident states, n<{min_incidents})' if min_incidents > 1 else ''

    ax.set_title(f'{category_name}\nAll Tiers Combined | Jan 2025 - Jan 2026\n'
                f'{displayed_incidents} incidents across {states_displayed} states{threshold_note}\n'
                f'"S" = Sanctuary State',
                fontsize=18, fontweight='bold', pad=20)

    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes([0.25, 0.08, 0.5, 0.02])
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Number of Incidents', fontsize=12)
    cbar.ax.tick_params(labelsize=10)

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


# =============================================================================
# BATCH GENERATION FUNCTIONS
# =============================================================================

def generate_all_category_maps(output_dir: Optional[Path] = None):
    """
    Generate all category-specific tiered and isolated maps.

    Args:
        output_dir: Directory to save maps (defaults to OUTPUT_DIR)
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR

    output_dir.mkdir(parents=True, exist_ok=True)

    category_configs = [
        {'categories': ['protester'], 'name': 'Protester'},
        {'categories': ['journalist'], 'name': 'Journalist'},
        {'categories': ['bystander'], 'name': 'Bystander'},
        {'categories': ['officer'], 'name': 'Officer/Agent'},
        {'categories': ['us_citizen_collateral'], 'name': 'US Citizen (Wrongly Targeted)'},
        {'categories': ['detainee'], 'name': 'Detainee (In Custody)'},
        {'categories': ['enforcement_target'], 'name': 'Enforcement Target'},
        {'categories': NON_IMMIGRANT_CATEGORIES,
         'name': 'Non-Immigrant Combined\n(Protesters, Journalists, Bystanders, Officers, US Citizens)'},
    ]

    print("=" * 60)
    print("Generating Category-Specific Maps")
    print("=" * 60)

    for config in category_configs:
        print(f"\nGenerating {config['name']} maps...")

        # Safe filename
        filename_base = config['name'].split('\n')[0].replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_')

        # Tiered (cumulative)
        create_category_tiered_ratio_map(
            victim_categories=config['categories'],
            category_name=config['name'],
            output_path=output_dir / f'ice_ratio_by_tier_{filename_base.upper()}.png'
        )

        # Isolated
        create_category_isolated_tier_ratio_map(
            victim_categories=config['categories'],
            category_name=config['name'],
            output_path=output_dir / f'ice_ratio_ISOLATED_{filename_base.upper()}.png'
        )

    print("\n" + "=" * 60)
    print("Done! All category maps generated.")
    print("=" * 60)
