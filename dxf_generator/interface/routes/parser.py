from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Depends
import uuid
import os

from dxf_generator.services.dxf_service import DXFService
from pydantic import BaseModel
from .utils import remove_file

router = APIRouter()

class ParseResponse(BaseModel):
    success: bool
    filename: str
    dimensions: dict
    message: str

@router.post("/parse")
async def parse_dxf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    try:
        temp_filename = f"temp_{uuid.uuid4().hex}_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            result = DXFService.parse(temp_filename)
            return result
        finally:
            if background_tasks:
                background_tasks.add_task(remove_file, temp_filename)
            else:
                remove_file(temp_filename)
                
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
