"""
Map Generation for ice_arrests
==============================
Choropleth map generation for ICE enforcement data.
"""

import warnings
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

try:
    import geopandas as gpd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

from .styles import (
    set_style,
    get_colormap,
    BLUE_LOW, WHITE_MID, RED_HIGH,
    NO_INCIDENTS_COLOR, NO_DATA_COLOR,
    STATUS_LABELS, STATUS_COLORS,
    CLASSIFICATION_COLORS, SMALL_STATES,
)

# Import from config
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import GEOJSON_PATH, STATE_ABBREV, OUTPUT_DIR


# =============================================================================
# DATA LOADING HELPERS
# =============================================================================

def load_state_geodata() -> 'gpd.GeoDataFrame':
    """Load state boundaries from local GeoJSON file."""
    if not HAS_GEOPANDAS:
        raise ImportError("geopandas is required for map generation")

    gdf = gpd.read_file(GEOJSON_PATH)
    if 'STUSPS' in gdf.columns:
        gdf = gdf.rename(columns={'STUSPS': 'state_po'})
    if 'STATEFP' in gdf.columns:
        gdf = gdf[gdf['STATEFP'].astype(int) <= 56]
    return gdf


def load_violence_data() -> pd.DataFrame:
    """Load the merged violence/arrest/classification data."""
    from ..analysis.merge import create_merged_dataset
    return create_merged_dataset()


# =============================================================================
# PLOTTING HELPER FUNCTIONS
# =============================================================================

def plot_states(ax, gdf: 'gpd.GeoDataFrame', cmap, norm,
                no_incidents_color: str, no_data_color: str):
    """
    Plot all states with appropriate colors.

    Args:
        ax: Matplotlib axes
        gdf: GeoDataFrame with state data
        cmap: Colormap for violence ratios
        norm: Normalizer for the colormap
        no_incidents_color: Color for states with no incidents
        no_data_color: Color for states with no data
    """
    for idx, row in gdf.iterrows():
        # Determine color
        if not row.get('has_data', True):
            color = no_data_color
        elif not row.get('has_incidents', True):
            color = no_incidents_color
        else:
            ratio = row.get('violence_per_1000_arrests', 0)
            color = cmap(norm(min(ratio, norm.vmax)))

        # Plot the state
        gdf[gdf.index == idx].plot(
            ax=ax,
            color=[color],
            edgecolor='black',
            linewidth=0.8
        )

        # Add hatching for no-data states
        if not row.get('has_data', True):
            gdf[gdf.index == idx].plot(
                ax=ax,
                facecolor='none',
                edgecolor='gray',
                linewidth=0.5,
                hatch='///'
            )


def add_state_labels(ax, gdf: 'gpd.GeoDataFrame', label_type: str = 'status'):
    """
    Add labels to states.

    Args:
        ax: Matplotlib axes
        gdf: GeoDataFrame with state data
        label_type: Type of label - 'status' for S/A/X/N, 'ratio' for values, 'abbrev' for state codes
    """
    for idx, row in gdf.iterrows():
        centroid = row.geometry.centroid

        if label_type == 'status':
            status = row.get('enforcement_classification', 'unknown')
            label = STATUS_LABELS.get(status, '?')
            fontsize = 7 if row.get('state_po', '') in SMALL_STATES else 8
            ax.annotate(
                label,
                xy=(centroid.x, centroid.y),
                ha='center', va='center',
                fontsize=fontsize,
                fontweight='bold',
                color='black',
                bbox=dict(boxstyle='circle,pad=0.2', facecolor='white',
                         edgecolor='gray', alpha=0.8)
            )

        elif label_type == 'ratio':
            if not row.get('has_data', True):
                label = "?"
            elif not row.get('has_incidents', True):
                label = "0"
            else:
                label = f"{row.get('violence_per_1000_arrests', 0):.1f}"
            fontsize = 6 if row.get('state_po', '') in SMALL_STATES else 7
            ax.annotate(label, xy=(centroid.x, centroid.y),
                       ha='center', va='center',
                       fontsize=fontsize, fontweight='bold', color='black')

        elif label_type == 'abbrev':
            fontsize = 6 if row.get('state_po', '') in SMALL_STATES else 7
            ax.annotate(
                row.get('state_po', ''),
                xy=(centroid.x, centroid.y),
                ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color='white',
                path_effects=[pe.withStroke(linewidth=2, foreground='black')]
            )


