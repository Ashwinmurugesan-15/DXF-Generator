import pytest

from dxf_generator.domain.base_component import BaseComponent


def test_base_component_generate_dxf_not_implemented():
    with pytest.raises(NotImplementedError):
        BaseComponent().generate_dxf("x.dxf")
