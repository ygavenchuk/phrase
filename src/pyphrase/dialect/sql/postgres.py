"""
PostgreSQL Dialect Implementation.

Extends the base SQL infrastructure with features unique to the Postgres
ecosystem. This dialect prioritizes strict type compliance and supports
advanced pattern matching.

Specifics:
    * Quoting: Uses double quotes (`"field"`) for identifiers.
    * Case Sensitivity: Implements `ILIKE` and `NOT ILIKE` operators for
      case-insensitive string matching.
    * Literals: Doubled single quotes (`''`) for string escaping and
      native `TRUE`/`FALSE` boolean constants.
"""

from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar

from pyphrase.base.factory import ConstantFactory
from pyphrase.base.operator import BinaryOperator, Operator
from pyphrase.dialect.sql.common import F as SqlF
from pyphrase.dialect.sql.common import (
    ILikeableMixin,
    ILikeInversionRule,
    SQLCompiler,
    SQLRenderer,
)

if TYPE_CHECKING:
    from collections.abc import Mapping


class PostgresRenderer(SQLRenderer):
    __slots__ = ()

    _mapping: ClassVar[Mapping[Operator, str]] = MappingProxyType(
        {
            BinaryOperator.EQ: "=",
            # Postgres supports both != and <>, but <> is standard
            BinaryOperator.NE: "<>",
        }
    )

    def render_field(self, field: str) -> str:
        # Postgres uses double quotes for identifiers
        return f'"{field}"'


class PostgresCompiler(SQLCompiler):
    __slots__ = ()

    renderer_class = PostgresRenderer
    optimization_rules = (
        *SQLCompiler.optimization_rules,
        ILikeInversionRule,
    )


class F(SqlF, ILikeableMixin[str]):
    """Field factory specialized for PostgreSQL."""

    __slots__ = ()

    _compiler_class = PostgresCompiler


C = ConstantFactory(compiler_class=PostgresCompiler)
