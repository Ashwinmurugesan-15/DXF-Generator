import os
from fastapi import APIRouter, HTTPException, BackgroundTasks, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import uuid
import zipfile
import hashlib

from dxf_generator.domain.column import Column
from dxf_generator.services.dxf_service import DXFService
from dxf_generator.exceptions.base import DXFValidationError
from dxf_generator.config.system_limits import MAX_BATCH_SIZE
from dxf_generator.config.logging_config import logger
from .utils import remove_file, remove_files

router = APIRouter()

class ColumnRequest(BaseModel):
    width: float
    height: float

class BatchColumnRequest(BaseModel):
    items: List[ColumnRequest]

@router.post("/column")
async def generate_column(request: ColumnRequest, background_tasks: BackgroundTasks):
    temp_filename = None
    logger.debug(f"Received Column generation request: {request.dict()}")
    try:
        column = Column(request.width, request.height)
        
        # Check cache first to avoid unnecessary UUID generation and disk prep
        cache_key = DXFService.get_cache_key(column)
        is_cached = cache_key in DXFService._generation_cache
        
        # Include a short hash in the filename for uniqueness and stability
        short_hash = hashlib.md5(cache_key.encode()).hexdigest()[:6]
        display_name = f"column_{int(request.width)}x{int(request.height)}_{short_hash}.dxf"
        
        # Use cached generation (internally logs hit/miss)
        # We pass a temporary filename that only gets used on a cache miss
        temp_filename = f"temp_{uuid.uuid4().hex[:8]}.dxf"
        content = DXFService.save_cached(column, temp_filename)
        
        if os.path.exists(temp_filename):
            background_tasks.add_task(remove_file, temp_filename)
            
        headers = {
            "Content-Disposition": f'attachment; filename="{display_name}"'
        }
        
        # Add cache status header for visibility
        headers["X-Cache"] = "HIT" if is_cached else "MISS"

        return Response(
            content=content,
            media_type="application/dxf",
            headers=headers
        )
            
    except DXFValidationError as e:
        logger.warning(f"Validation error generating Column: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating Column: {str(e)}", exc_info=True)
        if filename and os.path.exists(filename):
            remove_file(filename)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/column/batch")
async def generate_column_batch(request: BatchColumnRequest, background_tasks: BackgroundTasks):
    logger.info(f"Generating batch of {len(request.items)} Columns")
    logger.debug(f"Batch items: {[item.dict() for item in request.items]}")
    if len(request.items) > MAX_BATCH_SIZE:
        logger.warning(f"Batch size {len(request.items)} exceeds limit {MAX_BATCH_SIZE}")
        raise HTTPException(status_code=400, detail=f"Batch size exceeds maximum limit of {MAX_BATCH_SIZE} items")
    
    filenames = []
    try:
        components = []
        disk_filenames = []
        
        for i, item in enumerate(request.items):
            column = Column(item.width, item.height)
            unique_id = uuid.uuid4().hex[:8]
            filename = f"column_{unique_id}_{i+1}_{int(item.width)}x{int(item.height)}.dxf"
            display_name = f"column_{i+1}_{int(item.width)}x{int(item.height)}.dxf"
            
            components.append(column)
            disk_filenames.append(filename)
            filenames.append((filename, display_name))
        
        DXFService.save_batch(components, disk_filenames)
        
        zip_filename = f"columns_batch_{uuid.uuid4().hex[:8]}.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for f, d_name in filenames:
                zipf.write(f, arcname=d_name)
        
        disk_paths = [f[0] for f in filenames]
        background_tasks.add_task(remove_files, disk_paths + [zip_filename])
        logger.info(f"Successfully generated batch zip: {zip_filename}")
        return FileResponse(path=zip_filename, filename="columns_batch.zip", media_type="application/zip")
    except Exception as e:
        logger.error(f"Error in batch Column generation: {str(e)}", exc_info=True)
        disk_paths = [f[0] if isinstance(f, tuple) else f for f in filenames]
        remove_files(disk_paths)
        raise HTTPException(status_code=500, detail=str(e))
