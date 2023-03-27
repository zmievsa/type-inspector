import importlib
from types import ModuleType
from typing import Any

import pytest

from type_inspector import (
    AnyInspector,
    InspectionError,
    Inspector,
    UnionInspector,
    pick_inspector,
)


def test_getattr_of_unsubscriptable_type(inspector: Inspector) -> None:
    with pytest.raises(InspectionError):
        assert inspector.int_field.hello


def test_getitem_of_unsubscriptable_type(inspector: Inspector) -> None:
    with pytest.raises(InspectionError):
        assert inspector["int_field"]["hello"]


def test_getitem_of_dict_with_int_key(inspector: Inspector) -> None:
    with pytest.raises(InspectionError):
        inspector.dict_of_str_int_field[0]


def test_getitem_of_any_list_with_str_key(inspector: Inspector) -> None:
    with pytest.raises(InspectionError):
        inspector.list_field["hewwo"]


def test_getitem_of_generic_list_with_str_key(inspector: Inspector) -> None:
    with pytest.raises(InspectionError):
        inspector.list_of_int_field["hewwo"]


def test_getitem_of_union_not_found(inspector: Inspector) -> None:
    with pytest.raises(InspectionError):
        inspector.union_str_or_int_field.hewwo


def test_getitem_of_pydantic_with_non_str_key(inspector: Inspector) -> None:
    with pytest.raises(InspectionError):
        inspector[1]


def test_getitem_of_pydantic_with_non_existing_key(inspector: Inspector) -> None:
    with pytest.raises(InspectionError):
        inspector.hewwo_darkness


def test_getitem_of_invalid_pydantic_field(inspector: Inspector) -> None:
    with pytest.raises(TypeError):
        inspector.dict_of_int_str_field


def test_root_models(inspector: Inspector) -> None:
    assert inspector.root_field.wrapped is str


def test_optional_field(inspector: Inspector) -> None:
    assert isinstance(inspector.str_or_none_field, UnionInspector)
    assert inspector.str_or_none_field.wrapped == str | None


def test_deep_path(inspector: Inspector) -> None:
    assert inspector.dict_of_str_nested_model_field["key"].double_nested_model_field.int_field.wrapped is int


def test_getitem_of_union(inspector: Inspector) -> None:
    assert inspector.union_list_of_bytes_or_nested_model_field[2].wrapped is bytes
    assert inspector.union_list_of_bytes_or_nested_model_field.str_field.wrapped is str


def test_union(inspector: Inspector) -> None:
    inspector = inspector.list_field[83]
    assert type(inspector) is AnyInspector
    assert inspector.wrapped is Any


def test_empty_address() -> None:
    assert Inspector(int).address == ""


def test_any(inspector: Inspector) -> None:
    assert inspector.any_field["hello"].darkness[0].my[1].old["friend"].wrapped is Any


def test_empty_inspector():
    inspector = pick_inspector(int)
    assert inspector.address == ""
    assert isinstance(inspector, Inspector)
    assert inspector.wrapped is int


def test_dict_without_annotations():
    inspector = pick_inspector(dict)
    assert inspector.hello.darkness[0].my[1].old["friend"].wrapped is Any


def test_dict_access_with_int():
    inspector = pick_inspector(dict)
    with pytest.raises(InspectionError):
        inspector[0]


def test_list_without_annotations():
    inspector = pick_inspector(list)
    assert inspector[0].hello.darkness[0].my[1].old["friend"].wrapped is Any


def test_list_access_with_attr():
    inspector = pick_inspector(list)
    with pytest.raises(InspectionError):
        inspector.hewwo
