"""
MySQL and MariaDB Dialect Implementation.

Tailors SQL rendering for MySQL-compatible engines. This dialect replaces
standard ANSI quoting and boolean representations with MySQL-specific defaults.

Specifics:
    * Quoting: Uses backticks (`` `field` ``) for identifiers.
    * Booleans: Renders boolean literals as integers (`1` for True, `0` for False)
      to ensure compatibility with `TINYINT(1)` columns.
    * Operators: Uses `!=` as the default inequality operator.
"""

from phrase.base.factory import ConstantFactory
from phrase.dialect.sql.common import F as SqlF
from phrase.dialect.sql.common import SQLCompiler, SQLRenderer


class MySQLRenderer(SQLRenderer):
    __slots__ = ()

    @staticmethod
    def _render_boolean(value: bool) -> str:
        # MySQL/MariaDB use 1/0 for boolean literals
        return "1" if value else "0"

    def render_field(self, field: str) -> str:
        # MySQL/MariaDB uses backticks for identifiers
        return f"`{field}`"


class MySQLCompiler(SQLCompiler):
    __slots__ = ()

    renderer_class = MySQLRenderer


class F(SqlF):
    """Field factory specialized for PostgreSQL."""

    __slots__ = ()

    _compiler_class = MySQLCompiler


C = ConstantFactory(compiler_class=MySQLCompiler)
