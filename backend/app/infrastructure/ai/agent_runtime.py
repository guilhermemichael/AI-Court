from pydantic import BaseModel, Field


class AgentInput(BaseModel):
    case_id: str
    case_title: str
    plaintiff_name: str
    defendant_name: str
    plaintiff_argument: str
    defendant_argument: str
    conflict_type: str
    drama_level: int
    applicable_laws: list[str] = Field(default_factory=list)
    precedents: list[str] = Field(default_factory=list)
    previous_events: list[str] = Field(default_factory=list)
    allow_precedents: bool = True


class AgentOutput(BaseModel):
    role: str
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    extracted_facts: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    recommended_next_action: str
    metrics: dict[str, float | int | str] = Field(default_factory=dict)


class MockAgent:
    def __init__(self, role: str) -> None:
        self.role = role

    async def run(self, payload: AgentInput) -> AgentOutput:
        law_hint = (
            payload.applicable_laws[0] if payload.applicable_laws else "Art. 0 - convivio razoavel"
        )
        precedent_hint = (
            payload.precedents[0] if payload.precedents else "sem precedente catalogado"
        )
        if self.role == "CLERK":
            content = (
                f"Ata inicial registrada para o caso '{payload.case_title}'. "
                f"Fatos essenciais: conflito de {payload.conflict_type}, "
                f"drama nivel {payload.drama_level}, "
                f"autor {payload.plaintiff_name}, reu {payload.defendant_name}. "
                f"Base normativa inicial: {law_hint}."
            )
        elif self.role == "PROSECUTOR":
            content = (
                f"A acusacao sustenta que {payload.defendant_name} "
                "violou a harmonia domestica ao ignorar a narrativa de "
                f"{payload.plaintiff_name}. "
                f"O Ministerio da Pia entende que a conduta afronta {law_hint}."
            )
        elif self.role == "DEFENDER":
            content = (
                f"A defesa argumenta que ha contexto, atenuantes e reciprocidade emocional. "
                f"O argumento do reu destaca: '{payload.defendant_argument[:140]}'."
            )
        elif self.role == "EXPERT":
            content = (
                f"Pericia sintetica: gravidade {min(10, payload.drama_level)}, "
                f"dano emocional {payload.drama_level}, "
                "reincidencia estimada em 2 a 4 pontos e urgencia alta para restauracao da ordem."
            )
        elif self.role == "JURY":
            content = (
                "Juri popular IA: "
                "a pessoa pragmatica pede divisao clara de tarefas; "
                "a mae cansada quer paz imediata; "
                "o amigo debochado exige sobremesa compensatoria; "
                "o filosofo invoca responsabilidade compartilhada; "
                "o vizinho fofoqueiro recomenda carimbo oficial."
            )
        else:
            content = (
                "O Juiz IA observa coerencia minima entre fatos, "
                "normas da casa e dano emocional narrado. "
                f"Precedente consultado: {precedent_hint}."
            )
        return AgentOutput(
            role=self.role,
            content=content,
            confidence=0.91 if self.role != "JURY" else 0.77,
            extracted_facts=[
                payload.conflict_type,
                f"drama={payload.drama_level}",
                f"precedents={'on' if payload.allow_precedents else 'off'}",
            ],
            objections=[],
            recommended_next_action="ISSUE_VERDICT" if self.role == "JUDGE" else "CONTINUE",
            metrics={"drama_level": payload.drama_level, "law_count": len(payload.applicable_laws)},
        )
