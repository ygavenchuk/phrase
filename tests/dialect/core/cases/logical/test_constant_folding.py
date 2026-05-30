from typing import TYPE_CHECKING

from pytest import mark

if TYPE_CHECKING:
    from tests.dialect.core.infrastructure.types import (
        TBaseField,
        TConstant,
        TExpectedResult,
    )


@mark.spec("logical", "constant_folding", "x_and_true")
def test_x_and_true(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = (f("age") > 18) & True
    assert expression.compile() == expected_result


@mark.spec("logical", "constant_folding", "x_and_false")
def test_x_and_false(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = (f("age") > 18) & False
    assert expression.compile() == expected_result


@mark.spec("logical", "constant_folding", "true_and_x")
def test_true_and_x(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = True & (f("status") == "active")
    assert expression.compile() == expected_result


@mark.spec("logical", "constant_folding", "false_and_x")
def test_false_and_x(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = False & (f("status") == "active")
    assert expression.compile() == expected_result


@mark.spec("logical", "constant_folding", "x_or_true")
def test_x_or_true(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = (f("age") > 18) | True
    assert expression.compile() == expected_result


@mark.spec("logical", "constant_folding", "x_or_false")
def test_x_or_false(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = (f("age") > 18) | False
    assert expression.compile() == expected_result


@mark.spec("logical", "constant_folding", "complex_nested")
def test_complex_nested(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = ((f("a") == 1) & True) | ((f("b") == 2) & False)
    assert expression.compile() == expected_result


@mark.spec("logical", "constant_folding", "with_de_morgan")
def test_with_de_morgan(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = ~((f("a") > 10) & False)
    assert expression.compile() == expected_result


@mark.spec("logical", "constant_folding", "or_true_left")
def test_or_true_left(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = True | (f("status") == "active")
    assert expression.compile() == expected_result


@mark.spec("logical", "constant_folding", "and_true_left")
def test_and_true_left(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = True & (f("status") == "active")
    assert expression.compile() == expected_result


@mark.spec("logical", "constant_folding", "or_false_left")
def test_or_false_left(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = False | (f("status") == "active")
    assert expression.compile() == expected_result


@mark.spec("logical", "constant_folding", "or_true_right")
def test_or_true_right(f: TBaseField, expected_result: TExpectedResult) -> None:
    expression = (f("status") == "active") | True
    assert expression.compile() == expected_result


@mark.spec("logical", "constant_folding", "true_and_true")
def test_true_and_true(c: TConstant, expected_result: TExpectedResult) -> None:
    assert (c(True) & True).compile() == expected_result


@mark.spec("logical", "constant_folding", "true_or_true")
def test_true_or_true(c: TConstant, expected_result: TExpectedResult) -> None:
    assert (c(True) | True).compile() == expected_result


@mark.spec("logical", "constant_folding", "false_and_false")
def test_false_and_false(c: TConstant, expected_result: TExpectedResult) -> None:
    assert (c(False) & False).compile() == expected_result


@mark.spec("logical", "constant_folding", "false_or_false")
def test_false_or_false(c: TConstant, expected_result: TExpectedResult) -> None:
    assert (c(False) | False).compile() == expected_result
