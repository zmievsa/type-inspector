import contextlib
import dataclasses
import importlib.metadata
import types
from collections.abc import Mapping, Sequence
from types import GenericAlias
from typing import TYPE_CHECKING, Any, NoReturn, get_args, get_origin

from issubclass import issubclass

if TYPE_CHECKING:
    from typing_extensions import Never

__version__ = importlib.metadata.version("type-inspector")
__all__ = ["pick_inspector", "__version__", "InspectionError"]

DEFAULT_ERROR_MSG = "Object is not subscriptable"


class InspectionError(Exception):
    def __init__(self, message: str, address: str, problematic_key: object):
        self.message = message
        self.address = address
        self.problematic_key = problematic_key

        super().__init__(f"{self.message}. Object: {self.address}, Key: {self.problematic_key!r}")


@dataclasses.dataclass(slots=True, frozen=True)
class Inspector:
    wrapped: Any
    address_parts: list[str | int] = dataclasses.field(default_factory=list)

    def __getattr__(self, name: str) -> "Inspector":
        """We do this to mimic the behavior of javascript's dot notation"""
        return self.__getitem__(name)

    def __getitem__(self, key: Any) -> "Inspector":
        self.raise_error(key)

    def new_address(self, key: int | str) -> list[str | int]:
        return self.address_parts + [key]

    def raise_error(self, key: object, error: str = DEFAULT_ERROR_MSG) -> NoReturn:
        raise InspectionError(error, self.address, key)

    def wrap_child(self, obj: Any, new_part_of_address: str | int):
        return pick_inspector(obj, self.new_address(new_part_of_address))

    @property
    def address(self) -> str:
        if len(self.address_parts) == 0:
            return ""
        return str(self.address_parts[0]) + "".join(f"[{part!r}]" for part in self.address_parts[1:])


try:
    import pydantic

    class PydanticModelInspector(Inspector):
        wrapped: type[pydantic.BaseModel]

        def __getitem__(self, key: int | str | object):
            if not isinstance(key, str):
                self.raise_error(key, f"{key!r} is not a valid identifier")
            # Beware of https://github.com/pydantic/pydantic/issues/1112
            for field in self.wrapped.__fields__.values():
                if field.alias == key:
                    schema = field.type_

                    # means that it's a composite field such as list[int] or dict[str, int]
                    if field.sub_fields:
                        return self.wrap_child(field.outer_type_, key)
                    elif isinstance(field.annotation, types.UnionType) and not isinstance(field.type_, types.UnionType):
                        return self.wrap_child(field.annotation, key)
                    return self.wrap_child(schema, key)
            else:
                self.raise_error(key, f"Object has no key {key!r}")

except ImportError:
    pydantic = None


class AnyInspector(Inspector):
    def __getitem__(self, key: str | int) -> "AnyInspector":
        return AnyInspector(Any, self.new_address(key))


class GenericAliasInspector(Inspector):
    wrapped: GenericAlias

    def __getitem__(self, key: int | str | object):
        if issubclass(get_origin(self.wrapped), Mapping):
            if isinstance(key, str):
                return self.wrap_child(get_args(self.wrapped)[1], key)
            else:
                self.raise_error(key, f"Tried to use non-string key on an object that only supports string keys")
        elif (
            isinstance(key, int) and issubclass(get_origin(self.wrapped), Sequence) and len(get_args(self.wrapped)) == 1
        ):
            return self.wrap_child(get_args(self.wrapped)[0], key)
        else:
            self.raise_error(key)


class SequenceInspector(Inspector):
    def __getitem__(self, key: int | object) -> AnyInspector:
        if isinstance(key, int):
            return AnyInspector(Any, self.new_address(key))
        else:
            self.raise_error(key, f"The type `{self.wrapped!r}` does not support non-int key access")


class UnionInspector(Inspector):
    wrapped: types.UnionType

    def __getitem__(self, key: Any):
        for arg in get_args(self.wrapped):
            with contextlib.suppress(TypeError, InspectionError):
                return pick_inspector(arg, self.address_parts).__getattr__(key)
        self.raise_error(key, f"Object has no key {key!r}")


class DictInspector(Inspector):
    def __getitem__(self, key: str | object) -> AnyInspector:
        if isinstance(key, str):
            return AnyInspector(Any, self.new_address(key))
        else:
            self.raise_error(key, f"The type {self.wrapped!r} does not support non-string key access")


def pick_inspector(type_: Any, address: list[str | int] | None = None):
    if address is None:
        address = []
    if type_ is Any:
        return AnyInspector(type_, address)
    elif isinstance(type_, types.UnionType):
        return UnionInspector(type_, address)
    elif isinstance(type_, GenericAlias):
        if issubclass(get_origin(type_), Mapping):
            if not issubclass(get_args(type_)[0], str):
                raise TypeError(f"Schema contains a dict with non-string keys which is invalid")
        return GenericAliasInspector(type_, address)
    elif issubclass(type_, Sequence):
        return SequenceInspector(type_, address)
    elif pydantic is not None and issubclass(type_, pydantic.BaseModel):
        if "__root__" in type_.__fields__:
            return PydanticModelInspector(type_, address).__root__
        else:
            return PydanticModelInspector(type_, address)
    elif isinstance(type_, type) and issubclass(type_, dict):
        return DictInspector(type_, address)
    else:
        return Inspector(type_, address)
