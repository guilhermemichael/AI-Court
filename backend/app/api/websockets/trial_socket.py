from collections import defaultdict
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.application.services.trial_broadcaster import TrialBroadcaster

router = APIRouter(tags=["trial-websocket"])


class TrialConnectionManager(TrialBroadcaster):
    def __init__(self) -> None:
        self.active_connections: defaultdict[UUID, set[WebSocket]] = defaultdict(set)

    async def connect(self, case_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[case_id].add(websocket)

    async def disconnect(self, case_id: UUID, websocket: WebSocket) -> None:
        self.active_connections[case_id].discard(websocket)
        if not self.active_connections[case_id]:
            self.active_connections.pop(case_id, None)

    async def broadcast(self, case_id: UUID, payload: dict[str, object]) -> None:
        for websocket in list(self.active_connections.get(case_id, set())):
            try:
                await websocket.send_json(payload)
            except Exception:
                await self.disconnect(case_id, websocket)


websocket_trial_broadcaster = TrialConnectionManager()


@router.websocket("/ws/trials/{case_id}")
async def trial_socket(case_id: UUID, websocket: WebSocket) -> None:
    await websocket_trial_broadcaster.connect(case_id, websocket)
    try:
        await websocket.send_json(
            {
                "type": "SOCKET_READY",
                "case_id": str(case_id),
                "content": (
                    "Canal processual estabelecido. O tribunal aceita sustentacao em tempo real."
                ),
            }
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_trial_broadcaster.disconnect(case_id, websocket)
