import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import (
    CaseModel,
    HouseLawModel,
    PrecedentModel,
    TrialEventModel,
    VerdictModel,
)


class CaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, case: CaseModel) -> CaseModel:
        self.session.add(case)
        await self.session.commit()
        await self.session.refresh(case)
        return case

    async def get(self, case_id: uuid.UUID) -> CaseModel | None:
        return await self.session.get(CaseModel, case_id)

    async def update_status(self, case_id: uuid.UUID, status: str) -> None:
        case = await self.get(case_id)
        if case is None:
            raise LookupError("case_not_found")
        case.status = status
        await self.session.commit()


class TrialEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def next_sequence(self, case_id: uuid.UUID) -> int:
        stmt = select(func.coalesce(func.max(TrialEventModel.sequence_index), 0) + 1).where(
            TrialEventModel.case_id == case_id
        )
        result = await self.session.scalar(stmt)
        return int(result or 1)

    async def append(self, event: TrialEventModel) -> TrialEventModel:
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def list_for_case(self, case_id: uuid.UUID) -> list[TrialEventModel]:
        stmt = (
            select(TrialEventModel)
            .where(TrialEventModel.case_id == case_id)
            .order_by(TrialEventModel.sequence_index)
        )
        return list((await self.session.scalars(stmt)).all())


class VerdictRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, verdict: VerdictModel) -> VerdictModel:
        self.session.add(verdict)
        await self.session.commit()
        await self.session.refresh(verdict)
        return verdict

    async def get_by_case(self, case_id: uuid.UUID) -> VerdictModel | None:
        stmt = select(VerdictModel).where(VerdictModel.case_id == case_id)
        return await self.session.scalar(stmt)


class PrecedentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_recent(self, limit: int = 5) -> list[PrecedentModel]:
        stmt = select(PrecedentModel).order_by(PrecedentModel.created_at.desc()).limit(limit)
        return list((await self.session.scalars(stmt)).all())

    async def save(self, precedent: PrecedentModel) -> PrecedentModel:
        self.session.add(precedent)
        await self.session.commit()
        await self.session.refresh(precedent)
        return precedent


class HouseLawRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self, limit: int = 20) -> list[HouseLawModel]:
        stmt = (
            select(HouseLawModel)
            .order_by(HouseLawModel.severity.desc(), HouseLawModel.article_number)
            .limit(limit)
        )
        return list((await self.session.scalars(stmt)).all())
