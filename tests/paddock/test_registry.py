"""Tests for the Settlement Type registry metadata and seeding."""

from collections.abc import Mapping
from typing import Any

from paddock.settlement import SETTLEMENT_TYPES, seed
from paddock.settlement.grading import GRADERS
from paddock.settlement.registry import ENTITY_SET


class FakeDataverse:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, Mapping[str, Any]]] = []

    def upsert(self, entity_set: str, alternate_key: str, data: Mapping[str, Any]) -> None:
        self.calls.append((entity_set, alternate_key, data))


def test_registry_covers_all_twelve_types() -> None:
    codes = {t.code for t in SETTLEMENT_TYPES}
    assert codes == set(GRADERS)
    assert len(SETTLEMENT_TYPES) == 12
    assert all(t.tier == "A" for t in SETTLEMENT_TYPES)


def test_registry_parameters_match_models() -> None:
    for meta in SETTLEMENT_TYPES:
        model, _fn = GRADERS[meta.code]
        assert meta.parameters == tuple(model.model_fields)
        assert meta.label  # non-empty human label


def test_seed_upserts_every_type_by_code() -> None:
    dv = FakeDataverse()
    count = seed(dv)
    assert count == 12
    assert len(dv.calls) == 12
    entity, key, data = dv.calls[0]
    assert entity == ENTITY_SET
    assert key.startswith("racy_code=")
    assert data["racy_code"] == SETTLEMENT_TYPES[0].code
    assert data["racy_tier"] == "A"
