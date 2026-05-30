from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from typing import Protocol, TypeAlias, runtime_checkable

__all__ = ("CollectionValue", "LiteralValue", "Scalar", "TextualType")


@runtime_checkable
class TextualType(Protocol):
    """
    Protocol that checks whether the object has its own implementation of the __str__,
    that is not inherited from the version from basic `object`
    """

    def __str__(self) -> str: ...

    @classmethod
    def __subclasshook__(cls, c: type) -> bool:
        if cls is TextualType:
            str_method = getattr(c, "__str__", None)

            return str_method is not object.__str__

        raise NotImplementedError


Scalar: TypeAlias = str | int | float | TextualType | datetime | Decimal | None
CollectionValue: TypeAlias = Sequence[Scalar]
LiteralValue: TypeAlias = Scalar | CollectionValue
