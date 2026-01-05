from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from dxf_generator.config.logging_config import logger
from dxf_generator.interface.routes import ibeam, column, parser

# Simple in-memory metrics storage
metrics = {
    "total_requests": 0,
    "total_failures": 0,
    "avg_response_time_ms": 0.0,
    "total_processing_time_ms": 0.0
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize cache
    FastAPICache.init(InMemoryBackend())
    yield
    # Shutdown logic (if any) can go here

app = FastAPI(lifespan=lifespan)

# Performance and Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000  # ms
    
    # Update metrics (exclude metrics endpoint itself)
    if request.url.path != "/metrics":
        metrics["total_requests"] += 1
        metrics["total_processing_time_ms"] += process_time
        metrics["avg_response_time_ms"] = metrics["total_processing_time_ms"] / metrics["total_requests"]
        if response.status_code >= 400:
            metrics["total_failures"] += 1

    # Log request details
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} ({process_time:.2f}ms)",
        extra={
            "duration_ms": round(process_time, 2),
            "status_code": response.status_code,
            "method": request.method,
            "path": request.url.path
        }
    )
    
    return response

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ibeam.router, prefix="/api/v1")
app.include_router(column.router, prefix="/api/v1")
app.include_router(parser.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "DXF Generator API is running"}

@app.get("/metrics")
async def get_metrics():
    """Return system performance metrics."""
    return {
        "status": "healthy",
        "metrics": metrics
    }