def add_alaska_hawaii(ax, alaska_gdf, hawaii_gdf, cmap, norm):
    """
    Add Alaska and Hawaii insets to the map.

    Args:
        ax: Matplotlib axes
        alaska_gdf: GeoDataFrame for Alaska
        hawaii_gdf: GeoDataFrame for Hawaii
        cmap: Colormap
        norm: Normalizer
    """
    # Plot Alaska (scaled and moved)
    if alaska_gdf is not None and not alaska_gdf.empty:
        alaska_scaled = alaska_gdf.copy()
        alaska_scaled.geometry = alaska_scaled.geometry.scale(0.35, 0.35, origin=(0, 0))
        alaska_scaled.geometry = alaska_scaled.geometry.translate(-1800000, -1400000)

        ak_row = alaska_gdf.iloc[0]
        if not ak_row.get('has_data', True):
            alaska_scaled.plot(ax=ax, color=[NO_DATA_COLOR],
                             edgecolor='black', linewidth=0.8, hatch='///')
        elif not ak_row.get('has_incidents', True):
            alaska_scaled.plot(ax=ax, color=[NO_INCIDENTS_COLOR],
                             edgecolor='black', linewidth=0.8)
        else:
            color = cmap(norm(min(ak_row.get('violence_per_1000_arrests', 0), norm.vmax)))
            alaska_scaled.plot(ax=ax, color=[color], edgecolor='black', linewidth=0.8)

    # Plot Hawaii (scaled and moved)
    if hawaii_gdf is not None and not hawaii_gdf.empty:
        hawaii_scaled = hawaii_gdf.copy()
        hawaii_scaled.geometry = hawaii_scaled.geometry.scale(1.0, 1.0, origin=(0, 0))
        hawaii_scaled.geometry = hawaii_scaled.geometry.translate(5200000, -1200000)

        hi_row = hawaii_gdf.iloc[0]
        if not hi_row.get('has_data', True):
            hawaii_scaled.plot(ax=ax, color=[NO_DATA_COLOR],
                             edgecolor='black', linewidth=0.8, hatch='///')
        elif not hi_row.get('has_incidents', True):
            hawaii_scaled.plot(ax=ax, color=[NO_INCIDENTS_COLOR],
                             edgecolor='black', linewidth=0.8)
        else:
            color = cmap(norm(min(hi_row.get('violence_per_1000_arrests', 0), norm.vmax)))
            hawaii_scaled.plot(ax=ax, color=[color], edgecolor='black', linewidth=0.8)


def add_legend(ax, include_data_status: bool = True):
    """
    Add legend to the map.

    Args:
        ax: Matplotlib axes
        include_data_status: Whether to include data status indicators
    """
    legend_elements = [
        mpatches.Patch(facecolor=STATUS_COLORS['sanctuary'], edgecolor='black',
                      label='S = Sanctuary (limits ICE cooperation)'),
        mpatches.Patch(facecolor=STATUS_COLORS['aggressive_anti_sanctuary'], edgecolor='black',
                      label='X = Aggressive Anti-Sanctuary (mandates cooperation)'),
        mpatches.Patch(facecolor=STATUS_COLORS['anti_sanctuary'], edgecolor='black',
                      label='A = Anti-Sanctuary (some mandatory cooperation)'),
        mpatches.Patch(facecolor=STATUS_COLORS['neutral'], edgecolor='black',
                      label='N = Neutral (no statewide policy)'),
    ]

    if include_data_status:
        legend_elements.extend([
            mpatches.Patch(facecolor=NO_INCIDENTS_COLOR, edgecolor='black',
                          label='Gray = Has arrests data, zero documented incidents'),
            mpatches.Patch(facecolor=NO_DATA_COLOR, edgecolor='black', hatch='///',
                          label='Hatched = No data collected'),
        ])

    ax.legend(handles=legend_elements, loc='lower left', fontsize=8, framealpha=0.95,
             title='State Classification & Data Status', title_fontsize=10)


def add_colorbar(ax, fig, cmap, norm, label: str):
    """
    Add colorbar to the figure.

    Args:
        ax: Matplotlib axes
        fig: Matplotlib figure
        cmap: Colormap
        norm: Normalizer
        label: Label for the colorbar
    """
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, orientation='horizontal',
                       fraction=0.03, pad=0.02, aspect=40)
    cbar.set_label(label, fontsize=11)


