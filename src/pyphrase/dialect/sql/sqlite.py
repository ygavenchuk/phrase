"""
SQLite Dialect Implementation.

This module adapts the generic SQL renderer for SQLite-specific syntax.
Key characteristics include double-quote identifier quoting and standard
ANSI literal rendering. It serves as a lightweight implementation for
local file-based database systems.

Specifics:
    * Quoting: Uses double quotes (`"field"`) for identifiers.
    * Booleans: Supports standard `TRUE`/`FALSE` (SQLite 3.23.0+)
"""

from pyphrase.dialect.sql.common import C, F

__all__ = ("C", "F")
