from collections.abc import Mapping
from typing import TypeAlias

from pyphrase.base.factory import BaseField, ConstantFactory
from pyphrase.dialect.mongodb import TMongoRendered

TBaseField: TypeAlias = type[BaseField[str | TMongoRendered]]
TConstant: TypeAlias = ConstantFactory[str | TMongoRendered]
TExpectedResult: TypeAlias = str | TMongoRendered
TFixtureData: TypeAlias = TExpectedResult | Mapping[str, "TFixtureData"]
