from io import BytesIO
from unittest.mock import MagicMock, patch


def test_metrics_endpoint(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "healthy"
    assert "metrics" in payload


def test_metrics_summary_endpoint(client):
    resp = client.get("/metrics/summary")
    assert resp.status_code == 200
    assert "Total Requests" in resp.json()


@patch("dxf_generator.interface.routes.parser.DXFService.parse")
@patch("dxf_generator.interface.routes.parser.uuid.uuid4")
def test_parse_endpoint_success(mock_uuid4, mock_parse, client):
    mock_uuid4.return_value = MagicMock(hex="abc")
    mock_parse.return_value = {"type": "column", "data": {"width": 10.0, "height": 20.0}}

    file_bytes = b"dummy dxf bytes"
    resp = client.post(
        "/api/v1/parse",
        files={"file": ("x.dxf", BytesIO(file_bytes), "application/dxf")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["filename"] == "x.dxf"
    assert body["type"] == "column"
    assert body["dimensions"] == {"width": 10.0, "height": 20.0}


@patch("dxf_generator.interface.routes.tests.subprocess.run")
def test_testcases_run_all_endpoint_mocks_pytest(mock_run, client):
    mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")

    resp = client.get("/api/v1/testcases/run/all")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "passed"
    assert body["exit_code"] == 0
    assert "ok" in body["output"]


def test_testcases_list_endpoint(client):
    resp = client.get("/api/v1/testcases")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@patch("dxf_generator.interface.routes.benchmark.DXFService.save_batch")
@patch("dxf_generator.interface.routes.benchmark.time.sleep")
def test_benchmark_endpoint_fast(mock_sleep, mock_save_batch, client):
    mock_sleep.return_value = None
    mock_save_batch.return_value = []

    resp = client.get("/api/v1/benchmark")
    assert resp.status_code == 200
    text = resp.text
    assert "Starting Load Test Simulation" in text
    assert "Users" in text
