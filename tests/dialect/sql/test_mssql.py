from datetime import UTC, datetime
from decimal import Decimal

import pytest

from pyphrase.dialect.sql.mssql import C, F


def test_mssql_brackets_and_bit() -> None:
    expr = F("dbo.users.is_active") == C.true()
    assert str(expr) == "[dbo].[users].[is_active] = 1"


def test_mssql_reserved_word() -> None:
    expr = F("order") == "desc"
    assert str(expr) == "[order] = 'desc'"


@pytest.mark.parametrize(
    ["input_time", "expected"],
    [
        (datetime(2000, 1, 2, 3, 4, 5), "[created_at] = '2000-01-02 03:04:05'"),
        (
            datetime(2000, 1, 2, 3, 4, 5, tzinfo=UTC),
            "[created_at] = '2000-01-02 03:04:05+00:00'",
        ),
        (
            datetime(2000, 1, 2, 3, 4, 5, 678000),
            "[created_at] = '2000-01-02 03:04:05.678'",
        ),
        (
            datetime(2000, 1, 2, 3, 4, 5, 67800, tzinfo=UTC),
            "[created_at] = '2000-01-02 03:04:05.067+00:00'",
        ),
    ],
)
def test_handling_datetime(input_time: datetime, expected: str) -> None:
    expr = F("created_at") == input_time
    assert str(expr) == expected


@pytest.mark.parametrize(
    ["cost", "expected"],
    [
        ("124.45", "[cost] = 124.45"),
        ("0", "[cost] = 0"),
        ("0.00", "[cost] = 0.00"),
        ("1.12345", "[cost] = 1.12345"),
        ("12345.67", "[cost] = 12345.67"),
        ("1234", "[cost] = 1234"),
        ("-12345", "[cost] = -12345"),
        ("-1234.6789", "[cost] = -1234.6789"),
    ],
)
def test_handling_decimal(cost: str, expected: str) -> None:
    expr = F("cost") == Decimal(cost)
    assert str(expr) == expected
