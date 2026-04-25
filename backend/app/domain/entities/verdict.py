from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(slots=True, frozen=True)
class VerdictRecord:
    verdict_id: UUID
    case_id: UUID
    winner: str
    guilt_index: float
    sentence: str
    reasoning: str
    compensation_order: str | None
    appeal_allowed: bool
    created_at: datetime
    applied_laws: list[str] = field(default_factory=list)
    precedents: list[str] = field(default_factory=list)
