from app.domain.value_objects.guilt_index import GuiltInputs, calculate_guilt_index


def test_guilt_index_is_bounded() -> None:
    result = calculate_guilt_index(
        GuiltInputs(severity=10, recurrence=10, emotional_damage=10, mitigating_factors=0)
    )
    assert result.value == 100.0
    assert result.band == "CONDENACAO_DOMESTICA_MAXIMA"
