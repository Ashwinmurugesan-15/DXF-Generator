"""
Base component definition.

Defines the abstract base class for all DXF components.
"""
class BaseComponent:
    """Base DXF component"""

    def generate_dxf(self, filepath: str):
        """
        Generate DXF file at the given path.
        Must be implemented by all components.
        """
        raise NotImplementedError("generate_dxf() must be implemented by subclasses")
