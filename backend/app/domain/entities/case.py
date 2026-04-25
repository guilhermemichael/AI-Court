from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class CaseStatus(StrEnum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    RETRIEVING_PRECEDENTS = "RETRIEVING_PRECEDENTS"
    IN_TRIAL = "IN_TRIAL"
    DELIBERATING = "DELIBERATING"
    VERDICT_READY = "VERDICT_READY"
    PDF_READY = "PDF_READY"
    FAILED = "FAILED"


@dataclass(slots=True, frozen=True)
class CaseRecord:
    case_id: UUID
    title: str
    plaintiff_name: str
    defendant_name: str
    plaintiff_argument: str
    defendant_argument: str
    conflict_type: str
    drama_level: int
    allow_precedents: bool
    status: CaseStatus
    created_at: datetime
    updated_at: datetime
