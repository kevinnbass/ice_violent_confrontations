"""
ICE Violence/Arrest Ratio Map by State
======================================
Creates a choropleth map of US states colored by violence-to-arrest ratio,
with state labels indicating sanctuary status.

Style matches: voter id and welfare/standalone_high_contrast_maps project

Color scheme:
- Blue (low ratio) -> Red (high ratio) gradient for violence ratio
- State labels: S=Sanctuary, A=Anti-Sanctuary, X=Aggressive Anti-Sanctuary, N=Neutral
- Gray: States with arrests data but no documented incidents (ratio = 0)
- Hatched: States with no data collected at all

NOTE: This file now uses the ice_arrests package and centralized config.
      Core visualization functions are in ice_arrests/visualization/maps.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable
import matplotlib.patheffects as pe
from matplotlib.patches import Patch
from pathlib import Path
import warnings

# Import from centralized config
from config import (
    GEOJSON_PATH,
    OUTPUT_DIR,
    COLORS,
    STATE_ABBREV,
    STATE_CENTROIDS,
    STATUS_LABELS,
    STATUS_COLORS,
)

SCRIPT_DIR = Path(__file__).parent

# Extract colors from config for backward compatibility
BLUE_LOW = COLORS['blue_low']
RED_HIGH = COLORS['red_high']
WHITE_MID = COLORS['white_mid']

# Try to import from ice_arrests package
try:
    from ice_arrests.visualization.maps import (
        create_violence_ratio_map as _create_ratio_map,
        create_dual_panel_map as _create_dual_map,
    )
    from ice_arrests.visualization.styles import set_style as _set_style
    _NEW_PACKAGE_AVAILABLE = True
except ImportError:
    _NEW_PACKAGE_AVAILABLE = False


def set_style():
    """Set consistent style matching main branch."""
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 11,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'axes.edgecolor': '#333333',
        'grid.color': '#e0e0e0',
    })


def load_state_geodata():
    """Load state boundaries from local GeoJSON file."""
    gdf = gpd.read_file(GEOJSON_PATH)
    # Standardize to state_po column
    if 'STUSPS' in gdf.columns:
        gdf = gdf.rename(columns={'STUSPS': 'state_po'})
    if 'STATEFP' in gdf.columns:
        gdf = gdf[gdf['STATEFP'].astype(int) <= 56]
    return gdf


def load_violence_data():
    """Load the merged violence/arrest/classification data."""
    # Try to load from CSV first
    csv_path = SCRIPT_DIR / 'FINAL_MERGED_DATASET.csv'
    if csv_path.exists():
        return pd.read_csv(csv_path)

    # Otherwise, import and generate
    from FINAL_MERGED_DATABASE import create_final_dataset
    return create_final_dataset()


# STATE_ABBREV and STATE_CENTROIDS are now imported from config


def create_violence_ratio_map(output_path=None):
    """
    Create map of ICE violence/arrest ratios by state.

    Color: Blue (low) → White (mid) → Red (high) gradient
    Labels: S=Sanctuary, A=Anti-Sanctuary, X=Aggressive Anti-Sanctuary, N=Neutral

    Data categories:
    - States with incidents: Colored by violence ratio (gradient)
    - States with arrests but no incidents: Light gray (documented zero)
    - States with no data: Hatched pattern (no information collected)
    """
    set_style()
    warnings.filterwarnings('ignore')

    fig, ax = plt.subplots(1, 1, figsize=(16, 10))

    # Colors for special categories
    NO_INCIDENTS_COLOR = '#d0d0d0'  # Light gray for zero incidents with data
    NO_DATA_COLOR = '#f0f0f0'       # Very light gray for no data collected

    try:
        # Load data
        states_gdf = load_state_geodata()
        violence_df = load_violence_data()

        # Convert state names to abbreviations in violence data
        violence_df['state_po'] = violence_df['state'].map(STATE_ABBREV)

        # Merge with geometry
        states_gdf = states_gdf.merge(
            violence_df[['state_po', 'violence_per_1000_arrests', 'enforcement_classification',
                        'total_violent_incidents', 'arrests', 'deaths']],
            on='state_po',
            how='left'
        )

        # Categorize states by data availability
        # Has data: arrests > 0 OR total_violent_incidents > 0
        # No data: arrests == 0 AND (total_violent_incidents == 0 OR NaN)
        states_gdf['has_data'] = (states_gdf['arrests'].fillna(0) > 0) | (states_gdf['total_violent_incidents'].fillna(0) > 0)
        states_gdf['has_incidents'] = states_gdf['total_violent_incidents'].fillna(0) > 0

        # Fill missing values
        states_gdf['violence_per_1000_arrests'] = states_gdf['violence_per_1000_arrests'].fillna(0)
        states_gdf['enforcement_classification'] = states_gdf['enforcement_classification'].fillna('unknown')

        # Project to Albers for continental US
        states_gdf = states_gdf.to_crs('ESRI:102003')

        # Separate continental, Alaska, Hawaii
        continental = states_gdf[~states_gdf['state_po'].isin(['AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP'])].copy()
        alaska = states_gdf[states_gdf['state_po'] == 'AK'].copy()
        hawaii = states_gdf[states_gdf['state_po'] == 'HI'].copy()

        # Create custom colormap: Blue → White → Red
        cmap = LinearSegmentedColormap.from_list(
            'violence_ratio',
            [BLUE_LOW, WHITE_MID, RED_HIGH]
        )

        # Get max value for normalization (cap at reasonable max for visualization)
        max_ratio = min(violence_df['violence_per_1000_arrests'].max(), 5.0)
        norm = Normalize(vmin=0, vmax=max_ratio)

        # Determine color for each state based on data category
        def get_state_color(row):
            if not row['has_data']:
                return NO_DATA_COLOR  # No data collected
            elif not row['has_incidents']:
                return NO_INCIDENTS_COLOR  # Has arrests but no incidents documented
            else:
                return cmap(norm(min(row['violence_per_1000_arrests'], max_ratio)))

        continental['color'] = continental.apply(get_state_color, axis=1)

        # Plot states
        for idx, row in continental.iterrows():
            continental[continental.index == idx].plot(
                ax=ax,
                color=[row['color']],
                edgecolor='black',
                linewidth=0.8
            )
            # Add hatching for no-data states
            if not row['has_data']:
                continental[continental.index == idx].plot(
                    ax=ax,
                    facecolor='none',
                    edgecolor='gray',
                    linewidth=0.5,
                    hatch='///'
                )

        # Plot Alaska (scaled and moved)
        if not alaska.empty:
            alaska_scaled = alaska.copy()
            alaska_scaled.geometry = alaska_scaled.geometry.scale(0.35, 0.35, origin=(0, 0))
            alaska_scaled.geometry = alaska_scaled.geometry.translate(-1800000, -1400000)
            ak_row = alaska.iloc[0]
            if not ak_row['has_data']:
                alaska_scaled.plot(ax=ax, color=[NO_DATA_COLOR], edgecolor='black', linewidth=0.8, hatch='///')
            elif not ak_row['has_incidents']:
                alaska_scaled.plot(ax=ax, color=[NO_INCIDENTS_COLOR], edgecolor='black', linewidth=0.8)
            else:
                ak_color = cmap(norm(min(ak_row['violence_per_1000_arrests'], max_ratio)))
                alaska_scaled.plot(ax=ax, color=[ak_color], edgecolor='black', linewidth=0.8)

        # Plot Hawaii (scaled and moved)
        if not hawaii.empty:
            hawaii_scaled = hawaii.copy()
            hawaii_scaled.geometry = hawaii_scaled.geometry.scale(1.0, 1.0, origin=(0, 0))
            hawaii_scaled.geometry = hawaii_scaled.geometry.translate(5200000, -1200000)
            hi_row = hawaii.iloc[0]
            if not hi_row['has_data']:
                hawaii_scaled.plot(ax=ax, color=[NO_DATA_COLOR], edgecolor='black', linewidth=0.8, hatch='///')
            elif not hi_row['has_incidents']:
                hawaii_scaled.plot(ax=ax, color=[NO_INCIDENTS_COLOR], edgecolor='black', linewidth=0.8)
            else:
                hi_color = cmap(norm(min(hi_row['violence_per_1000_arrests'], max_ratio)))
                hawaii_scaled.plot(ax=ax, color=[hi_color], edgecolor='black', linewidth=0.8)

        # Add state labels with sanctuary status
        for idx, row in continental.iterrows():
            centroid = row.geometry.centroid
            status = row.get('enforcement_classification', 'unknown')
            label = STATUS_LABELS.get(status, '?')

            # Adjust font size for small states
            fontsize = 7 if row['state_po'] in ['CT', 'RI', 'DE', 'NJ', 'MD', 'MA', 'NH', 'VT'] else 8

            ax.annotate(
                label,
                xy=(centroid.x, centroid.y),
                ha='center', va='center',
                fontsize=fontsize,
                fontweight='bold',
                color='black',
                bbox=dict(boxstyle='circle,pad=0.2', facecolor='white', edgecolor='gray', alpha=0.8)
            )

        ax.axis('off')

        # Colorbar
        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, orientation='horizontal', fraction=0.03, pad=0.02, aspect=40)
        cbar.set_label('Violent Incidents per 1,000 ICE Arrests', fontsize=11)

        # Legend for status labels
        legend_elements = [
            mpatches.Patch(facecolor=STATUS_COLORS['sanctuary'], edgecolor='black',
                          label='S = Sanctuary (limits ICE cooperation)'),
            mpatches.Patch(facecolor=STATUS_COLORS['aggressive_anti_sanctuary'], edgecolor='black',
                          label='X = Aggressive Anti-Sanctuary (mandates cooperation)'),
            mpatches.Patch(facecolor=STATUS_COLORS['anti_sanctuary'], edgecolor='black',
                          label='A = Anti-Sanctuary (some mandatory cooperation)'),
            mpatches.Patch(facecolor=STATUS_COLORS['neutral'], edgecolor='black',
                          label='N = Neutral (no statewide policy)'),
            mpatches.Patch(facecolor=NO_INCIDENTS_COLOR, edgecolor='black',
                          label='Gray = Has arrests data, zero documented incidents'),
            mpatches.Patch(facecolor=NO_DATA_COLOR, edgecolor='black', hatch='///',
                          label='Hatched = No data collected'),
        ]
        ax.legend(handles=legend_elements, loc='lower left', fontsize=8, framealpha=0.95,
                 title='State Classification & Data Status', title_fontsize=10)

        # Title
        ax.set_title(
            'ICE Violent Incidents per 1,000 Arrests by State\n'
            'Blue = Low Ratio | Red = High Ratio | Gray = Zero Incidents | Hatched = No Data',
            fontsize=16, fontweight='bold', pad=20
        )

        # Add source note
        fig.text(0.5, 0.02,
                'Sources: Deportation Data Project (arrests); NBC News, The Trace, ProPublica (incidents); '
                'DOJ/ILRC (sanctuary classifications) | Period: Jan 20 – Oct 30, 2025',
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


def create_dual_panel_map(output_path=None):
    """
    Create two-panel map:
    - Panel A: Violence ratio (gradient) with data availability indicators
    - Panel B: Sanctuary classification (categorical)
    """
    set_style()
    warnings.filterwarnings('ignore')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

    # Colors for special categories
    NO_INCIDENTS_COLOR = '#d0d0d0'  # Light gray for zero incidents with data
    NO_DATA_COLOR = '#f0f0f0'       # Very light gray for no data collected

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

        # Categorize states by data availability
        states_gdf['has_data'] = (states_gdf['arrests'].fillna(0) > 0) | (states_gdf['total_violent_incidents'].fillna(0) > 0)
        states_gdf['has_incidents'] = states_gdf['total_violent_incidents'].fillna(0) > 0

        states_gdf['violence_per_1000_arrests'] = states_gdf['violence_per_1000_arrests'].fillna(0)
        states_gdf['enforcement_classification'] = states_gdf['enforcement_classification'].fillna('unknown')

        # Project
        states_gdf = states_gdf.to_crs('ESRI:102003')
        continental = states_gdf[~states_gdf['state_po'].isin(['AK', 'HI', 'PR', 'VI', 'GU', 'AS', 'MP'])].copy()

        # === PANEL A: Violence Ratio ===
        cmap = LinearSegmentedColormap.from_list('violence_ratio', [BLUE_LOW, WHITE_MID, RED_HIGH])
        max_ratio = min(violence_df['violence_per_1000_arrests'].max(), 5.0)
        norm = Normalize(vmin=0, vmax=max_ratio)

        # Determine color for each state based on data category
        def get_state_color(row):
            if not row['has_data']:
                return NO_DATA_COLOR
            elif not row['has_incidents']:
                return NO_INCIDENTS_COLOR
            else:
                return cmap(norm(min(row['violence_per_1000_arrests'], max_ratio)))

        for idx, row in continental.iterrows():
            color = get_state_color(row)
            continental[continental.index == idx].plot(ax=ax1, color=[color], edgecolor='black', linewidth=0.8)
            # Add hatching for no-data states
            if not row['has_data']:
                continental[continental.index == idx].plot(
                    ax=ax1, facecolor='none', edgecolor='gray', linewidth=0.5, hatch='///'
                )

        # Add labels with ratio values
        for idx, row in continental.iterrows():
            centroid = row.geometry.centroid
            if not row['has_data']:
                label = "?"  # No data
            elif not row['has_incidents']:
                label = "0"  # Zero incidents
            else:
                label = f"{row['violence_per_1000_arrests']:.1f}"
            fontsize = 6 if row['state_po'] in ['CT', 'RI', 'DE', 'NJ', 'MD', 'MA', 'NH', 'VT'] else 7
            ax1.annotate(label, xy=(centroid.x, centroid.y), ha='center', va='center',
                        fontsize=fontsize, fontweight='bold', color='black')

        ax1.axis('off')
        ax1.set_title('A. Violence Ratio\n(Incidents per 1,000 Arrests)', fontsize=14, fontweight='bold')

        # Colorbar for Panel A
        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax1, orientation='horizontal', fraction=0.03, pad=0.02, aspect=30)
        cbar.set_label('Incidents per 1,000 Arrests (0 = zero documented; ? = no data)', fontsize=9)

        # === PANEL B: Sanctuary Classification ===
        classification_colors = {
            'sanctuary': '#0047ab',
            'aggressive_anti_sanctuary': '#c41230',
            'anti_sanctuary': '#ff7f0e',
            'neutral': '#888888',
            'unknown': '#cccccc'
        }

        continental['class_color'] = continental['enforcement_classification'].map(classification_colors)
        continental['class_color'] = continental['class_color'].fillna('#cccccc')

        for idx, row in continental.iterrows():
            continental[continental.index == idx].plot(
                ax=ax2, color=[row['class_color']], edgecolor='black', linewidth=0.8
            )

        # Add state abbreviation labels
        for idx, row in continental.iterrows():
            centroid = row.geometry.centroid
            fontsize = 6 if row['state_po'] in ['CT', 'RI', 'DE', 'NJ', 'MD', 'MA', 'NH', 'VT'] else 7
            ax2.annotate(row['state_po'], xy=(centroid.x, centroid.y), ha='center', va='center',
                        fontsize=fontsize, fontweight='bold', color='white',
                        path_effects=[pe.withStroke(linewidth=2, foreground='black')])

        ax2.axis('off')
        ax2.set_title('B. Sanctuary Classification\n(State Immigration Enforcement Policy)', fontsize=14, fontweight='bold')

        # Legend for Panel B
        legend_elements = [
            mpatches.Patch(facecolor=classification_colors['sanctuary'], edgecolor='black',
                          label='Sanctuary (limits cooperation)'),
            mpatches.Patch(facecolor=classification_colors['aggressive_anti_sanctuary'], edgecolor='black',
                          label='Aggressive Anti-Sanctuary'),
            mpatches.Patch(facecolor=classification_colors['anti_sanctuary'], edgecolor='black',
                          label='Anti-Sanctuary'),
            mpatches.Patch(facecolor=classification_colors['neutral'], edgecolor='black',
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
                'DOJ/ILRC (classifications) | Period: Jan 20 – Oct 30, 2025',
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


if __name__ == '__main__':
    print("Generating ICE Violence Ratio Maps...")
    print("=" * 60)

    # Single panel map with sanctuary labels
    create_violence_ratio_map(output_path=OUTPUT_DIR / 'ice_violence_ratio_map.png')

    # Dual panel map
    create_dual_panel_map(output_path=OUTPUT_DIR / 'ice_violence_dual_panel_map.png')

    print("\nDone! Maps saved to:")
    print(f"  - {OUTPUT_DIR / 'ice_violence_ratio_map.png'}")
    print(f"  - {OUTPUT_DIR / 'ice_violence_dual_panel_map.png'}")
