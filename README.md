# type-inspector

Walk a deeply nested pydantic model, type alias or dataclass as if data was already put into it. While pydantic allows you to validate data with a model, type-inspector allows you to validate **operations** on data using a model **before** any data has been passed.

---

<p align="center">
<a href="https://github.com/ovsyanka83/type-inspector/actions?query=workflow%3ATests+event%3Apush+branch%3Amain" target="_blank">
    <img src="https://github.com/Ovsyanka83/type-inspector/actions/workflows/test.yaml/badge.svg?branch=main&event=push" alt="Test">
</a>
<a href="https://codecov.io/gh/ovsyanka83/type-inspector" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/ovsyanka83/type-inspector?color=%2334D058" alt="Coverage">
</a>
<a href="https://pypi.org/project/type-inspector/" target="_blank">
    <img alt="PyPI" src="https://img.shields.io/pypi/v/type-inspector?color=%2334D058&label=pypi%20package" alt="Package version">
</a>
<a href="https://pypi.org/project/type-inspector/" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/type-inspector?color=%2334D058" alt="Supported Python versions">
</a>
</p>

## Installation

```bash
pip install type-inspector
```

## Usage

### Quickstart

Let's pick an inspector for a model and try doing a few operations on it:

```python
from type_inspector import pick_inspector
from pydantic import BaseModel

class NestedModel(BaseModel):
    b: dict[str, int | list[bytes]]

class MyModel(BaseModel):
    a: list[NestedModel]

inspector = pick_inspector(MyModel, ["MyModel"])
result = inspector.a[1].b["hello"][11]
print(result.wrapped) # bytes
```

If you try to access a property or item that cannot exist, an `InspectionError` will be raised.

### Note on notation

This library was originally created to mimic javascript syntax so `Model["a"]["b"]` is the same as Model.a.b. However, this notation is not necessarily correct in terms of python syntax. But it will definitely make sure that the operations you write will work on a JSON object that the model was created for.
