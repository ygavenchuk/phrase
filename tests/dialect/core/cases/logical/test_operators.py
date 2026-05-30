from __future__ import annotations

from typing import TYPE_CHECKING

from pytest import mark

if TYPE_CHECKING:
    from tests.dialect.core.infrastructure.types import TBaseField, TExpectedResult


@mark.spec("logical", "operator", "and")
def test_and(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = (f("age") > 25) & (f("status") == "OK")
    assert expression.compile() == expected_result


@mark.spec("logical", "operator", "or")
def test_or(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = (f("age") > 25) | (f("status") == "OK")
    assert expression.compile() == expected_result


@mark.spec("logical", "operator", "precedence")
def test_precedence(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = (f("a") == 1) | (f("b") == 2) & (f("c") == 3)
    assert expression.compile() == expected_result
