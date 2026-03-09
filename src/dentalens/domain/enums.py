"""Domain enumerations for DentaLens AI."""

from enum import Enum


class ClaimStatus(str, Enum):
    SUBMITTED = "submitted"
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    APPEALED = "appealed"


class ProcedureCategory(str, Enum):
    DIAGNOSTIC = "diagnostic"
    PREVENTIVE = "preventive"
    RESTORATIVE = "restorative"
    ENDODONTIC = "endodontic"
    PERIODONTIC = "periodontic"
    PROSTHODONTIC = "prosthodontic"
    ORAL_SURGERY = "oral_surgery"
    ORTHODONTIC = "orthodontic"


class PlanType(str, Enum):
    PPO = "PPO"
    HMO = "HMO"
    DISCOUNT = "Discount"


class AgentType(str, Enum):
    ROUTER = "router"
    BENEFITS = "benefits"
    CLAIMS = "claims"


class IntentType(str, Enum):
    BENEFITS_QUESTION = "benefits_question"
    CLAIMS_INQUIRY = "claims_inquiry"
    GENERAL = "general"
    UNKNOWN = "unknown"
