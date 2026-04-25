import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.value_objects.guilt_index import guilt_band_for_score
from app.infrastructure.db.repositories import VerdictRepository
from app.infrastructure.db.session import get_session

router = APIRouter(prefix="/verdicts", tags=["verdicts"])


@router.get("/{case_id}")
async def get_verdict(
    case_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> dict[str, object]:
    verdict = await VerdictRepository(session).get_by_case(case_id)
    if verdict is None:
        raise HTTPException(status_code=404, detail="verdict_not_found")
    return {
        "case_id": str(case_id),
        "winner": verdict.winner,
        "guilt_index": float(verdict.guilt_index),
        "guilt_band": guilt_band_for_score(float(verdict.guilt_index)),
        "sentence": verdict.sentence,
        "reasoning": verdict.reasoning,
        "compensation_order": verdict.compensation_order,
        "appeal_allowed": verdict.appeal_allowed,
        "created_at": verdict.created_at.isoformat(),
    }
