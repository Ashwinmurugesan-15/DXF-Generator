"""
I-Beam calculations.
Functions for calculating I-Beam properties.
"""
def ibeam_area(total_depth, flange_width, web_thickness, flange_thickness):
    """
    Calculate the cross-sectional area of an I-Beam.
    Args:
        total_depth (float): Total depth in mm.
        flange_width (float): Flange width in mm.
        web_thickness (float): Web thickness in mm.
        flange_thickness (float): Flange thickness in mm.
    Returns:
        float: Area in mm^2.
    """
    # Area = (2 * flange_area) + web_area
    # web_height = total_depth - (2 * flange_thickness)
    flange_area = flange_width * flange_thickness
    web_area = (total_depth - 2 * flange_thickness) * web_thickness
    return (2 * flange_area) + web_area
