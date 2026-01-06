
## API Overview
# DXF Generator Professional API Documentation

Welcome to the **DXF Generator Professional API**. This high-performance CAD generation service allows structural engineers and developers to programmatically create and parse DXF (Drawing Exchange Format) files for standard structural components.

## API Overview

-API Version: 1.2.0
Base Path: /api/v1
Supported Formats:
          JSON → request & response data
          DXF → individual drawings 
          ZIP → batch downloads
---

#### Generate Single I-Beam
Generate a Single I-Beam
    Endpoint: POST /ibeam
Creates one DXF file representing an I-Beam using the given dimensions.
Required Inputs:
      Total depth of the beam (mm)
      Flange width (mm)
      Web thickness (mm)
      Flange thickness (mm)
      Beam length (mm)
What you get:
      A downloadable DXF file
      validation errors if dimensions are invalid

---

### Generate Multiple I-Beams (Batch)
Endpoint: POST /ibeam/batch
Generates multiple I-Beam DXF files at once and returns them as a ZIP archive.
Limits:
    Maximum 5 beams per request
What you get:
    One ZIP file containing all generated DXFs
---

### 2. Column Generation

### Generate a Single Column
Endpoint: POST /column
Creates a DXF file for a rectangular column using width and height inputs.
What you get:
    One DXF file
---

#### Generate Batch Columns

Endpoint: POST /column/batch
Creates multiple column DXF files and bundles them into a ZIP file.
---

### 3. DXF Parser

Extract Dimensions from an Existing DXF
Endpoint: POST /parse
Uploads an existing DXF file and extracts basic structural information.
Typical Output Includes:
      Component type (I-beam or column)
      Key dimensions (depth, width, etc.)
      File name and parsing status
      This is useful for verifying drawings or re-using legacy DXF files.
---

## Engineering Constraints

To ensure all generated components are structurally valid, the system enforces industry-based constraints:
      Minimum web thickness: 3 mm
      Maximum beam depth: 1500 mm
Dimensional relationships:
      Web thickness ≤ 25% of flange width
      Flange thickness ≤ 20% of flange width
      Web thickness ≥ 2% of total depth
      Flange width ≥ 25% of total depth
If any rule is violated, the API returns a clear validation error.

---
## Error Handling
Error Handling (Simple Explanation)
The API responds with standard HTTP status codes:
400 – Invalid Input
The dimensions provided are not structurally valid.
422 – Invalid Request Format
Required fields are missing or incorrectly formatted.
500 – Internal Error
An unexpected issue occurred during file generation.
Each error includes a clear message explaining the issue.
---

## System Metrics
A monitoring endpoint is available:
Endpoint: GET /metrics
It provides operational insights such as:
      Total number of API requests
      Average response time
      Number of failed requests
This helps with performance tracking and reliability monitoring.