# =============================================================================
# MAIN MAP GENERATION FUNCTIONS
# =============================================================================

def create_violence_ratio_map(output_path: Optional[Path] = None):
    """
    Create map of ICE violence/arrest ratios by state.

    Color: Blue (low) -> White (mid) -> Red (high) gradient
    Labels: S=Sanctuary, A=Anti-Sanctuary, X=Aggressive Anti-Sanctuary, N=Neutral

    Args:
        output_path: Optional path to save the figure.

    Returns:
        Matplotlib figure object.
    """
    set_style()
    warnings.filterwarnings('ignore')

    fig, ax = plt.subplots(1, 1, figsize=(16, 10))

    try:
        # Load data
        states_gdf = load_state_geodata()
        violence_df = load_violence_data()

        # Convert state names to abbreviations
        violence_df['state_po'] = violence_df['state'].map(STATE_ABBREV)

        # Merge with geometry
        states_gdf = states_gdf.merge(
            violence_df[['state_po', 'violence_per_1000_arrests', 'enforcement_classification',
                        'total_violent_incidents', 'arrests', 'deaths']],
            on='state_po',
            how='left'
        )

        # Categorize states by data availability
        states_gdf['has_data'] = (
            (states_gdf['arrests'].fillna(0) > 0) |
            (states_gdf['total_violent_incidents'].fillna(0) > 0)
        )
        states_gdf['has_incidents'] = states_gdf['total_violent_incidents'].fillna(0) > 0
        states_gdf['violence_per_1000_arrests'] = states_gdf['violence_per_1000_arrests'].fillna(0)
        states_gdf['enforcement_classification'] = states_gdf['enforcement_classification'].fillna('unknown')

        # Project to Albers for continental US
        states_gdf = states_gdf.to_crs('ESRI:102003')

        # Separate regions
        continental = states_gdf[~states_gdf['state_po'].isin(['AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP'])].copy()
        alaska = states_gdf[states_gdf['state_po'] == 'AK'].copy()
        hawaii = states_gdf[states_gdf['state_po'] == 'HI'].copy()

        # Create colormap and normalizer
        cmap = get_colormap()
        max_ratio = min(violence_df['violence_per_1000_arrests'].max(), 5.0)
        norm = Normalize(vmin=0, vmax=max_ratio)

        # Plot states
        plot_states(ax, continental, cmap, norm, NO_INCIDENTS_COLOR, NO_DATA_COLOR)

        # Add Alaska and Hawaii
        add_alaska_hawaii(ax, alaska, hawaii, cmap, norm)

        # Add labels
        add_state_labels(ax, continental, label_type='status')

        ax.axis('off')

        # Add colorbar and legend
        add_colorbar(ax, fig, cmap, norm, 'Violent Incidents per 1,000 ICE Arrests')
        add_legend(ax, include_data_status=True)

        # Title
        ax.set_title(
            'ICE Violent Incidents per 1,000 Arrests by State\n'
            'Blue = Low Ratio | Red = High Ratio | Gray = Zero Incidents | Hatched = No Data',
            fontsize=16, fontweight='bold', pad=20
        )

        # Source note
        fig.text(0.5, 0.02,
                'Sources: Deportation Data Project (arrests); NBC News, The Trace, ProPublica (incidents); '
                'DOJ/ILRC (sanctuary classifications) | Period: Jan 20 - Oct 30, 2025',
                ha='center', fontsize=8, style='italic', color='gray')

    except Exception as e:
        ax.text(0.5, 0.5, f'Error: {str(e)[:200]}',
               ha='center', va='center', transform=ax.transAxes, fontsize=10)
        import traceback
        traceback.print_exc()

    plt.tight_layout(rect=[0, 0.04, 1, 1])

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"Saved: {output_path}")
    else:
        plt.show()

    return fig


