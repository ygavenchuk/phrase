from typing import TYPE_CHECKING

from pytest import mark

if TYPE_CHECKING:
    from tests.dialect.core.infrastructure.types import (
        TBaseField,
        TConstant,
        TExpectedResult,
    )


@mark.spec("constant", "expression", "and_true")
def test_field_and_true(
    c: TConstant,
    f: TBaseField,
    expected_result: TExpectedResult,
) -> None:
    expr = (f("status") == "active") & c.true()
    assert expr.compile() == expected_result


@mark.spec("constant", "expression", "is_null")
def test_field_is_null(
    c: TConstant, f: TBaseField, expected_result: TExpectedResult
) -> None:
    expr = f("deleted_at") == c.null()
    assert expr.compile() == expected_result


@mark.spec("constant", "expression", "is_not_null")
def test_field_is_not_null(
    c: TConstant, f: TBaseField, expected_result: TExpectedResult
) -> None:
    expr = f("deleted_at") != c.null()
    assert expr.compile() == expected_result
