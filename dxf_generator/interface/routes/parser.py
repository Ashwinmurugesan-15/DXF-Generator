from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
import uuid

from dxf_generator.services.dxf_service import DXFService
from pydantic import BaseModel
from .utils import remove_file
from dxf_generator.config.logging_config import logger
from dxf_generator.validators.file_validation import (
    validate_upload,
    validate_and_save_upload,
    FileValidationError
)

router = APIRouter()


class ParseResponse(BaseModel):
    """Response model for DXF parsing endpoint."""
    success: bool
    filename: str
    type: str
    dimensions: dict
    message: str


@router.post("/parse", response_model=ParseResponse)
async def parse_dxf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Parse an uploaded DXF file and extract dimensions.
    
    Validates file type and size before processing.
    Returns structured response matching ParseResponse model.
    """
    logger.debug(f"Received parse request for file: {file.filename}")
    temp_filename = None
    
    try:
        # Step 1: Validate file metadata (extension)
        validate_upload(file)
        
        # Step 2: Stream to disk with size validation
        temp_filename = f"temp_{uuid.uuid4().hex}_{file.filename}"
        size = await validate_and_save_upload(file, temp_filename)
        logger.debug(f"Saved temporary file: {temp_filename} ({size} bytes)")
        
        # Step 3: Parse the DXF
        result = DXFService.parse(temp_filename)
        logger.info(f"Successfully parsed DXF: {file.filename} as {result['type']}")
        
        # Step 4: Return structured response matching ParseResponse
        return ParseResponse(
            success=True,
            filename=file.filename,
            type=result["type"],
            dimensions=result["data"],
            message=f"Successfully parsed {result['type']} from {file.filename}"
        )
        
    except FileValidationError as e:
        logger.warning(f"Validation error for {file.filename}: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
        
    except ValueError as e:
        logger.warning(f"Parse error for {file.filename}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error parsing {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
        
    finally:
        # Always clean up temp file
        if temp_filename:
            if background_tasks:
                background_tasks.add_task(remove_file, temp_filename)
            else:
                remove_file(temp_filename)
