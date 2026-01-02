"""
Column calculations.
Functions for calculating column properties.
"""
def column_area(width, height):
    """
    Calculate the cross-sectional area of a column.
    Args:
        width (float): Width in mm.
        height (float): Height in mm.
    Returns:
        float: Area in mm^2.
    """
    # Calculate area by multiplying width and height
    return width * height
