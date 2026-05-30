from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pytest import mark

if TYPE_CHECKING:
    from pyphrase.base.types import CollectionValue
    from tests.dialect.core.infrastructure.types import TBaseField, TExpectedResult


@mark.spec(
    "in",
    variant={
        "integer": ("age", [25, 26, 28]),
        "float": ("score", [25.5, 26.67, 28.893]),
        "string": ("name", ["lorem", "ipsum"]),
        "datetime": (
            "start_time",
            [
                datetime(2000, 1, 2, 3, 4, 5),
                datetime(2000, 12, 23, 22, 45, 55),
            ],
        ),
        "decimal": ("price", [Decimal("25.25"), Decimal("26.67")]),
    },
)
def test_in(
    f: TBaseField,
    expected_result: TExpectedResult,
    field_name: str,
    value: CollectionValue,
) -> None:
    expression = f(field_name).in_(value)
    assert expression.compile() == expected_result


@mark.spec(
    "not_in",
    variant={
        "integer": ("age", [25, 26, 28]),
        "float": ("score", [25.5, 26.67, 28.893]),
        "string": ("name", ["lorem", "ipsum"]),
        "datetime": (
            "start_time",
            [
                datetime(2000, 1, 2, 3, 4, 5),
                datetime(2000, 12, 23, 22, 45, 55),
            ],
        ),
        "decimal": ("price", [Decimal("25.25"), Decimal("26.67")]),
    },
)
def test_not_in(
    f: TBaseField,
    expected_result: TExpectedResult,
    field_name: str,
    value: CollectionValue,
) -> None:
    expression = f(field_name).not_in(value)
    assert expression.compile() == expected_result
