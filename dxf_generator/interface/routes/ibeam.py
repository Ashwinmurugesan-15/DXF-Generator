import os
from fastapi import APIRouter, HTTPException, BackgroundTasks, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import uuid
import zipfile

from dxf_generator.domain.ibeam import IBeam
from dxf_generator.services.dxf_service import DXFService
from dxf_generator.exceptions.base import DXFValidationError
from dxf_generator.config.system_limits import MAX_BATCH_SIZE
from dxf_generator.config.logging_config import logger
from .utils import remove_file, remove_files

router = APIRouter()

class IBeamRequest(BaseModel):
    total_depth: float
    flange_width: float
    web_thickness: float
    flange_thickness: float
    length: float = 1000.0

class BatchIBeamRequest(BaseModel):
    items: List[IBeamRequest]

@router.post("/ibeam")
async def generate_ibeam(request: IBeamRequest, background_tasks: BackgroundTasks):
    filename = None
    try:
        logger.info(f"Generating single I-Beam: {request.total_depth}x{request.flange_width}")
        ibeam = IBeam(
            request.total_depth, 
            request.flange_width, 
            request.web_thickness, 
            request.flange_thickness
        )
        filename = f"ibeam_{uuid.uuid4().hex[:8]}_{int(request.total_depth)}x{int(request.flange_width)}.dxf"
        display_name = f"ibeam_{int(request.total_depth)}x{int(request.flange_width)}.dxf"
        
        # Use cached generation
        content = DXFService.save_cached(ibeam, filename)
        
        # If it was a cache hit, the file might not exist or be the same one
        # but save_cached handles the generation/retrieval.
        # We can return the bytes directly as a Response to be fast
        
        # We still need to clean up the file if it was just created
        if os.path.exists(filename):
            background_tasks.add_task(remove_file, filename)
            
        return Response(
            content=content,
            media_type="application/dxf",
            headers={
                "Content-Disposition": f'attachment; filename="{display_name}"'
            }
        )
            
    except DXFValidationError as e:
        logger.warning(f"Validation error generating I-Beam: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating I-Beam: {str(e)}", exc_info=True)
        if filename and os.path.exists(filename):
            remove_file(filename)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@router.post("/ibeam/batch")
async def generate_ibeam_batch(request: BatchIBeamRequest, background_tasks: BackgroundTasks):
    logger.info(f"Generating batch of {len(request.items)} I-Beams")
    if len(request.items) > MAX_BATCH_SIZE:
        logger.warning(f"Batch size {len(request.items)} exceeds limit {MAX_BATCH_SIZE}")
        raise HTTPException(
            status_code=400, 
            detail=f"Batch size exceeds maximum limit of {MAX_BATCH_SIZE} items"
        )
    
    filenames = []
    try:
        components = []
        disk_filenames = []
        
        for i, item in enumerate(request.items):
            ibeam = IBeam(item.total_depth, item.flange_width, item.web_thickness, item.flange_thickness)
            unique_id = uuid.uuid4().hex[:8]
            filename = f"ibeam_{unique_id}_{i+1}_{int(item.total_depth)}x{int(item.flange_width)}.dxf"
            display_name = f"ibeam_{i+1}_{int(item.total_depth)}x{int(item.flange_width)}.dxf"
            
            components.append(ibeam)
            disk_filenames.append(filename)
            filenames.append((filename, display_name))
        
        DXFService.save_batch(components, disk_filenames)
        
        zip_filename = f"ibeams_batch_{uuid.uuid4().hex[:8]}.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for f, d_name in filenames:
                zipf.write(f, arcname=d_name)
        
        disk_paths = [f[0] for f in filenames]
        background_tasks.add_task(remove_files, disk_paths + [zip_filename])
        logger.info(f"Successfully generated batch zip: {zip_filename}")
        return FileResponse(path=zip_filename, filename="ibeams_batch.zip", media_type="application/zip")
    except Exception as e:
        logger.error(f"Error in batch I-Beam generation: {str(e)}", exc_info=True)
        disk_paths = [f[0] if isinstance(f, tuple) else f for f in filenames]
        remove_files(disk_paths)
        raise HTTPException(status_code=500, detail=str(e))
