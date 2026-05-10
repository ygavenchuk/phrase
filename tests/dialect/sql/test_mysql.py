from datetime import UTC, datetime
from decimal import Decimal

import pytest

from pyphrase.base.ast.node import ConstantNode
from pyphrase.dialect.sql.mysql import C, F


def test_mysql_field_quoting() -> None:
    """
    Verify that MySQL uses backticks (`) for field names.
    """
    expr = F("user_role") == "admin"
    assert str(expr) == "`user_role` = 'admin'"


def test_mysql_boolean_rendering() -> None:
    """
    Verify that MySQL renders booleans as 1 and 0.
    """
    # Test True
    expr_true = F("is_active") == C.true()
    assert str(expr_true) == "`is_active` = 1"

    # Test False
    expr_false = F("is_deleted") == C.false()
    assert str(expr_false) == "`is_deleted` = 0"


def test_mysql_null_optimization_integration() -> None:
    """
    Ensure NullOptimizationRule works with MySQL backticks.
    """
    # `f_my("deleted_at") == None or c_my.null()`
    expr = F("deleted_at") == C.null()

    # Should use IS NULL and backticks
    assert str(expr) == "`deleted_at` IS NULL"


def test_mysql_in_operator_with_backticks() -> None:
    """
    Test IN operator rendering for MySQL.
    """
    expr = F("status").in_(["active", "pending"])
    assert str(expr) == "`status` IN ('active', 'pending')"


def test_mysql_complex_expression() -> None:
    """
    Verify a complex expression with backticks, numbers, and strings.
    """
    expr = (F("age") >= 18) & (F("name").like("J%"))
    assert str(expr) == "(`age` >= 18) AND (`name` LIKE 'J%')"

    expr = (F("age") >= 18) & ~(F("name").like("J%"))
    assert str(expr) == "(`age` >= 18) AND (`name` NOT LIKE 'J%')"

    expr = (F("age") >= 18) & ~(F("name").not_like("J%"))
    assert str(expr) == "(`age` >= 18) AND (`name` LIKE 'J%')"


def test_render_null_literal() -> None:
    """
    Test that `SQLiteRenderer` correctly renders NULL literals.
    """
    expr = C.null()

    assert isinstance(expr.node, ConstantNode)
    assert expr.node.value is None

    assert str(expr) == "NULL"


@pytest.mark.parametrize(
    ["input_time", "expected"],
    [
        (datetime(2000, 1, 2, 3, 4, 5), "`created_at` = '2000-01-02 03:04:05'"),
        (
            datetime(2000, 1, 2, 3, 4, 5, tzinfo=UTC),
            "`created_at` = '2000-01-02 03:04:05+00:00'",
        ),
        (
            datetime(2000, 1, 2, 3, 4, 5, 678000),
            "`created_at` = '2000-01-02 03:04:05.678'",
        ),
        (
            datetime(2000, 1, 2, 3, 4, 5, 67800, tzinfo=UTC),
            "`created_at` = '2000-01-02 03:04:05.067+00:00'",
        ),
    ],
)
def test_handling_datetime(input_time: datetime, expected: str) -> None:
    expr = F("created_at") == input_time
    assert str(expr) == expected


@pytest.mark.parametrize(
    ["cost", "expected"],
    [
        ("124.45", "`cost` = 124.45"),
        ("0", "`cost` = 0"),
        ("0.00", "`cost` = 0.00"),
        ("1.12345", "`cost` = 1.12345"),
        ("12345.67", "`cost` = 12345.67"),
        ("1234", "`cost` = 1234"),
        ("-12345", "`cost` = -12345"),
        ("-1234.6789", "`cost` = -1234.6789"),
    ],
)
def test_handling_decimal(cost: str, expected: str) -> None:
    expr = F("cost") == Decimal(cost)
    assert str(expr) == expected
