"""
Unit tests for Column Validator.
"""
from dxf_generator.validators.column_validator import ColumnValidator

def test_valid_column():
    """
    Test validation of a column with valid dimensions.
    """
    ColumnValidator.validate({
        "width": 300,
        "height": 3000
    })
