"""
ice_arrests.visualization - Map and chart generation
=====================================================

Submodules:
- styles: Color constants and matplotlib styling
- maps: Basic violence ratio maps
- tiered_maps: Tier-based incident visualizations
- category_maps: Victim category-specific maps
"""

from .styles import set_style, COLORS, STATUS_LABELS, STATUS_COLORS
from .maps import create_violence_ratio_map, create_dual_panel_map

# Tiered map functions
from .tiered_maps import (
    create_tiered_ratio_maps,
    create_isolated_tier_ratio_maps,
    aggregate_incidents_by_tier,
    aggregate_incidents_single_tier,
    aggregate_incidents_by_tier_and_category,
)

# Category map functions
from .category_maps import (
    create_category_tiered_ratio_map,
    create_category_isolated_tier_ratio_map,
    create_single_panel_incident_map,
    generate_all_category_maps,
    VICTIM_CATEGORIES,
    NON_IMMIGRANT_CATEGORIES,
)

__all__ = [
    # Styles
    "set_style",
    "COLORS",
    "STATUS_LABELS",
    "STATUS_COLORS",
    # Basic maps
    "create_violence_ratio_map",
    "create_dual_panel_map",
    # Tiered maps
    "create_tiered_ratio_maps",
    "create_isolated_tier_ratio_maps",
    "aggregate_incidents_by_tier",
    "aggregate_incidents_single_tier",
    "aggregate_incidents_by_tier_and_category",
    # Category maps
    "create_category_tiered_ratio_map",
    "create_category_isolated_tier_ratio_map",
    "create_single_panel_incident_map",
    "generate_all_category_maps",
    "VICTIM_CATEGORIES",
    "NON_IMMIGRANT_CATEGORIES",
]
