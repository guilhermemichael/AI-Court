from pydantic import BaseModel, Field


class GuiltInputs(BaseModel):
    severity: int = Field(ge=1, le=10)
    recurrence: int = Field(ge=1, le=10)
    emotional_damage: int = Field(ge=1, le=10)
    mitigating_factors: int = Field(ge=0, le=10)


class GuiltIndex(BaseModel):
    value: float = Field(ge=0.0, le=100.0)
    band: str


def guilt_band_for_score(value: float) -> str:
    if value <= 25:
        return "ADVERTENCIA_VERBAL"
    if value <= 50:
        return "PUNICAO_LEVE"
    if value <= 75:
        return "SENTENCA_COMPENSATORIA"
    return "CONDENACAO_DOMESTICA_MAXIMA"


def calculate_guilt_index(inputs: GuiltInputs) -> GuiltIndex:
    raw = (inputs.severity * inputs.recurrence * inputs.emotional_damage) / (
        inputs.mitigating_factors + 1
    )
    value = round(min(100.0, max(0.0, raw)), 2)
    return GuiltIndex(value=value, band=guilt_band_for_score(value))
