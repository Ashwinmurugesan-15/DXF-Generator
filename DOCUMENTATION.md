# DXF Generator Project Documentation

## Project Overview
The DXF Generator is a professional engineering tool designed to validate, calculate, and generate DXF (Drawing Exchange Format) files for structural components, specifically I-Beams and Columns. It features a modern web interface for interactive use and a robust backend that enforces engineering tolerances.

---

## Technical Architecture

### 1. Frontend (React + Vite)
- **Framework**: React with Vite for fast development and optimized builds.
- **State Management**: React Hooks (`useState`) for managing component dimensions, batch modes, and UI states.
- **API Client**: Axios for communicating with the FastAPI backend.
- **Styling**: Custom CSS with a focus on professional UX, featuring a light-blue theme, responsive cards, and intuitive tab switching.
- **Key Components**:
    - `Login.jsx`: Handles user authentication.
    - `Generator.jsx`: Main interface for dimension input, batch generation, and DXF file parsing.

### 2. Backend (FastAPI + Python)
- **Framework**: FastAPI for high-performance asynchronous API endpoints.
- **CAD Engine**: `ezdxf` library for programmatic creation and parsing of DXF files.
- **Validation**: Pydantic models for request schema validation and custom domain validators for engineering logic.
- **Core Modules**:
    - `dxf_generator/domain/`: Contains core logic for `IBeam` and `Column` entities.
    - `dxf_generator/validators/`: Enforces engineering rules and raises custom exceptions.
    - `dxf_generator/drawing/`: Translates calculated coordinates into CAD polylines.
    - `dxf_generator/services/`: High-level services for file operations and parsing.

---

## Core Features

### 1. Validation-First Pipeline
Every input follows a strict sequence:
1. **Schema Check**: Validates that all fields are numeric and present.
2. **Engineering Validation**: Checks against `tolerances.py` (e.g., minimum web thickness, maximum depth).
3. **Calculation**: Derives the exact geometry points.
4. **Drawing**: Generates the DXF file.

### 2. Batch Generation & Multithreading
- **Concurrency**: The project uses a `ThreadPoolExecutor` from Python's `concurrent.futures` module to handle batch generation tasks.
- **Performance**: When multiple components are requested , the backend processes them in parallel rather than sequentially, significantly reducing the time required to generate the final ZIP archive.
- **Service Layer (`DXFService`)**: 
    - **Shared Executor**: Maintains a class-level `ThreadPoolExecutor` with 8 workers for efficient resource reuse.
    - **save_batch**: Orchestrates concurrent execution by submitting tasks to the thread pool and blocking until all futures are resolved.
    - **save**: Provides a standard synchronous interface for single-component generation.
- **ZIP Bundling**: Successfully generated DXF files are bundled into a unique ZIP file using the `zipfile` module and provided to the user as a single download.

### 3. DXF Parsing & Edit Mode
- **Reverse Engineering**: The `DXFService.parse` method allows the system to "read back" generated files.
- **Geometry Analysis**:
    - **Identification**: Uses vertex counts (12-13 for I-Beams, 4-5 for Columns) to identify the component type.
    - **Dimension Extraction**: Maps specific vertex coordinates back to engineering parameters like `total_depth`, `web_thickness`, etc.
- **Auto-Fill Logic**: The frontend uses the parsed data to switch tabs and populate the input fields, enabling a seamless "Upload and Edit" workflow.

### 4. Engineering Tolerances
The system enforces real-world engineering constraints defined in `dxf_generator/config/tolerances.py`:
- **I-Beam**: Validates Total Depth, Flange Width, Web Thickness, and Flange Thickness ratios.
- **Column**: Validates Width and Height limits.

---

## Project Structure
```text
DXF_Generator_Project2/
├── dxf_generator/          # Backend Source Code
│   ├── domain/             # Business logic (IBeam, Column)
│   ├── validators/         # Engineering rules
│   ├── drawing/            # CAD generation logic
│   ├── interface/          # API (web.py) and CLI
│   ├── services/           # DXFService for file ops
│   └── config/             # Engineering tolerances
├── frontend/               # React Source Code
│   ├── src/
│   │   ├── components/     # UI Components (Generator, Login)
│   │   └── App.jsx         # Main router and state
│   └── vite.config.js      # Frontend build config
├── run_web.py              # Backend entry point (Port 8000)
└── requirements.txt        # Python dependencies
```

---

## Getting Started

### Backend Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run the server: `python run_web.py`
3. API Documentation available at: `http://localhost:8000/docs`

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
