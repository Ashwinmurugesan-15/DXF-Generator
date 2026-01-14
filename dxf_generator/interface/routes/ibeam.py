import os
from fastapi import APIRouter, HTTPException, BackgroundTasks, Response
from pydantic import BaseModel
from typing import List
import uuid
import zipfile
import hashlib

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
    temp_filename = None
    logger.debug(f"Received I-Beam generation request: {request.model_dump()}")
    try:
        ibeam = IBeam(
            request.total_depth, 
            request.flange_width, 
            request.web_thickness, 
            request.flange_thickness
        )
        
        # Check cache first to avoid unnecessary UUID generation and disk prep
        cache_key = DXFService.get_cache_key(ibeam)
        is_cached = DXFService._generation_cache.contains(cache_key)
        
        # Include a short hash in the filename for uniqueness and stability
        short_hash = hashlib.md5(cache_key.encode()).hexdigest()[:6]
        display_name = f"ibeam_{int(request.total_depth)}x{int(request.flange_width)}_{short_hash}.dxf"
        
        # Use cached generation (internally logs hit/miss)
        # We pass a temporary filename that only gets used on a cache miss
        temp_filename = f"temp_{uuid.uuid4().hex[:8]}.dxf"
        content = DXFService.save_cached(ibeam, temp_filename)
        
        # If a file was actually created on disk (cache miss), schedule its removal
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
        logger.warning(f"Validation error generating I-Beam: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating I-Beam: {str(e)}", exc_info=True)
        if temp_filename and os.path.exists(temp_filename):
            remove_file(temp_filename)
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
    
    try:
        # 1. Prepare components to calculate batch key
        components = [
            IBeam(item.total_depth, item.flange_width, item.web_thickness, item.flange_thickness)
            for item in request.items
        ]
        
        # 2. Check Batch Cache
        batch_key = DXFService.get_batch_key(components)
        cached_zip = DXFService.get_cached_batch(batch_key)
        
        if cached_zip:
            logger.info(f"Batch cache hit for key: {batch_key}")
            headers = {
                "Content-Disposition": 'attachment; filename="ibeams_batch.zip"',
                "X-Cache": "HIT"
            }
            return Response(content=cached_zip, media_type="application/zip", headers=headers)

        # 3. Cache Miss - Generate Files
        logger.info(f"Batch cache miss for key: {batch_key}. Generating...")
        
        filenames = [] # List of (disk_path, archive_name)
        disk_filenames = []
        
        for i, (item, component) in enumerate(zip(request.items, components)):
            unique_id = uuid.uuid4().hex[:8]
            filename = f"ibeam_{unique_id}_{i+1}_{int(item.total_depth)}x{int(item.flange_width)}.dxf"
            display_name = f"ibeam_{i+1}_{int(item.total_depth)}x{int(item.flange_width)}.dxf"
            
            disk_filenames.append(filename)
            filenames.append((filename, display_name))
        
        DXFService.save_batch(components, disk_filenames)
        
        # 4. Create ZIP
        zip_filename = f"ibeams_batch_{uuid.uuid4().hex[:8]}.zip"
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
            "Content-Disposition": 'attachment; filename="ibeams_batch.zip"',
            "X-Cache": "MISS"
        }
        logger.info(f"Successfully generated and cached batch zip: {zip_filename}")
        
        return Response(content=zip_bytes, media_type="application/zip", headers=headers)

    except Exception as e:
        logger.error(f"Error in batch I-Beam generation: {str(e)}", exc_info=True)
        # Try to cleanup any files that were created
        try:
            if 'filenames' in locals():
                remove_files([f[0] for f in filenames])
            if 'zip_filename' in locals() and os.path.exists(zip_filename):
                remove_file(zip_filename)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=str(e))
