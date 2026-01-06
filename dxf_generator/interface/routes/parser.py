from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Depends
import uuid
import os

from dxf_generator.services.dxf_service import DXFService
from pydantic import BaseModel
from .utils import remove_file
from dxf_generator.config.logging_config import logger

router = APIRouter()

class ParseResponse(BaseModel):
    success: bool
    filename: str
    dimensions: dict
    message: str

@router.post("/parse")
async def parse_dxf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    logger.debug(f"Received parse request for file: {file.filename}")
    try:
        temp_filename = f"temp_{uuid.uuid4().hex}_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.debug(f"Saved temporary file for parsing: {temp_filename}")
        try:
            result = DXFService.parse(temp_filename)
            logger.info(f"Successfully parsed DXF: {file.filename} as {result['type']}")
            logger.debug(f"Parsed data: {result['data']}")
            return result
        finally:
            if background_tasks:
                background_tasks.add_task(remove_file, temp_filename)
            else:
                remove_file(temp_filename)
                
    except ValueError as e:
        logger.warning(f"Validation error parsing DXF {file.filename}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error parsing DXF {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