def create_dual_panel_map(output_path: Optional[Path] = None):
    """
    Create two-panel map:
    - Panel A: Violence ratio (gradient) with data availability indicators
    - Panel B: Sanctuary classification (categorical)

    Args:
        output_path: Optional path to save the figure.

    Returns:
        Matplotlib figure object.
    """
    set_style()
    warnings.filterwarnings('ignore')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

    try:
        # Load data
        states_gdf = load_state_geodata()
        violence_df = load_violence_data()

        # Convert state names to abbreviations
        violence_df['state_po'] = violence_df['state'].map(STATE_ABBREV)

        # Merge with geometry
        states_gdf = states_gdf.merge(
            violence_df[['state_po', 'violence_per_1000_arrests', 'enforcement_classification',
                        'total_violent_incidents', 'arrests']],
            on='state_po',
            how='left'
        )

        # Categorize states
        states_gdf['has_data'] = (
            (states_gdf['arrests'].fillna(0) > 0) |
            (states_gdf['total_violent_incidents'].fillna(0) > 0)
        )
        states_gdf['has_incidents'] = states_gdf['total_violent_incidents'].fillna(0) > 0
        states_gdf['violence_per_1000_arrests'] = states_gdf['violence_per_1000_arrests'].fillna(0)
        states_gdf['enforcement_classification'] = states_gdf['enforcement_classification'].fillna('unknown')

        # Project
        states_gdf = states_gdf.to_crs('ESRI:102003')
        continental = states_gdf[~states_gdf['state_po'].isin(['AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP'])].copy()

        # === PANEL A: Violence Ratio ===
        cmap = get_colormap()
        max_ratio = min(violence_df['violence_per_1000_arrests'].max(), 5.0)
        norm = Normalize(vmin=0, vmax=max_ratio)

        plot_states(ax1, continental, cmap, norm, NO_INCIDENTS_COLOR, NO_DATA_COLOR)
        add_state_labels(ax1, continental, label_type='ratio')

        ax1.axis('off')
        ax1.set_title('A. Violence Ratio\n(Incidents per 1,000 Arrests)', fontsize=14, fontweight='bold')

        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax1, orientation='horizontal', fraction=0.03, pad=0.02, aspect=30)
        cbar.set_label('Incidents per 1,000 Arrests (0 = zero documented; ? = no data)', fontsize=9)

        # === PANEL B: Sanctuary Classification ===
        continental['class_color'] = continental['enforcement_classification'].map(CLASSIFICATION_COLORS)
        continental['class_color'] = continental['class_color'].fillna('#cccccc')

        for idx, row in continental.iterrows():
            continental[continental.index == idx].plot(
                ax=ax2, color=[row['class_color']], edgecolor='black', linewidth=0.8
            )

        add_state_labels(ax2, continental, label_type='abbrev')

        ax2.axis('off')
        ax2.set_title('B. Sanctuary Classification\n(State Immigration Enforcement Policy)',
                     fontsize=14, fontweight='bold')

        # Legend for Panel B
        legend_elements = [
            mpatches.Patch(facecolor=CLASSIFICATION_COLORS['sanctuary'], edgecolor='black',
                          label='Sanctuary (limits cooperation)'),
            mpatches.Patch(facecolor=CLASSIFICATION_COLORS['aggressive_anti_sanctuary'], edgecolor='black',
                          label='Aggressive Anti-Sanctuary'),
            mpatches.Patch(facecolor=CLASSIFICATION_COLORS['anti_sanctuary'], edgecolor='black',
                          label='Anti-Sanctuary'),
            mpatches.Patch(facecolor=CLASSIFICATION_COLORS['neutral'], edgecolor='black',
                          label='Neutral'),
        ]
        ax2.legend(handles=legend_elements, loc='lower left', fontsize=9, framealpha=0.95)

        # Main title
        fig.suptitle(
            'ICE Enforcement Violence by State: Ratio and Sanctuary Status',
            fontsize=18, fontweight='bold', y=0.98
        )

        # Source note
        fig.text(0.5, 0.02,
                'Sources: Deportation Data Project (arrests); NBC News, The Trace, ProPublica (incidents); '
                'DOJ/ILRC (classifications) | Period: Jan 20 - Oct 30, 2025',
                ha='center', fontsize=8, style='italic', color='gray')

    except Exception as e:
        ax1.text(0.5, 0.5, f'Error: {str(e)[:200]}', ha='center', va='center', transform=ax1.transAxes)
        import traceback
        traceback.print_exc()

    plt.tight_layout(rect=[0, 0.04, 1, 0.96])

    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        print(f"Saved: {output_path}")
    else:
        plt.show()

    return fig
