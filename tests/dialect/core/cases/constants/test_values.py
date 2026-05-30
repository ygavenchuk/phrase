from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pytest import mark

from pyphrase.base.ast.node import ConstantNode

if TYPE_CHECKING:
    from pyphrase.base.types import Scalar
    from tests.dialect.core.infrastructure.types import TConstant, TExpectedResult


@mark.spec(
    "constant",
    "values",
    variant={
        "integer": 25,
        "float": 25.5678,
        "string": "lorem ipsum",
        "datetime": datetime(2000, 1, 2, 3, 4, 5),
        "datetime_with_timezone": datetime(2000, 1, 2, 13, 4, 5, 678901, tzinfo=UTC),
        "decimal": Decimal("25.25"),
        "none_value": None,
    },
)
def test_values(c: TConstant, expected_result: TExpectedResult, value: Scalar) -> None:
    expr = c(value)
    assert isinstance(expr.node, ConstantNode)
    assert expr.compile() == expected_result
