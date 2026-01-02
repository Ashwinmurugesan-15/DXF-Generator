from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import os
import zipfile
import uuid

from dxf_generator.domain.ibeam import IBeam
from dxf_generator.domain.column import Column
from dxf_generator.services.dxf_service import DXFService
from dxf_generator.exceptions.base import DXFValidationError

app = FastAPI(title="DXF Generator API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IBeamRequest(BaseModel):
    total_depth: float
    flange_width: float
    web_thickness: float
    flange_thickness: float

class ColumnRequest(BaseModel):
    width: float
    height: float

class BatchIBeamRequest(BaseModel):
    items: List[IBeamRequest]

class BatchColumnRequest(BaseModel):
    items: List[ColumnRequest]

def remove_file(path: str):
    """Helper to remove file after response is sent."""
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Error removing temporary file {path}: {e}")

def remove_files(paths: List[str]):
    """Helper to remove multiple files."""
    for path in paths:
        remove_file(path)

@app.post("/generate/ibeam")
async def generate_ibeam(request: IBeamRequest, background_tasks: BackgroundTasks):
    filename = None
    try:
        ibeam = IBeam(
            request.total_depth, 
            request.flange_width, 
            request.web_thickness, 
            request.flange_thickness
        )
        filename = f"ibeam_{int(request.total_depth)}x{int(request.flange_width)}.dxf"
        DXFService.save(ibeam, filename)
        
        if os.path.exists(filename):
            background_tasks.add_task(remove_file, filename)
            return FileResponse(
                path=filename,
                filename=filename,
                media_type="application/dxf"
            )
        else:
            raise HTTPException(status_code=500, detail="File generation failed")
            
    except DXFValidationError as e:
        print(f"Validation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Server Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/generate/ibeam/batch")
async def generate_ibeam_batch(request: BatchIBeamRequest, background_tasks: BackgroundTasks):
    filenames = []
    try:
        for i, item in enumerate(request.items):
            ibeam = IBeam(item.total_depth, item.flange_width, item.web_thickness, item.flange_thickness)
            filename = f"ibeam_{i+1}_{int(item.total_depth)}x{int(item.flange_width)}.dxf"
            DXFService.save(ibeam, filename)
            filenames.append(filename)
        
        zip_filename = f"ibeams_batch_{uuid.uuid4().hex[:8]}.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for f in filenames:
                zipf.write(f)
        
        background_tasks.add_task(remove_files, filenames + [zip_filename])
        return FileResponse(path=zip_filename, filename="ibeams_batch.zip", media_type="application/zip")
    except Exception as e:
        remove_files(filenames)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/column")
async def generate_column(request: ColumnRequest, background_tasks: BackgroundTasks):
    try:
        column = Column(request.width, request.height)
        filename = f"column_{int(request.width)}x{int(request.height)}.dxf"
        DXFService.save(column, filename)
        
        if os.path.exists(filename):
            background_tasks.add_task(remove_file, filename)
            return FileResponse(
                path=filename,
                filename=filename,
                media_type="application/dxf"
            )
        else:
            raise HTTPException(status_code=500, detail="File generation failed")
            
    except DXFValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/column/batch")
async def generate_column_batch(request: BatchColumnRequest, background_tasks: BackgroundTasks):
    filenames = []
    try:
        for i, item in enumerate(request.items):
            column = Column(item.width, item.height)
            filename = f"column_{i+1}_{int(item.width)}x{int(item.height)}.dxf"
            DXFService.save(column, filename)
            filenames.append(filename)
        
        zip_filename = f"columns_batch_{uuid.uuid4().hex[:8]}.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for f in filenames:
                zipf.write(f)
        
        background_tasks.add_task(remove_files, filenames + [zip_filename])
        return FileResponse(path=zip_filename, filename="columns_batch.zip", media_type="application/zip")
    except Exception as e:
        remove_files(filenames)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/parse/dxf")
async def parse_dxf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    try:
        # Save uploaded file temporarily
        temp_filename = f"temp_{uuid.uuid4().hex}_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Parse the DXF
        try:
            result = DXFService.parse(temp_filename)
            return result
        finally:
            # Always clean up temp file
            if background_tasks:
                background_tasks.add_task(remove_file, temp_filename)
            else:
                remove_file(temp_filename)
                
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "DXF Generator API is running"}
