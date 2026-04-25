from typing import Protocol
from uuid import UUID


class TrialBroadcaster(Protocol):
    async def broadcast(self, case_id: UUID, payload: dict[str, object]) -> None: ...


class NullTrialBroadcaster:
    async def broadcast(self, case_id: UUID, payload: dict[str, object]) -> None:
        del case_id
        del payload
