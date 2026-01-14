# DXF Generator Project (Human-Friendly Guide)

This repository generates and parses DXF files for two structural shapes:

- **I-Beam** (a.k.a. `ibeam`)
- **Column** (a rectangular section)

It has:

- A **FastAPI** backend that validates inputs, generates DXFs, parses uploaded DXFs, and provides metrics.
- A **React + Vite** frontend that calls the backend and downloads the generated DXF/ZIP.

## Quick Start (Run Locally)

### 1) Backend (FastAPI)

From the repo root:

```bash
pip install -r requirements.txt
python run_web.py
```

Default backend URL:

- `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`

The backend entrypoint is `run_web.py` which runs Uvicorn with values from `dxf_generator/config/env_config.py`.

### 2) Frontend (React + Vite)

From the repo root:

```bash
cd frontend
npm install
npm run dev
```

Default frontend URL:

- `http://localhost:5173/`

The frontend uses `VITE_API_BASE_URL` if set; otherwise it talks to `http://localhost:8000` (`frontend/src/hooks/useGenerator.js:4`).

## How To Use (UI)

- **Single mode**
  - Pick **Beam** or **Column**
  - Fill in dimensions
  - Click generate → downloads a `.dxf`

- **Batch mode**
  - Toggle batch mode
  - Add multiple rows of dimensions
  - Click generate → downloads a `.zip` containing multiple `.dxf`

- **Parse / Edit from DXF**
  - Upload an existing `.dxf`
  - Backend detects whether it looks like an `ibeam` or `column`
  - Backend returns extracted dimensions

Note: The frontend currently includes a `Login.jsx` screen, but there is no server-side authentication implemented in this backend.

## API Overview (Backend)

Base path: `/api/v1`

### Health & Metrics

- `GET /` → simple JSON “API is running”
- `GET /metrics` → runtime metrics
- `GET /metrics/summary` → simplified summary

### DXF Generation

- `POST /api/v1/ibeam` → generate a single I-beam DXF (returns `application/dxf`)
- `POST /api/v1/ibeam/batch` → generate many I-beams (returns `application/zip`)
- `POST /api/v1/column` → generate a single column DXF
- `POST /api/v1/column/batch` → generate many columns

Batch requests are limited by `MAX_BATCH_SIZE` from `dxf_generator/config/system_limits.py:5`.

### DXF Parsing (Upload)

- `POST /api/v1/parse` → upload a `.dxf` (multipart form field name: `file`)

Upload validation rules come from `dxf_generator/config/env_config.py:28`:

- `UPLOAD_MAX_SIZE_BYTES` default: `5 * 1024 * 1024` (5 MB)
- Allowed extension: `.dxf`
- Multiple MIME types allowed to support common DXF upload behaviors

### Dev/Test Helpers (Use Carefully)

These endpoints exist for development/debugging and should not be exposed publicly in production:

- `GET /api/v1/testcases` → lists test files
- `GET /api/v1/testcases/run/all` → runs `pytest` on the server machine
- `GET /api/v1/benchmark` → runs an internal benchmark simulation

## Validation & Engineering Rules (Backend)

The backend validates inputs in layers:

- **Schema-level validation**: request models in the route files (`dxf_generator/interface/routes/*.py`)
- **Engineering validation**: domain + validators (see `dxf_generator/domain/` and `dxf_generator/validators/`)
- **Generation**: DXF creation with `ezdxf` via `dxf_generator/drawing/` and `dxf_generator/services/`

Errors are surfaced as `400` (validation) or `500` (unexpected server errors). The base exception type is `DXFValidationError` (`dxf_generator/exceptions/base.py`).

## Caching & Concurrency (Backend)

There are two caching layers:

- **FastAPI response cache**: `fastapi-cache2` in-memory backend initialized in `dxf_generator/interface/web.py:19-26`
- **Service-level caches** in `DXFService` (`dxf_generator/services/dxf_service.py:21-24`)
  - Generation cache: `max_size=500`
  - Parse cache: `max_size=100`
  - Batch (ZIP) cache: `max_size=50`

Batch generation uses a thread pool managed by `BatchProcessor` (`dxf_generator/services/batch_processor.py`). The worker count comes from `MAX_THREADS` (`dxf_generator/config/env_config.py:17`).

## Configuration (Environment Variables)

Configuration lives in `dxf_generator/config/env_config.py`. You can set these via environment variables (optionally in a `.env` file if your environment has `python-dotenv` installed):

```bash
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=false

MAX_THREADS=20
MAX_BATCH_SIZE=50

UPLOAD_MAX_SIZE_BYTES=5242880
```

## Project Layout

```text
DXF_Generator_Project2/
├── dxf_generator/                 # Backend code
│   ├── config/                    # Env + logging + limits
│   ├── domain/                    # IBeam / Column domain objects
│   ├── drawing/                   # DXF drawing primitives
│   ├── exceptions/                # Custom exceptions
│   ├── interface/                 # FastAPI app + routes + CLI
│   ├── services/                  # DXFService facade + helpers
│   └── validators/                # Engineering/file validations
├── tests/                         # Pytest suite
├── frontend/                      # React + Vite app
└── run_web.py                     # Starts the FastAPI server (Uvicorn)
```

## Testing & Quality Checks

### Backend

```bash
pytest
```

Or:

```bash
python run_tests.py
```

### Frontend

From `frontend/`:

```bash
npm run lint
npm run build
```

## Common Issues

- **`ModuleNotFoundError: dotenv`**
  - `env_config.py` uses `load_dotenv()`. Install `python-dotenv` if your environment doesn’t already include it.
- **CORS / frontend can’t call backend**
  - The backend enables permissive CORS (`allow_origins=["*"]`) in `dxf_generator/interface/web.py:127-134`.
  - Ensure the backend is running on the URL the frontend uses (`VITE_API_BASE_URL` or `http://localhost:8000`).
- **Upload rejected**
  - Confirm the file extension is `.dxf` and size is within `UPLOAD_MAX_SIZE_BYTES`.
