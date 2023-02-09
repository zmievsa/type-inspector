from types import ModuleType


def test_without_pydantic(type_inspector_with_pydantic_not_installed: ModuleType):
    inspector = type_inspector_with_pydantic_not_installed.pick_inspector(list[dict[str, list[bytes]]], [])
    assert inspector[0]["key"][0].wrapped is bytes
