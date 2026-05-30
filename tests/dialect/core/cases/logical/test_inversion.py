from __future__ import annotations

from typing import TYPE_CHECKING

from pytest import mark

if TYPE_CHECKING:
    from tests.dialect.core.infrastructure.types import (
        TBaseField,
        TConstant,
        TExpectedResult,
    )


@mark.spec("logical", "inversion", "and")
def test_and(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = ~((f("age") > 18) & (f("status") == "active"))
    assert expression.compile() == expected_result


@mark.spec("logical", "inversion", "or")
def test_or(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = ~((f("score") < 0) | (f("score") > 100))
    assert expression.compile() == expected_result


@mark.spec("logical", "inversion", "true")
def test_true(c: TConstant, expected_result: TExpectedResult) -> None:
    assert (~c(True)).compile() == expected_result
    assert (~c.true()).compile() == expected_result


@mark.spec("logical", "inversion", "not_true")
def test_not_true(c: TConstant, expected_result: TExpectedResult) -> None:
    assert (~(~c(True))).compile() == expected_result


@mark.spec("logical", "inversion", "false")
def test_false(c: TConstant, expected_result: TExpectedResult) -> None:
    assert (~c(False)).compile() == expected_result
    assert (~c.false()).compile() == expected_result


@mark.spec("logical", "inversion", "not_false")
def test_not_false(c: TConstant, expected_result: TExpectedResult) -> None:
    assert (~(~c(False))).compile() == expected_result


@mark.spec("logical", "inversion", "like")
def test_like(f: TBaseField, expected_result: TExpectedResult) -> None:
    expr = ~(f("product_name").like("Banana%"))  # type: ignore[attr-defined]

    # Check both the operator and the quoting
    assert expr.compile() == expected_result


@mark.spec("logical", "inversion", "not_like")
def test_not_like(f: TBaseField, expected_result: TExpectedResult) -> None:
    expr = ~(f("sku").not_like("OLD-%"))  # type: ignore[attr-defined]

    # Check both the operator and the quoting
    assert expr.compile() == expected_result


@mark.spec("logical", "inversion", "in")
def test_in(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = ~(f("age").in_([25, 26, 28]))
    assert expression.compile() == expected_result


@mark.spec("logical", "inversion", "not_in")
def test_not_in(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = ~(f("age").not_in([25, 26, 28]))
    assert expression.compile() == expected_result


@mark.spec("logical", "inversion", "equal")
def test_equal(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = ~(f("age") == 25)
    assert expression.compile() == expected_result


@mark.spec("logical", "inversion", "not_equal")
def test_not_equal(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = ~(f("age") != 25)
    assert expression.compile() == expected_result


@mark.spec("logical", "inversion", "greater_than")
def test_greater_than(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = ~(f("age") > 25)
    assert expression.compile() == expected_result


@mark.spec("logical", "inversion", "greater_than_or_equal")
def test_greater_than_or_equal(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = ~(f("age") >= 25)
    assert expression.compile() == expected_result


@mark.spec("logical", "inversion", "less_than")
def test_less_than(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = ~(f("age") < 25)
    assert expression.compile() == expected_result


@mark.spec("logical", "inversion", "less_than_or_equal")
def test_less_than_or_equal(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = ~(f("age") <= 25)
    assert expression.compile() == expected_result
