from typing import TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
    from pyphrase.base.operator import Operator
    from pyphrase.base.types import LiteralValue

TLiteral = TypeVar("TLiteral")


class Renderer[TLiteral](Protocol):
    def render_field(self, field: str) -> str: ...
    def render_operator(self, operator: Operator) -> str: ...
    def render_literal(self, literal: LiteralValue) -> TLiteral: ...
