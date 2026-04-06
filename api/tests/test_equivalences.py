from app.services.equivalences import build_equivalences


def test_build_equivalences_returns_values_for_positive_debt() -> None:
    result = build_equivalences(300_000_000)

    assert len(result) == 3
    assert result[0].label == "hospitales_publicos"
    assert result[0].value == 2.0


def test_build_equivalences_returns_empty_when_debt_missing() -> None:
    assert build_equivalences(None) == []
    assert build_equivalences(0) == []
