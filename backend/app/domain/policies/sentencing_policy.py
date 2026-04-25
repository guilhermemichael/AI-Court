from dataclasses import dataclass

from app.domain.value_objects.guilt_index import GuiltIndex


@dataclass(slots=True, frozen=True)
class SentencingDecision:
    winner: str
    sentence: str
    reasoning: str
    compensation_order: str


def build_sentencing_decision(
    guilt: GuiltIndex,
    plaintiff_name: str,
    defendant_name: str,
    applicable_laws: list[str],
    precedent_summaries: list[str],
) -> SentencingDecision:
    laws_text = (
        ", ".join(applicable_laws[:2]) if applicable_laws else "os principios gerais da convivencia"
    )
    precedent_text = (
        precedent_summaries[0]
        if precedent_summaries
        else "nao ha precedente formal, mas a corte reconhece padroes recorrentes de caos domestico"
    )

    if guilt.value <= 25:
        return SentencingDecision(
            winner="MEDIATED",
            sentence="Advertencia verbal com registro em ata e conciliacao obrigatoria na cozinha.",
            reasoning=(
                f"A gravidade foi considerada baixa. Aplicam-se {laws_text}, "
                "com foco restaurativo. "
                f"O precedente orientador indica que pequenos atritos entre "
                f"{plaintiff_name} e {defendant_name} "
                "devem ser resolvidos com humor, nao com escalada."
            ),
            compensation_order="Troca simbolica de gentilezas e uma bebida de paz em ate 24 horas.",
        )

    if guilt.value <= 50:
        return SentencingDecision(
            winner="PARTIAL",
            sentence="Punicao leve com tarefa compensatoria unica e retratacao em tom respeitoso.",
            reasoning=(
                f"O tribunal reconhece culpa moderada e adota {laws_text} como base. "
                f"Prevalece o entendimento expresso no precedente: {precedent_text}."
            ),
            compensation_order=(
                "Lavar a louca completa de um jantar e devolver a paz social ao ambiente."
            ),
        )

    if guilt.value <= 75:
        return SentencingDecision(
            winner="PLAINTIFF",
            sentence=(
                "Sentenca compensatoria: tres dias consecutivos de servico domestico, "
                "com recurso condicionado a apresentacao de sobremesa convincente."
            ),
            reasoning=(
                "A combinacao de dano emocional, reincidencia e narrativa "
                f"consistente favorece {plaintiff_name}. "
                f"As normas aplicadas foram {laws_text}. "
                f"O tribunal ainda observa o precedente: {precedent_text}."
            ),
            compensation_order=(
                "Executar tarefa compensatoria por 3 dias e redigir pedido formal de desculpas."
            ),
        )

    return SentencingDecision(
        winner="PLAINTIFF",
        sentence=(
            "Condenacao domestica maxima: assumir a louca, a coleta do lixo "
            "e a sobremesa oficial da reconciliacao "
            "durante um ciclo completo de tres noites."
        ),
        reasoning=(
            f"O comportamento imputado a {defendant_name} violou frontalmente {laws_text}. "
            f"A corte considera decisivo o precedente: {precedent_text}."
        ),
        compensation_order=(
            "Servico domestico ampliado por 3 noites, com fiscalizacao moral do autor."
        ),
    )
