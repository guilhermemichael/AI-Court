import pytest

from app.infrastructure.ai.agent_runtime import AgentInput, MockAgent


@pytest.mark.asyncio
async def test_mock_agent_clerk_mentions_case_title_and_law() -> None:
    payload = AgentInput(
        case_id="case-1",
        case_title="A Batalha da Pia",
        plaintiff_name="Autor",
        defendant_name="Reu",
        plaintiff_argument="O autor afirma que cozinhou e ficou com toda a louca.",
        defendant_argument="O reu sustenta que lavou tudo ontem e pede moderacao.",
        conflict_type="louca",
        drama_level=7,
        applicable_laws=["Art. 1o - Quem cozinha nao lava."],
        precedents=[],
        previous_events=[],
        allow_precedents=True,
    )

    output = await MockAgent("CLERK").run(payload)

    assert "A Batalha da Pia" in output.content
    assert "Art. 1o" in output.content
