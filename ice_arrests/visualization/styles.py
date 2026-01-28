"""
Visualization Styles for ice_arrests
====================================
Colors, fonts, and styling functions for consistent visualization.
"""

import matplotlib.pyplot as plt

# =============================================================================
# COLOR CONSTANTS
# =============================================================================

# High contrast colors (matching voter id project)
COLORS = {
    "blue_low": "#0047ab",      # Low violence ratio
    "red_high": "#c41230",      # High violence ratio
    "white_mid": "#ffffff",     # Middle of gradient
    "no_incidents": "#d0d0d0",  # Light gray for zero incidents with data
    "no_data": "#f0f0f0",       # Very light gray for no data collected
}

# Convenience aliases
BLUE_LOW = COLORS["blue_low"]
RED_HIGH = COLORS["red_high"]
WHITE_MID = COLORS["white_mid"]
NO_INCIDENTS_COLOR = COLORS["no_incidents"]
NO_DATA_COLOR = COLORS["no_data"]

# =============================================================================
# STATUS LABEL MAPPINGS
# =============================================================================

# Sanctuary status label mapping
STATUS_LABELS = {
    "sanctuary": "S",
    "anti_sanctuary": "A",
    "aggressive_anti_sanctuary": "X",
    "neutral": "N",
}

STATUS_COLORS = {
    "sanctuary": "#0047ab",           # Blue
    "aggressive_anti_sanctuary": "#c41230",  # Red
    "anti_sanctuary": "#ff7f0e",      # Orange
    "neutral": "#888888",             # Gray
    "unknown": "#cccccc",             # Light gray
}

# =============================================================================
# CLASSIFICATION COLORS FOR MAPS
# =============================================================================

CLASSIFICATION_COLORS = {
    "sanctuary": "#0047ab",
    "aggressive_anti_sanctuary": "#c41230",
    "anti_sanctuary": "#ff7f0e",
    "neutral": "#888888",
    "unknown": "#cccccc",
}

# =============================================================================
# STYLING FUNCTIONS
# =============================================================================

def set_style():
    """Set consistent matplotlib style matching main branch."""
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


def get_colormap():
    """
    Get the Blue → White → Red colormap for violence ratios.

    Returns:
        matplotlib LinearSegmentedColormap
    """
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list(
        'violence_ratio',
        [BLUE_LOW, WHITE_MID, RED_HIGH]
    )


def get_state_color(row, cmap, norm):
    """
    Determine the color for a state based on its data.

    Args:
        row: DataFrame row with state data
        cmap: Colormap for violence ratio
        norm: Normalizer for the colormap

    Returns:
        Color value (hex string or RGBA tuple)
    """
    if not row.get('has_data', True):
        return NO_DATA_COLOR
    elif not row.get('has_incidents', True):
        return NO_INCIDENTS_COLOR
    else:
        ratio = row.get('violence_per_1000_arrests', 0)
        max_ratio = norm.vmax
        return cmap(norm(min(ratio, max_ratio)))


# =============================================================================
# SMALL STATES LIST
# =============================================================================

SMALL_STATES = ['CT', 'RI', 'DE', 'NJ', 'MD', 'MA', 'NH', 'VT']
