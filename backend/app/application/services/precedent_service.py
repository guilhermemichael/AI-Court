from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import CaseModel, PrecedentModel
from app.infrastructure.db.repositories import HouseLawRepository, PrecedentRepository


@dataclass(slots=True, frozen=True)
class ReferenceBundle:
    house_laws: list[str]
    precedents: list[str]


class PrecedentService:
    def __init__(self, session: AsyncSession) -> None:
        self.house_laws = HouseLawRepository(session)
        self.precedents = PrecedentRepository(session)

    async def gather(self, case: CaseModel) -> ReferenceBundle:
        law_models = await self.house_laws.list_all(limit=3)
        applicable_laws = [
            f"{law.article_number} - {law.description}"
            for law in law_models
            if law.severity >= max(3, case.drama_level - 2)
        ]
        if not applicable_laws:
            applicable_laws = [
                f"{law.article_number} - {law.description}" for law in law_models[:2]
            ]

        precedent_models = await self.precedents.list_recent(limit=3)
        precedent_summaries = [
            f"{precedent.principle}: {precedent.summary}"
            for precedent in precedent_models
            if precedent.source_case_id != case.id
        ]
        return ReferenceBundle(house_laws=applicable_laws, precedents=precedent_summaries)

    async def create_from_verdict(
        self,
        case: CaseModel,
        principle: str,
        summary: str,
        outcome_trend: str,
    ) -> PrecedentModel:
        precedent = PrecedentModel(
            source_case_id=case.id,
            principle=principle,
            summary=summary,
            outcome_trend=outcome_trend,
            embedding=None,
        )
        return await self.precedents.save(precedent)
