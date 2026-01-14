from dxf_generator.calculations.ibeam_calc import ibeam_area
from dxf_generator.calculations.column_calc import column_area


def test_column_area():
    assert column_area(10, 20) == 200


def test_column_area_allows_negative_values():
    assert column_area(-10, 20) == -200


def test_ibeam_area():
    assert ibeam_area(total_depth=200, flange_width=100, web_thickness=8, flange_thickness=10) == 3440


def test_ibeam_area_zero_web_thickness():
    assert ibeam_area(total_depth=200, flange_width=100, web_thickness=0, flange_thickness=10) == 2000
