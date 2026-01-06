# DXF Generator Project Documentation

## Project Overview
The DXF Generator is a professional engineering tool designed to validate, calculate, and generate DXF (Drawing Exchange Format) files for structural components, specifically I-Beams and Columns. It features a modern web interface for interactive use and a robust backend that enforces engineering tolerances.

---
## Technical Architecture

### 1. Frontend (React + Vite)
- **Framework**: React 19 with Vite for fast development and optimized builds.
- **State Management**: Modularized logic using a custom hook `useGenerator.js` for clean state separation.
- **API Client**: Axios for communicating with the FastAPI backend.
- **Styling**: Modern CSS with a professional blue-grey theme, responsive layouts, and intuitive UI components.
- **Key Components**:
    - `Generator.jsx`: Main container component using `useGenerator` hook.
    - `GeneratorParts/`: Modular sub-components:
        - `BeamInputs.jsx` & `ColumnInputs.jsx`: Specialized input forms for each component type.
        - `BatchList.jsx`: Manages the dynamic list of items in batch mode.
        - `TabSwitcher.jsx` & `BatchModeToggle.jsx`: Clean UI controls for mode switching.
    - `Login.jsx`: Secure entry point for user authentication.

### 2. Backend (FastAPI + Python)
- **Framework**: FastAPI for high-performance asynchronous API endpoints.
- **CAD Engine**: `ezdxf` library for programmatic creation and parsing of DXF files.
- **Validation**: Multi-layered validation using Pydantic schemas and custom engineering validators.
- **Caching**: Dual-layer in-memory caching using `FastAPICache` (InMemoryBackend) and custom LRU caching in `DXFService`.
- **Core Modules**:
    - `dxf_generator/domain/`: Core entities (`IBeam`, `Column`) with geometric calculation logic.
    - `dxf_generator/validators/`: Strict engineering rule enforcement.
    - `dxf_generator/drawing/`: Translation of geometry to DXF entities.
    - `dxf_generator/services/`: `DXFService` orchestrates generation, parsing, and concurrent execution.
    - `dxf_generator/config/`: Centralized configuration for tolerances, system limits, and environment variables.

---

## Core Features

### 1. Validation-First Pipeline
Every input follows a strict sequence:
1. **Schema Check**: Validates that all fields are numeric and present.
2. **Engineering Validation**: Checks against `tolerances.py` (e.g., minimum web thickness, maximum depth).
3. **Calculation**: Derives the exact geometry points.
4. **Drawing**: Generates the DXF file.

### 2. Batch Generation & Multithreading
- **Concurrency**: Utilizes a class-level `ThreadPoolExecutor` in `DXFService` for parallel processing.
- **Worker Configuration**: Thread pool size is dynamically configurable via environment variables (`MAX_THREADS`).
- **Optimization**: Batch requests are processed concurrently, with results bundled into a ZIP archive for efficient download.
- **Caching**: Repeated requests for the same dimensions are served instantly from the `_generation_cache`.

### 3. DXF Parsing & Edit Mode
- **Intelligent Detection**: Identifies component types based on vertex signatures (12-13 for I-Beams, 4-5 for Columns).
- **Reverse Mapping**: Extracts engineering parameters from raw DXF coordinates.
- **Parsing Cache**: Uses `_parse_cache` to speed up repeated file analysis.
- **Frontend Integration**: Auto-populates the UI and switches modes upon successful file upload.

### 4. Engineering Tolerances
The system enforces real-world engineering constraints defined in `dxf_generator/config/tolerances.py`:
- **I-Beam**: Validates Total Depth, Flange Width, Web Thickness, and Flange Thickness ratios.
- **Column**: Validates Width and Height limits.

