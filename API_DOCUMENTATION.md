# DXF Generator Professional API Documentation

Welcome to the **DXF Generator Professional API**. This high-performance CAD generation service allows structural engineers and developers to programmatically create and parse DXF (Drawing Exchange Format) files for standard structural components.

## **API Overview**

- **Version**: `1.2.0`
- **Base URL**: `/api/v1`
- **Formats**: JSON (Request/Response), DXF (Download), ZIP (Batch Download)
- **Interactive Docs**: 
  - Swagger UI: `/docs`
  - ReDoc: `/redoc`

---

## **Endpoints**

### **1. I-Beam Generation**

#### **Generate Single I-Beam**
`POST /ibeam`

Creates a single I-Beam DXF file based on specified dimensions.

**Request Body (`IBeamRequest`):**
| Field | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `total_depth` | `float` | Total height of the I-Beam (mm) | `300` |
| `flange_width` | `float` | Width of top/bottom flanges (mm) | `150` |
| `web_thickness` | `float` | Thickness of vertical web (mm) | `8` |
| `flange_thickness`| `float` | Thickness of horizontal flanges (mm)| `12` |
| `length` | `float` | Total length of the beam (mm) | `1000` |

**Response:**
- `200 OK`: Returns a `.dxf` file (`application/dxf`).
- `400 Bad Request`: Validation error (e.g., thickness too large for width).
- `500 Internal Server Error`: Generation failure.

---

#### **Generate Batch I-Beams**
`POST /ibeam/batch`

Creates multiple I-Beam DXF files bundled in a single ZIP archive.

**Request Body (`BatchIBeamRequest`):**
| Field | Type | Description |
| :--- | :--- | :--- |
| `items` | `List[IBeamRequest]` | List of I-Beam specifications |

**Response:**
- `200 OK`: Returns a `.zip` file (`application/zip`) containing the DXF files.
- `400 Bad Request`: Batch size exceeds limit (default: 50).

---

### **2. Column Generation**

#### **Generate Single Column**
`POST /column`

Creates a single rectangular column DXF file.

**Request Body (`ColumnRequest`):**
| Field | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `width` | `float` | Width of the column (mm) | `200` |
| `height` | `float` | Height of the column (mm) | `200` |

**Response:**
- `200 OK`: Returns a `.dxf` file.

---

#### **Generate Batch Columns**
`POST /column/batch`

Creates multiple rectangular column DXF files bundled in a ZIP archive.

---

### **3. DXF Parser**

#### **Parse DXF File**
`POST /parse`

Upload an existing DXF file to extract structural dimensions.

**Request:**
- `multipart/form-data`
- `file`: The `.dxf` file to parse.

**Response Body (`ParseResponse`):**
```json
{
  "success": true,
  "filename": "original_name.dxf",
  "dimensions": {
    "depth": 300,
    "width": 150,
    "type": "ibeam"
  },
  "message": "Parsing successful"
}
```

---

## **Engineering Constraints**

The API enforces several engineering rules to ensure generated components are physically viable:

- **Minimum Web Thickness**: 3.0mm
- **Maximum Total Depth**: 1500mm
- **Ratios**:
  - `Web Thickness` ≤ 25% of `Flange Width`
  - `Flange Thickness` ≤ 20% of `Flange Width`
  - `Web Thickness` ≥ 2% of `Total Depth`
  - `Flange Width` ≥ 25% of `Total Depth`

---

## **Error Handling**

The API uses standard HTTP status codes:

- `400`: **Validation Error**. The message body will contain specific details about why the geometry is invalid.
- `422`: **Unprocessable Entity**. Missing or malformed request parameters.
- `500`: **Server Error**. Unexpected failure during DXF generation.

---

## **System Metrics**

Performance metrics can be retrieved via the monitoring endpoint:

`GET /metrics`

Returns JSON data including:
- `total_requests`: Total number of API calls.
- `avg_response_time_ms`: Average latency.
- `total_failures`: Number of requests returning 4xx or 5xx.
