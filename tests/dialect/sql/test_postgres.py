from datetime import UTC, datetime
from decimal import Decimal

import pytest

from pyphrase.base.ast.node import ConstantNode
from pyphrase.dialect.sql.postgres import C, F


def test_pg_ilike_operator_rendering() -> None:
    """
    Test that the Postgres-specific `ILIKE` operator renders correctly.
    """
    assert str(F("username").ilike("admin%")) == "\"username\" ILIKE 'admin%'"
    assert str(F("username").not_ilike("admin%")) == "\"username\" NOT ILIKE 'admin%'"


def test_pg_not_ilike_inversion() -> None:
    """
    Test that `NOT (field ILIKE pattern)` is optimized to `NOT ILIKE`.
    """
    expr = ~(F("email").ilike("%@GMAIL.COM"))
    assert str(expr) == "\"email\" NOT ILIKE '%@GMAIL.COM'"

    expr = ~(F("email").not_ilike("%@GMAIL.COM"))
    assert str(expr) == "\"email\" ILIKE '%@GMAIL.COM'"


def test_pg_like_operator_rendering() -> None:
    """
    Test that the `LIKE` operator renders correctly.
    """
    expr = F("username").like("admin%")
    assert str(expr) == "\"username\" LIKE 'admin%'"

    expr = F("username").not_like("admin%")
    assert str(expr) == "\"username\" NOT LIKE 'admin%'"


def test_pg_not_like_inversion() -> None:
    """
    Test that `NOT (field LIKE pattern)` is optimized to `NOT LIKE`.
    """
    expr = ~(F("email").like("%@GMAIL.COM"))
    assert str(expr) == "\"email\" NOT LIKE '%@GMAIL.COM'"

    expr = ~(F("email").not_like("%@GMAIL.COM"))
    assert str(expr) == "\"email\" LIKE '%@GMAIL.COM'"


def test_pg_inequality_standard() -> None:
    """
    Verify that Postgres uses the chosen inequality operator (e.g., `<>`).
    """
    # If render_operator maps NE to <>, check for that
    assert str(F("status") != "deleted") == "\"status\" <> 'deleted'"
    assert str(F("status") != 42) == '"status" <> 42'
    assert str(F("status") != True) == '"status" <> TRUE'  # noqa: E712
    assert str(F("status") != C.true()) == '"status" <> TRUE'
    assert str(F("status") != False) == '"status" <> FALSE'  # noqa: E712
    assert str(F("status") != C.false()) == '"status" <> FALSE'


def test_pg_boolean_literal_rendering() -> None:
    """
    Ensure boolean values render as TRUE/FALSE keywords in Postgres.
    """
    expr = F("is_verified") == C.true()

    assert str(expr) == '"is_verified" = TRUE'


def test_pg_complex_ilike_and_null() -> None:
    """
    Test combination of ILIKE and NULL checks for Postgres.
    """
    expr = (F("tags").ilike("%python%")) & (F("deleted_at") == C.null())

    expected = '("tags" ILIKE \'%python%\') AND ("deleted_at" IS NULL)'
    assert str(expr) == expected


def test_pg_string_escaping() -> None:
    """
    Verify that string literals are properly escaped for Postgres.
    """
    expr = F("name") == "O'Reilly"

    # Single quotes must be doubled: 'O''Reilly'
    assert str(expr) == "\"name\" = 'O''Reilly'"


def test_pg_not_in_optimization() -> None:
    """
    Test that `NOT (field IN (values))` is optimized to `field NOT IN (values)`.
    """
    expr = ~(F("status").in_(["deleted", "banned"]))

    # InversionRule should handle NOT + IN -> NOT IN
    assert str(expr) == "\"status\" NOT IN ('deleted', 'banned')"


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
        (datetime(2000, 1, 2, 3, 4, 5), "\"created_at\" = '2000-01-02 03:04:05'"),
        (
            datetime(2000, 1, 2, 3, 4, 5, tzinfo=UTC),
            "\"created_at\" = '2000-01-02 03:04:05+00:00'",
        ),
        (
            datetime(2000, 1, 2, 3, 4, 5, 678000),
            "\"created_at\" = '2000-01-02 03:04:05.678'",
        ),
        (
            datetime(2000, 1, 2, 3, 4, 5, 67800, tzinfo=UTC),
            "\"created_at\" = '2000-01-02 03:04:05.067+00:00'",
        ),
    ],
)
def test_handling_datetime(input_time: datetime, expected: str) -> None:
    expr = F("created_at") == input_time
    assert str(expr) == expected


@pytest.mark.parametrize(
    ["cost", "expected"],
    [
        ("124.45", '"cost" = 124.45'),
        ("0", '"cost" = 0'),
        ("0.00", '"cost" = 0.00'),
        ("1.12345", '"cost" = 1.12345'),
        ("12345.67", '"cost" = 12345.67'),
        ("1234", '"cost" = 1234'),
        ("-12345", '"cost" = -12345'),
        ("-1234.6789", '"cost" = -1234.6789'),
    ],
)
def test_handling_decimal(cost: str, expected: str) -> None:
    expr = F("cost") == Decimal(cost)
    assert str(expr) == expected
