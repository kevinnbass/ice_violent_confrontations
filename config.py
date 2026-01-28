"""
Centralized Configuration for ice_arrests Package
==================================================
All paths, constants, and configuration settings in one place.
"""

from pathlib import Path

# =============================================================================
# PATHS
# =============================================================================

# Project root directory
PROJECT_ROOT = Path(__file__).parent.resolve()

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
INCIDENTS_DIR = DATA_DIR / "incidents"

# Output directory for generated files
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# External data paths (for GeoJSON, etc.)
GEOJSON_PATH = Path("C:/Users/kbass/OneDrive/Documents/voter id and welfare/standalone_high_contrast_maps/data/us_states.geojson")

# =============================================================================
# DATA FILES
# =============================================================================

# JSON data files
DATA_FILES = {
    "tier1_deaths": INCIDENTS_DIR / "tier1_deaths_in_custody.json",
    "tier2_shootings": INCIDENTS_DIR / "tier2_shootings.json",
    "tier2_less_lethal": INCIDENTS_DIR / "tier2_less_lethal.json",
    "tier3_incidents": INCIDENTS_DIR / "tier3_incidents.json",
    "tier4_incidents": INCIDENTS_DIR / "tier4_incidents.json",
    "arrests_by_state": DATA_DIR / "arrests_by_state.json",
    "state_classifications": DATA_DIR / "state_classifications.json",
}

# =============================================================================
# VISUALIZATION CONSTANTS
# =============================================================================

# High contrast colors (matching voter id project)
COLORS = {
    "blue_low": "#0047ab",      # Low violence ratio
    "red_high": "#c41230",      # High violence ratio
    "white_mid": "#ffffff",     # Middle of gradient
    "no_incidents": "#d0d0d0",  # Light gray for zero incidents with data
    "no_data": "#f0f0f0",       # Very light gray for no data collected
}

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
}

# =============================================================================
# STATE MAPPINGS
# =============================================================================

STATE_ABBREV = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "District of Columbia": "DC",
}

ABBREV_TO_STATE = {v: k for k, v in STATE_ABBREV.items()}

# State centroids for label placement (approximate, in lat/lon)
STATE_CENTROIDS = {
    "AL": (-86.9, 32.8), "AK": (-153.5, 64.2), "AZ": (-111.4, 34.0), "AR": (-92.4, 34.9),
    "CA": (-119.4, 36.8), "CO": (-105.5, 39.0), "CT": (-72.7, 41.6), "DE": (-75.5, 39.0),
    "FL": (-81.5, 27.8), "GA": (-83.5, 32.6), "HI": (-155.5, 19.9), "ID": (-114.5, 44.2),
    "IL": (-89.4, 40.0), "IN": (-86.1, 39.9), "IA": (-93.2, 42.0), "KS": (-98.4, 38.5),
    "KY": (-84.9, 37.8), "LA": (-91.9, 31.2), "ME": (-69.4, 45.4), "MD": (-76.6, 39.0),
    "MA": (-71.5, 42.2), "MI": (-85.6, 44.3), "MN": (-94.6, 46.4), "MS": (-89.7, 32.7),
    "MO": (-92.5, 38.5), "MT": (-110.4, 47.0), "NE": (-99.9, 41.5), "NV": (-116.6, 38.8),
    "NH": (-71.6, 43.7), "NJ": (-74.4, 40.1), "NM": (-106.2, 34.5), "NY": (-75.5, 43.0),
    "NC": (-79.0, 35.5), "ND": (-100.5, 47.5), "OH": (-82.8, 40.4), "OK": (-97.5, 35.5),
    "OR": (-120.6, 43.8), "PA": (-77.2, 41.2), "RI": (-71.5, 41.7), "SC": (-81.0, 33.8),
    "SD": (-100.3, 44.5), "TN": (-86.6, 35.8), "TX": (-99.9, 31.5), "UT": (-111.5, 39.3),
    "VT": (-72.6, 44.0), "VA": (-78.5, 37.5), "WA": (-120.7, 47.4), "WV": (-80.5, 38.9),
    "WI": (-89.6, 44.6), "WY": (-107.3, 43.0), "DC": (-77.0, 38.9),
}

# =============================================================================
# DATA COVERAGE METADATA
# =============================================================================

DATA_COVERAGE = {
    "start_date": "2025-01-20",
    "end_date": "2025-10-15",
    "arrests_source": "Deportation Data Project",
    "incidents_sources": ["NBC News", "The Trace", "ProPublica", "ICE Official Reports"],
    "classification_sources": ["DOJ", "ILRC"],
}
