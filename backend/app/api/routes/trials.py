import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.websockets.trial_socket import websocket_trial_broadcaster
from app.application.services.trial_orchestrator import TrialOrchestrator
from app.infrastructure.db.session import get_session

router = APIRouter(prefix="/trials", tags=["trials"])


@router.post("/{case_id}/start")
async def start_trial(
    case_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> dict[str, object]:
    try:
        verdict = await TrialOrchestrator(session, broadcaster=websocket_trial_broadcaster).run(
            case_id
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="case_not_found") from None
    return {
        "case_id": str(case_id),
        "status": "VERDICT_READY",
        "verdict": {
            "winner": verdict.winner,
            "guilt_index": float(verdict.guilt_index),
            "sentence": verdict.sentence,
            "reasoning": verdict.reasoning,
            "compensation_order": verdict.compensation_order,
            "appeal_allowed": verdict.appeal_allowed,
        },
    }
