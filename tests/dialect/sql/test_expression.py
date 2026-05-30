import pytest

from pyphrase.dialect.sql.common import F


def test_non_expression_operands() -> None:
    # Checks that we cannot apply a logical operator to a non-expression thing
    with pytest.raises(TypeError):
        # attempt to use "AND" between expression and a regular number
        _ = (F("a") == 1) & 123

    with pytest.raises(TypeError):
        # attempt to use "AND" between expression and a regular number
        _ = (F("a") == 1) | 123


def test_between_operator() -> None:
    assert str(F("age").between(18, 30)) == '("age" >= 18) AND ("age" <= 30)'
