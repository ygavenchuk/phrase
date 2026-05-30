import importlib
from collections.abc import Mapping
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, cast

import yaml
from _pytest.python import CallSpec2  # noqa: PLC2701
from pytest import FixtureRequest, Function, Mark, fixture

if TYPE_CHECKING:
    from types import ModuleType

    from tests.dialect.core.infrastructure.types import (
        TBaseField,
        TConstant,
        TExpectedResult,
        TFixtureData,
    )

_FIXTURES_DIRECTORY = Path(__file__).parent.parent / "fixtures"
DIALECTS = [p.stem for p in _FIXTURES_DIRECTORY.glob("*.yaml")]


def _decimal_constructor(
    loader: yaml.SafeLoader, node: yaml.ScalarNode | yaml.MappingNode
) -> Decimal:
    return Decimal(loader.construct_scalar(node))


yaml.SafeLoader.add_constructor("!decimal", _decimal_constructor)


@lru_cache
def _load_yaml_data(dialect_name: str) -> Mapping[str, TFixtureData]:
    yaml_path = _FIXTURES_DIRECTORY / f"{dialect_name}.yaml"
    with Path.open(yaml_path, "r", encoding="utf-8") as file:
        return cast("Mapping[str, TFixtureData]", yaml.safe_load(file))


def _get_dialect_name(request: FixtureRequest) -> str:
    match request.node:
        case Function(callspec=CallSpec2(params={"dialect": str(dialect_name)})):
            return dialect_name
        case _:
            raise RuntimeError(
                "The `expected_result` fixture can be used only with `f` or `c`"
            )


def _get_factory_module(request: FixtureRequest) -> ModuleType:
    dialect_name = _get_dialect_name(request)
    yaml_data = _load_yaml_data(dialect_name)
    return importlib.import_module(str(yaml_data["import_path"]))


@fixture(name="f")
def field_factory(request: FixtureRequest) -> TBaseField:
    module = _get_factory_module(request)
    return cast("TBaseField", module.F)


@fixture(name="c")
def constant_factory(request: FixtureRequest) -> TConstant:
    module = _get_factory_module(request)
    return cast("TConstant", module.C)


@fixture
def expected_result(request: FixtureRequest) -> TExpectedResult | None:
    dialect_name = _get_dialect_name(request)

    marker = request.node.get_closest_marker("spec")
    match marker:
        case Mark(args=tuple(base_keys)):
            keys = list(base_keys)
        case _:
            raise RuntimeError(
                "Test using `expected_result` must be decorated with `@mark.spec(...)`"
            )

    match getattr(request.node, "callspec", None) and request.node.callspec.params:
        case {"value_type": str(dynamic_key)}:
            keys.append(dynamic_key)
        case _:
            pass  # there's no extra parametrization, let's use basic keys

    yaml_data = _load_yaml_data(dialect_name)
    current_node: TFixtureData = yaml_data.get("cases", {})

    for key in keys:
        match current_node:
            case Mapping():
                current_node = current_node.get(key)
            case _:
                raise KeyError(
                    f"Cannot find key {key!r} because the node above isn't a dictionary"
                )

    return current_node
