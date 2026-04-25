from datetime import UTC, datetime
from decimal import Decimal

import pytest

from phrase.dialect.sql.qgis import C, F


def test_qgis_basic_comparison() -> None:
    """
    Check basic field-to-value comparison with QGIS double-quoting for fields.
    """
    expr = F("height") > 100

    assert str(expr) == '"height" > 100'


def test_qgis_string_escaping() -> None:
    """
    Check string literal rendering and single quote escaping in QGIS.
    """
    expr = F("city") == "O'Hara"
    assert str(expr) == "\"city\" = 'O''Hara'"


def test_qgis_null_logic() -> None:
    """
    Check NULL handling in QGIS expressions.
    """
    expr = F("deleted_at") != C.null()

    # In QGIS, both "IS NOT NULL" and "<> NULL" can be valid depending on implementation,
    # but based on standard SQL-like expression engine:
    assert str(expr) == '"deleted_at" IS NOT NULL'


def test_qgis_complex_expression() -> None:
    """
    Check complex logic with QGIS formatting (double quotes and AND/OR).
    """
    expr = (F("age") >= 18) & (F("status") == "active")

    assert str(expr) == '("age" >= 18) AND ("status" = \'active\')'


def test_qgis_not_optimization() -> None:
    """
    Check if NOT expression is optimized or correctly wrapped.
    """
    expr = ~(F("type") == "forest")

    # Simple NOT optimization: NOT(x = y) -> x != y
    assert str(expr) == "\"type\" != 'forest'"


def test_qgis_in_operator() -> None:
    """
    Check IN operator for QGIS.
    """
    expr = F("zone").in_(["A", "B", "C"])

    expected = "\"zone\" IN ('A', 'B', 'C')"
    assert str(expr) == expected


def test_qgis_ilike_operator_rendering() -> None:
    """
    Test that the Postgres-specific `ILIKE` operator renders correctly.
    """
    assert str(F("username").ilike("admin%")) == "\"username\" ILIKE 'admin%'"
    assert str(F("username").not_ilike("admin%")) == "\"username\" NOT ILIKE 'admin%'"


def test_qgis_not_ilike_inversion() -> None:
    """
    Test that `NOT (field ILIKE pattern)` is optimized to `NOT ILIKE`.
    """
    expr = ~(F("email").ilike("%@GMAIL.COM"))
    assert str(expr) == "\"email\" NOT ILIKE '%@GMAIL.COM'"

    expr = ~(F("email").not_ilike("%@GMAIL.COM"))
    assert str(expr) == "\"email\" ILIKE '%@GMAIL.COM'"


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
