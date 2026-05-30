from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
    from pyphrase.base.operator import Operator
    from pyphrase.base.types import LiteralValue


__all__ = ("Renderer",)


TLiteral_co = TypeVar("TLiteral_co", covariant=True)


class Renderer(Protocol[TLiteral_co]):
    def render_field(self, field: str) -> str: ...
    def render_operator(self, operator: Operator) -> str: ...
    def render_literal(self, literal: LiteralValue) -> TLiteral_co: ...
