from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(slots=True, frozen=True)
class TrialEventRecord:
    event_id: UUID
    case_id: UUID
    sequence_index: int
    event_type: str
    agent_role: str | None
    content: str
    metadata: dict[str, object] = field(default_factory=dict)
    created_at: datetime | None = None
