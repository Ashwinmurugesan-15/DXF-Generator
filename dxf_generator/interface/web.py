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
    
    # Debug log for incoming request
    logger.debug(
        f"Incoming {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client": request.client.host if request.client else None
        }
    )
    
    try:
        response = await call_next(request)
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"Unhandled exception during {request.method} {request.url.path}: {str(e)}",
            exc_info=True,
            extra={
                "duration_ms": round(process_time, 2),
                "method": request.method,
                "path": request.url.path
            }
        )
        raise e from None # Re-raise to let FastAPI handle it
    
    process_time = (time.time() - start_time) * 1000  # ms
    
    # Update metrics (exclude metrics endpoint itself)
    if request.url.path != "/metrics":
        metrics["total_requests"] += 1
        metrics["total_processing_time_ms"] += process_time
        metrics["avg_response_time_ms"] = metrics["total_processing_time_ms"] / metrics["total_requests"]
        if response.status_code >= 400:
            metrics["total_failures"] += 1

    # Log request details with appropriate level
    log_msg = f"{request.method} {request.url.path} - {response.status_code} ({process_time:.2f}ms)"
    log_extra = {
        "duration_ms": round(process_time, 2),
        "status_code": response.status_code,
        "method": request.method,
        "path": request.url.path
    }
    
    if response.status_code >= 500:
        logger.error(log_msg, extra=log_extra)
    elif response.status_code >= 400:
        logger.warning(log_msg, extra=log_extra)
    else:
        logger.info(log_msg, extra=log_extra)
    
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
