"""
ice_arrests - Analysis of ICE enforcement data
===============================================

A Python package for analyzing ICE arrests, violent incidents,
and state enforcement classifications.
"""

__version__ = "0.1.0"

from .data.loader import (
    load_incidents,
    load_arrests_by_state,
    load_state_classifications,
)

from .data.schemas import (
    SourceTier,
    IncidentType,
    VictimCategory,
    CollectionMethod,
)

__all__ = [
    "load_incidents",
    "load_arrests_by_state",
    "load_state_classifications",
    "SourceTier",
    "IncidentType",
    "VictimCategory",
    "CollectionMethod",
]
