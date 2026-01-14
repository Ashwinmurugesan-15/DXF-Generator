import pytest

from dxf_generator.exceptions.base import DXFValidationError
from dxf_generator.exceptions.schema import IBeamSchemaError, ColumnSchemaError
from dxf_generator.exceptions.geometry import IBeamGeometryError, ColumnGeometryError
from dxf_generator.exceptions.assembly import AssemblyError


def test_all_custom_exceptions_inherit_base():
    assert issubclass(IBeamSchemaError, DXFValidationError)
    assert issubclass(ColumnSchemaError, DXFValidationError)
    assert issubclass(IBeamGeometryError, DXFValidationError)
    assert issubclass(ColumnGeometryError, DXFValidationError)
    assert issubclass(AssemblyError, DXFValidationError)


def test_exceptions_are_catchable_as_base():
    with pytest.raises(DXFValidationError):
        raise IBeamGeometryError("bad geometry")

