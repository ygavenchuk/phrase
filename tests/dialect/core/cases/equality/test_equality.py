from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pytest import mark

if TYPE_CHECKING:
    from pyphrase.base.types import LiteralValue
    from tests.dialect.core.infrastructure.types import TBaseField, TExpectedResult


@mark.spec(
    "equality",
    "equal",
    variant={
        "boolean": ("status", True),
        "integer": ("age", 25),
        "float": ("length", 25.5678),
        "string": ("name", "John"),
        "string_with_escaping": ("name", "O'Reilly"),
        "datetime": ("created_at", datetime(2000, 1, 2, 3, 4, 5)),
        "datetime_with_timezone": (
            "created_at",
            datetime(2000, 1, 2, 13, 4, 5, 678901, tzinfo=UTC),
        ),
        "decimal": ("price", Decimal("25.25")),
        "none_value": ("status", None),
    },
)
def test_equal(
    f: TBaseField, expected_result: TExpectedResult, field_name: str, value: LiteralValue
) -> None:
    expression = f(field_name) == value
    assert expression.compile() == expected_result


@mark.spec(
    "equality",
    "not_equal",
    variant={
        "boolean": ("status", True),
        "integer": ("age", 25),
        "float": ("length", 25.5678),
        "string": ("name", "John"),
        "string_with_escaping": ("name", "O'Reilly"),
        "datetime": ("created_at", datetime(2000, 1, 2, 3, 4, 5)),
        "datetime_with_timezone": (
            "created_at",
            datetime(2000, 1, 2, 13, 4, 5, 678901, tzinfo=UTC),
        ),
        "decimal": ("price", Decimal("25.25")),
        "none_value": ("status", None),
    },
)
def test_not_equal(
    f: TBaseField, expected_result: TExpectedResult, field_name: str, value: LiteralValue
) -> None:
    expression = f(field_name) != value
    assert expression.compile() == expected_result


@mark.spec(
    "equality",
    "greater_than",
    variant={
        "integer": ("age", 25),
        "float": ("length", 25.5678),
        "datetime": ("created_at", datetime(2000, 1, 2, 3, 4, 5)),
        "datetime_with_timezone": (
            "created_at",
            datetime(2000, 1, 2, 13, 4, 5, 678901, tzinfo=UTC),
        ),
        "decimal": ("price", Decimal("25.25")),
    },
)
def test_greater_than(
    f: TBaseField, expected_result: TExpectedResult, field_name: str, value: LiteralValue
) -> None:
    expression = f(field_name) > value
    assert expression.compile() == expected_result


@mark.spec(
    "equality",
    "greater_than_or_equal",
    variant={
        "integer": ("age", 25),
        "float": ("length", 25.5678),
        "datetime": ("created_at", datetime(2000, 1, 2, 3, 4, 5)),
        "datetime_with_timezone": (
            "created_at",
            datetime(2000, 1, 2, 13, 4, 5, 678901, tzinfo=UTC),
        ),
        "decimal": ("price", Decimal("25.25")),
    },
)
def test_greater_than_or_equal(
    f: TBaseField, expected_result: TExpectedResult, field_name: str, value: LiteralValue
) -> None:
    expression = f(field_name) >= value
    assert expression.compile() == expected_result


@mark.spec(
    "equality",
    "less_than",
    variant={
        "integer": ("age", 200),
        "float": ("length", 25.5678),
        "datetime": ("created_at", datetime(2000, 1, 2, 3, 4, 5)),
        "datetime_with_timezone": (
            "created_at",
            datetime(2000, 1, 2, 13, 4, 5, 678901, tzinfo=UTC),
        ),
        "decimal": ("price", Decimal("25.25")),
    },
)
def test_less_than(
    f: TBaseField, expected_result: TExpectedResult, field_name: str, value: LiteralValue
) -> None:
    expression = f(field_name) < value
    assert expression.compile() == expected_result


@mark.spec(
    "equality",
    "less_than_or_equal",
    variant={
        "integer": ("age", 100),
        "float": ("length", 25.5678),
        "datetime": ("created_at", datetime(2000, 1, 2, 3, 4, 5)),
        "datetime_with_timezone": (
            "created_at",
            datetime(2000, 1, 2, 13, 4, 5, 678901, tzinfo=UTC),
        ),
        "decimal": ("price", Decimal("25.25")),
    },
)
def test_less_than_or_equal(
    f: TBaseField, expected_result: TExpectedResult, field_name: str, value: LiteralValue
) -> None:
    expression = f(field_name) <= value
    assert expression.compile() == expected_result