### 5. Scalability & Performance
The system is architected to support 100+ concurrent users with high reliability:
- **Asynchronous API**: Built on FastAPI, the server handles 100s of concurrent connections with minimal overhead.
- **Thread-Safe Generation**: CPU-bound CAD generation is offloaded to a `ThreadPoolExecutor`, preventing the main event loop from blocking.
- **Resource Management**: Background tasks handle automatic cleanup of temporary files.
- **In-Memory Metrics**: Real-time tracking of request counts, failure rates, and average processing times.
- **Structured Logging**: JSON-formatted logs with request IDs and duration metrics for production observability.
- **System Limits**:
    - `MAX_BATCH_SIZE`: 50 items (preventing OOM).
    - `MAX_THREADS`: Configurable concurrency level (default 32 for high load).
    - `LRU Caching`: 100-item limit on in-memory caches to maintain stability.
    - `UUID-based isolation`: Ensures 100+ concurrent users never experience file collisions.

---

## Production Tuning
To scale for 100+ concurrent users, adjust the following in `.env`:
- `API_WORKERS`: Increase based on CPU cores (e.g., `2 * cores + 1`).
- `MAX_THREADS`: Increase (e.g., `32` or `64`) if batch generation requests are frequent.
- `MAX_BATCH_SIZE`: Decrease if memory usage per worker is too high.

### 6. Monitoring & Documentation
- **API Documentation**: Detailed technical specifications for all endpoints can be found in `API_DOCUMENTATION.md`.
- **System Metrics**: Real-time performance monitoring is available via the `/metrics` endpoint.
- **Interactive Testing**: Built-in Swagger UI (`/docs`) and ReDoc (`/redoc`) for live API testing.

---

## Project Structure
```text
DXF_Generator_Project2/
├── dxf_generator/          # Backend Source Code
│   ├── domain/             # Business logic (IBeam, Column)
│   ├── validators/         # Engineering rules (Ratios & Limits)
│   ├── drawing/            # CAD generation logic
│   ├── interface/          # API (FastAPI) and CLI
│   │   └── routes/         # Component-specific endpoints
│   ├── services/           # Core DXFService with Caching
│   ├── config/             # Env-based configuration
│   └── exceptions/         # Custom Error Hierarchy
├── tests/                  # Automated Test Suite (Pytest)
├── frontend/               # React + Vite Frontend
│   ├── src/hooks/          # Custom state hooks
│   └── src/components/     # Modular UI parts
└── run_web.py              # Production entry point (Uvicorn)
```

---

## Getting Started

### Backend Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `python run_web.py`
3. API Documentation available at: `http://localhost:8000/docs`

### Testing
1. Run all tests: `pytest`
2. Run specific tests: `pytest tests/unit/test_ibeam.py`

### Frontend Setup
1. Navigate to directory: `cd frontend`
2. Install dependencies: `npm install`
3. Run development server: `npm run dev` (Port 5173)

---

## Error Handling
The project uses custom exceptions to provide detailed feedback:
- `IBeamSchemaError`: Missing or invalid field types.
- `IBeamGeometryError`: Dimension violations (e.g., "Web thickness too small").
- `DXFValidationError`: Base exception for all CAD-related validation issues.

---

## Scalability and Production Readiness

The project is designed to handle high concurrency (e.g., 100+ simultaneous users) through the following optimizations:

- **Asynchronous Core**: Built on FastAPI, the server handles many concurrent I/O connections efficiently.
- **Concurrent Processing**: CPU-bound DXF generation is offloaded to a `ThreadPoolExecutor` (default: 20 threads) to prevent blocking the main event loop.
- **Dual Caching**:
    - **FastAPI Cache**: In-memory response caching for API endpoints.
    - **DXF Service Cache**: Internal LRU-style cache for generated DXF content (500 item capacity).
- **Multi-Worker Support**: Configurable via `API_WORKERS` in `env_config.py` (default: 4).
- **Structured Logging**: JSON-formatted logs with Request IDs for observability in production environments (e.g., ELK stack).
- **Resource Management**: Background tasks automatically clean up temporary files to prevent disk bloat.
