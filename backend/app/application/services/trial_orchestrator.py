import asyncio
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.precedent_service import PrecedentService
from app.application.services.trial_broadcaster import NullTrialBroadcaster, TrialBroadcaster
from app.domain.policies.sentencing_policy import build_sentencing_decision
from app.domain.value_objects.guilt_index import GuiltInputs, calculate_guilt_index
from app.infrastructure.ai.agent_runtime import AgentInput, MockAgent
from app.infrastructure.db.models import TrialEventModel, VerdictModel
from app.infrastructure.db.repositories import (
    CaseRepository,
    TrialEventRepository,
    VerdictRepository,
)
from app.settings import get_settings

settings = get_settings()


class TrialOrchestrator:
    def __init__(
        self,
        session: AsyncSession,
        broadcaster: TrialBroadcaster | None = None,
    ) -> None:
        self.case_repo = CaseRepository(session)
        self.event_repo = TrialEventRepository(session)
        self.verdict_repo = VerdictRepository(session)
        self.precedent_service = PrecedentService(session)
        self.broadcaster = broadcaster or NullTrialBroadcaster()
        self.agents = [
            MockAgent("CLERK"),
            MockAgent("PROSECUTOR"),
            MockAgent("DEFENDER"),
            MockAgent("EXPERT"),
            MockAgent("JURY"),
            MockAgent("JUDGE"),
        ]

    async def run(self, case_id: uuid.UUID) -> VerdictModel:
        case = await self.case_repo.get(case_id)
        if case is None:
            raise LookupError("case_not_found")

        existing = await self.verdict_repo.get_by_case(case_id)
        if existing is not None:
            return existing

        await self.case_repo.update_status(case_id, "RETRIEVING_PRECEDENTS")
        references = await self.precedent_service.gather(case)
        await self._broadcast_status(
            case_id,
            "RETRIEVING_PRECEDENTS",
            "O Escrivao IA esta recuperando leis da casa e precedentes relevantes.",
        )

        await self.case_repo.update_status(case_id, "IN_TRIAL")
        await self._broadcast_status(
            case_id,
            "IN_TRIAL",
            "Audiencia iniciada. O tribunal abriu a fase probatoria em tempo real.",
        )

        previous_events: list[str] = [f"LAW: {law}" for law in references.house_laws]

        for agent in self.agents:
            payload = AgentInput(
                case_id=str(case.id),
                case_title=case.title,
                plaintiff_name=case.plaintiff_name,
                defendant_name=case.defendant_name,
                plaintiff_argument=case.plaintiff_argument,
                defendant_argument=case.defendant_argument,
                conflict_type=case.conflict_type,
                drama_level=case.drama_level,
                applicable_laws=references.house_laws,
                precedents=references.precedents if case.allow_precedents else [],
                previous_events=previous_events,
                allow_precedents=case.allow_precedents,
            )
            output = await agent.run(payload)
            event = await self._append_event(
                case_id=case_id,
                event_type="AGENT_SPOKE",
                agent_role=output.role,
                content=output.content,
                metadata=output.model_dump(),
            )
            await self.broadcaster.broadcast(case_id, self._serialize_event(event))
            previous_events.append(f"{output.role}: {output.content}")
            await asyncio.sleep(settings.trial_step_delay_ms / 1000)

        guilt = calculate_guilt_index(
            GuiltInputs(
                severity=min(10, max(1, case.drama_level)),
                recurrence=4 if references.precedents else 2,
                emotional_damage=case.drama_level,
                mitigating_factors=2 if len(case.defendant_argument) > 80 else 1,
            )
        )
        decision = build_sentencing_decision(
            guilt=guilt,
            plaintiff_name=case.plaintiff_name,
            defendant_name=case.defendant_name,
            applicable_laws=references.house_laws,
            precedent_summaries=references.precedents if case.allow_precedents else [],
        )

        await self.case_repo.update_status(case_id, "DELIBERATING")
        await self._broadcast_status(
            case_id,
            "DELIBERATING",
            "O Juiz IA entrou em deliberacao final e esta consolidando a sentenca.",
        )

        verdict = await self.verdict_repo.save(
            VerdictModel(
                case_id=case_id,
                winner=decision.winner,
                guilt_index=guilt.value,
                sentence=decision.sentence,
                reasoning=decision.reasoning,
                compensation_order=decision.compensation_order,
                appeal_allowed=True,
            )
        )
        await self.precedent_service.create_from_verdict(
            case=case,
            principle=f"Principio do caso {case.title}",
            summary=decision.reasoning,
            outcome_trend=decision.winner,
        )
        await self._append_event(
            case_id=case_id,
            event_type="VERDICT_ISSUED",
            agent_role="JUDGE",
            content=decision.sentence,
            metadata={"winner": decision.winner, "guilt_index": guilt.value, "band": guilt.band},
        )

        await self.case_repo.update_status(case_id, "VERDICT_READY")
        await self.broadcaster.broadcast(
            case_id,
            {
                "type": "VERDICT_READY",
                "case_id": str(case_id),
                "status": "VERDICT_READY",
                "winner": verdict.winner,
                "guilt_index": float(verdict.guilt_index),
                "sentence": verdict.sentence,
            },
        )
        return verdict

    async def _append_event(
        self,
        case_id: uuid.UUID,
        event_type: str,
        agent_role: str | None,
        content: str,
        metadata: dict[str, object],
    ) -> TrialEventModel:
        sequence = await self.event_repo.next_sequence(case_id)
        return await self.event_repo.append(
            TrialEventModel(
                case_id=case_id,
                sequence_index=sequence,
                event_type=event_type,
                agent_role=agent_role,
                content=content,
                event_metadata=metadata,
            )
        )

    async def _broadcast_status(self, case_id: uuid.UUID, status: str, content: str) -> None:
        await self.broadcaster.broadcast(
            case_id,
            {
                "case_id": str(case_id),
                "type": "TRIAL_STATUS",
                "status": status,
                "content": content,
            },
        )

    def _serialize_event(self, event: TrialEventModel) -> dict[str, object]:
        return {
            "case_id": str(event.case_id),
            "sequence_index": event.sequence_index,
            "type": event.event_type,
            "agent_role": event.agent_role,
            "content": event.content,
            "metadata": event.event_metadata,
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
