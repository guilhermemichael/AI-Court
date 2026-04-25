from app.domain.policies.sentencing_policy import build_sentencing_decision
from app.domain.value_objects.guilt_index import GuiltIndex


def test_sentencing_policy_returns_compensatory_sentence_for_mid_high_guilt() -> None:
    decision = build_sentencing_decision(
        guilt=GuiltIndex(value=68.0, band="SENTENCA_COMPENSATORIA"),
        plaintiff_name="Autor",
        defendant_name="Reu",
        applicable_laws=["Art. 3o - Comer o ultimo pedaco sem aviso e crime emocional."],
        precedent_summaries=["Caso da Lasanha Desaparecida: o consumo indevido agravou a pena."],
    )

    assert decision.winner == "PLAINTIFF"
    assert "sobremesa" in decision.sentence.lower()
    assert "Lasanha" in decision.reasoning
