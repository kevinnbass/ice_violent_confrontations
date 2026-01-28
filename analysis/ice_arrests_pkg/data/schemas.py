"""
Data Schemas and Enums for ice_arrests
======================================
Defines the enums, dataclasses, and type definitions used throughout the package.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class SourceTier(Enum):
    """
    Data source quality tiers.

    Tier 1: Official government data (ICE reports, court records, FOIA releases)
    Tier 2: FOIA-obtained / systematic investigative journalism
    Tier 3: News media - found via systematic search
    Tier 4: News media - found via ad-hoc search (may have selection bias)
    """
    OFFICIAL = 1
    FOIA_INVESTIGATIVE = 2
    NEWS_SYSTEMATIC = 3
    NEWS_ADHOC = 4


class IncidentType(Enum):
    """Types of incidents tracked."""
    DEATH_IN_CUSTODY = "death_in_custody"
    SHOOTING_BY_AGENT = "shooting_by_agent"
    SHOOTING_AT_AGENT = "shooting_at_agent"
    LESS_LETHAL = "less_lethal"
    PHYSICAL_FORCE = "physical_force"
    WRONGFUL_DETENTION = "wrongful_detention"
    WRONGFUL_DEPORTATION = "wrongful_deportation"
    MASS_RAID = "mass_raid"


class VictimCategory(Enum):
    """Who was affected by the incident."""
    DETAINEE = "detainee"
    ENFORCEMENT_TARGET = "enforcement_target"
    PROTESTER = "protester"
    JOURNALIST = "journalist"
    BYSTANDER = "bystander"
    US_CITIZEN_COLLATERAL = "us_citizen_collateral"
    OFFICER = "officer"
    MULTIPLE = "multiple"


class ProtestGranularity(Enum):
    """Granular classification for protest-related incidents."""
    INDIVIDUAL_INJURY = "individual_injury"
    FORCE_DEPLOYMENT = "force_deployment"
    MASS_ARREST = "mass_arrest"
    INDIVIDUAL_ARREST = "individual_arrest"
    JOURNALIST_ATTACK = "journalist_attack"
    PROPERTY_DAMAGE = "property_damage"
    CONFRONTATION = "confrontation"


class IncidentScale(Enum):
    """
    Scale of incident by number of people affected.
    Critical for weighting incidents in analysis - a mass raid affecting 1000 people
    should be treated differently than a single wrongful detention.
    """
    SINGLE = "single"          # 1 person
    SMALL = "small"            # 2-10 people
    MEDIUM = "medium"          # 11-50 people
    LARGE = "large"            # 51-200 people
    MASS = "mass"              # 200+ people

    @classmethod
    def from_count(cls, count: int) -> 'IncidentScale':
        """Compute scale category from affected count."""
        if count is None or count <= 1:
            return cls.SINGLE
        elif count <= 10:
            return cls.SMALL
        elif count <= 50:
            return cls.MEDIUM
        elif count <= 200:
            return cls.LARGE
        else:
            return cls.MASS


class OutcomeCategory(Enum):
    """
    Standardized outcome categories for analysis.
    The detailed outcome description is kept in 'outcome_detail' field.
    """
    DEATH = "death"                    # Fatal outcome
    SERIOUS_INJURY = "serious_injury"  # Hospitalization, surgery, permanent damage
    INJURY = "injury"                  # Non-fatal injury
    DETAINED = "detained"              # Held by ICE (enforcement targets)
    ARRESTED = "arrested"              # Arrested (protesters, bystanders)
    RELEASED = "released"              # Released without charge (wrongful detention)
    NO_INJURY = "no_injury"            # No physical harm (peaceful protests)
    DEPORTED = "deported"              # Deported/removed
    MULTIPLE = "multiple"              # Mixed outcomes (deaths + injuries + arrests)


class CollectionMethod(Enum):
    """How the data was collected."""
    OFFICIAL_REPORT = "official_report"
    FOIA = "foia"
    LITIGATION = "litigation"
    INVESTIGATIVE = "investigative"
    SYSTEMATIC_SEARCH = "systematic_search"
    AD_HOC_SEARCH = "ad_hoc_search"


class EnforcementClassification(Enum):
    """State enforcement classification."""
    SANCTUARY = "sanctuary"
    ANTI_SANCTUARY = "anti_sanctuary"
    AGGRESSIVE_ANTI_SANCTUARY = "aggressive_anti_sanctuary"
    NEUTRAL = "neutral"


class LocalSanctuaryStatus(Enum):
    """
    Local (city/county) sanctuary policy status.
    Based on ILRC color-coding system.
    """
    # Sanctuary-leaning policies
    SANCTUARY_STRONG = "sanctuary_strong"      # ILRC green: Active disentanglement from ICE
    SANCTUARY_LIMITED = "sanctuary_limited"    # ILRC light green: Decline detainers, limited cooperation
    SANCTUARY_PARTIAL = "sanctuary_partial"    # ILRC yellow: Reject detainers but some cooperation

    # Cooperation-leaning policies
    COOPERATIVE = "cooperative"                # ILRC orange: Honor detainers, share info
    AGGRESSIVE_COOPERATION = "aggressive"      # Active 287(g) or similar agreements

    # Conflict situations
    POLICY_CONFLICT = "policy_conflict"        # City policy conflicts with state law
    UNKNOWN = "unknown"


class DetainerPolicy(Enum):
    """
    Local law enforcement detainer compliance policy.
    """
    HONOR_ALL = "honor_all"                    # Honor all ICE detainers
    HONOR_JUDICIAL_ONLY = "honor_judicial"     # Only honor judicial warrants, not admin warrants
    HONOR_FELONY_ONLY = "honor_felony"         # Only honor for serious crimes
    DECLINE_ALL = "decline_all"               # Decline all ICE detainers
    CASE_BY_CASE = "case_by_case"              # Discretionary/case-by-case
    STATE_MANDATED = "state_mandated"          # Policy mandated by state law (e.g., TX SB4)


class JurisdictionLevel(Enum):
    """Level at which a policy applies."""
    STATE = "state"
    COUNTY = "county"
    CITY = "city"
    SHERIFF = "sheriff"                        # Sheriff-specific (elected, may differ from county)


# =============================================================================
# CONFIDENCE LEVELS
# =============================================================================

CONFIDENCE_LEVELS = {
    "HIGH": "Data from official government sources with mandated reporting",
    "MEDIUM_HIGH": "Data from FOIA releases or systematic investigative journalism",
    "MEDIUM": "Data from systematic news search with known coverage biases",
    "LOW_MEDIUM": "Data available but significant gaps acknowledged",
    "LOW": "Ad-hoc data collection with high selection bias risk",
}


# =============================================================================
# DATACLASSES
# =============================================================================

@dataclass
class Incident:
    """Represents a single incident."""
    id: str
    date: str
    state: str
    incident_type: str
    source_tier: int
    source_url: str
    source_name: str
    verified: bool = True
    city: Optional[str] = None
    victim_name: Optional[str] = None
    victim_age: Optional[int] = None
    victim_nationality: Optional[str] = None
    outcome: Optional[str] = None
    us_citizen: bool = False
    protest_related: bool = False
    notes: Optional[str] = None
    # Scale fields - critical for proper analysis weighting
    affected_count: Optional[int] = None  # Total people directly affected
    incident_scale: Optional[str] = None  # single/small/medium/large/mass
    # Legacy count fields (retained for specificity)
    victim_count: Optional[int] = None    # People detained/injured
    arrest_count: Optional[int] = None    # Arrests (protest context)
    officer_injuries: Optional[int] = None  # Officers injured
    # Cross-tier deduplication fields
    canonical_incident_id: Optional[str] = None  # Unique ID for real-world incident
    is_primary_record: bool = True               # True if this is the authoritative record
    related_incidents: List[str] = field(default_factory=list)  # Cross-references to other records
    # Sanctuary jurisdiction fields
    state_sanctuary_status: Optional[str] = None      # State-level policy (sanctuary/anti_sanctuary/neutral)
    local_sanctuary_status: Optional[str] = None      # City/county policy from LocalSanctuaryStatus
    detainer_policy: Optional[str] = None             # Local detainer compliance policy
    policy_conflict: bool = False                     # True if local policy conflicts with state
    jurisdiction_notes: Optional[str] = None          # Notes on jurisdiction policy context


@dataclass
class ArrestRecord:
    """Represents arrest data for a state."""
    state: str
    arrests: int
    rate_per_100k: float
    source_url: str
    source_name: str
    date_range: str
    notes: Optional[str] = None


@dataclass
class StateClassification:
    """Represents classification data for a state."""
    state: str
    classification: str
    tier: str
    primary_law: str
    source_url: str
    source_name: str
    doj_designated: bool = False
    effective_date: Optional[str] = None
    ilrc_rating: Optional[str] = None
