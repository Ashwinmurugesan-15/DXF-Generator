import pytest
from fastapi.testclient import TestClient
from dxf_generator.interface.web import app

@pytest.fixture
def client():
    """
    Test client for FastAPI integration tests.
    """
    with TestClient(app) as c:
        yield c
