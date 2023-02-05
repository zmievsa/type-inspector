# type-inspector

A library that allows you to walk a deeply nested pydantic model, type alias or dataclass as if data was already put into it. While pydantic allows you to validate data with a model, type-inspector allows you to validate **operations** on data using a model **before** any data has been passed.

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
