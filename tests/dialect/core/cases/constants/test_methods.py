from __future__ import annotations

from typing import TYPE_CHECKING

from pytest import mark

from pyphrase.base.ast.node import ConstantNode

if TYPE_CHECKING:
    from tests.dialect.core.infrastructure.types import TConstant, TExpectedResult


@mark.spec("constant", "methods", "true")
def test_true(c: TConstant, expected_result: TExpectedResult) -> None:
    expr = c.true()

    # Check the underlying AST node
    assert isinstance(expr.node, ConstantNode)
    assert expr.compile() == expected_result


@mark.spec("constant", "methods", "false")
def test_false(c: TConstant, expected_result: TExpectedResult) -> None:
    expr = c.false()

    # Check the underlying AST node
    assert isinstance(expr.node, ConstantNode)
    assert expr.compile() == expected_result


@mark.spec("constant", "methods", "null")
def test_null(c: TConstant, expected_result: TExpectedResult) -> None:
    expr = c.null()

    # Check the underlying AST node
    assert isinstance(expr.node, ConstantNode)
    assert expr.compile() == expected_result
