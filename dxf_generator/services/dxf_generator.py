"""
DXFGenerator - Handles DXF file generation.
Single Responsibility: Generate DXF content from component data, write to disk.
"""
from dxf_generator.config.logging_config import logger


class DXFGenerator:
    """
    Generates DXF files from component specifications.
    Delegates actual drawing to component's generate_dxf method.
    """
    
    @staticmethod
    def generate(component, filename: str) -> bytes:
        """
        Generate a DXF file from component and read back content.
        
        Args:
            component: Component with generate_dxf(filename) method
            filename: Output file path
            
        Returns:
            Generated DXF file content as bytes
        """
        logger.debug(f"Generating DXF: {filename}")
        logger.debug(f"Component data: {component.data}")
        
        # Delegate to component's generation method
        component.generate_dxf(filename)
        
        # Read back for caching
        with open(filename, 'rb') as f:
            content = f.read()
        
        logger.info(f"Generated DXF: {filename} ({len(content)} bytes)")
        return content
    
    @staticmethod
    def write_content(content: bytes, filename: str) -> None:
        """
        Write cached DXF content to file.
        
        Args:
            content: DXF file content
            filename: Output file path
        """
        with open(filename, 'wb') as f:
            f.write(content)
        logger.debug(f"Wrote cached content to: {filename}")
