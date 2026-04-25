import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import CaseModel
from app.infrastructure.db.repositories import (
    CaseRepository,
    TrialEventRepository,
    VerdictRepository,
)
from app.infrastructure.db.session import get_session

router = APIRouter(prefix="/cases", tags=["cases"])


class CaseCreate(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    plaintiff_name: str = Field(min_length=1, max_length=80)
    defendant_name: str = Field(min_length=1, max_length=80)
    plaintiff_argument: str = Field(min_length=10, max_length=8000)
    defendant_argument: str = Field(min_length=10, max_length=8000)
    conflict_type: str = Field(min_length=2, max_length=80)
    drama_level: int = Field(ge=1, le=10)
    allow_precedents: bool = True


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_case(
    payload: CaseCreate, session: AsyncSession = Depends(get_session)
) -> dict[str, object]:
    repo = CaseRepository(session)
    case = await repo.create(CaseModel(**payload.model_dump()))
    return {
        "id": str(case.id),
        "status": case.status,
        "title": case.title,
        "allow_precedents": case.allow_precedents,
    }


@router.get("/{case_id}")
async def get_case(
    case_id: uuid.UUID, session: AsyncSession = Depends(get_session)
) -> dict[str, object]:
    case = await CaseRepository(session).get(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="case_not_found")
    events = await TrialEventRepository(session).list_for_case(case_id)
    verdict = await VerdictRepository(session).get_by_case(case_id)
    return {
        "id": str(case.id),
        "title": case.title,
        "plaintiff_name": case.plaintiff_name,
        "defendant_name": case.defendant_name,
        "conflict_type": case.conflict_type,
        "drama_level": case.drama_level,
        "allow_precedents": case.allow_precedents,
        "status": case.status,
        "events": [
            {
                "sequence_index": event.sequence_index,
                "event_type": event.event_type,
                "agent_role": event.agent_role,
                "content": event.content,
                "metadata": event.event_metadata,
                "created_at": event.created_at.isoformat() if event.created_at else None,
            }
            for event in events
        ],
        "verdict": None
        if verdict is None
        else {
            "winner": verdict.winner,
            "guilt_index": float(verdict.guilt_index),
            "sentence": verdict.sentence,
            "reasoning": verdict.reasoning,
            "compensation_order": verdict.compensation_order,
            "appeal_allowed": verdict.appeal_allowed,
        },
    }
