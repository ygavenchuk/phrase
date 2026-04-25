"""
Microsoft SQL Server (T-SQL) Dialect Implementation.

Provides support for Transact-SQL syntax. This implementation significantly
diverges from ANSI standards regarding identifier quoting and boolean storage.

Specifics:
    * Quoting: Uses square brackets (`[field]`) for identifiers to handle
      reserved words and multi-part names (e.g., `[dbo].[table]`).
    * Booleans: Renders literals as `1`/`0` for compatibility with the `BIT` data type.
    * Operators: Prefers `<>` for inequality in accordance with T-SQL conventions.
"""

from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar

from phrase.base.factory import ConstantFactory
from phrase.base.operator import BinaryOperator, Operator
from phrase.dialect.sql.common import F as SqlF
from phrase.dialect.sql.common import SQLCompiler, SQLRenderer

if TYPE_CHECKING:
    from collections.abc import Mapping


class MSSQLRenderer(SQLRenderer):
    __slots__ = ()

    _mapping: ClassVar[Mapping[Operator, str]] = MappingProxyType(
        {
            BinaryOperator.EQ: "=",
            BinaryOperator.NE: "<>",
        }
    )

    @staticmethod
    def _render_boolean(value: bool) -> str:
        # MSSQL use 1/0 for boolean literals
        return "1" if value else "0"

    def render_field(self, field: str) -> str:
        # MSSQL standard - brackets
        # the field can be complex (schema.table.column)
        parts = field.split(".")
        return ".".join(f"[{p}]" for p in parts)


class MSSQLCompiler(SQLCompiler):
    __slots__ = ()

    renderer_class = MSSQLRenderer


class F(SqlF):
    """Field factory specialized for PostgreSQL."""

    __slots__ = ()

    _compiler_class = MSSQLCompiler


C = ConstantFactory(compiler_class=MSSQLCompiler)
