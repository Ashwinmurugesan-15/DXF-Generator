"""
Centralized file upload validation utilities.
Single responsibility: validate uploaded files before processing.
"""
from fastapi import UploadFile
from dxf_generator.config.env_config import config
from dxf_generator.config.logging_config import logger


class FileValidationError(Exception):
    """Custom exception for file validation failures."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def validate_file_extension(filename: str) -> str:
    """
    Validate file extension against allowed types.
    
    Args:
        filename: Original filename from upload
        
    Returns:
        Validated extension (lowercase with dot)
        
    Raises:
        FileValidationError: If extension is not allowed
    """
    if not filename or "." not in filename:
        raise FileValidationError("Filename must have an extension")
    
    ext = "." + filename.split(".")[-1].lower()
    
    if ext not in config.ALLOWED_UPLOAD_EXTENSIONS:
        raise FileValidationError(
            f"Invalid file type: {ext}. Allowed: {list(config.ALLOWED_UPLOAD_EXTENSIONS)}"
        )
    
    logger.debug(f"File extension validated: {ext}")
    return ext


async def validate_and_save_upload(
    file: UploadFile,
    destination_path: str,
    max_size: int = None
) -> int:
    """
    Stream file to disk while validating size.
    
    Args:
        file: FastAPI UploadFile object
        destination_path: Where to save the file
        max_size: Maximum allowed size in bytes (defaults to config value)
        
    Returns:
        Total bytes written
        
    Raises:
        FileValidationError: If file exceeds size limit
    """
    if max_size is None:
        max_size = config.UPLOAD_MAX_SIZE_BYTES
    
    size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    try:
        with open(destination_path, "wb") as buffer:
            while chunk := await file.read(chunk_size):
                size += len(chunk)
                if size > max_size:
                    raise FileValidationError(
                        f"File size ({size} bytes) exceeds limit of {max_size} bytes ({max_size // (1024*1024)} MB)"
                    )
                buffer.write(chunk)
    except FileValidationError:
        # Clean up partial file on validation failure
        import os
        if os.path.exists(destination_path):
            os.remove(destination_path)
        raise
    
    logger.debug(f"File saved: {destination_path} ({size} bytes)")
    return size


def validate_content_type(content_type: str) -> str:
    """
    Validate file content type (MIME).
    
    Args:
        content_type: MIME type string
        
    Returns:
        Validated content type
        
    Raises:
        FileValidationError: If type is not allowed
    """
    if not content_type:
        return "application/octet-stream" # Default if missing
        
    if content_type not in config.ALLOWED_UPLOAD_MIME_TYPES:
        raise FileValidationError(
            f"Invalid content type: {content_type}. Allowed: {list(config.ALLOWED_UPLOAD_MIME_TYPES)}"
        )
    
    logger.debug(f"Content type validated: {content_type}")
    return content_type


def validate_upload(file: UploadFile) -> None:
    """
    Validate file metadata before processing.
    Checks extension and content-type.
    
    Args:
        file: FastAPI UploadFile object
        
    Raises:
        FileValidationError: If validation fails
    """
    validate_file_extension(file.filename)
    validate_content_type(file.content_type)
