import os
from fastapi import APIRouter, HTTPException, BackgroundTasks, Response
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
    logger.debug(f"Received Column generation request: {request.model_dump()}")
    
    # Log level demonstration triggers
    if request.width == 1.11:
        logger.debug("DEBUG TRIGGER: Detailed diagnostic trace for Column width 1.11")
    elif request.width == 9.99:
        logger.error("ERROR TRIGGER: Simulating a critical failure for Column width 9.99")
        raise Exception("Demonstration of Column ERROR log with full stack trace")
        
    try:
        column = Column(request.width, request.height)
        
        # Check cache first to avoid unnecessary UUID generation and disk prep
        cache_key = DXFService.get_cache_key(column)
        is_cached = DXFService._generation_cache.contains(cache_key)
        
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
        if temp_filename and os.path.exists(temp_filename):
            remove_file(temp_filename)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/column/batch")
async def generate_column_batch(request: BatchColumnRequest, background_tasks: BackgroundTasks):
    logger.info(f"Generating batch of {len(request.items)} Columns")
    
    if len(request.items) > MAX_BATCH_SIZE:
        logger.warning(f"Batch size {len(request.items)} exceeds limit {MAX_BATCH_SIZE}")
        raise HTTPException(status_code=400, detail=f"Batch size exceeds maximum limit of {MAX_BATCH_SIZE} items")
    
    try:
        # 1. Prepare components to calculate batch key
        components = [
            Column(item.width, item.height)
            for item in request.items
        ]
        
        # 2. Check Batch Cache
        batch_key = DXFService.get_batch_key(components)
        cached_zip = DXFService.get_cached_batch(batch_key)
        
        if cached_zip:
            logger.info(f"Batch cache hit for key: {batch_key}")
            headers = {
                "Content-Disposition": 'attachment; filename="columns_batch.zip"',
                "X-Cache": "HIT"
            }
            return Response(content=cached_zip, media_type="application/zip", headers=headers)

        # 3. Cache Miss - Generate Files
        logger.info(f"Batch cache miss for key: {batch_key}. Generating...")
        
        filenames = []
        disk_filenames = []
        
        for i, (item, component) in enumerate(zip(request.items, components)):
            unique_id = uuid.uuid4().hex[:8]
            filename = f"column_{unique_id}_{i+1}_{int(item.width)}x{int(item.height)}.dxf"
            display_name = f"column_{i+1}_{int(item.width)}x{int(item.height)}.dxf"
            
            disk_filenames.append(filename)
            filenames.append((filename, display_name))
        
        DXFService.save_batch(components, disk_filenames)
        
        # 4. Create ZIP
        zip_filename = f"columns_batch_{uuid.uuid4().hex[:8]}.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for f, d_name in filenames:
                if os.path.exists(f):
                    zipf.write(f, arcname=d_name)
                else:
                    logger.error(f"Generated file missing: {f}")
        
        # 5. Read ZIP bytes for caching and response
        with open(zip_filename, "rb") as zf:
            zip_bytes = zf.read()
            
        # 6. Cache the result
        DXFService.cache_batch(batch_key, zip_bytes)
        
        # 7. Cleanup
        # Schedule removal of temp DXF files and the temp ZIP
        all_temp_files = [f[0] for f in filenames] + [zip_filename]
        background_tasks.add_task(remove_files, all_temp_files)
        
        headers = {
            "Content-Disposition": 'attachment; filename="columns_batch.zip"',
            "X-Cache": "MISS"
        }
        logger.info(f"Successfully generated and cached batch zip: {zip_filename}")
        
        return Response(content=zip_bytes, media_type="application/zip", headers=headers)

    except Exception as e:
        logger.error(f"Error in batch Column generation: {str(e)}", exc_info=True)
        # Try to cleanup any files that were created
        try:
            if 'filenames' in locals():
                remove_files([f[0] for f in filenames])
            if 'zip_filename' in locals() and os.path.exists(zip_filename):
                remove_file(zip_filename)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))
