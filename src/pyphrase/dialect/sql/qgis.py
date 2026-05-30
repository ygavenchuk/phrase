"""
QGIS Expression Dialect
=======================

This module provides a compiler and renderer for generating QGIS Expressions.
QGIS Expressions are a SQL-like language used within the QGIS desktop application
for filtering features, calculating field values, and defining symbology.

While the syntax closely resembles standard SQL, it has several key differences:
* Fields are strictly enclosed in double quotes: `"field_name"`
* String literals are strictly enclosed in single quotes: `'value'`

"""

from pyphrase.base.factory import ConstantFactory
from pyphrase.dialect.sql.common import F as SqlF
from pyphrase.dialect.sql.common import (
    ILikeableMixin,
    ILikeInversionRule,
    SQLCompiler,
    SQLRenderer,
)

__all__ = ("C", "F")


class QgisCompiler(SQLCompiler):
    __slots__ = ()

    renderer_class = SQLRenderer
    optimization_rules = (
        *SQLCompiler.optimization_rules,
        ILikeInversionRule,
    )


class F(SqlF, ILikeableMixin[str]):
    """Field factory specialized for QGIS."""

    __slots__ = ()

    _compiler_class = QgisCompiler


C = ConstantFactory(compiler_class=QgisCompiler)
