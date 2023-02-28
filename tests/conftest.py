import importlib
from collections.abc import Generator
from types import ModuleType
from typing import Any

import pytest
from pydantic import BaseModel

from type_inspector import Inspector, pick_inspector


class DoubleNestedModel(BaseModel):
    int_field: int


class NestedModel(BaseModel):
    str_field: str
    double_nested_model_field: DoubleNestedModel


class RootModel(BaseModel):
    __root__: str


class Model(BaseModel):
    int_field: int
    list_field: list
    list_of_int_field: list[int]
    nested_model_field: NestedModel
    dict_field: dict
    dict_of_str_nested_model_field: dict[str, NestedModel]
    dict_of_str_int_field: dict[str, int]
    union_str_or_int_field: int | str
    union_list_of_bytes_or_nested_model_field: list[bytes] | NestedModel
    dict_of_int_str_field: dict[int, str]
    any_field: Any
    root_field: RootModel
    str_or_none_field: str | None


@pytest.fixture
def inspector() -> Inspector:
    return pick_inspector(Model, ["Model"])


@pytest.fixture
def type_inspector_with_pydantic_not_installed() -> Generator[ModuleType, None, None]:
    import sys

    import type_inspector

    pydantic = sys.modules["pydantic"]
    sys.modules["pydantic"] = None  # type: ignore # Intentional craziness
    try:
        yield importlib.reload(type_inspector)
    finally:
        sys.modules["pydantic"] = pydantic
