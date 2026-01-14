from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from dxf_generator.config.logging_config import logger
from dxf_generator.interface.routes import ibeam, column, parser, tests, benchmark

# Advanced metrics tracking
metrics = {
    "total_requests": 0,
    "total_failures": 0,
    "total_processing_time_ms": 0.0,
    "start_time": time.time(),
    "unique_clients": set()
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize cache
    FastAPICache.init(InMemoryBackend())
    yield
    # Shutdown logic (if any) can go here

app = FastAPI(lifespan=lifespan)

@app.get("/metrics/summary")
async def get_load_summary():
    """Generates a simple live performance summary."""
    try:
        total_time = time.time() - metrics["start_time"]
        req_per_sec = metrics["total_requests"] / total_time if total_time > 0 else 0
        
        return {
            "Users": len(metrics["unique_clients"]),
            "Total Requests": metrics["total_requests"],
            "Time Taken (sec)": round(total_time, 2),
            "RPS": round(req_per_sec, 1)
        }
    except Exception as e:
        logger.error(f"Error in get_load_summary: {str(e)}")
        return {"error": str(e)}

@app.get("/metrics")
async def get_metrics():
    """Return system performance metrics."""
    # Convert set to list for JSON serialization
    display_metrics = metrics.copy()
    display_metrics["unique_clients"] = list(metrics["unique_clients"])
    return {
        "status": "healthy",
        "metrics": display_metrics
    }

@app.get("/")
async def root():
    return {"message": "DXF Generator API is running"}

# Register Routers
app.include_router(ibeam.router, prefix="/api/v1", tags=["ibeam"])
app.include_router(column.router, prefix="/api/v1", tags=["column"])
app.include_router(parser.router, prefix="/api/v1", tags=["parser"])
app.include_router(tests.router, prefix="/api/v1", tags=["tests"])
app.include_router(benchmark.router, prefix="/api/v1", tags=["benchmark"])

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
    if not request.url.path.startswith("/metrics"):
        metrics["total_requests"] += 1
        metrics["total_processing_time_ms"] += process_time
        if request.client:
            metrics["unique_clients"].add(request.client.host)
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